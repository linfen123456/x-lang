---
doc_id: DOC-TOOLS-LSP-DAP
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.1"
maturity: EXTENDED
status: 草案
phase: P3
last_reviewed: 2026-08-16
traceability_scope: [XLF-02-004, XLF-02-005, XLF-02-007, XLF-02-008, XLF-02-015, XLF-11-006, XLF-11-007]
---
# LSP 与 DAP 实施规范

> 状态：草案｜Owner：`role/tooling-team`

## LSP

每个请求包含 `jsonrpc:"2.0"`、`id:String|u64`、`method:String`、`params`、`document_version:i64?`、`cancel_id:String?`；server context 为 `WorkspaceSnapshotId`。`initialize` 协商 `protocol_version`、`capabilities`、`position_encoding`；不支持能力返回标准 `MethodNotFound/InvalidParams`，不猜测客户端版本。

打开/变更文档使用 `uri:String`、`version:i64`、`text:String|content_changes`，版本回退或旧 snapshot 请求返回 `X-LSP-STALE-DOCUMENT`。同一 `didChange` 的 `contentChanges` 按数组顺序应用，每个 range 相对前一 change 后的临时文本；在私有 rope 上全部验证成功后才发布新 version，任一步失败回滚整批。completion/hover/definition/diagnostics/formatting 结果带 snapshot version 和 source span；超过 deadline 可返回 partial + `retryable:true`。取消必须传播到 Compiler Query；取消后不得发布旧版本编辑。

单文档 16 MiB、workspace 64 MiB、并发请求 32、诊断 10k、补全项 5k、请求 2 s 只是 `candidate_default`，遵循 [工具链 Budget 治理](./README.md#安全profile-与完成定义)，不是响应时间或工作区容量承诺；`ci`/低内存 Profile 可收紧。LSP server 线程安全，长查询不阻塞消息循环，workspace snapshot 只读。

## DAP

`initialize` 协商 `supportsRunInTerminalRequest`、`supportsExceptionInfoRequest`、`linesStartAt1`；`launch/attach` 参数为 `program:PathBuf`、`args:Vec<String>`、`cwd:PathBuf`、`env:Map<String,String>`、`target:TargetSpecId`、`stopOnEntry:bool`、`timeout_ms:u64`。路径、env、target 经过 workspace/权限校验。

stack frame 字段为 `id:u64`、`name:String`、`source:{path,sourceReference}`、`line:u32`、`column:u32`；variable 为 `variablesReference:u64`、`name`、`value`、`type`。SourceMap 缺失返回 `X-DAP-NO-SOURCE-MAP`，断点未绑定要报告 verified=false/reason。调试器不得通过 eval 改写不可变变量或越过 sandbox。

## 负向测试与回滚

覆盖乱序请求、旧文档编辑、取消竞态、超时、超大诊断、恶意 URI、DAP 断点越界、进程退出、权限拒绝和协议降级。`TEST-TOOLS-LSP-001` 做版本一致性，`TEST-TOOLS-DAP-001` 做 source map/断点黄金。协议主版本使用 capability/namespace 协商；回归时切回旧 server/client adapter，禁用新分析能力但保留源码和诊断。
