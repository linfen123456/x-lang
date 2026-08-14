---
doc_id: DOC-OPERATIONS-PLATFORM-MATRIX
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
# 平台支持与发布矩阵

| Tier | 平台 | 目标阶段 | 必须证据 |
|---|---|---|---|
| Tier 1 | Windows/Linux/macOS，x86_64/ARM64 | P0-P4 | 编译、运行、安装、升级、回滚、标准库和安全测试 |
| Tier 2 | WASM/WASI、Android、iOS | P3-P5 | 目标能力矩阵、真机/浏览器测试、限制说明 |
| Tier 3 | 嵌入式、eBPF、GPU、裸机 | P5-P6 | 独立 RFC、工具链、资源预算、威胁模型和退出条件 |

每个目标另记 OS 版本、SDK、链接器、最低支持版本、维护截止日期和责任人。未通过 CI 的目标状态为 `planned` 或 `unknown`，不得写成“全平台支持”。
