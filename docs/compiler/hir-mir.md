---
doc_id: DOC-COMPILER-HIR-MIR
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-01-002, XLF-01-003, XLF-01-006, XLF-02-002, XLF-10-002, XLF-12-014]
---
# HIR、MIR 与 Verifier 实施规范

> 状态：草案｜Owner：`role/compiler-team`

## HIR 结构

HIR 是脱糖后仍保留语义边界的树/图。`HirBody` 是单 owner 的有类型、尚未验证 body，字段为 `owner:DefId`、`params:Vec<LocalDecl>`、`exprs:Vec<HirExpr>`、`patterns:Vec<HirPattern>`、`source_map:SpanMap`、`effect_set:EffectSet`。`TypedHirModule` 聚合 `Vec<HirBody>`、DefMap、TypeTable 和 module source map；`HirVerifier` 输出名义包装 `VerifiedHirModule`，MIR Builder 只能按 owner 消费其中的 `VerifiedHirBody`。表达式引用 `HirId:u32`，类型引用已 canonicalize 的 `TypeId`；所有名字已解析为 `DefId`，不能保留字符串查找。

Lowering 前置：AST root 通过 AST verifier，Resolver/Type/Trait 已产生 `TypedAst`；不读取 BorrowReport，也不要求 borrow 诊断完成。后置：每个 AST 可观察构造恰好有一个 HIR 语义节点；`defer`、`?`、模式匹配、隐式 drop 和闭包捕获均显式化。错误返回 `X-E-HIR-LOWER`，取消返回 `X-E-CANCELLED`，任何失败都不提交 body cache。

## MIR 结构和不变量

`MirBody` 字段为 `owner:DefId`、`locals:Vec<LocalDecl{ty:TypeId, mutability, drop_flag}>`、`basic_blocks:Vec<BasicBlock>`、`start:BlockId`、`node_count:u64`、`source_map:SpanMap`、`unwind_policy:UnwindPolicy`。每个 `BasicBlock` 是 `statements:Vec<Statement>` 加一个 `terminator:Terminator`；`Place` 由 local 与字段/索引/deref projection 组成；`Rvalue` 只能读取已初始化 place。`node_count` 必须等于所有 statements、terminators、operands 和 projections 的计数，超过 Profile 上限拒绝 lowering。

Verifier 必须检查：所有 BlockId/LocalId/TypeId 有界且存在；CFG 从 start 可达部分终止或显式 loop；每个 block 恰有一个 terminator；move 后 place 不可读；借用区域不跨越 owner drop；所有可能退出路径执行初始化资源的 Drop 一次；panic/unwind edge 与 `unwind_policy` 一致；调用参数和返回类型匹配；不允许悬空 raw pointer 进入 safe MIR。违规返回带 `invariant_id:String`、`span:Span`、`path:Vec<BlockId>` 的 `X-E-MIR-001`。

## 变换接口

`MirPass::run(input:&MirBody, ctx:&PassContext)->Result<PassOutput,PassError>`：前置为 input verifier 通过、Pass 版本匹配；后置为 output verifier 通过且 source map 可回溯；错误不替换 input。`PassOutput` 字段为 `body:MirBody`、`changed:bool`、`stats:PassStats`、`proof:ProofSummary`。Pass 在每个 block/循环头检查 `CancelToken`；30 s、256 MiB 仅为 `ci` Profile 的 `candidate_default`，遵循 [编译器 Budget 治理](./README.md#资源预算治理)，超限返回 `X-E-PASS-001`。

## 解释器与差分

MIR interpreter 只执行已验证 MIR，显式模拟布局、整数溢出、Drop、panic 和资源配额；它不是第二套 parser/type checker。`interpret(body, input, profile)->Result<Value,ExecError>` 的结果与 O0 backend 在可观测边界进行差分。未定义行为、平台定义浮点和外部 I/O 必须被标记为不可差分，而不是猜测。

## 负向测试、版本与回滚

规划测试为 `TEST-COMPILER-IR-001`、`TEST-COMPILER-IR-002`、`TEST-COMPILER-IR-003`，状态均为 `planned`：分别覆盖断 CFG/重复 Drop、未知 schema/截断、parse-print-parse 与 O0/interpreter 差分。IR schema minor 只加可选字段，major 读取拒绝并返回迁移建议；Pass 回归时按 Pass ID 禁用并回退输入 MIR/O0，保留规划中的 verifier 报告类型与 perf 数据类型，不伪造已有证据。
