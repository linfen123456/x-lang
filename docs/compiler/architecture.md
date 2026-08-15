---
doc_id: DOC-COMPILER-ARCHITECTURE
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P1
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-001, XLF-02-001, XLF-02-002, XLF-02-003, XLF-02-004, XLF-02-009]
---
# 编译器架构与阶段边界

> 状态：草案｜Owner：`role/compiler-team`

## 目标与依赖方向

架构目标是可替换前端、可验证中间表示、可插拔后端和可重现驱动。语义产物方向固定为 `source → syntax → semantic → typed HIR → MIR → borrow/verify → [optimize] → backend → artifact`；QueryEngine 是包围各阶段的调度与缓存机制，不是必须位于 MIR 与 Backend 之间的语义 IR。P1 的冷编译/O0 路径可在 MIR 验证后直接进入 Backend，P2 才引入增量 Query 与可配置优化 Pass。运行时只通过 ABI 头文件被 codegen 消费，工具通过 Driver/LSP/DAP 公共接口消费，不能反向引用前端私有类型。编译器会话只能拥有 `Arc<WorkspaceSnapshot>`，不能直接改变磁盘源文件。

## 核心结构

```text
WorkspaceSnapshot
  ├─ SourceManager -> TokenStore -> LosslessSyntaxTree/AST
  ├─ AST -> Resolver -> TypeChecker -> TraitSolver -> TypedHIR
  ├─ TypedHIR -> MIRBuilder -> BorrowChecker -> MirVerifier
  ├─ QueryEngine(CacheStore) wraps the stages above
  ├─ MirVerifier -> O0 Backend (P1 cold path)
  ├─ MirVerifier -> Optimizer -> Backend (P2 optimized path)
  └─ DiagnosticBus -> Driver -> ArtifactManifest
```

| 接口 | 字段类型 | 前置条件 | 后置条件/错误 |
|---|---|---|---|
| `CompilerSession::open` | `workspace:PathBuf, profile:Profile, cancel:CancelToken` | 根目录已授权且 profile 已解析 | 返回不可变会话；`E-SESSION-ROOT`、`E-SESSION-LIMIT` |
| `Stage::run` | `input:ArtifactId, ctx:StageContext` | 输入 schema 与 verifier 通过 | 返回新 `ArtifactId` 或 `DiagnosticSet`；不修改输入 |
| `ArtifactStore::commit` | `temp:TempArtifact, manifest:ArtifactManifest` | 所有文件在输出根内且 hash 完整 | 原子 rename；磁盘满/权限错误不留下成品 |
| `Verifier::verify` | `artifact:Bytes, schema:SchemaVersion` | 最大字节数和递归深度未超限 | `VerifyReport{ok, errors}`；拒绝未知主版本 |

取消在文件读、查询等待、验证循环、Pass 循环和外部进程边界观察；取消后返回 `E-CANCELLED`，缓存与制品均不提交。阶段内部可并行查询，但不得持有锁调用插件或执行用户代码。默认并行度为物理核数上限，`ci` Profile 固定为 2 以稳定资源。

## SourceManager 与工件生命周期

`SourceManager` 维护 `FileId:u32`、规范化绝对路径、版本 `u64`、原始 bytes、UTF-8 状态、行索引和 `source_fingerprint:[u8;32]`。虚拟文件和编辑缓冲必须有来源标记；路径必须位于授权 workspace 根，符号链接解析后再次检查。snapshot 采用 copy-on-write，旧 snapshot 只读并可被 LSP 查询。

工件头统一字段：`schema_version:SemVer`、`producer_version:SemVer`、`source_fingerprint:Hash32`、`target_fingerprint:Hash32?`、`profile_id:String`、`created_at:MonotonicDuration`。时间只用于诊断统计，不进入语义 hash。序列化采用长度前缀、上限检查和校验和，截断/整数溢出返回 `E-ARTIFACT-FORMAT`。

## 资源 Profile 与负向测试

`dev` 默认单 workspace 64 MiB、单文件 16 MiB、递归深度 256、IR 节点 10,000,000；`ci` 取一半并禁止插件；`release` 可提高但必须有 `resource_profile` 证据。测试 `TEST-COMPILER-ARCH-001` 检查非法依赖，`TEST-COMPILER-ARCH-002` 检查 snapshot 隔离，`TEST-COMPILER-ARCH-003` 检查取消无提交，`TEST-COMPILER-ARCH-004` 检查坏工件无崩溃。回滚通过关闭新 stage gate、清空对应缓存 namespace、恢复上一 producer/schema 版本完成。
