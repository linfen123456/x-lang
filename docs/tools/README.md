---
doc_id: DOC-TOOLS-README
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
# X-Lang 工具链工程专题

> 状态：草案｜成熟度：CORE（LSP/DAP/XPM 为 EXTENDED）｜Owner：Developer Experience Team
> 追溯字段：XLF-*、XLC-EXEC-*、XLC-FFI-*、XLE-DEV-*、XLE-AI-*

## 目标与目录

统一 CLI、XPM、格式化、文档、测试、LSP、DAP、调试、插件和 Agent 工具；工具只能消费版本化公共接口，不读取编译器私有结构。

    docs/tools/
    ├─ README.md
    ├─ cli.md
    ├─ package-manager.md
    ├─ lsp-dap.md
    ├─ formatter-doc.md
    ├─ test-runner.md
    ├─ plugin-sandbox.md
    └─ contracts/contract.md

## 完成定义与回滚

非 TTY 输出稳定；退出码和 JSON schema 版本化；离线构建、锁文件、签名和缓存可复现；LSP/DAP 支持取消和文档版本；插件默认无权限、超时可终止；测试失败保留最小复现和制品。未知命令、坏配置、锁冲突、网络中断、恶意 build、LSP 版本倒退和 DAP 断点失效必须稳定失败。协议回归时版本协商切回旧客户端/服务器。
