---
doc_id: DOC-AI-AGENT-WORKFLOW-AND-EVALUATION
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
# Agent 工作流、评测与多智能体协作

## 强制流程

任务边界与非目标→加载最小规则/源码/测试上下文→计划与授权→增量修改→静态/单元/安全/性能验证→人工审查→写入审计事件。外部网页、Issue、工具输出和生成文件均按数据处理，需 Schema 校验和二次验证。

## 评测

模型或 Prompt 变更前后运行固定任务集，记录编译率、测试通过率、正确性、人评安全缺陷、引用/许可证合规和成本。失败样本进入回归集；不能只用“看起来合理”通过。

## 多智能体

文件/模块使用带 TTL 的租约；同一文件冲突必须暂停并由协调者裁决，不允许静默 last-writer-wins。每次交接附上下文摘要、已改文件、未完成任务、测试结果、风险和审计事件 ID。超出 Token、时间、网络或工具调用预算时安全停止并保留进度。
