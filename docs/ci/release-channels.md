---
doc_id: DOC-CI-RELEASE-CHANNELS
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
# 发布通道、制品与回滚

| 通道 | 目的 | 兼容承诺 |
|---|---|---|
| Nightly | 主干探测、实验特性 | 不保证兼容；可撤回 |
| Beta | 候选验证、生态迁移 | 记录已知破坏和迁移 |
| Stable | 1.0 核心与稳定 std | 遵守兼容和安全政策 |
| LTS | 受限安全/关键修复 | 仅在资源和平台证据满足时承诺 |

发布包必须包含版本、目标三元组、SBOM、签名、来源证明、变更日志、校验和、许可证、已知问题和支持期限。回滚前确认数据 Schema 兼容；应用回滚、编译器回滚和数据库回滚分开演练。Kill Switch 只能关闭扩展/实验能力，不得静默改变核心语言语义。
