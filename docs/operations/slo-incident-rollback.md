---
doc_id: DOC-OPERATIONS-SLO-INCIDENT-ROLLBACK
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
# SLO、事故响应与回滚手册

## 1. SLI/SLO 基线

| 服务 | SLI | 初始目标 |
|---|---|---|
| 注册表/包下载 | 成功率、P95 延迟、完整性 | 目标待基线验证；按月审查 |
| CI 构建 | 成功率、排队/执行 P95 | 目标待团队容量确认 |
| LSP/文档服务 | 可用率、诊断延迟 | 目标待真实负载验证 |
| 发布系统 | 制品可验证率、回滚成功率 | 100% 签名与来源校验 |

所有目标必须附测量命令、窗口、排除项、预算和 Owner；不得把“高可用”当验收标准。

## 2. 事故流程

检测→分级→遏制→恢复→验证→无责复盘。事故记录 `incident_id`、时间线、影响范围、数据/安全判断、决策、命令、负责人、外部沟通和后续行动项。SEV-1/2 事故必须产生回归测试或门禁改进。

## 3. 回滚与灾备

发布前演练制品回滚、配置回滚、数据库 Expand/Migrate/Contract、密钥轮换和注册表撤回。每项服务在正式承诺前记录 RTO/RPO；没有备份恢复和校验结果不得宣称具备灾备能力。遥测默认最小化、脱敏和关闭个人内容采集。
