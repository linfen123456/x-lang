---
doc_id: DOC-RUNTIME-PANIC
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-10-001, XLF-10-002, XLF-10-003, XLF-10-013, XLF-12-014]
---
# Panic、unwind 与 abort

> 状态：草案｜Owner：`role/runtime-team`

## 失败模型

`PanicPayload` 字段为 `code:u32`、`message:StrRef`、`location:Span?`、`backtrace:Backtrace?`、`cause:Handle?`；payload 必须来自预留 panic arena。`panic(policy, payload)` 只能进入当前 task/thread 的 panic 状态一次；panic 期间第二次 panic、无法分配或 hook 失败必须转入最小化 abort，不能递归 unwind。

线程/task panic 状态机为 `Idle → Panicking → RunningHook → Unwinding → Caught|ThreadExit`，abort policy 从 Panicking/RunningHook 直接进入 `Aborting`。状态只前进；二次进入 Panicking、Drop 中 panic 遇到已有 unwind、损坏 unwind metadata 或 hook 超预算都进入 Aborting。`Caught` 只允许语言/runtime 明确的 catch/task join 边界，不能让任意 C frame 捕获。

Profile 的 `unwind` 为可恢复边界内的栈展开：按逆序运行已初始化 Drop，执行 `catch`/task join 约定；`abort` 不展开，仅执行 async-signal-safe 最小记录并终止进程；`no_std` 默认 abort。panic 不能跨未声明 FFI、线程入口或 ABI 版本边界；边界转换为 `XRT_E_PANIC` 并保证句柄状态可清理。

`no_exceptions` 与 `abort` 分离：no_exceptions 禁止生成 unwind table/landing pad，可恢复失败仍通过 Result/显式控制流；abort 规定不可恢复 panic 的终止方式。组合矩阵在编译时写入 ABI/artifact manifest，runtime init 检测不匹配返回 ABI error。已经进入 unwind 的 frame 只执行 MIR/ABI 标记为已初始化的 Drop；abort 不运行全局 Drop、atexit 或普通 observer flush。

FFI adapter 在允许 unwind 的 X 侧 catch panic，先把外部可见句柄转为失败/poisoned 状态，再返回固定布局 `XrtStatus`；payload 不跨 ABI，只有稳定 code/request_id。若边界无法安全恢复则 abort。C/C++ 异常进入 X 的行为同样必须由 ABI adapter 显式定义，默认拒绝穿越。

## Hook 与资源不变量

`PanicHook::on_panic(info:PanicInfo, sink:&PanicSink)->HookAction` 前置是 panic guard 已设置、sink 非阻塞且有预算；后置只允许写脱敏日志/trace/coredump 元数据。Hook 不能获取未知锁、分配普通堆、进行网络 I/O 或调用会 panic 的用户代码。正常返回、错误传播和 unwind 共同满足每个已初始化资源恰好 Drop 一次。

PanicSink 使用预分配固定容量 ring/文件描述符，写满只增加 dropped counter。HookAction 只能是 `ContinuePolicy|AbortNow`，不能恢复执行发生 panic 的 frame。backtrace 捕获是 Profile opt-in；失败只设置 unavailable reason，不能再次 panic。hook deadline 使用 monotonic clock，超时进入最小 abort。

## 负向测试与回滚

canonical 规划测试 `TEST-RUNTIME-PANIC-001/002/003` 覆盖 Drop 自身 panic、hook 超时、跨线程 join、FFI callback、信号重入、OOM、unwind 跨 C ABI、no_exceptions/abort、退出码和 coredump 脱敏，状态均为 `planned`。每个用例记录 Drop trace、唯一终态和 ABI status，不能只看进程退出码。

切换 panic policy 需要编译 Profile、Backend lowering、runtime ABI manifest 同时变更；回归时使用上一 policy 的完整 compiler/runtime 组合，不尝试在运行中改变栈模型。若 unwind 实现回归，可回滚到 abort Profile，但这属于显式制品变体，不能用 abort 产物冒充 unwind 兼容。
