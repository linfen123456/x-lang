---
doc_id: DOC-RUNTIME-README
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
# X-Lang XRT 运行时工程专题

> 状态：草案｜成熟度：CORE（异步/实时为 EXTENDED）｜Owner：Runtime Platform Team
> 规范依据：内存、并发、错误处理和 ABI 规范
> 追溯字段：XLF-*、XLC-PLATFORM-*、XLE-OPS-*

## 目标与目录

XRT 提供启动、资源、线程、任务、I/O、进程、观察和平台抽象；标准库通过 Runtime ABI 调用它。运行时不得反向依赖编译器前端、IDE 或 AI。

    docs/runtime/
    ├─ README.md
    ├─ abi.md
    ├─ allocation.md
    ├─ panic.md
    ├─ concurrency.md
    ├─ io.md
    ├─ pal.md
    ├─ observability.md
    └─ contracts/contract.md

## 完成定义

启动、退出、析构和失败路径在 Windows/Linux/macOS Tier 1 通过；资源上限可配置且有 Load Shed；无 unsafe 越权系统调用；sanitizer、压力、故障注入和长稳报告齐全。

## 负向测试与回滚

覆盖 OOM、句柄/线程耗尽、重复关闭、取消竞态、时钟回拨、I/O 错误、只读文件系统、信号冲突和 panic 期间再次 panic。运行时 ABI 采用版本探测；不兼容时启动失败并指导安装匹配 runtime，保留旧 ABI 一个稳定周期。
