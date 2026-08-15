---
doc_id: DOC-RUNTIME-ALLOCATION
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-006, XLF-05-005, XLF-05-006, XLF-10-010, XLF-10-011]
---
# Allocator、OOM、生命周期与资源配额

> 状态：草案｜Owner：`role/runtime-team`

## Allocator 接口

`Layout{size:usize,align:usize}` 要求 size 非负、align 为非零 2 的幂且不超过 target max alignment。`Allocator::alloc(layout, quota:&ResourceQuota)->Result<NonNull<[u8]>,AllocError>` 前置为 layout 合法并取得 quota lease；后置为返回满足对齐且由该 allocator owner 的内存。`dealloc(ptr,layout)` 要求 pointer、layout、allocator 三者匹配，后置为释放一次；违反返回 `XRT_E_INVALID_FREE` 并进入受控 abort/诊断模式，不能继续假装成功。

Arena 字段为 `chunk_size:usize`、`max_bytes:u64`、`reset_policy:ResetPolicy`；reset 只能在 arena owner 生命周期结束或显式 token 许可时执行。引用计数/Weak 的 upgrade、drop 和 allocator 回调不可在持锁时调用用户代码。

## OOM 与配额

`ResourceQuota` 字段为 `heap_bytes:u64`、`mapped_bytes:u64`、`handles:u32`、`threads:u32`、`tasks:u64`、`io_inflight:u32`、`deadline:Instant?`。`reserve(kind,amount)->Result<Lease,QuotaError>` 原子地检查并增加使用量；`Lease::release` 幂等。超限返回 `XRT_E_QUOTA`，内存分配返回 `XRT_E_OOM`，调用方可 Load Shed 或降级，不得自动重试无限次。

OOM 策略由 Profile 选择：`abort` 立即写最小诊断后终止，`recover` 仅在已预留 emergency pool 中生成错误并释放调用栈可释放资源，`embedded` 返回静态错误；不得在任意 OOM 路径继续分配格式化字符串、锁或网络。

## 并发、负向测试、版本与回滚

Allocator metadata 使用线程安全分区或明确非线程安全标志；不能把 arena pointer 跨线程伪装为 Send。Allocator 变更采用 `prepare(new) → dual-account → canary → promote → retire(old)`，任何 peak、碎片、泄漏或 OOM 回归都可在不改变 ABI 的情况下切回旧 allocator；旧 allocator 保留一个稳定周期。测试规划为 `TEST-RUNTIME-ALLOC-001`、`TEST-RUNTIME-ALLOC-002`、`TEST-RUNTIME-ALLOC-003`，状态均为 `planned`，覆盖错对齐/双重 free、并发 alloc/free、配额竞态和 OOM 期间 panic。Profile 默认 heap 512 MiB、单分配 64 MiB、映射 1 GiB；每项上限可降低，提升需审计。
