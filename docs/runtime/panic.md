---
doc_id: DOC-RUNTIME-PANIC
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
# Panic 与失败路径
> 状态：草案｜Owner：Runtime Reliability Team｜追溯：XLF-*、XLC-CORE-*

定义 panic hook、unwind、abort、析构顺序、线程边界和 coredump。panic 期间再次失败进入受控 abort；负向测试验证错误链、资源释放和 FFI 隔离。
