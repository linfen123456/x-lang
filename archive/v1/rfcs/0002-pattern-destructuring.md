> 已归档：见 v2 [specs/language/03-expressions-patterns.md](../../../specs/language/03-expressions-patterns.md)

# RFC-0002：模式解构、字段简写与剩余字段

> 状态：Proposed
> 日期：2026-08-17
> 目标版本：X-Lang 1.0 候选
> 依赖：RFC-0001 的名称/可见性、RFC-0005 的模式语法、RFC-0007 的所有权/Drop
> 正式产物：接受后生成 `specs/language/patterns.md`。

## 1. 摘要

本提案保留 X-Lang 的名义类型模式，增加 `Point { x, y }` 字段同名简写和 `..` 显式忽略剩余字段。裸 `{ x, y }` 不合法，避免引入 JavaScript 式结构类型语义。

## 2. 目标与非目标

### 2.1 目标

- 降低 `Point { x: x, y: y }` 的重复；
- 明确字段重命名、忽略、移动、借用和可失败性；
- 新增字段时让兼容影响可见；
- 保持 Parser、类型检查和 formatter 规则简单确定。

### 2.2 非目标

- 不引入匿名记录或结构类型；
- 1.0 不引入 OR、范围、守卫、运行时类型测试或默认字段值模式；
- `..` 只用于结构体模式，不引入通用范围运算符；
- 不允许通过模式绕过字段可见性或所有权。

## 3. 语法变更

建议将结构体模式产生式更新为：

```ebnf
struct_pattern = path, "{", [ struct_pattern_fields ], "}" ;
struct_pattern_fields = field_pattern, { ",", field_pattern },
                        [ ",", rest_pattern ], [ "," ]
                      | rest_pattern, [ "," ] ;
field_pattern = IDENT, [ ":", pattern ] ;
rest_pattern  = ".." ;
```

`pattern` 仍要求名义 `path`：

```x
let Point { x, y } = point;
```

以下非法：

```x
let { x, y } = point; // X-E2101
```

## 4. 字段简写

```x
let Point { x, y } = point;
```

等价于：

```x
let Point {
    x: x,
    y: y,
} = point;
```

字段重命名保持显式：

```x
let Point {
    x: horizontal,
    y: vertical,
} = point;
```

规则：

- 简写 `x` 同时引用字段 `x` 并创建绑定 `x`；
- 字段名称先按被匹配类型解析，绑定名称再进入局部作用域；
- 字段不得重复；绑定冲突按普通局部名称规则诊断；
- Formatter 对两个及以上字段采用逐行尾逗号规范格式。

## 5. `let`、`var` 与借用

```x
let Point { x, y } = point; // x、y 不可重新赋值
var Point { x, y } = point; // x、y 可以重新赋值
```

`var` 改变新绑定的可变性，不改变从源值取字段的所有权方式。

按值模式默认移动非 `Copy` 字段：

```x
let User { id, name } = user;
```

显式借用整个模式：

```x
let &User { id, name } = user_ref;
let &mut User { id, name } = user_mut_ref;
```

借用模式的 binding mode 固定如下：

- 外层 `&P` 要求输入类型恰为 `&T`，在 `P` 内新建的字段绑定类型为 `&FieldType`；外层 `&mut P` 要求输入类型恰为 `&mut T`，绑定类型为 `&mut FieldType`；
- binding mode 递归传播到元组和结构体嵌套模式，直至遇到另一个显式引用模式；没有显式 `&`/`&mut` 时不自动解引用；
- `&mut` 模式可以同时产生多个字段借用，仅当字段 Place 静态不重叠；这些独占借用的生命周期按普通词法/NLL 借用规则计算，且不得长于输入引用；
- `..` 不产生借用；混合字段级 move/ref 语法不在 1.0 中，未来增加必须由所有权 RFC 单独批准；
- `var` 只允许重新绑定局部变量，不把 `&FieldType` 升级为 `&mut FieldType`，也不改变输入借用权限。

因此上例的 `id`、`name` 分别是共享字段引用和独占字段引用，而不是字段值。类型检查器必须在 HIR 中记录 inherited binding mode，MIR lowering 不得自行猜测。

### 5.1 部分移动与 Drop

- 对拥有的 `T` 按值解构时，`Copy` 字段复制，非 `Copy` 字段移动；
- `..` 忽略的字段不创建绑定，也不移动或借用；
- 发生部分移动后不得整体读取、移动或显式 Drop 原值，但仍可访问尚未移动且可见的字段；
- 具有用户自定义 Drop 的类型在 1.0 禁止部分移动，调用者必须按引用解构或使用类型提供的 `into_parts()`；
- 编译器必须在 MIR 中跟踪字段级初始化状态，确保只析构仍初始化的字段且恰好一次。
- 上述规则递归应用到嵌套字段：每个叶子 Place 按 RFC-0007 独立记录 move/borrow/init 状态。

## 6. 穷尽字段与 `..`

- 没有 `..` 时必须列出当前上下文所有可见且参与匹配的字段；遗漏字段报错。
- `..` 明确表示忽略未列字段，最多出现一次且必须在最后。
- 包外匹配具有不可见字段的公开结构体时必须使用 `..`，除非该类型禁止外部解构。

```x
let User {
    id,
    name,
    ..
} = user;
```

如果库将结构体标记为不可穷尽，包外模式必须包含 `..`。不可穷尽属性的具体名称由属性 RFC 决定，本 RFC 只冻结行为。

## 7. 可失败性

- `let/var`、函数参数、闭包参数和 `for` 模式必须不可失败；
- `match` 分支允许可失败模式并要求整体穷尽；
- 匹配一个已知静态类型的结构体字段模式是不可失败的；
- 枚举变体模式在绑定位置不可失败规则下不得使用，除非类型系统能静态证明唯一变体。

```x
let Point { x, y } = point;          // 合法
let Some(value) = option;            // X-E2107
match (option) { Some(value) => value, None => fallback() }
```

### 7.1 单名模式解析

单个 `path` 在模式位置按以下顺序且不得回退：

1. 若它唯一解析到当前可见的无载荷枚举变体，或类型为 `Bool`、`Char`、固定宽度整数的具名编译期常量，则是构造器/常量模式；浮点、字符串、引用、聚合以及用户自定义相等性的常量在 1.0 不能作为常量模式；
2. 若首段在 Item Namespace 中没有任何定义，且该 path 只有一个未限定 `IDENT`，则创建新局部绑定；
3. 若它解析到函数、类型、模块、有载荷变体或其他错误种类，报告 wrong-kind，不把它重新解释为绑定；
4. 多段 path 永远不是新绑定，必须唯一解析到允许的模式 Item。

Prelude 中的 `None` 因而解析为 `Option::None` 的无载荷变体；显式 `Option::None` 永远是构造器模式。若显式导入或本地 Item 与 Prelude `None` 冲突，遵循 RFC-0001 的名称冲突规则并要求限定路径，不允许静默变为通配绑定。`Some(value)` 必须解析到有载荷构造器，括号内才创建 `value` 绑定。

## 8. 元组与嵌套模式

现有元组模式保持：

```x
let (left, right) = pair;
```

结构体字段可以嵌套：

```x
let Rectangle {
    origin: Point { x, y },
    size: Size { width, height },
} = rectangle;
```

第 5 节的 binding mode、部分移动和 Drop 规则递归应用到嵌套模式。Parser 只建立模式树；类型检查器按 RFC-0007 给每个叶子 Place 标注按值、共享借用或独占借用，MIR 跟踪字段级状态。

## 9. 诊断

| 诊断 | 含义 |
|---|---|
| `X-E2101` | 使用裸结构模式 |
| `X-E2102` | 字段不存在 |
| `X-E2103` | 字段重复 |
| `X-E2104` | 未列全且没有 `..` |
| `X-E2105` | `..` 重复或不在最后 |
| `X-E2106` | 访问不可见字段 |
| `X-E2107` | 不可失败位置使用可失败模式 |
| `X-E2108` | 解构后非法使用部分移动值 |
| `X-E2109` | 单名/路径解析到不能用于模式的 Item，且不得回退成绑定 |
| `X-E2110` | 引用模式、输入引用权限或字段借用发生冲突 |

规则追溯使用 `RULE-PAT-*`，不得把诊断码当成规范规则 ID。

诊断必须指出类型、字段、绑定位置和可用修复，例如插入 `..` 或转为 `match`。

## 10. 验收

- Parser/formatter 覆盖简写、重命名、嵌套、尾逗号和 `..`；
- compile-pass/fail 覆盖未知/重复/私有字段、不可穷尽类型和可失败绑定；
- MIR/解释器固定按值移动、`Copy`、共享/独占字段借用、嵌套传播和部分 Drop Trace；
- compile-pass/fail 覆盖 Prelude `None`、`Option::None`、新绑定、wrong-kind、同名冲突和无回退解析；
- 新增公开字段的 API Diff 能区分穷尽模式破坏与带 `..` 模式兼容；
- IDE Rename 同时正确处理字段名和简写绑定，不把两者混为同一 DefId。

## 11. 替代方案

### 裸 `{ x, y }`

拒绝。它隐藏名义类型、可见性和重构边界，容易被误解为结构类型或动态对象解构。

### 维持 `x: x`

语义最简单，但高频重复降低可读性；字段简写只增加局部、确定的 Parser 规则，收益足够。

### 默认忽略未列字段

拒绝。它会让新增字段静默改变数据处理意图；要求显式 `..` 更适合审查和兼容分析。
