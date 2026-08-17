# X-Lang 完整项目目录架构与模块说明

> 总纲：[X-Lang 企业级完整文档体系总纲](./X-Lang企业级完整文档体系总纲.md)  
> 大纲版本：1.1-outline｜状态：责任边界已冻结；物理结构 Proposed，见 [ADR-0002](./decisions/ADR-0002-staged-modular-monolith.md)｜核心架构候选：阶段化模块化 Monorepo｜初始实现：Rust + LLVM
> 目的：区分当前真实目录、下一阶段物理结构和长期能力归属，为项目搭建、团队分工、测试与发布提供不超前的蓝图。

## 1. 架构原则

- 核心语言语义与 LLVM、操作系统、IDE、云厂商和 AI 服务解耦。
- 编译依赖只允许 `source → syntax → semantic → IR → codegen → driver`；工具通过公共查询接口消费语义数据。
- `compiler/`、`runtime/`、`library/` 是稳定主线；P5+ 生态采用联邦仓库独立版本；`labs` 默认关闭且不得被稳定包依赖。
- 禁止建立无边界的 `utils/common/shared`；跨域能力必须命名为明确契约，如 `x-source-map`、`x-target-spec`。
- 所有公共接口采用输入/输出类型、结构化错误、版本和边界校验；LLVM 类型不得出现在前端公共接口。
- 每个独立构建或发布的项目必须有 `README.md`，记录职责、非职责、所有者、依赖、命令、公开接口、测试和成熟度；普通内部模块不复制空模板。
- 本文目录树是长期能力归属图，不代表每个命名节点都必须成为独立 crate、独立版本或立即创建的目录。
- P0/P1 采用模块化单体：只有存在独立发布、安全/进程隔离、两个以上稳定消费者、可测编译收益或长期独立所有者时才拆分叶子项目。
- 不创建空目录、空 crate 或只为未来设想存在的接口；未到阶段的节点保留在大纲中，不进入实际 Workspace。

### 1.1 架构模型：物理结构服从成熟度

本文采用四层视图，后一层不能反向污染前一层：

| 阶段 | 物理策略 | 可以冻结 | 禁止事项 |
|---|---|---|---|
| D0 文档阶段 | 保留当前文档、历史材料和真实 RFC/ADR | 权威顺序、目标/非目标、候选规则、依赖方向 | 空 `specs`、空代码项目、把 Proposed 候选写成实现 |
| P0/P1 可运行核心 | 4–6 个 Workspace 成员的模块化单体 | 单一纵向编译链、Runtime/CLI/测试边界 | 宏/Effect/async/UI/AI/ML 项目和无消费者接口 |
| P2–P4 1.0 工程化 | 依据消费者、隔离和测量结果拆分 | core/alloc/std、核心工具、平台与发布契约 | 为目录整齐或未来复用预拆 crate |
| P5+ 生态 | 独立版本的联邦仓库 | Web/UI/Server/SDK/AI/ML 公共接口 | 依赖编译器私有 AST/HIR/MIR 或成为核心必需依赖 |

### 1.2 D0：当前真实项目结构

当前仓库仍是文档与架构项目，以下结构由工作区事实决定，而不是未来规划：

```text
x/
├─ README.md
├─ rfcs/                              # Proposed 规范提案及索引；数量以索引为准
└─ docs/
   ├─ README.md
   ├─ decisions/                     # Proposed/Accepted 架构决策及索引
   ├─ X-Lang企业级完整文档体系总纲.md
   ├─ X-Lang语言规范与学习研究大纲.md
   ├─ X-Lang编译器工程实施文档大纲.md
   ├─ X-Lang完整项目目录架构与模块说明.md
   ├─ X-Lang原始功能全量追溯矩阵.md
   ├─ X-Lang未纳入与偏离内容再审核及回归路线.md
   ├─ X-Lang多语言对标与全栈能力补全大纲.md
   ├─ X-Lang日常开发与AI协作风险补全大纲.md
   └─ 原始文档/                       # 12 份只读历史输入
```

根 `rfcs/` 和 `docs/decisions/` 已因真实提案创建；`specs/` 仍只接收已批准规则，当前 Proposed 设计继续留在 RFC/ADR，不以目录名伪装成熟度。

### 1.3 P0/P1：推荐模块化单体

首个可运行仓库只建议 5 个 Rust Workspace 成员；LLVM 在编译器内部适配器隔离，直到出现第二后端或独立编译收益再拆 crate。

```text
x-lang/
├─ Cargo.toml
├─ Cargo.lock
├─ rust-toolchain.toml
├─ README.md
├─ AGENTS.md
├─ compiler/                         # 单一 crate、内部严格分层
│  └─ src/
│     ├─ lib.rs                      # 唯一受控门面
│     ├─ source/                     # SourceId、Span、SourceMap、诊断基础
│     ├─ syntax/                     # token、lexer、CST、parser、AST
│     ├─ semantic/                   # resolve、types、traits、ownership
│     ├─ ir/                         # HIR、MIR、verifier、基础分析
│     ├─ codegen/                    # Backend 契约 + LLVM 适配
│     └─ driver/                     # session、查询编排、工件清单
├─ runtime/                          # 最小 Runtime ABI、alloc、panic、PAL
├─ cli/                              # `x` 主命令；`xc` 仅兼容入口
├─ library-core/                     # Option/Result/基础 Trait 和原语封装
├─ conformance/                      # 规范语料 runner 与 Rule ID 追溯
├─ tests/
│  ├─ conformance/                   # compile-pass/fail/run-pass
│  ├─ end-to-end/                    # source → executable
│  ├─ abi/                           # 最小 C harness 与布局探针
│  └─ fixtures/
└─ dev/
   └─ xtask/                         # CI、代码生成和语料维护，不是用户工具
```

P0/P1 不创建独立宏、Effect、Contract、高级 Trait、async scheduler、平台 I/O 家族、XPM、LSP、IDE、Web、UI、CSS、AI、ML、注册表或云服务项目。格式化器先复用 `compiler::syntax` 并作为 `x fmt` 子命令实现；接口稳定且确有独立消费者后才拆出 `xfmt`。

`dev/xtask` 是仓库开发辅助程序，但 P0/P1 不加入 Cargo Workspace 或 `default-members`，因此不计入上述 5 个发布/构建成员；若后续加入，必须重新核对 4～6 成员预算。

### 1.4 P2–P4：证据驱动的 Core Monorepo

模块通过拆分门禁后，物理结构最多先收敛到以下责任组，而不是直接展开为每个概念一个 crate：

```text
x-lang/
├─ compiler/
│  ├─ base/                          # Source、Span、Diagnostic 契约
│  ├─ syntax/                        # Lexer、CST、Parser、AST
│  ├─ semantic/                      # Resolve、Type、Trait、Borrow、HIR
│  ├─ ir/                            # MIR、Verifier、优化
│  ├─ codegen-api/
│  ├─ codegen-llvm/
│  └─ driver/                        # Query、Session、Metadata、编排
├─ runtime/
│  ├─ core/                          # ABI、panic、alloc
│  └─ platform/                      # Tier 1 OS 适配
├─ library/
│  ├─ core/
│  ├─ alloc/
│  └─ std/
├─ tools/
│  ├─ x/                             # init/check/build/run/test
│  ├─ xfmt/
│  ├─ xpm/
│  ├─ x-lsp/
│  └─ xdoc/
├─ editors/vscode/                   # 薄客户端，不复制语义服务
├─ specs/                            # 已批准规范
├─ rfcs/
├─ docs/decisions/
├─ tests/{conformance,end-to-end,interoperability,security,reproducibility}/
├─ benchmarks/
├─ distribution/
└─ release/
```

允许依赖方向为 `base → syntax → semantic → ir → codegen-api → codegen-llvm`，`driver` 组合各层，CLI/LSP/工具只消费 `driver` 和稳定查询门面。任何底层层级禁止反向依赖 `driver`，前端禁止依赖 LLVM，标准库禁止依赖工具。

### 1.5 P5+：联邦生态仓库

1.0 核心稳定后，不再向 Core Monorepo 无限添加领域项目；按独立版本、Owner、CI、威胁模型和发布节奏建立：

```text
xlang/
├─ x-lang/                           # 编译器、Runtime、标准库、核心工具
├─ x-web/                            # WASM/JS、DOM、SSR、Web 构建
├─ x-ui/                             # View、Style IR、Web/Native Renderer
├─ x-server/                         # HTTP、API、数据库和可观测适配
├─ x-sdk/                            # C/Python/JVM/Node 绑定
├─ x-registry/                       # 包注册表和发布服务
├─ x-ai-tools/                       # MCP、Agent、Eval、Provenance
└─ x-ml/                             # Tensor、Autograd、设备后端
```

生态仓库只依赖稳定公开 API，不导入私有 AST/HIR/MIR，不成为编译、格式化或包解析的必需依赖；未通过独立稳定门禁时保持 Experimental。

### 1.6 UI、CSS 与跨平台渲染边界

XUI 是普通类型和函数库，不新增 JSX/XML、UI 关键字或专用核心 AST。Web 默认使用标准 CSS；CSS Modules/解析器生成类型化类名，XStyle 只承载 Design Token、类型化值、主题和受限跨平台 `CoreStyle` IR，不重新实现浏览器 Cascade、Selector、Flex 或 Grid。

```text
标准 CSS ──→ CSS Modules/类型生成 ──→ XUI ──→ DOM/SSR Renderer

Theme/Design Token ──→ CoreStyle IR ──┬─→ Web CSS
                                      ├─→ Desktop Renderer
                                      └─→ Mobile Renderer
```

Web/原生特有属性通过显式扩展类型表达；不支持的属性必须报错、警告或要求显式降级，禁止静默忽略。原生 Renderer 只有在真实需求证明浏览器/平台布局能力不可复用时，才能独立立项布局引擎。

### 1.7 项目拆分门禁

内部模块成为独立 crate/项目/仓库至少满足一项理由：两个以上稳定消费者、独立发布周期、进程/权限隔离、必须隔离的第三方依赖、长期独立 Owner、可测的增量编译收益或平台独立构建需求；并且必须全部提供 ADR、输入/输出/错误/资源契约、无环依赖图、先行契约测试、真实源码、Owner、独立 CI 和合并回单体的回退方案。

“未来可能复用”“功能矩阵有一个 `x-*` 名称”“目录更整齐”或“以后也许独立发布”都不足以拆分。内部模块无需复制 `OWNERS/CHANGELOG/docs/benches/fuzz/examples` 全套目录；只在存在独立发布、攻击面或性能门禁时创建真实需要的工件。

## 2. 长期逻辑能力归属

本节只维护责任域，不再展开数百个假想目录。物理结构以 1.2～1.5 和 [ADR-0002](./decisions/ADR-0002-staged-modular-monolith.md) 为准；第 6 节只维护能力组到责任域的架构映射，逐项 `XLF-*` 追溯仍以原始功能矩阵和未来 Traceability 工件为准。任何名称都不自动产生 crate、目录、仓库或稳定承诺。

| 责任域 | 长期能力 | 稳定依赖边界 | 物理化条件 |
|---|---|---|---|
| Compiler Frontend | Source、Diagnostic、Token、Lexer、CST/AST、Resolve、Type、Trait、Borrow | 不依赖 LLVM、Runtime、IDE 或生态框架 | P0/P1 先为 `compiler` 内部模块；稳定查询和第二消费者出现后再拆 |
| IR/Backend | HIR、MIR、Verifier、分析、LLVM、Target、Link | 只消费已类型化 IR 和 Target Contract，不反向修改前端语义 | 后端替换、独立构建收益或平台隔离有证据 |
| Runtime | 启动、分配、panic、线程、任务、I/O、PAL、资源 | 不依赖编译器前端、包管理、Web 或 AI | ABI、平台和故障域需要独立测试/发布 |
| Library | core、alloc、std、集合、文本、Codec、系统 API | `core → alloc → std` 单向；生态库不能进入 Prelude | API 和平台矩阵达到对应阶段门禁 |
| Toolchain | `x`、XPM/XBuild、fmt/doc/test、LSP/DAP、诊断 | 通过 Driver/Query/Metadata 契约消费编译器，不读私有结构 | 两个消费者、独立发布或进程权限隔离 |
| Distribution | Installer、Bundle、签名、SBOM、Provenance、Registry Client | 只消费已验证 Artifact 与 Lock Graph | P3 后供应链和回滚门禁通过 |
| SDK/FFI | C、Python、JVM、Node、WASM 桥接 | 所有权、错误、线程、ABI 和版本显式，不进入核心类型 | 每个生态独立兼容矩阵和发布周期 |
| Federated Ecosystem | Web、UI、Server、Data、ML、移动、Serverless | 只依赖稳定公开 API，不读取私有 AST/HIR/MIR | P5+ 独立 Owner、CI、版本和威胁模型 |
| AI Tools | Context、Policy、Verify、Review、Eval、Provenance、Budget | 最小权限；不能绕过规范、CI、人工审批或供应链门禁 | 独立发布，默认不在编译关键路径 |
| Labs | async/effect/comptime 扩展、ZKP、Replay、硬实时等研究 | 默认关闭；CORE 和 Stable 工件不得依赖 | Charter、预算、退出条件和实验报告完整 |

### 2.1 名称到责任域的规则

- 历史 `x-*` 名称首先视为逻辑目标，映射到现有责任域；
- 宏、Effect、async、UI、AI、ML 等未到阶段的能力只保留需求/RFC，不预建项目；
- Web 采用标准 CSS + CSS Modules，XStyle 仅承载 Token、主题和受限 CoreStyle IR；
- JSON 位于官方 Codec，Map 位于 alloc/std，二者不增加核心语法；
- XPM 解析锁图，XBuild 消费锁图生成 Action DAG；Compiler 不回调 Resolver；
- 需要新增物理项目时，必须通过 1.7 的拆分门禁并更新 ADR，而不是恢复长期目录树。

## 3. 稳定主线子项目契约

| 子系统 | 主要输入 | 主要输出 | 允许依赖 | 禁止依赖 | 必备测试 |
|---|---|---|---|---|---|
| Source/Syntax | 源文件、增量文本 | Token/CST/AST/Span | x-source、x-diagnostics | LLVM、runtime、IDE | Unicode、恢复、fuzz、快照 |
| Semantic | AST、包图 | DefId、Type、Borrow 结果、HIR | syntax、规范化类型 | codegen、IDE UI | 规则级 pass/fail、属性测试 |
| IR/Middle | HIR | MIR/LIR、分析和优化报告 | semantic、target-spec | runtime 实现细节 | verifier、diff、reducer |
| Codegen | MIR、TargetSpec | IR/对象/调试信息 | codegen-api、LLVM 适配 | Parser/IDE | ABI、汇编、链接、差分 |
| Driver | 清单、源码、编译选项 | 诊断、工件清单 | compiler 各稳定内部 API | 服务端注册表实现 | E2E、取消、缓存失效 |
| Runtime | 后端生成的 Runtime ABI 调用 | 进程行为和系统资源 | PAL、系统 API | compiler frontend | sanitizer、压力、故障注入 |
| Core/Std | 语言原语、Runtime ABI | 稳定库 API | core→alloc→std 单向 | tools/editors | doc-test、平台、复杂度 |
| Tools | Driver/Query/Metadata | CLI/LSP/DAP/文档 | 公开内部接口 | 私有 AST 字段、LLVM | 协议、快照、E2E、性能 |
| Ecosystem | 稳定语言/标准库 API | 独立版本库/框架 | public API | compiler 私有接口 | 互操作、安全、升级 |
| Labs | 明确实验接口 | 原型/报告 | 只依赖稳定接口 | 被 CORE 反向依赖 | 假设、基准、退出测试 |

### 3.1 公共接口通则

- 输入类型和输出类型分离；外部输入在边界验证，内部不重复猜测。
- 错误统一为机器代码、消息、Span/上下文和可选详情；不得返回裸字符串作为协议。
- 集合接口有大小限制/分页/流式形式；取消、超时和资源上限必须是契约一部分。
- 内部工件（HIR/MIR/Metadata/Diagnostic JSON）带 `schema_version`；读取者拒绝未知主版本。
- 公共 API 只做向后兼容的增量扩展；移除通过废弃期、API diff 和迁移工具。

## 4. 子项目内容标准

只有独立构建/发布且已通过拆分门禁的项目才采用以下参考结构；目录按真实风险创建，不要求无攻击面的项目保留空 `fuzz/security`，也不要求内部模块复制 `OWNERS/CHANGELOG`。二进制项目将 `lib.rs` 换为 `main.rs`，非 Rust 项目保留等价目录。

```text
project-name/
├─ Cargo.toml | package.json | build.gradle.kts
├─ README.md                   # 目标、非目标、接口、依赖、命令、成熟度
├─ OWNERS.md                   # 可由根 CODEOWNERS 代替
├─ CHANGELOG.md                # 仅独立发布时必需
├─ src/
│  ├─ lib.rs                   # 最小导出面
│  ├─ model/                   # 领域类型，不依赖基础设施
│  ├─ api/                     # 输入/输出契约与版本
│  ├─ engine/                  # 核心实现
│  ├─ adapters/                # LLVM/OS/网络/编辑器等外部适配
│  └─ diagnostics/             # 领域错误和帮助
├─ tests/
│  ├─ contract/                # 公共接口契约
│  ├─ integration/             # 与真实适配器集成
│  ├─ fixtures/                # 最小测试数据
│  └─ regression/              # 每个历史缺陷一个用例
├─ benches/                    # 仅性能有门禁时创建
├─ fuzz/                       # 仅处理不可信输入时创建
├─ examples/                   # 有公开 API/命令时创建
└─ docs/
   ├─ architecture.md
   ├─ api.md
   ├─ testing.md
   └─ security.md              # 有攻击面时必需
```

## 5. 重点项目内容与边界

| 项目 | 核心内容 | 公开接口/工件 | 依赖和完成标准 |
|---|---|---|---|
| `x-compiler` | 参数适配和一次编译生命周期 | `CompileRequest/CompileResult`、工件清单 | 只调用 x-driver；不包含语义逻辑 |
| `x-driver` | 查询编排、阶段取消、缓存、诊断汇总 | `check/build/emit` 内部 API | Hello World 到链接 E2E |
| `x-syntax` | 无损 CST、恢复、增量编辑 | `ParseResult<SyntaxTree>` | 任何字节输入不崩溃 |
| `x-types/x-traits/x-borrow` | 类型、约束、所有权和生命周期 | 类型化查询、稳定 ID、诊断 | 与规范规则 ID 双向追溯 |
| `x-hir/x-mir` | 分层语义 IR 和控制流 IR | 版本化 dump、verifier | 所有 Pass 前后验证 |
| `x-codegen-llvm` | LLVM 降级、ABI、对象和调试信息 | `Backend` 实现 | LLVM 隔离、目标矩阵通过 |
| `x-runtime` 系列 | 启动、内存、任务、I/O、失败 | Runtime ABI | sanitizer、压力、跨平台 |
| `x-core/x-alloc/x-std` | 稳定库分层 | X-Lang 公共 API | 无循环、文档和平台契约 |
| `x-cli/x-build` | 命令、工作区、构建脚本沙箱 | CLI/JSON、BuildPlan | 非 TTY 稳定、可复现 |
| `xpm-*` | 解析、锁文件、缓存、注册表 | `x.toml`/lockfile、包工件 | PubGrub 确定、签名验证 |
| `x-lsp` | 文档状态和语义查询适配 | 标准 LSP + 命名空间扩展 | 大项目延迟、取消和版本测试 |
| `x-debug` | DAP 和平台调试器桥 | DAP、变量/栈/断点模型 | GDB/LLDB/Windows 调试器矩阵 |
| `xfmt/xdoc/xrepl/x-search` | 格式、文档、交互、索引 | CLI 与版本化元数据 | 幂等、doc-test、索引一致性 |
| `x-bindgen` | C/脚本语言/C++ shim | 头文件、绑定源码、ABI metadata | 不承诺通用 C++ ABI |
| `x-mir-interpreter/x-codegen-fast` | 参考语义执行与快速 Debug | 执行结果、UB 报告、后端工件 | 与 LLVM 差分；不得形成第二套语义 |
| `x-vet/x-race/x-coverage/x-profiler` | 静态误用、竞态、覆盖和生产剖析 | 稳定规则 ID、SourceMap、标准报告 | 已知缺陷语料、开销预算和平台矩阵 |
| `x-python/x-jni/x-js` | Python、JVM、JavaScript SDK | 句柄、异常、异步和包工件 | 所有权图、泄漏、版本与发布测试 |
| `x-web-*` | 浏览器宿主、框架、构建和部署 | WASM/JS/CSS、SourceMap、SSR 工件 | WPT 子集、浏览器 E2E、安全和回滚 |
| `x-ui::{style,a11y}` / `x-web::ui` | Token、类型化样式、标准 CSS 互操作和无障碍 | CoreStyle IR、类型化 class、平台诊断 | CSS/WPT 对照、截图差分和 WCAG；不重写浏览器布局引擎 |
| `x-registry` | 包/制品/索引/透明日志 | 版本化 HTTP API | 认证、分页、签名、灾备和审计 |
| `x-agent/x-mcp` | Agent 编排和工具协议 | MCP、补丁提案、审计事件 | 默认只读，写入需确认与测试 |
| `x-tensor/x-autograd` | 张量、设备、梯度 | 独立框架 API/IR | 不向核心增加关键字前先原型 |
| `x-ui::native` | 普通类型/函数式 View、状态和平台渲染 | UI tree、event、Renderer adapter | 不新增核心语法；无障碍、生命周期和真机测试 |
| `labs/*` | 单一研究假设 | 原型、数据、exit-report | 默认关闭、不得被稳定项目依赖 |

## 6. 功能矩阵逻辑目标到责任域映射

功能矩阵中的目标名用于表达责任，不允许据此随意新增顶层项目。下表路径是长期候选责任域，不表示目录已经存在；进入物理结构时优先落入 1.3/1.4 的聚合模块，只有通过拆分门禁才采用独立路径。

| 逻辑能力目标 | 长期候选责任域 |
|---|---|
| `x-compiler-frontend`、`x-parser` | `compiler/x-lexer`、`compiler/x-syntax`、`compiler/x-ast` |
| `x-compiler-middle`、`x-lowering` | `compiler/x-hir`、`compiler/x-mir`、`compiler/x-optimizer` |
| `x-bootstrap` | `compiler/x-compiler` + `tests/reproducibility/bootstrap` |
| `x-async`、`x-scheduler`、`x-std-sync` | `runtime/xrt-task`、`runtime/xrt-scheduler`、`library/x-std-atomic` |
| `x-async-stream` | `runtime/xrt-task` + `library/x-std` 的 `stream` 模块 |
| `x-baremetal` | `backends/x-codegen-baremetal` + `library/x-core` |
| `x-ffi`、`x-bindgen-cxx` | `tools/x-bindgen` + `specs/abi` |
| `x-build-cache`、`x-build-script` | `tools/x-build` 的 `cache`、`script-sandbox` 模块 |
| `x-cli-schema` | `tools/x-cli` 的 `schema` 模块 + `library/x-config` |
| `x-codec-stream` | `library/x-codec` 的 `stream` 模块 |
| `x-compliance-analysis`、`x-resilience-lab` | `tools/x-compliance-analysis`、`x-server::resilience` + `labs/x-self-healing` |
| `x-contracts`、`x-latency-contracts` | `compiler/x-contracts`、`runtime/xrt-realtime` |
| `x-data-columnar` | `x-server::data::{arrow,parquet}` |
| `x-distributed-time` | `library/x-distributed-time` |
| `x-environment` | `tools/x-cli` 的 `env` 子命令 + `tools/x-dev-shadow` |
| `x-error` | `compiler/x-diagnostics` + `library/x-core` 的 `error` 模块 |
| `x-gc-experiment` | `labs/proposals/gc`；原型代码不得进入 runtime 默认成员 |
| `x-hot-reload` | `tools/x-watch` 的 `hot_reload` 实验模块 |
| `x-index` | `tools/x-search::index` + `x-ai-tools::semantic` |
| `x-intrinsics`、`x-optimizer-tco` | `compiler/x-optimizer` 的 feature-gated Pass |
| `x-intellij`、`x-vscode` | `editors/intellij-x`、`editors/vscode-x` |
| `x-io`、`x-io-mmap`、`x-io-zero-copy` | `runtime/xrt-io` 与平台 I/O 项目 |
| `x-ipc`、`x-ipc-ring`、`x-message-log` | `library/x-message-bus` 的 `ipc/ring/log` 模块 |
| `x-lint-cognitive` | `compiler/x-analysis` 的 `lint/cognitive` 模块 |
| `x-memory-gpu`、`x-tensor-ir`、`x-ml-core` | `ml/x-tensor`、`ml/x-ml-compiler` |
| `x-metrics`、`x-tracing` | `library/x-observability` 的 `metrics/tracing` 模块 |
| `x-mobile-runtime`、`x-platform-desktop`、`x-ui-render` | `x-ui::{native,renderer}`；满足拆分门禁后再独立 |
| `x-net-protocols` | `x-server::{http,quic,grpc}` |
| `x-numeric-decimal` | `library/x-decimal` |
| `x-os-signal`、`x-process`、`x-pal` | `runtime/xrt-process`、`runtime/xrt-pal` |
| `x-plugin` | `tools/x-build` 的插件宿主 + `specs/abi/plugin` |
| `x-profiler-advanced` | `tools/x-profiler` 的 feature-gated 硬件适配器 |
| `x-reflect` | `compiler/x-analysis` 的受限反射查询实验 |
| `x-codegen` | `compiler/x-codegen-api` + `compiler/x-codegen-llvm` |
| `x-source-map` | `compiler/x-source` 的 `SourceMap` 公共模型 |
| `x-runtime` | `runtime/xrt-*` 系列，不建立无边界总包 |
| `x-async` | `runtime/xrt-task`、`xrt-scheduler` + `specs/concurrency` |
| `x-dynamic` | `library/x-dynamic` + `compiler/x-types` 的边界检查 |
| `x-migrate` | `tools/x-migrate` + `tools/x-api-diff` |
| `x-deploy` | `infra/`、`distribution/`、`release/` 的部署模板与验证任务 |
| `x-observability` | `library/x-observability` + `runtime/xrt-observe` |
| `x-regex-compile` | `library/x-regex` + `compiler/x-consteval` |
| `x-runtime-affinity` | `runtime/xrt-thread` 的 `affinity/numa` 模块 |
| `x-sanitizer`、`x-unsafe` | `tests/security` + `tools/x-debug` 的审计模式 |
| `x-scheduler-jobs` | `library/x-job-scheduler` |
| `x-serverless-bindgen`、`x-serverless-snapshot` | `x-server::serverless::{bindgen,snapshot}` 实验模块 |
| `x-snapshot` | `tools/x-replay` 的 `snapshot` 模块 + 平台 Core/Minidump 适配 |
| `x-symbolic` | `tools/x-symbolic-check`；通用程序合成保留 `labs/x-symbolic-research` |
| `x-realtime` | `runtime/xrt-realtime`；硬实时认证保留 `labs/x-realtime-research` |
| `x-pmem` | `library/x-pmem`；隐式持久对象研究位于 `labs/x-pmem-research` |
| `x-autotune` | `tools/x-autotune`；业务逻辑搜索位于 `labs/x-autotune-research` |
| `x-std-memory` | `library/x-alloc`、`x-std-cell` |
| `x-supply-chain` | `security/`、`tools/xpm-client`、`release/` |
| `x-test-mock`、`x-test-snapshot` | `tools/x-test-runner` 的 `mock/snapshot` 模块 |
| `x-agent-ml`、`x-agent-sys`、`x-agent-workflow` | `x-ai-tools::agent` 的受权工具适配器；不得进入 compiler |

### 6.1 `XLC-*` 派生需求的物理责任域

| 派生需求系列 | 主责任目录 | 必须协作的目录 | 禁止的反向依赖 |
|---|---|---|---|
| `XLC-CORE-*` | `specs/language`、`specs/memory-model`、`specs/concurrency`、`compiler/` | `tests/conformance`、`tools/x-migrate` | 规范与 compiler 不得依赖 ecosystem/ai/ml/labs。 |
| `XLC-EXEC-*` | `compiler/x-mir-interpreter`、`x-instrumentation`、`backends/x-codegen-fast`、`tools/` | `tests/tools`、`benchmarks/` | 快速后端不得定义不同于 LLVM 的语言行为。 |
| `XLC-FFI-*` | `sdk/`、`tools/x-bindgen`、`specs/ffi` | `tests/interoperability`、`distribution/` | SDK 不得暴露 compiler 私有 AST/HIR。 |
| `XLC-WEB-*` | `x-web::{runtime,dom,api,worker,ui,framework,ssr,tooling}` | Core 的 WASM 后端公共接口、联邦仓库测试 | Web 框架不得成为 core/std 或 compiler 依赖。 |
| `XLC-STYLE-*` | `x-ui::{style,native,a11y}` + `x-web::ui` | `specs/style`、联邦仓库 accessibility 测试 | 浏览器 Cascade/Flex/Grid 交给标准 CSS；样式不得改变核心求值规则。 |
| `XLC-SERVER-*` | `x-server::{http,api,resilience,traffic,runtime,cloud}` | 稳定观测 API、联邦仓库安全测试 | 云/K8s 适配不得进入 runtime 最小 ABI。 |
| `XLC-PLATFORM-*` | `compiler/x-target-spec`、`runtime/xrt-pal`、`distribution/`、`release/` | 平台 CI、`tests/reproducibility` | Tier 3/实验目标不得降低 Tier 1 发布门禁。 |

### 6.2 原始价值回归后的稳定/研究拆分

第二轮复审采用“双落点”而非整体搁置：成熟、受限、可测试的部分进入 compiler/runtime/library/tools/ecosystem；只有通用化、自治化或认证级难题留在 Labs。稳定项目只能依赖公开实验接口，不能依赖 Labs 实现。

| 价值域 | 回归实施项目 | 继续隔离的研究部分 |
|---|---|---|
| 契约与 Effect | `compiler/x-contracts`、`x-effects` | 完整形式化证明和开放效果代数另立 RFC。 |
| 能耗与时间 | `library/x-energy`、`x-distributed-time` | `labs/x-energy-research` 的跨中心自治策略。 |
| PMEM | `library/x-pmem` 显式事务 | `labs/x-pmem-research` 的隐式持久对象。 |
| Replay/调试 | `tools/x-replay`、`x-profiler` | `labs/x-replay-research` 的通用完全重放。 |
| 自动调优 | `tools/x-autotune` 的参数/Profile 搜索 | `labs/x-autotune-research` 的业务逻辑演化。 |
| 合规与符号执行 | `tools/x-compliance-analysis`、`x-symbolic-check` | 跨系统证明和通用程序合成。 |
| 实时 | `runtime/xrt-realtime` 的 Deadline/Budget/软实时 | `labs/x-realtime-research` 的硬实时认证。 |
| 生产影子 | `tools/x-dev-shadow` 的脱敏只读回放 | `labs/x-dev-shadow-research` 的受控写流量。 |

### 6.3 `XLE-*` 日常开发与 AI 风险责任域

| 系列 | 主责任目录 | 关键边界 |
|---|---|---|
| `XLE-GOV-*` | `specs/requirements`、`specs/governance`、`governance/`、`docs/decisions` | 规则和决策必须可追溯，不由 Agent 静默裁决冲突。 |
| `XLE-DEV-*` | `tools/x-doctor`、`x-workspace-guard`、`x-repro`、`xpm-audit`、`x-codegen-manifest` | 不覆盖用户变更；依赖和生成工件可验证、可回滚。 |
| `XLE-DATA-*` | `x-server::db`、稳定 `schema/std/cache` API、`security/data-governance` | 数据迁移、时间、文本、文件和数值行为必须跨版本/平台验证。 |
| `XLE-OPS-*` | `runtime/xrt-resource`、`tools/x-fault-injection`、`x-chaos`、`x-test-isolation`、`x-release-control` | 故障注入只能作用于授权环境；发布控制与数据兼容协同。 |
| `XLE-AI-*` | `x-ai-tools::{context,policy,verify,review,provenance,eval}` | AI 不绕过权限、测试、安全、许可证、人工审批和预算。 |

逻辑目标补充映射：`x-db-migrate` → `x-server::db::migrate`；`x-time` → `library/x-std/time` + `runtime/xrt-time`；`x-text` → `library/x-i18n`；`x-fs` → `library/x-std/fs`；`x-stream` → `library/x-std/stream`；`x-resource-governor` → `runtime/xrt-resource`；`x-data-governance` → `security/data-governance`。

映射表是架构适应度测试的输入：功能矩阵出现新的 `x-*` 目标时，必须先映射到现有项目，只有无法满足单一职责且 ADR 获批后才能新增物理目录。

## 7. 开发者 X-Lang 项目模板

```text
my-x-project/
├─ x.toml                       # 包、workspace、依赖、target、profile
├─ x.lock                       # 解析后的不可手改依赖图
├─ README.md
├─ LICENSE
├─ src/
│  ├─ main.x                    # 二进制入口
│  ├─ lib.x                     # 库入口
│  └─ domain/                   # 领域命名模块，不使用 misc/common
├─ tests/
│  ├─ integration/
│  └─ fixtures/
├─ benches/
├─ examples/
├─ docs/
├─ .x/
│  ├─ config.toml               # 项目级工具配置
│  └─ rules.toml                # 结构化 Agent/团队规则
├─ target/                      # 生成目录，不提交
└─ .gitignore
```

## 8. 测试、发布和维护目录责任

| 生命周期 | 权威目录 | 必须内容 |
|---|---|---|
| 规范 | `specs/` | 规则 ID、示例、兼容政策、生成语法 |
| 提案 | `rfcs/` | Motivation、Design、Alternatives、Compatibility、Rollout |
| 决策 | `docs/decisions/` | Context、Decision、Alternatives、Consequences |
| 开发 | 各项目 `src/tests/docs` | 契约优先、回归测试、项目 README |
| 符合性 | `tests/conformance` | compile-pass/fail/run、平台期望 |
| 安全 | `security/`、`tests/security` | 威胁模型、沙箱、供应链、响应 |
| 性能 | `benchmarks/` | 环境、数据、统计、回归阈值 |
| 发布 | `release/`、`distribution/` | 通道、签名、SBOM、回滚、公告 |
| 运维 | `docs/operations/`、`infra/` | SLO、告警、Runbook、RTO/RPO |
| 追溯 | `docs/traceability/` | XLF→Spec→RFC/ADR→Module→Test→Release |

## 9. 建仓顺序

1. 建立根治理、`specs/`、`docs/decisions/`、`tests/conformance/` 和最小 CI；没有首份内容时不建空目录。
2. 建立模块化 `x-compiler`，以内部分层完成 Source、诊断、Token、Lexer、可恢复 Parser、AST、Resolve、Type、HIR/MIR 和验证器。
3. 建立 `x-codegen-llvm` 适配、最小链接与 Driver，完成 Hello World 端到端原生编译。
4. 建立最小 `x-runtime`、`x-core/x-alloc/x-std`，明确 Runtime ABI、分配、panic 和平台边界。
5. 建立 `x-cli` 与 conformance/spec-check，形成 `check/build/run/test/fmt` MVP 闭环。
6. 只有内部模块出现稳定消费者、隔离或编译收益后，才按本目录图拆出 source/syntax/semantic/IR 等独立 crate。
7. 核心稳定后依次建立 XPM、LSP、IDE、增量编译、调试和发布服务。
8. `x-web/x-ui/x-server/x-sdk/x-ai-tools/x-ml` 联邦仓库与 Labs 只能在稳定接口出现后并行立项；不得提前让核心依赖实验项目。

## 10. 目录架构验收清单

- [ ] 原始功能矩阵中的每个 `XLF-*` 都进入 Traceability 工件，并映射到一个主责任域；跨域依赖明确。
- [ ] 每个叶子项目有 README、Owner、契约、测试和成熟度。
- [ ] Core 不依赖 Ecosystem/Labs，Compiler Frontend 不依赖 LLVM/Runtime/UI。
- [ ] 所有内部工件带版本和验证器，所有外部输入在边界验证。
- [ ] 三大 OS 的构建、测试、安装和回滚目录均有流水线责任人。
- [ ] 实验项目默认关闭、有预算、威胁模型和退出报告。
- [ ] 文档、RFC、ADR、代码和测试通过功能 ID 自动追溯。
- [ ] 目录树变更必须通过 ADR；禁止无职责说明的新顶层目录。
