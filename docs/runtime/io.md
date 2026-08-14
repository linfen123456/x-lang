---
doc_id: DOC-RUNTIME-IO
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
# 异步 I/O
> 状态：草案｜Owner：Runtime I/O Team｜追溯：XLF-*、XLC-PLATFORM-*

统一 Reactor/Proactor 接口，适配 epoll、io_uring、IOCP、kqueue；提交、完成、取消和资源关闭幂等。覆盖断网、队列满、超时、句柄耗尽和平台 fallback。
