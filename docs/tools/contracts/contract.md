---
doc_id: DOC-TOOLS-CONTRACTS-CONTRACT
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-02-005, XLF-02-013, XLF-02-014, XLF-02-015, XLF-03-007, XLF-10-012, XLF-11-001, XLF-11-013]
---
# 工具链公共接口契约

> 状态：草案｜Owner：`role/tooling-team`

| 接口 | 字段类型 | 前置/后置 | 错误/取消 | 并发/资源 |
|---|---|---|---|---|
| `Command.run` | `CommandRequest{schema_version:"1.0",command,args,cwd,format,profile,timeout,cancel}` | 路径/profile 合法；返回统一 `CommandResult` | exit 1/2/3/4/5 | 子进程 64、输出 1 GiB |
| `Xpm.resolve` | `Manifest,Lock?,RegistrySnapshot,Target` | canonical manifest；唯一 Resolution | config/conflict/signature/offline | 包 512 MiB，下载 10 并发 |
| `Formatter.format` | `Files,FmtConfig,check,cancel` | parse；parse-print-parse | syntax/permission/cancel | 文件 16 MiB |
| `TestRunner.run` | `TestPlan,seed,isolation,cancel` | 清单/target 合法；TestReport | failed/timeout/cancel | jobs/Profile；不无限 retry |
| `Lsp.request` | `JsonRpc{version,method,params,doc_version,cancel}` | capability/version 合法 | standard JSON-RPC + retryable | 请求 2 s；并发 32 |
| `Dap.request` | `JsonRpc{method,program,target,env}` | source map/权限合法 | verified=false 或标准错误 | 进程/变量有上限 |
| `Plugin.start` | `PluginManifest,inputs,outputs,limits,cancel` | 签名/审批/沙箱通过 | timeout/quota/crash/cancel | CPU 30 s、内存 256 MiB |

## JSON 结构和安全规则

统一结果：`{schema_version:"1.0",command:String,request_id:String,status:success|user_error|build_failed|environment_failed|cancelled|internal_error,exit_code:u8,diagnostics:[Diagnostic],artifacts:[ArtifactRef],duration_ms:u64,resource:{peak_memory_bytes:u64,network_bytes:u64,children:u16}}`。`request_id` 使用 16-byte u128 的 canonical 32-hex 表示。字段只追加；未知主版本拒绝。路径使用 workspace-relative canonical form；所有外部文本按数据处理，经过大小/schema/来源校验，禁止注入命令、配置或 Agent 指令。

## 提交、缓存、取消和回滚

文件、锁、report 和 plugin output 均采用 temp→validate→atomic replace；取消/失败不写最终文件。缓存 key 必须含工具/compiler/target/profile/schema fingerprint；坏缓存隔离。协议版本通过 capability 协商，破坏性变更保留 adapter 一个稳定周期；回滚使用上一 CLI/lock/schema、冷编译或源码构建，不能依赖无法验证的旧缓存。

## 负向证据

`TEST-TOOLS-CONTRACT-001` 覆盖未知 schema/字段、`TEST-TOOLS-CONTRACT-002` 覆盖恶意路径和日志注入、`TEST-TOOLS-CONTRACT-003` 覆盖锁竞争/并发取消、`TEST-TOOLS-CONTRACT-004` 覆盖 plugin 超时/网络越权、`TEST-TOOLS-CONTRACT-005` 覆盖 LSP/DAP 乱序和旧文档。每个测试保存请求、版本、Profile、退出码和最小 artifact。
