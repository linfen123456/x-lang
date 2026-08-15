---
doc_id: DOC-COMPILER-FRONTEND-ALGORITHMS
authority: implementation
owner: role/compiler-team
backup_owner: role/language-team
version: "1.0"
maturity: CORE
status: 草案
phase: P1
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-002, XLF-01-006, XLF-01-010, XLF-02-002, XLF-02-004, XLF-02-012, XLF-11-005, XLF-11-013]
---
# 编译器前端算法与任务拆分

> 本文把[前端接口基线](./frontend.md)展开为可实现的算法和任务切片。字段与公共错误结构以[编译器公共接口](./interfaces/contract.md)为准，语法语义以[语言核心规范](../specs/language-core.md)为准。本文不宣称实现、测试或性能结果已经存在；全部测试与证据均为 `planned`。

## 1. 目标、非目标与完成边界

目标是为 `SourceManager → Lexer → Parser → Resolver → TypeChecker/TraitSolver → TypedHirModule → HirVerifier` 给出确定的数据流、终止条件、错误恢复、取消点和资源上限，使工程人员无需重新决定基本算法即可拆卡实现。

本阶段不做以下事项：

- 不在前端执行借用检查；借用检查以 MIR 的 `Place/MovePath/Loan/PointId` 为输入。
- 不稳定 `async/await`、宏系统、Effect 或任意编译期执行；未通过对应 RFC 时只产生 feature-disabled 诊断。
- 不为 IDE 另写一套语法或类型系统；LSP 复用错误容忍前端。
- 不以恢复 AST 生成可执行制品；`release` 路径要求零阻断诊断。
- 不把 tree-sitter 设为权威 Parser；其是否用于编辑增量解析由独立 ADR 比较。

完成定义：同一源码、Edition、Feature、Target-independent 配置产生确定的 Token/AST/DefMap/TypeTable/TypedHirModule/VerifiedHirModule；非法输入有界终止；取消、超限和内部错误不提交成功缓存；每个诊断有稳定错误码与原始 Span。

## 2. 端到端数据模型

| 产物 | 必需字段 | 生产者 | 消费者 | 可含错误节点 |
|---|---|---|---|---|
| `FileSnapshot` | `snapshot_id,file_id,version,bytes,line_starts,encoding,origin,fingerprint` | SourceManager | Lexer、诊断 | 否；非法编码保留原字节 |
| `TokenStore` | `tokens,trivia,eof,file_id,snapshot_id,diagnostics` | Lexer | Parser、Formatter | 是；使用 `Unknown` token |
| `SyntaxTree` | `green_root,token_coverage,synthetic_tokens,error_nodes` | Parser | AST builder、Formatter | 是 |
| `AstFile` | `items,node_spans,attrs,error_nodes` | AST builder | Resolver | 是 |
| `DefMap` | `modules,scopes,defs,imports,visibility,diagnostics` | Resolver | TypeChecker、LSP | 是；未解析名不生成伪 DefId |
| `TypeTable` | `expr_types,pattern_types,coercions,obligations,diagnostics` | TypeChecker | TraitSolver、HIR lowerer | 使用唯一 `Ty::Error` |
| `TypedHirModule` | `bodies,def_map,type_table,source_map,feature_set` | HIR lowerer | MIR builder | 仅 LSP 模式可保留 poison body |

所有 arena ID 都是 `index + generation` 或受所属工件生命周期约束的整数。跨 snapshot 使用 ID 必须被 verifier 拒绝。字符串驻留器保存原文和规范化比较键，但诊断始终展示原文。

## 3. SourceManager 实施算法

### 3.1 加载与快照

`load(path, workspace, cancel)` 按以下顺序执行：

1. 打开 workspace 根目录句柄并记录根身份；将用户路径拆成不含 `..`/NUL 的相对 components，不把字符串 `canonicalize` 结果当作授权依据。
2. 通过目录句柄逐段打开（Linux/Unix 使用 `openat`/等价 no-follow 策略；Windows 使用受限 CreateFile handle），取得最终文件句柄后查询最终路径与稳定文件身份，再验证它仍属于授权根且不是目录/设备。验证和读取使用同一已打开句柄，避免检查后替换的 TOCTOU。
3. 从已验证句柄读取元数据并拒绝超过 Profile 上限的输入；以只读方式分块读取，每个 1 MiB 或一次系统调用后检查取消。
4. 保留原始 bytes；验证 UTF-8，但不得以替换字符改变 offset。
5. 单次线性扫描构建 `line_starts`，接受 `LF` 和 `CRLF`，并记录原始换行种类供格式化器使用。
6. 对语义输入计算指纹；mtime 只能作为快速失效提示，不能作为内容等价证据。
7. 构造不可变 `FileSnapshot`，成功后才发布到 snapshot 表。

编辑器内存文档走 `apply_changes(base_version, changes)`：先验证版本严格递增、区间不重叠且 UTF-16/UTF-8 position encoding 已协商，再生成新 rope/chunk snapshot。旧 snapshot 只读存活到引用归零，不能原位改写。

### 3.2 位置映射

`byte_offset → (line,column)` 先二分 `line_starts`，再按协商编码计算列；Span 使用半开区间 `[start,end)`。offset 位于 UTF-8 continuation byte、超过 EOF 或跨 FileId 时返回 `X-E-SOURCE-001`，不得截断纠正。行列仅为展示数据，语义缓存使用字节 Span。

## 4. Lexer 的确定有限状态扫描

### 4.1 状态与游标

游标结构为 `Cursor{bytes,pos,token_start,state,nesting,cancel_counter}`。最小状态集：

```text
Default | Identifier | Number(base,seen_dot,seen_exp)
String(quote,escape,raw_hashes) | Char(escape)
LineComment | BlockComment(depth) | OperatorPrefix
```

主循环每次必须消费至少一个字节或结束；这是防止坏输入死循环的核心不变量。标识符规范化只用于比较，不修改 token 文本。最长匹配仅用于已在语言规范登记的运算符；未知前缀生成一个最短 `Unknown` token 后继续。

### 4.2 Token 扫描顺序

1. 消费空白与注释为 trivia；P1 可移植基线允许嵌套块注释并保证至少 128 层，参考实现固定 `MAX_BLOCK_COMMENT_DEPTH=128`，第 129 层产生 `X-E-LEX-COMMENT-DEPTH` 并有界同步。改变上限必须走 Edition/RFC，Profile 不得降到 128 以下。
2. 识别标识符/关键字；关键字表由 Edition 版本化，不能散落在 Parser 中。
3. 扫描数值前缀、数字、分隔符、小数点、指数与 suffix；Lexer 只验证词形，范围和精度交给类型检查。
4. 扫描字符串/字符；raw string 词形只在 `raw-string` Feature 开启时接受，P2/RFC 冻结前同样扫描完整词形但产生 `X-E-FEATURE-RAW-STRING`，避免 Parser 级联。转义失败产生局部诊断并同步到当前引号、换行或 EOF。
5. 按最长匹配扫描标点与运算符。
6. 发出唯一 EOF，验证 token 区间单调、不重叠且 trivia 覆盖间隙。

未闭合字符串不得吞掉后续整个文件：普通字符串在不允许裸换行时于换行处结束错误 token；raw string 只在匹配 hash 数的结束符或 EOF 停止。数值如 `1__2` 保留为单 token 并附词形诊断，避免 Parser 产生级联错误。

### 4.3 增量边界

P1 先实现全文件线性 lex。P2 可按“安全重启点”增量扫描：从变更前最近的 Default 状态行首开始，直到新旧 token 序列及末状态连续匹配。块注释、raw string 或多行字面量内的修改必须向前扩展到其起点；无法证明状态等价时回退全文件扫描。增量结果必须与冷扫描 token-by-token 相同。

## 5. Parser、Pratt 表达式与错误恢复

### 5.1 语句/声明解析

顶层和块级结构使用递归下降。每个解析函数遵循统一返回：`Parsed(NodeId)`、`Recovered(NodeId,DiagnosticId)` 或 `Absent`。只有调用方确认 FIRST 集不匹配时可返回 `Absent`；消费 token 后不得静默返回 `Absent`。

列表解析使用 `parse_delimited(open, separator, close, element, recovery_set)`，集中处理尾逗号、缺失分隔符、EOF 和预算。模块、函数、类型、Trait、impl、控制流和模式的 FIRST/FOLLOW 集必须在测试夹具中固定。

### 5.2 Pratt 表达式算法

运算符表来自语言规范的版本化表项：`token,left_binding_power,right_binding_power,fixity,edition`。算法步骤：

1. 解析 prefix/atom 得到 `lhs`；失败时插入带 Span 的 `ErrorExpr`，保证前进。
2. 查看下一个 token 的 postfix/infix binding power；若左 binding power 小于调用方 `min_bp` 则返回。
3. 消费运算符；postfix 直接包裹 `lhs`，infix 以 `right_bp` 递归解析 rhs。
4. 构造节点并继续，直到同步符或优先级退出。

赋值和管道的结合性、短路运算的求值顺序、调用/索引/成员访问的最高优先级必须以黄金 AST 验证，不能只验证“解析成功”。Edition 改变运算符表时必须提升 parser table fingerprint。

### 5.3 错误恢复和预算

错误恢复分三级：

- 单 token 修复：仅对唯一预期的 `) ] } , ;` 插入 synthetic token，不移动源码 Span。
- 局部跳过：消费到当前产生式 FOLLOW 集或声明 FIRST 集，最多 `max_skip_tokens`。
- 项级同步：在 `}`、声明关键字或 EOF 恢复；生成一个覆盖被跳过 token 的 `ErrorNode`。

去重键为 `(diagnostic_code,primary_span,recovery_context)`。默认单文件错误预算 100、递归深度 256、节点 10,000,000；任一耗尽只追加一次 `X-E-PARSE-LIMIT` 并快速构造剩余错误节点。Parser 每创建 4096 节点或跨函数体边界检查取消。

### 5.4 CST 到 AST

Lossless CST 保留 trivia 与 synthetic token；AST 只保留语义结构。转换必须维护 `CstNodeId → AstNodeId?` 和反向 source map。synthetic 节点不能被当成用户声明进入导出 API。`parse → print original tokens` 必须字节保持；格式化输出的幂等性由格式化专题负责。

## 6. 名称解析与模块图

### 6.1 分阶段解析

Resolver 不进行字符串全局搜索，按四阶段执行：

1. **收集模块与 item header**：为模块、类型、函数、Trait 和常量分配稳定 `DefId`；函数体暂不解析名称。
2. **建立导入图**：规范化导入路径，区分显式导入、公开重导出、glob 和 prelude。
3. **求解导入**：对强连通分量进行固定点迭代；只有类型/声明可见性的环可保留，涉及初始化求值的环产生 `X-E-MODULE-001`。
4. **解析 body**：词法作用域从外到内查找 local、泛型参数、item、显式导入、公开导入、prelude；同级歧义不以顺序猜测。

命名空间至少区分 type、value、module、label、lifetime。可见性校验发生在找到候选之后，以便诊断“存在但不可见”而不是“找不到”。glob 导入应惰性展开并记录来源，用于冲突解释。

### 6.2 稳定性和增量失效

`DefPathHash = hash(package,module_path,item_name,namespace,disambiguator)`；源码位置不能作为跨会话稳定身份。`disambiguator` 优先使用 item kind、规范化签名/泛型 arity 和显式稳定属性的 header fingerprint；真正同名同签名项由重复定义诊断拒绝，诊断恢复使用的临时 ordinal 只在当前 snapshot 内有效，不进入跨会话 hash。新增私有函数不应改变无关公开 DefId。模块 public API fingerprint 改变才使依赖模块的名称/类型查询失效；仅函数体改变不重算无关导入图。

## 7. 类型推断、统一与约束求解

### 7.1 类型表示

`Ty` 至少包括 `Primitive`、`Tuple`、`Array`、`Slice`、`Struct`、`Enum`、`Ref`、`RawPtr`、`Fn`、`Param`、`InferVar`、`Never`、`Error`。类型驻留表进行结构哈希，避免重复深树。推断变量使用 union-find，并为每个根保存 `kind`、`binding?`、`lower/upper constraints` 和 origin Span。

### 7.2 单函数求解流程

1. 从签名、显式标注和泛型参数创建初始环境。
2. 按确定的语法遍历顺序为表达式生成等式、子类型/强制转换和 Trait obligation。
3. 用 occurs-check 的统一算法合并等式；禁止构造无限类型。
4. 处理允许的 coercion；隐式窄化、bool/int 互转、改变所有权的隐式复制直接报错。
5. 将 Trait obligation 送入 TraitSolver；`Ambiguous` 放入带依赖 InferVar 集合的 delayed queue，不立即报错。每次统一绑定相关变量时重新入队；函数最终化时按 canonical goal 排序重试一次，仍 Ambiguous 才产生 `X-E-TRAIT-001`。公开 `TypeCheckResult` 不得把未最终化 Ambiguous 当成功。
6. 对未约束数值变量应用规范默认类型；其他未约束变量产生需要标注的诊断。
7. zonk 所有类型，确保 TypedHirModule 不包含未解析 InferVar；错误位置统一为 `Ty::Error` 以抑制级联。

统一伪代码：

```text
unify(a, b, origin):
  a = shallow_resolve(a); b = shallow_resolve(b)
  if a == b: return
  if a is Error or b is Error: return
  if a is Var: bind_var(a, b, occurs_check=true); return
  if b is Var: bind_var(b, a, occurs_check=true); return
  if constructors differ: emit TYPE_MISMATCH(origin); return
  unify corresponding children in declared order
```

求解器必须有变量数、约束数和迭代次数预算；耗尽返回 `X-E-TYPE-LIMIT`，不得以 `Ty::Error` 伪装成功。

## 8. Trait Solver 与一致性检查

canonical goal 将局部 InferVar 替换为编号占位符，缓存键包括 Edition、Feature、solver version 和可见 impl fingerprint。候选流程：

1. 收集当前模块可见、Trait/类型允许的 impl。
2. 用 head type 快速筛选，再实例化泛型并统一。
3. 将 where-clause 转为子目标，使用深度优先或工作队列求解。
4. 用 active-goal 栈检测递归；允许的 coinductive goal 必须由 RFC 明确，否则为 overflow/ambiguous。
5. 对全部成功候选执行一致性/特化排序；没有候选为 `NoSolution`，多个不可排序候选为 `Ambiguous`。`NoSolution` 可立即诊断；`Ambiguous` 遵循上一节 delayed queue/finalization，禁止另一路径立即诊断。

孤儿规则、overlap 和特化当前都是待正式语言决策的高风险点；在规则冻结前实现只能处于 gate 后。默认深度 128、候选 10,000、单 goal 迭代 100,000。诊断应展示最小 obligation 链，不输出全部候选导致日志耗尽。

## 9. Typed HIR Lowering

HIR lowering 只接受已完成的 `DefMap + TypeTable + obligation result`。顺序为：

`HirBody` 是单个 owner 的有类型但尚未验证 body；`TypedHirModule` 聚合多个 `HirBody`、DefMap、TypeTable 与 module source map；`HirVerifier` 对整个 module 及每个 body 检查后生成名义包装 `VerifiedHirModule`，其中下游按 owner 取得 `VerifiedHirBody`。MIR Builder 只接受 `VerifiedHirBody`，不存在无定义的泛称 `VerifiedHir` 转换。

Lowering 顺序：

1. 将名称替换为 `DefId`，类型替换为 canonical `TypeId`。
2. 固化命名参数到声明顺序，同时保留参数名 Span 用于诊断；默认参数求值位置和顺序服从语言规范。
3. 展开管道、方法调用候选和语法糖，但保留 source map。
4. 将模式转为显式 pattern tree，并记录穷尽性输入。
5. 将闭包捕获先记录为 `CaptureCandidate`；最终 move/ref 形式在 MIR/借用阶段确认。
6. `?` 仅在 P1 的 CORE Result/Option propagation gate 开启且 `RULE-LANG-016` 冻结后生成语义节点；`defer` 仍属独立 RFC/Feature，未决时只产生 feature-disabled poison body。raw pointer 属 EXTENDED/P2，必须 `raw-pointer` Feature + unsafe/RFC-ABI-01；三者均不得因 Parser 已识别而绕过阶段门控。具体 Drop/unwind CFG 在 MIR lowering 完成。
7. 运行 HIR verifier：无未解析名称、无 InferVar、每个 HirId 唯一、Span 可回溯、禁用 feature 不出现对应节点。

`defer` 当前源自 `XLF-10-002` 且仍需 RFC；未决时 Parser 可识别以提供精确 feature 诊断，但不得 lower 为稳定 HIR。

## 10. 诊断、取消与资源耗尽

前端错误不得使用内部 arena 地址或 panic 文本。每条诊断包含 code、主 Span、必要的 secondary Span、简短原因和至多一个机器可应用 Fix-it；Fix-it 必须基于相同 snapshot version。错误码范围：

| 阶段 | 规划前缀 | 典型场景 |
|---|---|---|
| Source | `X-E-SOURCE-*` | 越权路径、坏 offset、非法编码 |
| Lexer | `X-E-LEX-*` | 未闭合字面量、非法转义、未知字符 |
| Parser | `X-E-PARSE-*` | 缺失 token、恢复/深度预算 |
| Resolver | `X-E-NAME-*`、`X-E-MODULE-*` | 重复、不可见、导入环 |
| Type | `X-E-TYPE-*` | 不匹配、无限类型、推断不足 |
| Trait | `X-E-TRAIT-*` | 无实现、歧义、overflow |
| HIR | `X-E-HIR-*` | lowering 或 verifier 不变量 |

取消检查点包括文件块读取、每 4K token、每 4K AST/HIR 节点、模块 SCC、约束工作队列和 Trait 候选循环。取消返回单一 `X-E-CANCELLED` 控制结果；不得把部分结果写入共享成功缓存。LSP 可以在请求仍有效时使用局部只读结果，但必须携带 snapshot version。

## 11. 分阶段实施任务

### 11.1 TASK-P1-COMP-001 / 切片 A：Source、Lexer 与稳定 Span

- 输入：语言词法表、workspace guard、Profile。
- 输出：`FileSnapshot`、`TokenStore`、行列映射、词法诊断。
- 依赖：`TASK-P0-COMP-001`。
- 验收：任意 bytes 有界终止；token 覆盖完整；冷扫描确定；取消无缓存提交。
- 回滚：关闭增量入口，仅保留全文件扫描。

### 11.2 TASK-P1-COMP-001 / 切片 B：CST/AST 与恢复 Parser

- 输入：TokenStore、EBNF/优先级表。
- 输出：lossless CST、AST、恢复诊断。
- 验收：合法语料 AST 黄金一致；非法语料诊断不爆炸；root 覆盖 EOF。
- 回滚：禁用新产生式 gate，使用上一 parser table fingerprint。

### 11.3 TASK-P1-COMP-002 / 切片 A：模块与名称

- 输入：AstFile、package/module graph、可见性规则。
- 输出：DefMap、导入解释、public API fingerprint。
- 验收：shadow、glob 冲突、不可见项和初始化环均有确定结果。
- 回滚：失效 DefMap namespace，重新冷解析，不改源码。

### 11.4 TASK-P1-COMP-002 / 切片 B：类型、Trait 与 TypedHirModule

- 输入：DefMap、类型/Trait 规范、FeatureSet。
- 输出：TypeTable、ObligationReport、TypedHirModule、VerifiedHirModule。
- 验收：无 InferVar 泄漏；歧义不猜测；禁用特性只产生门控诊断。
- 回滚：退回 AST-only diagnostics，禁用 HIR/codegen gate。

### 11.5 TASK-P2-COMP-001、TASK-P3-TOOLS-002 / 共享切片：增量与 IDE 容错

- 输入：旧/新 snapshot、QueryEngine、LSP deadline。
- 输出：可失效查询与带版本诊断。
- 验收：增量与冷路径语义相同；旧请求不能发布到新文档。
- 回滚：`--no-incremental` 全量前端。

## 12. 规划测试矩阵

| 测试 ID | 类型 | 场景 | 预期证据 | 状态 |
|---|---|---|---|---|
| `TEST-COMPILER-FRONT-001` | source/lexer | 句柄授权、坏 UTF-8、数值、raw-string gate、128/129 层注释 | token/诊断 golden | planned |
| `TEST-COMPILER-FRONT-002` | parser/fuzz | 产生式正反例、连续恢复、任意 bytes、取消 | AST/有界报告 | planned |
| `TEST-COMPILER-FRONT-003` | incremental | 编辑序列增量结果对比冷编译 | fingerprint diff | planned |
| `TEST-COMPILER-SEM-001` | name/type | shadow、glob、导入 SCC、occurs-check、coercion | DefMap/TypeTable dump | planned |
| `TEST-COMPILER-SEM-002` | trait | 单候选、NoSolution、延迟 Ambiguous、overflow | obligation/finalization trace | planned |
| `TEST-COMPILER-HIR-001` | verifier | 未解析 ID、feature 泄漏、module/body wrapper | verifier report | planned |

性能证据必须记录机器、OS、编译器版本、语料规模、冷/热路径和 P50/P95/P99；不得把原始资料中的“毫秒级”等目标写为验收事实。

## 13. 来源与待决策项

- `XLF-01-002`、`XLF-02-002`：Lexer/Parser/Semantic/HIR 全流水线。
- `XLF-01-006`：所有权入口，但实际 Borrow 算法归 MIR 专题。
- `XLF-01-010`、`XLF-02-012`：清晰显式语法与正式规范。
- `XLF-02-004`、`XLF-11-013`：增量前端、稳定诊断、Fix-it。
- `XLF-11-005`：管道、解构、命名/默认参数；其求值顺序仍须语言规则冻结。

待决策：Trait coherence/特化、默认参数求值、`defer`、宏/属性展开阶段、tree-sitter 角色、async 语法门控。任何一项未决都不得通过实现细节反向成为语言事实。
