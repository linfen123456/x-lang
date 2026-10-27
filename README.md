# X-Lang

> 类型：Index｜本文件是**阅读顺序、文档地图、权威顺序、规范用语**的唯一定义处。

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
| 贡献者/AI Agent | [GOVERNANCE](docs/governance.md)（流程、分支、评审、AI 规则） |

## 3. 文档地图

| 路径 | 类型 | 唯一负责的事实 |
|---|---|---|
| [README.md](README.md) | Index | 项目介绍、阅读顺序、地图、权威顺序、规范用语 |
| [docs/README.md](docs/README.md) | Index | 文档目录架构、内容归属、维护入口 |
| [docs/governance.md](docs/governance.md) | Governance | 角色、RFC/ADR 流程、分支/提交/评审、AI 协作规则 |
| [docs/toolchain.md](docs/toolchain.md) | Governance | 宿主工具链版本锁定 |
| [docs/changelog.md](docs/changelog.md) | Log | 文档体系与发布变更记录 |
| [docs/migration.md](docs/migration.md) | Log | 旧文档 → v2 映射与归档清单 |
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

原始需求 `1.txt～12.txt` 是只读历史输入，永久保存在 [archive/original/](archive/original)。旧文档保存在 [archive/v1/](archive/v1)，v2 导入压缩包保存在 [archive/imports/x-docs-v2.zip](archive/imports/x-docs-v2.zip)，归档映射见 [MIGRATION](docs/migration.md)。

## 4. 当前目录

```text
x-lang/
├─ README.md                 # 项目介绍与阅读导航
├─ docs/                     # 设计、规划、治理和维护文档
│  ├─ README.md              # 文档架构与内容归属
│  ├─ decisions/             # 架构决策
│  ├─ design/                # 编译器设计与实施工作分解
│  └─ requirements/          # 需求登记册与生成视图
├─ specs/                    # 语言、标准库、包与诊断规范
│  ├─ language/              # 语言规范 01–08
│  ├─ library/               # core / alloc / std 契约
│  ├─ packages/              # 清单、锁文件与构建契约
│  └─ diagnostics/           # 诊断登记册与生成视图
├─ rfcs/                     # 后续规范变更提案与模板
├─ tools/doccheck.py         # 文档校验与登记册生成
└─ archive/                  # 历史输入与导入包
   ├─ v1/                   # 旧文档，保留追溯
   ├─ original/             # 12 份原始需求
   └─ imports/              # 原始导入压缩包
```

完整文档目录和内容归属见 [文档索引](docs/README.md)。后续编译器源码、Cargo workspace 与测试目录按 [仓库实施架构](docs/repository.md) 创建；当前仓库尚未包含可构建的编译器实现。

## 5. 权威顺序（冲突时按此裁决）

1. 已 Accepted 的 `specs/`、ADR。
2. Proposed 的 `specs/`、ADR（本 v2 初始状态）。
3. [roadmap](docs/roadmap.md)（阶段与门禁）。
4. [architecture](docs/architecture.md)、[repository](docs/repository.md)、`docs/design/`。
5. [requirements 登记册](docs/requirements/registry.yaml)（需求去向）。
6. 其余 Policy/Register 文档。
7. 原始需求 txt（历史输入，只说明意图，不构成规则）。

发现冲突时：不得自行挑选一方继续实现。必须开 Issue 并标记 `conflict`，按 [GOVERNANCE](docs/governance.md) §3 处理；修正后由 `tools/doccheck.py` 复检。

## 6. 规范用语

| 用语 | 含义 |
|---|---|
| **必须 / 不得** | 强制要求；违反即缺陷或门禁失败 |
| **应 / 不应** | 默认要求；偏离时必须在 PR 或 ADR 中写明理由 |
| **可** | 允许，不强制 |
| 【推断】 | 基于经验的判断，未经测量；首个基线数据出来后必须替换 |
| 【待核实】 | 外部事实（如版本号）尚未核实；M0 前必须核实 |

## 7. 文档格式

文档以一级标题开头，正文说明职责、设计依据和具体内容，不添加版本、状态页头。章节使用稳定编号，引用规则时链接到对应规范，避免复制定义。

## 8. 维护规则

- 同一事实只写在第 3 节指定的那份文档里，其他文档只能链接。
- 阶段名只使用 roadmap 中定义的 `M0`、`P0`～`P5`、`R`。
- 诊断码只能在诊断登记册中分配；需求去向只能在需求登记册中修改。
- 每个 PR 必须通过 `python3 tools/doccheck.py --check`。

## 9. 本地检查

只需要 Python 3.10 或更高版本，无第三方依赖。在仓库根目录执行：

```shell
python tools/doccheck.py --check
```

修改需求或诊断 YAML 后，先重新生成视图，再校验：

```shell
python tools/doccheck.py
python tools/doccheck.py --check --old-matrix archive/v1/docs/X-Lang原始功能全量追溯矩阵.md
```

检查覆盖内部链接、章节引用、术语、需求去向、诊断登记和规则引用。生成的登记册 Markdown 不手工维护；历史归档不参与当前文档校验。
