# X-Lang 文档体系 v2（总入口）

> 状态：Accepted｜版本：2.1.0｜负责人：Project Lead｜最后更新：2026-10-22
> 类型：Index｜本文件是**阅读顺序、文档地图、状态词表、权威顺序、规范用语**的唯一定义处。

## 1. 一句话

X-Lang 是一门**无 GC、所有权安全、编译到原生代码**的系统/应用语言，宿主实现为 Rust + LLVM。1.0 只有一个楔子：**安全原生 CLI 与服务端程序**。UI、AI、ML、平台扩展都在独立生态中逐步交付，研究项进入研究赛道。当前阶段是 **M0（启动）**，还没有代码；开工前的决策已经全部闭环（ADR-0008），可以直接按 [P0 工作分解](docs/design/p0-workplan.md) §7 初始化仓库。

## 2. 阅读顺序

| 角色 | 顺序 |
|---|---|
| 所有人 | 本文件 → [vision](docs/vision.md) → [roadmap](docs/roadmap.md) → [开工决策汇总 ADR-0008](docs/decisions/ADR-0008-pre-kickoff-decisions.md) |
| 编译器工程师 | [architecture](docs/architecture.md) → [compiler 设计](docs/design/compiler.md) → [specs/language](specs/language/01-lexical-syntax.md) 01–08 → [P0 工作分解](docs/design/p0-workplan.md) → [P1 工作分解](docs/design/p1-workplan.md) |
| 运行时/标准库 | [architecture](docs/architecture.md) §4 → [std 规范](specs/library/std-core.md) → [并发](specs/language/08-concurrency.md) → [平台](docs/platforms.md) |
| 工具链/包管理 | [ADR-0004](docs/decisions/ADR-0004-xpm-xbuild-layering.md) → [包与构建规范](specs/packages/manifest-lock-build.md) → [release](docs/release.md) |
| 测试/发布 | [testing](docs/testing.md) → [release](docs/release.md) → [performance](docs/performance.md) |
| 生态（UI/AI/服务端/ML） | [ecosystem](docs/ecosystem.md) → [需求登记册](docs/requirements/registry.md) |
| 贡献者/AI Agent | [GOVERNANCE](GOVERNANCE.md)（流程、分支、评审、AI 规则） |

## 3. 文档地图

| 路径 | 类型 | 唯一负责的事实 |
|---|---|---|
| [README.md](README.md) | Index | 阅读顺序、地图、状态词表、权威顺序、规范用语 |
| [GOVERNANCE.md](GOVERNANCE.md) | Governance | 角色、RFC/ADR 流程、分支/提交/评审、AI 协作规则 |
| [TOOLCHAIN.md](TOOLCHAIN.md) | Governance | 宿主工具链版本锁定 |
| [CHANGELOG.md](CHANGELOG.md) | Log | 文档体系与发布变更记录 |
| [MIGRATION.md](MIGRATION.md) | Log | 旧文档 → v2 映射与归档清单 |
| [docs/vision.md](docs/vision.md) | Vision | 设计理念、目标/非目标、范围分层（core/toolchain/eco/labs） |
| [docs/roadmap.md](docs/roadmap.md) | Plan | **阶段定义**（M0、P0–P5、R）、交付物、验收标准、退出门禁 |
| [docs/architecture.md](docs/architecture.md) | Architecture | 系统分层、编译器管线、运行时、工具链、LSP/MCP、XUI |
| [docs/repository.md](docs/repository.md) | Architecture | 仓库目录、crate/模块职责、依赖规则、拆分门禁 |
| [docs/design/compiler.md](docs/design/compiler.md) | Design | 编译器数据结构、查询、Pass 顺序、MIR、解释器 |
| [docs/design/p0-workplan.md](docs/design/p0-workplan.md) | Plan | M0/P0 任务分解、完成定义、示例与期望输出 |
| [docs/design/p1-workplan.md](docs/design/p1-workplan.md) | Plan | P1 任务分解、完成定义、示例与期望输出 |
| [docs/testing.md](docs/testing.md) | Design | 测试分层、符合性语料格式、差分、fuzz、基准 |
| [docs/performance.md](docs/performance.md) | Design | 性能设计与可测目标 |
| [docs/platforms.md](docs/platforms.md) | Policy | 目标平台 Tier 1/2/3 与晋级规则 |
| [docs/release.md](docs/release.md) | Policy | 版本号、Edition、渠道、产物、签名、变更日志、回滚 |
| [docs/risks.md](docs/risks.md) | Register | 风险登记与缓解 |
| [docs/ecosystem.md](docs/ecosystem.md) | Design | 独立生态包边界：XUI/Web、服务端、AI 工具、ML、x-json |
| [docs/decisions/](docs/decisions/ADR-0001-host-and-backend.md) | ADR | 架构决策 ADR-0001～0008（0008 是开工前决策汇总） |
| [docs/requirements/registry.yaml](docs/requirements/registry.yaml) | Register | **原始需求（XLF）唯一登记册**；[registry.md](docs/requirements/registry.md) 由它生成 |
| [specs/language/](specs/language/01-lexical-syntax.md) | Spec | 语言规范 01–08 |
| [specs/library/std-core.md](specs/library/std-core.md) | Spec | core/alloc/std 最小 API 契约 |
| [specs/packages/manifest-lock-build.md](specs/packages/manifest-lock-build.md) | Spec | x.toml、x.lock、XPM/XBuild 契约 |
| [specs/diagnostics/registry.yaml](specs/diagnostics/registry.yaml) | Register | **诊断码唯一登记册**；[registry.md](specs/diagnostics/registry.md) 由它生成 |
| [rfcs/0000-template.md](rfcs/0000-template.md) | Template | RFC 模板；以后的 RFC 都放在 `rfcs/` |
| [tools/doccheck.py](tools/doccheck.py) | Tool | 生成登记册 md，并检查链接、头部、术语、ID 覆盖 |

原始需求 `1.txt～12.txt` 是只读历史输入，永久保存在 [archive/original/](archive/original/)。旧文档保存在 [archive/v1/](archive/v1/)，v2 导入压缩包保存在 [archive/imports/x-docs-v2.zip](archive/imports/x-docs-v2.zip)，归档映射见 [MIGRATION](MIGRATION.md)。

## 4. 状态词表（全体系唯一）

| 状态 | 含义 | 可否据此实现 |
|---|---|---|
| Draft | 起草中，可随时改 | 否 |
| Proposed | 已提交评审，内容完整 | 可以做探针和原型；不得据此宣称稳定 |
| Accepted | 评审通过，成为实现依据 | 是 |
| Implemented | 已实现，并有符合性语料覆盖 | 是 |
| Stable | 进入兼容承诺（Edition 内不破坏） | 是 |
| Deprecated | 仍可用，计划移除 | 仅维护 |
| Superseded | 已被新文档取代（必须链接取代者） | 否 |
| Archived | 只读历史 | 否 |

规则：
- 文档头部的“状态”只能取上表的值。
- v2 全部文档的初始状态为 Proposed。
- 规范条目要从 Accepted 升到 Implemented，必须有对应的 `RULE-*` 语料（见 [testing](docs/testing.md)）。

## 5. 权威顺序（冲突时按此裁决）

1. 已 Accepted 的 `specs/`、ADR。
2. Proposed 的 `specs/`、ADR（本 v2 初始状态）。
3. [roadmap](docs/roadmap.md)（阶段与门禁）。
4. [architecture](docs/architecture.md)、[repository](docs/repository.md)、`docs/design/`。
5. [requirements 登记册](docs/requirements/registry.yaml)（需求去向）。
6. 其余 Policy/Register 文档。
7. 原始需求 txt（历史输入，只说明意图，不构成规则）。

发现冲突时：不得自行挑选一方继续实现。必须开 Issue 并标记 `conflict`，按 [GOVERNANCE](GOVERNANCE.md) §3 处理；修正后由 `tools/doccheck.py` 复检。

## 6. 规范用语

| 用语 | 含义 |
|---|---|
| **必须 / 不得** | 强制要求；违反即缺陷或门禁失败 |
| **应 / 不应** | 默认要求；偏离时必须在 PR 或 ADR 中写明理由 |
| **可** | 允许，不强制 |
| 【推断】 | 基于经验的判断，未经测量；首个基线数据出来后必须替换 |
| 【待核实】 | 外部事实（如版本号）尚未核实；M0 前必须核实 |

## 7. 统一头部格式

每个 Markdown 文件的标题下一行必须是：

```text
> 状态：<状态词>｜版本：<semver>｜负责人：<角色或姓名>｜最后更新：YYYY-MM-DD
```

`python3 tools/doccheck.py` 会检查这一格式。

## 8. 维护规则

- 同一事实只写在第 3 节指定的那份文档里，其他文档只能链接。
- 阶段名只使用 roadmap 中定义的 `M0`、`P0`～`P5`、`R`。
- 诊断码只能在诊断登记册中分配；需求去向只能在需求登记册中修改。
- 每个 PR 必须通过 `python3 tools/doccheck.py --check`。
