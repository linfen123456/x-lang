# 02 类型系统、泛型与 Trait

> 类型：Spec｜唯一负责：原始类型命名、复合与名义类型、类型推断边界、泛型、Trait 最小集、内建 Trait、`@derive`、`const`/`static`、布局默认规则。

## 1. 结论

1. **原始类型名一律小写**：`i8…i128 isize u8…u128 usize f32 f64 bool char str never`。unit 类型的唯一写法是 `()`。用户类型和库类型用 `UpperCamel`（`String`、`Vec`、`Option`）。
2. 1.0 只有**静态分派**：泛型单态化。没有 `dyn`（保留字）。
3. Trait 最小集包括：方法（可带默认实现）、关联类型、泛型 bound、`where`、孤儿规则、禁止重叠。不支持特化、高阶 Trait bound、泛型关联类型。
4. 只能在公开边界写显式类型，推断只在函数体内进行。

## 2. 原始类型 [RULE-TYPE-LITRANGE]

| 类型 | 说明 | 实现的内建 Trait |
|---|---|---|
| `i8 i16 i32 i64 i128` | 二补码有符号整数 | Copy Clone Eq Ord Hash Default Display Debug Send Sync |
| `isize` | 指针宽度有符号整数 | 同上 |
| `u8 u16 u32 u64 u128 usize` | 无符号整数 | 同上 |
| `f32 f64` | IEEE 754 binary32/binary64 | Copy Clone Eq（IEEE 语义，NaN ≠ NaN）Default Display Debug Send Sync；**没有** Ord、Hash |
| `bool` | `true` / `false`，占 1 字节 | Copy Clone Eq Ord Hash Default Display Debug Send Sync |
| `char` | Unicode 标量值，4 字节 | 同 `bool` |
| `str` | UTF-8 字节序列，动态大小；只能以 `&str`、`Box<str>` 形式使用 | Eq Ord Hash Display Debug Send Sync |
| `()` | unit，零大小，唯一值为 `()` | Copy Clone Eq Ord Hash Default Debug Send Sync |
| `never` | 无值类型（`return`、`panic`、无限 `loop` 的类型），可强制转换为任意类型 | — |

规则：
- 原始类型名不可被重定义或遮蔽，否则报 `X-E2004`。
- 整数默认类型为 `i32`，浮点默认类型为 `f64`。
- 1.0 **没有** `Unit`、`Bool`、`I32` 等大写别名，用大写别名报 `X-E2010` 并给出 Fix-it。

## 3. 复合与名义类型

| 类型 | 写法 | 规则 |
|---|---|---|
| 元组 | `(A, B)`；单元素写作 `(A,)` | 字段 `.0`、`.1` |
| 数组 | `[T; N]`，`N` 为 `usize` 常量表达式 | 固定长度，按值存储 |
| 切片 | `[T]`，动态大小 | 只能以 `&[T]`、`&mut [T]`、`Box<[T]>` 使用 |
| 引用 | `&T`、`&mut T` | 见 [04](04-ownership-borrowing.md) |
| 原始指针 | `*const T`、`*mut T` | 见 [07](07-unsafe-ffi.md) |
| 函数指针 | `fn(A) -> R`、`extern "C" fn(A) -> R` | 不捕获环境，Copy |
| struct | `struct P { x: i32 }` | 名义类型；字段默认私有 |
| enum | `enum E { A, B(i32), C { x: i32 } }` | 带载荷的和类型 |
| 类型别名 | `type Id = u64;` | 不产生新类型 |

递归类型必须经过 `Box`、`Vec` 等间接层，否则报 `X-E3019` [RULE-TYPE-RECURSIVE]。

## 4. 类型推断边界 [RULE-TYPE-BOUNDARY] [RULE-TYPE-INFER]

1. 函数签名、struct 字段、const/static、Trait 方法签名、extern 签名都必须写显式类型。缺失报 `X-E3001`。
2. 函数体内的局部绑定、闭包参数、泛型实参可以推断，推断算法为局部合一（不跨函数）。
3. 推断不唯一或无法推断时报 `X-E3003`，并建议写类型注解或 `::<T>`。
4. 不做隐式数值转换，也不做用户定义的隐式转换。
5. 类型不匹配报 `X-E3004` [RULE-TYPE-MISMATCH]；实参个数不符报 `X-E3005` [RULE-TYPE-ARITY]；调用非函数值报 `X-E3006` [RULE-TYPE-CALLABLE]；字段不存在报 `X-E3007` [RULE-TYPE-FIELD]。

## 5. 泛型 [RULE-TYPE-GENERICARITY] [RULE-TYPE-MONOBUDGET]

```x
pub fn largest<T: Ord + Copy>(items: &[T]) -> T {
    var best = items[0];
    for (item in items) {
        if (*item > best) { best = *item; }
    }
    best
}

pub struct Pair<A, B> { pub first: A, pub second: B }
```

- 泛型参数只能是类型参数。const 泛型留待 1.0 后。
- 泛型实参个数不符报 `X-E3017`。
- 实现方式是单态化。每个包的实例数默认上限为 50,000（可在 `x.toml [profile]` 中调整）；超限报 `X-E3023`，并输出实例统计报告。

## 6. Trait [RULE-TRAIT-BOUND] [RULE-TRAIT-MISSING] [RULE-TRAIT-ORPHAN] [RULE-TRAIT-OVERLAP] [RULE-TRAIT-ASSOC] [RULE-TRAIT-ORD]

```x
pub trait Shape {
    fn area(self: &Self) -> f64;
    fn describe(self: &Self) -> String {          // 默认实现
        f"area = {self.area()}"
    }
}

pub trait Iterator {
    type Item;
    fn next(self: &mut Self) -> Option<Self::Item>;
}

impl Shape for Circle {
    fn area(self: &Self) -> f64 { 3.14159 * self.r * self.r }
}
```

规则：
1. **约束**：泛型 bound 和 `where` 子句中的约束必须被满足，否则报 `X-E3011`，并列出缺少的 impl。
2. **完整性**：impl 必须实现所有没有默认实现的方法和全部关联类型，否则报 `X-E3013` 或 `X-E3016`。
3. **孤儿规则**：`impl Trait for Type` 要求 Trait 或 Type 至少一个在当前包中定义；`Type` 的泛型外壳（如 `Vec<Local>`）不算本地类型。违反报 `X-E3014`。
4. **不重叠**：同一 Trait 的任意两个 impl 不得同时适用于同一类型。全覆盖式的 `impl<T: B> Tr for T` 只能写在定义 `Tr` 的包里。违反报 `X-E3015`。
5. **方法查找**：按 [06](06-modules.md) §9 进行。Trait 方法只有在 Trait 被导入或位于 Prelude 时才参与候选。
6. **运算符**：
   - 算术与位运算只作用于原始数值类型（不支持运算符重载）。
   - `==`/`!=` 对用户类型调用 `Eq::eq`；`<`/`<=`/`>`/`>=` 对用户类型调用 `Ord::cmp`。缺少实现时分别报 `X-E3011` 和 `X-E3012`。
   - 原始类型的比较是内建运算；浮点 `<` 按 IEEE 语义执行，不需要 `Ord`。
7. **Trait 对象**：1.0 不提供。

## 7. 内建 Trait（lang items）与 `@derive` [RULE-TRAIT-COPY] [RULE-TRAIT-DERIVE]

| Trait | 签名要点 | 阶段 | 可 `@derive` | 规则 |
|---|---|---|---|---|
| `Copy` | 标记 Trait，以 `Clone` 为父 Trait | P1 | 是 | 所有字段都是 Copy；不得同时实现 Drop（违反报 X-E4011） |
| `Clone` | `fn clone(self: &Self) -> Self` | P1 | 是 | — |
| `Drop` | `fn drop(self: &mut Self)` | P1 | 否 | 不得显式调用，用 `std::mem::drop(x)` 提前析构 |
| `Eq` | `fn eq(self: &Self, other: &Self) -> bool` | P1 | 是 | 驱动 `==`、`!=` |
| `Ord` | `fn cmp(self: &Self, other: &Self) -> Ordering`，父 Trait 为 `Eq` | P1 | 是 | 全序；驱动 `<` 等 |
| `Hash` | `fn hash(self: &Self, h: &mut Hasher)` | P1 | 是 | 必须与 `Eq` 一致 |
| `Default` | `fn default() -> Self` | P1 | 是 | — |
| `Display` | `fn fmt(self: &Self, f: &mut Formatter) -> Result<(), FmtError>` | P1 | 否 | 驱动 `f"{x}"` |
| `Debug` | 同上 | P1 | 是 | 驱动 `f"{x:?}"` |
| `Iterator` / `IntoIterator` | 见 §6 | P1 | 否 | 驱动 `for` |
| `Fn` / `FnMut` / `FnOnce` | bound 语法 `F: Fn(i32) -> i32` | P2 | 否 | 闭包自动实现，见 [03](03-expressions-patterns.md) §8 |
| `Send` / `Sync` | 自动 Trait | P2 | 否 | 见 [08](08-concurrency.md) |

`@derive` 规则：
- 只能派生上表中“可 `@derive`”的 Trait。字段未实现对应 Trait 时报 `X-E3018`。
- 生成的代码是确定的：`Eq` 逐字段比较；`Ord` 按字段声明顺序做字典序比较，枚举先比变体序号；`Hash` 按字段顺序哈希；`Debug` 输出 `Name { a: 1, b: 2 }` 形式。
- `@derive` 是闭集，不是宏系统。用户自定义派生留待 1.0 后的 RFC。

## 8. `const` 与 `static` [RULE-TYPE-STATIC]

| 项 | 写法 | 规则 | 阶段 |
|---|---|---|---|
| `const` | `const MAX: usize = 1024;` | 编译期求值，每次使用都内联一个副本；初始化器必须是常量表达式（见 [03](03-expressions-patterns.md) §9） | P0（字面量）/ P2（`const fn`） |
| `static` | `static COUNTER: AtomicU64 = AtomicU64::new(0);` | 全局唯一地址，不可变绑定；类型必须是 `Sync`；初始化器必须是常量表达式；不运行 Drop | P2 |

- 1.0 没有 `static mut`。可变全局状态必须用原子类型或 `Mutex`。
- static 初始化器不是常量表达式、或类型不是 `Sync`，报 `X-E3022`。
- static 之间的初始化形成环时报 `X-E2011`。

## 9. 布局

- 默认布局不作规定：编译器可以重排字段，不得依赖默认布局。
- `@repr(C)` 的布局与目标平台 C ABI 一致，见 [07](07-unsafe-ffi.md) §5。
- `Option<&T>`、`Option<Box<T>>` 保证与指针同宽（空指针优化）。
- `size_of<T>()`、`align_of<T>()` 由 `core::mem` 提供。

## 10. 规则与诊断

| Rule ID | 诊断 |
|---|---|
| RULE-TYPE-BOUNDARY | X-E3001 |
| RULE-TYPE-INFER | X-E3003 |
| RULE-TYPE-MISMATCH | X-E3004 |
| RULE-TYPE-ARITY | X-E3005 |
| RULE-TYPE-CALLABLE | X-E3006 |
| RULE-TYPE-FIELD | X-E3007 |
| RULE-TYPE-LITRANGE | X-E3009 |
| RULE-TRAIT-BOUND | X-E3011 |
| RULE-TRAIT-ORD | X-E3012 |
| RULE-TRAIT-MISSING | X-E3013 |
| RULE-TRAIT-ORPHAN | X-E3014 |
| RULE-TRAIT-OVERLAP | X-E3015 |
| RULE-TRAIT-ASSOC | X-E3016 |
| RULE-TYPE-GENERICARITY | X-E3017 |
| RULE-TRAIT-DERIVE | X-E3018 |
| RULE-TYPE-RECURSIVE | X-E3019 |
| RULE-TYPE-STATIC | X-E3022 |
| RULE-TYPE-MONOBUDGET | X-E3023 |
| RULE-TRAIT-COPY | X-E4011 |
