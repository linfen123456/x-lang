---
doc_id: DOC-TOOLS-FORMATTER-DOC
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
# 格式化与文档
> 状态：草案｜Owner：Developer Experience Team｜追溯：XLF-*、XLE-DEV-*

xfmt 必须幂等，xdoc 生成 API、依赖图和 doc-test；文档示例进入 compile-pass/fail。格式化失败不得覆盖源文件。
