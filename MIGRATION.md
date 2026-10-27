# 迁移说明：旧文档 → v2

> 状态：Accepted｜版本：2.1.0｜负责人：Project Lead｜最后更新：2026-10-22
> 类型：Log｜唯一负责：旧文件 → v2 的映射、旧编号与旧阶段的对照、归档清单。

## 1. 结论

1. v2 生效后，旧仓库的 `docs/` 与 `rfcs/` 全部移到 `archive/v1/`（保持原路径），设为只读，并在每个文件开头加一行横幅：`> 已归档：见 v2 <新路径>`。
2. 原始需求 `docs/原始文档/1.txt～12.txt` 移到 `archive/original/`，**永久保留**，作为需求登记册中 `source` 字段的出处。
3. 以后所有修改只发生在 v2 中；归档文件不再修改（错别字也不改）。

## 2. 文件映射

| 旧文件 | v2 去向 | 处理 |
|---|---|---|
| `README.md`、`docs/README.md` | [README](README.md) | 合并 |
| `docs/X-Lang企业级完整文档体系总纲.md` | [vision](docs/vision.md)、[roadmap](docs/roadmap.md)、[architecture](docs/architecture.md) | 拆分，矛盾已裁决（C3–C10） |
| `docs/X-Lang原始功能全量追溯矩阵.md` | [需求登记册](docs/requirements/registry.yaml) | 164 条全部迁入，补充 4 条遗漏需求 |
| `docs/X-Lang未纳入与偏离内容再审核及回归路线.md` | 需求登记册的 `phase/disposition/note` 字段；[ADR-0003](docs/decisions/ADR-0003-scope-1.0-and-wedge.md) | RETURN 波次废止，逐条重定阶段 |
| `docs/X-Lang多语言对标与全栈能力补全大纲.md` | 需求登记册、[ecosystem](docs/ecosystem.md)、[std-core](specs/library/std-core.md) | 拆分 |
| `docs/X-Lang完整项目目录架构与模块说明.md` | [repository](docs/repository.md) | 重写（5 个成员） |
| `docs/X-Lang日常开发与AI协作风险补全大纲.md` | [GOVERNANCE](GOVERNANCE.md) §6–7、[risks](docs/risks.md)、[testing](docs/testing.md) | XLE-AI 条目并入 §6 |
| `docs/X-Lang编译器工程实施文档大纲.md` | [compiler](docs/design/compiler.md)、[roadmap](docs/roadmap.md)、[testing](docs/testing.md) | G/R 体系废止 |
| `docs/X-Lang语言规范与学习研究大纲.md` | [specs/language](specs/language/01-lexical-syntax.md)、[testing](docs/testing.md) §9 | 拆分 |
| `docs/design/00-gap-analysis-and-design-targets.md` | [CHANGELOG](CHANGELOG.md)、本文件 | 缺口已在 v2 中关闭 |
| `docs/design/p0-vertical-slice.md` | [p0-workplan](docs/design/p0-workplan.md) | P0 缩为单文件；三包 Workspace 移到 P1 |
| `docs/design/semantic-pipeline.md` | [architecture](docs/architecture.md) §3、[compiler](docs/design/compiler.md) | 合并 |
| `docs/design/conformance-and-gates.md` | [testing](docs/testing.md) §3（含 gate manifest） | 合并 |
| `docs/design/evidence-and-platform-gates.md` | [roadmap](docs/roadmap.md)、[platforms](docs/platforms.md) | 合并 |
| `docs/design/ai-development-and-learning.md` | [GOVERNANCE](GOVERNANCE.md) §6、[ecosystem](docs/ecosystem.md) §5、[testing](docs/testing.md) §9 | 拆分 |
| `docs/design/xui-and-platforms.md` | [ecosystem](docs/ecosystem.md) §2 | 合并 |
| `docs/design/README.md`、`docs/decisions/README.md`、`rfcs/README.md` | [README](README.md) §3 | 合并 |

## 3. RFC 映射

| 旧 RFC | v2 去向 | 主要修订 |
|---|---|---|
| RFC-0001 模块与名称解析 | [06-modules](specs/language/06-modules.md) | 导入根名的 `-`→`_`（C17）；Prelude 加入打印函数；方法调用允许一次自动解引用 |
| RFC-0002 模式解构 | [03-expressions-patterns](specs/language/03-expressions-patterns.md) §10 | 负数字面量只在模式中出现；浮点字面量模式禁止（`X-E2109`） |
| RFC-0003 清单/解析/Lockfile | [manifest-lock-build](specs/packages/manifest-lock-build.md) | 分期后移（ADR-0004） |
| RFC-0004 构建工件与外部依赖 | [manifest-lock-build](specs/packages/manifest-lock-build.md) §6 | 1.0 不提供通用构建脚本（C7） |
| RFC-0005 词法与表层语法 | [01-lexical-syntax](specs/language/01-lexical-syntax.md) | 新增关键字 `static`、8 个保留字；位运算优先级高于比较运算；块类语句不需要 `;`；`return/break/continue` 成为表达式；turbofish；属性注册表；删除 `export_function` |
| RFC-0006 类型、值、Place、求值 | [02-types-traits](specs/language/02-types-traits.md)、[03](specs/language/03-expressions-patterns.md) | 小写类型名（C1）；赋值先左后右（C2）；溢出在所有 Profile 下 panic |
| RFC-0007 所有权、借用、移动、Drop | [04-ownership-borrowing](specs/language/04-ownership-borrowing.md) | 隐式区域 + 省略规则（C15）；P1 起检查借用（C21）；Drop 顺序保持为逆声明顺序 |
| RFC-0008 Result/panic/终止/清理 | [05-errors-panics](specs/language/05-errors-panics.md) | P0–P2 只有 abort；`map_error` 是唯一名称 |
| RFC-0009 文本、字节与集合 | [std-core](specs/library/std-core.md) §5 | 合并 |
| RFC-0010 JSON | [ecosystem](docs/ecosystem.md) §4 | 移出核心规范 |
| RFC-0011 XUI | [ecosystem](docs/ecosystem.md) §2 | 小程序改为研究赛道 |
| （新增） | [07-unsafe-ffi](specs/language/07-unsafe-ffi.md)、[08-concurrency](specs/language/08-concurrency.md)、[02](specs/language/02-types-traits.md) 中的 Trait/泛型部分 | 补齐审查报告指出缺失的 5 份语义规范：Trait/泛型、unsafe/UB、FFI、并发、属性 |

## 4. ADR 重新编号

| 旧编号 | 新编号 | 说明 |
|---|---|---|
| ADR-0004 Rust + LLVM 宿主基线 | [ADR-0001](docs/decisions/ADR-0001-host-and-backend.md) | 基础决策排在最前 |
| ADR-0002 阶段化模块化单体 | [ADR-0002](docs/decisions/ADR-0002-repository-modular-monolith.md) | 成员数固定为 5 个 |
| ADR-0003 P0 语言 Profile 与 Labs 冻结 | [ADR-0003](docs/decisions/ADR-0003-scope-1.0-and-wedge.md) | 扩展为 1.0 范围 |
| ADR-0001 XPM/XBuild 分层 | [ADR-0004](docs/decisions/ADR-0004-xpm-xbuild-layering.md) | 分期后移 |
| — | ADR-0005、ADR-0006、ADR-0007 | v2.0 新增 |
| — | [ADR-0008](docs/decisions/ADR-0008-pre-kickoff-decisions.md) | v2.1 新增：开工前决策汇总 |

## 5. 旧阶段与编号体系对照

旧体系 **已废止**，以下对照只用于阅读归档文件。

| 旧标识 | 旧含义 | v2 对应 |
|---|---|---|
| D0 | 冲突/决策闭环 | M0 + ADR-0007 |
| 旧 P0（三包 Path Workspace + 单宿主端到端） | — | v2 P0（单文件端到端）+ v2 P1（三包 Workspace） |
| 旧 P1–P5 | 各阶段 | 名称保留，但内容按 [roadmap](docs/roadmap.md) 重新定义 |
| 旧 P6 | 生态扩展 | P5 / R |
| G0 语言冻结 | 门禁 | P2 退出门禁（规范 Accepted）+ P4（Stable） |
| G1 可运行核心 | 门禁 | P1 退出门禁 |
| G2 生产工具 | 门禁 | P3 退出门禁 |
| G3 服务端、G4 Web、G5 样式与 UI | 门禁 | P4 生态样例 / P5 |
| G6 生态扩展 | 门禁 | P5、R 的立项规则（[ecosystem](docs/ecosystem.md) §7） |
| R0 决策与探针 | 回归波次 | M0–P1，按登记册逐条处理 |
| R1 核心开发体验 | 回归波次 | P2–P3（多数改为工具或生态替代） |
| R2 企业与生产工具 | 回归波次 | P3–P4 |
| R3 领域框架、R4 平台扩展 | 回归波次 | P3–P5 eco |
| R5 高风险条件能力 | 回归波次 | R（研究赛道） |
| GAP 波次 A–D | 缺口关闭批次 | 按 v2 阶段关闭，见 [roadmap](docs/roadmap.md) |
| 缺口编号 G1–G6（design/00） | 文档缺口 | 已关闭：见 CHANGELOG |

注意：v2 中的 `R` 只表示“研究赛道”，与旧的 R0–R5 回归波次无关。

## 6. 语法与语义的破坏性变化（对照旧 RFC 写的代码）

| 旧写法 | 新写法 | 自动迁移 |
|---|---|---|
| `I32`、`USize`、`Bool`、`Unit`、`Str` | `i32`、`usize`、`bool`、`()`、`str` | 可以，机械替换 |
| `a & b == c` 被解析为 `a & (b == c)` | 现在解析为 `(a & b) == c` | 需要人工复核 |
| `if (c) { … };`（必须加分号） | `if (c) { … }` | 可以 |
| `export_function …` | `@export("sym") pub extern "C" fn …` | 可以 |
| `map_err` | `map_error` | 可以 |
| `static` 用作标识符 | 改名（`static` 现在是关键字） | 可以 |
| `async`、`await`、`defer`、`dyn`、`macro`、`throw`、`try`、`yield` 用作标识符 | 改名（它们现在是保留字） | 可以 |

## 7. 归档清单（全部移到 `archive/`）

- `archive/v1/README.md`
- `archive/v1/docs/` 下的全部 `.md` 文件：8 份大纲/矩阵 + `README.md`，`decisions/` 下 5 个文件，`design/` 下 8 个文件
- `archive/v1/rfcs/` 下的 12 个文件（0001–0011 + README）
- `archive/original/1.txt … 12.txt`（永久保留）

以上共 47 个文件，与审查时的输入一致。

## 8. main 分支迁移记录 — 2026-10-27

- v2.1.0 已提升到仓库根目录，作为 main 分支的当前文档体系。
- 迁移前的工作区文档先提交保存；上述 47 个文件全部归档，旧 Markdown 仅添加归档横幅，12 份原始需求保持字节不变。
- 原始导入包保存在 [archive/imports/x-docs-v2.zip](archive/imports/x-docs-v2.zip)，不参与当前文档检查。
- `doccheck` 只检查当前文档，跳过 `.git/` 与只读 `archive/`；生成链接统一使用 `/`，保证 Windows 与 Linux 上的生成物一致。
- 验证命令：`python tools/doccheck.py --check --old-matrix archive/v1/docs/X-Lang原始功能全量追溯矩阵.md`。
