---
doc_id: DOC-COMPILER-IR-VERIFICATION
authority: implementation
owner: role/compiler-team
backup_owner: role/quality-team
version: "1.0"
maturity: CORE
status: 草案
phase: P1
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-003, XLF-01-006, XLF-02-002, XLF-02-004, XLF-10-002, XLF-10-003, XLF-12-014, XLF-12-020]
---
# HIR/MIR 验证器、Borrow 数据流与 Pass 证明义务

> 本文细化[HIR/MIR 实施规范](./hir-mir.md)，不重复其公共字段。语言内存语义以[内存与并发规范](../specs/memory-concurrency.md)为准，Backend 只接收本文定义的 `VerifiedMir`。所有测试、报告和基准均为 `planned`。

## 1. 目标与信任边界

验证器把“编译器内部应当成立”转换为可执行检查，阻止损坏 IR 进入优化、解释或代码生成。它不证明用户程序完全正确，也不替代类型系统或运行时安全检查。

信任边界如下：

```text
TypedHirModule(HirBody[]) --HirVerifier--> VerifiedHirModule(VerifiedHirBody[])
VerifiedHirBody --MirBuilder--> MirBody --StructuralVerifier--> StructuralMir
StructuralMir --Move/Borrow/Drop analyses--> BorrowReport
StructuralMir + BorrowReport --SemanticVerifier--> VerifiedMir
VerifiedMir --Pass--> MirBody --full verify--> VerifiedMir
VerifiedMir --Backend/Interpreter--> output
```

任何失败均返回原输入和 `VerifyReport`，不得发布新工件。Verifier 自身 panic、超时或资源耗尽属于编译器错误，不能降级为用户代码诊断后继续 codegen。

## 2. 版本化不变量目录

每个检查有稳定 `invariant_id`、严重度、适用 IR schema 和修复责任：

| 范围 | ID 前缀 | 例子 | 责任阶段 |
|---|---|---|---|
| HIR 结构 | `HIR-S-*` | ID 有界、owner 一致、Span 可回溯 | HIR lowerer |
| HIR 语义 | `HIR-M-*` | 无 InferVar、名称均为 DefId、feature 合法 | type/HIR |
| MIR 结构 | `MIR-S-*` | block/locals 有界、terminator 唯一 | MIR builder/decoder |
| CFG | `MIR-CFG-*` | successor 合法、cleanup edge 合法 | MIR builder/pass |
| 类型 | `MIR-TY-*` | operand/rvalue/call 类型匹配 | MIR builder/pass |
| move/init | `MIR-MOVE-*` | read 前初始化、move 后不可读 | move analysis |
| borrow | `MIR-LOAN-*` | alias、region、激活点合法 | borrow checker |
| Drop/unwind | `MIR-DROP-*` | 恰好一次、cleanup 路径完整 | drop elaboration |
| Pass | `PASS-*` | 保留 source map、声明分析失效 | optimizer |

新增检查只能追加 ID；改变含义须新增 ID 并废弃旧项。发布报告必须列出实际执行的 invariant set fingerprint，避免“同名 verifier、检查集合不同”。

## 3. IR 解码前防御

从缓存、插件或磁盘读入 IR 时先执行非递归的格式防御：

1. 检查 magic、schema major、producer、长度、checksum 和 source/target fingerprint。
2. 所有计数先验证乘加不溢出，再分配；拒绝声明 10 个节点却携带额外尾部数据的工件。
3. ID 仅解析为整数，不能在边界检查前索引 arena。
4. 字符串、Span map、projection 深度和总节点数受 Profile 限制。
5. 未知 enum variant 在 minor-compatible 扩展位可保留，否则拒绝整个 body。

这一步不解析用户语义，失败统一为 `X-E-IR-FORMAT` 并隔离缓存条目。不能尝试“修复”截断 IR。

## 4. HIR Verifier

### 4.1 结构检查

单次 arena 扫描建立 bitset，验证：

- `HirId`、`DefId`、`TypeId` 和 pattern 引用存在并属于当前 session/snapshot。
- body owner 与声明 owner 相同；参数 local 唯一且顺序与签名一致。
- source map Span 有界，synthetic 节点有最近用户源节点作为 origin。
- 表达式图无非规范共享；仅显式允许的 interned type/const 可共享。
- node_count 等于完整遍历计数，不允许隐藏节点逃避预算。

### 4.2 语义检查

- 不存在 `InferVar`、未解析字符串名称或未求解的阻断 obligation。
- 表达式 `TypeId` 与签名、pattern binding 和分支 join 类型一致。
- 禁用 Feature 对应的 HIR kind 不得出现。
- 管道、命名参数、默认参数和解构已经按语言规则降糖，且 source map 保留调用位置。
- `?` 与 `defer` 若 Feature/RFC 未启用，只能以 poison `HirBody` 存在于 LSP 工件，不能进入 `VerifiedHirModule`；raw pointer HIR 同样要求 EXTENDED/P2 的 `raw-pointer` Feature、unsafe 与 RFC-ABI-01。

HIR verifier 采用工作栈避免宿主调用栈溢出；每 4096 节点检查取消。

## 5. MIR 结构与 CFG 验证

### 5.1 基础结构

第一遍检查 locals、blocks、constants 和类型索引；第二遍检查每个 statement/terminator 引用。每个 block 必须有且仅有一个 terminator，terminator 后无 statement。start block 存在；unreachable block 可保留用于诊断或后续 DCE，但必须结构合法。

### 5.2 CFG 构造

对 terminator 生成 normal 和 cleanup 两类 edge：

- `Goto` 一个 normal successor。
- `SwitchInt` 的 value 集互斥并有 otherwise。
- `Call` 有 return edge；可 unwind 时另有 cleanup edge。
- `Drop` 有 normal edge；unwind policy 允许时有 cleanup edge。
- `Return/Abort/Resume/Unreachable` 无 normal successor。

算法用迭代 DFS 标记 reachable、计算 reverse-postorder，并检查 cleanup block 只能沿合法 cleanup/exit 边传播。`abort/no_exceptions` Profile 中不得出现 unwind/resume edge；`unwind` Profile 的潜在 panic 调用必须有明确 unwind action。

### 5.3 支配与循环

P1 可使用 Lengauer-Tarjan 或 Cooper 算法计算 dominator；选择需通过 ADR 和交叉测试。Phi/SSA 若尚未进入 MIR，不要求 SSA 不变量；进入 LIR/SSA 后，每个 use 必须被 def 支配，phi 输入与 predecessor 一一对应。自然循环之外的不可约 CFG 允许与否必须由 Pass 能力显式声明，不能让优化器隐式假定不存在。

## 6. Place、Projection 与类型验证

`Place = local + projections` 按投影逐步求类型：

```text
Field(i): base 必须为 tuple/struct/enum active variant，i 有界
Index(local): index 必须为整数，base 为 array/slice
ConstantIndex: offset/min_length/from_end 不溢出且相容
Deref: base 为 ref/raw pointer；raw pointer 标记 unsafe provenance
Downcast(variant): base 为 enum 且 variant 有界
Subslice: 范围与 base kind 合法
```

`Rvalue` 检查 operand ownership kind、算术类型、溢出策略、aggregate 字段顺序和 cast 白名单。transmute、raw deref、SIMD intrinsic 必须携带 unsafe capability 和 Target-independent 约束；目标 ISA 合法性留给 Backend 再验证。

调用验证参数数量、ABI、receiver、泛型实例、返回 place 和 unwind policy。变参只允许显式支持的 C ABI 边界。panic 不得跨未声明 FFI。

## 7. 初始化与移动数据流

### 7.1 MovePath 树

为可移动 Place 建立 `MovePath{place,parent,children}`。动态索引导致无法区分的部分按保守重叠处理；raw pointer 指向的别名不参与 safe 精确分析，而由 unsafe 契约承担。

每个 CFG point 对每个 MovePath 使用双 may-bit lattice `(may_init,may_uninit)`：`(1,0)=确定已初始化`、`(0,1)=确定未初始化`、`(1,1)=路径相关/可能初始化`、`(0,0)=不可达`。入口参数为 `(1,0)`，未初始化 local 为 `(0,1)`；赋值把目标及适用子路径转 `(1,0)`，move/Drop 转 `(0,1)`。父/子部分 move 通过 MovePath 树向祖先汇总为 `(1,1)`，不能把部分初始化误判为整个 aggregate 已初始化。

### 7.2 固定点算法

```text
worklist = reverse_postorder(blocks)
while worklist not empty:
  b = pop()
  in[b] = join(out[p] for p in predecessors[b])
  new_out = transfer_block(in[b], statements, terminator)
  if new_out != out[b]: push successors(b)
```

join 对两个 may-bit 分别取并集，形成有限高度 lattice 并保证单调收敛。safe read/drop 只接受 `(1,0)`；`(0,1)` 和 `(1,1)` 均拒绝，后者诊断分支相关的初始化路径。不可达 `(0,0)` 不产生用户诊断。循环迭代超过 `MovePath × CFG edge` 推导出的明确上限或 Profile 工作量上限时返回分析超限，而非接受近似成功。

## 8. Borrow Checker 输入与算法

### 8.1 Loan 与 region

每个借用产生 `Loan{loan_id,kind:Shared|Mutable,borrowed_place,issued_at,activation?,region,origin_span}`。两阶段借用是否进入 1.0 必须由语言规则决定；未决时不得默认为开启。

Region 约束至少包括：

- `live_at(region, point)`：引用值在 point 活跃。
- `outlives(r1,r2)`：r1 必须覆盖 r2。
- `contains_loan(region,loan)`：loan 在 region 内有效。
- `killed_at(loan,point)`：赋值、move、Drop 或 storage-dead 终止 loan。

P1 使用 CFG 点集/bitset 固定点即可；更高级的 NLL/Polonius 风格关系求解须独立性能验证。结果必须与规范语义一致，算法替换不能改变接受程序集。

### 8.2 冲突判定

Place overlap 规则按 projection 比较：不同 struct 字段可分离；动态数组索引保守重叠；union、raw deref 和内部可变性进入专门规则。访问矩阵：

| 已激活 Loan | Read | Write | Move | Drop |
|---|---:|---:|---:|---:|
| Shared | 允许 | 冲突 | 冲突 | 冲突 |
| Mutable | 冲突（借用自身访问除外） | 冲突 | 冲突 | 冲突 |

检查每个 MIR point 的访问与 live loans；诊断同时指向 loan origin、冲突访问和预计结束点。不得“自动插锁”修复数据竞争，这偏离核心静态所有权模型；可以给非自动应用的建议。

### 8.3 跨线程约束

`spawn` 捕获在 TypedHirModule 中标注候选，在 MIR 中完成 move/ref 分类。跨线程 move 要求 `Send` obligation 已解决；共享引用要求 referent `Sync` 且 region 覆盖 join/scope。detached task 不得借用栈 local。async gate 未通过时相关 MIR kind 不会进入 VerifiedMir。

## 9. Drop elaboration 与 panic 策略

为每个需要析构的 local 建 drop flag；初始化置位，move/Drop 清位。Drop elaboration 在所有 normal return、`?` 错误传播和 unwind cleanup 路径按逆声明/构造顺序插入 Drop。`defer` 若启用，按规范 LIFO 降为 guard/drop action，并明确与普通 local 的相对顺序。

Verifier 以状态数据流检查：

- 任一路径不对未初始化值 Drop。
- 同一所有权实例最多 Drop 一次。
- normal/unwind join 的 drop flags 一致或有显式条件 Drop。
- `abort` 路径不声称执行全局清理；它只验证到 abort terminator 为止。
- FFI 边界按声明 catch/abort，不能让 unwind 穿越不支持的 ABI。

`no_exceptions` 与 `abort` 不是同义词：前者禁止 unwind 并以显式错误控制流表达可恢复失败；后者是 panic 的进程终止策略。

## 10. Pass 合同与分析失效

每个 Pass 登记：`pass_id,version,requires,preserves,may_change_cfg,deterministic,feature_gate,resource_budget`。执行协议：

1. 验证输入满足 `requires`，并记录 input hash。
2. 在隔离的 builder/copy-on-write body 上执行，不原位覆盖已验证输入。
3. 检查取消、deadline 和节点增长预算。
4. 运行完整 verifier；不能只运行 Pass 自己挑选的检查。
5. 正式构建对全部 `preserves` 声明运行对应完整 verifier/analysis fingerprint 校验；不允许抽样作为接受证据。调试构建可额外抽样昂贵的内部自一致性检查，但抽样结果只辅助定位，不能替代第 4/5 步完整验证。
6. 生成 `PassReport{input_hash,output_hash,changed,stats,invariant_set,analysis_invalidated}`。
7. 成功后原子发布；失败回退 input VerifiedMir。

优化必须保留可观察行为：Result/panic 策略、Drop 次序、volatile/atomic、外部调用和浮点严格模式。只有语言/Profile 明确允许时才能采用 fast-math 或移除 panic check。

## 11. Interpreter 与 Backend 差分

MIR interpreter 是验证工具，不是生产语言的第二语义源。它支持的最小集合：整数/布尔/聚合、局部内存、分支/调用、move/Drop、Result/panic 模拟。外部 I/O、平台浮点、raw pointer 与并发必须返回 `UnsupportedForDifferential`。

差分用相同 input seed 比较：返回值、标准化诊断、Drop trace、panic outcome 和允许比较的内存摘要。解释器与 O0 Backend 不一致时阻断发布；不能通过修改 expected 结果掩盖差异。

## 12. 错误、资源与取消

`VerifyReport` 最少包含 `status,ir_hash,schema,invariant_set,violations,checked_nodes,max_worklist,cancelled,resource_usage`。违规路径限制为最短反例 block 序列，最多 64 个节点；更多内容以截断标志表示。

默认上限沿用架构 Profile：单函数 10M 节点、projection 深度 256、Verifier 30 秒/256 MiB（CI 可更严）。每个 block、工作队列批次和关系迭代检查取消。取消或超限不缓存 `VerifiedMir`；原始输入保留供诊断。

## 13. 实施任务切片

### TASK-P0-COMP-001、TASK-P1-COMP-003 / 切片 A：格式、HIR 与结构 MIR Verifier

- 输入：版本化 IR schema、恶意/截断 fixture。
- 输出：invariant registry、VerifyReport、StructuralMir wrapper。
- 验收：任意字节输入不越界/不无限分配；所有 ID 在索引前检查。
- 回滚：禁用磁盘 IR cache，只接受进程内 builder 产物但仍验证。

### TASK-P1-COMP-003 / 切片 B：CFG、类型和 move/init

- 输入：StructuralMir、TypeTable。
- 输出：CFG、MoveData、InitResults。
- 验收：断边、坏 terminator、use-after-move、条件初始化均有最小反例。
- 回滚：停止 codegen，不允许绕过检查。

### TASK-P1-COMP-003 / 切片 C：Borrow、Drop 与 VerifiedMir

- 输入：MoveData、region constraints、panic Profile。
- 输出：BorrowReport、DropTrace、VerifiedMir。
- 验收：借用/线程/Drop compile-pass/fail 与规范一致。
- 回滚：关闭尚未稳定的语言能力；核心 Borrow 检查本身不可旁路。

### TASK-P2-COMP-001 / 切片 A：Pass 门禁与差分

- 输入：VerifiedMir、Pass registry、Interpreter corpus。
- 输出：PassReport、O0/O2 和 interpreter 差分报告。
- 验收：单 Pass 可独立禁用；失败保持输入 hash 和行为。
- 回滚：`-O0 --no-incremental` 冷路径。

## 14. 规划测试

| 测试 ID | 覆盖 | 判定 | 状态 |
|---|---|---|---|
| `TEST-COMPILER-IR-001` | HIR/MIR 格式、CFG、类型、move lattice、Drop | invariant ID 与最短路径 | planned |
| `TEST-COMPILER-IR-002` | 截断/随机 bytes、Pass 前后完整 verifier、取消、节点爆炸、O0/O2 差分 | 拒绝且保留 input | planned |
| `TEST-COMPILER-BORROW-001` | shared/mutable、dynamic index、scope thread、region | loan origin/冲突/结束点 | planned |

## 15. 来源、验收与回滚总则

- 来源：`XLF-01-003`（HIR→MIR/LIR）、`XLF-01-006`（所有权/借用）、`XLF-02-002`（IR 全流水线）、`XLF-02-004`（增量与诊断）、`XLF-10-002/003`（defer 与 panic 策略）、`XLF-12-014`（no-exceptions）。
- 验收证据：fixture、compile-pass/fail、invariant registry、差分报告、资源报告，当前全部 `planned`。
- 性能声明遵循 `XLF-12-020`：只记录测量方法和候选预算，不承诺原始材料中的绝对数字。
- 回滚只能回到上一 VerifiedMir、关闭单个 Pass、冷编译或 O0；不得以 `--skip-verify` 作为用户可用回滚手段。
