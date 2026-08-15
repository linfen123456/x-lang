---
doc_id: DOC-TOOLS-PLUGIN-SANDBOX
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.1"
maturity: EXTENDED
status: 草案
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [XLF-03-005, XLF-03-007, XLF-03-012, XLF-10-012, XLF-10-014]
---
# 插件与 `build.x` 沙箱

> 状态：草案｜Owner：`role/tooling-team`

## Manifest 与启动接口

`PluginManifest` 字段为 `id:String`、`version:SemVer`、`entry:PathBuf`、`api_version:SemVer`、`permissions:BTreeSet<Permission>`、`inputs:Vec<PathBuf>`、`outputs:Vec<PathBuf>`、`network:NetworkPolicy`、`limits:ResourceProfile`、`signature:Signature`。解析时拒绝未知主版本、重复权限、entry/输入路径越界、缺签名或声明与实际不匹配。

`Sandbox::start(manifest, request, cancel)->Result<PluginHandle,SandboxError>` 前置是签名/registry policy/用户批准（提升权限时）通过；后置是独立进程、最小 env、只读 mount 和审计记录。默认无网络、只读 workspace、只能写声明 outputs/temp，禁止 raw OS handles、secret env、任意子进程和动态下载。

## IPC、取消和资源

IPC 消息为 `Envelope{schema_version:SemVer,request_id:u128,method:String,payload:Bytes,deadline_ms:u64}`；每条消息校验 schema、来源、大小和路径。默认 CPU 30 s、内存 256 MiB、输出 128 MiB、进程 16、并发 4、IPC 64 MiB。取消先发 cooperative cancel，`cancel_grace_ms` 后杀进程组；无论成功/失败都清理 sandbox 临时目录，保留审计和最小 stdout/stderr。

插件错误区分 `invalid_manifest|permission_denied|timeout|quota|crash|protocol|cancelled`。插件输出不能直接作为编译器配置或 Agent 指令，必须过 schema 和二次验证；写入操作默认只产生 patch proposal，需用户批准才能应用。

## 负向测试、版本和回滚

覆盖路径穿越、symlink escape、权限提升未批准、网络/秘密访问、fork bomb、CPU/内存/输出超限、恶意 IPC、日志注入、崩溃后残留、协议乱序和签名撤回。`TEST-TOOLS-PLUGIN-001` 做 syscall/network deny，`TEST-TOOLS-PLUGIN-002` 做 kill/清理，`TEST-TOOLS-PLUGIN-003` 做 API 版本协商。API major 变化需 adapter/feature gate；回滚时禁用 plugin/build gate，使用生成源或上一已签名插件，不执行未审计缓存。
