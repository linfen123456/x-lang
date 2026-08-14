---
doc_id: DOC-CI-PIPELINE-AND-GATES
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
# CI 流水线与 G0-G6 门禁

| 门禁 | 必检内容 | 失败处理 |
|---|---|---|
| G0 文档与追溯 | docs-lint、ID、链接、原始文件只读 | 阻断合并 |
| G1 快速正确性 | fmt、lint、单元、compile-pass/fail | 阻断合并 |
| G2 编译器/运行时 | E2E、IR 验证、Sanitizer、标准库契约 | 阻断阶段晋级 |
| G3 安全/供应链 | Fuzz、依赖/CVE/许可证、SBOM、秘密扫描 | 阻断发布 |
| G4 平台/兼容 | Tier 1 构建、测试、ABI、升级/回滚 | 未执行标 unknown |
| G5 性能/可靠性 | 基准、资源、故障注入、Flaky 趋势 | 超阈值需批准 |
| G6 发布/运维 | 签名、来源证明、Canary、监控、Runbook、灾备演练 | 禁止 Stable/LTS |

每个门禁输出 `gate-report.json`：`build_id`、`commit`、`toolchain`、`checks`、`owner`、`status`、`evidence`、`exceptions`、`expires_at`。例外必须有 RFC/ADR、补偿测试、期限和批准人，过期自动失败。

## 流水线阶段

PR 执行 G0-G2 快速集；Nightly 执行全平台、Fuzz 和性能；Beta 执行 G3-G5；Stable/LTS 执行全部门禁及安装、升级、回滚和灾备演练。制品使用内容寻址、签名和不可变保留策略。
