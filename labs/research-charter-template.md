---
doc_id: DOC-LABS-CHARTER-TEMPLATE
authority: research
owner: role/research-team
backup_owner: role/security-team
version: "2.1.0"
maturity: RESEARCH
status: 已决策
phase: P4
last_reviewed: 2026-08-15
traceability_scope: [LAB, XLF, REVIEW]
---
# Labs 研究 Charter 模板

复制本模板创建独立 Markdown 文件。没有填写的字段必须写“待决策”及负责人，不能删除字段或用宣传文字代替证据。

## 1. 身份与责任

| 字段 | 内容 |
|---|---|
| Charter ID | `LAB-<DOMAIN>-NNN` |
| 来源需求 | `XLF-*` / `XLC-*` / 复审条目 |
| Owner / Backup Owner | 研究负责人 / 安全或质量负责人 |
| 状态与复审日期 | proposed / approved / running / evidence_ready / graduated / stopped / archived |
| 目标阶段 | 只能是 EXPERIMENTAL 或 RESEARCH，不得成为 P0-P4 CORE 前置 |

## 2. 假设、用户价值与非目标

写出一个可被实验推翻的假设、受益用户、当前基线和为什么值得研究。列出明确非目标，例如“不改变稳定语义”“不接触生产数据”“不承诺性能结果”。

## 3. 原型范围与依赖

定义最小原型、代码或文档路径、允许调用的组件、禁止依赖和 Feature Gate。CORE/EXTENDED 不得反向依赖本研究；关闭 Gate 后主线构建、测试和发布必须保持可用。

## 4. 数据来源与数据政策

逐项记录数据集、许可证、授权、个人/敏感数据分类、采集方式、保留期限、删除方式和可复现替代数据。数据权利不清或无法删除时自动 No-Go。

## 5. 预算与资源上限

记录 CPU/GPU 小时、存储、网络、费用、最长日历时间和负责审批的人。达到 80% 预算触发复审，达到 100% 自动停止；不得以拆分任务规避预算。

## 6. 威胁、安全、伦理与法规

引用[AI 与 Agent 威胁模型](../docs/ai/threat-model.md)，补充本项目的攻击面、滥用场景、秘密与网络权限、模型/数据供应链、双重用途、地区法规和人工监督。无法验证的高影响安全边界属于 No-Go。

## 7. 基准、测试和成功标准

定义对照基线、硬件/OS/工具链、数据集版本、随机种子、样本量、P50/P95/P99 或统计方法、正确性测试、安全测试和负向结果记录。成功标准必须含误差区间和最大成本，不接受“明显更快”“智能提升”等不可证伪表述。

## 8. Go / No-Go 决策

Go 至少要求实验可复现、收益超过预设阈值、安全和许可证通过、成本在预算内。No-Go 至少包括安全边界无法验证、数据权利不清、预算超限、无法复现、收益不足或破坏稳定兼容。记录决策人、日期和依据。

## 9. 退出、回滚和清理

说明如何关闭 Feature Gate、隔离/删除实验制品、撤销权限和秘密、删除受限数据、恢复稳定实现并发布负向结果。停止研究不得删除决策和复现说明。

## 10. 晋级所需 RFC/ADR 与证据

列出候选 RFC/ADR、测试 ID、实验报告、许可证审查、安全评审和维护 Owner。只有通过正式 RFC、主线质量门禁、迁移与回滚评审后，能力才能从 Labs 迁出；Charter 本身不授予晋级资格。
