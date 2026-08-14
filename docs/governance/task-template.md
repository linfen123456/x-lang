---
doc_id: DOC-GOVERNANCE-TASK-TEMPLATE
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
# X-Lang 正式任务卡模板

```yaml
task_id: TASK-P?-DOMAIN-000
title: "任务名称"
source_ids: [XLF-00-000]
spec_ids: [RULE-DOMAIN-000]
rfc_ids: []
adr_ids: []
project_id: PROJ-DOMAIN-name
project_path: path/to/project
owner: role/compiler-team
backup_owner: role/reviewer
phase: P0
milestone: M0
status: 草案
maturity: CORE
dependencies: []
inputs: []
outputs: []
api_or_artifacts: []
tests: [TEST-domain-unit-001]
performance_budget: "待基准验证"
security_budget: "威胁模型与审计记录"
rollback: "关闭 Feature Gate 或回退到上一稳定版本"
acceptance_evidence: []
estimate: "待评估"
non_goals: []
last_reviewed: 2026-08-15
```

任务关闭前必须补齐实现提交、测试结果、性能/安全证据、发布影响和回滚演练记录。
