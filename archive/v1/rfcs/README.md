> 已归档：见 v2 [README.md](../../../README.md)

# X-Lang RFC 索引

本目录保存尚待评审或已经完成决策的 X-Lang 变更提案。RFC 用于冻结问题、候选规则、替代方案和验收证据；`Proposed` RFC 不是正式语言规范，也不能覆盖已批准规范。

## 状态机

```text
Draft → Proposed → Accepted → Implemented → Stable
                   ↘ Rejected
Accepted/Implemented/Stable → Superseded
```

- `Draft`：内容不完整，不进入正式评审。
- `Proposed`：规则完整，可进行语言、实现、安全和生态评审。
- `Accepted`：决策已批准，但不代表实现或证据完成。
- `Implemented`：参考实现和要求的自动化语料已经存在。
- `Stable`：满足发布门禁并进入兼容承诺。
- `Rejected`：保留提案及否决原因。
- `Superseded`：由新 RFC 取代，旧记录不得删除。

## 当前提案

| RFC | 状态 | 主题 | 正式产物 |
|---|---|---|---|
| [RFC-0001](0001-module-import-name-resolution.md) | Proposed | 模块、导入、名称解析、方法查找与可见性 | `specs/language/modules.md` |
| [RFC-0002](0002-pattern-destructuring.md) | Proposed | 模式解构、字段简写和剩余字段 | `specs/language/patterns.md` |
| [RFC-0003](0003-package-manifest-resolution-lockfile.md) | Proposed | 包身份、Manifest、解析、Feature 与 Lockfile | `specs/packages/` |
| [RFC-0004](0004-build-artifact-and-foreign-dependencies.md) | Proposed | 构建图、源码/制品缓存、Git 与外部生态依赖 | `specs/build/` |
| [RFC-0005](0005-core-lexical-and-surface-grammar.md) | Proposed | 核心词法、31 个关键字与唯一表层语法 | `specs/language/lexical.md`、`grammar.ebnf` |
| [RFC-0006](0006-type-value-place-and-evaluation.md) | Proposed | 类型、Value/Place/Temporary 与确定求值 | `specs/language/types-and-evaluation.md` |
| [RFC-0007](0007-ownership-borrow-move-and-drop.md) | Proposed | 所有权、借用、移动、初始化与 Drop | `specs/language/ownership-and-drop.md` |
| [RFC-0008](0008-result-panic-termination-and-cleanup.md) | Proposed | Result、panic、终止类别与清理 | `specs/language/errors-and-termination.md` |
| [RFC-0009](0009-owned-text-bytes-and-collections.md) | Proposed | 拥有型文本/字节与 HashMap/BTreeMap/OrderedMap | `specs/library/text-bytes-and-collections.md` |
| [RFC-0010](0010-json-data-model-codec-and-canonical-output.md) | Proposed | JSON 模型、三类 Codec、资源上限与 Canonical Output | `specs/library/json.md` |
| [RFC-0011](0011-xui-typed-declarative-and-platform-capabilities.md) | Proposed | P3+ XUI 类型化声明、UI IR 与宿主能力契约；不扩核心语法 | 独立 x-ui 生态接口规范（接受后） |

## 接受门禁

RFC 至少满足以下条件才能转为 `Accepted`：

1. 目标、非目标、术语、规则和失败行为完整；
2. 与现有候选语法、工程阶段和依赖方向没有未解释冲突；
3. 至少一名语言/架构审查者和一名实现/测试审查者通过；
4. 每个未决问题有 Owner、截止阶段和失败回退；
5. 定义可执行的正例、反例、诊断和兼容性验收；
6. 安全、性能、供应链和跨平台影响已评估；
7. 接受后由单一来源生成正式规范，不复制 RFC 全文。
