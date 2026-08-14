---
doc_id: DOC-RUNTIME-PAL
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
# 平台抽象层
> 状态：草案｜Owner：Platform Team｜追溯：XLF-*、XLC-PLATFORM-*

PAL 负责 OS 能力探测、权限、线程、时钟、文件和信号；调用方只能使用已探测能力。主机与交叉编译环境分离，能力矩阵和 sysroot 指纹进入制品。
