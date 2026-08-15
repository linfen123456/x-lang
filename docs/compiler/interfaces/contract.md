---
doc_id: DOC-COMPILER-INTERFACES-CONTRACT
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-001, XLF-01-002, XLF-02-002, XLF-02-004, XLF-02-011, XLF-02-014, XLF-11-013]
---
# 编译器公共接口契约

> 状态：草案｜Owner：`role/compiler-team`

本文件是 Driver、LSP、DAP 和后端的接口基线。字段类型使用 Rust 风格记法只是规范表示；实现必须提供等价的稳定 ABI/JSON Schema。

## 接口表

| 接口 | 字段类型 | 前置 | 后置 | 错误与取消 | 并发/资源 Profile |
|---|---|---|---|---|---|
| `SourceManager.load` | `PathBuf -> FileSnapshot` | workspace 根授权 | bytes、行索引和 hash 完整 | `E-SOURCE-*`; 读期间可取消 | snapshot 只读；单文件 16 MiB |
| `Lexer.lex` | `FileSnapshot, LexLimits, CancelToken -> TokenStore` | UTF-8 原 bytes | token range 递增且无越界 | `E-LEX-*`, `E-CANCELLED` | 每 4K token 检查取消 |
| `Parser.parse` | `TokenStore -> ParseResult` | token 顺序合法 | root 覆盖输入，虚拟 token 有标记 | `E-PARSE-*` | 深度 256、节点 10M |
| `QueryEngine.get` | `QueryKey, CancelToken -> QueryValue` | key canonical 且依赖声明 | value hash 与依赖记录一致 | cycle/corrupt/cancel | per-key owner；缓存 10 GiB |
| `Verifier.verify` | `ArtifactRef -> VerifyReport` | schema 可解析 | `ok=true` 才可下游 | `E-VERIFY-*` | blob 2 GiB、递归 256 |
| `Backend.compile` | `VerifiedMir, TargetSpec, CodegenOptions, OperationContext -> OperationOutcome<CodegenOutput>` | MIR/target 已验证 | Completed 时对象和 source map 带目标 hash | unsupported/tool/cancel/timeout/quota | 外部进程 10 min |
| `Linker.link` | `ObjectArtifact[], TargetSpec, LinkOptions, OperationContext -> OperationOutcome<LinkedArtifact>` | 对象架构、ABI 与 target 一致 | Completed 时制品与 manifest 原子发布 | symbol/tool/cancel/timeout/quota | 外部进程 10 min、临时目录 4 GiB |
| `Driver.compile` | `CompileRequest -> CompileResult` | 配额/profile 已解析 | 成功只有完整 manifest | user/build/env/cancel | 默认并行=CPU 数 |

## 取消与提交协议

`CancelToken` 字段为 `id:RequestId`、`reason:CancelReason`、`deadline:Instant?`、`source:Caller|Timeout|Quota|Shutdown`。实现必须在 I/O、锁等待、查询、验证、Pass 和子进程边界观察 token；取消的调用可返回已有的只读 cache hit，但不能创建新 cache entry。提交采用 `prepare → validate → fsync(optional) → atomic-rename → publish-index`；任一步失败都回滚临时目录。

## 稳定 JSON 结构

```json
{
  "schema_version":"1.0",
  "command":"build",
  "request_id":"0123456789abcdef0123456789abcdef",
  "status":"success",
  "diagnostics":[{"code":"X-E-TYPE-MISMATCH","severity":"error","message":"type mismatch","primary_span":{"file_id":1,"start":4,"end":5},"retryable":false}],
  "artifacts":[{"kind":"object","path":"target/app.o","sha256":"hex-digest","size":123}],
  "duration_ms":12,
  "resource":{"peak_memory_bytes":456,"network_bytes":0,"children":1},
  "compiler_stats":{"cache_hits":3}
}
```

`duration_ms` 与 `resource` 是所有工具共享的稳定字段；`compiler_stats` 是编译器可选扩展，客户端必须允许忽略未知次版本字段。未知 `schema_version` 主版本拒绝。JSON 消息、路径、fix-it 和日志不得回显秘密；错误必须包含可操作的 `notes` 或 `retryable` 原因。

## 负向测试、兼容与回滚

必须有 `TEST-COMPILER-CONTRACT-001`（越权路径/坏 schema）、`TEST-COMPILER-CONTRACT-002`（重复取消/超时）、`TEST-COMPILER-CONTRACT-003`（缓存损坏/提交原子性）、`TEST-COMPILER-CONTRACT-004`（并发查询）和跨平台 ABI 黄金测试。接口变更先追加可选字段并更新 schema；破坏性变化提升主版本、保留 adapter 一个稳定周期，回归时通过 `--compiler-schema 1.0`、禁用新 Backend 或冷编译回滚。
