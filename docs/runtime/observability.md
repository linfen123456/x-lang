---
doc_id: DOC-RUNTIME-OBSERVABILITY
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
# 运行时可观测性
> 状态：草案｜Owner：Runtime Reliability Team｜追溯：XLF-*、XLE-OPS-*

日志、指标、Trace、Profiler 和 coredump 默认隐私安全、可采样、可关闭。指标记录资源预算和取消原因；故障制品脱敏并保留 request id。
