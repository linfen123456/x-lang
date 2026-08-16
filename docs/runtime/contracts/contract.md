---
doc_id: DOC-RUNTIME-CONTRACTS-CONTRACT
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-02-009, XLF-02-011, XLF-05-001, XLF-05-005, XLF-05-008, XLF-10-003, XLF-12-014]
---
# XRT 全量接口契约

> 状态：草案｜Owner：`role/runtime-team`

表中的固定资源数字均为 Profile 的 `candidate_default`，遵循 [运行时 Budget 治理](../README.md#资源预算治理)。它们用于限制失控输入，不是并发、吞吐或稳定 ABI 承诺；P4 前须由 Budget ADR 决定发布值。

| 接口 | 输入字段类型 | 前置/后置 | 错误 | 取消 | 并发/资源上限 |
|---|---|---|---|---|---|
| `xrt_init` | `req:*const XrtInit,out:*mut XrtHandle` | 非空且匹配 ABI/target；out 成功写入 | `XRT_E_ABI_MISMATCH`, `XRT_E_CAPABILITY` | 初始化可取消 | 1 次进程；heap profile |
| `xrt_shutdown` | `ctx:XrtHandle,policy:XrtShutdownPolicy,deadline:XrtInstant` | ctx 为 Running/ShutdownRequested；最终 Closed 或返回剩余资源摘要 | `XRT_E_STALE_HANDLE`, `XRT_E_DEADLINE`, `XRT_E_ACTIVE_LEASE` | 重复调用观察同一关闭状态 | deadline 内 drain；禁止接受新 Task/I/O/Lease |
| `Allocator.alloc` | `Layout{size:usize,align:usize}` | 合法 layout + quota；返回 owned ptr | `OOM`, `QUOTA`, `INVALID_LAYOUT` | 不在分配中途取消 | 单次 64 MiB、heap 512 MiB |
| `Task.spawn` | `Future,TaskBudget,CancelToken` | Send/预算合法；返回 TaskId | `TASK_LIMIT`, `SHUTDOWN` | token 传播至 future | 任务 1M、线程 1024 |
| `Waker.wake` | `TaskId{raw,generation}` | generation 有效；入 ready 队列 | `STALE_HANDLE`, `QUEUE_FULL` | 不取消 wake | 幂等；队列 100k |
| `Timer.sleep` | `deadline:Instant,cancel:CancelToken` | 单调 deadline；完成或取消 | `TIMER_LIMIT`, `CLOCK` | 协作式 | timer 1M |
| `Io.submit` | `IoOp{resource,buffer,kind,deadline,cancel}` | capability/长度/对齐合法 | `IO_LIMIT`, `UNSUPPORTED` | OS cancel 或隔离线程 | 100k op、64 MiB/op |
| `ResourceQuota.reserve` | `kind,amount:u64` | 原子 quota 检查；返回 Lease | `QUOTA` | 取消释放 lease | 句柄 100k |
| `Observer.emit` | `LogEvent|Metric|Span` | 脱敏/大小通过 | `SINK`, `DROPPED` | 可丢弃 | event 64 KiB、队列 64 MiB |

所有 handle close/drop 必须幂等；panic/unwind/FFI 不能跨未声明边界；回调时不得持有 runtime 锁。错误结构统一为 `XrtStatus{code:u32,detail:u32,retryable:u8,reserved:u8,request_id:XrtRequestId{hi:u64,lo:u64}}`，未知 code 按 fatal 处理。C ABI 不暴露 `Result`；`cancelled`、`deadline_exceeded`、`quota_exhausted` 和 `completed` 不得混淆。

`xrt_shutdown` 的统一后置条件是：状态单向经过 `Running → ShutdownRequested → Draining → Closed`；进入 ShutdownRequested 后新 Task、I/O 和 Lease 返回 SHUTDOWN；Drain 策略等待已提交操作并拒绝新操作，Cancel 策略请求取消后等待安全边界，Immediate 仅用于进程终止且不承诺全局 Drop。deadline 到期时返回活跃 Task/I/O/Lease 的计数摘要，context 保持 Draining，可由同一调用者继续等待或升级策略；任何路径都不得重复完成 I/O 或复用已关闭 handle generation。

## 负向测试、版本和回滚

接口套件规划为 `TEST-RUNTIME-CONTRACT-001`、`TEST-RUNTIME-CONTRACT-002`、`TEST-RUNTIME-CONTRACT-003`，状态均为 `planned`，覆盖错 ABI/布局、取消竞态、I/O 队列满、关闭中的完成和观测脱敏。ABI/资源/观测 schema 的主版本变化须有 adapter、迁移说明和旧制品；失败时停用新 backend/allocator/scheduler、切换 PAL fallback 或旧 runtime，保留规划中的诊断和 quota 账本类型。
