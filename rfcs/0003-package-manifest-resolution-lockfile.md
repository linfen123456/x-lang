# RFC-0003：包身份、Manifest、依赖解析与 Lockfile

> 状态：Proposed
> 日期：2026-08-17
> 目标阶段：P0 最小 PackageId/Path Workspace/ResolvedGraph，P2 完整解析原型，P3 工程化
> 依赖：RFC-0001 的包根和直接依赖规则
> 相关缺口：`GAP-DX-06`、`GAP-GOV-02`、`XLF-09-017`
> 正式产物：接受后生成 `specs/packages/manifest.md`、`resolution.md` 和 `lockfile.md`。

## 1. 摘要

本提案定义 XPM 的包身份、`x.toml`、Workspace、直接/传递依赖、版本选择、受控多主版本、Feature Resolution Domain、`x.lock`、Git/Path/Registry 来源和基础供应链策略。XPM 负责确定“使用哪些包”，不负责构建动作调度。

## 2. 目标与非目标

### 2.1 目标

- 相同 Manifest、索引、策略和目标产生字节一致的 Lockfile；
- 冲突有最小约束链和可操作修复；
- 源码只能访问显式直接依赖；
- 支持 Workspace、Registry、精确 Git、Path、Vendor 和离线构建；
- 在类型身份可解释的前提下支持迁移期多主版本；
- 将来源、摘要、签名、许可证和公共依赖纳入治理。

### 2.2 非目标

- 不定义语言 Import 语法和 Trait 解析；
- 不定义 Action DAG、编译缓存或 C/JVM 构建；这些由 RFC-0004 负责；
- 不在 1.0 提供任意联网 Build Script 或过程宏；
- 不保证直接兼容 Cargo/npm/Maven 的全部历史语义。

## 3. 核心术语与责任边界

```text
x.toml
  → XPM validate/resolve/fetch/verify
    → x.lock + ResolvedPackageGraph
      → XBuild
```

- **Package Name**：经 Unicode/大小写/保留名规则规范化的发布名称。
- **Source ID**：Registry、Git、Workspace/Path 或 Vendor 的规范来源身份。
- **Package ID**：`normalized-name + SourceId + exact-version-or-commit`；依赖 Alias 不参与真实身份。
- **Dependency Key**：当前包源码中使用的包根名称，可以与 Package Name 不同。
- **Resolution Domain**：Feature 和依赖选择互不污染的 `target-normal`、`host-build`、`dev-test` 等域。
- **Public Dependency**：类型出现在当前包公开 API 中的直接依赖。

## 4. `x.toml` 候选结构

```toml
manifest-version = 1

[package]
name = "order-service"
version = "1.4.0"
edition = "2026"
publish = true
license = "Apache-2.0"
repository = "https://example.invalid/acme/order-service"

[workspace]
members = ["packages/*", "apps/*"]
default-members = ["apps/server"]
exclude = ["experiments/*"]
resolver = "1"

[workspace.package]
edition = "2026"
license = "Apache-2.0"

[workspace.dependencies]
log = "^2.3"

[dependencies]
log = { workspace = true }
codec = { version = "^3.1", public = false }
protocol_v2 = { package = "protocol", version = "^2.8" }
ui = { git = "https://example.invalid/ui.git", rev = "<commit>" }
http = { version = "^2.0", default-features = false }
tls = { version = "^1.0", optional = true }

[build-dependencies]
bindgen = { version = "^1.2", capabilities = ["read:include"] }

[dev-dependencies]
testkit = "^4.0"

[features]
default = []
tls = ["dep:tls", "http/tls"]

[policy]
undeclared-transitive-imports = "deny"
public-dependency-leaks = "deny"
unsafe-build-scripts = "deny"
```

本示例是 Schema 候选而非当前可执行配置。正式 Schema 还必须定义 Library/Binary/Test/Example/Bench Target、包 include/exclude、最低 X 版本、未知字段和迁移策略。

## 5. 直接与传递依赖

1. 源码只能导入 `[dependencies]` 中直接声明的 Dependency Key。
2. `[dev-dependencies]` 只进入测试、示例和基准域；`[build-dependencies]` 只进入 Host Build 域。
3. 传递依赖进入 `x.lock`、SBOM、漏洞和许可证图，但不进入名称解析。
4. 依赖默认 Private。公开签名暴露第三方类型时必须声明 `public = true`，否则 API Lint 阻断。
5. 推荐使用本地领域类型和 `lib.x` Facade 隔离第三方类型；Public Dependency 的 SemVer/来源变化传播为当前包兼容风险。

```x
use http::Client; // http 必须是直接 Dependency Key
```

## 6. 版本策略与受控多版本

1. 默认在同一 Resolution Domain 内，对相同 `normalized-name + SourceId` 选择一个满足全部兼容约束的最高稳定非预发布版本。
2. Prerelease 必须显式请求；Resolver Tie-break 与网络响应或索引遍历顺序无关。
3. 不兼容主版本默认给出冲突；只有显式 Dependency Key/Alias 和 Workspace Policy 许可时才能并存。
4. 多版本拥有不同 Package ID 和类型身份，禁止隐式转换、统一 Trait impl 或 ABI 混用。
5. Core、Runtime ABI、Public Dependency 和安全关键包可声明严格 One-Version，禁止例外。
6. 多版本例外必须记录理由、Owner 和到期日；到期阻断更新/发布，但不破坏已有 Lockfile 的离线复现。

```toml
[resolver.multiple-versions]
"protocol@registry:official" = {
    allow = ["2", "3"],
    reason = "migration",
    owner = "team-api",
    expires = "2027-01-01"
}
```

XPM 首个 Resolver 建议使用 PubGrub，但规范只承诺确定结果、版本策略和冲突解释，不永久绑定算法。

## 7. Feature Resolution Domain

- Feature 只在同一 `PackageId + ResolutionDomain` 内单调合并；
- 至少隔离 `target-normal`、`host-build` 和 `dev-test`；
- Build Dependency 的 Feature 不污染 Target Dependency；
- Feature 只能增加能力，不能删除 API、改变类型/所有权/错误语义或关闭安全检查；
- 互斥后端使用显式配置枚举、Target 或不同包，不使用冲突 Boolean Feature；
- 默认 Feature 最小；依赖 Feature 使用命名空间；
- `all-features` 只表示所有可共存 Feature；
- CI 覆盖 minimal/default/all-compatible 和风险驱动 Pairwise 组合。

### 7.1 激活语义与失败行为

- `optional = true` 的直接依赖默认不进入图；`dep:key` 激活当前依赖表中名为 `key` 的 Optional Dependency，并隐藏其同名隐式 Feature；
- `key/feature` 只激活已声明的直接依赖 `key` 上公开的 `feature`；依赖未激活、key 未声明、Feature 未知或指向传递依赖时稳定报错；
- 1.0 不提供 Weak Activation。若需要“仅当依赖已激活时再启用其 Feature”，必须由后续 RFC 引入独立语法，不把 `key/feature` 隐式解释为弱激活；
- Feature 引用形成有向图；自环或多节点环即 Manifest 错误，不依赖固定点求值顺序；
- Feature 激活不能跨 Resolution Domain。`target-normal` 不能激活 `host-build`/`dev-test` 的依赖或 Feature，反向同理；共享需求必须在各域显式声明；
- 同一 `PackageId + ResolutionDomain` 内重复激活取有序集合并集；未知 Feature、禁止组合或 Domain 穿越必须在生成 Lockfile 前失败。

示例中的 `tls` Feature 同时激活 Optional Dependency `tls` 和直接依赖 `http` 的公开 `tls` Feature；它不能激活未声明的传递依赖。

## 8. Workspace

- 显式定义 `members/default-members/exclude`；成员匹配和排序确定；
- 默认禁止嵌套 Workspace；越出根目录的 Path Dependency 需要 Policy 授权；
- Workspace 可以统一继承 Edition、许可证、版本和依赖约束；成员可以收紧但不能静默放宽安全策略；
- 所有依赖边形成无环 DAG；1.0 连 Dev-only Cycle 也拒绝，保持工具一致；
- Workspace 根拥有 Resolver、来源 Allowlist、严格单版本、多版本例外和供应链 Policy；
- 成员名称和 Dependency Key 在规范化后必须唯一。

## 9. Git、Path、Registry 与 Vendor 来源

### 9.1 Git

```toml
[dependencies]
json = {
    git = "https://github.com/example/x-json.git",
    rev = "6f1e8d03a35c7f764b33f32e8ac7f1c0dbe41f72",
    subdir = "packages/json"
}
```

- Manifest 的 Branch/Tag 只是请求；Lockfile 必须固定 Commit 和规范源码树摘要；
- Git URL 规范化但不得静默切换来源；更新只能通过显式 `x update`；
- Submodule/LFS 默认拒绝，启用时必须递归固定 Commit/Object Digest；
- 不读取脏工作树、Hook 或未声明全局 Git 配置；凭据只用于 Fetch，不能进入 Lockfile、日志或 Build Script；
- 稳定 Registry 发布原则上要求将 Git 依赖替换为 Registry 版本；Exact Commit 例外需要组织 Policy。

### 9.2 Path/Workspace

- Path 必须规范化，默认保持在 Workspace 根内；
- 源码摘要、成员身份和相对路径进入构建键；
- 发布包不能携带消费者无法解析的本机 Path；
- 符号链接不得逃逸授权根。

### 9.3 Registry

- Package Version 的源码内容不可变并内容寻址；
- 同名异源、Mirror、Proxy 和 Registry Replacement 必须显式配置并进入审计；
- Yank 版本不参与新解析，但已有 Lockfile 仍可复现；安全撤回由独立 Advisory/Deny Policy 阻断；
- 下载必须验证 Digest，签名不能替代内容摘要。

### 9.4 Vendor

- `x vendor` 只从已锁定图生成并带 Vendor Manifest；
- Vendor 内容默认只读，Patch 必须形成新摘要和来源记录；
- `--offline --locked` 不得产生 DNS/网络请求；缺包时报告精确 Package ID 和补齐命令。

## 10. `x.lock` 候选结构

```toml
lock-version = 1
manifest-digest = "sha256:..."
resolver-version = "1"
policy-digest = "sha256:..."

[[package]]
id = "codec@3.2.1#registry:official"
name = "codec"
version = "3.2.1"
source = "registry:official"
content-digest = "sha256:..."
signature = "sigstore:..."
provenance = "slsa:..."
yanked = false
license = "MIT"

[[resolution]]
id = "target-normal:x86_64-pc-windows-msvc"
domain = "target-normal"
host = "x86_64-pc-windows-msvc"
target = "x86_64-pc-windows-msvc"
root = "order-service@1.4.0#workspace"

[[resolution.node]]
package = "order-service@1.4.0#workspace"
features = ["tls"]
cfg = "true"

[[resolution.node]]
package = "codec@3.2.1#registry:official"
features = ["std"]
cfg = 'target_os = "windows"'

[[resolution.edge]]
from = "order-service@1.4.0#workspace"
dependency-key = "codec"
to = "codec@3.2.1#registry:official"
kind = "normal"
public = false
cfg = "true"

[[git-source]]
url = "https://github.com/example/x-json.git"
commit = "6f1e8d..."
tree-digest = "sha256:..."
subdir = "packages/json"

[[foreign-resolution]]
id = "maven:jvm-21:sha256:..."
ecosystem = "maven"
adapter = "x-foreign-maven@1"
external-lock-digest = "sha256:..."
host = "x86_64-pc-windows-msvc"
target = "jvm-21"
abi = "jvm-module-path"
```

`resolution.node` 是版本化图节点，记录每包在该 Domain 实际启用的 Feature 和规范化 Target/Cfg 条件；`resolution.edge` 记录来源节点、Dependency Key/Alias、目标 Package ID、`normal|build|dev` 边类型、Public 标记和激活条件。Host、Target 和 Domain 共同构成解析实例身份，同一 Package ID 可在不同 Domain 有不同 Feature 集。工具必须从边而非全局包列表实现 `tree/why/audit/SBOM`。

`foreign-resolution` 是 RFC-0004 所定义冻结外部图的引用；`x.lock` 至少内嵌可审计节点/边及制品摘要，`external-lock-digest` 只证明原生态 Lockfile，不能代替该图。Lockfile 必须稳定排序且不可手改，禁止记录凭据、用户绝对路径、下载时间或其他不稳定字段。

### 10.1 P0 最小图契约

P0 即冻结 `PackageId`、Path/Workspace Source ID、`resolution.node/edge`、Host/Target 和 `normal|build|dev` 边类型；只需解析单包及 Workspace Path Dependency，不需要 SemVer、Git、Registry 或 PubGrub。P2 在同一版本化契约上增加完整来源和解析，不允许 XBuild 使用临时的第二套 `BuildInput`。

### 10.2 Lockfile 政策

- 应用、工具和最终制品 Workspace 必须提交 `x.lock`；
- 发布库可以提交用于自身 CI 的 Lockfile，但不得约束下游解析；
- `--locked` 禁止更改 Lockfile；`--offline` 禁网；`--frozen` 等于两者同时启用；
- Lock Schema 有主版本、未知字段规则、迁移工具和 N-1/N-2 兼容测试。

## 11. 命令契约

```text
x add/remove <package> [--dev|--build|--public]
x resolve [--target <triple>]
x update [package] [--precise <version>] [--breaking]
x lock check|diff
x tree [--duplicates|--domain|--invert]
x why <package>
x explain <conflict-id>
x fetch --locked
x vendor [--locked]
x audit
x publish --dry-run
x yank/unyank
```

所有命令同时提供人类文本和版本化 JSON。解析失败必须包含最小冲突集合、约束来源、Resolution Domain 和可行修复。

## 12. 安全和供应链

- 新直接依赖记录用途、Owner、许可证、维护状态、替代项、Public 状态和执行权限；
- Build Script、过程宏、插件和 Foreign Adapter 是高权限依赖，默认无网络、源码只读、声明输入输出和 Capability；
- Registry 支持摘要、签名、透明日志、SBOM、Provenance、密钥轮换、Yank、撤回和离线恢复；
- Source Allowlist 和同名异源检查先于版本解析；
- Lockfile 和诊断不输出 Token、SSH Key、Authorization Header 或凭据路径。

## 13. 验收

- Manifest/Lock Golden、Round-trip、未知字段、Schema 迁移；
- 同输入跨 OS、索引/网络返回顺序和并行度产生字节一致 Lockfile；
- PubGrub 实现与小图穷举 Oracle 差分；
- Alias、Prerelease、Yank、同名异源、受控多版本和冲突解释语料；
- 三个 Feature Domain 隔离及组合测试；
- 传递依赖 Import、Public Dependency 泄漏和过期多版本例外产生稳定错误；
- Digest/签名篡改、Mirror 替换、撤回和离线恢复演练；
- N-1/N-2 Lockfile 迁移与 `--locked/--offline/--frozen` 行为测试。

## 14. 未决问题

| 问题 | Owner | 截止阶段 | 未达成一致时的失败回退 |
|---|---|---|---|
| Package Name 的 Unicode/ASCII、连字符和保留名策略 | Language + Registry WG | P0 Parser 冻结前 | 仅允许小写 ASCII、数字和单连字符，拒绝 Unicode 名称 |
| Public Dependency 是否必须显式 `public = true` | Package WG | P2 Lock Schema 冻结前 | 必须显式声明；工具只提供 Fix-it，不自动修改 |
| Exact Git Commit 在公开 Registry 包中的政策 | Supply-chain WG | P3 Publish 开启前 | Registry 发布拒绝任何 Git 依赖 |
| 是否提供最低版本测试模式 | Resolver WG | P3 Resolver 稳定前 | 不承诺最低版本模式，只保留锁定图与最高兼容解析 |
