# RFC-0001：模块、导入、名称解析与可见性

> 状态：Proposed
> 日期：2026-08-17
> 目标版本：X-Lang 1.0 候选
> 依赖：RFC-0005 的语法、RFC-0006 的 Place/求值和 RFC-0007 的 Receiver 所有权
> 相关缺口：`GAP-LANG-07`、`XLC-CORE-010`
> 正式产物：接受后生成 `specs/language/modules.md`，本 RFC 保留决策历史。

## 1. 摘要

本提案冻结文件到模块的映射、绝对路径、精确导入、别名、显式重导出、名称空间、Prelude、可见性、方法查找和冲突诊断。目标是让同一源码在操作系统、文件遍历顺序、导入顺序、缓存状态和并行度变化时解析到相同定义。

## 2. 目标与非目标

### 2.1 目标

- 单一、确定、可增量计算的名称解析算法；
- 让人、IDE 和 Agent 从源码直接看出符号来源；
- 适配大型 Workspace、Facade API 和公开 API Diff；
- 避免函数重载、隐式相对搜索和导入顺序影响；
- 为 Trait 方法、字段/方法同名和重导出循环提供稳定诊断。

### 2.2 非目标

- 1.0 不支持 glob、group/nested import、friend、protected 或继承可见性；
- 不支持根据参数、返回类型或调用上下文选择函数重载；
- 不允许依赖编译器私有 AST/HIR/MIR 作为包接口；
- 不在本 RFC 定义版本解析、Lockfile 或 Registry；这些由 RFC-0003 负责。

## 3. 文件、包与模块

1. `x.toml` 的 Package ID 确定包根，文件规范化相对路径确定模块；源码不使用 `mod/module/package` 声明。
2. `src/lib.x` 是库包的 Facade 根；`src/main.x` 是二进制入口。两者同时存在时属于同一 Package 的不同 Target，共享包内模块但公开入口分别计算。
3. 路径分隔在规范层统一为 `/`；Windows 路径、Unicode 正规化和大小写在进入模块图前转换为规范形式。
4. 同一规范路径映射到两个文件、文件与目录大小写折叠后冲突、或符号链接逃出包根时必须报错。
5. 包依赖图和模块值初始化图不得有环；纯类型引用是否允许成环由类型布局规则决定，不能由文件遍历顺序决定。

## 4. 绝对路径与包根解析

源码路径的第一段必须唯一匹配：

1. 当前包在源码中使用的规范名称；或者
2. 当前包 `x.toml` 中声明的直接依赖 key。

禁止从当前目录、父目录、Workspace 根、传递依赖或标准库依次试探。当前包名与依赖 key 冲突时，Manifest 校验失败。

```x
use order_service::domain::Order;
use http::Client;
```

这里 `order_service` 是当前包名，`http` 是直接依赖 key。源码只能访问直接依赖；传递依赖只存在于 `x.lock`、构建图和 SBOM。

## 5. 导入与重导出

规范语法保持：

```ebnf
use_decl = [ "pub" ], "use", path, [ "as", IDENT ], ";" ;
```

### 5.1 精确导入

```x
use app::model::User;
use app::model::UserId;
use app::repository as repository;
```

- 终端可以是模块或 Item；导入模块不会顺带导入其成员。
- 不支持 `use app::*;` 或 `use app::{A, B};`。
- `use` 只影响当前模块；普通导入不改变包的公开 API。
- 重复导入同一 DefId 可以由 formatter 去重；不同 DefId 同名必须使用 `as`。

### 5.2 别名与冲突

```x
use billing::Error as BillingError;
use shipping::Error as ShippingError;
```

- Alias 在当前作用域绑定唯一名称，不创建新类型或新 DefId。
- Alias 不得覆盖本地 Item、另一个 Import 或包根。与 Prelude 同名时，显式 Import 胜出并产生默认 Lint；不得形成随机歧义。
- Import 顺序、格式化顺序和文件遍历顺序不得改变冲突结果。
- 局部绑定遮蔽 Import 默认产生错误；未来若降级为 Lint，必须通过 Edition RFC。

### 5.3 显式重导出

```x
pub use order_service::domain::model::Order;
pub use order_service::domain::model::OrderId as PublicOrderId;
```

- 只有 `pub use` 才创建公开 Facade 边；普通 `use` 不重导出。
- 只能重导出当前上下文可访问且允许公开的 Item。
- Alias 是消费者看到的公开名称，进入 SemVer/API Diff。
- 元数据保留原始 Package ID、DefId 和来源路径；重导出不是复制定义。
- 重导出图必须做 SCC 检测；任何循环稳定报错，不执行文件顺序固定点猜测。

## 6. 名称空间

1. 1.0 采用单一 Item Namespace：模块、类型、Trait、函数和常量在同一 Item 作用域不能重名。枚举变体位于所属枚举的关联名称空间；默认通过 `Enum::Variant` 访问，只有显式导入或版本化 Prelude Alias 才能产生裸名称。
2. 局部值使用 Local Value Namespace，但不得遮蔽 Import 或公开 Item。
3. 标签、宏和生命周期不进入 1.0，因此不建立对应名称空间。
4. 每个解析结果绑定唯一 DefId；不得将一个 Import 解析成随上下文变化的一组候选。

```x
struct Parser {}
fn Parser() -> Unit {} // X-E2004
```

## 7. 可见性与 Facade

1.0 候选采用 module/package/public 三层可见性。`package` 仅为紧随 `pub (` 后的上下文词，不加入全局硬关键字：

```x
struct ParserState {}                 // 当前模块
pub(package) struct ParsedModule {}   // 当前包
pub struct Compiler {}                // 包外
```

规则：

- 默认 Item/字段是模块私有；
- `pub(package)` 对同一 Package 的模块可见，不对依赖包公开；
- `pub` 对包外公开，但是否可达还取决于 `lib.x` Facade；
- 下游只能访问从包 Facade 可达的公开 Item，不能钻入内部路径；
- 公开签名不能泄漏比自身可见性更低的类型；
- 不提供 `protected`、friend 列表、`pub(super)` 或任意祖先范围。

产生式为 `visibility = "pub", [ "(", "package", ")" ]`，并统一用于 Item、字段、`use` 与允许显式可见性的 impl item。Formatter 必须写作 `pub(package)`；其他位置的 `package` 仍是普通标识符。

`pub(package) use current_pkg::a::Item;` 创建仅同一 Package 可见的重导出绑定：包内其他模块必须通过包含该声明的绝对模块路径访问它，它不进入 `lib.x` 包外 Facade、公开 API Diff 或下游名称解析。普通 `use` 仍只影响当前模块，`pub use` 仍是包外 Facade 边；禁止对依赖包来源或不可访问 Item 扩大可见性。

## 8. `::`、`.` 与调用

- `::` 左侧是非运行时求值的包、模块、类型、Trait 或关联路径；用于模块成员、关联函数/常量和枚举变体。
- `.` 左侧是运行时值且恰好求值一次；用于字段访问和方法调用。
- 禁止同时提供 `Type.method()` 与 `Type::method()`，或 `value::method()` 与 `value.method()`。

```x
let user = User::new(id, name);
let error = LookupError::NotFound(id);
let renamed = user.rename(new_name);
```

## 9. Receiver 与无重载规则

1. Receiver 只允许 `self: Self`、`self: &Self`、`self: &mut Self`。
2. Receiver 必须是第一参数、最多一次；静态关联函数不得声明 Receiver。
3. 同一模块不能按参数或返回类型重载函数。
4. 同一类型的固有方法/关联函数共享名称集合，不允许同名后依靠 `.`/`::` 消歧。
5. Trait 可以声明同名方法，但调用点必须满足第 10 节的唯一候选规则。

## 10. Trait 方法查找

对 `value.method(arguments)`：

1. 先确定 `value` 的静态类型，且只求值一次；
2. 收集该类型唯一可见的固有方法；
3. 收集当前模块显式导入、且该类型具有唯一合法 impl 的 Trait 方法；
4. Receiver 只做一次、由声明精确决定的调整：`self: Self` 移动或复制该值，`self: &Self` 创建共享借用，`self: &mut Self` 要求可变 Place 并创建独占借用；
5. 不做多级自动解引用、用户定义转换、临时克隆或按失败顺序反复尝试不同 Receiver；候选在其唯一调整通过类型和借用检查时才“适用”；
6. 只有一个适用候选时调用成功；零候选报未找到；多个候选报歧义，不根据返回类型、Import 顺序或“更具体”猜测；
7. 歧义使用完全限定调用，并传入与声明一致的 Receiver 表达式：`Trait::take(value)`、`Trait::read(&value)` 或 `Trait::write(&mut value)`。

```x
let display = Display::format(&value);       // format(self: &Self)
let debug = Debug::format(&value);           // format(self: &Self)
Hasher::reset(&mut hasher);                  // reset(self: &mut Self)
let bytes = Encoder::finish(encoder);        // finish(self: Self)
```

Trait 必须显式导入才参与方法候选，Prelude Trait 除外。隐式借用的生命周期覆盖本次调用并受普通借用规则约束；`value` 不是可变 Place 时，`self: &mut Self` 候选不适用。

## 11. 字段与方法同名

1. 同一类型禁止声明同名字段与固有方法。
2. 如果 Trait 方法与字段同名，`.name` 始终是字段；`.name()` 表示调用该字段值。字段不可调用时报类型错误，不回退到 Trait 方法；Trait 调用必须按其 Receiver 写成 `Trait::name(value)`、`Trait::name(&value)` 或 `Trait::name(&mut value)`。
3. 字段调用和方法调用的选择不能依赖返回类型或失败后的候选回退；解析结果必须在类型检查前保持稳定。

## 12. Prelude

- Prelude 是按 Edition 固定、版本化且可显式关闭的精确名单。
- 1.0 只考虑 `Bool`、固定数值类型、`Unit/Never`、`Option/Result` 和明确登记的 `Some/None/Ok/Err` Alias；这四个裸名称解析到关联变体的同一 DefId，不是隐式注入全部枚举变体。
- Prelude 不包含 I/O、网络、常见工具函数或会大规模改变方法候选的扩展 Trait。
- 已发布 Edition 不得静默向 Prelude 加入产生名称或方法冲突的 Item。
- `no_std`、编译器和符合性测试必须支持关闭 Prelude。

## 13. 诊断

至少提供稳定代码：

| 诊断 | 含义 |
|---|---|
| `X-E2001` | 文件路径规范化后冲突 |
| `X-E2002` | 路径第一段不是当前包或直接依赖 |
| `X-E2003` | 尝试导入未直接声明的依赖 |
| `X-E2004` | Item Namespace 重名 |
| `X-E2005` | Import/Alias 冲突 |
| `X-E2006` | `pub use` 环 |
| `X-E2007` | 可见性不足或绕过 Facade |
| `X-E2008` | 多个方法候选 |
| `X-E2009` | 字段和方法冲突 |

规则追溯使用 `RULE-MOD-*` 与 `RULE-METHOD-*`，不得复用诊断码表达规范身份。

## 14. 验收

- 多文件 compile-pass/fail 覆盖当前包、直接/传递依赖、Alias、Facade、Prelude 和方法冲突；
- 名称解析 Dump 在 Windows/Linux/macOS、随机文件顺序、冷/热缓存和并行度变化时字节一致；
- 公开 API Diff 只计算 Facade 可达项，并保留重导出 Provenance；
- 增量修改一个 Import 只失效受影响作用域，不导致无关包全量重算；
- 至少一个 100 包、10,000 文件合成 Workspace 完成全量/增量基准；
- Parser、formatter、LSP、文档生成和编译器共享同一规范数据源。

## 15. 未决问题

| 问题 | Owner | 截止阶段 | 未达成一致时的失败回退 |
|---|---|---|---|
| Prelude 的最终精确名单 | Language + Std WG | P1 名称解析冻结前 | 只保留基础类型与 `Option/Result`，Trait 全部显式导入 |
| 类型引用环与布局计算边界 | Type-system WG | P1 类型布局实现前 | 拒绝跨模块类型引用环 |
| `lib.x` 与多二进制 Target 的共享可达性 | Module WG | P1 多 Target 支持前 | 每个 Target 只经自身 Facade 根计算可达性 |
