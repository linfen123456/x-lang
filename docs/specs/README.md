---
doc_id: SPEC-INDEX
title: X-Lang 正式规范索引
status: draft
maturity: CORE
owner: language-architecture
sources: [XLF-01-001, XLF-01-006, XLC-CORE-001..020]
---

# X-Lang 正式规范索引

## 目标与非目标

本目录是语言可观察行为的唯一规范来源，负责把语言大纲转为可引用的规则、语法和符合性测试。实现细节、标准库 API 和平台适配分别归属编译器、`stdlib` 与平台文档；本目录不承诺未通过 RFC 的实验特性。

## 规范文件

| 文件 | 范围 | 阶段 |
|---|---|---|
| [语言核心](./language-core.md) | 词法、语法、类型、模块、错误、版本 | P0–P2 |
| [内存与并发](./memory-concurrency.md) | 所有权、RAII、借用、线程、异步和失败边界 | P0–P2 |
| `evaluation-and-ub.md` | 求值顺序、布局、未定义行为分类 | P1 |
| `macros-and-consteval.md` | 宏、受限编译期求值、资源预算 | P2 |
| [符合性](./conformance.md) | 规则 ID、实现状态、符合性等级和发布门禁 | P0 |

## 统一条文格式

每条规则使用 `XSP-<DOMAIN>-<NNN>`，必须写明：规范性措辞、实现状态、反例诊断、平台差异、兼容性影响和测试 ID。`CORE` 规则不得依赖 `ecosystem/`、`ai/` 或 `labs/`。

## 统一契约示例

```x
fn add(a: Int, b: Int) -> Result<Int, Error> { Ok(a + b) }
```

非法程序必须产生稳定诊断码，不得静默改变所有权、同步或异常语义。

## 边界、性能与安全

规范只规定可观察语义；优化可改变执行计划但不得改变结果、资源安全和数据竞争规则。编译期资源上限、诊断时间和运行时开销写入基准登记表，未测量值只能标记为目标。

## 测试与回滚

规则映射至 `tests/conformance` 的 pass/fail、诊断快照、布局探针和跨后端差分测试。规范变更通过 RFC/Edition；若回归失败，保留旧规则并以 feature gate 或迁移工具回滚，不删除历史条文。

## 追溯

来源：`XLF-*` 由[原始功能全量追溯矩阵](../X-Lang原始功能全量追溯矩阵.md)维护，`XLC-CORE-*` 由[多语言对标大纲](../X-Lang多语言对标与全栈能力补全大纲.md)维护；工程落点见项目目录架构中的 `specs/` 与 `tests/conformance/`。
