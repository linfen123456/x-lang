---
doc_id: DOC-RUNTIME-SCHEDULER-IO-STATE-MACHINES
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.0"
maturity: EXTENDED
status: 待决策
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-009, XLF-02-009, XLF-04-007, XLF-05-001, XLF-05-002, XLF-05-008, XLF-05-009, XLF-10-009, XLF-12-013, XLF-12-015, XLF-12-016]
---
# 调度器、取消与异步 I/O 状态机实施规范

> 本文展开[并发契约](./concurrency.md)、[I/O 契约](./io.md)和[XRT 公共接口](./contracts/contract.md)。`async-runtime` 默认关闭，只有 `RFC-ASYNC-001` 转为已决策后才实施 Task/Future/Waker 子范围；此前 P2 可实现同步 I/O、资源配额和 shutdown，不得把本文状态机视为稳定语言承诺。所有证据均为 `planned`。

## 1. 目标与非目标

目标是把 M:N 调度、结构化取消、Timer、Reactor/Proactor I/O 和 shutdown 组合成无重复完成、无句柄复用、资源有界的状态机，并给出可拆实现任务。

非目标：

- 不承诺纳秒级切换、百万级定时器或通用硬实时；数字必须经指定环境基准验证。
- 不在 Borrow Checker 中自动插锁，也不从语言层隐藏阻塞系统调用。
- 不实现用户态 TCP/QUIC 协议栈；本阶段只提供 I/O substrate。
- 不保证 OS 已受理的所有操作都能立即取消；不可取消路径必须显式保留 buffer/quota。
- 不让优先级跨平台等价；PAL 能力不足时返回 Unsupported/Denied 或使用公开 fallback。

## 2. 统一身份、代次与一次完成

运行时内部对象使用 `SlotHandle{slot:u32,generation:u32,kind:u16,flags:u16}`。slot 释放时 generation 单调增加；所有队列项、Waker、I/O completion 和 Timer entry 都携带 generation。C ABI 的 `XrtHandle` 是独立的不透明 owner token，只能经 ABI handle table 的 `decode_and_validate(XrtHandle) → SlotHandle` 和 `export(SlotHandle) → XrtHandle` 转换；不得 bitcast、复用 raw 字段或向外暴露 slot。旧 generation 只能得到 `XRT_E_STALE_HANDLE`，不能作用于新对象。

一次完成槽：

```text
CompletionCell<T> {
  state: Atomic<Empty|Writing|Ready|Taken>,
  value: MaybeUninit<T>,
  waiters: WaitList
}
```

`CompletionCell<T>` 是**单消费者结果槽**：只有唯一 `JoinHandle`/`IoOpHandle` 能 CAS `Ready→Taken` 并移动出 `T`；其他 waiters 只接收“已就绪”广播，随后从共享的只读终态摘要观察状态，不能复制或再次取得 `T`。需要多消费者的 API 必须在 `T` 外显式使用 `Arc`/cloneable result，不能改变该槽语义。只有 CAS `Empty→Writing` 的执行者可写 value，release store 到 Ready 后广播 waiters。取消、超时、OS completion、panic 竞争同一个槽；失败方只观察赢家结果并清理自身注册，不重复释放资源。

## 3. Runtime 与 shutdown 状态机

```text
Uninitialized → Starting → Running
Running → ShutdownRequested → Draining → Closed
Starting → Failed
Draining --deadline--> Draining (返回活跃摘要，可继续或升级策略)
```

进入 `ShutdownRequested` 后：

1. 原子关闭 admission gate；新 Task、I/O、Timer 和 Lease 返回 `XRT_E_SHUTDOWN`。
2. `Drain` 等待现有工作；`Cancel` 向 root scope 广播取消；`Immediate` 仅用于进程终止且不承诺全局 Drop。
3. 关闭外部 listeners，再排空 worker/local/global queue、I/O backend 和 blocking pool。
4. active task/io/timer/lease 全为零后关闭 observer，释放 PAL/context，转 Closed。
5. deadline 到期返回计数与最老资源摘要，context 保持 Draining，不能伪报 Closed。

shutdown 可重复调用；同一 context 的调用观察同一状态。不得持 scheduler 锁调用用户 Drop、observer sink 或 PAL callback。

## 4. Task 生命周期

### 4.1 状态

```text
Created → Queued → Running → Waiting → Queued
Running → Completed | Panicked | Cancelled
Queued  → Cancelled
Waiting → Cancelled
terminal → Joined | DetachedCleanup
```

`TaskControl` 至少包含 `id,generation,state,future,result,parent_scope,cancel,budget,home_worker,wake_epoch,queued_epoch`。`wake_epoch` 防止 wake 丢失，`queued_epoch` 防止同一 Task 多次并发入队。

### 4.2 poll 协议

1. worker CAS `Queued→Running`；失败说明 stale queue entry，直接丢弃。
2. 构造只含 `task_id:generation` 的 Waker，不暴露 task 指针。
3. 在用户 poll 前检查 cancel/deadline/budget；取消时 drop Future，走一次完成槽。
4. `Poll::Ready(v)` 发布 Completed；panic 按 Profile 捕获为 Panicked 或触发 abort。
5. `Poll::Pending` 先读取 wake epoch，再 CAS `Running→Waiting`；若 poll 期间 epoch 已变化，立即转 Queued，避免 lost wakeup。
6. 每次 poll 记账 CPU 时间/次数；超预算触发 cooperative yield 或 ResourceExhausted，策略必须配置。

Future 的 Drop 必须撤销其 Timer/I/O 注册；若 OS 操作不可取消，I/O owner 持有独立 buffer lease，不能依赖 Future 内存继续存在。

### 4.3 Waker

`wake()` 原子增加 wake epoch；若状态为 Waiting，赢家 CAS 到 Queued 并入队；Running 状态只留下 epoch；Queued 状态无需重复入队；终态返回幂等结果。wake 不得阻塞、分配无限内存或执行用户代码。queue 满时使用每任务内置 wake slot 或受控 overflow queue，不能丢失唤醒。

## 5. Scope、Join 与取消树

每个 Task 属于 `TaskScope{parent,children,state,cancel,deadline}`。scope 状态为 `Open→Closing→Closed`；Closing 后禁止 spawn。结构化 scope 返回前必须 join/cancel 所有非 detached child。detached 是显式能力并转移到 runtime root scope，不能借用父栈数据。

取消 token 状态：

```text
Active → CancelRequested(reason,epoch) → Observed → Completed
Active --deadline--> CancelRequested(Deadline)
```

取消传播按父到子 snapshot 执行，不持父锁调用子 callback。注册与取消竞态通过 epoch 解决：callback 注册后再次读取 epoch；若已变化则自行执行一次。取消 callback 必须短小、不可 panic，复杂清理只入控制队列。

结果优先级只解决同一原子瞬间的竞态：已成功发布 Completed 则返回结果；否则 cancel 优先于 timeout，timeout 优先于资源耗尽。真实先发生的 OS completion 不得被事后取消改写。

## 6. M:N 工作窃取调度

### 6.1 队列结构

- worker local deque：owner push/pop bottom，stealer 从 top steal；适合 cache locality。
- global injection queue：外部线程、Timer 和 I/O completion 入队。
- blocking pool：只执行标记 blocking 的函数，不得占用 async worker。
- per-priority queues：优先级只作提示，必须通过 aging 防止低优先级饿死。

### 6.2 worker 循环

```text
while runtime not Closed:
  drain bounded local completions
  task = pop_local() ?? pop_global() ?? steal_bounded()
  if task: poll_with_budget(task); continue
  publish_idle()
  park_until(notification or next_timer_deadline)
```

每轮 completion、local task 和 steal 都有批量上限，避免 I/O 风暴饿死 Timer 或普通 Task。随机 steal seed 在确定性测试 Profile 固定。worker park 前使用 epoch handshake，避免在通知到达后睡眠。

### 6.3 阻塞隔离

公开 API 要么明确 async/nonblocking，要么通过 `spawn_blocking`。blocking pool 有独立 max threads、queue 和 deadline；队列满返回背压，不无限扩线程。不可取消系统调用完成前保持 lease；shutdown 报告 orphaned blocking op，不能宣称已清理。

## 7. Timer Wheel/Heap

Timer 以单调时钟 deadline 排序。P2 基线可用分片最小堆；大量 timer 是否切换分层 timing wheel 由基准决定，不先行复杂化。

Timer 状态：`Created→Registered→Fired|CancelRequested→Cancelled`。backend 线程取得到期 entry 后仍需 CAS 一次完成；取消与 fired 竞争时只有赢家发布。墙钟 Timer 必须在 API 层转换并声明对 clock adjustment 的行为；调度核心不使用 wall clock。

最小堆实现任务：分片锁、generation、lazy tombstone、定期 compaction、最近 deadline 通知。compaction 受预算和取消控制。测试使用虚拟单调时钟，禁止依赖真实 sleep。

## 8. I/O Operation 状态机

统一内部状态比现有摘要更精确。公共 `IoState` 仍保持[现有 I/O 契约](./io.md)中的 `Created → Submitted → Ready|Cancelled|TimedOut|Failed`；资源关闭由独立 `ResourceState` 表达。下列 `Validated/Completing/CancelRequested/Cancelling/OrphanedKernelOp/Reaped` 只属于 XRT 内部实现，不得通过稳定 ABI 暴露。映射规则是：`Created/Validated` 对外为 Created；尚未发布用户终态的 `Submitted/Completing/Cancelling` 对外为 Submitted；进入 OrphanedKernelOp 前用户终态已经固定为 Cancelled 或 TimedOut，Orphaned/Reaped 不能改变它；Reaped 后操作句柄失效。

内部状态机：

```text
用户完成轨：Created → Validated → Submitted
                         ├→ Completing → Ready|Failed
                         ├→ CancelRequested → Cancelling → Cancelled
                         └→ TimeoutRequested → Cancelling → TimedOut

内核回收轨：NotSubmitted → InFlight → KernelCompleted → Reaped
                                  └→ OrphanedKernelOp → Reaped
```

两条轨由同一 op 关联但不是同一个 enum：用户轨终态不可逆；内核轨只回答“kernel 是否还可能访问资源”。正常完成时先取得用户完成槽再 Reaped；取消/超时先发布用户终态而 kernel 未确认时，内核轨才进入 OrphanedKernelOp。

`IoControl` 包含 `op_id,generation,resource,kind,buffer_lease,quota_lease,deadline,cancel,backend_cookie,completion`。用户终态与内核回收态严格分离：一旦用户侧已发布 Cancelled/TimedOut，若 kernel 仍可能访问 buffer，内部回收记录进入 OrphanedKernelOp；后到的 kernel completion 只记录 OS 摘要并释放 buffer/quota，然后单向进入 Reaped，**不得再次写 CompletionCell、不得改写用户终态、不得产生第二次完成事件**。若用户侧先收到真实完成，则直接发布 Ready/Failed 并回收，不经过 orphan。

### 8.1 提交流程

1. 验证 handle kind/capability/generation，buffer 生命周期、长度、权限和 Direct I/O 对齐。
2. 预留 inflight、bytes、handle quota；失败不创建 op。
3. 创建 completion 与 cancel/timer registration。
4. 调用 backend submit；只有确认 OS 接受后转 Submitted。
5. submit 同步失败时注销全部 registration 并归还 lease。
6. 返回 OpHandle 仅表示已提交，不表示完成。

### 8.2 完成流程

backend 将 OS 结果转换为 `{bytes,os_code,eof,flags}`，验证 `bytes ≤ buffer_len`。短读/短写是正常结果，不自动循环，除非 API 明确为 `read_exact/write_all`。完成赢家注销 Timer/cancel，发布结果，再释放 resource reference 和 quota。observer 事件必须在锁外发送。

### 8.3 关闭竞态

Resource 状态 `Open→Closing→Closed`。Closing 关闭 admission，snapshot 当前 ops，逐个 cancel/drain；新 op 返回 closed。最后一个 op reaped 后关闭 OS handle 并增加 generation。不能先关闭 handle 再让旧 completion 被新 handle slot 接收。

## 9. Reactor 与 Proactor 适配

### 9.1 Reactor（epoll/kqueue）

readiness 不是完成。收到 readable/writable 后执行非阻塞 syscall，处理：

- 成功 bytes：发布完成。
- `EAGAIN/EWOULDBLOCK`：重新 arm，保持 Submitted。
- `EINTR`：检查取消后有界重试。
- EOF：以 `bytes=0,eof=true` 完成。
- 错误：映射平台 code 后 Failed。

edge-trigger 模式必须 drain 到 EAGAIN；one-shot 必须显式 rearm。单 fd 的事件携带 generation，忽略关闭后的 stale event。

### 9.2 Proactor（IOCP/io_uring）

提交时 kernel 获得 buffer lease；completion 直接表示操作结果。IOCP 的 OVERLAPPED、io_uring user_data 均编码安全索引+generation，而非裸 Rust 指针。取消 API 返回“请求已受理”不等于已取消，必须等待 completion 确认。

### 9.3 fallback

能力优先级由 PAL 返回，不能用宿主推测目标：

```text
Linux: io_uring(通过 capability/版本/权限探测) → epoll → blocking pool
Windows: IOCP → blocking pool
macOS/BSD: kqueue → blocking pool
```

fallback 必须保持结果/取消契约，但性能与真正可取消能力写入 capability report。Direct I/O、sendfile/splice 不支持时显式使用 buffered copy；不得标记 zero-copy。

## 10. 背压、资源与公平

资源账本按 runtime/scope/task 三级：`tasks,ready_queue,inflight_io,io_bytes,timers,handles,blocking_jobs,orphan_ops`。reserve 原子检查父子预算，成功返回 Lease；任何退出路径恰好释放一次。

背压策略：

- spawn 队列满：返回 `TASK_LIMIT` 或 await capacity future。
- I/O inflight/bytes 满：submit 返回 `IO_LIMIT` 或 await lease，不占 scheduler 锁。
- completion 风暴：每轮处理固定 batch 后让出 worker。
- Stream/Channel：有界 buffer；下游取消向上游传播，不能无限缓存。

`XLF-12-016` 延迟预算只作为实验 hook：超时产生事件/取消建议，降级函数必须由应用显式提供，runtime 不可擅自复用旧业务结果。

## 11. 平台差异

| 能力 | Linux | Windows | macOS/BSD | 统一语义 |
|---|---|---|---|---|
| readiness | epoll | 非主路径 | kqueue | 可重复 arm、stale generation 拒绝 |
| completion | io_uring（有条件） | IOCP | 部分 API/后备 | 一次完成、buffer lease |
| fd/handle close | fd 可复用 | HANDLE/IOCP key | fd 可复用 | slot+generation 防 ABA |
| affinity/NUMA | sched/sysfs | group affinity | 能力有限 | Unsupported/Denied 可观察 |
| realtime priority | 需权限 | priority class | 需权限/不同语义 | 不保证硬实时 |
| zero-copy | sendfile/splice | TransmitFile 候选 | sendfile 候选 | capability + buffered fallback |

## 12. 实施任务切片

### TASK-P2-RT-001 / 切片 A：同步核心、Handle、Quota、Shutdown

- 不依赖 async RFC。
- 输出：generation handle table、Lease ledger、shutdown 状态和活跃摘要。
- 验收：重复 close/shutdown 幂等；deadline 后仍能继续 drain；无代次复用。
- 回滚：单线程同步 PAL 路径。

### TASK-P2-RT-001 / 切片 B：单线程 Executor、Waker、Timer（RFC 达到已决策后）

- 先实现单 worker，验证 poll/wake/cancel/Timer 状态机。
- 验收：lost wakeup、重复 wake、cancel/fired 竞态模型检查通过。
- 回滚：关闭 `async-runtime` feature。

### TASK-P2-RT-001 / 切片 C：M:N 与 blocking pool

- 在单线程语义稳定后增加 local/global/steal 队列。
- 验收：公平、queue full、worker park race、blocking 隔离。
- 回滚：`workers=1`，保留相同 Task API。

### TASK-P2-RT-001 / 切片 D：Reactor 基线

- Linux epoll、macOS kqueue；Windows 可先 blocking fallback。
- 验收：短读写、EINTR/EAGAIN、close/stale event。
- 回滚：有界 blocking pool。

### TASK-P2-RT-001 / 切片 E：IOCP/io_uring Proactor

- 独立 backend capability gate。
- 验收：cancel-after-complete、complete-after-timeout、orphan buffer 生命周期。
- 回滚：epoll/kqueue/blocking fallback，不改变 API 结果分类。

### TASK-P2-RT-001 / 切片 F：zero-copy/Direct I/O/Stream

- 只有平台矩阵与基准证据后启用。
- 验收：对齐、文件截断、fallback、背压、资源耗尽。
- 回滚：buffered I/O。

## 13. 规划测试与模型检查

| 测试 ID | 场景 | 必需断言 | 状态 |
|---|---|---|---|
| `TEST-RUNTIME-CONC-001` | wake、join、scope、steal、park、取消全排列 | 无 lost wake、单入队、单消费者结果 | planned |
| `TEST-RUNTIME-IO-001` | short/EINTR/EAGAIN/EOF、cancel/timeout/completion、stale handle | 用户终态一次发布；orphan 只回收 | planned |
| `TEST-RUNTIME-SHUTDOWN-001` | Drain/Cancel/Immediate/deadline、故障注入与资源耗尽 | admission 关闭、摘要准确、资源有界 | planned |

测试不得以真实 sleep 判定时序；使用虚拟时钟、可控 backend 和确定性调度 seed。压力结果记录硬件/OS/kernel/backend/Profile 和 P50/P95/P99，不转写为无条件承诺。

## 14. 来源、验收与回滚

来源包括 `XLF-01-009`（协程/CSP）、`XLF-02-009`（XRT）、`XLF-04-007`（io_uring/IOCP）、`XLF-05-001/002/008/009`（线程、M:N、异步/零拷贝 I/O）、`XLF-10-009`（Stream/背压）、`XLF-12-013/015/016`（affinity、实时和延迟预算）。

最终验收需要状态机模型结果、跨平台 contract、故障注入、资源账本和 shutdown drill；当前均为 `planned`。回滚优先级为关闭实验能力 → 稳定 Reactor → 有界 blocking pool → 单线程同步 PAL，任何回滚都不得改变一次完成、generation 和取消结果分类。
