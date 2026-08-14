---
doc_id: SPEC-LANG-CORE
title: X-Lang 核心语言规范（P0–P2）
status: draft
maturity: CORE
owner: language-architecture
depends_on: [SPEC-INDEX]
trace: [XLF-01-002, XLF-01-006, XLF-01-010, XLF-02-002, XLF-10-002, XLC-CORE-001..009]
---

# X-Lang 核心语言规范

## 目标与非目标

定义可移植的词法、语法、类型、函数、模块、错误和版本行为，支持 Rust+LLVM MVP。宏高级特性、运行时 GC、动态原型链和完整效果证明不属于本文件的稳定承诺。

## 规范条文

### XSP-LANG-001 源码与词法

源码按 UTF-8 解释；实现必须保留行列和字节偏移。空白通常分隔 token，注释不产生语义；标识符不得与关键字冲突。非法 UTF-8、未闭合字符串和未知转义必须报诊断，不得替换为 U+FFFD 后继续编译。

### XSP-LANG-002 求值与类型

每个表达式有静态类型；隐式窄化、布尔与整数互转、可失败转换均禁止。整数溢出策略由构建 profile 明确（Debug 检查，Release 采用 RFC 决定的 checked/wrapping API），不得依赖 LLVM 未定义行为。

### XSP-LANG-003 函数与返回

函数参数按声明顺序求值；返回值必须满足声明类型。`Result<T,E>` 表示可恢复失败，`panic` 表示程序不变量或不可恢复失败。跨 FFI 不得传播未声明的 panic/unwind。

### XSP-LANG-004 模块与可见性

模块导入形成有向图；循环初始化必须被拒绝或显式延迟。默认私有，公开 API 需要 `pub`，包解析使用锁文件和确定性版本求解。

### XSP-LANG-005 Edition 与兼容

语法或语义破坏性变化只能在新 Edition 引入；编译器必须提供迁移诊断，N-1 Edition 至少可检查并给出可操作迁移建议。未标记为 Edition 的变化不得改变已稳定程序的可观察行为。

## 正例与反例

```x
fn parse_id(s: String) -> Result<Int, ParseError> { s.to_int() }
let id = parse_id(input)?; // 正例：显式传播失败
```

```x
let n: Int = "42"; // 反例 X-E-TYPE-001：禁止隐式字符串转整数
```

## 边界与实现定义项

浮点 NaN、时间、Unicode 正规化、结构体 padding、链接器布局和诊断文本在对应 RFC 前均为实现定义；规则必须区分“未指定”“实现定义”“禁止行为”，不得把实现偶然性写成保证。

## 测试映射

`CON-LANG-LEX-*`、`CON-LANG-TYPE-*`、`CON-LANG-MOD-*`、`CON-LANG-ERR-*`：覆盖合法/非法源码、诊断码、Edition 迁移、跨 LLVM/解释器差分和快照。每项规则至少一个 pass、一个 fail 和一个边界样例。

## 性能、安全与回滚

解析和类型检查记录 P50/P95/P99 与内存峰值；宏和编译期求值必须有 token/时间/内存预算。发现规则回归时通过 Edition gate、编译器版本回退和迁移工具恢复，不直接修改既有 Edition。
