---
doc_id: DOC-AI-THREAT-MODEL
authority: evidence
owner: role/security-team
backup_owner: role/ai-safety-team
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [SECURITY, AI, XLE, REVIEW]
---
# AI 与 Agent 威胁模型入口

## 资产与边界

资产包括源代码/规范、凭据和个人数据、构建/发布权限、制品签名、租约状态、测试结果、模型/Prompt/检索索引和审计日志。边界分为用户→编排器、编排器→模型、模型→工具、工具→工作区/网络、Agent→Agent、CI→发布系统六段；每段都必须有身份、授权、Schema、大小/时间预算和审计。

## 威胁与控制

| 威胁 | 例子 | 必须控制 | 证据 |
|---|---|---|---|
| Prompt Injection | Issue 指令 Agent 泄露 Token | 外部内容降权、检测/隔离、拒绝执行 | TEST-AI-INJECTION-001 |
| 越权/路径穿越 | 写入授权目录外或生产 | canonical path、deny-by-default、租约 | TEST-AI-AUTHZ-001 |
| 工具投毒 | 返回伪造 API/超大 JSON | 来源、Schema、大小、二次查询 | TEST-AI-TOOL-001 |
| 数据泄露 | Prompt 含密钥/PII | 脱敏、最小上下文、供应商策略、删除证明 | TEST-AI-PRIVACY-001 |
| 多 Agent 冲突 | Last-writer-wins 覆盖修复 | epoch 租约、base hash、仲裁 | TEST-AI-LEASE-001 |
| 供应链/生成代码 | 未知许可证/恶意补丁 | SBOM、签名、双审、可回滚 | TEST-AI-PROVENANCE-001 |

每次模型、工具、规则、依赖或权限边界变化重新评估；高风险路径先在影子环境演练。威胁模型不是安全批准，发布仍需 G5/G6。
