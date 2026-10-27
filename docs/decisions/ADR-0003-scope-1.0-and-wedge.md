# ADR-0003 1.0 范围与唯一楔子

> 状态：Accepted｜版本：2.1.0｜负责人：Project Lead｜最后更新：2026-10-22
> 类型：ADR｜取代：旧 ADR-0003（并且以本 ADR 为准，修正了旧回归路线中与它冲突的条目）

## 背景

原始需求覆盖了语言、UI、AI、ML、网络、嵌入式和研究性想法。旧回归路线又把 46 项标为 RETURN，其中多项排在 P2，与“1.0 收缩”的目标冲突。

## 决策

1. **唯一楔子**：P0–P4 只服务“安全原生 CLI 与服务端程序”。
2. **不进入 1.0** 的内容（替代方案见 [vision](../vision.md) §4）：
   - 用户宏、通用 comptime、async/await、`defer`、GC、继承、异常、函数重载；
   - `dyn`、显式生命周期、管道运算符、命名/默认参数、Map/JSON 字面量；
   - Effect 系统与 `pure`、`#spec` 契约语法、通用反射与用户派生、通用构建脚本。
3. 对旧回归路线的修正：XLF-03-001、XLF-03-003、XLF-09-001、XLF-10-002、XLF-10-012 不在 P2 进入核心，改为 1.0 后的 RFC 候选，或由工具/生态替代（见[登记册](../requirements/registry.md)）。
4. UI、ML、AI、ZKP、脑机接口等**不进入核心**，分别由 eco 或 labs 承接。
5. Labs 默认关闭，任何 Stable 工件都不得依赖 Labs。
6. 任何想把 1.0 排除项提前纳入的提议，都必须先提交 RFC，并经 Project Lead 与 Language Lead 共同批准。

## 后果

- P2 的范围聚焦在 Core-CLI 稳定子集上，见 [roadmap](../roadmap.md)。
- [RULE-STAGE-EXCLUDED] 编译器遇到已排除的语法时，必须报 `X-E9002` 并给出替代建议，不能报晦涩的语法错误。
