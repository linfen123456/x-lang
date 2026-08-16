---
doc_id: DOC-CI-PIPELINE-GATES
authority: evidence
owner: role/release-team
backup_owner: role/security-team
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P0
last_reviewed: 2026-08-16
traceability_scope: [QUALITY, GOVERNANCE, SECURITY, XLF, XLC, XLE]
---
# CI 流水线与 G0-G6 硬门禁

## 门禁定义

| 门禁 | 触发与硬条件 | 失败处置 |
|---|---|---|
| G0 事实完整性 | 专题 front matter 或等价可读元数据块；8 份主大纲元数据；H1/层级/Fence/链接；原始 12 文件 Git 差异为空；ID 唯一和 164/94/60/87 计数 | 阻断；不得为通过检查改写原始资料或伪造 ID |
| G1 设计与契约 | RFC/ADR、非目标、接口/数据契约、威胁模型、项目/Owner、迁移/回滚；无需为每项契约新增机器 Schema | 阻断设计合并 |
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

每个 job 输出 `run_id、commit、environment_digest、input_hash、canonical_test_ids、result、artifact_digest`。目录中的 `CASE-*` 不能代替 canonical `TEST-*`。缓存命中也要记录来源和校验；缓存污染、签名不匹配、未知接口/数据格式主版本一律失败。当前仅文档阶段没有真实 CI run 时，状态保持 planned，不能手工填写 run ID。

## 变更例外

只有安全修复或灾难恢复允许临时缩小范围，并需值班负责人和安全负责人双签，限定到一个发布窗口；补跑期限由事件级别和发布 RFC 明确，不能在尚无值班制度时伪造固定 SLA。实验能力不能以“内部”名义绕过权限、审计、资源和回滚，也不能因失败阻断与其无依赖关系的 CORE；失败时关闭 Feature Gate、隔离制品并保留研究证据。
