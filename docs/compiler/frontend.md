---
doc_id: DOC-COMPILER-FRONTEND
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
# 编译器前端实施
> 状态：草案｜Owner：Frontend Team｜追溯：XLF-*、XLC-CORE-*

Source Manager 处理 UTF-8、CRLF、虚拟文件和 Span；Lexer/Parser 必须恢复并生成稳定诊断；Resolve、Type、Trait、Borrow 分阶段产出 DefId、TypeId、约束和借用结果。每阶段有正反语料、fuzz、快照和 verifier。

负向验收：错误编码、深嵌套、重复定义、歧义 Trait、借用冲突不得崩溃；取消不提交查询缓存。
