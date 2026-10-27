# ADR-0003：P0/1.0 语言剖面冻结与 Labs 隔离

## 状态

Proposed

## 日期

2026-08-18

## 背景

设计审查表明：1.0 候选宪法与回归路线之间存在范围张力——总纲与语言大纲将 `defer`、async、宏、UI/ML 等排除出 1.0 核心，但价值回归文档仍将大量能力标为 `RETURN`（含 `XLF-10-002 defer` 标为 P1–P2）。若不冻结实现剖面，P0 纵向切片会被远期能力挤占，语义 RFC 也无法收敛。

同时需要明确「楔子」：P0–P4 只服务原生 CLI/系统工具/服务端工程闭环，不追求万能平台。

## 决策

### 1. P0–P4 实现剖面（冻结）

允许进入实现与符合性门禁的能力，仅来自：

- 已 `Proposed`/`Accepted` 且列入当前阶段切片的 RFC（P0 见 [p0-vertical-slice.md](../design/p0-vertical-slice.md)）；
- [语言规范大纲 §1.8](../X-Lang语言规范与学习研究大纲.md) 1.0 候选设计宪法中的核心约束。

下列能力在 **P0–P4 禁止实现为语言表面或核心运行时默认行为**：

| 能力 | 处置 |
|---|---|
| `defer` | **不进入 1.0**；与总纲 §12 一致。清理只通过 RAII/`Drop` |
| `async/await`、用户宏、通用 comptime、默认 GC | 不进入 1.0 |
| 类继承、异常、函数重载、JSON/map 字面量 | 不进入 1.0 |
| UI / Tensor-ML / ZKP / BCI / Agent 提权 | 不得进入核心 Workspace 或阻塞 P0–P4 门禁 |

### 2. `XLF-10-002`（defer）复审降级

将价值回归中的 `RETURN / P1-P2` 调整为：

- **复审结论**：`CONDITIONAL`
- **条件**：核心 Drop/panic 模型 `Stable` 之后，经独立 RFC 证明与 RFC-0007/0008 无双重释放、顺序可测试，方可进入 **1.0 之后 Edition** 候选
- **P0–P4**：任何 `defer` 语法必须 `X-E9001`（未实现）或词法拒绝，不得部分实现

（权威行更新见价值回归文档对应表项。）

### 3. Labs 隔离门禁

- 标为 `RESEARCH` 或未满足条件的 `CONDITIONAL`/`RETURN` 项，物理上只能进 `labs/` 或联邦仓库，且 **不得** 成为 `compiler`/`runtime`/`library-core` 的构建依赖；
- P0/P1 Workspace 成员集合以 ADR-0002 为准，不因回归 `RETURN` 自动增员；
- 发布说明禁止将 Labs 能力表述为 1.0 Stable。

### 4. 产品楔子（工程优先级）

P0–P4 唯一优先楔子：**确定性原生工具链上的安全 CLI/服务端子集**（模块解析确定、构建图可复现、诊断 Rule ID 稳定）。其他楔子（AI 语义面、垂直 DSL 等）不得并行扩张核心语法。

## 替代方案

### 维持 defer 为 P1 RETURN

拒绝。与总纲、RFC-0007/0008「清理以 Drop 为唯一核心模型」冲突，制造双重清理语义。

### P0 同时启动 UI/ML 项目

拒绝。违反 ADR-0002 与 GAP-COMP-02，必然空心化语言核心。

### 不做剖面冻结，仅靠任务自觉

拒绝。审查已证明文档层存在互相竞争的权威信号，必须用 ADR 裁决。

## 后果

### 正面

- P0 实现设计与符合性门禁有单一范围；
- `defer` 矛盾关闭；
- 回归 `RETURN` 不再自动等同「下一迭代编码」。

### 负面 / 风险

- 部分原始愿景支持者会视为收缩；需在回归文档写清 CONDITIONAL 条件；
- 若未来 Accept defer RFC，本 ADR 必须被 Supersede，不得静默推翻。

## 关联

- 实现设计：[docs/design/](../design/README.md)
- 工程大纲第十二篇 P0
- GAP：`GAP-LANG-01`、`GAP-COMP-02`、`GAP-GOV-01`
