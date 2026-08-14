---
doc_id: DOC-TESTING-README
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
# X-Lang 测试与质量证据

> 版本：1.0｜状态：已决策｜Owner：role/qa-team

本目录定义编译器、运行时、标准库、工具链和生态的测试分层、证据格式及发布质量门禁。测试是 `XLF/XLC/XLE → 规范/RFC → 项目 → 测试 → 发布` 追溯链中的权威证据，不以覆盖率单一数字替代正确性。

## 质量门禁

- `docs-lint`：标题、围栏、链接、元数据和术语检查。
- `trace-lint`：定义 ID 唯一、必需边完整、项目/测试存在。
- `x test conformance`：compile-pass、compile-fail、run 和诊断快照。
- `x test fuzz`：词法、解析、类型、IR、包清单和不可信输入。
- `x bench verify`：编译时间、运行时间、内存和尾延迟回归。
- `x test platform`：Tier 1 平台矩阵；未运行的平台不得标绿。

所有门禁必须保存命令、工具版本、提交 SHA、环境指纹、日志和制品路径。
