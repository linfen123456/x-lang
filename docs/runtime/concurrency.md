---
doc_id: DOC-RUNTIME-CONCURRENCY
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-009, XLF-03-003, XLF-05-001, XLF-05-002, XLF-12-006, XLF-12-017]
---
# 线程、原子、Task/Waker 与协作式取消

> 状态：草案｜Owner：`role/runtime-team`

## Thread 与原子

`ThreadConfig` 字段为 `stack_bytes:u64`、`name:String`、`priority:Priority`、`affinity:CpuSet?`、`cancel:CancelToken`；`Thread::spawn(config, entry:FnOnce()->Exit)->Result<ThreadId,ThreadError>` 前置是 stack/priority/权限通过 PAL 能力检查；后置是入口拥有自己的 join handle，失败不泄漏 quota。原子操作必须声明 `Ordering`，非原子共享只能在锁/Channel/ownership 下访问；`Send` 允许迁移，`Sync` 允许共享，不满足则编译期拒绝。

## Task、Waker、Cancel

异步运行时不是默认能力：`async-runtime` feature gate 默认关闭，必须关联 `RFC-ASYNC-001`（待决策）和语言规则 `XSP-MEM-004`。gate 未打开时，Task/await API 返回 `XRT_E_FEATURE_DISABLED`；RFC 通过后才允许把这些 API 标为 EXTENDED/已验证。

`TaskState` 状态机为 `Created → Queued → Running → {Waiting,Completed,Cancelled,Panicked}`；`Waiting → Queued` 仅由有效 Waker，终态拒绝 wake/join 以外操作。`TaskSpec` 字段为 `future:Pin<Box<dyn Future>>`、`budget:TaskBudget`、`cancel:CancelToken`、`parent:TaskId?`、`priority:Priority`。`spawn(spec)->Result<JoinHandle,TaskError>` 要求 future 满足 Send（跨线程调度时），后置是 task 可被 join/cancel 且占用 quota。`JoinHandle` 字段为 `task_id:TaskId`、`generation:u32`、`state:Atomic<JoinState>`、`result_slot:OnceCell<TaskResult>`；drop 默认 detach 并触发取消策略，显式 `join(deadline,cancel)` 等待终态并释放 quota。`Waker` 只有 `task_id:generation`，`wake()->Result<(),WakeError>` 必须幂等，过期 generation 返回 `XRT_E_STALE_HANDLE`。

取消为协作式：`CancelToken{state:Atomic<CancelState>,deadline:Instant?,reason:CancelReason,quota_lease:LeaseId?}`；任务、Timer、I/O、阻塞池必须观察它，取消 quota lease 时先标记 `CancelRequested`，阻止新资源 acquire，最后由 owner 释放 lease。返回值区分 `cancelled|deadline_exceeded|completed`。Future 被 drop 时释放注册的 waker、I/O op 和句柄；不可取消 syscall 放入隔离线程并计入泄漏预算，不能阻塞调度器线程。

调度器可 M:N、工作窃取或单线程，但必须记录 `max_workers:u32`、`max_tasks:u64`、`max_queue:u64`、`cancel_grace_ms:u64`。队列满返回 `XRT_E_TASK_LIMIT` 或施加背压；优先级不保证跨平台实时性。锁顺序必须静态文档化，禁止持锁 await；原子无锁扩展需要 ABA/回收和模型检查证据。

## 负向测试、资源 Profile 和回滚

覆盖数据竞争 litmus、错误 ordering、死锁/锁反转、waker 风暴、重复 wake、task orphan、取消竞态、join 超时、阻塞调用、队列满和线程耗尽。规划测试 `TEST-RUNTIME-CONC-001`、`TEST-RUNTIME-CONC-002`、`TEST-RUNTIME-CONC-003` 状态均为 `planned`。默认线程 1024、任务 1,000,000、单队列 100,000；Profile 可收紧。调度器回归时切换旧 scheduler 或单线程 fallback，保留规划中的 task/trace 证据类型和取消语义。
