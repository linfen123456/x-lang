---
doc_id: DOC-GUIDE-CORE-LANGUAGE
title: X-Lang 核心语言渐进教程
authority: implementation
owner: role/docs-team
backup_owner: role/language-council
version: "0.1"
maturity: CORE
status: 草案
phase: P1
last_reviewed: 2026-08-15
applies_to: [learner, parser, type-checker]
traceability_scope: [XLF]
supersedes: []
---

# X-Lang 核心语言渐进教程

## 1. 学习目标与状态声明

本章把原始材料中的“简洁、显式、渐进学习、OOP 与函数式表达力”落实为一条可执行学习路径。先决条件是完成[入门教程](./getting-started.md)。

> 当前没有可执行 X-Lang 工具链。本章代码是 [核心语言规范](../specs/language-core.md) 的目标示例；当示例涉及待决 RFC，会就地标注，不把候选设计伪装成稳定行为。

完成后应能编写由绑定、函数、控制流、结构体、枚举、模式、泛型和 Trait 组成的 P1/P2 程序，并能解释编译器应在哪个阶段拒绝错误程序。

## 2. 绑定、类型和作用域

### 2.1 默认不可变

```x
fn main() {
    let width: i32 = 8;
    let height = 5;
    let area = width * height;
    println(area);
}
```

局部类型可从初始化表达式推断，但不能依赖上下文猜测任意类型。未写 `mut` 的绑定不能重新赋值：

```x
fn main() {
    let total = 0;
    total = 1; // 预期：不可赋值给不可变绑定
}
```

正确写法：

```x
fn main() {
    let mut total = 0;
    total = total + 1;
}
```

这体现原始材料的“显式优于隐式”：编译器可建议 `mut`，不能自动改变程序。

### 2.2 作用域与遮蔽

```x
fn main() {
    let value = 10;
    {
        let value = value + 1;
        println(value); // 11
    }
    println(value);     // 10
}
```

内层声明产生新绑定。是否允许同一作用域重复声明、lint 强度和名称解析细节由模块/作用域 RFC 决定；教程不依赖这些待决行为。

### 2.3 显式转换

```x
fn main() {
    let small: u8 = 10;
    let wide: u32 = small as u32;
}
```

数值类型之间不做可能改变值域的隐式转换。窄化转换、溢出和浮点行为见 RULE-LANG-007/009；不要从示例推断所有 `as` 都无损。

## 3. 表达式与控制流

### 3.1 `if` 是表达式

```x
fn grade(score: i32) -> &'static str {
    if score >= 60 {
        "pass"
    } else {
        "fail"
    }
}
```

两个分支必须产生可统一的类型。如果一个分支是字符串、另一个是整数，类型检查应失败，而不是在运行时转换。

### 3.2 循环

```x
fn sum_positive(values: Vec<i32>) -> i32 {
    let mut sum = 0;
    for value in values {
        if value < 0 {
            continue;
        }
        sum += value;
    }
    sum
}
```

`while` 适合条件循环，`loop` 表示显式无限循环。迭代器消耗、借用还是复制元素取决于被迭代值和迭代器 API，不由 `for` 静默复制所有数据。

### 3.3 管道操作符是候选能力

原始 `11.txt` 明确提出 `|>`：

```x
fn run(raw: Input) -> Output {
    raw |> parse |> validate |> process
}
```

它已进入 XLF-11-005，但调用展开、参数位置和求值顺序仍需 RFC。因此当前只能把它当作 EXTENDED 目标；CORE 教程使用普通调用：

```x
fn run(raw: Input) -> Output {
    process(validate(parse(raw)))
}
```

## 4. 函数、参数与闭包

### 4.1 函数签名和尾表达式

```x
fn clamp(value: i32, min: i32, max: i32) -> i32 {
    if value < min {
        min
    } else if value > max {
        max
    } else {
        value
    }
}
```

参数和公开返回类型应显式。末尾表达式没有分号；写成 `value;` 后它变成语句，函数将不再产生 `i32`，编译器应定位到返回类型不匹配。

### 4.2 命名参数与默认参数尚未冻结

`draw_circle(radius=10, color="red")` 来自原始 `11.txt`，追溯为 XLF-11-005。现有 EBNF 可解析命名实参，但重复参数、默认表达式求值时机、API 兼容性尚待 RFC。教程不得把它作为 CORE API 的必要条件。

### 4.3 闭包与捕获

```x
fn main() {
    let threshold = 10;
    let is_large = |value: i32| value > threshold;
}
```

闭包可借用、可变借用或移动捕获环境；具体选择必须由使用方式和 `move` 明确约束。需要跨线程保存的闭包通常写为 `move |value| ...`，并接受 Send 与生命周期检查。完整捕获推断见类型专题和内存规范。

## 5. 结构体、方法和枚举

### 5.1 数据结构与固有实现

```x
struct Point {
    x: f64,
    y: f64,
}

impl Point {
    fn squared_distance(&self) -> f64 {
        self.x * self.x + self.y * self.y
    }
}
```

`&self` 只读借用接收者；`&mut self` 允许修改；`self` 消耗值。方法调用只是受名称解析和接收者调整约束的调用形式，不意味着隐式垃圾回收或类继承。

### 5.2 用枚举表达有限状态

```x
enum ConnectionState {
    Closed,
    Connecting,
    Open(u32),
    Failed(NetError),
}
```

与空指针或魔法整数相比，枚举把状态与载荷放入静态类型。布局与 ABI 不应从声明顺序猜测；除非受批准的 `repr` 规则约束，外部程序不得依赖内部布局。

## 6. 模式匹配与穷尽性

```x
fn describe(state: ConnectionState) -> &'static str {
    match state {
        ConnectionState::Closed => "closed",
        ConnectionState::Connecting => "connecting",
        ConnectionState::Open(_) => "open",
        ConnectionState::Failed(_) => "failed",
    }
}
```

编译器应对闭合枚举检查穷尽性。以下程序必须拒绝：

```x
fn connection_id(state: ConnectionState) -> u32 {
    match state {
        ConnectionState::Open(id) => id,
    }
}
```

通配 `_` 可以覆盖剩余情况，但会让后来新增分支不再触发遗漏提示；公共枚举的演进规则由版本治理决定。

解构来自 XLF-11-005。当前已能表达元组、结构体和变体模式；深度剩余模式 `..rest` 尚未进入现有正式 EBNF，不能作为已稳定语法。

## 7. Option、Result 与问号传播

### 7.1 缺失值不是空指针

```x
fn first<'a>(values: &'a [i32]) -> Option<&'a i32> {
    if values.len() == 0 {
        None
    } else {
        Some(&values[0])
    }
}
```

调用者必须匹配 `Some`/`None` 或使用标准库批准的组合子。`Option` 的签名目标见 RULE-STD-010。

### 7.2 可恢复失败使用 Result

```x
fn load_settings(path: &Path) -> Result<Settings, LoadError> {
    let text = file::read_to_string(path)?;
    parse_settings(text)
}
```

`?` 对 `Ok` 解包，对 `Err` 进行兼容转换后提前返回；转换必须由明确 Trait/规则提供，不能任意丢失上下文。不可恢复的不变量破坏才考虑 `panic`。

## 8. 泛型和 Trait

```x
trait Printable {
    fn print(&self);
}

fn print_twice<T: Printable>(value: &T) {
    value.print();
    value.print();
}
```

泛型调用必须满足声明的 Trait 约束。不能仅因某类型“碰巧有同名方法”就满足 `Printable`；需要可解析的 `impl`。一致性、重叠实现和 Solver 终止条件见[类型、Trait 与模式规范](../specs/types-traits-patterns.md)。

反例：

```x
struct Token {}

fn main() {
    let token = Token {};
    print_twice(&token); // 没有 Printable impl，应在类型检查期失败
}
```

## 9. 一个完整的小程序

```x
enum ParseCountError {
    Empty,
    Invalid,
}

fn parse_count(text: &str) -> Result<u32, ParseCountError> {
    if text.len() == 0 {
        return Err(ParseCountError::Empty);
    }
    parse_u32(text).map_err(|_| ParseCountError::Invalid)
}

fn report(text: &str) -> Result<(), ParseCountError> {
    let count = parse_count(text)?;
    let label = if count == 1 { "item" } else { "items" };
    println(count, label);
    Ok(())
}
```

这段示例有意不包含网络、异步、宏、默认参数或 GC：它验证 CORE 的函数、借用、枚举、Result、闭包和控制流组合。`parse_u32`、`map_err`、`println` 的最终 API 需由标准库规范固定。

## 10. 常见错误、练习与验收

常见错误：给尾表达式误加分号；假设整数可隐式窄化；遗漏枚举分支；把同名方法当成 Trait 实现；把 `panic` 当普通业务错误；在稳定代码中使用未冻结的管道或默认参数。

练习：

1. 为 `Point` 实现 `Printable`，分别解释 `&self` 与 `self` 的影响。
2. 定义 `enum Temperature { Celsius(f64), Fahrenheit(f64) }` 并写穷尽匹配。
3. 将一个嵌套 `match Result` 改写为 `?`，列出错误类型必须满足的条件。
4. 写一个泛型 `choose<T>`；不要在没有规则依据时加入运算符重载。
5. 故意遗漏枚举分支、去掉 Trait impl、制造分支类型不一致，记录预期诊断阶段。

检查点：能够从代码判断绑定是否可变、值是否被移动、匹配是否穷尽；能够区分语法已可解析与语义已稳定；能够沿 RULE/XLF 找到规范来源。

## 11. 来源与继续阅读

- 原始来源：`1.txt` 的显式、渐进式、OOP+FP；`2.txt` 的变量、函数、结构体、泛型、模式和 Trait 草案；`10.txt` 的 Result；`11.txt` 的管道、解构、命名/默认参数。
- 追溯：XLF-01-010、XLF-02-012、XLF-10-001、XLF-11-005。
- 继续阅读：[所有权、错误与并发教程](./ownership-errors-concurrency.md)、[类型、Trait 与模式规范](../specs/types-traits-patterns.md)。
