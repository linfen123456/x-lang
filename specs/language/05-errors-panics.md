# 05 错误模型：Result、panic、终止与清理

> 状态：Accepted｜版本：2.1.0｜负责人：Language Lead｜最后更新：2026-10-22
> 类型：Spec｜唯一负责：可恢复错误、`?`、panic、终止、`main` 返回约定、退出码、清理矩阵。

## 1. 结论

1. `Result<T, E>` 是**唯一**的可恢复错误模型。语言没有异常，也没有 `throw/try/catch`。
2. `?` 只传播**相同的** `E`，不做隐藏转换。需要转换时显式调用 `map_error`。
3. 1.0 的 panic 策略**只有** `abort`（[ADR-0008](../../docs/decisions/ADR-0008-pre-kickoff-decisions.md) K3）。`unwind` 不属于 1.0，1.0 之后可以经 RFC 评估。
4. `main` 可以返回 `()` 或 `Result<(), E>`（要求 `E: Display`）。

## 2. `Result` 与 `?` [RULE-ERR-SAMEE] [RULE-ERR-MIX] [RULE-ERR-QTYPE]

```x
use std::fs;
use std::io::IoError;

enum AppError { Io(IoError), BadLine(usize) }

fn count_lines(path: &str) -> Result<usize, AppError> {
    let text = fs::read_to_string(path).map_error(fn(e) => AppError::Io(e))?;
    Ok(text.lines().count())
}
```

规则：
- `e?` 中，若 `e: Result<T, E>`，所在函数必须返回 `Result<_, E>`，且两个 `E` 是同一类型；否则报 `X-E5001`。
- `Option<T>` 的 `?` 只能用在返回 `Option<_>` 的函数中。`Result` 与 `Option` 混用报 `X-E5002`；转换用 `ok_or(err)` 或 `ok()`。
- `?` 用于非 `Result`/`Option` 的值报 `X-E5005`。
- `Result` 带 `@must_use`，忽略它会产生 `X-W0006`。需要显式丢弃时写 `let _ = f();`。
- 1.0 没有 `From` 自动转换，也没有异常规格。错误链（来源、回溯上下文）由生态库提供（XLF-10-001）。

## 3. panic [RULE-TERM-MAIN]

- panic 表示**程序缺陷**：违反不变量、越界、溢出、`unwrap` 遇到 `None`/`Err`、显式 `panic(msg)`。它不用于业务错误。
- panic 时输出到 stderr，格式为：

  ```text
  panic at src/main.x:12:5: index out of bounds: len 3, index 7
  ```

  P2 起，设置环境变量 `X_BACKTRACE=1` 时会追加回溯。
- `panic=abort`（P0 起默认）：输出信息后调用平台 abort。Unix 上进程被 `SIGABRT` 终止（shell 中的退出状态通常是 134），Windows 上退出码为 3。**不保证**执行 Drop。
- `panic=unwind`：1.0 中不提供。`X-E5003` 预留给 1.0 之后可能引入的 unwind（P5，需 RFC）；任何 RFC 都必须保证 unwind 不穿越 `extern "C"`。
- 测试：在 abort 模型下，`x test` 把每个测试放在独立子进程中运行，因此单个测试 panic 不会中断整个测试集（与 Rust 在 `panic=abort` 下的测试模式一致）。
- panic 期间再次 panic：直接 abort。
- 内存不足（OOM）：默认 abort。需要可恢复处理时使用 `try_reserve` 等返回 `Result` 的 API。

## 4. `main` 与退出码

| `main` 签名 | 行为 | 退出码 |
|---|---|---|
| `fn main() -> ()` | 正常返回 | 0 |
| `fn main() -> Result<(), E>`，其中 `E: Display` | 返回 `Err(e)` 时向 stderr 输出 `error: {e}` | 1 |
| 任意签名下调用 `std::process::exit(n)` | 立即退出，不执行 Drop | `n` |
| panic | 见 §3 | 平台 abort |

其他签名报 `X-E5004`。

## 5. 清理矩阵

| 退出方式 | 执行 X 的 Drop | 能否跨 C ABI |
|---|---|---|
| 正常返回 / `?` / `break` / `return` | 是 | 只能传递 FFI 安全值 |
| panic=abort / OOM / `process::exit` | 否 | 不适用 |

## 6. 规则与诊断

| Rule ID | 诊断 |
|---|---|
| RULE-ERR-SAMEE | X-E5001 |
| RULE-ERR-MIX | X-E5002 |
| RULE-TERM-FFIUNWIND | X-E5003 |
| RULE-TERM-MAIN | X-E5004 |
| RULE-ERR-QTYPE | X-E5005 |
| LINT-MUST-USE | X-W0006 |
