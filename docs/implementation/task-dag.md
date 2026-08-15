---
doc_id: DOC-IMPLEMENTATION-TASK-DAG
authority: implementation
owner: role/architecture
backup_owner: role/program-management
version: "1.2"
maturity: CORE
status: 草案
phase: P0
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-001, XLF-01-002, XLF-01-003, XLF-01-006, XLF-01-009, XLF-02-001, XLF-02-002, XLF-02-003, XLF-02-004, XLF-02-009, XLF-02-011, XLF-02-013, XLF-02-014, XLF-02-015, XLF-05-001, XLF-05-002, XLF-05-005, XLF-05-008, XLF-09-006, XLF-10-001, XLF-10-002, XLF-10-003, XLF-10-012, XLF-11-001, XLF-11-004, XLF-11-013, XLF-12-016, XLF-12-020]
---
# X-Lang P0–P6 实施任务 DAG

本 DAG 采用 Markdown 任务卡，字段名与治理模板一致。所有测试、报告、基准和审计目前均为 `planned`，这里只定义注册项和证据类型，不声称已经存在实现证据。阶段主链为 `P0 规范与探针 → P1 前端/IR/Backend/Linker/CLI 闭环 → P2 语义/运行时/增量 → P3 LSP/DAP/XPM/沙箱 → P4 冻结/安全/性能 → P5 扩展 → P6 研究`。

## P0：基线

### TASK-P0-GOV-001 文档治理与追溯基线

- `title`: 元数据、Owner/状态、真实 XLF 和链接门禁
- `owner`: `role/architecture`; `backup_owner`: `role/documentation`
- `status`: 草案; `phase`: P0; `milestone`: M0
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-02-001`, `XLF-11-001`, `XLF-11-003`, `XLF-11-013`
- `spec_or_rfc`: `RULE-GOV-001`, `RULE-GOV-002`
- `project_id`: `PROJ-TESTING`; `project_path`: `tests/`
- `dependencies`: 无
- `inputs`: `docs/governance/`, 原始追溯矩阵、目标专题 Markdown
- `outputs`: planned `reports/document-metadata.md`, planned `reports/traceability.md`
- `api_or_artifacts`: `DocCheckReport`, `TraceabilityReport`
- `test_ids`: `TEST-GOV-META-001`, `TEST-GOV-TRACE-001`（planned registry）
- `performance_budget`: 2 分钟、256 MiB、并发 4
- `security_budget`: 原始文档只读；路径和链接不能越出 workspace
- `acceptance`: 所有目标 Markdown 有合法 front matter；Owner/状态正文一致；source ID 逐项命中矩阵；无断链
- `evidence`: planned 元数据报告、planned 追溯报告、planned CI 日志
- `rollback`: 恢复上一版文档门禁规则，不修改原始文档
- `estimate`: 12h; `non_goals`: 不实现编译器或测试源码

### TASK-P0-COMP-001 语言与 IR 契约冻结

- `title`: Token/AST/TypedHIR/MIR/Verifier 字段和不变量
- `owner`: `role/compiler-team`; `backup_owner`: `role/language-team`
- `status`: 草案; `phase`: P0; `milestone`: M0
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-01-001`, `XLF-01-002`, `XLF-01-003`, `XLF-01-006`
- `spec_or_rfc`: `XSP-LANG-001`, `XSP-LANG-002`, `XSP-MEM-001`, `RULE-COMPILER-001`
- `project_id`: `PROJ-COMPILER-CORE`; `project_path`: `compiler/`
- `dependencies`: `TASK-P0-GOV-001`
- `inputs`: `docs/specs/language-core.md`, `docs/specs/memory-concurrency.md`
- `outputs`: planned `compiler/x-syntax/README.md`, planned `compiler/x-hir/README.md`, planned `compiler/x-mir/README.md`
- `api_or_artifacts`: `TypedAst`, `HirBody`, `MirBody`, `VerifierReport`
- `test_ids`: `TEST-COMPILER-SCHEMA-001`, `TEST-COMPILER-SCHEMA-002`（planned registry）
- `performance_budget`: schema round-trip 1 分钟、单工件 2 GiB
- `security_budget`: 拒绝截断、未知主版本和越界 Span
- `acceptance`: 规定 `Resolver/Type/Trait → TypedHIR → MIR → Borrow`；HIR 节点数约束明确；每个 MIR block 有 terminator
- `evidence`: planned schema diff、planned verifier fixture、planned RFC/ADR
- `rollback`: 保留上一 IR 版本并关闭新 lowering gate
- `estimate`: 24h; `non_goals`: 不实现 async 稳定语义

## P1：端到端最小闭环

### TASK-P1-COMP-001 SourceManager、Lexer、恢复 Parser

- `title`: 源快照、词法、错误恢复和稳定诊断
- `owner`: `role/compiler-team`; `backup_owner`: `role/architecture`
- `status`: 草案; `phase`: P1; `milestone`: M1
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-01-002`, `XLF-02-002`, `XLF-02-004`, `XLF-11-013`
- `spec_or_rfc`: `XSP-LANG-001`, `RULE-COMPILER-002`
- `project_id`: `PROJ-DOMAIN-X-SYNTAX`; `project_path`: `compiler/x-syntax/`
- `dependencies`: `TASK-P0-COMP-001`
- `inputs`: planned `FileSnapshot`、UTF-8 bytes、LSP document snapshot
- `outputs`: planned TokenStore、lossless syntax tree、错误 AST
- `api_or_artifacts`: `SourceManager.load`, `Lexer.lex`, `Parser.parse`
- `test_ids`: `TEST-COMPILER-FRONT-001`, `TEST-COMPILER-FRONT-002`, `TEST-COMPILER-FRONT-003`（planned registry）
- `performance_budget`: 单文件 16 MiB、Parser 深度 256、节点 10M、2 秒
- `security_budget`: workspace 根校验、非法 UTF-8 不替换、不读网络
- `acceptance`: Hello World 和非法输入均输出可定位诊断；恢复不重复报错；取消不提交缓存
- `evidence`: planned 诊断快照、planned fuzz 结果、planned 峰值内存报告
- `rollback`: 切换旧 parser gate，保留旧快照
- `estimate`: 40h; `non_goals`: 不执行类型或 borrow 检查

### TASK-P1-COMP-002 Resolver、Type/Trait 与 TypedHIR

- `title`: 名称解析、类型/Trait 求解和 TypedHIR lowering
- `owner`: `role/compiler-team`; `backup_owner`: `role/language-team`
- `status`: 草案; `phase`: P1; `milestone`: M1
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-01-002`, `XLF-01-006`, `XLF-01-010`
- `spec_or_rfc`: `XSP-LANG-002`, `XSP-LANG-004`, `RULE-COMPILER-003`
- `project_id`: `PROJ-DOMAIN-X-TYPES`; `project_path`: `compiler/x-types/`
- `dependencies`: `TASK-P1-COMP-001`
- `inputs`: planned AST、module graph、feature set
- `outputs`: planned DefMap、TypeTable、ObligationReport、TypedHIR
- `api_or_artifacts`: `Resolver`, `TypeChecker`, `TraitSolver`, `HirLowerer`
- `test_ids`: `TEST-COMPILER-SEM-001`, `TEST-COMPILER-SEM-002`, `TEST-COMPILER-HIR-001`（planned registry）
- `performance_budget`: trait depth 128、候选 10k、单函数 10M 节点、512 MiB
- `security_budget`: 不猜 ambiguous trait；未知名称/循环导入阻断
- `acceptance`: 输出只引用 DefId/TypeId；TypedHIR 不依赖 BorrowReport；async gate 未通过时产生 feature-disabled 诊断
- `evidence`: planned resolver trace、planned type diagnostics、planned HIR verifier report
- `rollback`: 回退到 AST-only diagnostics，禁用 TypedHIR gate
- `estimate`: 56h; `non_goals`: 不实现 MIR borrow

### TASK-P1-COMP-003 MIR、Borrow 和优化前 verifier

- `title`: TypedHIR→MIR、节点约束、Borrow 两阶段检查
- `owner`: `role/compiler-team`; `backup_owner`: `role/memory-team`
- `status`: 草案; `phase`: P1; `milestone`: M1
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-01-003`, `XLF-01-006`, `XLF-10-002`, `XLF-12-014`
- `spec_or_rfc`: `XSP-MEM-001`, `XSP-MEM-002`, `RULE-COMPILER-004`
- `project_id`: `PROJ-DOMAIN-X-MIR`; `project_path`: `compiler/x-mir/`
- `dependencies`: `TASK-P1-COMP-002`
- `inputs`: planned TypedHIR、Drop/unwind policy、Target-independent types
- `outputs`: planned MIR、BorrowReport、VerifierReport
- `api_or_artifacts`: `MirBuilder`, `BorrowChecker`, `MirVerifier`
- `test_ids`: `TEST-COMPILER-IR-001`, `TEST-COMPILER-IR-002`, `TEST-COMPILER-BORROW-001`（planned registry）
- `performance_budget`: 单函数 10M 节点、30 秒、256 MiB
- `security_budget`: move/loan/Drop 不变量；raw pointer 不进入 safe MIR
- `acceptance`: MIR 后才开始 Borrow；每个 block 一个 terminator；Drop 恰好一次；节点计数等于结构遍历计数
- `evidence`: planned malformed-MIR fixtures、planned compile-fail cases、planned verifier proof
- `rollback`: 禁用 Borrow/Pass gate，使用未优化 MIR；保留输入 body
- `estimate`: 64h; `non_goals`: 不改变语言规则

### TASK-P1-COMP-004 Backend、Codegen、Linker 与 Hello World

- `title`: TargetSpec 适配、LLVM backend、链接器和端到端制品
- `owner`: `role/compiler-team`; `backup_owner`: `role/release-team`
- `status`: 草案; `phase`: P1; `milestone`: M1
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-01-001`, `XLF-02-002`, `XLF-02-003`, `XLF-02-011`
- `spec_or_rfc`: `RULE-COMPILER-005`, `RULE-FFI-001`
- `project_id`: `PROJ-DOMAIN-X-CODEGEN-LLVM`; `project_path`: `compiler/x-codegen-llvm/`
- `dependencies`: `TASK-P1-COMP-003`, `TASK-P0-COMP-001`；P1 使用 MirVerifier→O0 Backend 冷路径，不依赖 P2 Query/Optimizer
- `inputs`: planned verified MIR、公开 `PalTargetRequest`、ABI header、TargetSpec
- `outputs`: planned object、executable、debug map、ArtifactManifest、Hello World run log
- `api_or_artifacts`: `Backend.compile`, `Linker.link`, `OperationContext`, `ArtifactManifest`
- `test_ids`: `TEST-COMPILER-CODEGEN-001`, `TEST-COMPILER-LINK-001`, `TEST-COMPILER-E2E-001`（planned registry）
- `performance_budget`: Backend/Linker 共用 10 分钟 deadline、单制品 2 GiB、temp 4 GiB
- `security_budget`: sysroot/linker 在授权根；无隐式 host config；panic 不跨 C ABI
- `acceptance`: Windows/Linux/macOS Tier 1 至少完成 Hello World compile→link→run；Backend 和 Linker 共享 cancel/timeout 状态；失败无半成品
- `evidence`: planned ABI probe、planned linker log、planned E2E transcript、planned manifest digest
- `rollback`: 切回旧 Backend/Linker 或 O0 interpreter；删除未发布临时制品
- `estimate`: 72h; `non_goals`: 不实现 WASM/GPU/eBPF

### TASK-P1-TOOLS-001 x.toml entry、CLI JSON 和冷编译

- `title`: `x check/build/run`、entry 解析、统一 CLI JSON
- `owner`: `role/tooling-team`; `backup_owner`: `role/compiler-team`
- `status`: 草案; `phase`: P1; `milestone`: M1
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-02-013`, `XLF-02-014`, `XLF-11-013`
- `spec_or_rfc`: `RULE-TOOLS-001`, `XSP-LANG-005`
- `project_id`: `PROJ-TOOLS-XCLI`; `project_path`: `tools/x-cli/`
- `dependencies`: `TASK-P1-COMP-004`
- `inputs`: planned `x.toml` with `package.entry`、source、TargetSpec、ProfileSpec
- `outputs`: planned CommandResult、executable、manifest、退出码报告
- `api_or_artifacts`: `CommandRequest`, `CommandResult`, `x.toml`, `ArtifactManifest`
- `test_ids`: `TEST-TOOLS-CLI-001`, `TEST-TOOLS-CLI-002`, `TEST-TOOLS-CLI-003`（planned registry）
- `performance_budget`: 命令 10 分钟、JSON 1 GiB、子进程 64
- `security_budget`: entry 必须 workspace-relative；stdout/stderr 分离；无秘密回显
- `acceptance`: `x.toml` entry 合法性明确；compiler/tool JSON 结构一致；冷编译可生成并运行 Hello World
- `evidence`: planned CLI transcript、planned JSON fixtures、planned exit-code matrix
- `rollback`: 使用上一 CLI/schema 和冷编译，不删除用户源或 lockfile
- `estimate`: 40h; `non_goals`: 不实现 publish/插件

## P2–P6 后续卡（接口先行，全部 planned）

### TASK-P2-COMP-001 Query、Pass 和增量缓存

- `title`: Query、Pass 和增量缓存
- `owner`: `role/compiler-team`; `backup_owner`: `role/architecture`; `status`: 草案; `phase`: P2; `milestone`: M2
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-01-003`, `XLF-02-004`, `XLF-12-020`; `spec_or_rfc`: `RULE-COMPILER-006`
- `project_id`: `PROJ-COMPILER-CORE`; `project_path`: `compiler/`; `dependencies`: `TASK-P1-COMP-003`
- `inputs`: planned MIR、schema/pass/pipeline fingerprints; `outputs`: planned cache index、PassReport
- `api_or_artifacts`: `QueryKey`, `QueryState`, `CacheEntry`, `PassReport`
- `test_ids`: `TEST-COMPILER-QUERY-001`, `TEST-COMPILER-OPT-001`（planned registry）
- `performance_budget`: cache 10 GiB、Pass 单次 30 秒/256 MiB、并发由 Profile 决定
- `security_budget`: content hash、schema/pass/pipeline fingerprint；坏缓存隔离
- `acceptance`: Query 状态 `Vacant→Running→Ready|Poisoned`；key 含 schema/pass/pipeline；取消 waiter 不毒化 owner
- `evidence`: planned invalidation trace、planned O0/O2 diff; `rollback`: 关闭增量和新 Pass
- `non_goals`: 不改变语言语义; `estimate`: 64h

### TASK-P2-RT-001 Task、I/O、配额和 shutdown

- `title`: Task、I/O、配额和 shutdown
- `owner`: `role/runtime-team`; `backup_owner`: `role/architecture`; `status`: 草案; `phase`: P2; `milestone`: M2
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-01-009`, `XLF-02-009`, `XLF-05-001`, `XLF-05-008`, `XLF-12-016`; `spec_or_rfc`: `XSP-MEM-004`, `RFC-ASYNC-001`
- `project_id`: `PROJ-RUNTIME-XRT`; `project_path`: `runtime/xrt/`; `dependencies`: `TASK-P0-COMP-001`, `TASK-P1-COMP-004`，以及 async 子范围的 `RFC-ASYNC-001` 已决策
- `inputs`: planned JoinHandle/IoOp/Quota/Cancel; `outputs`: planned runtime state-machine report
- `api_or_artifacts`: `JoinHandle`, `TaskState`, `IoState`, `ShutdownState`, `QuotaLease`
- `test_ids`: `TEST-RUNTIME-CONC-001`, `TEST-RUNTIME-IO-001`, `TEST-RUNTIME-SHUTDOWN-001`（planned registry）
- `performance_budget`: 任务 1M、并发 I/O 100k、单 I/O 64 MiB、取消宽限 1 秒
- `security_budget`: C ABI 仅固定布局 XrtStatus；句柄 generation 防重用
- `acceptance`: RFC 未通过时只实现同步 I/O、配额和 shutdown，async gate 保持关闭；RFC 通过后才实现 Future/Task/Waker 子范围；Task/I/O/shutdown 状态机无重复完成；quota cancel 阻止新 acquire；C ABI 仅 XrtStatus
- `evidence`: planned model test、planned fault injection、planned ABI probe; `rollback`: 单线程/稳定 I/O fallback
- `non_goals`: 不承诺通用硬实时; `estimate`: 80h

### TASK-P3-TOOLS-001 XPM 与可复现依赖解析

- `title`: XPM registry、依赖求解、x.lock、离线缓存与签名验证
- `owner`: `role/package-team`; `backup_owner`: `role/security-team`; `status`: 草案; `phase`: P3; `milestone`: M3
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-02-005`, `XLF-11-001`, `XLF-11-006`; `spec_or_rfc`: `RULE-TOOLS-002`
- `project_id`: `PROJ-TOOLS-XPM`; `project_path`: `tools/xpm/`; `dependencies`: `TASK-P1-TOOLS-001`
- `inputs`: planned x.toml、旧 lock、registry snapshot、target/features；`outputs`: planned resolution、x.lock、下载/签名报告
- `api_or_artifacts`: `Resolution`, `Lockfile`, `RegistrySnapshot`, `PackageSignature`
- `test_ids`: `TEST-TOOLS-XPM-001`, `TEST-TOOLS-XPM-002`, `TEST-TOOLS-XPM-OFFLINE-001`（planned）
- `performance_budget`: 包 512 MiB、下载并发 10、求解 60 秒；`security_budget`: hash/signature/SBOM、路径与解包上限、构建脚本默认禁用
- `acceptance`: 相同输入产生唯一 lock；offline 不联网；签名/哈希错误不写缓存；冲突给出最小解释
- `evidence`: planned resolution fixtures、planned offline transcript；`rollback`: 恢复旧 lock/registry snapshot 并冷解析
- `non_goals`: 不自动发布包；`estimate`: 32h

### TASK-P3-TOOLS-002 LSP 与 DAP

- `title`: 增量语言服务、调试协议与 Snapshot 一致性
- `owner`: `role/ide-team`; `backup_owner`: `role/compiler-team`; `status`: 草案; `phase`: P3; `milestone`: M3
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-02-007`, `XLF-11-003`; `spec_or_rfc`: `RULE-TOOLS-003`
- `project_id`: `PROJ-TOOLS-XLSP`; `project_path`: `tools/x-lsp/`; `dependencies`: `TASK-P2-COMP-001`
- `inputs`: planned document snapshots、capabilities、source maps、cancel tokens；`outputs`: planned diagnostics/completion/navigation/debug transcripts
- `api_or_artifacts`: `LspSnapshot`, `LspRequest`, `DapSession`, `SourceMap`
- `test_ids`: `TEST-TOOLS-LSP-001`, `TEST-TOOLS-LSP-CANCEL-001`, `TEST-TOOLS-DAP-001`（planned）
- `performance_budget`: 普通请求 P95 2 秒、并发 32；`security_budget`: URI/workspace 授权、变量值截断与脱敏
- `acceptance`: 旧 document version 不覆盖新诊断；取消不发布结果；断点能经 SourceMap 映射脱糖代码
- `evidence`: planned protocol fixtures、planned editor E2E；`rollback`: 关闭增量、使用上一协议能力集
- `non_goals`: 不直接修改未授权文件；`estimate`: 32h

### TASK-P3-TOOLS-003 Formatter、Doc 与 Test Runner

- `title`: xfmt、xdoc/doc-test 与 xtest 的一致执行契约
- `owner`: `role/tooling-team`; `backup_owner`: `role/quality-team`; `status`: 草案; `phase`: P3; `milestone`: M3
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-02-014`, `XLF-03-010`, `XLF-11-004`; `spec_or_rfc`: `RULE-TOOLS-004`
- `project_id`: `PROJ-TOOLS-XFMT`; `project_path`: `tools/xfmt/`; `dependencies`: `TASK-P1-TOOLS-001`, `TASK-P2-COMP-001`
- `inputs`: planned AST/HIR、FormatConfig、DocIndex、TestPlan；`outputs`: planned patches、文档、TestReport
- `api_or_artifacts`: `FormatResult`, `DocIndex`, `TestPlan`, `TestReport`
- `test_ids`: `TEST-TOOLS-FMT-001`, `TEST-TOOLS-DOC-001`, `TEST-TOOLS-RUNNER-001`（planned）
- `performance_budget`: 单文件 16 MiB、单 test 5 分钟、输出 64 MiB；`security_budget`: doc-test 隔离、子进程树清理、无隐式网络
- `acceptance`: formatter 幂等且保持语义；doc-test 失败阻止发布；测试 retry 不掩盖首次失败；退出码遵守统一矩阵
- `evidence`: planned round-trip corpus、planned report fixtures；`rollback`: 固定旧 format_version/test schema
- `non_goals`: 不提供生产代码执行服务；`estimate`: 28h

### TASK-P3-TOOLS-004 插件与构建脚本沙箱

- `title`: 插件 manifest、能力授权、隔离执行与审计
- `owner`: `role/security-team`; `backup_owner`: `role/tooling-team`; `status`: 草案; `phase`: P3; `milestone`: M3
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-10-012`, `XLF-11-006`; `spec_or_rfc`: `RULE-SECURITY-001`
- `project_id`: `PROJ-TOOLS-XPLUGIN`; `project_path`: `tools/x-plugin-host/`; `dependencies`: `TASK-P1-TOOLS-001`, `TASK-P3-TOOLS-001`
- `inputs`: planned signed PluginManifest、声明输入/输出、limits；`outputs`: planned plugin output、审计摘要、拒绝原因
- `api_or_artifacts`: `PluginManifest`, `SandboxProfile`, `PluginOutcome`
- `test_ids`: `TEST-TOOLS-PLUGIN-001`, `TEST-TOOLS-PLUGIN-NET-001`, `TEST-TOOLS-PLUGIN-QUOTA-001`（planned）
- `performance_budget`: CPU 30 秒、内存 256 MiB、输出 64 MiB；`security_budget`: 默认只读/无网络/无秘密、显式 capability lease
- `acceptance`: 越权网络/路径/进程被拒绝；取消清理子进程；不可信输出重新验证后才进入构建图
- `evidence`: planned sandbox denial log、planned malicious plugin corpus；`rollback`: 全局禁用插件并使用纯核心构建
- `non_goals`: 不允许插件改变稳定语义或直接发布；`estimate`: 28h

### TASK-P4-REL-001 冻结、兼容、安全和性能

- `title`: 冻结、兼容、安全和性能
- `owner`: `role/release-team`; `backup_owner`: `role/security-team`; `status`: 草案; `phase`: P4; `milestone`: M4
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-11-001`, `XLF-11-004`, `XLF-12-020`; `spec_or_rfc`: `RULE-RELEASE-001`
- `project_id`: `PROJ-RELEASE`; `project_path`: `release/`; `dependencies`: `TASK-P2-COMP-001`, `TASK-P3-TOOLS-001`, `TASK-P3-TOOLS-002`, `TASK-P3-TOOLS-003`, `TASK-P3-TOOLS-004`
- `inputs`: planned API/ABI diff、SBOM、benchmark baseline; `outputs`: planned compatibility/security/performance report
- `api_or_artifacts`: `CompatReport`, `SbomReport`, `BenchmarkReport`, `RollbackDrill`
- `test_ids`: `TEST-RELEASE-COMPAT-001`, `TEST-SEC-SUPPLY-001`, `TEST-PERF-REPRO-001`（planned registry）
- `performance_budget`: benchmark 60 分钟、固定硬件/OS/数据集并报告 P50/P95/P99
- `security_budget`: SBOM、签名、CVE/许可证和双构建；高危阻断
- `acceptance`: N-1/N/N+1、双构建、SBOM、P50/P95/P99 和 rollback drill 均有 planned evidence 类型
- `evidence`: planned Go/No-Go ADR、planned signed manifest; `rollback`: 保持 Beta 或恢复上一稳定版本
- `non_goals`: 不把无证据数字写成 SLO; `estimate`: 48h

### TASK-P5-EXT-001 扩展目标与生态适配

- `title`: 扩展目标与生态适配
- `owner`: `role/compiler-team`; `backup_owner`: `role/runtime-team`; `status`: 草案; `phase`: P5; `milestone`: M5
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-01-005`, `XLF-02-011`, `XLF-05-009`; `spec_or_rfc`: `RULE-TARGET-EXT-001`
- `project_id`: `PROJ-COMPILER-WASM`; `project_path`: `backends/x-codegen-wasm/`; `dependencies`: `TASK-P4-REL-001`
- `inputs`: planned target capability、ABI adapter; `outputs`: planned wasm/native extension artifacts
- `api_or_artifacts`: `TargetAdapter`, `ExtensionArtifactManifest`
- `test_ids`: `TEST-EXT-ABI-001`, `TEST-EXT-TARGET-001`（planned registry）
- `performance_budget`: 单目标构建 10 分钟、单制品 2 GiB
- `security_budget`: capability、签名、ABI/target fingerprint 必须匹配
- `acceptance`: 扩展失败不影响 CORE；每目标有 capability、签名、回滚和资源证据类型
- `evidence`: planned target matrix; `rollback`: 关闭扩展 gate
- `non_goals`: 不承诺通用 C++ 模板互操作; `estimate`: 60h

### TASK-P6-RES-001 研究原型退出门禁

- `title`: 研究原型退出门禁
- `owner`: `role/research-team`; `backup_owner`: `role/security-team`; `status`: 草案; `phase`: P6; `milestone`: M6
- `last_reviewed`: 2026-08-15
- `source_ids`: `XLF-03-005`, `XLF-03-007`, `XLF-11-006`, `XLF-12-015`; `spec_or_rfc`: `RFC-RESEARCH-GATE-001`
- `project_id`: `PROJ-LABS`; `project_path`: `labs/`; `dependencies`: `TASK-P4-REL-001`
- `inputs`: planned threat model、budget、capability matrix; `outputs`: planned prototype、Go/No-Go、退出报告
- `api_or_artifacts`: `ResearchCharter`, `ExitReport`, `ProvenanceRecord`
- `test_ids`: `TEST-RESEARCH-GATE-001`（planned registry）
- `performance_budget`: 每实验 2 小时/8 GiB；token、工具调用和网络预算显式记录
- `security_budget`: 独立 labs、默认无生产权限、威胁模型和 provenance
- `acceptance`: 默认关闭、不进入 CORE 依赖图；连续两个里程碑无证据自动归档
- `evidence`: planned charter、planned benchmark、planned exit report; `rollback`: 归档并移除 gate
- `non_goals`: 不生成稳定实现或生产制品; `estimate`: 80h

## 阶段门禁

- P0：规范、真实追溯和前置/后置不变量齐全。
- P1：Source→TypedHIR→MIR→Borrow→Backend→Linker→CLI 的 Hello World 闭环可规划验收，所有测试仍标记 planned。
- P2：Query/Task/I/O/cache/profile 状态机和资源取消契约完成。
- P3：工具协议和沙箱完成兼容/安全规划。
- P4：只有获得实际测试、性能、安全和制品证据后才允许升级成熟度。
- P5/P6：扩展或研究失败只能局部回滚，不得影响 CORE。
