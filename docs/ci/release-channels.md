---
doc_id: DOC-CI-RELEASE-CHANNELS
authority: evidence
owner: role/release-team
backup_owner: role/operations-team
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [QUALITY, GOVERNANCE, XLF, XLC, XLE]
---
# 发布通道、制品、LTS 与 EOL

| 通道 | 允许内容 | 支持承诺 | 晋级条件 |
|---|---|---|---|
| Nightly | 主干、实验 Feature Gate | 无兼容承诺，保留诊断 | G0–G3 |
| Beta | 候选 API、Tier 2 探针 | 版本窗口内修复阻断缺陷 | G0–G5、迁移说明 |
| Stable | CORE/已稳定和明确 EXTENDED | 安全修复与关键回归 | G0–G6、签名/SBOM/回滚 |
| LTS | 有预算、有 Owner、有平台矩阵的 Stable 子集 | 固定支持窗口由 RFC 批准 | 两次发布周期可靠性与灾备演练 |
| EOL | 到期或无维护 Owner | 只保留公告和迁移 | 删除下载入口前完成归档与撤回 |

LTS 不预设年限：RFC 必须给出窗口、补丁范围、SLA、平台、资金和 Bus Factor。EOL 前至少提前两个稳定周期公告，提供最后安全版本、迁移工具、SBOM 和可验证归档；不得悄然删除制品或撤销签名。

制品必须包含 `artifact_digest、source_commit、toolchain_digest、target、ABI、license、SBOM、签名、traceability_ids`。`.xlib` 只表示该制品，不改变项目注册；Target/ABI 不匹配时回退源码构建。
