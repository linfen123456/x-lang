> 已归档：见 v2 [specs/language/05-errors-panics.md](../../../specs/language/05-errors-panics.md)

# RFC-0008：Result、panic、终止与清理

> 状态：Proposed
> 日期：2026-08-18
> 目标版本：X-Lang 1.0 候选
> 依赖：RFC-0007
> 相关缺口：`GAP-LANG-06`、`GAP-DX-04`
> 正式产物：接受后生成 `specs/language/errors-and-termination.md`。

## 1. 唯一可恢复错误模型

`Result<T, E>` 是 1.0 唯一内建可恢复错误模型。语言不提供独立的 `raises/throw/catch/try` 异常系统。

- `Ok(value)` 与 `Err(error)` 是标准库枚举构造器；
- `expr?` 只能在返回 `Result<_, E>` 的上下文传播同一 `E`；
- `Option<T>` 的 `?` 只能传播到 `Option<_>`；
- `Result` 与 `Option` 不隐式桥接，错误类型不做隐藏 `From` 转换；
- 转换使用显式 `map_error` 或构造上层错误，调用点可见。

## 2. panic 与终止

- panic 表示程序缺陷或无法继续维持不变量，不用于普通业务错误；
- Profile 固定选择 `panic=abort` 或 `panic=unwind`，同一最终 Artifact 不混用未知策略；
- unwind 只能经过标记为 unwind-safe 的 X 帧，不能跨 `extern "C"` 或未知 Foreign ABI；
- OOM 默认 abort；未来可恢复分配 API通过 `try_reserve` 等显式 `Result` 提供；
- 线程/任务失败以 Join Result 观察，未观察策略由并发 RFC 定义，不能伪装成普通返回值。

## 3. 清理矩阵

| 退出方式 | Result | 执行 X Drop | 可跨 C ABI |
|---|---|---|---|
| 正常返回 | 值 | 是 | 仅 ABI 兼容值 |
| `?` | `Err(E)` | 是 | 否，必须桥接 |
| panic=unwind | Panic Payload | 是，直到边界 | 否 |
| panic=abort | 进程终止 | 不保证 | 不适用 |
| OOM abort | 进程终止 | 不保证 | 不适用 |
| 线程失败 | Join Result | 在线程帧内按策略 | 否 |

FFI 包装函数必须在进入 Foreign ABI 前把 `Result` 映射为状态码、Tagged Result 或 Opaque Error Handle，并阻止 unwind 穿越边界。

## 4. 诊断和验收

首批符合性语料固定使用：`X-E5001` `?` 的错误类型与返回类型不一致、`X-E5002` `Result`/`Option` 传播上下文混用、`X-E5003` unwind 可能跨越 Foreign ABI。Rule ID 使用 `RULE-ERR-*`、`RULE-TERM-*`；新增诊断必须登记具体四位编号。

- compile-pass：同型 `Result/?`、显式 `map_error`、FFI 状态桥接；
- compile-fail：不同错误类型隐式传播、Result/Option 混用、Foreign ABI unwind；
- AST/HIR Snapshot：AST 将 `?` 保存为后缀节点，HIR 显式记录同型提前返回；不得生成隐藏 `From`、`throw` 或异常边；
- 诊断 Snapshot：`X-E5001/5002/5003` 固定实际错误类型、期望类型、ABI 边界和显式转换位置；
- 边界反例：OOM、panic=abort、双重 panic、线程失败和 Foreign 回调分别按清理矩阵验证，不能都建模成 `Err`；
- run-pass：正常、`Err`、unwind、abort 子进程和线程失败分类；
- Drop Trace：正常、`?` 与 unwind 必须符合 RFC-0007；
