> 已归档：见 v2 [README.md](../../../../README.md)

# 实现设计文档索引

本目录保存**实现级设计**：把已批准或候选 RFC/ADR 落到可编码的模块边界、数据流、接口与验收。它们不是语言可观察语义的权威来源，也不能覆盖 `Proposed`/`Accepted` RFC。

## 放置规则

| 内容 | 放这里？ | 权威落点 |
|---|---|---|
| 语言可观察规则 | 否 | 根 `rfcs/` → 接受后 `specs/` |
| 为何选某架构 | 否（摘要可链） | `docs/decisions/` ADR |
| 如何编码、模块接口、阶段切片、符合性 runner | 是 | 本目录 |
| 大纲级范围/路线 | 否 | 现有 `X-Lang*.md` 大纲 |

冲突裁决：已批准 RFC/ADR > 总纲 > 语言大纲 > 工程大纲 > **本目录设计** > Backlog。

## 当前设计

| 文档 | 关闭的审查缺口 | 状态 |
|---|---|---|
| [缺口分析与设计目标](00-gap-analysis-and-design-targets.md) | 审查问题清单 → 设计交付映射 | Proposed |
| [P0 纵向切片实现设计](p0-vertical-slice.md) | 无可运行子集、GAP-COMP-02、P0-T04～T06 | Proposed |
| [语义管线实现设计](semantic-pipeline.md) | RFC-0006/0007/0008 过薄、GAP-LANG-03～05 | Proposed |
| [符合性与门禁实现设计](conformance-and-gates.md) | 无证据链、P0 检查点不可执行 | Proposed |
| [XUI 与多平台适配](xui-and-platforms.md) | UI IR、能力差异和各宿主晋级 | Proposed |
| [AI 应用、协作与学习](ai-development-and-learning.md) | SDK、信任边界、学习及训练隔离 | Proposed |
| [阶段证据与平台门禁](evidence-and-platform-gates.md) | 黄金项目、对照基线和逐目标晋级 | Proposed |

配套 ADR：

- [ADR-0003](../decisions/ADR-0003-p0-language-profile-and-labs-freeze.md)：Proposed 剖面冻结、`defer` 候选裁决与 Labs 隔离；接受前不能额外约束已批准语义
- [ADR-0004](../decisions/ADR-0004-rust-llvm-host-baseline.md)：Proposed 宿主编译器与 LLVM 基线；接受后才能锁定工具链

## 成熟度

设计文档状态：`Draft → Proposed → Accepted → Superseded`。`Accepted` 表示实现 Owner 与工程评审同意按此编码；**不等于**语言 RFC 已 Accepted，也不等于代码已存在。
