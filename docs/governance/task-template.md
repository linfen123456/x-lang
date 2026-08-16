---
doc_id: DOC-GOVERNANCE-TASK-TEMPLATE
authority: implementation
owner: role/program-management
backup_owner: role/architecture
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P0
last_reviewed: 2026-08-16
traceability_scope: [GOVERNANCE, XLF, XLC, XLE]
---
# X-Lang 正式任务卡模板

本模板直接填写 Markdown，不要求另建 YAML/JSON。示例值只说明格式，不表示项目或证据已经存在。

## 任务身份与追溯

| 字段 | 填写要求 | 示例 |
|---|---|---|
| Task ID | 唯一、不可复用 | `TASK-P2-COMPILER-001` |
| Owner / Backup | 角色或已确认人员 | compiler / quality |
| 阶段、成熟度、状态 | 分别填写，不相互推导 | P2 / CORE / 待决策 |
| 原始来源 | 真实 XLF/XLC/XLE | `XLF-01-002` |
| 规范决策 | 已存在或明确 planned 的 Rule/RFC/ADR | `RULE-LANG-001` |
| 项目与路径 | 物理责任域和允许修改路径 | `compiler/x-syntax` |
| Canonical Test ID | `TEST-*`；目录 CASE 仅作说明 | `TEST-LANG-LEX-001` |

## 输入、输出与依赖

列出版本化输入、上游任务、接口版本和外部标准。输出必须是可审查工件，例如规范条文、源码模块、测试语料、诊断或发布制品；“完善功能”“支持所有平台”不是合格输出。跨团队依赖要写 Owner、所需状态和失败时的降级路线。

## 实施与约束

说明最小可交付切片、非目标、所有权/错误/取消/资源契约、目标平台、性能基线状态和安全边界。实验任务必须通过 Feature Gate 隔离，并证明关闭后 CORE 的构建、测试和发布不受影响。

## 验收、证据与回滚

- 验收：正例、反例、边界、错误码和平台差异均有 canonical 测试映射。
- 证据：尚未运行时写 `planned`；运行后记录 commit、toolchain、target、run ID、日志和制品摘要，不填写假路径。
- 回滚：写清关闭开关、上一兼容版本、数据/Schema 处理和验证步骤；只写“git revert”不足以覆盖外部状态。
- 停止条件：依赖未满足、安全边界不可验证、预算耗尽或回滚失败时停止，不以降级测试绕过。

任务没有来源、规范、项目、canonical Test ID、阶段、状态、验收和证据状态时不得进入“已完成”。研究任务还必须链接 Charter、预算、Go/No-Go 和退出报告。
