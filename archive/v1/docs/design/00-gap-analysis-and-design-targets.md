> 已归档：见 v2 [docs/changelog.md](../../../../docs/changelog.md)

# 缺口分析与设计目标

> 状态：Proposed｜日期：2026-08-18  
> 性质：把设计审查结论转为可关闭的实现设计目标；不是语言规范，不新增需求 ID。  
> 依据：[语言设计审查](../../README.md)、工程大纲第十二篇、GAP 波次 A、RFC-0005～0008、ADR-0002。

## 1. 审查结论摘要

| 判定 | 说明 |
|---|---|
| 文档治理 | 强：权威顺序、追溯、Proposed≠规范 |
| 1.0 宪法 | 自洽：小核心、所有权、Result、显式边界 |
| 实现就绪 | 弱：无代码；语义 RFC 过薄；工具链 RFC 相对过厚 |
| 范围风险 | 高：回归路线大量 `RETURN` 与 1.0 收缩并存 |

当前综合档约 **C+（文档大纲）**。冲到可运行 **A** 靠实现设计 + P0 切片；冲到场景内 **SS** 靠唯一楔子与证据，不靠扩大面积。

## 2. 问题 → 设计交付

| ID | 问题 | 影响 | 关闭物 | 验收 |
|---|---|---|---|---|
| G1 | 无端到端实现路径验证 | 规范无法证伪 | [p0-vertical-slice.md](p0-vertical-slice.md) + ADR-0002/0004 | `x run` 跑通 Hello World；CI 可复现 |
| G2 | RFC-0006/0007/0008 不足以编码 | 借用/类型/错误无法开工 | [semantic-pipeline.md](semantic-pipeline.md) | 每 Pass 有输入/输出/不变量/诊断映射 |
| G3 | 无符合性 runner / 证据链 | Proposed 无法晋级 | [conformance-and-gates.md](conformance-and-gates.md) | Rule ID → 语料 → 门禁可自动跑 |
| G4 | `defer` 总纲排除 vs 回归 `RETURN` | 实现范围漂移 | [ADR-0003](../decisions/ADR-0003-p0-language-profile-and-labs-freeze.md) | P0–P4 不实现 `defer`；回归项降级 |
| G5 | UI/ML/ZKP/Agent 等 `RETURN` 挤占主线 | 永远 B 档平台愿景 | ADR-0003 Labs 隔离 | P0/P1 工作包禁止这些依赖 |
| G6 | Rust/LLVM 仍标「待决策」 | 探针无法锁定版本 | [ADR-0004](../decisions/ADR-0004-rust-llvm-host-baseline.md) | toolchain/LLVM 版本写入锁与 CI |
| G7 | 语义/工具链深度失衡 | 先造 Cargo 克隆、语言空心 | 语义管线优先于完整 XPM | P0 仅最小包图（P0-T10），完整 XPM 在 P3 |
| G8 | GAP-GOV-01 未跑通 | 状态机空转 | ADR-0003/0004 与核心 RFC 经独立评审 | ≥2 ADR、≥3 RFC 走完评审模板；仅评审通过者标 Accepted |

## 3. D0 冲突关闭与接受检查表

D0 由语言/编译器 Owner 维护同一冲突清单，符合性 Owner 校验语料，安全 Owner 评审信任边界；各 RFC 仅在本体完成评审后独立改为 Accepted。设计文档不能代替 RFC 裁决。每条记录至少填「Rule ID｜诊断码或不适用理由｜正例/反例｜Owner｜冲突引用｜失败回退｜评审状态」。未能裁决的规则不得写为已稳定；缩小 P0 子集并明确拒绝未实现语法。

| 冲突域 | 候选权威与 D0 检查 | 失败回退 |
|---|---|---|
| 词法/语法 | RFC-0005 与最小剖面：关键字、错误 token、结构体/函数正反例 | 仅保留经评审的词法/语法子集 |
| 类型/求值 | RFC-0006/0007：Place、赋值、求值顺序和诊断码一致 | 不接受未定义的隐式转换或副作用顺序 |
| 所有权/Drop | RFC-0007/0008 与语义管线：移动、清理恰好一次、返回/`?`/panic/abort 路径 | 限定 P0 为不含用户 Drop 的子集；未支持边报错 |
| 错误 | RFC-0008：`Result/?` 与 panic 终止类别、优化差分反例 | 保留显式返回；不发布不完整 `?` 行为 |
| 模块 | RFC-0001：单/双文件名称和可见性、失败诊断 | 缩小可用模块子集并公布限制 |
| 包图 | RFC-0003/0004：PackageId、三包 Path 图、确定性 Action DAG、环诊断 Rule ID | 不进入最终 P0；不得把单包 Hello World 视为通过 |
| 工具链 | ADR-0004：Rust/LLVM/链接器精确版本、主机 triple 与升级探针 | 保持 Proposed，不对外承诺可复现工具链 |

D0 退出材料包括带 Owner 签名的冲突表、各 RFC 正反语料清单、ADR 评审结果及待办回退记录；P0 最终自动语料阻断见[符合性门禁](conformance-and-gates.md)。

## 4. 非目标（本轮设计明确不做）

- 不把 319 个 ID 全部写成实现设计；
- 不预建 `specs/`、空 crate、Web/UI/ML 目录；
- 不在本目录重写语言可观察语义全文（补算法与接口，规则仍以 RFC 为准）；
- 不宣称性能/安全领先；
- 不引入用户宏、async、comptime、默认 GC、类继承。

## 5. P0 必须关闭的 GAP（波次 A 子集）

实现设计至少覆盖到可执行任务卡，对应工程大纲 12.8 波次 A：

| GAP | 本目录对应章节 |
|---|---|
| `GAP-LANG-01` | ADR-0003 剖面与非目标 |
| `GAP-LANG-02` | P0 切片语法子集 + RFC-0005 |
| `GAP-LANG-03`～`05` | 语义管线（P0 子集；完整 Safe X 仍属后续） |
| `GAP-LANG-07` | P0 单文件/双文件最小模块；完整 RFC-0001 在 P2 |
| `GAP-COMP-01` | P0 切片 ABI 探针节 |
| `GAP-COMP-02` | P0 Workspace 成员与拆分禁令 |
| `GAP-GOV-01` | ADR-0003/0004 进入评审；RFC Accept 另轨 |

`GAP-LANG-06`（并发内存模型）**不进入 P0 实现设计正文**；P0 仅单线程 Hello/CLI，并发 RFC 独立跟踪。

## 6. 成功标准

1. 任一实现者可仅凭 `docs/design/*` + 引用 RFC，写出 P0 crate 骨架与首批 Pass，而无需猜测模块边界；
2. 每个设计验收项可映射到 `conformance/` 或 `tests/end-to-end/` 命令；
3. 与回归路线冲突时，以总纲已有约束为准；ADR-0003 仍是 Proposed，须经批准后才能作为额外剖面约束，并回写回归表状态。
