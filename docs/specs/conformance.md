---
doc_id: SPEC-CONFORMANCE
title: X-Lang 符合性与实现状态规范
status: draft
maturity: CORE
owner: language-architecture
trace: [XLF-01-001, XLF-01-002, XLF-11-001, XLF-12-020, XLC-CORE-018..020]
---

# X-Lang 符合性与实现状态规范

## 目标与非目标

定义规则状态、实现等级和发布门禁，避免“实现了一个原型”被误写成稳定语言保证。本文件不替代具体语义规范，也不授予实验后端 CORE 资格。

## 实现等级

| 等级 | 要求 |
|---|---|
| Core | 规范已决策；至少一个参考实现；pass/fail/diagnostic 测试；跨平台差分无已知高危缺陷 |
| Extended | Core 不变；有 feature gate、降级方案和平台矩阵 |
| Experimental | RFC、原型、资源预算、基准、安全审计和退出条件 |
| Research | 独立 Labs，不进入稳定依赖图 |

## 规范条文

`XSP-CONF-001`：实现不得宣称高于其测试和审计证据的等级。`XSP-CONF-002`：每条稳定规则必须有唯一 Rule-ID、变更记录和至少一个正例、反例、边界例。`XSP-CONF-003`：发布门禁必须生成 `规则→实现→测试→版本` 报告，缺失映射即阻止 Stable 发布。

## 正反例

正例：某规则在 LLVM、MIR 解释器和三平台 CI 均通过，发布报告标记 Core。反例：只在 Windows Debug 原型通过却宣称跨平台稳定，属于门禁违规。

## 边界、性能与安全

实现定义行为必须写入平台矩阵；未定义行为不得被测试样例依赖。性能数字必须含硬件、OS、编译器、数据集、P50/P95/P99 和复现命令。安全高危缺陷、供应链未签名制品和不可回滚迁移均阻止升级。

## 测试与回滚

`tests/conformance`、`tests/diagnostics`、`tests/reproducibility` 和发布流水线共同验证等级。门禁失败时回退到上一稳定版本或降低成熟度标签，保留失败证据和 RFC，不删除规则历史。
