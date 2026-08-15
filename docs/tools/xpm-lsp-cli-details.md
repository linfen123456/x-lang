---
doc_id: DOC-TOOLS-XPM-LSP-CLI-DETAILS
authority: implementation
owner: role/tooling-team
backup_owner: role/security-team
version: "1.0"
maturity: EXTENDED
status: 草案
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-013, XLF-01-014, XLF-02-004, XLF-02-005, XLF-02-007, XLF-02-013, XLF-02-014, XLF-03-005, XLF-09-015, XLF-09-017, XLF-10-012, XLF-11-001, XLF-11-004, XLF-11-007, XLF-11-013, XLF-12-001, XLF-12-003, XLF-12-004]
---
# `x` CLI、XPM 求解器与 LSP 增量服务实施细则

> 本文补齐[CLI 契约](./cli.md)、[XPM 契约](./package-manager.md)、[LSP/DAP 规范](./lsp-dap.md)缺少的执行算法。公共结果结构以[工具链公共接口](./contracts/contract.md)为准，不在本文另造协议。尚未实现的命令、测试、Registry、IDE 与缓存全部标记为 `planned`。

## 1. 目标、边界与实施顺序

目标是让工程团队可直接拆出：命令解析/执行、manifest/lockfile、确定性依赖求解、下载缓存、LSP snapshot/取消/增量查询，以及 Watch/REPL 的安全边界。

实施顺序：

```text
P1: x check/build/run + x.toml entry + 冷编译
P2: test/fmt/doc + Query/缓存集成
P3: XPM/lock/offline + LSP/DAP + watch/repl
P4: publish/SBOM/API diff/签名与稳定发布
P5/P6: AI/语义搜索/实验工具，默认关闭
```

非目标：让 CLI 修改用户业务代码、在 offline 模式访问网络、在 LSP 消息线程执行长编译、从不可信 build script 读取任意环境/秘密、把 AI `fix` 自动应用或发布、为所有包提供预编译 `.xlib` 兼容承诺。

## 2. `x` 命令执行内核

### 2.1 解析阶段

`CommandRequest` 构建顺序固定：

1. 只解析全局选项和 subcommand；`--` 后原样传给目标程序。
2. 拒绝未知/重复冲突 flag、数值溢出、非法 UTF-8 展示输入和缺少值。
3. 解析 `--manifest-path`，通过 workspace 目录句柄打开并在打开后验证实际文件身份属于授权根；不能只依赖字符串 canonicalize，后续读取复用同一句柄。
4. 读取 `x.toml`，应用优先级 `CLI > profile > target defaults > toolchain defaults`；环境变量只从 declared allowlist 进入。
5. 构建 `ExecutionPlan` 并输出可审查摘要；此阶段不写最终文件、不启动网络或子进程。

`ExecutionPlan` 概念字段：`command,workspace,package_selection,target,profile,features,offline,locked,steps,declared_inputs,output_roots,limits`。每一步声明输入/输出、网络/进程 capability、取消点和缓存 key。

### 2.2 执行与提交

Driver 按 DAG 执行步骤；同一输出路径有排他锁。中间产物写 request 临时目录，完成后 `validate → optional fsync → atomic replace → publish manifest`。Ctrl-C 第一次请求协作取消，等待 grace；第二次可强杀子进程树，但仍不得删除 workspace 源文件。

退出码保持公共矩阵：1 用户/配置错误，2 编译/测试失败，3 环境/工具/网络/签名失败，4 取消，5 工具内部错误。目标程序的退出码在 `x run` 结果字段保留，但 CLI 自身 status 不能与它混淆。

### 2.3 子进程与输出

子进程从最小环境开始，显式继承 PATH/toolchain/用户声明变量；秘密值只以受控引用传递并加入脱敏表。stdout/stderr 独立流式读取，单流与总输出有上限；超限继续 drain 或终止子进程，防止管道死锁。取消结束整个 process group/Job Object。

非 TTY 或 `--format json` 禁止 ANSI 和动态进度条；JSON stdout 只输出协议，日志进 stderr。`--color always` 也不能污染 JSON。

## 3. 逐命令可落地行为

| 命令 | 核心步骤 | 不写/不做 | 原子输出 |
|---|---|---|---|
| `x check` | manifest→resolve lock→Compiler check | 不链接/运行 | diagnostics/report |
| `x build` | resolve→compile→codegen→link→manifest | 不运行程序 | `target/<triple>/<profile>` |
| `x run` | build→选择唯一 executable→受控 spawn | 不把程序参数解释为 x flag | build manifest/run report |
| `x test` | discover→TestPlan→隔离执行→聚合 | 不无限 retry | TestReport/log refs |
| `x fmt` | parse→format→parse/semantic guard→diff | `--check` 不写盘 | patch 或原子替换 |
| `x doc` | API index→render→doc-test→link check | doc-test 失败不发布 | site/index |
| `x repl` | session snapshot→parse/type/execute | 默认无插件/网络 | 可选历史（脱敏） |
| `x clean` | enumerate allowlisted outputs→展示→删除 | 不接受 workspace root/未解析 glob | CleanReport |
| `x publish` | locked build→test→API diff→SBOM/sign→upload→confirm digest | 不自动改版本 | receipt |
| `x doctor` | read-only probe | 不自动安装/提权 | DoctorReport |

P1 的 `run` 必须从 manifest 选择 artifact，不能猜测 `target/` 中最新文件。`publish` 在 P4 前保持 disabled/experimental。

## 4. Manifest 与 workspace 解析

读取 `x.toml` 时保留字段 Span 以定位错误，随后转 canonical model。workspace 成员路径解析符号链接后必须在 root；package 名、版本、Edition、entry、target、feature 和 dependency name 分别校验。未知字段在当前 schema 默认报错，除非位于明确的 `metadata` 扩展区。

Feature 展开使用有向图固定点：

1. 从 CLI/default features 建 active queue。
2. 展开 feature→local feature/dependency feature/optional dependency 边。
3. 检测未知引用和循环；纯幂等 feature 环可归并 SCC，导致条件矛盾的环报错。
4. canonical 排序得到 `FeatureSet` 和 fingerprint。

Target-specific dependency 必须在解析目标集合后选择；lockfile 可记录多 target set，但一次 build 不引入无关目标的构建依赖。

## 5. XPM Registry Snapshot 与缓存

### 5.1 Snapshot

求解器不直接发网络请求，而只读取不可变 `RegistrySnapshot{registry_id,revision,packages,signing_roots,revocations,fetched_at,digest}`。`fetched_at` 仅用于缓存过期提示和审计展示，不参与 snapshot digest、求解、lock digest 或 build fingerprint；决定语义的是 revision、内容、信任根/撤回集及其 digest。联网 refresh 是前置步骤，成功验证并原子发布 snapshot 后才交给 resolver。这样相同语义输入可重放。

`--offline` 禁止 DNS、HTTP、Git fetch 和签名在线查询，只使用指定 snapshot/cache/vendor；缺失即 `XPM_E_OFFLINE_MISS`。`--locked` 要求 manifest/target/features 与 lock 输入 fingerprint 相符，不运行会改变 lock 的求解。

### 5.2 下载管线

```text
resolve URL/source → allowlist/redirect validation → temp download
→ compressed size limit → digest/signature/revocation/license check
→ safe unpack(path traversal/symlink/bomb limits)
→ content hash → atomic cache publish
```

任何阶段失败都不进入可用缓存；失败包移入有界 quarantine 供审计。构建脚本默认不在下载阶段执行。Git dependency 固定 commit；branch/tag 只能在显式 update 时解析并写入 lock。

## 6. 确定性依赖求解

### 6.1 输入与术语

输入必须完整：root manifests、可见 registry snapshots、target set、FeatureSet、toolchain/Edition、旧 lock（偏好而非真相，`--locked` 除外）。Package identity 是 `(name,source,version)`，同名不同源不能静默合并。

约束表示 `Term(package, version_set, positive|negative)`；incompatibility 记录一组不能同时成立的 terms 和 cause。决策栈项含 `level,package,version,derived_from`。

### 6.2 PubGrub 风格算法

1. 把 root dependency 转为 incompatibilities。
2. **unit propagation**：若 incompatibility 只剩一个未满足 term，推导其反面并记录 cause；冲突则进入 resolution。
3. 选择未决定 package；固定选择顺序为“约束最紧、名称/source canonical 次序”。
4. 从允许版本中选择：优先兼容旧 lock，其次最高非撤回稳定版本；完整 tie-break 写入 solver version。
5. 加入所选版本依赖 incompatibilities，回到 propagation。
6. 冲突时沿 cause 图求最近共同决策层，生成 learned incompatibility，回跳而非仅回退一个版本。
7. root 冲突即无解，压缩 cause graph 输出最小可解释链。
8. 成功后 canonical 排序 Resolution，重新验证所有约束并生成 lock digest。

候选耗尽是显式 NoSolution：当 package 的允许 version set 为空，立即生成包含造成空集的 incompatibilities；不得重复选择相同 package/version。终止度量为“尚未尝试的有限候选数 + 当前决策层可回跳次数”；每次 decide 消耗一个候选，每次 conflict learning 新增此前不存在的 canonical incompatibility 并回跳到更低层。若归一化后得到重复 learned incompatibility，求解器必须标记当前决策候选已耗尽并继续回跳；若已在 root 则返回 NoSolution，不能原地重复 propagation。RegistrySnapshot 对每个 package 的候选列表在求解开始前冻结、去重并有限化；超过候选/learned incompatibility/迭代预算返回 `XPM_E_SOLVER_LIMIT`，与语义上的 `XPM_E_CONFLICT/NoSolution` 区分。

伪代码：

```text
loop:
  conflict = propagate(assignments, incompatibilities)
  if conflict:
    learned, backjump = resolve_conflict(conflict)
    if backjump is none: return NoSolution(explain(learned))
    rewind(backjump); add(learned); continue
  pkg = choose_package()
  if none: return verify_and_lock(assignments)
  ver = choose_version(pkg, old_lock, policy)
  decide(pkg, ver); add_dependencies(pkg, ver)
```

求解 deadline、package/version/incompatibility 数量均受限。超限返回 `XPM_E_SOLVER_LIMIT` 并附统计，不输出猜测 lock。相同输入+solver version 必须生成字节相同 lock。

### 6.3 Feature 与多版本策略

同一 package identity 的 feature 通常取并集；若语言决定允许同一包多版本，则不同 version 是不同 PackageId，类型/ABI 不自动兼容。可选依赖只在对应 feature 激活时进入图。platform cfg 在目标集合确定后求值，不读取 host。

## 7. Lockfile 写入、迁移与回滚

新 lock 先生成内存模型，验证所有 edge 指向存在 PackageId、无重复 ID、target set 和 toolchain fingerprint 一致，并按来源要求不同信任字段：Registry 必须有 registry identity、immutable revision、package checksum、签名/签名策略与撤回快照；Git 必须有 canonical repository identity、不可变 commit、tree/content digest，并记录签名验证状态而不伪造 Registry 签名；Path 必须有 workspace/vendor-root 相对 canonical path、内容 digest 和 `local=true`，不得写虚假远端 checksum/signature。序列化固定 UTF-8/LF/字段与包排序，写临时文件后原子替换。

build fingerprint 只包含会改变构建语义的 manifest/lock、source content、compiler/toolchain、target/profile/Edition/Feature 和 declared environment digest。Registry 的 `fetched_at`、下载时间、缓存路径，以及 LSP 的内存 document/runtime snapshot ID 都不得进入 build fingerprint；LSP snapshot 仅用于请求隔离和结果新鲜度。

`x update` 先展示 `{added,removed,changed,feature_change,security_change}`，成功才写。schema major 迁移使用 `x lock migrate`，保存旧 lock backup/reference；迁移不访问网络，除非用户显式 refresh。求解回归时可恢复旧 lock+snapshot 或 vendor 源码，不能采用哈希不匹配缓存。

## 8. LSP 进程与 snapshot 架构

```text
JSON-RPC reader → request router (快速)
                    ↓
Workspace actor → DocumentStore(versioned snapshots)
                    ↓
Compiler QueryEngine(read-only snapshot) → response publisher
```

消息循环只做解析、大小限制、capability/version 校验和调度。每个 workspace 串行提交文档版本，但分析请求并发运行于不可变 snapshot。磁盘 watcher 变更和编辑器 overlay 分层；打开文档时 overlay 权威，关闭后回到磁盘 snapshot。

### 8.1 文档变更

`didOpen` 创建 version；`didChange` 要求 version 严格递增。LSP `contentChanges` 必须**按数组顺序**应用：第 1 个 range 相对 base text，第 n 个 range 相对前 n-1 个 change 应用后的临时文本；每步按协商 position encoding 转 byte range 并验证。整个批次在私有临时 rope 上事务执行，任一步无效则丢弃整批并保留旧 snapshot，全部成功后才一次发布新 version。不能把所有 range 预先换算到 base 后排序/并行应用。

旧 snapshot 的查询可完成供缓存复用，但发布前必须比较 current document version/request cancel epoch。旧结果丢弃，不撤回新诊断。

### 8.2 请求取消与 deadline

Router 创建 `RequestContext{id,workspace_snapshot,document_version,cancel,deadline,limits}`，传到 QueryEngine。收到 `$/cancelRequest` 只标记 token，不在消息线程等待。Compiler 在 I/O、query wait、前端和索引循环检查。取消后禁止 publish response/diagnostics；若 JSON-RPC 要求取消响应，使用标准错误并不带过时 partial result。

### 8.3 诊断发布

每个诊断携带 snapshot/version、稳定 code 和 byte Span；发布时转换为客户端 position encoding。相同 `(code,span,message-key)` 去重并 canonical 排序。解析错误可发布快速诊断，语义诊断随后以相同 version 替换整组；不能把两版混合。

## 9. LSP 功能算法

### 9.1 Completion

1. 取 position 的 syntax/AST context；错误节点时向最近完整 scope 回退。
2. 从 local scope、members、imports、keywords 收集候选。
3. 用 expected type/Trait obligation 过滤但不隐藏所有不确定候选。
4. 固定评分：精确前缀、作用域距离、类型相容、稳定 tie-break；AI/使用历史不得影响默认确定性排序。
5. 截断到 limit，设置 `isIncomplete=true`；resolve 请求延迟加载文档与 edits。

自动 import edit 必须基于同一 version，且经过 Formatter/import policy；客户端应用前若版本变化则失效。

### 9.2 Definition/References/Rename

definition 通过 `Token→AstNode→DefId→definition Span`，不做文本搜索。references 使用 snapshot-indexed DefId inverted index；索引条目含 file fingerprint。rename 先收集所有引用，校验可编辑 workspace、命名冲突、生成 changes，最后返回 WorkspaceEdit；工具自身不写盘。字符串/反射引用是否参与必须由语言规则明确。

### 9.3 Hover/Code Action/Formatting

hover 只展示已验证类型/签名/文档，错误状态标记“推断不完整”。Code Action 的 Fix-it 必须来自相同诊断和 version，分 `safe` 与 `requires_review`；默认不自动应用。formatting 调用共享 Formatter，不在 LSP 复制规则。

## 10. DAP 与 SourceMap 最小闭环

P3 DAP 顺序：launch/attach 权限 → 读取 ArtifactManifest/SourceMap → 设断点 → continue/step → stack/scopes/variables → disconnect/terminate。断点从源码 Span 映射到一个或多个机器位置；无法绑定返回 `verified=false + reason`，不能默默移动到无关行。

变量展开使用 `variablesReference` 代次表和深度/数量/字符串长度限制。evaluate 默认只读且受 timeout；禁止绕过不可变/unsafe/sandbox。脱糖函数、闭包和 async frame 的显示规则必须记录 compiler version；async 未稳定前不承诺相应调试体验。

## 11. Watch、REPL 与 Shell completion

### 11.1 Watch

平台 watcher 事件先 debounce/coalesce，再通过内容 hash 判断真实变化。单次 build 运行时到达新变更只设置 dirty；当前 build 完成/取消后基于最新 snapshot 再构建，避免无限并发。热重启先 graceful shutdown 旧子进程，deadline 后终止进程树，再启动已验证新 artifact。状态保持热重载是独立实验 RFC，不属于 watch 基线。

### 11.2 REPL

每次输入形成递增 cell module，使用同一前端/类型规则；成功 cell 才提交 session，失败保持上一状态。Ctrl-C 取消当前 cell，不销毁历史 session；`:reset` 显式清空。历史文件需权限限制和秘密过滤，默认不执行任意 build script/plugin/network。

### 11.3 Shell completion

completion 从版本化 command schema 生成 bash/zsh/fish/PowerShell 脚本。生成是纯函数且有黄金测试；动态包/target completion 通过快速、只读、可超时子命令完成，不触发网络求解。

## 12. 缓存、离线与可复现性

工具缓存 key 至少包含 tool/compiler version、schema、target/profile/Edition/Feature、declared env、source/lock/snapshot fingerprint。时间、绝对 workspace 路径和随机 seed 不得无意进入语义 hash。cache hit 仍验证 blob hash/schema。

离线含义贯穿所有步骤：XPM、doc links、diagnostic help、AI 和 toolchain fetch 均不得联网；缺失离线文档时提供本地错误而不是 fallback 云端。`x explain` 的核心错误说明必须随工具链发布。

## 13. 安全与资源边界

| 风险 | 控制 |
|---|---|
| 路径穿越/恶意 archive | canonical root guard、safe unpack、数量/大小限制 |
| Registry/代理投毒 | TLS policy、digest、签名、snapshot、revocation |
| build script/plugin | 默认禁用；能力沙箱、声明输入输出、无秘密/网络 |
| LSP 恶意 URI/超大文档 | scheme/root allowlist、16 MiB、请求/诊断上限 |
| 命令/日志注入 | 不拼 shell、参数数组、终端控制字符转义 |
| 凭据泄漏 | 引用传递、环境 allowlist、统一脱敏、禁止 artifact 写入 |
| 取消残留进程 | process group/Job Object、drain pipes、临时目录清理 |
| AI 自动修改 | diff、权限、测试、人工确认；默认不应用/发布 |

## 14. 实施任务切片

### TASK-P1-TOOLS-001 / 切片 A：Command kernel 与 P1 三命令

- 输入：公共 Command/Compiler contract。
- 输出：parse/plan/execute/commit、`check/build/run`。
- 验收：退出码、JSON/stdout 分离、取消、原子 artifact。
- 回滚：上一 CLI schema + 冷编译。

### TASK-P3-TOOLS-001 / 切片 A：Manifest、Feature 与 lock reader

- 输出：canonical model、Span diagnostics、`--locked/--offline` 守卫。
- 验收：路径/feature/target 负向语料；不联网可证明。
- 回滚：vendor + 已验证旧 lock。

### TASK-P3-TOOLS-001 / 切片 B：Resolver 与 Registry cache

- 输出：PubGrub-style solver、explanation、canonical lock、safe cache。
- 验收：相同输入字节相同；无解最小链；坏包不入缓存。
- 回滚：旧 solver version/lock/snapshot，不静默换版本。

### TASK-P3-TOOLS-002 / 切片 A：DocumentStore 与基础 LSP

- 输出：initialize/open/change/close、diagnostics、hover/definition。
- 验收：版本/encoding/取消/旧结果竞态。
- 回滚：关闭增量，保留冷 snapshot 分析。

### TASK-P3-TOOLS-002 / 切片 B：Completion/References/Rename/Formatting

- 输出：DefId 索引、WorkspaceEdit、共享 Formatter。
- 验收：冲突、partial、超限、版本变化后 edit 失效。
- 回滚：逐 capability 关闭，不影响诊断。

### TASK-P3-TOOLS-002、TASK-P1-TOOLS-001 / 共享切片：DAP、Watch、REPL

- 独立 capability gate 和进程权限。
- 验收：SourceMap、子进程树、cell transaction、shell matrix。
- 回滚：关闭对应子命令，不改项目文件。

## 15. 规划测试矩阵

| 测试 ID | 场景 | 证据 | 状态 |
|---|---|---|---|
| `TEST-TOOLS-CLI-001` | flag/`--`/TTY/JSON/坏 UTF-8、目录句柄授权 | transcript + CommandResult | planned |
| `TEST-TOOLS-CLI-002` | Ctrl-C、timeout、子进程树、输出满 | cleanup report | planned |
| `TEST-TOOLS-CLI-003` | Watch/REPL/Shell completion | state trace + generated golden | planned |
| `TEST-TOOLS-XPM-001` | manifest、候选耗尽、冲突回跳、多来源信任字段 | resolution/explanation golden | planned |
| `TEST-TOOLS-XPM-002` | 输入乱序、重复/两主机、坏包与安全解包 | lock hash + quarantine report | planned |
| `TEST-TOOLS-XPM-OFFLINE-001` | DNS trap、缓存缺失、vendor、fetched_at 变化 | zero-network/相同 fingerprint | planned |
| `TEST-TOOLS-LSP-001` | 顺序 contentChanges、乱序 version、旧结果、新诊断、语义功能 | protocol/semantic golden | planned |
| `TEST-TOOLS-LSP-CANCEL-001` | 各分析阶段取消/deadline | 无过期 publish | planned |
| `TEST-TOOLS-DAP-001` | 断点/脱糖/坏 map/变量上限 | DAP transcript | planned |

## 16. 来源、验收与回滚

来源覆盖 `XLF-01-013/014`、`XLF-02-004/005/007/013/014`、`XLF-09-015/017`、`XLF-10-012`、`XLF-11-001/004/007/013`、`XLF-12-001/003/004`。AI 命令仅继承 `XLF-03-005` 的可审计价值，不在本文实现模型生成逻辑。

验收必须有确定 lock、离线零网络、供应链负向、LSP 版本/取消、CLI 退出码和子进程清理证据；当前全部为 `planned`。回滚按命令/solver/capability 独立执行，绝不删除源、覆盖脏文件或采用未经验证的缓存。
