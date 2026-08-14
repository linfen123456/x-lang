---
doc_id: DOC-TESTING-PERFORMANCE-AND-COMPATIBILITY
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
# 性能、兼容性与可复现测试

## 基准规则

性能数字只能作为目标或实测结果。报告必须记录 CPU/内存/OS、编译器版本、优化参数、输入规模、预热、样本数、统计方法、P50/P95/P99 和比较基线。默认退化阈值由发布 RFC 指定；超过阈值自动阻断或要求性能 Owner 签署例外。

## 兼容性矩阵

- 语言：Edition、诊断、ABI、包清单和锁文件。
- 平台：Windows/Linux/macOS × x86_64/ARM64；WASM、移动和实验目标单独标注。
- 数据：N-1/N/N+1 Schema、数据库滚动升级、序列化和未知字段。
- 制品：可复现构建、签名、SBOM、安装/升级/回滚。

每次发布保存矩阵快照。未执行的组合为 `unknown`，不得默认为通过。
