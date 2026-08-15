---
doc_id: DOC-CI-PIPELINE-GATES
authority: evidence
owner: role/release-team
backup_owner: role/security-team
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P0
last_reviewed: 2026-08-15
traceability_scope: [QUALITY, GOVERNANCE, SECURITY, XLF, XLC, XLE]
---
# CI 流水线与 G0-G6 硬门禁

## 门禁定义

| 门禁 | 触发与硬条件 | 失败处置 |
|---|---|---|
| G0 事实完整性 | 专题 front matter；8 份主大纲可读元数据块；H1/层级/Fence/链接；原始 12 文件 Git 差异为空；ID 唯一和 164/94/60/87 计数 | 阻断；不得人工改结果 |
| G1 设计与契约 | RFC/ADR、非目标、Schema、威胁模型、项目/Owner、迁移/回滚 | 阻断设计合并 |
| G2 构建与静态 | 锁定工具链、依赖/许可证/SBOM、格式、lint、编译和依赖方向 | 阻断制品 |
| G3 语义质量 | T1/T2、compile-pass/fail、属性/fuzz、sanitizer、flaky 预算 | 阻断晋级 |
| G4 集成与平台 | Tier 1 OS、FFI/WASM/工具 E2E、N-1/N/N+1 兼容、性能阈值 | 只可保留在实验通道 |
| G5 安全与运维 | SAST/SCA、威胁模型、权限、Prompt Injection、签名、SLO、回滚/灾备演练 | 阻断发布 |
| G6 发布批准 | 变更清单、追溯闭合、人工双签、Canary 指标、公告、撤回方案 | 不得进入 stable/LTS |

## 执行顺序

```text
G0 → G1 → G2 → G3 → G4 → G5 → G6 → canary → stable
                         ↘ research（隔离，不绕过 G0/G1/G5）
```

每个 job 输出 `run_id、commit、environment_digest、input_hash、test_ids、result、artifact_digest`。缓存命中也要记录来源和校验；缓存污染、签名不匹配、未知 Schema 主版本一律失败。

## 变更例外

只有安全修复或灾难恢复允许临时缩小范围，并需值班负责人和安全负责人双签，限定到一个发布窗口；事后 24 小时内补跑缺失门禁和复盘。实验能力不能以“内部”名义绕过权限、审计、资源和回滚。
