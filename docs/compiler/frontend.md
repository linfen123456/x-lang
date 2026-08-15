---
doc_id: DOC-COMPILER-FRONTEND
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-002, XLF-01-006, XLF-01-010, XLF-02-004, XLF-02-012, XLF-11-005, XLF-11-013]
---
# 前端、名称解析与语义分析

> 状态：草案｜Owner：`role/compiler-team`

## SourceManager、Lexer 和 Parser

`SourceManager::load(path:PathBuf)->Result<FileId,SourceError>` 只接受 workspace 授权路径，保留原始 bytes，不以替换字符修复非法 UTF-8。`FileId` 只在所属 `SnapshotId` 生命周期内有效；`FileSnapshot` 字段为 `snapshot_id:SnapshotId`、`file_id:u32`、`version:u64`、`bytes:Arc<[u8]>`、`line_starts:Arc<[u32]>`、`encoding:Utf8Status`、`origin:SourceOrigin`。旧 snapshot 在仍有 query/LSP 引用时保持只读，引用计数归零后才能回收；越界或跨 snapshot 使用返回 `X-E-SOURCE-001`。

`Lexer::lex(file:FileSnapshot, limits:LexLimits, cancel:CancelToken)->Result<TokenStore,DiagnosticSet>` 生成 `Token{kind:TokenKind, text_range:ByteRange, flags:TokenFlags}`；token range 不重叠且按字节递增，注释/空白可保存在 trivia。未知转义、未闭合字符串、非法 UTF-8 分别产生 `X-E-LEX-001`、`X-E-LEX-002`、`X-E-LEX-003` 并停止消费当前 token，不能吞掉后续文件。取消返回 `X-E-CANCELLED`，不写入成功 cache。

`Parser::parse(tokens:TokenStore)->ParseResult` 生成带 `NodeId:u32`、`SyntaxKind`、子节点序列和 token range 的 lossless tree，再转换 AST。恢复策略固定为：在同步集（`;`、`}`、声明起始关键字、EOF）前最多跳过 `max_skip_tokens`；插入虚拟 token 只能标记 `synthetic=true`；单个错误节点不重复报告同一 span。前置是 token 顺序合法，后置是 root 覆盖整个 token stream；深度、节点或错误预算耗尽返回 `X-E-PARSE-001`。

## AST/HIR 输入不变量

AST 节点字段至少为 `id:NodeId`、`span:Span`、`kind:AstKind`、`children:Vec<NodeId>`、`attrs:Vec<Attr>`；节点 span 覆盖子节点，列表保持源码顺序，标识符保存原文和规范化比较键。AST 允许缺失/错误节点但不能伪造语义成功。

名称解析按 `ModuleId -> ScopeId -> DefId` 建图。每个定义有 `name:Symbol`、`kind:DefKind`、`visibility:Visibility`、`span:Span`、`owner:ScopeId`；导入图必须无未处理初始化环。解析顺序是本地定义、显式导入、模块公开导入、预导入；同一命名空间重复定义返回 `X-E-NAME-001`，未解析返回 `X-E-NAME-002`，循环导入返回 `X-E-MODULE-001`。

## 类型、Trait 与借用（两阶段顺序）

类型表使用 `TypeId:u32`、`Ty::{Primitive,Tuple,Struct,Ref{mutability,lifetime},Fn,Param,Error}`。类型检查约束为 `Constraint{lhs:Ty,rhs:Ty,span:Span,origin:Origin}`，求解结果为 `TypeCheckResult{types:Map<ExprId,TypeId>, obligations:Vec<Obligation>, errors:DiagnosticSet}`。禁止隐式窄化、布尔/整数互转和未声明的错误吞噬；失败返回 `X-E-TYPE-001`。

Trait 求解输入 `Goal{trait_id:TraitId, self_ty:Ty, args:Vec<Ty>, depth:u16}`，输出 `Solved|Ambiguous|NoSolution|Overflow`。候选必须按模块可见性和特化规则确定排序；遇到 Ambiguous 不猜测，返回 `X-E-TRAIT-001`；深度/候选预算耗尽返回 `X-E-TRAIT-002`。缓存键包括 canonical goal、edition、feature set 和 solver version。

借用检查明确位于 `Resolver/Type/Trait → TypedHIR → MIR → Borrow` 的第二阶段，不参与 TypedHIR 生成。它以 `Place{local:LocalId, projections:Vec<Projection>}`、`Loan{kind,place,region,origin_span}` 和 CFG 上的 `PointId` 工作。前置是 MIR verifier 通过、locals 已有类型和 move paths；后置是每一处 read/write/drop 满足 loan graph，资源 Drop 只执行一次。冲突返回 `X-E-BORROW-001`，use-after-move 返回 `X-E-BORROW-002`；unsafe 边界必须带 capability/不变量注解。检查过程可并行按函数运行，但同一函数只产生一个提交版本。

异步语义不在默认 CORE lowering 中启用。`async-runtime` 是默认关闭的 feature gate，必须绑定 `RFC-ASYNC-001`（状态：待决策）和 `XSP-MEM-004`；RFC 未转为已决策前，`async/await/Task` 只允许产生 `X-E-FEATURE-ASYNC`，不能被当作稳定语言行为。

## 负向测试、Profile、版本与回滚

负向集包含非法编码、注释/字符串边界、连续错误恢复、重复定义、导入环、递归类型、trait overflow、可变/共享借用重叠、跨线程缺少 `Send`；规划注册项为 `TEST-COMPILER-FRONT-001`、`TEST-COMPILER-FRONT-002`、`TEST-COMPILER-FRONT-003`，状态均为 `planned`。`ci` 禁止错误恢复后的伪成功，`lsp` 可返回错误 AST 以支持编辑，`release` 只接受无错误 AST/HIR。Parser schema 通过 minor 追加字段，major 变化由版本协商；回归时切换旧 parser gate，保留旧诊断快照和最小复现。
