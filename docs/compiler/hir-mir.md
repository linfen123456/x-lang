---
doc_id: DOC-COMPILER-HIR-MIR
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
# HIR/MIR 实施
> 状态：草案｜Owner：Middle-End Team｜追溯：XLF-*、XLC-EXEC-*

AST 脱糖为 HIR，HIR 降为含 CFG、Place、Drop 和终结器的 MIR。每次变换执行输入/输出 verifier，序列化含 schema_version 和 source fingerprint。MIR interpreter 仅作参考语义，不得成为第二套语言规则。

验收：parse-print-parse、IR 往返、控制流不变量、Drop 顺序和差分执行通过；截断/未知版本工件安全拒绝。
