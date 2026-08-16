---
doc_id: DOC-LABS-README
authority: research
owner: role/research-team
backup_owner: role/security-team
version: "2.0.0"
maturity: RESEARCH
status: 已决策
phase: P6
last_reviewed: 2026-08-16
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

本表只登记各能力中尚未满足正式实施门禁的“研究剩余部分”，不能把已经按回归路线进入 P3-P5 的切片重新降级成纯研究。例如 CPU Tensor/Shape、PQC Provider、eBPF 探针和本地项目索引已有条件实施路线；Labs 只研究编译期 AD、跨设备统一内存、受限后端、联邦同步等高风险部分。正式边界以[回归路线](../docs/X-Lang未纳入与偏离内容再审核及回归路线.md)为准。

| 项目 | 状态 | 章程 | 是否阻塞主线 |
|---|---|---|---|
| 可选 GC | proposed | 待按模板建立 | 否 |
| 编译期自动微分、跨设备统一内存与多 GPU 自动并行 | proposed | 待按模板建立；CPU Tensor 和独立图/Tape 不在此阻塞 | 否 |
| 受限 ZKP 电路后端 | proposed | 待按模板建立；标准化 PQC Provider 按 P4 实施路线评审 | 否 |
| 因果回溯、确定性重放与时间旅行调试 | proposed | 待按模板建立 | 否 |
| 通用硬实时认证与高风险裸机/eBPF 扩展 | proposed | 待按模板建立；受限 no_std/eBPF 探针按条件实施 | 否 |
| `.xbrain` 跨组织联邦同步 | proposed | 待按模板建立；本地索引、来源与删除能力按 P4 实施 | 否 |
| 无人自治优化、自修复与生产混沌决策 | proposed | 待按模板建立；可审计建议、熔断和故障注入按正式路线实施 | 否 |
| 空间、触觉与脑机接口 | proposed | 待按模板建立 | 否 |

模板入口：[研究 Charter 模板](research-charter-template.md)。新增研究项目时创建独立 Markdown 章程并更新本表；没有章程的 proposed 条目不得启动代码、申请生产数据或占用持续 GPU/云预算。只有状态和证据真实存在时才能迁移。
