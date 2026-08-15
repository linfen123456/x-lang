---
doc_id: DOC-GOVERNANCE-TASK-TEMPLATE
authority: implementation
owner: role/program-management
backup_owner: role/architecture
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P0
last_reviewed: 2026-08-15
traceability_scope: [GOVERNANCE, XLF, XLC, XLE]
---
# X-Lang 正式任务卡模板

```yaml
task_id: TASK-P2-COMPILER-001
owner: role/compiler-team
backup_owner: role/quality-team
status: 待决策
phase: P2
source_ids: [XLF-01-002]
spec_or_rfc: RFC-0001
project_id: PROJ-COMPILER-CORE
test_ids: [TEST-COMPILER-CONFORMANCE-001]
inputs: [docs/specs/language-core.md]
outputs: [compiler/x-syntax/README.md]
acceptance:
  - 正例、反例、边界和错误码已定义
  - 规范、实现、测试、文档和安全审查通过
  - Markdown 标题、链接、代码围栏和术语由评审人员检查通过
  - XLF/XLC/XLE、规范、项目、测试与证据映射由评审人员逐项抽查通过
rollback: feature flag 或反向迁移步骤
evidence: [artifacts/ci/run-id.json]
```

任务没有 `source_ids/spec_or_rfc/project_id/test_ids/phase/status/evidence` 时不得进入“已完成”。研究任务还必须链接 Charter、预算、Go/No-Go 和退出报告。
