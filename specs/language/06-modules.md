# 06 模块、导入、可见性、名称解析与 Prelude

> 状态：Accepted｜版本：2.1.0｜负责人：Language Lead｜最后更新：2026-10-22
> 类型：Spec｜唯一负责：文件到模块的映射、包根路径、导入/重导出、名称空间、可见性、方法查找、Prelude 精确名单。

## 1. 结论

1. 模块由文件路径决定，源码中没有 `mod` 声明。路径都是绝对路径，第一段必须是当前包或某个直接依赖。
2. 导入只有一种形式：精确的 `use a::b::C;`，可以加 `as`。不支持 glob（`*`）和分组导入。
3. 可见性分三级：私有（默认）、`pub(package)`、`pub`。
4. 名称解析的结果与文件遍历顺序、导入顺序、操作系统、缓存状态无关。

## 2. 文件与模块 [RULE-MOD-PATH]

1. 库包的根是 `src/lib.x`，二进制包的根是 `src/main.x`。`src/a/b.x` 对应模块 `<pkg>::a::b`。目录 `src/a/` 本身也对应模块 `<pkg>::a`，其内容可写在 `src/a.x` 中，`a.x` 与 `a/` 可以同时存在。
2. 路径规范化：分隔符统一为 `/`。大小写折叠后冲突、符号链接逃出包根，都报 `X-E2001`。
3. 模块之间不存在初始化顺序：模块没有顶层可执行语句，static 初始化器必须是常量表达式。

## 3. 包根与导入根名 [RULE-MOD-ROOT] [RULE-MOD-DIRECT]

- 包名规则见[包规范](../packages/manifest-lock-build.md) §2。**导入根名 = 包名中的 `-` 全部替换为 `_`**。例如包 `order-service` 的导入根名是 `order_service`。
- 路径第一段必须恰好是当前包的导入根名，或 `[dependencies]` 中某个直接依赖的 key（同样把 `-` 换成 `_`），否则报 `X-E2002`。
- 导入传递依赖报 `X-E2003`。

```x
use order_service::domain::Order;   // 当前包
use http::Client;                   // 直接依赖
use std::fs;                        // 标准库根：core / alloc / std 总是可用
```

## 4. 导入、别名与重导出 [RULE-MOD-ALIAS] [RULE-MOD-REEXPORT]

- `use p::Item;` 只在当前模块内绑定名字。
- `use p::Item as Name;` 起别名，不产生新类型。
- 同名冲突、别名覆盖本地 Item，报 `X-E2005`。
- `pub use p::Item;` 是唯一的重导出方式，形成公开 Facade 边。`pub(package) use` 只在包内可见。重导出成环报 `X-E2006`。
- 未使用的导入产生 `X-W0002`。

## 5. 名称空间 [RULE-MOD-NS] [RULE-MOD-UNRESOLVED]

- 同一模块中，类型、Trait、函数、常量、static、子模块共享一个 Item 名称空间，重名报 `X-E2004`。
- 枚举变体位于所属枚举之下，写作 `Enum::Variant`。Prelude 额外提供裸名 `Some`、`None`、`Ok`、`Err`。
- 局部变量使用独立的值名称空间，但不得遮蔽导入的名字或 Item。
- 名称无法解析时报 `X-E2010`，并尽量给出“你是否想用……”的建议，包括大写原始类型名的 Fix-it。

## 6. 可见性与 Facade [RULE-MOD-VIS]

| 写法 | 可见范围 |
|---|---|
| （无） | 当前模块（包括其子模块） |
| `pub(package)` | 当前包 |
| `pub` | 包外。但下游只能通过 `lib.x` 中可达的路径访问 |

- 公开签名中不得出现可见性更低的类型，绕过 Facade 访问也不允许。两者都报 `X-E2007`。
- 1.0 不提供 `protected`、friend、`pub(super)`。

## 7. `::` 与 `.`

- `::` 的左侧是包、模块、类型或 Trait（不是运行时值），用于访问关联函数、关联常量和变体。
- `.` 的左侧是运行时值（只求值一次），用于访问字段和调用方法。
- 两者不可互换，`Type.method()` 和 `value::method()` 都非法。

## 8. Receiver 与禁止重载

- Receiver 只能是 `self: Self`、`self: &Self`、`self: &mut Self` 之一，而且必须是第一个参数。
- 同一作用域内同名函数只能有一个，不支持按参数类型重载。
- 同一类型的固有方法与字段不得同名，否则报 `X-E2009`。

## 9. 方法查找（`value.m(args)`）[RULE-METHOD-AMBIG] [RULE-METHOD-FIELD]

1. 求值 `value` 一次，取其静态类型 `T`。
2. 收集 `T` 上可见的固有方法，以及已导入（或位于 Prelude 中）且 `T` 有唯一 impl 的 Trait 方法。
3. Receiver 只做一次调整，由方法声明决定：`self: Self` 移动或复制，`&Self` 自动借用，`&mut Self` 自动独占借用。如果 `value` 本身是引用，可以再做**一次**自动解引用。不做多级自动解引用，也不做用户定义转换。
4. 恰好一个候选适用时调用它；没有候选报 `X-E2010`；多于一个候选报 `X-E2008`，此时用完全限定形式 `Trait::m(&value)` 消除歧义。
5. `.name` 永远指字段；`.name()` 先找方法，找不到时如果 `name` 是可调用的字段则调用字段。

## 10. Prelude（1.0 精确名单）

Prelude 按 Edition 固定，可以用 `x.toml [package] prelude = false` 关闭。

| 类别 | 名称 |
|---|---|
| 类型 | `Option` `Result` `String` `Vec` `Box` |
| 变体裸名 | `Some` `None` `Ok` `Err` |
| Trait | `Copy` `Clone` `Drop` `Eq` `Ord` `Hash` `Default` `Display` `Debug` `Iterator` `IntoIterator` `Fn` `FnMut` `FnOnce` `Send` `Sync` |
| 函数 | `print` `println` `eprint` `eprintln` `panic` `assert` `assert_eq` `unreachable` `range` `range_inclusive` |

说明：
- 打印函数只能写 stdout/stderr，不涉及文件或网络。它们放进 Prelude 是为了 CLI 场景的易用性，这是对旧版 RFC-0001“Prelude 不含 I/O”的有意修改，见 [ADR-0007](../../docs/decisions/ADR-0007-language-core-decisions.md)。
- 原始类型名不属于 Prelude，它们总是可用。
- 显式导入的名字遮蔽 Prelude 中的名字时，产生 `X-W0007`。

## 11. 规则与诊断

| Rule ID | 诊断 |
|---|---|
| RULE-MOD-PATH | X-E2001 |
| RULE-MOD-ROOT | X-E2002 |
| RULE-MOD-DIRECT | X-E2003 |
| RULE-MOD-NS | X-E2004 |
| RULE-MOD-ALIAS | X-E2005 |
| RULE-MOD-REEXPORT | X-E2006 |
| RULE-MOD-VIS | X-E2007 |
| RULE-METHOD-AMBIG | X-E2008 |
| RULE-METHOD-FIELD | X-E2009 |
| RULE-MOD-UNRESOLVED | X-E2010 |
| RULE-MOD-INITCYCLE | X-E2011 |
| LINT-UNUSED-IMPORT | X-W0002 |
| LINT-PRELUDE-SHADOW | X-W0007 |
