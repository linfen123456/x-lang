---
doc_id: DOC-OPERATIONS-SLO-INCIDENT-ROLLBACK
authority: evidence
owner: role/operations-team
backup_owner: role/security-team
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [QUALITY, SECURITY, XLE, REVIEW]
---
# SLO、事故响应、回滚与灾备

## SLI/SLO 基线

| SLI | Stable 目标 | 告警阈值 |
|---|---:|---:|
| 编译/制品服务可用性 | 月度 99.9% | 5 分钟错误预算燃烧率 > 2 |
| P95 编译延迟（固定语料） | 基线 +10% | 连续 3 个窗口 |
| 失败可诊断率 | ≥99% 有 run/trace/artifact ID | 任一无关联严重事故 |
| 签名/供应链验证 | 100% | 任意绕过或不匹配立即阻断 |

SLO 只对声明的 Tier、版本和工作负载有效；没有数据的目标是候选，不是承诺。错误预算耗尽时冻结非必要变更，优先修复可靠性和回归。

## 事故流程

1. 值班人确认影响、建立 `INC-YYYYMMDD-NNN`，冻结高风险发布并保护证据。
2. 5 分钟内分级：SEV-1 数据损坏/安全/大范围不可用；SEV-2 关键能力退化；SEV-3 局部或可绕过。
3. 指派 Incident Commander、技术负责人、沟通负责人和记录人；每 15 分钟更新时间线。
4. 先止血（kill switch、限流、降级、隔离），再定位；不在事故中直接做大重构。
5. 恢复后验证 SLO、数据完整性、签名和回滚结果；SEV-1/2 在 5 个工作日内完成无责复盘和回归测试。

## 回滚与灾备

代码/制品回滚优先使用上一签名版本；数据库采用 Expand→Migrate→Contract，回滚前先验证 N-1 读写兼容。数据恢复必须校验哈希、顺序、幂等键和权限，禁止以恢复覆盖原始证据。

| 资产 | RTO | RPO | 演练 |
|---|---:|---:|---|
| 发布制品/签名/SBOM | 1 小时 | 0 | 每季度 |
| 注册表元数据 | 4 小时 | 15 分钟 | 每季度 |
| 研究数据 | 1 工作日 | 24 小时 | 每半年 |

灾备演练必须注入区域不可用、密钥轮换、损坏快照、网络分区和权限丢失；演练记录链接到测试/追溯 ID，失败即形成阻断行动项。
