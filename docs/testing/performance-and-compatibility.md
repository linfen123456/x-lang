---
doc_id: DOC-TESTING-PERFORMANCE-COMPATIBILITY
authority: evidence
owner: role/performance-team
backup_owner: role/quality-team
version: "2.0.0"
maturity: EXTENDED
status: 已决策
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [QUALITY, XLF, XLC, XLE]
---
# 性能、兼容性与可复现测试

## 基准协议

任何性能数字必须同时记录硬件、OS、工具链版本、编译参数、数据集、预热、样本数、P50/P95/P99、对照版本、置信区间和复现命令。没有完整记录只能写“研究目标”。阈值按平台和 Tier 分开，禁止用平均值掩盖尾延迟。

本文件只冻结测量协议，不冻结全项目统一百分比。每个基准在启用门禁前必须有 Benchmark ID、Owner、平台/工作负载、至少一个稳定版本的基线、噪声分布、最小可检测变化和批准 RFC。尚无这些证据时结果只生成趋势报告，不得因任意百分比阻断发布或通过扩大容差放行。

## 兼容矩阵

| 维度 | N-1 | N | N+1/实验 |
|---|---|---|---|
| 编译器/标准库 | 读取并构建 | 发布基线 | 探针，不阻断稳定 |
| 锁文件/制品 | 可升级、可回滚 | 签名且可复现 | 兼容性报告 |
| ABI/协议 | C ABI/公开 Schema | 稳定契约 | 明确 Feature Gate |
| OS/架构 | Tier 1 必测 | Tier 1 必测 | Tier 2/3 按能力 |

性能门禁按 Benchmark RFC 中的统计阈值执行：超过经验证的阻断预算才触发阻断和 bisect；低于阻断预算但超过趋势预算时告警。阈值必须高于已测噪声并按平台分别配置；没有基线/RFC 时标记 `insufficient-evidence`，不能套用历史材料中的 5%、2% 或绝对性能数字。兼容破坏必须有迁移工具、弃用窗口、公告、回滚和 RFC。

## 失败与回滚路径

基准失败先验证环境漂移、频率/温控、后台负载、样本和制品是否一致；不能通过重复运行挑选最好结果。确认代码回归后关联首个坏提交，关闭相关优化 Pass/Feature 或回滚制品，并保留失败报告。若优化提高吞吐却破坏正确性、内存、安全或尾延迟，正确性门禁优先，不能用综合分数抵消。
