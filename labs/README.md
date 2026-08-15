---
doc_id: DOC-LABS-README
authority: research
owner: role/research-team
backup_owner: role/security-team
version: "2.0.0"
maturity: RESEARCH
status: 已决策
phase: P4
last_reviewed: 2026-08-15
traceability_scope: [LAB, XLF, XLC, REVIEW]
---
# X-Lang Labs 研究区

Labs 是隔离的研究区，不被 CORE/EXTENDED 依赖，不向 Stable 暗示兼容承诺。每项研究能力必须在本目录建立独立 Markdown 章程，且在开始前写出假设、Owner、预算、威胁模型、数据来源、Go/No-Go、退出条件和下一次评审日期。

## 生命周期

```text
proposed → approved → running → evidence_ready → graduated | stopped | archived
```

`approved` 需要研究负责人、安全负责人和质量负责人签字；`evidence_ready` 需要可复现实验、负向结果、成本和许可证。No-Go 或预算/安全阈值触发立即停止、隔离制品、保留日志并写退出报告。只有稳定替代方案通过 G0–G6 后才可迁入主线。

## 研究项目清单

| 项目 | 状态 | 章程 | 是否阻塞主线 |
|---|---|---|---|
| 可选 GC | proposed | 待按模板建立 | 否 |
| GPU/统一内存与自动微分 | proposed | 待按模板建立 | 否 |
| ZKP/PQC | proposed | 待按模板建立 | 否 |
| 因果回溯、确定性重放与时间旅行调试 | proposed | 待按模板建立 | 否 |
| eBPF、裸机与硬实时认证 | proposed | 待按模板建立 | 否 |
| `.xbrain` 与 Agent 联邦记忆 | proposed | 待按模板建立 | 否 |
| 自动优化、自修复与混沌工程 | proposed | 待按模板建立 | 否 |
| 空间、触觉与脑机接口 | proposed | 待按模板建立 | 否 |

模板入口：[研究 Charter 模板](research-charter-template.md)。新增研究项目时创建独立 Markdown 章程并更新本表；只有状态和证据真实存在时才能从 proposed 迁移。
