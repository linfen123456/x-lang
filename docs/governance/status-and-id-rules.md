---
doc_id: DOC-GOVERNANCE-STATUS-AND-ID-RULES
authority: normative
owner: role/architecture
backup_owner: role/documentation
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P0
last_reviewed: 2026-08-15
traceability_scope: [GOVERNANCE, XLF, XLC, XLE, REVIEW]
---
# 状态、成熟度、阶段与 ID 规则

## 正交字段

`authority` 说明谁能解释事实，`status` 说明当前证据状态，`maturity` 说明承诺强度，`phase` 说明实施顺序。它们不互相推导：`RESEARCH/研究/P6` 不是失败，`CORE/已稳定/P2` 也不代表在所有平台可用。

| 字段 | 允许值 | 机器检查 |
|---|---|---|
| authority | master / normative / implementation / evidence / research | Schema enum |
| maturity | CORE / EXTENDED / EXPERIMENTAL / RESEARCH | Schema enum |
| status | 草案、待决策、已决策、原型验证中、已验证、已稳定、研究、归档、否决 | Schema enum |
| phase | P0–P6 | Schema enum |

## 状态迁移

```text
草案 → 待决策 → 已决策 → 原型验证中 → 已验证 → 已稳定
  └──────────────────────────────→ 研究 → 归档
  └──────────────────────────────→ 否决
```

每次迁移都需要 `RFC/ADR、owner、日期、影响 ID、测试结果、证据链接`。`已稳定` 只能由已验证的规则、实现、兼容、性能、安全和回滚证据共同触发；回退必须新建 RFC，不能覆盖历史。

## ID 约束

| 类型 | 格式 | 定义位置 |
|---|---|---|
| 文档 | `DOC-[A-Z0-9-]+` | Markdown front matter |
| 规则 | `RULE-[DOMAIN]-[0-9]{3}` | 规范正文/Schema |
| 原始功能 | `XLF-[来源]-[0-9]{3}` | XLF 权威矩阵 |
| 对标缺口 | `XLC-[DOMAIN]-[0-9]{3}` | XLC 权威矩阵 |
| 工程风险 | `XLE-[DOMAIN]-[0-9]{3}` | XLE 权威矩阵 |
| 复审边 | `REVIEW-[0-9]{3}` | [未纳入与偏离内容再审核及回归路线](../X-Lang未纳入与偏离内容再审核及回归路线.md) |
| 项目 | `PROJ-[DOMAIN]-[NAME]` | 项目注册表 |
| 测试 | `TEST-[DOMAIN]-[TYPE]-[0-9]{3}` | 测试注册/追溯数据 |

定义 ID 不复用；正文引用不增加计数。`xdoc-test` 是 `PROJ-TOOLS-XDOC` 的别名，`.xlib` 是 `PROJ-ARTIFACT-XLIB` 的制品别名，二者不创建第二个项目。
