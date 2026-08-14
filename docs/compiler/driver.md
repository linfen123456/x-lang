---
doc_id: DOC-COMPILER-DRIVER
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
# 编译驱动实施
> 状态：草案｜Owner：Driver Team｜追溯：XLF-*、XLC-EXEC-*、XLE-DEV-*

Driver 编排 check/build/emit，管理 Session、Query、诊断、取消、缓存和 ArtifactManifest。输出原子提交；错误带 request id、retryable 和结构化 spans。缓存键包含源、规范、编译器、target、feature 和工具链 fingerprint。

验收：多文件项目、缓存命中/失效、并发取消、磁盘满和外部进程失败均可复现；回退冷编译不改变语义。
