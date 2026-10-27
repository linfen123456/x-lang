# ADR-0007 1.0 语言核心取舍与矛盾裁决

> 状态：Accepted｜版本：2.1.0｜负责人：Language Lead｜最后更新：2026-10-22
> 类型：ADR｜新增（v2）。本 ADR 记录 v2 规范中每一项关键取舍的理由，并裁决审查报告中列出的矛盾（C 编号见 `X-Lang架构深度审查报告.md` §6.1）。

## 决策清单

| # | 决策 | 裁决的矛盾 | 理由 | 落点 |
|---|---|---|---|---|
| D1 | 原始类型名全部小写（`i32`、`bool`、`usize`、`str`、`never`）；unit 只写作 `()`；不提供大写别名 | C1 | 与 C/Rust/Go/Zig 一致，学习和迁移成本最低；小写把原始类型与名义类型（UpperCamel）区分开；遵守“一种写法”原则 | [02](../../specs/language/02-types-traits.md) §2 |
| D2 | 赋值：先求值左侧 Place，再求值右侧，然后写入 | C2 | 与“处处从左到右”的总规则一致；旧语言大纲中“右侧先求值”的写法作废 | [03](../../specs/language/03-expressions-patterns.md) §3 |
| D3 | `defer` 不进入 1.0，用 `std::guard::on_exit` 替代 | C3 | RAII 已能覆盖所有场景，避免两套清理机制 | [04](../../specs/language/04-ownership-borrowing.md) §9 |
| D4 | WASM 在 P3 做探针，P5 升为 Tier 2 | C4 | 依赖 std/PAL 成熟；P0 只做 Linux + Windows 双主机，P1 增加 macOS（ADR-0008 K5） | [platforms](../platforms.md) |
| D5 | XUI：P3 原型 → P4 Web 样例 → P5 桌面/移动；小程序放研究赛道 | C5、C6 | 统一采用总纲与 RFC-0011 的时间线 | [ecosystem](../ecosystem.md) |
| D6 | 1.0 没有通用构建脚本 | C7 | 构建的确定性与供应链安全 | [包规范](../../specs/packages/manifest-lock-build.md) §6 |
| D7 | `#spec`、`pure`、静态反射不在 P2 进入核心 | C8 | ADR-0003 的楔子；用 `@derive` 闭集、doc-test、`x vet` 替代 | [登记册](../requirements/registry.md) |
| D8 | Workspace 固定 5 个成员 | C9 | 单一数值，避免“4–6”与“恰好 5”两种说法 | [ADR-0002](ADR-0002-repository-modular-monolith.md) |
| D9 | Safe/UB 清单在 P2 冻结；并发模型在 P2 落地 | C10 | 旧波次 A 要求在 P0→P1 关闭，不可达 | [07](../../specs/language/07-unsafe-ffi.md)、[08](../../specs/language/08-concurrency.md) |
| D10 | 新增硬关键字 `static`；`static` 只能不可变，类型必须 `Sync`；没有 `static mut` | C14 | 规范中本来就需要 Static Place 根，FFI 也需要固定地址 | [02](../../specs/language/02-types-traits.md) §8 |
| D11 | 生命周期采用“隐式区域 + 唯一省略规则”，1.0 没有 `'a` 语法 | C15 | 让“1.0 无生命周期语法”和“返回借用需要约束”同时成立；表达力限制已登记 | [04](../../specs/language/04-ownership-borrowing.md) §4–5 |
| D12 | 导出唯一写法：`@export("sym") pub extern "C" fn` | C16 | 删除旧语法中的 `export_function` 重复产生式 | [07](../../specs/language/07-unsafe-ffi.md) §7 |
| D13 | 导入根名 = 包名中的 `-` 换成 `_` | C17 | 闭合旧版 RFC-0003 的未决问题 | [06](../../specs/language/06-modules.md) §3 |
| D14 | 优先级调整：位运算高于比较运算；比较运算不可结合 | 新发现 | 旧文法中 `a & b == c` 会被解析为 `a & (b == c)`，这是 C 的经典陷阱 | [01](../../specs/language/01-lexical-syntax.md) §4 |
| D15 | 块类表达式可以不带 `;` 作为语句；`return/break/continue` 是类型为 `never` 的表达式 | C22 | 修复旧文法要求 `if` 语句后加 `;` 的缺陷 | [01](../../specs/language/01-lexical-syntax.md) §5.1 |
| D16 | 表达式中显式泛型实参写作 `::<T>` | 新发现 | 旧文法中 `value_path` 不能携带泛型实参 | [01](../../specs/language/01-lexical-syntax.md) §5 |
| D17 | 新增属性 `@test @derive @cfg @deprecated @must_use @non_exhaustive @inline @cold @tailcall @allow/@warn/@deny @link` | 审查报告 L-06 | 旧规范只登记了 `@repr/@export`，导致无法写测试和条件编译 | [01](../../specs/language/01-lexical-syntax.md) §7 |
| D18 | 整数溢出在所有构建配置下都会 panic | 新发现（旧文档写“暂定 checked”） | 安全默认，跨 Profile 行为一致；性能代价通过基准监控（[performance](../performance.md) §4） | [03](../../specs/language/03-expressions-patterns.md) §4 |
| D19 | 1.0 只有静态分派，没有 `dyn` | 新发现 | 降低 P1/P2 的工作量；用枚举 + 泛型覆盖 CLI/服务端场景 | [02](../../specs/language/02-types-traits.md) §6 |
| D20 | `==` 和 `<` 对用户类型分别经由 `Eq`、`Ord`；算术运算不能重载 | 新发现 | 集合与排序需要；避免完整的运算符重载 | [02](../../specs/language/02-types-traits.md) §6 |
| D21 | Prelude 加入 `print/println/eprint/eprintln` 等函数 | 对 RFC-0001 的修改 | CLI 楔子的易用性；它们只写 stdout/stderr | [06](../../specs/language/06-modules.md) §10 |
| D22 | 方法调用时，Receiver 为引用的情况下允许一次自动解引用 | 对 RFC-0001 的修改 | 否则 `r.len()`（`r: &String`）无法调用 | [06](../../specs/language/06-modules.md) §9 |
| D23 | 加入 `f"…{x}…"` 插值字符串（P1） | 新发现 | 没有宏时，格式化输出的唯一简洁写法 | [03](../../specs/language/03-expressions-patterns.md) §7 |
| D24 | 1.0 只提供 `panic=abort`；unwind 推迟到 1.0 后，经 RFC 评估（[ADR-0008](ADR-0008-pre-kickoff-decisions.md) K3） | C 系列 | 运行时、FFI 边界与测试矩阵最简单 | [05](../../specs/language/05-errors-panics.md) §3 |
| D25 | 1.0 之前的 Edition 名称是 `"preview"`；首个稳定 Edition 以 1.0 发布年份命名（K10） | 新发现 | 避免提前绑定年份 | [release](../release.md) §2 |
| D26 | 保留字 `async await defer dyn macro throw try yield` | 新发现 | 方便后续 Edition 平滑引入，并给出友好的 `X-E9002` 诊断 | [01](../../specs/language/01-lexical-syntax.md) §3.2 |

## 状态

[ADR-0008](ADR-0008-pre-kickoff-decisions.md) K1 已确认：维持以上全部决策，本 ADR 转为 Accepted。

## 可推翻条件

满足下列任一条件，经 Language Lead 批准后，可以用新 ADR 取代本表中的某一项：
- 第一次易学实验（P2）显示某项决策的失败率超过 30%；
- 基准显示 D18 的开销超过 [performance](../performance.md) 规定的阈值。
