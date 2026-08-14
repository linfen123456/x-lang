---
doc_id: DOC-LABS-RESEARCH-CHARTER-TEMPLATE
authority: research
owner: role/documentation
backup_owner: role/architecture
version: "1.0"
maturity: RESEARCH
status: 研究
phase: P6
last_reviewed: 2026-08-15
traceability_scope: [XLF, XLC, XLE]
---
# Labs 研究 Charter 模板

```yaml
charter_id: LAB-AREA-000
title: "研究主题"
owner: role/research-team
maturity: RESEARCH
status: 草案
phase: P6
hypothesis: "可证伪假设"
non_goals: []
prototype_scope: []
dependencies: []
budget: {people: 0, cpu_hours: 0, storage_gb: 0, deadline: "YYYY-MM-DD"}
benchmarks: []
threat_model: []
data_policy: {classification: public, retention: "期限", deletion: "方法"}
success_criteria: []
exit_conditions: []
rollback_or_disable: "关闭 Feature Gate 并移除实验依赖"
source_ids: []
rfc_ids: []
adr_ids: []
evidence: []
```

晋级 Stable 前必须转化为正式 RFC/ADR，完成可重复原型、兼容/安全/性能证据、平台矩阵和维护资源评审；否则归档或继续保持 Labs 隔离。
