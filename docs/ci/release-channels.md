---
doc_id: DOC-CI-RELEASE-CHANNELS
authority: evidence
owner: role/release-team
backup_owner: role/operations-team
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P3
last_reviewed: 2026-08-16
traceability_scope: [QUALITY, GOVERNANCE, XLF, XLC, XLE]
---
# 发布通道、制品、LTS 与 EOL

| 通道 | 允许内容 | 支持承诺 | 晋级条件 |
|---|---|---|---|
| Nightly | 主干、实验 Feature Gate | 无兼容承诺，保留诊断 | G0–G3 |
| Beta | 候选 API、Tier 2 探针 | 版本窗口内修复阻断缺陷 | G0–G5、迁移说明 |
| Stable | CORE/已稳定和明确 EXTENDED | 安全修复与关键回归 | G0–G6、签名/SBOM/回滚 |
| LTS | 有预算、有 Owner、有平台矩阵的 Stable 子集 | 固定支持窗口由 RFC 批准 | RFC 指定观察窗口的可靠性证据与灾备演练 |
| EOL | 到期或无维护 Owner | 只保留公告和迁移 | 删除下载入口前完成归档与撤回 |

LTS 不预设年限：RFC 必须给出窗口、补丁范围、SLA、平台、资金和 Bus Factor。EOL 公告期由同一支持 RFC 根据用户迁移成本和可维护资源批准，并提供最后安全版本、迁移工具、SBOM 和可验证归档；不得悄然删除制品或撤销签名。

制品必须包含 `artifact_digest、source_commit、toolchain_digest、target、ABI、license、SBOM、签名、traceability_ids`。`.xlib` 只表示该制品，不改变项目注册；Target/ABI 不匹配时回退源码构建。

## 晋级失败、撤回与回滚

- Nightly 缺少 G0-G3 证据时不发布该日制品；已有 Nightly 可继续保留但标记已知问题，不能自动晋级 Beta。
- Beta 任一目标平台出现数据损坏、安全、ABI、安装/升级或回滚失败时，候选整体停止晋级；不受影响的平台只能以新候选版本重新评审，不能沿用旧签名冒充通过。
- Stable 候选在 G6、Canary 或签名验证失败时作废，修复后生成新版本/新摘要；禁止覆盖已发布的同版本制品。
- 已发布 Stable 出现严重问题时先停止新分发、发布撤回/安全公告，再回退上一签名版本或前滚修复；注册表保留不可变历史和撤回原因。
- LTS 补丁若无法维持声明平台或兼容范围，必须暂停发布并启动支持范围 RFC；不得无公告缩小承诺。

每次晋级或撤回至少记录 source/artifact digest、canonical Test ID、平台结果、批准人、失败原因和恢复验证。尚无实际制品时这些流程保持 planned，不填写假版本、签名或运行记录。
