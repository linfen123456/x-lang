---
doc_id: DOC-RUNTIME-ABI
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
# XRT ABI
> 状态：草案｜Owner：Runtime API Maintainer｜追溯：XLF-*、XLC-PLATFORM-*

定义入口、版本探测、句柄所有权、布局、调用约定和 panic/异常边界。ABI 探针在 Tier 1 与 C ABI 黄金测试中运行；不兼容返回诊断而非静默降级。
