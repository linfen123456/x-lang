---
doc_id: DOC-TOOLS-README
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-02-005, XLF-02-007, XLF-02-013, XLF-02-014, XLF-02-015, XLF-03-005, XLF-10-012, XLF-11-001, XLF-11-003, XLF-11-004, XLF-11-013]
---
# X-Lang 工具链工程实施规范

> 状态：草案｜Owner：`role/tooling-team`｜成熟度：CORE（LSP/DAP/XPM 为 EXTENDED）

## 目标和边界

工具链为编译器和运行时提供可脚本化、可复现且安全的 `x` CLI、x.toml/x.lock、依赖求解、LSP/DAP、fmt/doc/test/repl、缓存和插件沙箱。工具只能消费版本化 Driver、ArtifactManifest、诊断和 ABI；不能读取编译器私有结构、覆盖用户未授权修改或在无审批下执行网络/生产操作。

## 统一进程契约

每个命令输入 `CommandRequest{schema_version:"1.0",command:String,args:Vec<String>,cwd:PathBuf,env:DeclaredEnv,format:Text|Json,offline:bool,timeout_ms:u64,cancel:CancelToken}`，输出统一 `CommandResult{schema_version:"1.0",command,request_id:String,status:success|user_error|build_failed|environment_failed|cancelled|internal_error,exit_code:u8,diagnostics:Vec<Diagnostic>,artifacts:Vec<ArtifactRef>,duration_ms:u64,resource}`。`request_id` 是 16-byte u128 的 32-hex 文本；该结构与 compiler/runtime-facing tool adapters 相同。未知参数、坏配置、越权路径、超时、取消和内部错误都必须可区分。

退出码固定为：`0` 成功；`1` 参数/用户输入错误；`2` 编译、测试或文档示例失败；`3` 环境、依赖、网络或签名失败；`4` 用户取消/超时；`5` 工具内部错误。JSON 字段只追加，消息可本地化但 `code`、`status`、`exit_code` 稳定。非 TTY 禁止彩色控制符，stdout 只输出结果，诊断/进度使用 stderr（JSON 模式除外）。

## 安全、Profile 与完成定义

`offline` 禁止网络；`ci` 固定工具链/locale/时区和随机种子；`repro` 禁止隐式环境；`interactive` 可询问但 stdin EOF 必须安全失败。工具使用共享 `ProfileSpec`，优先级为 `CLI > x.toml profile > TargetSpec defaults > toolchain defaults`。默认单输入 64 MiB、命令 10 min、输出 1 GiB、并发 32、插件 CPU 30 s/内存 256 MiB；Profile 只能收紧，放宽需要审计。所有命令支持 cancel，外部进程用进程组清理。

完成定义：命令 help、text/json、非 TTY、坏配置、网络中断、锁冲突、取消和权限测试；x.lock 可重现；LSP/DAP 版本协商；fmt 幂等；doc/test/repl 有可执行样例；插件越权被终止；失败保留最小复现和制品。回滚通过旧 CLI/schema/lockfile、禁用实验 plugin gate 和离线缓存完成。

## 文档索引

- [逐命令 CLI 与退出码](./cli.md)
- [x.toml、x.lock 与依赖求解](./package-manager.md)
- [fmt/doc/repl](./formatter-doc.md)
- [test runner](./test-runner.md)
- [LSP/DAP](./lsp-dap.md)
- [插件沙箱](./plugin-sandbox.md)
- [统一协议结构](./contracts/contract.md)
- [CLI 执行流水线、XPM 求解与 LSP/DAP 细则](./xpm-lsp-cli-details.md)
