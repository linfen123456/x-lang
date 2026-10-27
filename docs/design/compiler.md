# 编译器设计（x-compiler）

> 状态：Accepted｜版本：2.1.0｜负责人：Compiler Lead｜最后更新：2026-10-22
> 类型：Design｜唯一负责：编译器内部数据结构、查询清单、驱动契约、代码生成约定、intrinsic 清单。系统边界见 [architecture](../architecture.md)，语言语义见 [specs](../../specs/language/01-lexical-syntax.md)。

## 1. 结论

1. 编译器是一个 rlib（`x-compiler`），对外只暴露 `driver` 门面：`check`、`build`、`run_interp`、`dump`、`query_db`。
2. 每个阶段都是纯函数，挂在查询数据库上（P0 用顺序调用模拟，P1 起改为真正的查询，见 [ADR-0005](../decisions/ADR-0005-query-compiler-and-lossless-cst.md)）。
3. 所有 ID 都是整数索引（`FileId`、`DefId`、`LocalId`、`BlockId`、`TyId`），不使用指针图。类型做 intern。
4. MIR 是唯一的中端 IR。借用检查、解释器、代码生成都读取同一份 MIR。

## 2. 模块与数据结构

| 模块 | 关键类型 | 说明 |
|---|---|---|
| `source` | `SourceDb`、`FileId`、`Span{file, lo, hi}`、`LineIndex` | 字节偏移；行列号按需计算（UTF-16 列号用于 LSP） |
| `diag` | `Diagnostic{code, severity, primary: Span, labels, notes, fix: Option<Fix>}` | 只能通过 `diag::emit` 发出诊断；`code` 必须在[诊断登记册](../../specs/diagnostics/registry.md)中登记 |
| `syntax` | `SyntaxKind`、`GreenNode`、`SyntaxNode`、AST 包装类型 | 无损 CST；带错误恢复，用同步集合 `; } ) fn struct enum impl use` 跳过；`syntax::tree` 封装 `rowan` 0.17 |
| `hir` | `Item`、`Body`、`Expr`/`Pat`（arena）、`DefId`、`DefMap` | 去掉语法糖：`for` → `loop+match`，`?` → `match`，f-string → `fmt` 调用 |
| `ty` | `Ty`（interned）、`TyKind`、`TraitRef`、`Obligation`、`TypeckResults` | 局部 HM 风格合一 + 整数/浮点字面量变量；Trait 选择不允许重叠，结果唯一 |
| `mir` | `Body{locals, blocks}`、`Place{local, projections}`、`Rvalue`、`Statement`、`Terminator` | 见 §4 |
| `borrowck` | `LoanSet`、`RegionInference`、`MoveData` | 位于 `mir` 子模块中，见 [04](../../specs/language/04-ownership-borrowing.md) |
| `interp` | `Machine`、`Allocation{bytes, init_mask, provenance}` | 见 [ADR-0006](../decisions/ADR-0006-mir-interpreter-oracle.md) |
| `codegen` | `Backend` trait；`codegen::llvm` | 只有 `codegen::llvm` 能引用 `llvm_sys` |
| `target` | `TargetSpec{triple, data_layout, pointer_width, endian, os, env, abi}` | 唯一的平台描述来源 |
| `driver` | `Session`、`Options`、`QueryDb` | 命令行解析放在 `x-cli` 中，driver 只接收结构化的 `Options`；`driver::db` 封装 `salsa` 0.28（P1 起；P0 是顺序调用） |

## 3. 查询清单（P1 起）

| 查询 | 键 → 值 | 失效条件 |
|---|---|---|
| `file_text` | `FileId → Arc<str>` | 输入（由外部设置） |
| `parse` | `FileId → (GreenNode, Vec<Diagnostic>)` | 文件文本变化 |
| `module_tree` | `PackageId → ModuleTree` | 文件集合或 `mod` 声明变化 |
| `def_map` | `PackageId → DefMap` | 任一 Item 签名或 `use` 变化 |
| `item_signature` | `DefId → Signature` | 该 Item 的签名文本变化 |
| `trait_impls` | `PackageId → ImplTable` | 任一 `impl` 头变化 |
| `typeck` | `DefId(body) → TypeckResults` | 该函数体或其依赖的签名变化 |
| `mir_built` | `DefId → Body` | `typeck` 变化 |
| `borrowck` | `DefId → BorrowResults` | `mir_built` 变化 |
| `mir_optimized` | `DefId → Body` | `borrowck` 通过且 `mir_built` 变化 |
| `const_eval` | `DefId(const/static) → ConstValue` | 依赖的 MIR 变化 |
| `mono_items` | `PackageId(bin) → Vec<MonoItem>` | 任一可达 MIR 变化 |
| `codegen_unit` | `CguId → ObjectFile` | 该 CGU 内的 MonoItem 变化 |

**不变式**：
1. 函数体内的修改只让本函数的 `typeck` 及其下游失效，签名不变就不触发其他函数重检。由“查询计数器测试”验证。
2. 查询不得读取环境变量、时间或文件系统；所有外部输入都必须作为输入查询注入。
3. 查询可以取消：LSP 编辑会触发取消，此时查询返回 `Cancelled`，不留下半成品。

## 4. MIR

```text
Body      = { params, return_local: _0, locals: [LocalDecl{ty, mutability, span}], blocks: [BasicBlock] }
BasicBlock= { statements: [Statement], terminator: Terminator }
Statement = Assign(Place, Rvalue) | StorageLive(Local) | StorageDead(Local) | SetDiscriminant(Place, VariantIdx) | Nop
Rvalue    = Use(Operand) | Ref(Shared|Mut, Place) | AddrOf(Const|Mut, Place) | BinaryOp(op, Operand, Operand)
          | CheckedBinaryOp(op, Operand, Operand) | UnaryOp(op, Operand) | Cast(kind, Operand, Ty)
          | Aggregate(kind, [Operand]) | Discriminant(Place) | Len(Place)
Operand   = Copy(Place) | Move(Place) | Constant(ConstValue)
Terminator= Goto(bb) | SwitchInt(Operand, [(value, bb)], otherwise) | Return | Unreachable
          | Call{func, args, dest: Place, target: Option<bb>} | Drop{place, target}
          | Assert{cond, expected, msg: PanicKind, target}
```

1. 溢出、除零、越界、移位越界一律 lower 为 `CheckedBinaryOp` + `Assert`，`PanicKind` 是封闭枚举（[03](../../specs/language/03-expressions-patterns.md) §4）。
2. MIR 校验器（P0 起）检查：类型一致、每个 Place 使用前都已 `StorageLive`、每个块都有终结符、`Move` 之后不再读取（P0 只检查局部变量）。
3. 优化遍（P1 起）：常量传播、死块消除、简单内联（`@inline` 或小函数）。优化必须保持 Drop 轨迹与 panic 位置不变，由 [testing](../testing.md) 中的差分测试守护。
4. `x dump mir <file> --fn <name>` 输出文本格式的 MIR，作为快照测试的输入（带 `schema_version: 1`）。

## 5. 驱动契约

1. [RULE-DRV-CLI] 命令行参数无效时，必须报 `X-E0003`，列出可接受的取值，退出码为 2。
2. [RULE-DRV-IO] 源文件不可读（不存在、权限不足、不是 UTF-8 由 X-E1001 处理）时，报 `X-E0002`，包含路径与 OS 错误文本，退出码为 1。
3. [RULE-DRV-LINK] 链接失败时报 `X-E0004`，附链接器的完整命令行与原始输出（`--verbose` 时显示全部，否则截取前 50 行）。
4. [RULE-DRV-ICE] 编译器内部 panic 时，必须捕获，报 `X-E0001`，并把复现包（源码、Options、编译器版本、backtrace）写到 `target/x-ice-<时间戳>/`，退出码为 101。ICE 不得表现为“静默成功”或无信息的崩溃。
5. 退出码：0 = 成功；1 = 用户代码诊断错误或 I/O 错误；2 = 用法错误；101 = ICE。
6. 诊断输出有两种格式：
   - 人类可读：`error[X-E3001]: 类型不匹配` + 源码片段 + 标签；
   - JSON v1：`--message-format json`，每行一个对象，字段 `schema_version, code, severity, message, spans[{file, byte_lo, byte_hi, line, col, label}], notes, fix`。
7. 在同一输入下，诊断顺序必须确定：按 (文件路径, 字节偏移, 代码) 排序。
8. 跨平台一致性（P0 双主机的前提）：诊断与 panic 消息中的路径，一律相对于当前工作目录或包根目录，并在所有平台上用 `/` 分隔；行号与列号按 Unicode 标量计数，与换行风格（LF 或 CRLF）无关。快照测试因此在 Linux 和 Windows 上逐字节一致。

## 6. 代码生成约定

1. 名称修饰：`_X` + 包名 + 模块路径 + 名称 + 泛型实参哈希（v0 方案，P1 定稿，可通过 `x demangle` 还原）。`@export("sym")` 不做修饰。
2. 调用约定：X 函数之间使用 LLVM `fastcc`（P2 前可以先用 `ccc`）；`extern "C"` 一律用 `ccc`。
3. 入口：xrt 提供 C 层的 `main`，调用 `xrt_start(argc, argv, x_main)`；`x_main` 由编译器生成，负责包装用户 `main` 的 `Result` 与退出码（[05](../../specs/language/05-errors-panics.md) §4）。
4. 调试信息：P0 生成行号表（`-g` 时），P1 生成局部变量信息，P3 为 DAP 提供完整 DWARF/CodeView。
5. 链接命令（P0）：
   - Linux：`cc -o <out> <obj> <libxrt.a> <native-static-libs>`；
   - Windows：`link.exe /NOLOGO /SUBSYSTEM:CONSOLE /OUT:<out>.exe <obj> xrt.lib <native-static-libs>`，`-g` 时加 `/DEBUG` 并生成 `.pdb`。
   `<native-static-libs>` 在构建 xrt 时用 `cargo rustc -- --print native-static-libs` 获取，写入 `xrt.link.json` 随工具链分发，不允许手写库名列表。
6. Profile：`dev = -O0 + debug`，`release = -O2`，`release-lto = -O2 + thin LTO`。三种 Profile 下溢出检查都开启（[ADR-0007](../decisions/ADR-0007-language-core-decisions.md) D18）。
7. 单态化预算：上限以 [02](../../specs/language/02-types-traits.md) §5 为准（每包 50,000 个实例）；另外，实例化递归深度超过 64 时也按同一规则报 `X-E3023`。

## 7. Intrinsic 清单（唯一来源）

`core`/`std` 通过 `@intrinsic` 声明的函数调用下表中的能力；用户代码不能直接使用 `@intrinsic`。

| Intrinsic | 签名（X 侧） | 实现 | 阶段 |
|---|---|---|---|
| `write_stdout` / `write_stderr` | `fn(bytes: &[u8]) -> isize` | xrt → PAL。Windows 上：如果句柄是控制台，就把 UTF-8 转成 UTF-16 后调用 `WriteConsoleW`（保证中文正常显示）；否则调用 `WriteFile` 原样写出字节。Unix 上调用 `write` | P0 |
| `abort` | `fn() -> never` | xrt | P0 |
| `panic_impl` | `fn(msg: &str, file: &str, line: u32, col: u32) -> never` | xrt：打印 `panic at file:line:col: msg` 后 abort | P0 |
| `exit` | `fn(code: i32) -> never` | xrt | P0 |
| `alloc` / `dealloc` / `realloc` | `fn(size: usize, align: usize) -> *mut u8` 等 | xrt 分配器钩子 | P1 |
| `size_of<T>` / `align_of<T>` | `fn() -> usize` | 编译器常量折叠 | P1 |
| `drop_in_place<T>` | `unsafe fn(p: *mut T)` | 编译器生成 drop glue | P1 |
| `args` / `env_get` | `fn(i: usize) -> Option<&str>` 等 | xrt | P1 |
| `fs_open/read/write/close`、`proc_spawn/wait` | 句柄式 | PAL | P1 |
| `clock_monotonic` / `clock_system` | `fn() -> u64` | PAL | P1 |
| `thread_spawn` / `thread_join` / `tls_*` | 句柄式 | xrt | P2 |
| `atomic_load/store/cas/fetch_*<T>` | 带 `Ordering` 参数 | LLVM 原子指令 | P2 |
| `include_str` / `include_bytes` | 见 [01](../../specs/language/01-lexical-syntax.md) §6 | 编译器 | P2 |

新增 intrinsic 必须同时完成三件事：修改本表；在解释器中实现，或标记 `interp: unsupported`；补充语料。

## 8. 性能内建手段

- 字符串与标识符做 intern；Arena 分配 HIR/MIR；类型用 `TyId` 比较。
- 并行：P1 起按 CGU 并行代码生成；P3 起并行类型检查（查询框架支持时）。
- 自身度量：`x build --timings` 输出每个阶段的耗时与查询命中率，供 [performance](../performance.md) 使用。
