---
doc_id: DOC-TESTING-PERFORMANCE-COMPATIBILITY
authority: evidence
owner: role/performance-team
backup_owner: role/quality-team
version: "2.0.0"
maturity: EXTENDED
status: 已决策
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [QUALITY, XLF, XLC, XLE]
---
# 性能、兼容性与可复现测试

## 基准协议

任何性能数字必须同时记录硬件、OS、工具链版本、编译参数、数据集、预热、样本数、P50/P95/P99、对照版本、置信区间和复现命令。没有完整记录只能写“研究目标”。阈值按平台和 Tier 分开，禁止用平均值掩盖尾延迟。

## 兼容矩阵

| 维度 | N-1 | N | N+1/实验 |
|---|---|---|---|
| 编译器/标准库 | 读取并构建 | 发布基线 | 探针，不阻断稳定 |
| 锁文件/制品 | 可升级、可回滚 | 签名且可复现 | 兼容性报告 |
| ABI/协议 | C ABI/公开 Schema | 稳定契约 | 明确 Feature Gate |
| OS/架构 | Tier 1 必测 | Tier 1 必测 | Tier 2/3 按能力 |

性能回归超过 5% 触发阻断和自动 bisect；超过 2% 进入趋势告警。兼容破坏必须有迁移工具、弃用窗口、公告、回滚和 RFC。
