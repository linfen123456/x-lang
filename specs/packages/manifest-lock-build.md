# 包、Manifest、Lockfile 与构建契约（XPM / XBuild）

> 类型：Spec｜唯一负责：包名规则、`x.toml` Schema、`x.lock` 格式、依赖解析规则、Action DAG 与构建键、缓存、命令契约、供应链要求。分层决策见 [ADR-0004](../../docs/decisions/ADR-0004-xpm-xbuild-layering.md)。

## 1. 结论

1. XPM 负责“用哪些包”，输出 `x.lock` 和 ResolvedGraph。XBuild 负责“怎么构建”，输出 Action DAG 和工件。XBuild **不得**重新选择版本，编译器**不得**回调 Resolver。
2. 能力分期：
   - P1：Path/Workspace 依赖，加 `x.lock` v1；
   - P2：Git、版本约束、PubGrub、Feature；
   - P3：Registry、签名、远程只读缓存、SBOM；
   - P4：publish、yank、API diff 门禁；
   - P5：外部生态依赖（C/C++/JVM 适配器）。
3. 相同的输入在任何 OS、任何遍历顺序下都必须产生**字节一致**的 `x.lock` 与构建计划。

## 2. 包名 [RULE-PKG-NAME] [RULE-PKG-IMPORTROOT]

1. 包名格式：`[a-z][a-z0-9]*(-[a-z0-9]+)*`，最长 64 个字符。
2. 保留名：`core alloc std x test self crate xrt`。
3. 包名不合法，或使用了保留名，报 `X-E8003`。
4. **导入根名**：把包名中的 `-` 替换为 `_`。依赖 key（`[dependencies]` 中的键）必须满足 `[a-z][a-z0-9_]*`。
5. 当前包与依赖、或依赖与依赖映射到同一个导入根名时，报 `X-E8004`。

## 3. `x.toml` Schema [RULE-PKG-PARSE] [RULE-PKG-UNKNOWN]

```toml
manifest-version = 1

[package]
name = "order-service"
version = "0.3.0"              # SemVer
edition = "preview"            # 1.0 前固定为 "preview"；1.0 起使用稳定 Edition 名
license = "Apache-2.0 OR MIT"  # SPDX 表达式（x init 默认值）
description = "…"
prelude = true                 # 可关闭
no-std = false                 # P4 起生效

[dependencies]                 # P1：path；P2：version/git；P3：registry
util = { path = "../util" }
log = { version = "^2.3" }                                  # P2
json = { git = "https://example.invalid/x-json.git", rev = "<commit>" }   # P2
tls = { version = "^1.0", optional = true }                 # P2

[dev-dependencies]             # 只用于测试、示例、基准
testkit = { path = "../testkit" }

[features]                     # P2
default = []
tls = ["dep:tls"]

[profile.dev]                  # 也可以写 [profile.release]
opt-level = 0                  # 0..3
debug = true
panic = "abort"                # P0–P2 只允许 abort

[workspace]                    # 只能出现在 Workspace 根
members = ["crates/*", "apps/*"]

[target.x86_64-unknown-linux-gnu.link]
search = ["native/lib"]        # 相对包根
```

规则：
- 解析失败报 `X-E8001`。
- 未知字段报 `X-E8002`（错误而非警告，以防拼写错误被静默忽略）。
- `manifest-version` 升级时，必须提供迁移工具。
- 目标自动发现：
  - `src/main.x` 编译为与包同名的二进制；
  - `src/lib.x` 编译为库；
  - `src/bin/*.x` 是额外的二进制；
  - `tests/*.x` 是集成测试；
  - `benches/*.x` 是基准。

## 4. 依赖规则 [RULE-PKG-CYCLE] [RULE-PKG-PATHESCAPE] [RULE-PKG-FEATURE] [RULE-PKG-CONFLICT]

1. 源码只能导入直接依赖（见 [06](../language/06-modules.md) §3）。传递依赖只出现在 `x.lock`、构建图和 SBOM 中。
2. 依赖图必须是有向无环图，包括 dev 依赖在内，成环报 `X-E8005`。Path 依赖越出 Workspace 根报 `X-E8006`。
3. 版本选择（P2）：
   - 在同一解析域内，同名同源的包只选一个版本，取满足全部约束的最高稳定版；
   - 预发布版本必须显式请求；
   - 冲突时报 `X-E8009`，并给出最小冲突链。
   - 1.0 不支持同一主版本以外的多版本共存，留到 P5 由 RFC 决定。
4. Feature（P2）：
   - 只能增加能力，在同一 `PackageId + 解析域` 内单调合并；
   - 解析域至少隔离 `target-normal`、`dev-test`、`host-tool`；
   - 未知 Feature 或跨域激活报 `X-E8008`。
5. Git 依赖：Lockfile 必须固定 commit 和源码树摘要；不读取工作区脏状态和 Git hook。

## 5. `x.lock` v1 [RULE-PKG-LOCKED] [RULE-PKG-DIGEST]

```toml
lock-version = 1
manifest-digest = "sha256:…"

[[package]]
id = "util@0.1.0#path:crates/util"
name = "util"
version = "0.1.0"
source = "path:crates/util"
content-digest = "sha256:…"

[[resolution]]
id = "target-normal:x86_64-unknown-linux-gnu"
domain = "target-normal"
host = "x86_64-unknown-linux-gnu"
target = "x86_64-unknown-linux-gnu"
root = "order-service@0.3.0#path:."

[[resolution.edge]]
from = "order-service@0.3.0#path:."
dependency-key = "util"
to = "util@0.1.0#path:crates/util"
kind = "normal"               # normal | dev | tool
```

- 内容稳定排序；不得记录时间戳、绝对路径、凭据。
- 应用和 Workspace **必须**提交 `x.lock`。
- 构建开关：
  - `--locked`：Lockfile 需要更新时失败，报 `X-E8007`；
  - `--offline`：禁止网络访问；
  - `--frozen`：同时等于 `--locked` 和 `--offline`。
- 下载内容的摘要或签名不匹配时报 `X-E8010`，构建中止。

## 6. 构建：Action DAG 与构建键

每个 Action 必须声明以下字段：

```text
kind | tool + digest | args | cwd | inputs[] | outputs[] | env allowlist
host | target | timeout/memory limit | cache policy
```

构建键至少包含：

```text
源码树摘要 | manifest/lock 摘要 | 编译器与 std 身份 | target triple + CPU 特性
profile（含 panic 策略） | Feature 集与解析域 | 依赖工件 ID | 链接器/SDK 身份 | @cfg 输入 | include_str/include_bytes 文件摘要
```

- 未声明的环境、时间、随机数、网络输入不得影响可缓存的 Action。
- `x build --plan --format json` 输出 `plan-v1`。
- **源码优先**：X 包的权威形态是源码。预编译工件只是可删除的缓存，未命中或校验失败时回退到源码构建。X ABI 稳定之前，不得以纯二进制形式发布 X 库。
- 1.0 **没有**通用构建脚本：`@cfg`、`include_str`/`include_bytes` 和 `[target.*.link]` 覆盖了确定性需求。沙箱构建脚本留待 1.0 后的 RFC。

## 7. 命令契约（按阶段）

| 命令 | 阶段 | 说明 |
|---|---|---|
| `x init` / `x new <name>` | P1 | 生成[项目模板](../../docs/repository.md) |
| `x check` / `x build` / `x run` | P0 | `--release`、`--target`、`--message-format json` |
| `x test` | P1 | 运行 `@test` 用例与 `tests/`；`--bench`（P2）；`conformance` 子命令（P0，仓库内部） |
| `x fmt [--check]` | P1 | — |
| `x add/remove`、`x tree`、`x why`、`x update`、`x lock check` | P2 | — |
| `x fetch`、`x vendor`、`x audit`、`x lock diff` | P3 | — |
| `x publish [--dry-run]`、`x yank` | P4 | 发布前执行 API diff 与 SemVer 门禁 |
| `x doc`、`x lsp`、`x mcp`、`x repl`、`x debug`、`x completions` | P3 | — |
| `x explain X-E####` | P1 | 离线展示诊断说明 |
| `x query --json <查询>` | P1 | 机器可读查询 |

所有命令都必须同时提供人类可读文本和带版本号的 JSON 输出，并且在非 TTY 环境下行为稳定。

## 8. 源替换与镜像（P3，原始需求“x proxy / replace”）

```toml
# .x/config.toml 或用户级配置
[source.replace]
"registry:official" = "registry:corp-mirror"

[source.corp-mirror]
url = "https://mirror.corp.invalid/x"
```

- 源替换必须显式配置，并记入审计日志。
- 镜像返回的内容必须与 Lockfile 中的摘要一致，否则报 `X-E8010`。

## 9. 供应链要求（P3–P4）

- Registry 工件必须内容寻址，并带签名（Sigstore 无密钥签名，与工具链发布相同，见 [ADR-0008](../../docs/decisions/ADR-0008-pre-kickoff-decisions.md) K9）和 SLSA Provenance。
- `x audit` 根据 Advisory 数据库检查锁图。
- `x sbom` 输出 CycloneDX JSON；SPDX 作为可选导出格式（P4）。
- Lockfile 与诊断中不得出现 Token、凭据或私钥路径。

## 10. 规则与诊断

| Rule ID | 诊断 |
|---|---|
| RULE-PKG-PARSE | X-E8001 |
| RULE-PKG-UNKNOWN | X-E8002 |
| RULE-PKG-NAME | X-E8003 |
| RULE-PKG-IMPORTROOT | X-E8004 |
| RULE-PKG-CYCLE | X-E8005 |
| RULE-PKG-PATHESCAPE | X-E8006 |
| RULE-PKG-LOCKED | X-E8007 |
| RULE-PKG-FEATURE | X-E8008 |
| RULE-PKG-CONFLICT | X-E8009 |
| RULE-PKG-DIGEST | X-E8010 |
