---
doc_id: DOC-RUNTIME-PAL
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P1
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-011, XLF-05-001, XLF-05-008, XLF-12-013, XLF-12-015]
---
# 平台抽象层（PAL）

> 状态：草案｜Owner：`role/runtime-team`

## 能力探测

`PalCapabilities` 字段为 `os:Os`、`arch:Arch`、`page_size:u32`、`clock:ClockCaps`、`io:IoCaps`、`threads:ThreadCaps`、`signals:SignalCaps`、`filesystem:FsCaps`、`tls:TlsCaps`、`sysroot_hash:Hash32`。`Pal::probe(request:PalTargetRequest{triple:String,arch:String,os:String,sysroot_fingerprint:Hash32})->Result<PalCapabilities,PalError>` 只消费公开 primitive request，不依赖 compiler 私有 `TargetSpec`；编译器负责把 TargetSpec 映射为 request。交叉编译不把运行主机能力写入目标制品。能力结果带 probe version/fingerprint。

## 操作边界

PAL API 的文件路径、权限、线程优先级、affinity、时钟、信号、I/O backend 都必须先通过能力/权限检查；每个操作返回 `Supported|Unsupported|Denied|Failed` 并保留平台 code。调用方不得依赖裸 OS handle 的布局，所有 handle 通过 XRT opaque wrapper 管理。系统调用适配层是唯一允许 `unsafe` 的区域之一。

`Clock::now(kind:Monotonic|Wall)->Timestamp` 保证 monotonic 不倒退（除非检测到平台故障并报告）；wall clock 明确允许调整。`Signal::install` 只注册 async-signal-safe trampoline，复杂处理转交控制线程。

## 资源 Profile、负向测试和回滚

覆盖不存在 sysroot、能力误报、权限拒绝、时钟回拨、信号重入、文件系统只读、长路径、大小写差异、epoll/io_uring/IOCP/kqueue 缺失、NUMA/affinity 无权和目标/主机混淆。`TEST-RUNTIME-PAL-001` 比较能力矩阵，`TEST-RUNTIME-PAL-002` 做跨平台 contract，`TEST-RUNTIME-PAL-003` 做故障注入。能力缓存按 OS/kernel/driver/probe 版本分 key；回归时禁用具体 capability、切到稳定 fallback，旧 fingerprint 制品保留。
