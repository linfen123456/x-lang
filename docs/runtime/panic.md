---
doc_id: DOC-RUNTIME-PANIC
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-10-001, XLF-10-002, XLF-10-003, XLF-10-013, XLF-12-014]
---
# Panic、unwind 与 abort

> 状态：草案｜Owner：`role/runtime-team`

## 失败模型

`PanicPayload` 字段为 `code:u32`、`message:StrRef`、`location:Span?`、`backtrace:Backtrace?`、`cause:Handle?`；payload 必须来自预留 panic arena。`panic(policy, payload)` 只能进入当前 task/thread 的 panic 状态一次；panic 期间第二次 panic、无法分配或 hook 失败必须转入最小化 abort，不能递归 unwind。

Profile 的 `unwind` 为可恢复边界内的栈展开：按逆序运行已初始化 Drop，执行 `catch`/task join 约定；`abort` 不展开，仅执行 async-signal-safe 最小记录并终止进程；`no_std` 默认 abort。panic 不能跨未声明 FFI、线程入口或 ABI 版本边界；边界转换为 `XRT_E_PANIC` 并保证句柄状态可清理。

## Hook 与资源不变量

`PanicHook::on_panic(info:PanicInfo, sink:&PanicSink)->HookAction` 前置是 panic guard 已设置、sink 非阻塞且有预算；后置只允许写脱敏日志/trace/coredump 元数据。Hook 不能获取未知锁、分配普通堆、进行网络 I/O 或调用会 panic 的用户代码。正常返回、错误传播和 unwind 共同满足每个已初始化资源恰好 Drop 一次。

## 负向测试与回滚

测试覆盖 Drop 自身 panic、panic hook 超时、跨线程 join panic、FFI 回调 panic、信号重入、OOM 中 panic、unwind 跨 C ABI、abort 退出码和 coredump 脱敏。`TEST-RUNTIME-PANIC-001` 验证资源计数，`TEST-RUNTIME-PANIC-002` 验证 no-exceptions/no-unwind，`TEST-RUNTIME-PANIC-003` 验证二次 panic 受控 abort。切换 panic policy 需要编译 Profile 和 ABI manifest 同时变更；回归时使用上一 policy 的 runtime，不尝试在运行中改变栈模型。
