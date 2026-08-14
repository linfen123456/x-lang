---
doc_id: DOC-RUNTIME-ALLOCATION
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
# 分配与资源
> 状态：草案｜Owner：Runtime Memory Team｜追溯：XLF-*、XLE-OPS-*

Allocator、Arena、RAII、OOM 和 ResourceQuota 通过契约接口实现；堆、句柄和映射均有预算。覆盖双重释放、碎片、OOM、并发引用计数和泄漏账本；回退系统分配器需显式记录。
