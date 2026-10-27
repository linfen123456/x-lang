# 08 并发最小模型

> 状态：Accepted｜版本：2.1.0｜负责人：Runtime Lead｜最后更新：2026-10-22
> 类型：Spec｜唯一负责：1.0 并发能力、`Send`/`Sync`、线程、通道、锁、原子与内存模型、数据竞争定义；async 演进路径。

## 1. 结论

1. 1.0 的并发 = **OS 线程 + 作用域线程 + 通道（CSP 风格）+ 锁 + 原子**。这是原始需求中“协程 / CSP”在 1.0 的落地子集。
2. Safe 代码**不会发生数据竞争**，由 `Send`/`Sync` 在编译期保证。
3. 编译器**不会**自动插锁。缺少同步时报错，并建议使用 `Mutex` 或 `RwLock`。
4. 内存模型采用 C++20 原子模型，这也是 LLVM 实现的模型。
5. async/await 和 M:N 调度在 P5 通过 Edition 引入（§8）。

## 2. `Send` 与 `Sync` [RULE-CONC-SEND] [RULE-CONC-SYNC] [RULE-CONC-UNSAFEIMPL]

| Trait | 含义 | 自动推导 |
|---|---|---|
| `Send` | 值可以转移到另一线程 | 所有字段都是 `Send` 时自动成立 |
| `Sync` | `&T` 可以在线程间共享（即 `&T: Send`） | 所有字段都是 `Sync` 时自动成立 |

- 不满足 Send 的类型：原始指针、`Rc<T>`。不满足 Sync 的类型：原始指针、`Rc`、`Cell`、`RefCell`。
- `Arc<T>` 在 `T: Send + Sync` 时满足 Send 和 Sync。`Mutex<T>` 在 `T: Send` 时满足 Send 和 Sync。
- 手动实现必须写 `unsafe impl Send for T {}`，缺少 `unsafe` 报 `X-E6005`。
- 违反时报 `X-E7001`（值跨线程转移但不是 Send）或 `X-E7003`（跨线程共享但不是 Sync）。诊断必须指出导致失败的字段路径。

## 3. 线程 [RULE-CONC-DETACHED]

```x
use std::thread;

fn sum_parallel(data: &[u64]) -> u64 {
    let (left, right) = data.split_at(data.len() / 2);
    thread::scope(fn(s) {
        let h = s.spawn(fn() => left.iter().sum());      // 可以借用外部数据
        let r: u64 = right.iter().sum();
        h.join().unwrap_or_panic() + r
    })
}
```

| API | 规则 |
|---|---|
| `thread::scope(f)` | `scope` 返回前，等待其中所有线程结束。所以线程可以借用 `scope` 外部的数据（要求是 `Send`/`Sync`） |
| `Scope::spawn(f) -> ScopedJoinHandle<T>` | 要求 `F: FnOnce() -> T + Send`，`T: Send` |
| `thread::spawn(f) -> JoinHandle<T>` | 线程可能比调用者活得长，所以闭包和返回值**都不得是借用承载类型**，否则报 `X-E7002`，并要求 `Send` |
| `JoinHandle::join() -> Result<T, ThreadPanic>` | 1.0 只有 `panic=abort`，线程 panic 会导致整个进程 abort，`Err` 实际不会出现；保留这个类型是为了让 1.0 之后可能引入的 unwind 不破坏 API（[ADR-0008](../../docs/decisions/ADR-0008-pre-kickoff-decisions.md) K3）。`unwrap_or_panic()` 是便捷方法 |
| `thread::sleep`、`thread::current`、`available_parallelism` | 平台封装 |

## 4. 通道（CSP）

```x
use std::sync::channel;

let (tx, rx) = channel::bounded::<String>(64);   // 有界：队列满时 send 阻塞
let tx2 = tx.clone();                          // 多生产者
thread::spawn(move fn() { tx2.send(String::from("job")).unwrap_or_panic(); });
for (msg in rx) { println(&msg); }             // 所有发送端都析构后，循环结束
```

| API | 语义 |
|---|---|
| `channel::bounded::<T>(cap)` / `channel::unbounded::<T>()` | 多生产者、多消费者（MPMC），要求 `T: Send` |
| `Sender::send(v) -> Result<(), SendError<T>>` | 所有接收端都已析构时返回 `Err(v)` |
| `Receiver::recv() -> Result<T, RecvError>` | 阻塞接收；所有发送端都已析构且队列为空时返回 `Err` |
| `try_send`、`try_recv`、`recv_timeout` | 非阻塞或带超时的版本 |
| `channel::select`（P3） | 在多个接收端上等待，P3 作为库 API 提供 |

## 5. 锁与同步原语

`Mutex<T>`、`RwLock<T>`（它们的 Guard 是借用承载类型，作用域结束时自动解锁）、`Condvar`、`Once`、`OnceLock<T>`、`Barrier`、`SpinLock<T>`（`std::sync::spin`，只适合极短的临界区）。

- 锁中毒：1.0 只有 abort，所以不存在锁中毒；`lock()` 直接返回 Guard。
- **不防止死锁**。死锁是逻辑错误，不是 UB。缓解手段：P3 提供 `x vet` 的锁顺序 lint，测试中可启用锁顺序检测模式。

## 6. 原子与内存模型

- 原子类型：`AtomicBool`、`AtomicI32/I64/U32/U64/Isize/Usize`、`AtomicPtr<T>`。
- `Ordering` 取值：`Relaxed`、`Acquire`、`Release`、`AcqRel`、`SeqCst`。语义与 C++20 相同，`fence(order)` 也一样。
- **数据竞争**的定义：两个线程访问同一内存位置，至少一个是写，至少一个不是原子操作，且两者之间没有 happens-before 关系。数据竞争是 UB，但只可能出现在 unsafe 代码中。
- std 中的无锁结构必须经过模型检查（类似 loom 的穷举调度测试），并通过 TSan 压力测试（见 [testing](../../docs/testing.md) §6）。

## 7. 线程局部存储与亲和性

- 线程局部存储用 `thread_local` 函数式 API：`std::thread::LocalKey<T>`，通过 `static` 和 `const` 初始化器声明，P2 提供。
- CPU 亲和性和 NUMA 信息由 `std::os::thread`（P3）提供。

## 8. async 演进路径（P5，不属于 1.0）

| 步骤 | 内容 | 前提 |
|---|---|---|
| 1 | async RFC：`async fn`、`await`、`Future` Trait、取消语义、结构化任务作用域 | 1.0 发布，并完成借用承载 Future 的区域方案 |
| 2 | 新的 Edition 启用 `async`/`await` 关键字（1.0 中已是保留字） | RFC Accepted |
| 3 | 官方执行器：工作窃取、阻塞任务线程池；I/O 适配器分别对接 io_uring、IOCP、kqueue | 执行器可替换，替换执行器不得改变语义 |
| 4 | `Stream`、生成器 `yield` | 步骤 1 |

## 9. 规则与诊断

| Rule ID | 诊断 |
|---|---|
| RULE-CONC-SEND | X-E7001 |
| RULE-CONC-DETACHED | X-E7002 |
| RULE-CONC-SYNC | X-E7003 |
| RULE-CONC-UNSAFEIMPL | X-E6005 |
