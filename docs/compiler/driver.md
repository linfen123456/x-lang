---
doc_id: DOC-COMPILER-DRIVER
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-02-003, XLF-02-004, XLF-02-014, XLF-10-012, XLF-11-001, XLF-11-004, XLF-11-013]
---
# 编译 Driver、查询系统与制品清单

> 状态：草案｜Owner：`role/compiler-team`

## CompileRequest / CompileResult

`CompileRequest` 字段：`schema_version:SemVer`、`workspace_root:PathBuf`、`inputs:Vec<PathBuf>`、`target:TargetSpecId`、`profile:ProfileId`、`edition:Edition`、`features:BTreeSet<String>`、`emit:BTreeSet<EmitKind>`、`limits:ResourceProfile`、`cancel:CancelToken`、`previous:SnapshotId?`、`environment:DeclaredInputs`。前置是路径、target、profile、edition 和 feature 已解析，工作区锁已取得；后置是成功返回完整 manifest，失败只返回诊断。环境只接受 `DeclaredInputs`，不得隐式读取秘密、时间或网络。

`CompileResult` 字段：`status:CompileStatus`、`diagnostics:DiagnosticSet`、`artifacts:Vec<ArtifactRef>`、`manifest:ArtifactManifest?`、`stats:CompileStats`、`cache:CacheStats`、`request_id:RequestId`。成功状态不能带阻断错误；取消/资源超限明确区分，均不提交最终产物。

## QueryEngine 与增量缓存

`QueryKey` 为 `QueryKind + canonical_inputs + compiler_version + edition + target_fingerprint + profile + feature_fingerprint + declared_env_hash + schema_version + pass_version + pipeline_fingerprint`；`QueryValue` 含 `value:ArtifactId`、`dependencies:Vec<QueryKey>`、`fingerprint:Hash32`、`diagnostics`、`cost`、`determinism:Determinism`。查询状态机为 `Vacant → Running(owner) → Ready(value)` 或 `Running → Poisoned(error)`；失效为 `Ready → Vacant`，调用方取消只转为 `WaiterCancelled`，不能毒化 owner。循环查询转 `CycleDetected` 并 poison 当前 key；非确定性 query 不得进入可复用 cache。

缓存采用 content-addressed store：先写临时 blob、校验 hash 与 schema、fsync（Profile 要求时），再原子更新索引。依赖变化只失效受影响节点；版本/target/feature 不匹配必须 miss。循环查询返回 `E-QUERY-CYCLE`；坏 blob、校验失败、未知 schema 返回 `E-CACHE-CORRUPT` 并隔离该条目。取消、诊断阻断、内部错误均为不可提交状态。

并发采用不可变 snapshot + per-key lock，禁止持锁调用 Backend、插件或用户代码。默认缓存 10 GiB、索引 1 GiB、并发查询不超过 Profile 的 `max_parallelism`；磁盘满触发可观测 eviction，不删除仍被运行查询引用的 blob。

## 诊断和 ArtifactManifest

`Diagnostic` 字段：`code:String`、`severity:Severity`、`message:String`、`primary_span:Span?`、`secondary_spans:Vec<Span>`、`notes:Vec<String>`、`fixes:Vec<FixIt>`、`origin:Stage`、`retryable:bool`、`request_id:RequestId`。JSON 序列化字段只追加；路径和消息按 locale 生成，但 code/span 稳定。错误码命名空间为 `X-E-LEX-*`、`X-E-PARSE-*`、`X-E-NAME-*`、`X-E-TYPE-*`、`X-E-BORROW-*`、`X-E-MIR-*`、`X-E-BACKEND-*`、`X-E-CANCELLED`。

`ArtifactManifest` 字段：`schema_version:SemVer`、`producer_version:SemVer`、`target_fingerprint:Hash32`、`profile:ProfileId`、`entries:Vec<{kind,path,sha256,size,mode}>`、`source_fingerprint:Hash32`、`dependencies:Vec<ArtifactRef>`、`sbom:PathBuf?`、`signature:Signature?`。路径必须是输出根相对路径，重复 entry 或 hash 不匹配拒绝发布。

## 负向验收、版本和回滚

覆盖工作区越权、声明环境缺失、并发取消竞态、查询循环、缓存污染/截断、诊断超长、重复输出、磁盘满、外部进程超时和旧 lockfile。回归时使用 `--no-incremental` 冷编译作为基线；如语义差异，关闭新 query/pass gate、删除对应 namespace、恢复上一 compiler/schema 版本。迁移工具必须可在旧版本上运行并输出新的 manifest，不覆盖源文件。
