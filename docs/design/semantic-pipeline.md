# 语义管线实现设计

> 状态：Proposed｜日期：2026-08-18  
> 关闭：G2、`GAP-LANG-03`～`05`（P0/P1 可实现子集）  
> 规范权威：RFC-0006、RFC-0007、RFC-0008（均为 Proposed；本设计不提升其状态）  
> 编码落点：`compiler/src/semantic/*`、`compiler/src/ir/*`

## 1. 目的

RFC-0006/0007/0008 定义了**候选可观察规则**，但缺少可编码的判断步骤与数据结构。本文给出 Pass 顺序、核心 ADT、算法骨架与诊断映射，使实现者无需发明第二套语义。

**分层诚实性：**

| 层级 | 内容 |
|---|---|
| L0 P0 | 标量类型、函数、赋值 Place 检查、非 Copy 移动近似、`Result` 类型存在性 |
| L1 P1 | 名称解析、基础类型检查、`?` 脱糖、panic=abort、MIR Drop 插桩（无用户 Drop） |
| L2 P2 | 借用检查、字段级 init、用户 Drop、NLL 与 Drop 顺序约束 |
| L3 后续 RFC | Trait 一致性、完整 lifetime 语法、Provenance、并发模型 |

未进入当前层级的规则：实现必须 **诊断为未实现或拒绝**，不得静默错误接受。

## 2. Pass 流水线

```text
AST
  → P-Resolve     (DefId, scopes, imports subset)
  → P-Type        (TypeId, inference locals, Place classify, assignment)
  → H-Lower       (AST+types → HIR)
  → P-OwnerPrep   (move/copy candidate marks on typed HIR)
  → M-Lower       (HIR → MIR: BB, Place, Rvalue, Terminator)
  → P-ErrorLower  (? → EarlyReturn Err, panic Abort/Unwind exits)
  → P-Borrow      (P2+: loans, conflicts)
  → P-Init        (init/move flags on the complete CFG)
  → P-DropElab    (normal/return/?/unwind exits cleanup; abort makes no guarantee)
  → Verifier
  → Codegen
```

P0 可合并：`P-Resolve`（同文件）、`P-Type`（标量）、跳过 `P-Borrow`，`P-DropElab` 空操作，`P-ErrorLower` 仅识别非法 `?`。P1 引入 `?` 前必须先形成提前返回 CFG 边，再执行 Init/Drop 插桩。

## 3. 核心数据结构

### 3.1 类型与值

```text
TypeId        interned
TypeKind      = Scalar(I32|I64|Bool|Unit)
              | Struct(StructId)
              | Ref { mutability, pointee: TypeId }     // P1+
              | AdtResult { ok: TypeId, err: TypeId }   // library-core
              | ErrorType                               // 恢复用

PlaceRoot     = Local(LocalId) | Param(ParamId) | Static(StaticId) | Deref(PlaceId)
PlaceProj     = Field(FieldIdx) | Index(Operand) | Downcast(...)
Place         = { root, projs: [PlaceProj] }

TempId        表达式临时
Operand       = Copy(Place) | Move(Place) | Constant(Const)
Rvalue        = Use(Operand) | BinaryOp | Ref { mut, place } | ...
```

Assignment：AST 保留普通 `Expr`；`P-Type` 产出 `PlaceClass = WritablePlace | RvalueOnly`，非法写报 `X-E3008`。

### 3.2 所有权（P1/P2）

```text
MovePathId    每个可移动 Place 前缀
InitState     = Uninit | Init | Moved
Loan          = { id, kind: Shared|Mut, place_prefix, live_region }
BorrowError   → X-E4003 等
```

### 3.3 错误与终止

```text
Terminator    = Return | Goto | Switch | Call | Drop | Abort
              | EarlyReturn { payload: Operand }   // ? 脱糖
PanicStrategy = Abort | Unwind   // Artifact 级；P0/P1 仅 Abort
```

## 4. 算法骨架

### 4.1 局部推断（RFC-0006）

1. 公开签名位已写类型 → 直接 `TypeId`；缺省 → `X-E3001`。
2. 局部 `let`/`var`：若有注解用注解；否则从初始化式收集约束。
3. 使用 **局部** unification（Hindley-Milner 简化版即可）：仅当前函数体；禁止泛型/`impl` 远程候选。
4. 多解 → `X-E3003`；冲突 → 类型不匹配诊断（编号在 RFC 域内登记）。

溢出：P0 固定为 **调试与发布均 checked 或均 wrapping 之一**（默认 checked → panic=abort）；最终默认必须以 RFC 补丁冻结，本设计暂定 checked。

### 4.2 Place 与求值顺序（RFC-0006）

- 降低表达式时按源码左到右压入求值事件列表（供 MIR/解释器快照）。
- 复合赋值：`place` 地址计算一次 → 读旧值 → 求右值 → 写回。
- 优化 Pass 不得改变事件列表中的副作用顺序与 Drop Trace。

### 4.3 移动近似（P0/P1）

对非 `Copy` 标量结构体：

1. `Copy` 集合：P0 = `{i32,i64,bool,()}`；含 `i32` 字段的结构体若全字段 Copy 则 Copy。
2. `Operand::Move` 后将 `InitState` 标为 `Moved`；再读 → `X-E4001`/`X-E4002`。
3. 不实现字段级部分移动（P0）；用户 `Drop` 禁止（无该 trait）。

### 4.4 借用检查（P2，RFC-0007）

最小可实现版本（非完整 Polonius）：

1. 在 MIR 上构建 Loan 集合与 point-in-CFG 活跃性。
2. 冲突：同 Place 前缀上 `Mut` 与任意 Loan，或两个重叠 `Mut`。
3. 返回 `&`/`&mut`：逃逸分析——callee 局部 Place 不得出现在返回操作数；否则 `X-E4004`。
4. NLL：Loan 活到最后使用；**Drop 顺序仍按 RFC-0007 §4 逆序**，NLL 不得重排 Drop。

完整区域推断/显式 lifetime 语法：独立 RFC；P2 先支持「仅输入借用可返回」的省略规则。

### 4.5 `?` 与 panic（RFC-0008）

`?` 脱糖（同型 `E`）：

```text
match scrutinee {
  Ok(v) => v,
  Err(e) => { /* drop live locals */; return Err(e); }
}
```

- `E` 不等 → `X-E5001`；`Result`/`Option` 混用 → `X-E5002`。
- 无隐藏 `From`。
- P0/P1：`panic!` → `Abort` terminator；不生成 unwind landing pad。
- `extern "C"` 边界：若 MIR 显示可能 unwind → `X-E5003`（在引入 unwind 后启用）。

### 4.6 Drop 阐述（RFC-0007 §4）

1. `P-ErrorLower` 后遍历所有退出边；正常/return/`?`/允许 unwind 的边根据仍 `Init` 的本地插入 `Drop`；abort 不承诺 Drop。
2. 顺序：局部逆初始化序；结构体字段逆声明序。
3. P1 起为正常返回/`?`/abort 建立 MIR 快照；P2 增加用户 Drop、unwind 的运行 Trace 和随机 CFG 属性测试：保证清理的路径每个已初始化资源恰好 Drop 一次，abort 路径不作承诺。

## 5. 诊断映射表

| 阶段 | 代码 | Rule 前缀 | 触发 |
|---|---|---|---|
| Type | X-E3001 | RULE-TYPE-EXPLICIT | 公开边界缺类型 |
| Type | X-E3002 | RULE-TYPE-CAST | 非法 `as` |
| Type | X-E3003 | RULE-TYPE-INFER | 多候选 |
| Type | X-E3008 | RULE-EVAL-PLACE | 不可写 Place 赋值 |
| Own | X-E4001～4005 | RULE-OWN-* / RULE-DROP-* | RFC-0007 §5 |
| Err | X-E5001～5003 | RULE-ERR-* / RULE-TERM-* | RFC-0008 §4 |
| Impl | X-E9001（候选，D0 须在 RFC-0005 登记） | RULE-IMPL-UNIMP（候选） | 语法/语义未在本阶段实现；未登记前不能计入最终 P0 覆盖 |

所有诊断必须含主 Span；Fix-it 仅在确定安全时提供。

## 6. 与 MIR Codegen 的契约

| MIR 特性 | Codegen 义务 |
|---|---|
| `Move`/`Copy` | 按值传递；Moved Place 不再读 |
| `Drop` | 调用 Drop glue 或跳过（无 Drop 类型） |
| `Abort` | 进程 abort，不生成清理 |
| 求值事件 | `-Z dump-eval-trace` 可选；优化关闭时与解释器一致 |

## 7. 测试分层

| 层 | 内容 | 阶段 |
|---|---|---|
| 单元 | unification、Place 分类、InitState 转移 | P0 |
| compile-fail | X-E3001/3008、X-E4001、X-E9001 | P0/P1 |
| MIR snapshot | `?` 脱糖、Drop 顺序 | P1/P2 |
| run-pass Drop Trace | 正常/return/`?` | P2 |
| 解释器 vs LLVM 差分 | 同输入同可观察结果 | P1+ |

## 8. 明确延期（禁止偷偷实现）

- Trait 孤儿规则 / 一致性 / specialization；
- 完整 Pointer Provenance 与 Safe X 完备表（工程大纲 9.11）——P4 前仅文档清单；
- 并发 happens-before；
- `defer`（见 ADR-0003）；
- 用户自定义 `Drop` 的部分移动例外 API。

## 9. 验收

- [ ] 每个 L0/L1 Pass 有模块文件与单测；
- [ ] 诊断表中的 P0 代码均有 compile-fail 黄金文件；
- [ ] 文档声明的延期项在语料中有 `X-E9001` 或明确「阶段外」标记；
- [ ] 不与 RFC 正文冲突；若算法需改可观察规则，先改 RFC 再改本文。
