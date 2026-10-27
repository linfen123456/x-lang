> 已归档：见 v2 [specs/language/02-types-traits.md](../../../specs/language/02-types-traits.md)

# RFC-0006：类型、值、Place 与确定求值

> 状态：Proposed
> 日期：2026-08-18
> 目标版本：X-Lang 1.0 候选
> 依赖：RFC-0005
> 相关缺口：`GAP-LANG-03`、`GAP-LANG-04`
> 正式产物：接受后生成 `specs/language/types-and-evaluation.md`。

## 1. 模型

- **Value**：已经求值、可复制或移动的值；
- **Place**：指向一处存储位置的表达式及投影链；
- **Temporary**：表达式求值产生、在规定临时作用域结束时清理的匿名存储；
- **Constant**：编译期可求值且不观察时间、随机、网络、未声明环境或文件的值。

Place 根可以是局部绑定、参数、静态对象或解引用；投影可以是字段、tuple 索引、内建索引或进一步解引用。`*ptr`、`(*ptr).field`、`tuple.0`、`items[i]` 均先形成普通表达式，再由类型检查器分类。

## 2. Assignment

Parser 不维护第二份受限 Place 文法。`left = right;` 先生成 Assignment AST；类型检查器要求 left 是可写 Place，且权限、初始化和类型满足赋值规则。函数调用结果、算术值和只读借用不是可写 Place。

复合赋值按“左侧求值一次、读取旧值、右侧求值、执行运算、写回”定义，不脱糖成会重复求值左侧的源码表达式。

## 3. 求值顺序

- 调用 Receiver、实参、操作数、索引和结构体字段初始化按源码从左到右；
- 每个子表达式恰好求值一次；
- `&&`、`||` 短路，未选择分支不求值；
- Assignment 先确定左侧 Place，再求值右侧，最后写入；
- `match` Scrutinee 只求值一次；Pattern 不重复求值用户表达式；
- 优化可以重排不可观察操作，但不能改变值、诊断外的运行时副作用、Drop Trace 或终止类别。

## 4. 类型边界与转换

- 公开函数、字段、常量、Trait、extern 和 export 边界必须显式写类型；
- 私有局部绑定和非递归表达式允许局部推断，不跨模块或全程序推断；
- 泛型调用不能依赖返回类型之外的远程上下文猜测多个候选；
- `as` 只允许规范白名单中的无损数值扩宽、表示保持转换和明确安全的引用调整；
- 窄化使用 `T::try_from`，环绕使用 `T::wrapping_from`；指针/位重解释仅能通过受审计的 unsafe API。

## 5. 诊断和验收

首批符合性语料固定使用：`X-E3001` 公开边界缺少显式类型、`X-E3002` 非白名单转换、`X-E3003` 推断存在多个候选、`X-E3008` 非法或不可写 Place。Rule ID 使用 `RULE-TYPE-*`、`RULE-EVAL-*`；新增诊断必须登记具体四位编号。

- compile-pass：所有 Place 根/投影、显式转换和局部推断；
- compile-fail：向 Temporary、只读借用或调用结果赋值，链式隐式转换，公开类型省略；
- AST/HIR Snapshot：Assignment 左侧保留普通 Expression AST，HIR 单独记录 Place 分类和转换种类；
- 诊断 Snapshot：`X-E3001/3002/3003/3008` 固定主 Span、实际/期望类型、Rule ID 和安全 Fix-it；
- 边界反例：带副作用的 Receiver/索引不得重复求值，窄化、位重解释和跨模块推断不得借 `as` 绕过；
- run-pass：带副作用 Receiver、索引和复合赋值证明只求值一次；
- MIR/解释器 Snapshot：左到右事件与 Drop Trace 固定；
- 跨优化级别和后端差分不得改变可观察结果。
