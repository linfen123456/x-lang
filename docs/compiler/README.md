---
doc_id: DOC-COMPILER-README
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
# X-Lang 编译器工程专题

> 状态：草案｜成熟度：CORE（实验接口另行标记）｜Owner：Compiler Architecture Team
> 规范依据：语言规范大纲、编译器工程实施大纲
> 追溯字段：XLF-*、XLC-CORE-*、XLE-DEV-*

## 目标与边界

本专题定义 Source、Syntax、Semantic、HIR/MIR、Query、Codegen、Driver 之间可实施的契约。编译器前端不得依赖 LLVM、运行时、IDE 或生态项目；实验后端只能实现公开 Backend 接口。本文不定义用户语言规则，规则以 specs 和 RFC 为准。

## 专题文件树

    docs/compiler/
    ├─ README.md
    ├─ architecture.md
    ├─ frontend.md
    ├─ hir-mir.md
    ├─ optimizer.md
    ├─ codegen.md
    ├─ driver.md
    └─ interfaces/contract.md

## 公共契约摘要

详细字段见 interfaces/contract.md。所有工件携带 schema_version；未知主版本必须拒绝并给出可操作错误。接口错误统一为 X-E####，包含 code、severity、message、span、notes、fixes、origin 和 retryable。

## 完成定义

- 每个阶段都有输入输出不变量、验证器和 compile-pass/fail 语料。
- 取消、超时、内存/文件/递归深度上限可观察且不会留下半成品。
- -O0 与优化构建通过差分测试；LLVM 只存在于 codegen 适配层。
- 每个实现变更关联规范/RFC/ADR、测试、性能报告和 XLF/XLC/XLE 追溯。

## 负向测试与回滚

无效 UTF-8、超深嵌套、递归类型、重复定义、借用冲突、Trait 求解超限、未知目标、LLVM 错误、缓存损坏、取消竞态和磁盘满必须产生稳定诊断；禁止 panic、死锁或静默生成错误工件。契约变更使用 feature gate 和 schema 主版本，回归时关闭 gate 并保留最小复现包。
