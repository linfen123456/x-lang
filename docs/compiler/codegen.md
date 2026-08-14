---
doc_id: DOC-COMPILER-CODEGEN
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
# 代码生成与后端实施
> 状态：草案｜Owner：Backend Team｜追溯：XLF-*、XLC-PLATFORM-*

TargetSpec 描述 triple、布局、ABI、sysroot 和能力；Codegen API 隔离 LLVM；Linker 负责对象、符号、调试信息和失败清理。Tier 1 为 Windows/Linux/macOS x86_64/ARM64，WASM/GPU/eBPF 为独立扩展。

验收：IR verify、ABI/汇编/链接/调试信息、跨平台运行和签名工件通过；未知目标不误用主机配置。
