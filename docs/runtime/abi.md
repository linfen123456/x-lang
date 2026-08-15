---
doc_id: DOC-RUNTIME-ABI
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-02-011, XLF-10-003, XLF-11-008, XLF-12-014]
---
# XRT ABI 与 FFI 契约

> 状态：草案｜Owner：`role/runtime-team`

## ABI 版本与数据布局

入口导出为 `extern "C"`，固定字段使用 `u8/u16/u32/u64/i32/i64`, `bool:u8`、`XrtSemVer{major:u16,minor:u16,patch:u16,reserved:u16}`、`XrtRequestId{hi:u64,lo:u64}`（语义为 u128）和 `XrtSlice{ptr:*const u8,len:u64}`。句柄统一为 `XrtHandle{raw:u64,kind:u32,generation:u32}`，错误统一为 `XrtStatus{code:u32,detail:u32,retryable:u8,reserved:u8,request_id:XrtRequestId}`；结构体附带 `size:u32`、`abi_version:u16`、`flags:u32`。指针只在调用期间借用，句柄为不透明 owner token，不能按整数推断布局。

 C ABI 禁止 `Result`、Rust enum、trait object、Rust slice 或 panic 穿越边界。`xrt_init(req:*const XrtInit,out_ctx:*mut XrtHandle)->XrtStatus` 前置是 req/out_ctx 非空、版本和 target hash 匹配；后置是成功写入 context handle，失败不写入 out。`xrt_shutdown(ctx:XrtHandle)->XrtStatus` 要求无活跃 lease 或按策略取消并等待，后置为所有 runtime 线程/句柄关闭。版本不匹配返回 `XRT_E_ABI_MISMATCH`，不做隐式转换。

## 所有权、线程和错误

每个 API 说明 `borrowed`、`owned` 或 `out` 指针；owned 必须由同一 allocator 的 `xrt_free` 释放，跨 ABI 不得释放。错误只通过 `XrtStatus` 返回，`request_id` 始终为 16 字节 u128 语义；不把 panic 当 C++/SEH 异常传播。FFI 调用者必须检查 status 并消费 out 参数；未知错误码按 fatal 处理。

跨线程传递只允许 `Send` 句柄，跨线程共享只允许 `Sync` 句柄；context 默认非线程安全，调用方需使用 `xrt_context_clone(src:XrtHandle,out_view:*mut XrtHandle)->XrtStatus` 返回带引用计数的并发安全视图，不能复制 allocator/quota owner。ABI 回调不得在 runtime 内部锁持有时回调用户代码。

## 负向、资源和回滚

ABI 黄金测试覆盖错误 size/version、错对齐、空指针与溢出长度、重复 close、跨线程错误句柄、panic 穿越 FFI、不同 endianness/指针宽度和 allocator 不匹配。单次 slice 最大 64 MiB、句柄 100k、回调栈深度 64；超过返回 `XRT_E_LIMIT`。每次 ABI 变更增加 versioned symbol/adapter，保留旧 header 与探针一个稳定周期；回归时依据 feature gate 恢复上一版本，不覆盖旧制品。
