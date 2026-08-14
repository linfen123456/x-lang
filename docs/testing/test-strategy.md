---
doc_id: DOC-TESTING-TEST-STRATEGY
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
# 测试策略与符合性套件

## 1. 分层策略

| 层级 | 范围 | 必须证据 |
|---|---|---|
| 单元 | Lexer、Parser、类型、借用、IR Pass、运行时原语 | `TEST-*-unit-*`、覆盖分支和错误路径 |
| 契约 | 规范规则、公共 API、ABI、Schema、CLI 输出 | `TEST-*-contract-*`、版本化黄金样例 |
| 编译器端到端 | compile-pass/fail、run、诊断和跨后端差分 | 源码、期望结果、编译器版本、快照 |
| 集成 | std、包管理、LSP、调试器、网络和数据库适配 | 平台、依赖版本、清理和重试记录 |
| 故障与安全 | OOM、磁盘满、恶意输入、供应链和权限 | 威胁模型、注入命令、恢复结果 |
| 性能 | 编译、运行、内存、P95/P99、冷/热缓存 | 基准环境、样本、统计和阈值 |

## 2. 编译器符合性

每条稳定 `RULE-*` 至少有一个正例、负例、边界例和诊断断言。compile-fail 测试只断言稳定错误码、主 Span 和必要标签；非稳定文本使用快照版本标记。跨 LLVM/WASM/解释器后端执行差分测试，发现差异必须建 Issue 或 RFC。

## 3. Flaky 与数据管理

测试不得用无限重试掩盖失败。Flaky 必须登记 Owner、根因、隔离期限和修复版本；超过期限阻断发布。测试夹具禁止秘密和个人数据，随机测试记录种子，数据库/端口/时钟使用隔离租约。

## 4. 关闭条件

测试任务关闭需附 `source_ids/spec_ids/project_id/test_id`、命令、提交、平台、结果、失败分析、性能/安全影响和回滚验证。
