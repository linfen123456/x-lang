---
doc_id: DOC-TOOLS-PLUGIN-SANDBOX
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
# 插件与构建脚本沙箱
> 状态：草案｜Owner：Security + Tooling Team｜追溯：XLF-*、XLE-AI-*

插件/build.x 独立进程、默认只读无网络、有限 CPU/内存/输出；权限提升需审批和审计。超时、逃逸和恶意输出测试失败即终止。
