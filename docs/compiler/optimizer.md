---
doc_id: DOC-COMPILER-OPTIMIZER
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: EXTENDED
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-01-003, XLF-02-004, XLF-12-011, XLF-12-012]
---
# MIR 优化 Pass 实施规范

> 状态：草案｜Owner：`role/compiler-team`

## Pass 契约

`PassSpec` 字段为 `id:String`、`version:SemVer`、`requires:Vec<Invariant>`、`preserves:Vec<Invariant>`、`profile_gate:ProfileGate`、`max_cpu_ms:u64`、`max_memory_bytes:u64`、`determinism:Determinism`。`PassManager::run(pipeline:Vec<PassSpec>, body:VerifiedMir, cancel:CancelToken)->Result<OptimizedBody,PassReport>` 的前置是输入完整 verifier 通过且 pipeline DAG 无环；每个 Pass 输出都必须重新运行完整结构/类型/CFG/move/borrow/Drop verifier，并对全部 `preserves` 声明核对 analysis fingerprint 后才可交给下一 Pass。抽样只允许作为 debug 额外诊断，不能成为正式接受条件。后置是每个 Pass 产生输入/输出 hash、变更统计和完整 verifier 报告。

默认管线按 `const-fold → cfg-simplify → copy-prop → dead-block → drop-elaboration-check` 执行；O0 只运行必要 lowering，O1 可启用局部传播，O2 才能启用内联/逃逸分析。TCO、likely/unlikely、自动微分和平台专用向量化需独立 RFC/feature gate，不得改变失败、Drop、借用或 ABI 语义。

## 不变量和优化证明

每个 Pass 必须明确保持：类型和布局、控制流终止、初始化/移动状态、Drop 顺序、借用合法性、panic/unwind edge、volatile/atomic 顺序、source map 可追溯性。常量折叠遇到溢出、NaN、外部可观察副作用时必须保持原操作；`likely` 仅生成 hint，不允许删除分支。优化失败或证明未知时保留输入 MIR 并返回 `PassSkipped{reason}`，不是静默生成。

## 并发、取消和资源 Profile

不同函数的纯 Pass 可并行，但同一 `MirBody` 的 Pass 串行；共享 analysis cache 采用不可变快照。每个 Pass 在循环回边和节点批次检查取消，返回 `E-CANCELLED` 且不提交 cache。单函数 10M 节点、Pass 30 s、256 MiB 只是 `candidate_default` 防御预算，遵循 [编译器 Budget 治理](./README.md#资源预算治理)，由 Profile 提供且不得硬编码；超过返回 `E-PASS-LIMIT`。`release` 只有在 Budget ADR 批准并写入 ArtifactManifest 后才可提高。

## 负向测试与回滚

使用 compile-pass/fail、随机 MIR、边界整数/浮点、panic/Drop、原子与 volatile 样例，比较 O0/O2 与 interpreter。负向测试 `TEST-COMPILER-OPT-001` 验证错误 Pass 被 verifier 拒绝，`TEST-COMPILER-OPT-002` 验证取消和超时无部分结果，`TEST-COMPILER-OPT-003` 验证非确定 Pass 在两次运行得到同一 hash。单 Pass 有独立 gate；回归时从 manifest 删除该 Pass、恢复上一个 pipeline 版本，禁止回退到未验证缓存。
