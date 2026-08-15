---
doc_id: DOC-SPECS-TYPES-TRAITS-PATTERNS
title: X-Lang 类型推断、Trait 与模式规范
authority: normative
owner: role/language-council
backup_owner: role/compiler-team
version: "0.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
applies_to: [resolver, type-checker, trait-solver, exhaustiveness-checker, hir]
traceability_scope: [XLF, XLC]
supersedes: []
---

# X-Lang 类型推断、Trait 与模式规范

## 1. 目的、非目标与权威关系

本文细化 RULE-LANG-007、008、010、011，供类型检查器和符合性测试直接实现。词法、语法、数值运行时语义仍以[核心语言规范](./language-core.md)为准；所有权与 Place 以[内存与并发规范](./memory-concurrency.md)为准。

本版目标是局部类型推断、名义复合类型、显式 Trait 实现、有限且可终止的约束求解和枚举穷尽性。以下不在本版承诺中：结构化鸭子类型、运行时反射、任意高阶类型、特化、负向 impl、开放世界精确穷尽性、隐式数值窄化。Trait 对象、对象安全和高级关联类型在 RFC-TRAIT-01 决策前保持 feature gate。

## 2. 共同术语与输入输出

- **声明类型**：源码签名写出的类型。
- **推断变量**：类型检查器创建的未知量 `?Tn`，不得泄露到发布 ABI。
- **约束**：等价、子类型/强制转换、Trait obligation 或常量条件。
- **obligation**：形如 `T: Trait<Args>` 的待证明目标。
- **候选 impl**：在当前包图和可见规则下可能满足 obligation 的实现。
- **构造器**：枚举变体、元组、结构体、字面量区间或通配空间。
- **usefulness**：一个模式是否覆盖此前模式尚未覆盖的值。

输入为名称解析后的 AST、可见声明集合和目标配置；输出为 Typed HIR、每个表达式/模式的确定类型、选择的 impl、强制转换节点、诊断与未决 obligation 清单。类型检查成功时不得遗留无默认规则可解的推断变量。

## RULE-TYPE-001：类型身份、等价与可见别名

- maturity: CORE
- status: 草案
- phase: P1

**规范性条文。** 基础类型由规范名称标识；结构体和枚举是按“定义身份”区分的名义类型，即使字段相同也不等价；元组、数组、切片、引用、指针和函数类型按构成部分递归等价。`type Alias = T` 是透明别名，不创建新名义身份。类型比较必须在消除透明别名后进行，并检测别名循环。

**决策步骤。** (1) 解析类型路径；(2) 展开透明别名并记录访问栈；(3) 遇到重复别名报告循环；(4) 规范化泛型实参；(5) 按类型构造器和参数比较。编译器必须设置递归深度/工作量上限，并以资源诊断退出，不能栈溢出。

**正例。** `type UserId = u64; let id: UserId = 1;` 由显式声明确定字面量类型，别名与 `u64` 等价。

**反例。** `struct Metres { value: i32 }` 与 `struct Seconds { value: i32 }` 不可相互赋值。

**边界。** 不同包中同名结构体不是同一类型；Edition 不得改变已编译包导出类型的身份；数组长度属于类型组成部分。递归结构必须经 Box/引用等间接层，否则布局无限。

**诊断。** X-E2201 类型不匹配；X-E2202 循环别名；X-E2203 无限尺寸递归类型。诊断展示源码别名，并附规范化类型作为帮助信息，避免只输出内部 ID。

**编译器影响。** Resolver 为每个名义声明分配稳定 DefId；TypeInterner 缓存规范化结构；HIR 保留别名显示信息，MIR 使用规范化类型。

**planned 测试/追溯。** TEST-TYPE-EQ-001..008：别名、跨包同名、泛型参数、数组长度、递归和资源边界；来源 XLF-01-002、XLF-02-012、XLC-CORE-004；RFC-TYPE-IDENTITY-01（P1）。

## RULE-TYPE-002：局部推断、统一与默认化

- maturity: CORE
- status: 草案
- phase: P1

**规范性条文。** X-Lang 只保证函数体内的局部推断。公共函数参数、公共返回类型、公开字段和公开常量必须显式标注。推断不得跨包依赖函数实现细节。整数/浮点无后缀字面量可以延迟定型；若所有约束处理后仍无上下文，默认类型候选为 `i32`/`f64`，最终默认规则由 RFC-NUM-01 冻结。

**算法。**

1. 为未标注局部绑定和多态调用创建推断变量。
2. 自底向上为字面量、路径和复合表达式生成类型；自顶向下传入期望类型。
3. 为赋值、参数、返回、分支和模式生成等价/可转换约束。
4. 用 occurs-check 的统一算法求解等价约束；禁止 `?T = Vec<?T>`。
5. 将 Trait obligation 交给 RULE-TYPE-004；将强制转换交给 RULE-TYPE-003。
6. 重复处理因 impl 选择产生的新约束，直到固定点或工作量上限。
7. 对允许默认的数值变量执行默认化；其余不确定变量报告错误。
8. 将确定类型和显式 coercion 写入 HIR，并运行“无未解变量”验证器。

**正例。** `let byte: u8 = 1; let values = Vec::new(); values.push(byte);` 可由 `push` 将元素推断为 `u8`。

**反例。** `let values = Vec::new();` 在没有后续约束时不能凭空选择元素类型，应报告 X-E2211。

**边界。** 分支类型必须有唯一可接受的汇合；递归函数不能依赖函数体推断公开签名；闭包参数在无调用上下文时需要标注；错误恢复产生的 ErrorType 只能抑制级联诊断，不能让编译成功。

**诊断。** X-E2210 约束冲突，需同时标出约束两端来源；X-E2211 类型信息不足并建议标注；X-E2212 无限类型；X-R2213 Solver 预算耗尽。

**编译器影响。** 类型检查按函数体查询，结果依赖签名而非其他函数体；约束原因链必须可序列化供诊断和增量失效使用。

**planned 测试/追溯。** TEST-TYPE-INFER-001..012：局部、分支、闭包、递归、默认化、occurs-check、预算和诊断快照；来源 XLF-01-002、XLF-01-010、XLF-02-012、XLC-CORE-004；RFC-TYPE-INFER-01、RFC-NUM-01。

## RULE-TYPE-003：显式转换与有限强制转换

- maturity: CORE
- status: 草案
- phase: P1

**规范性条文。** 可能改变数值、符号、精度或所有权的转换必须显式使用 `as` 或标准库转换 API。CORE 仅允许以下隐式强制转换候选：`&mut T → &T`；具体数组引用到同元素切片引用；永不返回类型 `!` 到任意期望类型；函数项到匹配函数指针。自动解引用/借用仅用于已决策的方法接收者调整，不得组成无界搜索链。

**决策步骤。** 先尝试类型等价，再按固定优先级尝试唯一 coercion；若需要两条以上用户可见转换或存在多个结果，拒绝并要求显式写法。不得调用用户代码完成隐式转换。

**正例。** 接受 `&[u8]` 的函数可接收 `&array`，前提是元素类型一致。

**反例。** `let n: u8 = 300;` 不得截断；`let f: f32 = integer;` 不得隐式转换。

**边界。** raw pointer、FFI、枚举表示、decimal 与 SIMD 转换不属于 CORE coercion；不同生命周期的引用还须满足借用规则；转换不得延长引用生命周期。

**诊断。** X-E2220 不允许的隐式转换；X-E2221 转换结果不唯一；X-E2222 常量超出目标值域。Fix-it 只有在语义唯一且无信息丢失误导时才建议 `as` 或库 API。

**编译器影响。** HIR 必须显式记录每个 coercion 及规则 ID，MIR 不得重新猜测；差分后端必须得到一致类型。

**planned 测试/追溯。** TEST-TYPE-COERCE-001..010；来源 XLF-02-012、XLF-10-004、XLC-CORE-010；RFC-NUM-01、RFC-ABI-01。

## RULE-TYPE-004：泛型 obligation 与 Trait 求解

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** 泛型函数只能使用其声明约束保证的操作。满足 `T: Trait<Args>` 必须能找到唯一可用 impl 或由当前环境中的显式假设推出。没有显式 impl 的同名方法不构成 Trait 实现。CORE 采用保守的全局一致性：Trait 或 self 类型至少一个由当前包拥有；重叠 impl 在无法证明互斥时拒绝。

**求解流程。**

1. 规范化 obligation，并建立递归栈键 `(Trait, Self, Args)`。
2. 先检查当前泛型环境的假设，再枚举通过孤儿规则的候选 impl。
3. 用新推断快照匹配候选头部，生成 where/关联项子 obligation。
4. 递归求解；遇到相同或更一般目标时判为循环/歧义，不视为成功。
5. 零个成功候选为未满足；一个为选定；多个为歧义。
6. 提交唯一候选的替换和关联项，回滚其他快照。
7. 达到深度、候选数或步骤预算时报告资源限制，并提供最小 obligation 链。

**正例。** `fn sort<T: Ord>(items: &mut [T])` 内允许调用比较；调用点必须证明元素类型实现 `Ord`。

**反例。** 两个泛型 impl 均可匹配 `Vec<i32>` 时不得按声明顺序选择。

**边界。** 自动 Trait、负向 impl、特化、Trait object、对象安全、跨包新增 impl 的兼容性均待 RFC；编译器不得在未决情况下采用 Rust/C++ 的行为作为 X-Lang 事实。单态化是初始实现路线，但代码体积预算和跨 crate 共享不属于类型语义。

**诊断。** X-E2301 obligation 未满足；X-E2302 实现重叠；X-E2303 孤儿规则；X-E2304 选择歧义；X-R2305 Solver 预算。诊断列出被拒候选及原因，最多显示配置上限并提供完整日志入口。

**编译器影响。** impl 索引按 Trait/类型头部建立；选择结果进入 Typed HIR 与单态化键；增量指纹必须包含可见 impl 集合和 Trait 定义版本。

**planned 测试/追溯。** TEST-TRAIT-SOLVE-001..016：直接、泛型、where 子目标、缺失、重叠、孤儿、循环、歧义、预算、跨包失效；来源 XLF-01-008、XLF-01-010、XLF-02-012、XLC-CORE-004..009；RFC-TRAIT-01（P2）。

## RULE-TYPE-005：方法解析与接收者

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** 方法候选仅来自接收者类型的可见固有 impl 和作用域内可用 Trait。解析按有限接收者调整序列进行，初始建议为原类型、一次或多次内建解引用、再选择 `self`/`&self`/`&mut self`；精确 deref 上限和用户 Deref 是否进入 CORE 由 RFC 决定。同一优先级多个候选必须报歧义。

**正例。** 对 `&Point` 调用 `distance(&self)` 无需显式写 UFCS。

**反例。** 两个导入 Trait 为同一接收者提供同名同签名方法时，不得随机选择；要求限定路径调用。

**边界。** 接收者调整不得绕过可变性或移动规则；选择 `self` 方法会移动非 Copy 接收者；动态分派需 Trait object RFC。

**诊断。** X-E2310 未找到方法并列出接近候选；X-E2311 方法歧义；X-E2312 接收者会非法移动/借用。

**编译器影响。** HIR 将方法调用降低为选定 DefId 加显式接收者调整，后续阶段不再按名称查找。

**planned 测试/追溯。** TEST-TRAIT-METHOD-001..010；来源 XLF-01-010、XLF-02-012、XLC-CORE-006；RFC-TRAIT-01。

## RULE-PAT-001：模式类型检查、绑定与可达性

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** 每个模式由被匹配值的期望类型检查。构造器必须属于该类型；字段必须存在且不能重复；同一模式分支中绑定名唯一。绑定默认按值，是否复制或移动由字段类型决定；引用匹配人体工程学在 RFC 前不做隐式承诺。守卫在模式匹配成功后求值，守卫不得被用于证明穷尽。

**正例。** `Point { x, y }` 对 `Point` 值建立两个字段绑定。

**反例。** `Point { x, x }` 重复绑定；用 `Some` 匹配非 Option 类型；匹配已移动字段后再使用整个值。

**边界。** 原始 `..rest` 深度解构属于 XLF-11-005 候选，当前最小 EBNF 尚未定义；浮点 NaN 模式、字符串范围和用户自定义模式不在 CORE。

**诊断。** X-E2400 模式类型不匹配；X-E2401 非穷尽；X-W2402 不可达分支；X-E2403 非法/重复绑定。

**编译器影响。** 类型检查器输出 pattern matrix 所需构造器信息和绑定模式；借用检查器消费每个绑定的 move/borrow Place。

**planned 测试/追溯。** TEST-PAT-TYPE-001..010；来源 XLF-02-012、XLF-11-005、XLC-CORE-005；RFC-PATTERN-01。

## RULE-PAT-002：穷尽性与 usefulness 算法

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** 对 bool、枚举、元组、结构体和有限整数/字符构造器，编译器必须检查 match 穷尽性与分支 usefulness。守卫分支仅用于可达性提示，不计为无条件覆盖。带非穷尽演进属性的外部枚举必须要求通配分支；该属性语法待版本 RFC。

**算法。** 将已有分支模式展开为矩阵 `P`，对候选模式向量 `q`：按首列构造器专门化 `P` 与 `q`，递归判断是否存在尚未覆盖值；通配按当前类型的完整构造器集合展开。若候选无 useful witness，则分支不可达；所有分支处理后，以通配 `q` 查询 witness，存在则非穷尽并将最小 witness 展示给用户。整数范围先规范化为不相交区间，避免逐值枚举。

**正例。** bool 的 `true`、`false` 两分支穷尽；Option 的 Some/None 穷尽。

**反例。** 只有 `Some(_)` 必须报告缺少 `None`；在 `_` 后的任何无守卫分支不可达。

**边界。** 大整数范围使用区间集合并受预算限制；递归类型采用共享构造器描述避免无限展开；开放/外部枚举按非穷尽策略处理；预算耗尽不得误报为“已穷尽”。

**诊断。** X-E2401 必须给出至少一个缺失 witness；X-W2402 指向完全被覆盖的模式和先前覆盖分支；X-R2404 表示检查预算不足并使构建失败或由明确非稳定 Profile 控制，不能静默放行 Stable。

**编译器影响。** 检查在类型确定后、MIR lowering 前运行；lowering 可复用决策树，但优化不能改变守卫求值顺序。

**planned 测试/追溯。** TEST-PAT-EXHAUST-001..016：bool、枚举、嵌套元组、结构体、范围、守卫、不可达、外部枚举、递归和预算；来源 XLF-02-012、XLF-11-005、XLC-CORE-005；RFC-PATTERN-01。

## 3. 固定流水线、验收和待决项

推荐实现顺序：名称解析 → 类型身份/别名 → 表达式约束 → Trait 求解 → coercion 固化 → 模式 usefulness → Typed HIR 验证。发生前置错误时后续阶段可以恢复分析，但不能发布含 ErrorType、未解 obligation 或未选择方法的 HIR。

章节验收要求：每条规则至少有 compile-pass、compile-fail、boundary；Trait Solver 有循环和预算攻击语料；模式算法有 reference interpreter/穷举小域差分测试；诊断快照包含 Span、原因链和稳定代码；跨包增量测试验证新增 impl、变更 Trait 和 Edition 不会错误复用缓存。

待决 RFC：RFC-TYPE-IDENTITY-01、RFC-TYPE-INFER-01、RFC-NUM-01、RFC-TRAIT-01、RFC-PATTERN-01。它们未通过前，本文是实现对齐草案，不得标为“已稳定”。
