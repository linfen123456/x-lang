---
doc_id: DOC-TESTING-STRATEGY
authority: evidence
owner: role/quality-team
backup_owner: role/compiler-team
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P1
last_reviewed: 2026-08-15
traceability_scope: [QUALITY, XLF, XLC, XLE]
---
# 测试策略与符合性套件

## 分层与最小覆盖

本文件描述未来测试工程，并不声称测试目录或运行结果已经存在。所有 `TEST-*` 在测试卡和可执行案例落地前均为 planned；只有实际运行记录可作为“已验证”证据。[符合性案例目录](./conformance-case-catalog.md)中的 `CASE-*` 只是人类可读别名，落地时必须映射到一个全仓唯一 canonical `TEST-*` 和规范 Rule/XLF；CI、追溯与发布证据只引用 canonical Test ID。

1. 解析器：Unicode、恢复、空输入、超长输入、注入样本和 fuzz；任何输入不得崩溃。
2. 语义：每条规则的 compile-pass/compile-fail、诊断稳定性、所有权/Effect/错误路径和属性测试。
3. IR/后端：每个 Pass 前后 verifier、差分执行、ABI/调试信息、目标矩阵和 determinism。
4. Runtime/库：并发模型、取消、超时、资源耗尽、故障注入、sanitizer、泄漏和升级兼容。
5. 工具/生态：CLI JSON、LSP/DAP、xpm 锁文件、文档示例、WASM/WPT、FFI 和签名制品 E2E。
6. 系统：Windows/Linux/macOS Tier 1；WASM、移动、裸机和 GPU 按能力探测与 Tier 门禁运行。

## 变形与故障矩阵

每个公共契约至少覆盖：空/最大/恶意输入、并发交错、取消/超时、磁盘满、权限撤销、时钟回拨、网络分区、版本 N-1/N/N+1 和损坏制品。生成语料必须记录 seed、缩减器和来源；测试数据不得含真实秘密或未脱敏个人数据。

## Flaky、隔离和质量预算

测试使用临时目录、随机端口、固定时钟和 seed；并行运行不能共享全局状态。单测 flaky 率目标 <0.1%，E2E <1%；连续两次失败自动隔离并在 2 个工作日内有 Owner。隔离项不能阻断回归修复，且不能被无限重试绕过。

## 关闭条件

只有当规则清单引用的每个测试均有实际运行记录、T1–T3 通过、T4 风险已接受、覆盖的负向路径完整、性能未越界、无未解释 flaky、回滚演练成功，状态才可从“已验证”进入“已稳定”。测试记录至少包含 Test ID、Rule ID、输入摘要、目标/Profile、预期、实际结果、环境、运行时间和证据路径；没有运行记录时维持 planned。
