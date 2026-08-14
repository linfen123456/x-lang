---
doc_id: DOC-RUNTIME-CONCURRENCY
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
# 并发运行时
> 状态：草案｜Owner：Runtime Concurrency Team｜追溯：XLF-*、XLC-CORE-*

Thread、Task、Waker、Cancel、调度器和原子操作分层；公平性、背压和阻塞隔离不冒充语言确定性保证。压力、竞态、取消和死锁检测为发布门禁。
