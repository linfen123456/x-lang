# 设计理念、目标与范围分层

> 状态：Accepted｜版本：2.1.0｜负责人：Project Lead｜最后更新：2026-10-22
> 类型：Vision｜唯一负责：设计理念、目标/非目标、范围分层（track）定义。

## 1. 结论

1. X-Lang 1.0 = **安全（所有权 + 借用）+ 原生性能（LLVM）+ 显式简单语法 + 一体化工具链**，目标场景是 CLI 与服务端。
2. 原始 12 份需求的所有诉求，都在[需求登记册](requirements/registry.md)中有去处。去处有四种轨道：`core`、`toolchain`、`eco`、`labs`。
3. 判断一项能力进不进核心，标准只有一条：它是否必须改变**语言语义或编译器**才能实现。能用库、工具或协议实现的，一律不进核心。

## 2. 设计理念（取舍原则，按优先级）

| # | 原则 | 落地规则 | 来源 |
|---|---|---|---|
| 1 | 安全默认 | Safe 代码无数据竞争、无悬垂引用、无未定义行为；整数溢出、越界、除零都确定地触发 panic | 1.txt“安全”、5.txt |
| 2 | 显式优于隐式 | 无隐式转换、无隐藏 `From`、无重载、无异常、无自动插锁；可能失败的操作体现在类型上 | 1.txt“清晰”、ADR-0003 |
| 3 | 一种写法 | 同一语义只保留一种语法：`()` 是唯一 unit 写法，导入只有精确 `use` | 1.txt、11.txt |
| 4 | 零成本抽象可验证 | 泛型单态化；抽象的代价必须能用基准或汇编证明，不能只靠口号 | 1.txt“高性能” |
| 5 | 确定性 | 名称解析、构建、Lockfile 在任何 OS、任何遍历顺序、任何并行度下结果相同 | 2.txt、11.txt |
| 6 | 工具友好（含 AI） | 稳定诊断码、机器可读 JSON、规范格式化器、查询 API；AI 只是查询 API 的一个消费者 | 3.txt |
| 7 | 小核心，大生态 | UI/ML/网络协议/云适配是库，不是关键字 | 4、6、9、12.txt |
| 8 | 证据晋级 | 每项能力按阶段门禁晋级；数值目标必须可复现测量 | 12.txt 性能表的修正 |

## 3. 目标（1.0，即 P4）

| 目标 | 可验收定义 |
|---|---|
| G-SAFE 安全 | 符合性套件覆盖 specs 01–08 的全部 `RULE-*`；Safe 代码的 fuzz 与差分测试中没有内存错误 |
| G-PERF 性能 | 运行时基准几何平均 ≤ 同算法 C（clang -O2）的 1.25 倍（见 [performance](performance.md)） |
| G-SIMPLE 易学 | 20 名未参与设计的开发者，80% 能在 2 小时内完成参考 CLI 任务（实验方法见 [testing](testing.md) §9） |
| G-TOOL 工具链 | `x init/check/build/run/test/fmt/doc/add/publish`、LSP、调试器全部可用 |
| G-PORT 跨平台 | 4 个 Tier 1 目标全部通过发布门禁（[platforms](platforms.md)） |
| G-SUPPLY 供应链 | 可复现构建、签名、SBOM、Lockfile 校验 |
| G-COMPAT 兼容 | 首个稳定 Edition 发布；Edition 内不做破坏性变更 |

## 4. 非目标（1.0 不做；1.0 之后可经 RFC 重新评估）

- 用户宏、过程宏、通用 comptime。替代：内置 `@derive` 闭集、`const fn`。
- async/await、M:N 协程。替代：作用域线程 + 通道；async 在 P5 以 Edition 引入。
- GC、继承、异常、函数重载、运算符重载（比较运算经 `Eq/Ord` 除外）、隐式转换。
- `defer`。替代：RAII Guard。
- 显式生命周期语法。替代：隐式区域策略，见 [04](../specs/language/04-ownership-borrowing.md)。
- Trait 对象 `dyn`。替代：枚举 + 泛型。已经由 [ADR-0007](decisions/ADR-0007-language-core-decisions.md) D19 决定，并经 ADR-0008 K1 确认；1.0 后可以经 RFC 引入。
- 管道运算符、命名/默认参数、Map/JSON 字面量、范围运算符。
- 语言内建 Tensor/GPU/UI/网络协议/AI 语义。

## 5. 范围分层（track 定义，全体系唯一）

| track | 名称 | 包含 | 兼容承诺 | 发布方式 |
|---|---|---|---|---|
| `core` | 核心语言 | 语言规范、编译器、运行时 xrt、core/alloc/std | Edition 内稳定 | 随工具链发布 |
| `toolchain` | 官方工具链 | `x` CLI、XPM/XBuild、fmt、doc、test、LSP、MCP、调试集成 | 命令与 JSON Schema 版本化 | 随工具链发布 |
| `eco` | 独立生态 | `x-json`、`x-http`、`x-server`、XUI、`x-ai-tools`、`x-ml` 等官方/社区包 | 各包自己的 SemVer | 独立仓库，经 Registry 发布 |
| `labs` | 研究赛道 | GC、ZKP、语言级 Effect、硬实时、通用重放等 | 无 | 实验仓库；必须有退出报告 |

依赖铁律：
- `core` 和 `toolchain` **不得**依赖 `eco` 或 `labs`。
- `eco` 只能依赖公开稳定 API。
- `labs` 不得被任何 Stable 工件依赖。

## 6. 原始需求的落地原则（不删需求，只改落地方式）

| 处置 | 含义 | 例子 |
|---|---|---|
| adopt | 原样落地 | XLF-01-004 LLVM 后端 |
| adapt | 修正后落地（缩小范围、调整阶段、改成显式） | XLF-01-009 协程/CSP：1.0 先用线程 + 通道，P5 再上 async |
| replace | 以可行替代满足同一诉求 | XLF-04-001 内建 Tensor → `x-tensor` 库 + 互操作 |
| research | 研究赛道，有预算和退出条件 | XLF-07-008 ZKP |

不可行或不宜进核心的典型条目及替代方式（完整列表见[登记册](requirements/registry.md)）：

| 原始诉求 | 不进核心的理由 | 替代落地 |
|---|---|---|
| 内建 Tensor/自动微分/GPU Kernel（4.txt） | 相当于再造一个 ML 编译器，超出团队规模 | `x-tensor` 库 + ONNX/DLPack 互操作；Kernel 生成进研究赛道 |
| 用户态协议栈 / DPDK 进 std（4.txt） | 安全与维护成本高 | std 只提供 TCP/UDP；`x-http` 等生态包；内核旁路作为可选适配器 |
| 小程序模板转译（6.txt） | 平台规则变化快，WASM 支持受限 | 研究赛道实验：JS 胶水 + WASM 逻辑包 |
| ZKP 闭包、脑机接口（7.txt） | 研究级难题，涉及伦理/法规 | 研究赛道；HID/触觉走生态适配 |
| `@intend` 自动生成算法（7.txt） | 涉及停机问题，不可判定 | `x verify` 有界模型检查实验 |
| 编译器自动插读写锁（5.txt） | 静默改变语义，可能引入死锁 | 编译期报 `X-E7001/7003`，并给出 `Mutex/RwLock` 修复建议 |
| CPU/GPU 同一指针类型（5.txt） | 违背设备内存模型 | 显式 `ManagedBuffer` API |
| 12.txt 性能承诺表（如“< 1ns”） | 没有环境和对照 | [performance](performance.md) 中的可测目标与基准 |
