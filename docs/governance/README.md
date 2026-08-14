---
doc_id: DOC-GOVERNANCE-README
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
# X-Lang 文档治理与证据规范

> 文档版本：1.0｜状态：已决策｜权威入口：[企业级完整文档体系总纲](../X-Lang企业级完整文档体系总纲.md)

本目录定义专题文档、需求追溯、项目注册、状态迁移和任务卡的统一机器可读约束。这里维护规则和 Schema，不复制 `XLF/XLC/XLE` 的完整明细。

## 专题文档最低完成定义

每个专题 README 或正式章节必须具备：目标、非目标、目标读者、术语、成熟度、状态、Owner、输入依赖、规范/接口内容、正反例、边界案例、测试映射、性能预算、安全边界、输出物、回滚方式、验收标准和来源 ID。

## 权威来源

- 原始来源与 `XLF-*`：`../X-Lang原始功能全量追溯矩阵.md`
- 87 项复审：`../X-Lang未纳入与偏离内容再审核及回归路线.md`
- `XLC-*`：`../X-Lang多语言对标与全栈能力补全大纲.md`
- `XLE-*`：`../X-Lang日常开发与AI协作风险补全大纲.md`
- 物理项目和目录：`../X-Lang完整项目目录架构与模块说明.md`

## 质量门禁

专题提交必须通过标题/Fence/链接检查、元数据字段检查、定义 ID 唯一性检查、追溯完整性检查和原始资料只读校验。正文可以重复引用 ID，但定义表只能有一个权威行。
