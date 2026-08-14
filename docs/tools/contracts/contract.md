---
doc_id: DOC-TOOLS-CONTRACTS-CONTRACT
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
# 工具链接口契约

> 状态：草案｜Owner：Tooling API Maintainer｜追溯：XLC-EXEC-*、XLC-FFI-*、XLE-DEV-*、XLE-AI-*

## CLI 与 XPM

命令 x check、build、run、test、fmt、doc、repl、clean 统一支持 format=text|json、offline、timeout。退出码：0 成功、1 用户错误、2 编译/测试失败、3 环境/依赖失败、4 取消、5 内部错误。JSON 含 schema_version、command、diagnostics、artifacts、duration_ms。

x.toml 和 x.lock 使用 canonical serialization；拒绝重复依赖、路径逃逸、未知主版本和未签名制品。解析、下载、校验、解包分别有超时、大小和并发上限；撤回或哈希不匹配不得静默使用缓存。

## LSP/DAP 与插件

LSP 请求携带文档版本和取消 token，不返回旧版本编辑；超时返回 partial + retryable。DAP 变量、栈、断点和异常映射带 source/line/column，能力缺失返回标准错误。插件/build.x 独立进程沙箱运行，默认只读、无网络、有限 CPU/内存/输出；权限提升需批准并审计。Agent 工具输出经过 schema、大小、来源和路径验证，写入只生成补丁提案。

## 负向测试、线程安全和回滚

CLI 进程级并发安全；缓存使用锁文件和原子替换。覆盖坏 schema、锁竞争、协议乱序、取消竞态、恶意路径、插件超时、日志注入和注册表 5xx。协议回归时按版本协商回退旧客户端/服务器，保留可迁移缓存与锁文件。
