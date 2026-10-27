# 文档索引与目录架构

本文说明文档放在哪里、每类内容由谁负责以及修改后如何校验。项目介绍、阅读顺序、规范用语与权威顺序见 [项目 README](../README.md)。

## 1. 目录架构

```text
docs/
├─ README.md                 # 本文：文档架构与维护入口
├─ vision.md                 # 目标、非目标、范围分层
├─ roadmap.md                # 阶段、交付物与退出门禁
├─ architecture.md           # 系统分层和编译器管线
├─ repository.md             # 实现目录、模块职责与依赖
├─ governance.md             # 协作、决策、评审和贡献流程
├─ toolchain.md              # 工具链及关键依赖的锁定依据
├─ testing.md                # 测试体系、语料和验证门禁
├─ performance.md            # 性能目标、基准与证据要求
├─ platforms.md              # 平台分级与晋级规则
├─ release.md                # 发布、兼容、签名与回滚
├─ risks.md                  # 风险及缓解措施
├─ ecosystem.md              # UI、AI、服务端等生态边界
├─ migration.md              # 历史文档映射与归档说明
├─ changelog.md              # 文档与发布变更记录
├─ decisions/                # ADR-0001～0008
├─ design/
│  ├─ compiler.md            # 编译器数据结构与 Pass 设计
│  ├─ p0-workplan.md         # 启动及首个端到端切片
│  └─ p1-workplan.md         # 模块、所有权和标准库工作分解
└─ requirements/
   ├─ registry.yaml          # 需求数据源
   └─ registry.md            # 自动生成的阅读视图
```

## 2. 内容归属

| 要查阅或修改的内容 | 入口 | 边界 |
|---|---|---|
| 项目目标与计划 | [vision](vision.md)、[roadmap](roadmap.md) | 定义范围和阶段，不复制语言规则 |
| 系统与模块设计 | [architecture](architecture.md)、[repository](repository.md)、[compiler](design/compiler.md) | 定义实现组织，通过链接引用规范 |
| 具体实施任务 | [P0 工作分解](design/p0-workplan.md)、[P1 工作分解](design/p1-workplan.md) | 任务、依赖、验收及测试证据 |
| 语言与公开契约 | [语言规范](../specs/language/01-lexical-syntax.md)、[标准库](../specs/library/std-core.md)、[包与构建](../specs/packages/manifest-lock-build.md) | 规范集中在 `specs/`，设计文档引用它们 |
| 架构决策与变更提案 | [ADR](decisions/ADR-0008-pre-kickoff-decisions.md)、[RFC 模板](../rfcs/0000-template.md) | ADR 记录取舍；RFC 承载规范变更提案 |
| 需求与诊断编号 | [需求数据源](requirements/registry.yaml)、[诊断数据源](../specs/diagnostics/registry.yaml) | YAML 是数据源，Markdown 是生成视图 |
| 开发协作与环境 | [governance](governance.md)、[toolchain](toolchain.md) | 流程、职责和工具链约束 |
| 质量与交付 | [testing](testing.md)、[performance](performance.md)、[platforms](platforms.md)、[release](release.md)、[risks](risks.md) | 质量标准、验证证据和交付约束 |
| 生态扩展 | [ecosystem](ecosystem.md) | 生态包职责和进入核心的边界 |
| 历史追溯 | [migration](migration.md)、[changelog](changelog.md)、[原始需求](../archive/original/) | 原始输入永久保留；归档正文保持原样 |

## 3. 文档间的关系

目标与需求确定范围，路线图确定交付阶段，规范定义行为，ADR 记录取舍，架构和设计说明实现方式，工作分解与测试说明如何落地和验收。发生冲突时按 [权威顺序](../README.md) §5 处理。

文档目录在本文维护；编译器和运行时的未来源码目录由 [repository](repository.md) 维护。目录树中的源码规划不能作为已有实现的证明。

## 4. 维护与校验

先修改负责该事实的文档，再更新引用和导航。新增文档时在 [根目录文档地图](../README.md) §3 登记职责，并更新本文目录；迁移文件时同步修正链接和检查脚本中的路径。

需求和诊断登记册修改 YAML 后，在仓库根目录执行：

```shell
python tools/doccheck.py
python tools/doccheck.py --check --old-matrix archive/v1/docs/X-Lang原始功能全量追溯矩阵.md
```

普通文档修改只需运行 `python tools/doccheck.py --check`。正文以一级标题开头，不添加版本、状态页头；归档横幅仅用于指向当前内容，历史正文不改写。
