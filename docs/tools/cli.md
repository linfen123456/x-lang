---
doc_id: DOC-TOOLS-CLI
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
# CLI 契约
> 状态：草案｜Owner：Tooling Team｜追溯：XLF-*、XLE-DEV-*

统一命令、退出码、JSON schema、非 TTY 行为、超时和取消。坏配置、未知命令和环境缺失需可操作错误；输出不得泄露秘密。
