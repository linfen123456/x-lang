---
doc_id: DOC-SPECS-INDEX
title: X-Lang 正式语言规范索引
authority: normative
owner: role/language-council
backup_owner: role/compiler-team
version: "0.2"
maturity: CORE
status: 草案
phase: P0
last_reviewed: 2026-08-16
applies_to: [x-language, xc, x-lsp, conformance-suite]
traceability_scope: [XLF, XLC]
supersedes: [DOC-SPECS-INDEX-LEGACY]
---

# X-Lang 正式语言规范索引

本目录是 X-Lang 可观察语言行为的规范入口。本文档组是 `0.2` 候选规范初稿，不表示编译器已经实现或所有条文已冻结。规范性要求使用“必须/禁止”，实现建议使用“应当”，非规范说明使用“解释”。

## 规范范围与权威顺序

当资料冲突时，优先级为：已批准 RFC/ADR → 本目录已稳定条文 → 本目录草案条文 → 工程实现文档 → 原始材料。原始材料只用于追溯，不自动授予语义。实现不得以“编译器当前行为”替换规范结论。

| 文件 | 责任域 | 当前阶段 | 主要内容 |
|---|---|---|---|
| [language-core.md](./language-core.md) | 词法、EBNF、表达式、类型、Trait、模式、模块、Edition、错误 | P0–P2 | `RULE-LANG-*` |
| [types-traits-patterns.md](./types-traits-patterns.md) | 类型统一、约束求解、Trait 候选/一致性、方法解析和模式穷尽性算法 | P1–P2 | `RULE-TYPE-*`、`RULE-TRAIT-*`、`RULE-PAT-*` |
| [modules-packages-editions.md](./modules-packages-editions.md) | 模块发现、名称解析、可见性、清单、依赖、Feature 和 Edition | P1–P3 | `RULE-MOD-*`、`RULE-PKG-*`、`RULE-EDITION-*` |
| [memory-concurrency.md](./memory-concurrency.md) | 所有权、借用、生命周期、Drop、内存模型、线程、原子、async 取消 | P0–P3 | `RULE-MEM-*`、`RULE-CONC-*` |
| [evaluation-and-ub.md](./evaluation-and-ub.md) | 求值顺序、清理路径、整数/浮点、有效值、provenance 与 UB 分类 | P1–P2 | `RULE-EVAL-*`、`RULE-NUM-*`、`RULE-UB-*` |
| [conformance.md](./conformance.md) | 术语、实现等级、诊断、测试和发布门禁 | P0–P4 | `RULE-CONF-*` |

### 规划中的规范文件

`macros-and-consteval.md`（`RULE-META-*`）和 `abi-layout.md`（`RULE-ABI-*`）只应在对应 RFC 形成可评审草案后拆出；当前宏/consteval 与显式 ABI 边界仍由核心、互操作规范和待决 RFC 管理，不以空文件冒充完成。`evaluation-and-ub.md` 已形成 P1–P2 决策草案，但其中待决策略在 RFC 通过前不是稳定承诺。

## 统一规则记录格式

每一个规范规则必须使用全仓库唯一的 `RULE-域-NNN` ID，域由大写 ASCII 组成，例如 `RULE-LANG-001`、`RULE-MEM-001`。历史规则前缀不再作为规范 ID 使用。每条规则都必须包含以下字段：

1. **规范性条文**：能直接实现和判定的 MUST/ MUST NOT；
2. **解释**：条文意图和与相邻规则的关系；
3. **正例**与**反例**：反例必须给出预期诊断码；
4. **边界**：未指定、实现定义、平台能力或资源耗尽时的行为；
5. **诊断**：稳定诊断码和最小 span 要求；
6. **测试**：至少一个 `TEST-域-类型-NNN`，含 pass/fail/boundary 分类；
7. **追溯**：`XLF-*`、`XLC-*`（若有）和本规则关联的 RFC/ADR；
8. **待决 RFC**：已决策则写 `无（已决策依据：...）`，未决则写候选方案、决策门禁和最迟阶段。

规则状态和成熟度正交：`CORE` 不是“已实现”，`草案` 不是“可随意改变”。所有未决语义必须保留候选和退出条件，不得用示例暗示已批准结论。

## 诊断与测试命名

诊断码采用 `X-E####`（编译错误）、`X-W####`（警告）和 `X-R####`（运行时可报告错误）。诊断文本可本地化，代码、严重级别、主 span 和结构化参数必须稳定。测试 ID 采用 `TEST-[域]-[类型]-NNN`，定义在测试注册表或 conformance manifest 中；正文引用不算重复定义。

## 追溯与实现边界

正式条文必须能够沿以下链路反查：

```text
XLF/XLC → RULE → RFC/ADR → compiler/runtime/library module → TEST → phase/release
```

`XLF` 来源见 [原始功能全量追溯矩阵](../X-Lang原始功能全量追溯矩阵.md)，对标来源见 [多语言对标大纲](../X-Lang多语言对标与全栈能力补全大纲.md)。学习者应从[快速入门](../guide/getting-started.md)开始；教程只解释和练习本目录规则，不拥有独立语义权威。

## 最小符合性门槛

P0 实现必须能解析本文件中的稳定词法和最小语法，并对每条 CORE 规则提供 pass/fail/boundary 测试；P1 必须提供类型、模块、错误和 MIR/LLVM 端到端证据；P2 才能考虑 Trait、泛型和基础标准库稳定化；P3 之前不得将实验后端、GC、GPU、热重载或自动插锁列为默认语义。
