---
doc_id: DOC-RUNTIME-IO
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: EXTENDED
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-05-008, XLF-05-009, XLF-05-010, XLF-12-006, XLF-12-007]
---
# Reactor/Proactor 异步 I/O

> 状态：草案｜Owner：`role/runtime-team`

## 统一契约

公开 `IoState` 是用户可观察状态：`Created → Submitted → {Ready,Cancelled,TimedOut,Failed}`。资源关闭另用 `ResourceState: Open → Closing → Closed`，不得把 `Closing/Closed` 当作第二组 I/O 完成终态。一次操作只发布一个用户终态；重复 complete/cancel/close 返回幂等观察结果。若 Cancelled/TimedOut 后内核仍持有请求，内部回收态为 `OrphanedKernelOp → Reaped`：后到 completion 只释放 buffer/quota 并记录 OS 摘要，不得改写公开终态或二次发布。

`IoOp` 字段为 `op_id:u64`、`resource:Handle`、`kind:Read|Write|Accept|Connect|Poll`、`buffer:BorrowedSlice|OwnedBuffer`、`offset:u64?`、`deadline:Instant?`、`cancel:CancelToken`。`Io::submit(op)->Result<OpId,IoError>` 前置是 handle capability、buffer 生命周期、长度和对齐（Direct I/O）合法；后置只表示已入队，不表示完成。`Io::complete(op_id)->Result<IoResult,IoError>` 返回 bytes/status/OS code，完成、取消和关闭只能发布一次。

Reactor（epoll/kqueue）只报告 readiness，调用方负责 read/write；Proactor（IOCP/io_uring）报告 operation completion，runtime 负责 buffer ownership。PAL 报告 backend/能力后，统一层选择 backend；不支持的 cancel/zerocopy 必须返回 capability 或显式 fallback，不得伪造成功。

## 取消、关闭和背压

提交时登记 `op_id -> cancel/handle/generation`；取消是幂等的，若 OS 不可取消则标记 `cancel_pending`，由隔离线程完成并在 quota 中保留 buffer。关闭 handle 先停止新提交，再取消/排空已提交 op，最后释放句柄。队列达到 `max_inflight:u32` 或 buffer 达到 `max_io_bytes:u64` 返回 `XRT_E_IO_LIMIT`，调用方必须 await 背压信号。

零拷贝 `sendfile/splice` 只在 source/destination capability 和对齐满足时启用；mmap 预取是可选 hint，不能改变文件语义，page fault/不可用时回退普通 read。定时器 `Timer::sleep(deadline, cancel)->Result<(),TimerError>` 使用单调时钟；墙钟跳变只用于 wall-clock API。

## 负向测试、Profile、版本与回滚

覆盖短读/短写、EINTR、断网、队列满、超时、重复完成、关闭竞态、错误 buffer、错对齐、句柄耗尽、时钟回拨、mmap 截断和 io_uring/IOCP 不可用。规划测试 `TEST-RUNTIME-IO-001`、`TEST-RUNTIME-IO-002`、`TEST-RUNTIME-IO-003` 状态均为 `planned`。单 I/O 64 MiB、并发 100k、提交超时 30 s 是 Profile 的 `candidate_default`，遵循 [运行时 Budget 治理](./README.md#资源预算治理)，不是吞吐或延迟承诺；backend 由能力矩阵版本化，回归时切换稳定 fallback 并保留旧 op schema。
