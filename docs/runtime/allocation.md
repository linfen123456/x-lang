---
doc_id: DOC-RUNTIME-ALLOCATION
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-01-006, XLF-05-005, XLF-05-006, XLF-10-010, XLF-10-011]
---
# Allocator、OOM、生命周期与资源配额

> 状态：草案｜Owner：`role/runtime-team`

## Allocator 接口

`Layout{size:usize,align:usize}` 要求 size 非负、align 为非零 2 的幂且不超过 target max alignment。`Allocator::alloc(layout, quota:&ResourceQuota)->Result<NonNull<[u8]>,AllocError>` 前置为 layout 合法并取得 quota lease；后置为返回满足对齐且由该 allocator owner 的内存。`dealloc(ptr,layout)` 要求 pointer、layout、allocator 三者匹配，后置为释放一次；违反返回 `XRT_E_INVALID_FREE` 并进入受控 abort/诊断模式，不能继续假装成功。

Arena 字段为 `chunk_size:usize`、`max_bytes:u64`、`reset_policy:ResetPolicy`；reset 只能在 arena owner 生命周期结束或显式 token 许可时执行。引用计数/Weak 的 upgrade、drop 和 allocator 回调不可在持锁时调用用户代码。

分配路径固定为 `validate Layout → reserve quota lease → allocator call → validate returned alignment/range → publish ownership record`。allocator 返回 null 时先释放 lease 再按 OOM Profile 处理；返回错对齐或重叠已分配区间属于 allocator invariant violation，进入受控 abort，不能交给用户。dealloc 先以 `(allocator_id,allocation_id,generation)` 验证 ownership record，再从可见表摘除、调用底层释放并归还 lease；并发 double-free 只能有一个 CAS 赢家。

零大小分配返回非空对齐 sentinel 或按 ABI 规定的唯一行为，不能送入底层 allocator 再猜测。`size + align - 1`、数组 `count × element_size` 和 quota 累加均使用 checked arithmetic。realloc 语义是成功后旧 allocation 失效，失败则旧 allocation 保持有效；quota 同时覆盖迁移峰值，避免先释放旧账本造成超卖。

Arena 以 chunk generation 标识借用；reset 先关闭新分配，等待/验证所有可逃逸 lease 为零，再一次提高 generation 并释放 chunk。P1/P2 不支持引用跨 reset 存活；debug sanitizer 可用 generation 捕获 stale pointer，但它不是安全证明。

## OOM 与配额

`ResourceQuota` 字段为 `heap_bytes:u64`、`mapped_bytes:u64`、`handles:u32`、`threads:u32`、`tasks:u64`、`io_inflight:u32`、`deadline:Instant?`。`reserve(kind,amount)->Result<Lease,QuotaError>` 原子地检查并增加使用量；`Lease::release` 幂等。超限返回 `XRT_E_QUOTA`，内存分配返回 `XRT_E_OOM`，调用方可 Load Shed 或降级，不得自动重试无限次。

父子 quota 预留按根到叶固定顺序执行；任一级失败则逆序释放已取 lease，避免部分记账。`used + amount ≤ limit` 使用 CAS 循环和 checked addition；取消/ShutdownRequested 关闭 admission 后新 reserve 返回对应状态。Lease 状态 `Reserved → Attached → Released` 单向变化，资源句柄发布前必须 Attached，失败路径可从 Reserved 直接 Released。

OOM 策略由 Profile 选择：`abort` 立即写最小诊断后终止，`recover` 仅在已预留 emergency pool 中生成错误并释放调用栈可释放资源，`embedded` 返回静态错误；不得在任意 OOM 路径继续分配格式化字符串、锁或网络。

emergency pool 在 runtime init 时预留且只允许第一个 OOM owner 使用，状态为 `Available → InUse → Consumed`；二次 OOM 直接走最小 abort。recover 只适用于显式 fallible allocation API，普通不可失败分配触发 panic/abort 的具体选择由 Profile 冻结，不能在调用现场动态变化。

## 并发、负向测试、版本与回滚

Allocator metadata 使用线程安全分区或明确非线程安全标志；不能把 arena pointer 跨线程伪装为 Send。Allocator 变更采用 `prepare(new) → dual-account → canary → promote → retire(old)`，canary 只接收新 allocation，旧 allocation 始终由原 allocator_id 释放；retire 必须等待其 live count 为零。任何 peak、碎片、泄漏或 OOM 回归都可停止 canary 并切回旧 allocator；旧 allocator 至少保留一个稳定周期。

canonical 规划测试 `TEST-RUNTIME-ALLOC-001`、`TEST-RUNTIME-ALLOC-002`、`TEST-RUNTIME-ALLOC-003` 覆盖 checked Layout/零大小/错对齐、并发 alloc/free/realloc/double-free、父子配额竞态、Arena reset generation、OOM 中 panic 和 allocator canary 回滚，状态均为 `planned`。heap 512 MiB、单分配 64 MiB、映射 1 GiB 是 Profile 的 `candidate_default`，遵循 [运行时 Budget 治理](./README.md#资源预算治理)，不是容量或性能承诺。回滚不改变公开 ABI：停止新 allocator admission，等待/迁移可迁移资源，保留旧 allocator 处理其已有 allocation；不能用另一 allocator 释放旧指针。
