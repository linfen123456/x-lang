---
doc_id: DOC-RUNTIME-README
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-007, XLF-01-009, XLF-01-011, XLF-02-009, XLF-02-011, XLF-05-001, XLF-05-008, XLF-10-003, XLF-12-014]
---
# X-Lang XRT 运行时工程实施规范

> 状态：草案｜Owner：`role/runtime-team`｜成熟度：CORE（异步/实时为 EXTENDED）

## 目标和边界

XRT 提供启动、ABI、内存/分配、panic、线程/原子、Task/Waker/Cancel、定时器、I/O、PAL、资源配额和可观测性。语言规范定义可观察语义；XRT 只实现这些语义并报告平台能力，不把平台偶然行为伪装成跨平台保证。

Runtime context 状态机为 `Uninitialized → Starting → Running → ShutdownRequested → Draining → Stopped`；只有 `Running` 接受新 task/I/O，`ShutdownRequested` 拒绝新 acquire，`Draining` 等待或取消已有 owner，`Stopped` 的 handle 只返回 `XRT_E_SHUTDOWN`。`xrt_context_clone` 只复制带引用计数的并发安全视图，不复制 allocator、quota owner 或 PAL 私有句柄。

非目标：默认不提供 GC、隐式插锁、跨 FFI 的 panic、通用硬实时、未审计的动态插件和把秘密写入日志。实验性 GC、统一 GPU 内存、Replay 和硬实时必须在独立 RFC/feature gate 中隔离。

## 分层和不变量

```text
X ABI (stable C-compatible handles/types)
  -> resource governor -> allocator/panic/task/io
  -> PAL capability probe -> OS/driver
```

ABI 入口只接收固定宽度整数、布尔、长度指针和不透明句柄；所有句柄明确 owner/thread-safety/close 规则。所有资源 acquire 有 quota lease，所有 lease drop 幂等；panic、cancel、OOM、shutdown 都必须释放已取得且可释放的资源，不能双重释放。

## Profile 化策略

`dev` 开启泄漏账本、完整 backtrace 和 sanitizer hook；`release` 关闭昂贵诊断但保留结构化错误；`ci` 固定调度种子、开启故障注入；`embedded` 无 OS/heap 时只启用 `no_std` 子集；`realtime` 只在能力探测通过的系统启用 deadline/priority。Profile 使用共享 `ProfileSpec`，资源字段映射为 `heap_bytes:u64`、`threads:u32`、`tasks:u64`、`handles:u64`、`io_bytes:u64`、`cancel_grace_ms:u64`、`trace_sample_ppm:u32`；优先级为 `CLI > x.toml profile > TargetSpec defaults > toolchain defaults`，超限返回明确错误而不是隐式阻塞。

## 完成定义

Tier 1 Windows/Linux/macOS x86_64/ARM64 必须通过 ABI、内存、panic、线程、I/O、配额、故障注入、sanitizer、长稳和可观测性测试。每个接口必须有字段类型、前置/后置、错误、取消、并发和上限说明；规划测试使用显式 ID（例如 `TEST-RUNTIME-ABI-001`、`TEST-RUNTIME-CONC-001`、`TEST-RUNTIME-IO-001`），尚未实现的证据标为 `planned`；版本不兼容可检测并能切回上一 ABI/runtime。

## 文档索引

- [ABI 与 FFI 边界](./abi.md)
- [Allocator、OOM 与配额](./allocation.md)
- [Panic、unwind 与 abort](./panic.md)
- [线程、原子、Task/Waker/Cancel](./concurrency.md)
- [Reactor/Proactor I/O](./io.md)
- [平台抽象层](./pal.md)
- [观测、追踪和故障制品](./observability.md)
- [完整接口表](./contracts/contract.md)

回滚只允许恢复已发布的 ABI/runtime 配对；检测到 ABI 不匹配应在启动或首次入口返回 `XRT_E_ABI_MISMATCH`，不得静默使用错误布局。旧 ABI 保留一个稳定周期，迁移由显式 adapter 完成。
