---
doc_id: DOC-RUNTIME-CONTRACTS-CONTRACT
authority: implementation
owner: role/documentation
backup_owner: role/architecture
version: "1.0"
maturity: EXTENDED
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF, XLC, XLE]
---
# XRT 运行时接口契约

> 状态：草案｜Owner：Runtime API Maintainer｜追溯：XLF-050~120、XLC-PLATFORM-*、XLE-OPS-*

## ABI 与线程安全

Runtime ABI 入口使用 C-compatible 固定宽度类型、显式所有权和 abi_version。句柄为不透明值，创建与销毁必须成对；跨线程传递需标记 Send 能力，非线程安全对象禁止共享。异常、panic 和调用栈不得跨未声明 FFI 边界。

## 核心接口

    Allocator::alloc(layout) -> Result<NonNull, X-E8001>
    Task::spawn(future, budget, cancel) -> Result<TaskId, X-E8101>
    Waker::wake(TaskId) -> Result<(), X-E8102>
    Clock::now(kind) -> Timestamp
    Timer::sleep(deadline, cancel) -> Result<(), X-E8201>
    Io::submit(op, deadline, cancel) -> Result<OpId, X-E8301>
    ResourceQuota::reserve(kind, amount) -> Result<Lease, X-E8401>

所有调用可失败；Lease 释放幂等。unsafe 仅限 PAL、allocator、FFI 适配层，并须有不变量注释和 Miri/ASan 证据。

## 取消、超时和资源上限

取消是协作式的：任务、I/O、定时器和阻塞池都必须观察 token；不可取消系统调用使用隔离线程并有泄漏预算。默认进程配额：堆 512 MiB、线程 1024、任务 1M、句柄 100k、单次 I/O 64 MiB。超限返回结构化错误并可触发 Load Shed；结果区分 cancelled、deadline_exceeded 和 completed。

## 平台、负向测试与回滚

PAL 报告 epoll/io_uring/IOCP/kqueue、TLS、时钟、信号和 NUMA 能力；缺失能力选择明确 fallback 或返回 unsupported。覆盖错误 layout、双重 free、跨线程句柄、OOM、队列满、时钟回拨、信号重入和 panic 递归。验收需有 ABI 探针、跨平台契约、sanitizer、压力、长稳和故障注入；泄漏或差异时切回旧 ABI。
