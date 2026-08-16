---
doc_id: DOC-COMPILER-CODEGEN
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-01-001, XLF-01-003, XLF-01-005, XLF-02-002, XLF-02-003, XLF-02-011, XLF-11-008]
---
# TargetSpec、Backend 与制品

> 状态：草案｜Owner：`role/compiler-team`

## TargetSpec

`TargetSpec` 是编译器侧显式序列化的目标合同：`triple:String`、`arch:Arch`、`os:Os`、`env:Env`、`endianness:Endian`、`pointer_width:u8`、`data_layout:String`、`calling_conventions:Map<String,CallingConv>`、`abi_version:SemVer`、`sysroot:PathBuf`、`linker:ToolRef`、`features:BTreeSet<String>`、`capabilities:BTreeSet<Capability>`、`fingerprint:Hash32`。前置是 triple、sysroot、工具版本和 data layout 可验证；后置是 fingerprint 稳定且所有缺失能力显式记录。未知 target 返回 `X-E-TARGET-001`，不能读取宿主配置代替。PAL 不消费此私有结构，而消费 `PalTargetRequest{triple:String,arch:String,os:String,sysroot_fingerprint:Hash32}`。

Profile 的 `native` 只能在用户明确请求时探测主机；`cross`/CI 必须拒绝隐式探测。sysroot、SDK 和 linker 路径须在授权根或签名工具链中，路径逸出返回 `E-TARGET-SYSROOT`。

TargetSpec 验证按 `parse → canonicalize → toolchain identity → data-layout cross-check → capability closure → fingerprint` 执行。`data_layout`、pointer width、endianness、object format 和 LLVM target machine 必须互相一致；任一冲突都在创建 LLVM context 前失败。fingerprint 只含目标语义和签名工具链身份，不含 host 路径、探测时间或 runtime capability snapshot。

## Backend 接口

`OperationContext` 是 Backend 与 Linker 共用的控制结构：`cancel:CancelToken`、`deadline:Instant`、`limits:ResourceLimits`、`request_id:RequestId`、`profile:ProfileId`。两者在每个函数/对象批次、外部进程 I/O 和等待锁时检查相同 token，并统一返回 `OperationOutcome{status:Completed|Cancelled|TimedOut|ResourceExhausted|Failed,diagnostics,stats}`；取消优先于 timeout，deadline 到期返回 `X-E-CANCEL-001`，资源耗尽返回 `X-E-RESOURCE-001`。

`Backend::compile(input:VerifiedMir, target:TargetSpec, options:CodegenOptions, ctx:OperationContext)->OperationOutcome<CodegenOutput>`：前置是 MIR verifier、TargetSpec verifier、ABI capability check 均通过；后置为 `CodegenOutput{objects:Vec<ObjectArtifact>, debug:DebugArtifact?, symbols:SymbolMap, diagnostics:DiagnosticSet, stats:CodegenStats}`，每个对象有 hash、target fingerprint 和 source map。Backend 只能通过 TargetSpec 调用 assembler/linker，不能读取未声明环境变量或网络。

错误分为 `UnsupportedCapability`、`InvalidMir`、`ToolFailure{exit_code,stderr_digest}`、`ResourceExhausted`、`Cancelled`、`TimedOut`；stderr 默认脱敏并截断。外部进程使用独立句柄、`OperationContext.deadline` 和进程组，取消后先优雅终止再强杀，强杀仍要清理临时文件。

## Lowering、布局与 LLVM 验证

Backend 逐函数处理，但模块提交是事务性的：

1. 从 `VerifiedMir` 和 TargetSpec 计算类型布局；递归类型通过指针打断，否则返回 `X-E-LAYOUT-CYCLE`。布局缓存键包含 TypeId、repr、target data layout 和 ABI version。
2. 先声明全部符号和函数签名，再生成 body，避免生成顺序改变可见结果。
3. 将 MIR block 映射为 LLVM basic block；每个 MIR terminator 恰好生成一个终止指令，cleanup/unwind 仅在 Profile 允许时生成。
4. 对算术、cast、load/store、atomic、volatile 和调用逐项检查 target capability；不能用 LLVM 的宽松类型转换掩盖 MIR 类型错误。
5. 每个函数生成后运行 LLVM function verifier，模块结束运行 module verifier；任一失败丢弃整个临时 module。
6. 优化由已登记 pipeline 执行，完成后再次运行 module verifier，再写临时 object。

布局结果至少包含 `size,align,field_offsets,abi_class,padding,niche?`。只有 `repr(C)`/`repr(transparent)` 和正式 ABI 规则形成外部承诺；默认 X 布局可随非稳定版本变化，但同一 compiler/target/profile 必须确定。零大小类型、DST、enum niche 和向量类型未冻结前必须 feature gate，不能由 LLVM 自动布局反向定义语言语义。

## ABI 与调用约定

调用 lowering 先把语言签名转为 `AbiSignature{params,return,calling_conv,unwind,variadic}`，再按目标 ABI 分类为 direct、indirect/sret、extend、split 或 ignore。调用方和被调用方使用同一分类器 fingerprint；不匹配阻断链接。C ABI 只允许 FFI 规范批准的固定布局类型、指针和 opaque handle；slice/string 以显式 ptr+len 传递，所有权与释放函数写入接口文档。

panic policy 是 ABI 输入：`unwind` 生成目标支持的 personality/landing pad，`abort/no_exceptions` 不得残留 unwind edge。任何不允许 unwind 的外部边界必须生成 catch-to-status 或 abort adapter，不能直接穿越。stdcall/vectorcall 等非默认 calling convention 必须由 TargetSpec 显式列出并经过 ABI golden test。

## 链接与制品

`Linker::link(objects, target, options, ctx:OperationContext)->OperationOutcome<LinkedArtifact>` 校验对象架构、ABI、符号冲突、重定位和入口；输出字段为 `path:PathBuf`、`kind:ArtifactKind`、`sha256:Hash32`、`debug_refs:Vec<PathBuf>`、`reproducibility:ReproReport`、`signature:Signature?`。写入临时目录，manifest 校验成功后原子替换；失败返回 `X-E-LINK-001`，超时返回 `X-E-LINK-002`，取消返回 `X-E-CANCEL-001`，且不暴露半成品。

链接前建立 `LinkPlan`：canonical 排序 objects/libraries，解析唯一 entry，验证 object format/arch/target/ABI fingerprint，拒绝重复强符号和未声明动态库搜索路径。响应文件只写参数数组的工具链规定编码，不能通过 shell 拼接。链接后重新读取制品 header，核对架构、入口、动态依赖 allowlist、调试引用和 build-id；成功后才生成 manifest 并原子发布。链接器退出 0 但产物缺失或 header 不符仍是失败。

确定性构建固定对象/section/symbol 输入顺序、archive member 顺序、随机 seed、路径映射和时间戳策略。签名通常会改变最终 bytes，应分别记录 unsigned content digest 与 signed artifact digest；签名步骤不进入编译语义缓存。

Windows/Linux/macOS x86_64 与 ARM64 是目标 Tier 1 范围，不表示当前已经支持；只有[平台后端规范](../runtime/platform-backends.md)的晋级证据齐全后才能发布为 Tier 1。WASM、GPU、eBPF 作为扩展目标，必须独立 capability、conformance 和回滚。C ABI 只使用固定宽度类型、显式布局和不透明句柄，panic 不跨 FFI。

## 验收、资源与回滚

canonical 规划测试为 task-dag 登记的 `TEST-COMPILER-CODEGEN-001`、`TEST-COMPILER-LINK-001`、`TEST-COMPILER-E2E-001`，分别覆盖布局/ABI/LLVM verifier、对象/链接/产物回读，以及目标平台 Hello World 闭环；Target/PAL 负向由 `TEST-RUNTIME-PAL-001/002` 覆盖。状态均为 `planned`。测试必须包含未知 target、坏 sysroot、工具退出 0 但无产物、重复符号、磁盘满、取消、unwind ABI 和两次构建 hash 差分。单制品 2 GiB、Backend/Linker deadline 10 min、临时目录 4 GiB 是 `candidate_default`，遵循 [编译器 Budget 治理](./README.md#资源预算治理)，由 Profile 提供并写入 manifest。

回滚顺序为：禁用单个优化 pipeline → 使用 O0 VerifiedMir 冷路径 → 切换上一 Backend/ABI adapter → 暂停问题目标的 Tier 发布。回滚只删除当前 request 的未发布临时文件和坏 cache namespace，不删除已发布制品或用户输出；无法验证的旧 cache 必须 miss。
