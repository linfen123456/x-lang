---
doc_id: DOC-COMPILER-CODEGEN
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-001, XLF-01-003, XLF-01-005, XLF-02-002, XLF-02-003, XLF-02-011, XLF-11-008]
---
# TargetSpec、Backend 与制品

> 状态：草案｜Owner：`role/compiler-team`

## TargetSpec

`TargetSpec` 是编译器侧显式序列化的目标合同：`triple:String`、`arch:Arch`、`os:Os`、`env:Env`、`endianness:Endian`、`pointer_width:u8`、`data_layout:String`、`calling_conventions:Map<String,CallingConv>`、`abi_version:SemVer`、`sysroot:PathBuf`、`linker:ToolRef`、`features:BTreeSet<String>`、`capabilities:BTreeSet<Capability>`、`fingerprint:Hash32`。前置是 triple、sysroot、工具版本和 data layout 可验证；后置是 fingerprint 稳定且所有缺失能力显式记录。未知 target 返回 `X-E-TARGET-001`，不能读取宿主配置代替。PAL 不消费此私有结构，而消费 `PalTargetRequest{triple:String,arch:String,os:String,sysroot_fingerprint:Hash32}`。

Profile 的 `native` 只能在用户明确请求时探测主机；`cross`/CI 必须拒绝隐式探测。sysroot、SDK 和 linker 路径须在授权根或签名工具链中，路径逸出返回 `E-TARGET-SYSROOT`。

## Backend 接口

`OperationContext` 是 Backend 与 Linker 共用的控制结构：`cancel:CancelToken`、`deadline:Instant`、`limits:ResourceLimits`、`request_id:RequestId`、`profile:ProfileId`。两者在每个函数/对象批次、外部进程 I/O 和等待锁时检查相同 token，并统一返回 `OperationOutcome{status:Completed|Cancelled|TimedOut|ResourceExhausted|Failed,diagnostics,stats}`；取消优先于 timeout，deadline 到期返回 `X-E-CANCEL-001`，资源耗尽返回 `X-E-RESOURCE-001`。

`Backend::compile(input:VerifiedMir, target:TargetSpec, options:CodegenOptions, ctx:OperationContext)->OperationOutcome<CodegenOutput>`：前置是 MIR verifier、TargetSpec verifier、ABI capability check 均通过；后置为 `CodegenOutput{objects:Vec<ObjectArtifact>, debug:DebugArtifact?, symbols:SymbolMap, diagnostics:DiagnosticSet, stats:CodegenStats}`，每个对象有 hash、target fingerprint 和 source map。Backend 只能通过 TargetSpec 调用 assembler/linker，不能读取未声明环境变量或网络。

错误分为 `UnsupportedCapability`、`InvalidMir`、`ToolFailure{exit_code,stderr_digest}`、`ResourceExhausted`、`Cancelled`、`TimedOut`；stderr 默认脱敏并截断。外部进程使用独立句柄、`OperationContext.deadline` 和进程组，取消后先优雅终止再强杀，强杀仍要清理临时文件。

## 链接与制品

`Linker::link(objects, target, options, ctx:OperationContext)->OperationOutcome<LinkedArtifact>` 校验对象架构、ABI、符号冲突、重定位和入口；输出字段为 `path:PathBuf`、`kind:ArtifactKind`、`sha256:Hash32`、`debug_refs:Vec<PathBuf>`、`reproducibility:ReproReport`、`signature:Signature?`。写入临时目录，manifest 校验成功后原子替换；失败返回 `X-E-LINK-001`，超时返回 `X-E-LINK-002`，取消返回 `X-E-CANCEL-001`，且不暴露半成品。

Tier 1 为 Windows/Linux/macOS x86_64 与 ARM64；WASM、GPU、eBPF 作为扩展目标，必须独立 capability、conformance 和回滚。C ABI 只使用固定宽度类型、显式布局和不透明句柄，panic 不跨 FFI。

## 验收、资源与回滚

规划测试 `TEST-COMPILER-CODEGEN-001`、`TEST-COMPILER-CODEGEN-002`、`TEST-COMPILER-CODEGEN-003`、`TEST-COMPILER-CODEGEN-004` 分别覆盖 ABI/布局、汇编/链接、跨平台差分、未知 target/坏 sysroot/工具失败/磁盘满，状态均为 `planned`。默认单制品 2 GiB、Backend/Linker deadline 10 min、临时目录 4 GiB，可按 Profile 调整并写入 manifest。后端回归时切换旧 Backend gate/旧 ABI，删除未签名缓存并保留规划中的失败对象与诊断类型。
