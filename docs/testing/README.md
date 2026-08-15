---
doc_id: DOC-TESTING-README
authority: evidence
owner: role/quality-team
backup_owner: role/security-team
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P0
last_reviewed: 2026-08-15
traceability_scope: [QUALITY, XLF, XLC, XLE, REVIEW]
---
# X-Lang 测试与质量证据

测试是追溯边的终点，不是发布后的补充。每个稳定规则至少有正向、负向、边界、兼容和回滚测试；测试工件包含提交、工具链、平台、输入哈希、随机种子、开始/结束时间和日志索引。

## 证据等级

| 等级 | 证据 | 用途 |
|---|---|---|
| T0 | Schema/静态检查 | 文档、配置、ID 和依赖方向 |
| T1 | 单元/属性/模糊测试 | 纯函数、解析器、状态机和错误边界 |
| T2 | 契约/组件测试 | 编译阶段、Runtime ABI、库和工具协议 |
| T3 | 跨平台/互操作/E2E | OS、WASM、FFI、IDE、制品和升级 |
| T4 | 故障/安全/性能/灾备演练 | 生产门禁和 LTS 证据 |

失败测试必须保留原始日志和复现命令。重试最多一次且必须标记 `flaky`；重试通过不等于门禁通过。
