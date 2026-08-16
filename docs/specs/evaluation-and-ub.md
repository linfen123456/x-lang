---
doc_id: DOC-SPECS-EVALUATION-UB
title: X-Lang 求值、数值、对象生命周期与未定义行为规范
authority: normative
owner: role/language-council
backup_owner: role/compiler-team
version: "0.1"
maturity: CORE
status: 待决策
phase: P1
last_reviewed: 2026-08-16
applies_to: [type-checker, hir, mir, optimizer, interpreter, backend]
traceability_scope: [XLF, XLC, XLE]
supersedes: []
---

# X-Lang 求值、数值、对象生命周期与未定义行为规范

## 1. 目的、权威边界与实现门禁

本文展开 RULE-LANG-009、RULE-LANG-012、RULE-MEM-004 和 RULE-MEM-005，解决 P0–P2 在 HIR→MIR、优化、解释执行和 LLVM 后端之间必须一致的可观察语义。语法与默认布局边界见[核心语言规范](./language-core.md)，借用、对象有效性和 Drop 基线见[内存与并发规范](./memory-concurrency.md)。冲突时，上述基础规则定义能力范围，本文定义执行细节；仍标“待决策”的策略不得进入 Stable 承诺。C ABI 与显式布局仍由[互操作规范](../ffi/README.md)和 RFC-ABI-01 管理，本轮不虚构尚不存在的独立 ABI 规范。

本章不引入新语法，不承诺 consteval、pure/effect、生成器、自动并行求值或任意 unsafe 行为安全。CORE 的目标是：同一合法程序在解释器、LLVM 和未来后端具有同一可观察结果；安全代码不能触发未定义行为（Undefined Behavior, UB）；优化只能利用本文明确列出的不变量。

实现 P1 前必须冻结 RULE-EVAL-001、RULE-EVAL-002 和 RULE-EVAL-003。P2 布局/借用验证前必须冻结 RULE-UB-001、RULE-UB-002 和 RULE-UB-003。整数 release 溢出和浮点快速模式若未通过 RFC-NUM-01，只能保留在非稳定实验 Profile。

## 2. 术语与可观察行为

- **求值（evaluation）**：表达式产生值、控制流或失败的过程。
- **副作用**：写内存、I/O、原子操作、资源获取/释放、日志、panic 等外部可观察变化。
- **临时值**：由表达式产生、未直接绑定名称但具有生命周期的值。
- **对象生命周期**：存储开始包含某类型有效值到该值被移动、Drop 或存储失效的区间。
- **无效值**：不满足其类型有效性不变量的位模式或状态。
- **UB**：规范不赋予程序任何结果的行为；只有 unsafe 契约违例或实现缺陷可以使其发生。
- **运行时失败**：有规定结果的越界、溢出、panic、abort 或 Result，不是 UB。

可观察行为至少包括返回值、标准 I/O、volatile/原子访问、FFI 调用、panic/abort、已规定的 Drop 次序和公开诊断类别。普通局部变量地址、默认结构字段偏移、padding 内容、优化次数和未承诺的浮点载荷不属于稳定可观察行为。

## RULE-EVAL-001：表达式、参数与赋值顺序

- maturity: CORE
- status: 待决策
- phase: P1

**规范性条文。** 在同一线程内，函数/方法的接收者先求值，实参随后严格按源码从左到右求值；索引表达式先求值容器，再求值索引；二元运算先左后右；赋值先确定左侧 place，再求值右侧，最后执行写入。普通表达式不得由优化器跨越具有可观察副作用的操作重排。赋值表达式的结果是否为 unit 由 RULE-LANG-005 的 AST 契约固定，不能由后端改变。

```x
fn main() {
    consume(record("first"), record("second"), record("third"));
}
```

上例必须依次记录 first、second、third。若 `record("second")` panic，third 不得求值，已经完成的临时值按 RULE-EVAL-003 清理。方法调用还必须在第一个显式实参之前求值接收者。

**反例。** LLVM 为提高寄存器利用率先执行第二实参的 I/O；复合赋值重复计算带副作用的索引；优化器把可能 panic 的除法移到前一个日志之前，均违反本规则。

**边界。** C/系统 ABI 只规定参数传递位置，不覆盖 X 源码求值顺序；进入 extern 函数前的实参仍按本规则。原子/volatile 还受并发模型约束。编译器可以重排经证明无可观察差异的纯计算，但证明不得假设尚未批准的 `pure` 标记。

**诊断与编译器影响。** 该规则通常无用户诊断；MIR lowering 必须为每个有序子表达式创建明确临时和控制流边。Verifier 检查 call 参数的定义支配 call；差分失败使用 X-I5101（编译器内部错误），不得归因用户程序。

**planned 测试/追溯。** TEST-EVAL-ORDER-001..012：调用、方法、索引、赋值、复合赋值、panic 中断、FFI 前置求值和 O0/O3 差分；来源 XLF-02-002、XLF-11-005、XLC-CORE-011、XLC-CORE-019；RFC-EVAL-01。

## RULE-EVAL-002：短路、分支、match 与循环

- maturity: CORE
- status: 草案
- phase: P1

**规范性条文。** `&&` 仅在左值为 true 时求值右侧；`||` 仅在左值为 false 时求值右侧。`if` 只求值被选择的分支。`match` 先一次性求值 scrutinee，再按源码顺序测试模式；模式成功后才求值该分支守卫，守卫为 false 时继续后续分支。选中 arm 后其他 arm 不求值。循环每次迭代按条件、主体、下一次条件的程序顺序执行； `break`、`continue`、`return` 立即转移到规定清理边。

```x
fn safe_divisor(value: i32) -> bool {
    value != 0 && 100 / value > 2
}
```

`value == 0` 时除法不得执行。match 守卫不得提前执行或跨 arm 合并，即使优化器认为表达式相同。

**反例。** 将 `a() && b()` 降低为无条件调用两者再按位与；为了并行而同时运行两个 if 分支；重复求值 match scrutinee，均违反本规则。

**边界。** Pattern usefulness 只影响静态可达性，不授权改变守卫次序；整数字面量/无副作用比较可合并，但 panic、Drop、原子和 FFI 都是障碍。未来并行表达式必须使用独立显式能力，不能改变 CORE 运算符。

**诊断与编译器影响。** 不可达模式由 X-W2402；常量 false 分支可 lint，但不得改变类型检查要求。MIR 以分支基本块表示短路，禁止先生成 eager 值再修补。

**planned 测试/追溯。** TEST-EVAL-CONTROL-001..014：短路、scrutinee 单次求值、守卫顺序、break/continue/return 和优化差分；来源 XLF-02-012、XLF-11-005、XLC-CORE-011；RFC-EVAL-01、RFC-PATTERN-01。

## RULE-EVAL-003：临时值、Drop、Result 与 panic 路径

- maturity: CORE
- status: 待决策
- phase: P1

**规范性条文。** 完整表达式中的临时值必须活到该表达式规定的清理点；函数局部按完成初始化的逆序 Drop，结构字段按声明顺序的逆序 Drop，数组元素按索引逆序 Drop。移动出去的 place 不再 Drop；部分初始化只 Drop 已初始化字段。`return`、`?` 的 Err 路径和 unwind 都沿显式 cleanup edge 执行适用 Drop；abort 不保证跨当前点的全局清理。正常控制流和 unwind 不得对同一值执行两次 Drop。

```x
fn write(path: &Path) -> Result<(), IoError> {
    let file = File::create(path)?;
    let buffer = Buffer::new();
    file.write(buffer.bytes())?;
    Ok(())
}
```

第二次 `?` 返回 Err 时，buffer 先 Drop，file 后 Drop。若 `File::create` 失败，file 从未初始化，不得 Drop。

**反例。** 把局部提前 Drop 到其最后一次普通读取之前；unwind 时遗漏 mutex guard；移动字段后仍 Drop 整个旧值；在 abort 文档中承诺所有文件缓冲已刷新。

**边界。** 临时生命周期延长、match 绑定和闭包捕获的精确 cleanup scope 必须由 MIR lowering 表记录并经 RFC-EVAL-01 冻结。`defer` 尚属 XLF-10-002 实验项，不改变当前 RAII 顺序。Drop 自身 panic 的二次失败策略见运行时规范。

**失败模式决策门。** `Result`/`?` 是普通控制流，不启动 unwind；panic 必须先完整求值其 payload，再进入 Profile 选择的 unwind 或 abort 路径。unwind 执行已建立的 cleanup，abort 不承诺进程级清理；`no_exceptions` 必须禁止生成隐藏 unwind 边，但“panic 一律 abort”还是“禁止可 panic 调用”仍由 RFC-ERROR-01 选择。`defer` 若通过 RFC，必须在语法位置、何时注册、与局部 Drop 的相对顺序、panic 中执行及 defer 自身失败五项全部确定后才能启用；本草案不自行选择这些答案。

**诊断与编译器影响。** 借用跨清理点冲突使用 X-E4002/4003；非法显式 Drop 使用由标准库 RFC 指定的诊断。MIR 必须含 drop flag，Verifier 验证每条退出边的“至多一次、仅已初始化”不变量。

**planned 测试/追溯。** TEST-EVAL-DROP-001..018：正常、return、`?`、panic unwind/abort、no_exceptions、部分初始化、部分移动、数组和二次 panic；来源 XLF-01-006、XLF-10-002、XLF-10-003、XLF-12-014、XLC-CORE-011、XLC-CORE-012；RFC-EVAL-01、RFC-ERROR-01。

## RULE-NUM-001：整数运算、移位、除法与溢出

- maturity: CORE
- status: 待决策
- phase: P1

**规范性条文。** 整数宽度固定；无符号值域为 `0..2^N-1`，有符号采用二进制补码值域。显式 `wrapping_*` 按模运算，`checked_*` 返回 Option/Result，`saturating_*` 饱和到边界。普通 `+ - *` 的 checked Profile 在溢出时产生规定 panic；Stable release 的普通溢出策略必须由 RFC-NUM-01 在“同样检查”或“明确 wrapping”中选择，任何 Profile 都不得把源语言普通整数溢出直接解释为 LLVM poison/任意 UB。

除数为零总是规定运行时失败；最小有符号数除以 `-1` 按普通溢出策略处理。移位量必须在 `0..N-1`，越界时按 checked 失败；需要掩码移位必须调用显式 API。位运算对固定宽度位模式操作，不做隐式整数提升。

**正例。** `u8::wrapping_add(255, 1)` 为 0；`u8::checked_add(255, 1)` 返回 None。

**反例。** 依赖 O0 panic、O3 任意结果；把 `let value: u32 = 1; value << 32` 静默当 `1`；有符号右移行为随宿主编译器变化。

**边界。** 字面量必须先通过目标类型值域检查；`isize/usize` 由 TargetSpec 指针宽度决定。decimal、任意精度整数、bitfield 和 SIMD 不属于 CORE 普通整数规则。

**诊断与编译器影响。** 常量越界 X-E2222；运行时溢出 X-R3001；除零 X-R3003；移位越界 X-R3004。MIR 使用语义化 checked/wrapping op，后端不得从优化等级反推语义。

**planned 测试/追溯。** TEST-NUM-INT-001..024：每宽度边界、除法、余数、移位、常量/运行时、O0/O3、LLVM/WASM 差分；来源 XLC-CORE-011、XLC-CORE-019、XLE-DATA-006；RFC-NUM-01。

## RULE-NUM-002：浮点严格模式、NaN 与转换

- maturity: CORE
- status: 待决策
- phase: P2

**规范性条文。** `f32/f64` 分别采用 IEEE 754 binary32/binary64。默认严格模式保持源程序规定的操作边界和舍入方向（初始候选为 roundTiesToEven）；NaN 与任何值的有序比较为 false，`NaN != NaN` 为 true；需要总序必须使用显式 `total_cmp`。编译器不得在严格模式假设 NaN/Infinity 不存在、重结合表达式、静默收缩为 FMA 或刷新 subnormal 为零。

快速浮点仅能是显式非 CORE Profile/局部能力，必须记录启用项，不能笼统使用“fast”。序列化需规定字节序和 NaN 规范化策略；普通内存转储不是跨平台格式。

**正例。** 严格模式下 `(a + b) + c` 不得重结合为 `a + (b + c)`；需要 FMA 时调用明确 API。

**反例。** 优化器用 `x == x` 恒真删除 NaN 分支；不同后端一个使用 FMA、一个不用却宣称严格结果一致；把 NaN payload 当稳定业务标识。

**边界。** 数学库超越函数的逐位一致性需要独立准确度规范；硬件不支持规定语义时使用软件回退或报告目标不支持。浮点到整数越界/NaN 转换必须用 checked API，普通 `as` 的精确策略在 RFC-NUM-01 决策前不得稳定。

**诊断与编译器影响。** 非法 strict/fast 组合 X-E2230；目标不能满足 strict X-E2231；快速模式产物必须带非稳定标记。MIR FP op 附带模式，后端能力矩阵验证 FMA、subnormal 和舍入。

**planned 测试/追溯。** TEST-NUM-FP-001..024：±0、Infinity、quiet/signaling NaN、subnormal、FMA、舍入、转换、序列化和跨后端差分；来源 XLC-CORE-019、XLE-DATA-006；decimal 扩展另见 XLF-10-004，不由本规则实现；RFC-NUM-01。

## RULE-UB-001：有效值、初始化与生命周期

- maturity: CORE边界
- status: 待决策
- phase: P2

**规范性条文。** 读取未初始化存储、把无效位模式当作类型值、访问生命周期已结束的对象、使用已移动 place、越界访问以及对未满足对齐的类型化指针解引用均违反语言规则。安全操作必须在执行这些行为前以静态错误或规定运行时失败阻止；若 unsafe 代码违反其证明义务，则为 UB。仅创建未解引用的 raw pointer 是否允许越界地址计算由 RFC-PROVENANCE-01 决定。

**有效性最低要求。** bool 只能表示 true/false；引用必须非空、对齐、指向生命周期内且满足别名权限的有效对象；函数指针必须指向兼容签名；枚举判别值必须有效；整数所有位模式有效。char、niche 和 SIMD 的完整有效集由对应 RFC/布局规则补齐。

**正例。** 安全数组索引先检查边界；MaybeUninit 类容器只有在所有字段已初始化后才能 `assume_init`，该调用必须 unsafe。

**反例。** 从零位模式构造引用；读取未初始化 padding 为整数值；释放后解引用；把任意枚举 tag 当合法变体。

**边界。** 分配的字节存在不等于某类型对象生命周期已开始；FFI 返回值进入安全世界前必须验证有效性。padding 可由内存工具复制，但不能作为已初始化业务值读取或比较。

**诊断与编译器影响。** 可静态证明的错误使用 X-E4101；解释器/UB 检测器使用 X-R4102 并报告分配、初始化、失效来源链。优化器可假设合法引用满足有效性，但只能在前端/unsafe 契约已定义后使用该事实。

**planned 测试/追溯。** TEST-UB-VALIDITY-001..020：未初始化、无效 bool/enum/ref、越界、use-after-move/free、padding 和 FFI 污染；来源 XLF-01-006、XLF-05-006、XLC-CORE-012、XLC-EXEC-002；RFC-ABI-01、RFC-PROVENANCE-01。

## RULE-UB-002：别名、引用权限与 provenance

- maturity: CORE边界
- status: 待决策
- phase: P2

**规范性条文。** 共享引用授予其生命周期内的只读访问，除非类型通过已批准的内部可变性原语；可变引用授予相应 place 的排他访问。raw pointer 不自动继承安全引用保证，但其解引用必须证明来源分配仍存活、地址在允许范围、对齐/初始化/类型兼容且访问不违反仍生效引用权限。整数不能凭数值相等自动恢复可解引用 provenance。

**地址暴露决策。** 为 FFI、分配器和设备地址，RFC-PROVENANCE-01 必须选择并定义 `expose_addr/from_exposed_addr` 类显式操作、可恢复范围及优化器限制；在此之前，整数往返仅允许穿过外部 ABI 的 opaque handle，不得在安全代码解引用。

**正例。** 从同一有效切片创建不重叠子切片并分别可变访问；C 返回 opaque 整数句柄只传回 C 销毁函数。

**反例。** 保留 `&mut value` 同时经 raw pointer 写 value；把地址整数加偏移后转回引用；分配释放后因地址被复用就认为旧指针重新有效。

**边界。** volatile 只约束访问发生，不修复 provenance、别名或数据竞争；原子只解决并发同步，不允许无效指针；MMIO、GPU/PMEM 地址空间需独立实验模型。

**诊断与编译器影响。** BorrowChecker 处理安全引用冲突；MIR 解释器跟踪 allocation ID、offset、权限与生命周期；后端 alias metadata 必须由已证明信息生成，不能仅凭语法 `&mut` 在 FFI 逃逸后过度假设。

**planned 测试/追溯。** TEST-UB-PTR-001..024：重借用、raw 逃逸、整数往返、释放复用、one-past、zero-sized、FFI、volatile；来源 XLF-05-006、XLF-06-009、XLC-CORE-012、XLC-CORE-013；RFC-PROVENANCE-01。

## RULE-UB-003：UB、规定失败与实现缺陷分类

- maturity: CORE治理
- status: 草案
- phase: P2

**规范性条文。** 规范和诊断必须区分：(1) 编译期拒绝；(2) Result/Option；(3) 规定 panic；(4) abort；(5) unsafe 契约违例导致 UB；(6) 编译器/运行时缺陷。安全源程序若通过编译后触发 UB，必须作为实现缺陷处理，不能反向宣称用户负有 unsafe 义务。资源耗尽、操作系统错误、除零、checked 溢出和边界检查失败都有规定分类，不是 UB。

| 情况 | 分类 | 实现责任 |
|---|---|---|
| 安全代码数组越界 | 规定失败 | 检查并 panic/返回已规定错误 |
| unsafe 解引用悬垂指针 | UB | 文档前置条件；检测器尽力报告 |
| 合法程序 O0/O3 结果不同 | 编译器缺陷 | 保留 IR 并阻断发布 |
| 分配失败 | Result/OOM 策略/abort | 不得构造空安全值 |
| 数据竞争 | 安全代码应静态阻止；unsafe 违例为 UB | 并发模型与 sanitizer 验证 |

**反例。** 把 LLVM `unreachable`、poison、inbounds 或 noalias 的行为原样当 X 用户规范；因后端方便把原本规定 panic 的错误改成 UB。

**诊断与编译器影响。** 用户错误使用稳定 `X-E/X-R`；实现不变量使用 `X-I` 并保留 Source→HIR→MIR→IR 最小证据。发布门禁必须运行 UB 语料、MIR 解释器与至少一个原生后端差分。

**planned 测试/追溯。** TEST-UB-CLASS-001..014；来源 XLF-01-001、XLF-01-006、XLC-CORE-012、XLC-CORE-019、XLC-EXEC-001、XLC-EXEC-002；RFC-UB-01。

## 3. 决策表、实现顺序与验收

| 决策 | P0/P1 安全默认 | 晋级 Stable 的证据 |
|---|---|---|
| 普通整数溢出 | checked Profile；release 不冻结 | 全宽度、O0/O3、LLVM/WASM 差分 |
| 浮点 | strict；fast 默认关闭 | NaN/subnormal/FMA 真机矩阵 |
| 临时/Drop scope | 显式 MIR cleanup | 正常、Result、panic、部分初始化测试 |
| provenance | 禁止整数恢复安全引用 | 解释器模型、FFI/allocator 用例、优化审查 |
| UB 分类 | safe code 不允许 UB | UB 语料无安全路径漏检基线 |

实现顺序：冻结求值顺序 → lowering 显式临时/cleanup → 整数语义 op → MIR 解释器 → 有效性/provenance 检查 → LLVM 映射与差分。任何后端不能表示安全语义时必须拒绝目标或使用回退，不能静默弱化。

验收输出：规范规则、MIR 示例、compile-pass/fail、runtime-fail、UB-negative、O0/O3 与跨后端差分报告。所有 `TEST-*` 当前均为 planned；在测试文件和 CI 证据实际存在前，本章不得标为“已验证”。
