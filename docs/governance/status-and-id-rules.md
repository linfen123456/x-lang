---
doc_id: DOC-GOVERNANCE-STATUS-AND-ID-RULES
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
# 状态、成熟度与 ID 规则

## 状态机

允许的正式迁移为：

```text
草案 → 待决策 → 已决策 → 原型验证中 → 已验证 → 已稳定
                         ├→ 研究
                         ├→ 归档
                         └→ 否决
```

每次迁移必须记录 RFC/ADR、责任人、日期、证据链接和影响的需求/项目/测试 ID。已稳定内容不得直接回退；必须通过新的 RFC 标记废弃、替代或兼容迁移。

## 成熟度与复审状态

`CORE`、`EXTENDED`、`EXPERIMENTAL`、`RESEARCH` 描述能力成熟度；`草案` 至 `已稳定` 描述文档/实现状态；`RETURN`、`CONDITIONAL`、`SPLIT`、`RESEARCH` 描述原始价值复审结果。三者互相正交，不能用一个字段替代另一个字段。

## ID 约束

| 类型 | 格式 | 唯一范围 |
|---|---|---|
| 规范规则 | `RULE-[域]-[3位]` | 全仓库 |
| 原始需求 | `XLF-[来源]-[3位]` | 追溯矩阵定义表 |
| 对标需求 | `XLC-[域]-[3位]` | 对标矩阵定义表 |
| 工程/AI 风险 | `XLE-[域]-[3位]` | 风险矩阵定义表 |
| 任务 | `TASK-[阶段]-[域]-[3位]` | 全仓库 |
| 项目 | `PROJ-[域]-[名称]` | 项目注册表 |
| 测试 | `TEST-[域]-[类型]-[3位]` | 测试注册表 |

ID 不得复用。替代关系使用 `supersedes`，废弃关系使用 `deprecated_by`；正文交叉引用不计入定义数量。
