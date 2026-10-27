# 03 表达式、求值顺序、算术语义与模式

> 类型：Spec｜唯一负责：Value/Place 模型、求值顺序、算术与转换语义、控制流、闭包、插值字符串、模式、常量求值、`@tailcall`。

## 1. 结论

1. **所有求值都从左到右，每个子表达式恰好求值一次。赋值时先确定左侧 Place，再求值右侧，最后写入。**
2. 整数溢出、除零、`MIN / -1`、移位量不小于位宽、越界索引，在**所有构建配置下**都会 panic。需要环绕或饱和运算时，显式调用 `wrapping_*`、`checked_*`、`saturating_*` 方法。
3. `as` 只允许无损或表示保持的转换。窄化转换必须用 `try_from` 或 `wrapping_from`。

## 2. 值的分类 [RULE-EVAL-PLACE]

| 类别 | 定义 | 例子 |
|---|---|---|
| Value | 已求值、可复制或可移动的值 | `1 + 2`、`f()` |
| Place | 一个存储位置：根（局部变量、参数、static、解引用）加投影（字段、元组下标、索引、解引用） | `x`、`p.x`、`t.0`、`v[i]`、`*r` |
| Temporary | 表达式产生的匿名存储，在**所在语句结束时**析构 | `&make()` 中的 `make()` |
| Constant | 编译期可求值的值 | `const` 项、字面量 |

临时值生命周期延长规则（唯一的一条）：`let r = &expr;` 或 `let r = &mut expr;` 中，如果 `expr` 是 Temporary，它的生命周期延长到包含这条 `let` 的块结束。没有其他延长规则。

赋值目标必须是可写 Place，否则报 `X-E3008`。函数调用结果、算术值、经共享借用得到的 Place 都不可写。

## 3. 求值顺序 [RULE-EVAL-ORDER]

1. 调用：先求值被调用者（或方法的 Receiver），再按从左到右求值实参，然后执行调用。
2. 二元运算：先左操作数，后右操作数。`&&`、`||` 短路，没有被选中的一侧不求值。
3. 结构体字面量、元组、数组：按**源码书写顺序**求值，与字段声明顺序无关。
4. 索引 `a[i]`：先 `a`，再 `i`，然后做边界检查。
5. **赋值 `place = value`**：
   - (a) 求值左侧 Place 的子表达式（基址、索引），并做边界检查；
   - (b) 求值右侧；
   - (c) 如果左侧原来已初始化，析构旧值；
   - (d) 写入新值。
6. **复合赋值 `place op= value`**：
   - (a) 求值左侧 Place（只求值一次）；
   - (b) 读取旧值；
   - (c) 求值右侧；
   - (d) 计算（溢出则 panic）；
   - (e) 写回。
7. `match` 的被匹配值只求值一次；模式中不含用户表达式。
8. 优化可以重排**不可观察**的操作，但不得改变：值、副作用顺序、panic 的发生点、Drop 顺序。

示例（`log` 会打印参数并原样返回它）：

```x
var v = [0, 0, 0];
v[log(0)] = log(1);       // 输出 0 然后 1
v[log(2)] += log(3);      // 输出 2 然后 3
```

## 4. 算术语义 [RULE-EVAL-OPERATOR]

| 运算 | 语义 |
|---|---|
| 整数 `+ - *` | 溢出即 panic |
| 整数 `/ %` | 除数为 0，或有符号 `MIN / -1`，即 panic；`%` 结果的符号与被除数相同 |
| `<< >>` | 移位量 ≥ 位宽即 panic；有符号 `>>` 是算术右移 |
| 一元 `-` | 只能用于有符号整数和浮点；`-MIN` 即 panic |
| `~` | 整数按位取反 |
| `!` | 只能用于 `bool` |
| 浮点 | 遵循 IEEE 754，默认舍入为就近偶数；不做 FMA 合并；不启用 fast-math |
| 显式方法 | `wrapping_add`、`checked_add -> Option<T>`、`saturating_add`、`overflowing_add -> (T, bool)`，减、乘、移位同样提供 |

运算符作用于不支持的类型时，报 `X-E3010`。

算术 panic 消息（封闭集合，测试按原文匹配；位置取运算表达式的起始位置）：

| 情形 | 消息 |
|---|---|
| `+ - *` 溢出 | `attempt to add with overflow`、`attempt to subtract with overflow`、`attempt to multiply with overflow` |
| `/ %` 除数为 0 | `attempt to divide by zero`、`attempt to calculate the remainder with a divisor of zero` |
| `MIN / -1`、`-MIN` | `attempt to divide with overflow`、`attempt to negate with overflow` |
| 移位越界 | `attempt to shift left with overflow`、`attempt to shift right with overflow` |
| 下标越界 | `index out of bounds: len {len}, index {index}` |

## 5. `as` 转换白名单 [RULE-EVAL-CAST]

| 源 → 目标 | 是否允许 | 语义 |
|---|---|---|
| 整数 → 更宽的同号整数；`u_N` → 更宽的 `i_M` | 允许 | 无损扩展 |
| `u8` → `char`；`char` → `u32`；`bool` → 任意整数 | 允许 | 表示保持 |
| 整数 → 浮点（值必定可以精确表示时，如 `i32 → f64`） | 允许 | 精确 |
| `f32` → `f64` | 允许 | 精确 |
| `&T` → `*const T`；`&mut T` → `*mut T` | 允许 | 取地址 |
| 窄化整数、有符号 ↔ 无符号同宽转换、浮点 → 整数、`f64 → f32`、`i64 → f64` | **不允许**（报 `X-E3002`） | 分别改用 `T::try_from(x)`、`T::wrapping_from(x)`、`x.to_i64_checked()`、`x.round_to_f32()` |
| 指针 ↔ 整数、指针类型之间互转 | 不允许 | 使用 [07](07-unsafe-ffi.md) 中的 unsafe API |

## 6. 控制流表达式

| 形式 | 类型规则 |
|---|---|
| `if (c) { a } else { b }` | `c: bool`；两个分支类型必须一致；没有 `else` 时类型为 `()` |
| `match (e) { p => x, ... }` | 所有分支类型一致；必须穷尽（§10） |
| `loop { ... break v; }` | 类型取 `break` 携带值的类型；没有 `break` 时为 `never` |
| `while (c) { }`、`for (p in it) { }` | 语句；`break` 不能携带值 |
| `return e` | 类型为 `never` |
| `{ s; e }` | 块的类型为尾表达式的类型；没有尾表达式时为 `()` |

`for (p in e) { body }` 的脱糖形式：

```x
{
    var __it = IntoIterator::into_iter(e);
    loop {
        match (Iterator::next(&mut __it)) {
            Some(p) => { body },
            None => break,
        }
    }
}
```

整数区间迭代用 `range(a, b)`（左闭右开）和 `range_inclusive(a, b)`，两者都由 `core` 提供，见 [std-core](../library/std-core.md)。

## 7. 插值字符串

`f"a{x}b{y:?}c"` 脱糖为向一个新建 `String` 依次写入：
- `"a"`；
- `Display::fmt(&x, ...)`；
- `"b"`；
- `Debug::fmt(&y, ...)`；
- `"c"`。

插值表达式按从左到右求值，结果类型为 `String`。1.0 不支持格式说明符（宽度、精度），需要时使用 `std::fmt` 中的函数。

## 8. 闭包 [RULE-OWN-CAPTURE]

```x
let k = 3;
let add_k = fn(x: i32) => x + k;           // 按共享借用捕获 k
var total = 0;
var acc = fn(x: i32) { total += x; };     // 按独占借用捕获 total
let owned = move fn() => name.len();        // 按值捕获 name
```

- 捕获方式：每个被捕获的变量取满足闭包体使用所需的**最弱**方式，顺序为“共享借用 → 独占借用 → 按值”。写了 `move` 时一律按值捕获。
- 闭包根据捕获内容和用法自动实现 `Fn`/`FnMut`/`FnOnce`。
- 捕获了借用的闭包是借用承载值（见 [04](04-ownership-borrowing.md) §4）。
- 1.0 不支持在签名中返回闭包类型。函数指针 `fn(A) -> R` 只能接收不捕获环境的闭包。

## 9. 常量求值 [RULE-EVAL-CONST]

- 常量表达式包括：字面量、算术、`const` 引用、`const fn` 调用、结构体/元组/数组构造、不涉及分配的 `match`/`if`。
- `const fn` 体内不得出现：分配、I/O、原始指针解引用、调用非 `const fn`。
- 常量表达式由 MIR 解释器求值（[ADR-0006](../../docs/decisions/ADR-0006-mir-interpreter-oracle.md)）。每个常量的预算为 1,000,000 步、64 MiB；超限、panic 或除零报 `X-E3021`。
- 常量求值的结果必须与运行时求值结果一致，这一点由差分测试保证。

## 10. 模式 [RULE-PAT-NOMINAL] [RULE-PAT-FIELD] [RULE-PAT-DUP] [RULE-PAT-EXHAUSTFIELDS] [RULE-PAT-REST] [RULE-PAT-VIS] [RULE-PAT-IRREFUTABLE] [RULE-PAT-PARTIAL] [RULE-PAT-KIND] [RULE-PAT-REF] [RULE-PAT-EXHAUSTIVE]

```x
let Point { x, y } = p;                     // 字段简写
let Point { x: px, .. } = p;                // 重命名并忽略其余字段
let (a, b) = pair;
let &User { id, name } = user_ref;          // id: &u64，name: &String
match (cmd) {
    Command::Add { a, b } => a + b,
    Command::Neg(v) => -v,
    _ => 0,
}
match (arg) { "-h" => help(), "-v" => version(), other => run(other) }
```

| 规则 | 诊断 |
|---|---|
| 结构体模式必须带类型名，裸 `{ x, y }` 非法 | X-E2101 |
| 字段必须存在、不得重复 | X-E2102 / X-E2103 |
| 没有 `..` 时必须列出所有可见字段；`..` 只能出现一次且必须在最后 | X-E2104 / X-E1012（语法层）/ X-E2105（语义层） |
| 不得匹配不可见的字段；包外的 `@non_exhaustive` 类型必须带 `..` 或 `_` | X-E2106 |
| `let`/`var`、函数参数、`for` 中只能用不可失败模式 | X-E2107 |
| 部分移动后不得整体使用原值；实现了 Drop 的类型不得部分移动 | X-E2108 / X-E4005 |
| 单个名字的解析顺序：先找可见的无载荷变体或常量，找不到才新建绑定；解析到不能用于模式的 Item 时报错，不得回退成绑定 | X-E2109 |
| `&P` 要求输入为 `&T`，`&mut P` 要求输入为 `&mut T`；绑定模式向下递归传递 | X-E2110 |
| `match` 必须穷尽，诊断给出一个缺失模式的示例 | X-E2111 |

字面量模式允许整数、`bool`、`char`、字符串（匹配 `&str`）。浮点字面量模式报 `X-E2109`。1.0 不支持 OR 模式、范围模式、守卫。

## 11. `@tailcall` [RULE-EVAL-TAILCALL]

标注 `@tailcall` 的函数中，所有**直接自调用**都必须处于尾位置（即 `return f(...)` 或块尾表达式），并且调用点没有待析构的局部值。满足条件时，编译器必须把它降级为跳转，栈深度为 O(1)。不满足时报 `X-E3020`，并指出待析构的值。互递归不作保证。

## 12. 规则与诊断

| Rule ID | 诊断 |
|---|---|
| RULE-EVAL-PLACE | X-E3008 |
| RULE-EVAL-CAST | X-E3002 |
| RULE-EVAL-OPERATOR | X-E3010 |
| RULE-EVAL-ORDER | （运行时语义，run-pass 语料验证） |
| RULE-EVAL-CONST | X-E3021 |
| RULE-EVAL-TAILCALL | X-E3020 |
| RULE-OWN-CAPTURE | X-E4009 |
| RULE-PAT-NOMINAL | X-E2101 |
| RULE-PAT-FIELD | X-E2102 |
| RULE-PAT-DUP | X-E2103 |
| RULE-PAT-EXHAUSTFIELDS | X-E2104 |
| RULE-PAT-REST | X-E1012、X-E2105 |
| RULE-PAT-VIS | X-E2106 |
| RULE-PAT-IRREFUTABLE | X-E2107 |
| RULE-PAT-PARTIAL | X-E2108 |
| RULE-PAT-KIND | X-E2109 |
| RULE-PAT-REF | X-E2110 |
| RULE-PAT-EXHAUSTIVE | X-E2111 |
| LINT-UNREACHABLE | X-W0003 |
