---
doc_id: DOC-COMPILER-DRIVER
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-02-003, XLF-02-004, XLF-02-014, XLF-10-012, XLF-11-001, XLF-11-004, XLF-11-013]
---
# 编译 Driver、查询系统与制品清单

> 状态：草案｜Owner：`role/compiler-team`

## CompileRequest / CompileResult

`CompileRequest` 字段：`schema_version:SemVer`、`workspace_root:PathBuf`、`inputs:Vec<PathBuf>`、`target:TargetSpecId`、`profile:ProfileId`、`edition:Edition`、`features:BTreeSet<String>`、`emit:BTreeSet<EmitKind>`、`limits:ResourceProfile`、`cancel:CancelToken`、`previous:SnapshotId?`、`environment:DeclaredInputs`。前置是路径、target、profile、edition 和 feature 已解析，工作区锁已取得；后置是成功返回完整 manifest，失败只返回诊断。环境只接受 `DeclaredInputs`，不得隐式读取秘密、时间或网络。

`CompileResult` 字段：`status:CompileStatus`、`diagnostics:DiagnosticSet`、`artifacts:Vec<ArtifactRef>`、`manifest:ArtifactManifest?`、`stats:CompileStats`、`cache:CacheStats`、`request_id:RequestId`。成功状态不能带阻断错误；取消/资源超限明确区分，均不提交最终产物。

Driver 的阶段状态固定为 `Accepted → Snapshotted → Planned → Executing → Validating → Committing → Completed`，失败可从任一非终态进入 `Failed|Cancelled|TimedOut|ResourceExhausted`。只有 Committing 可以写最终输出；诊断成功但 manifest 缺失、manifest 有重复路径或任一 artifact hash 不符都不能进入 Completed。请求取消在 Committing 开始后只阻止尚未发布的 entry；已经原子发布的完整 manifest 作为 Completed 返回，不能报告 Cancelled 却留下未声明成品。

编译计划按 `source/front-end → VerifiedHirBody → VerifiedMir → [Pass] → Backend → Linker → Manifest` 构建 DAG，每条边记录 schema/fingerprint 和前置 verifier。阶段错误只取消依赖后继；无依赖的诊断查询可继续用于汇总，但不得生成制品。阻断诊断按稳定 `(stage,file,span,code)` 排序，消息本地化不参与排序或缓存 hash。

## QueryEngine 与增量缓存

`QueryKey` 为 `QueryKind + canonical_inputs + compiler_version + edition + target_fingerprint + profile + feature_fingerprint + declared_env_hash + schema_version + pass_version + pipeline_fingerprint`；`QueryValue` 含 `value:ArtifactId`、`dependencies:Vec<QueryKey>`、`fingerprint:Hash32`、`diagnostics`、`cost`、`determinism:Determinism`。查询状态机为 `Vacant → Running(owner) → Ready(value)` 或 `Running → Poisoned(error)`；失效为 `Ready → Vacant`，调用方取消只转为 `WaiterCancelled`，不能毒化 owner。循环查询转 `CycleDetected` 并 poison 当前 key；非确定性 query 不得进入可复用 cache。

owner 执行前把 key 压入 task-local active stack；请求依赖已在 stack 中时立即构造最短 cycle path，终止当前 query 并只 poison 该 key 的当前 computation epoch。Poisoned 不跨 compiler/schema/source fingerprint 永久复用；下一独立请求可在依赖变化后重试。waiter 注册采用 epoch，取消 waiter 只移除自身；最后一个 waiter 取消时 owner 是否协作取消由 query 的 `shareable` 标志决定，不能留下永不消费的无限计算。

查询算法的终止来自有限 DAG/明确 cycle detection 和每类 query 的工作量预算。动态发现依赖必须在返回前冻结并 canonical 排序；同一 key 执行期间反复加入相同依赖不增加工作量。超过节点、递归、时间或内存预算返回具体 `E-QUERY-LIMIT`，不能把部分 QueryValue 标 Ready。

缓存采用 content-addressed store：先写临时 blob、校验 hash 与 schema、fsync（Profile 要求时），再原子更新索引。依赖变化只失效受影响节点；版本/target/feature 不匹配必须 miss。循环查询返回 `E-QUERY-CYCLE`；坏 blob、校验失败、未知 schema 返回 `E-CACHE-CORRUPT` 并隔离该条目。取消、诊断阻断、内部错误均为不可提交状态。

cache key 的语义输入不含 wall time、绝对 workspace 路径、Registry `fetched_at`、LSP runtime snapshot ID 或进程随机值。Source content/snapshot fingerprint 可进入 key，但仅编辑器隔离用的 snapshot 序号不能进入可共享磁盘 cache。eviction 先标记索引不可见，等待 reader lease 归零再删除 blob；隔离坏 blob 也不能删除其他 request 正在读取的相同 content。

并发采用不可变 snapshot + per-key lock，禁止持锁调用 Backend、插件或用户代码。缓存 10 GiB、索引 1 GiB 是 `candidate_default`，遵循 [编译器 Budget 治理](./README.md#资源预算治理)；并发查询不超过 Profile 的 `max_parallelism`。磁盘满触发可观测 eviction，不删除仍被运行查询引用的 blob。

## 诊断和 ArtifactManifest

`Diagnostic` 字段：`code:String`、`severity:Severity`、`message:String`、`primary_span:Span?`、`secondary_spans:Vec<Span>`、`notes:Vec<String>`、`fixes:Vec<FixIt>`、`origin:Stage`、`retryable:bool`、`request_id:RequestId`。JSON 序列化字段只追加；路径和消息按 locale 生成，但 code/span 稳定。错误码命名空间为 `X-E-LEX-*`、`X-E-PARSE-*`、`X-E-NAME-*`、`X-E-TYPE-*`、`X-E-BORROW-*`、`X-E-MIR-*`、`X-E-BACKEND-*`、`X-E-CANCELLED`。

`ArtifactManifest` 字段：`schema_version:SemVer`、`producer_version:SemVer`、`target_fingerprint:Hash32`、`profile:ProfileId`、`entries:Vec<{kind,path,sha256,size,mode}>`、`source_fingerprint:Hash32`、`dependencies:Vec<ArtifactRef>`、`sbom:PathBuf?`、`signature:Signature?`。路径必须是输出根相对路径，重复 entry 或 hash 不匹配拒绝发布。

提交协议使用同一输出根内的 staging generation：准备所有 entry → 逐项 hash/size/mode 验证 → 写 manifest-last → 按平台原子切换 generation 指针/目录。若平台不支持目录级原子切换，则持输出锁逐项替换，并在 manifest 发布前记录 rollback journal；崩溃恢复只接受“旧完整 generation”或“新完整 generation”，不会暴露混合 manifest。签名/SBOM 失败时未签名构建产物可保留为本地非发布 artifact，但 `publishable=false`，不能进入发布通道。

## 负向验收、版本和回滚

canonical 规划测试为 `TEST-COMPILER-QUERY-001`（cycle、owner/waiter cancel、失效与预算）、`TEST-COMPILER-CONTRACT-003`（缓存损坏和原子提交）以及 `TEST-COMPILER-E2E-001`（冷编译到 manifest）。同时覆盖工作区越权、声明环境缺失、诊断超长、重复输出、磁盘满、外部进程超时和旧 lockfile；状态均为 `planned`。

回归时先用 `--no-incremental` 冷编译定位 cache/query 差异，再关闭新 query/pass gate、隔离对应 namespace、恢复上一 compiler/schema。提交阶段回滚到上一完整 generation；迁移工具必须可在旧版本上运行并输出新的 manifest，不覆盖源文件。若冷路径也不一致，则停止制品发布而不是绕过 verifier。
