# 04 所有权、借用、区域（1.0 生命周期策略）与 Drop

> 状态：Accepted｜版本：2.1.0｜负责人：Language Lead｜最后更新：2026-10-22
> 类型：Spec｜唯一负责：绑定、移动/复制、借用规则、NLL、隐式区域与省略规则、借用承载类型、P1 受限子集、初始化与 Drop 顺序。

## 1. 结论

1. 内存安全靠**所有权 + 借用检查**保证，不使用 GC。
2. **1.0 没有显式生命周期语法**。每个引用类型、每个借用承载类型都隐含**恰好一个区域**；函数签名中的区域由 §5 的省略规则唯一确定。确定不了就报错 `X-E4010`，并建议改为返回拥有型值。
3. 写 `'a` 形式的生命周期标注报 `X-E1030`。显式生命周期保留给 1.0 之后的 Edition。
4. 借用检查在 MIR 上做 NLL（非词法生命周期）。P1 不支持两阶段借用，P2 起完整支持。

## 2. 绑定、移动与复制 [RULE-OWN-USEMOVED] [RULE-OWN-DOUBLEMOVE] [RULE-OWN-LETASSIGN] [RULE-OWN-MOVEOUT]

- `let` 绑定不可重新赋值（违反报 `X-E4008`）；`var` 绑定可以重新赋值。两者在所有权上没有区别。
- 实现 `Copy` 的值按值使用时复制，其他值按值使用时**移动**。移动后再使用报 `X-E4001`，重复移动报 `X-E4002`（例如在循环中移动）。
- 不能从借用中移出值（`*r`、`r.field`，其中 `r: &T`，字段非 Copy），报 `X-E4006`；需要时改用 `clone()` 或 `std::mem::replace`。

```x
let s = String::from("hi");
let t = s;            // s 被移动
print(s);             // X-E4001：s 已被移动（指出第 2 行的移动点）
```

## 3. 借用 [RULE-OWN-CONFLICT] [RULE-OWN-SHAREDMUT] [RULE-OWN-ESCAPE]

1. `&place` 产生共享借用，`&mut place` 产生独占借用。`&mut` 要求 `place` 可变：`var` 绑定，或经由 `&mut` 到达。
2. 在任一程序点，同一 Place 上可以有任意多个共享借用，或者恰好一个独占借用，两者不能同时存在。冲突报 `X-E4003`。
3. 不能经由共享借用修改数据，违反报 `X-E4007`。内部可变性需要使用 `Cell`/`RefCell`/`Mutex`/原子类型。
4. **NLL**：借用从创建点开始，一直活到它最后一次被使用的点（沿控制流计算）。借用的活跃范围**不影响** Drop 的时机。
5. 字段级精度：对同一结构体中不同字段的借用互不冲突；对同一数组不同索引的借用视为冲突（切片拆分用 `split_at_mut`）。
6. 借用不得活得比被借用的值更久。被借用的值包括局部变量、临时值、已被移动的值。违反报 `X-E4004`，诊断需指出拥有者及其失效点。
7. **两阶段借用**（P2）：`v.push(v.len())` 中，Receiver 的 `&mut v` 到调用真正开始时才激活，因此这种写法合法。P1 不支持，需要写成 `let n = v.len(); v.push(n);`。

## 4. 区域与借用承载类型 [RULE-OWN-NOLIFETIME]

- **区域**：一段程序点集合，借用在其中有效。区域只存在于编译器内部，源码中不可见。
- **借用承载类型**：本身是引用，或者其字段（递归地）或泛型实参中含有引用/借用承载类型。例如 `&str`、`Iter<T>`（内部含 `&[T]`）、`Pair<&str, i32>`、捕获了借用的闭包。
- 每个借用承载的**类型定义**（struct/enum）只有一个隐式区域参数，其中所有引用字段共享这个区域：

```x
pub struct Words { text: &str, pos: usize }     // 借用承载类型：隐式区域 'ρ
// 等价于概念上的 Words<'ρ>，'ρ 不能在源码中写出
```

- 所以，“一个结构体同时持有两个寿命不同的借用”在 1.0 中无法表达。这类场景使用拥有型数据、索引，或拆成两个结构体。这是已登记的表达力限制。
- 文档生成器和 LSP 必须把借用承载类型标注为“借用承载”。

## 5. 函数签名省略规则（唯一规则）[RULE-OWN-ELISION]

先定义**区域来源**：类型为引用或借用承载类型的参数（包括 `self`）。同一个参数内部的所有区域合并为一个。

| 情形 | 返回值中的区域取自 |
|---|---|
| Receiver 是 `self: &Self` 或 `self: &mut Self`，或者 `Self` 本身是借用承载类型 | Receiver |
| 否则，恰好有一个区域来源参数 | 该参数 |
| 否则，没有区域来源参数 | 只能是 `static` 区域，即字符串字面量、`static` 项的借用 |
| 否则（≥ 2 个来源，且没有引用类 Receiver） | 报 `X-E4010`：返回借用无法确定唯一来源 |

```x
fn first_word(s: &str) -> &str { ... }                     // 合法：唯一来源 s
impl Config { fn name(self: &Self) -> &str { ... } }       // 合法：来源 self
fn longest(a: &str, b: &str) -> &str { ... }               // X-E4010；改为返回 String，或用 Pair 方法
fn version() -> &str { "1.0.0" }                           // 合法：static
```

调用点：实参的借用必须覆盖返回值的所有使用点，这由 NLL 检查。

## 6. P1 受限子集（P1 必须实现）

P1 实现第 2–5 节的全部规则，例外如下：
1. 不支持两阶段借用（§3 第 7 条）；
2. 没有闭包，所以不涉及捕获（闭包在 P2 引入）；
3. 借用检查失败时，只要求给出主 Span 和拥有者，不要求给出修复建议。

P1 **不得**接受任何未经检查的引用。这是取代旧方案中“P1 有引用、P2 才有借用检查”的关键修正。

## 7. 初始化与赋值

- 每个绑定都必须在声明时初始化（文法强制）。
- MIR 为每个可移动的 Place（细化到字段）维护初始化状态；条件移动之后的使用按“可能已移动”处理，报 `X-E4001`。
- 覆盖已初始化的 Place 时：先求值新值，再析构旧值，然后写入（与 [03](03-expressions-patterns.md) §3 一致）。即使中途 panic，也不会重复析构。

## 8. Drop 顺序 [RULE-DROP-PARTIAL]

1. 局部绑定按**初始化的逆序**析构，析构点是作用域结束处。
2. struct 字段按**声明逆序**析构，元组、数组元素按下标逆序析构（与局部绑定一致，都是“后构造先析构”）；枚举只析构当前活跃变体的字段。
3. 只析构仍处于已初始化状态的值，每个值恰好析构一次。部分移动后，剩余字段照常析构。
4. 实现了 `Drop` 的类型禁止部分移动，违反报 `X-E4005`。
5. 正常退出、`return`、`break`、`?` 都执行清理。`panic=abort` 不保证执行 Drop（见 [05](05-errors-panics.md)）。
6. 临时值在所在语句结束时析构（延长规则见 [03](03-expressions-patterns.md) §2）。
7. `std::mem::drop(x)` 立即析构；`std::mem::forget(x)` 不析构（这是安全操作，泄漏不属于 UB）。

## 9. RAII Guard（替代 `defer`）

```x
let guard = std::guard::on_exit(fn() => cleanup());   // 作用域结束时调用 cleanup
// …
guard.dismiss();                                        // 可选：取消
```

`std::guard::on_exit` 在 P2 提供，它覆盖了原始需求中 `defer` 的全部 LIFO 清理场景。

## 10. 规则与诊断

| Rule ID | 诊断 |
|---|---|
| RULE-OWN-USEMOVED | X-E4001 |
| RULE-OWN-DOUBLEMOVE | X-E4002 |
| RULE-OWN-CONFLICT | X-E4003 |
| RULE-OWN-ESCAPE | X-E4004 |
| RULE-DROP-PARTIAL | X-E4005 |
| RULE-OWN-MOVEOUT | X-E4006 |
| RULE-OWN-SHAREDMUT | X-E4007 |
| RULE-OWN-LETASSIGN | X-E4008 |
| RULE-OWN-ELISION | X-E4010 |
| RULE-OWN-NOLIFETIME | X-E1030 |
| LINT-UNUSED-VAR | X-W0001 |
