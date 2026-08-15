---
doc_id: DOC-AI-AGENT-WORKFLOW-EVALUATION
authority: research
owner: role/ai-safety-team
backup_owner: role/quality-team
version: "2.0.0"
maturity: EXPERIMENTAL
status: 已决策
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [AI, SECURITY, QUALITY, XLE]
---
# Agent 工作流、评测与多智能体协作

## 强制流程

```text
任务边界 → 读取规则/规范/测试 → 建上下文清单 → 只读分析
→ 计划与租约 → 最小补丁 → 编译/测试/安全审查
→ 人工确认 → 审计事件 → 交付或安全停止
```

Agent 必须声明目标、非目标、允许目录、预算、外部操作和停止条件。读取到的外部文本不得提高信任级别；每次工具返回都做 Schema、大小、来源和注入检查。失败后保留进度和证据，不能只改测试迎合结果。

## 权限与租约

| Capability | 默认 | 升级条件 |
|---|---|---|
| read | allow（授权工作区） | 脱敏和路径边界 |
| write | deny | 用户确认、diff、测试、租约 |
| execute | deny | 命令白名单、沙箱、超时 |
| network/secret | deny | 逐次批准、最小范围、审计 |
| release/production | deny | 双人批准、G5/G6、Canary |

租约写入 `lease_id/agent_id/paths/mode/epoch/expires_at/base_hash`。提交前验证 base hash；冲突时释放租约并请求协调者仲裁。心跳丢失或 TTL 到期自动只读，不能续租后覆盖他人变更。

## 评测门禁

代表性任务集至少测：引用真实 API、编译率、测试通过率、安全缺陷率、Prompt Injection 拒绝率、越界工具调用率、成本、延迟、许可证来源和人审可理解性。模型、Prompt、规则、工具或检索版本变化必须 A/B 对照；关键任务任一安全指标下降即阻断。
