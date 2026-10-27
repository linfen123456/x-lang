> 已归档：见 v2 [README.md](../../README.md)

# X-Lang

X-Lang 是一个处于语言设计和工程规划阶段的现代原生编程语言项目，首要研究方向是系统工具、CLI、服务端和跨平台开发。

初始实现计划采用 Rust + LLVM，核心安全方向采用所有权、借用与 RAII。当前仓库只有文档、大纲、`Proposed` RFC 和 ADR，没有编译器源码、可运行版本或正式 X-Lang 1.0 规范。

## 项目原则

- 安全和正确性优先于语法便利与功能数量；
- 追求小而正交的语言核心，生态能力优先由库、协议和工具承载；
- 所有性能、安全和“领先”结论必须有可复现证据；
- 实验与研究能力不得反向依赖或阻塞稳定核心；
- 同一事实只保留一个权威来源，其他文档通过链接引用。

## 阅读顺序

1. [企业级完整文档体系总纲](docs/X-Lang企业级完整文档体系总纲.md)：项目范围、文档权威顺序与实施阶段。
2. [语言规范与学习研究大纲](docs/X-Lang语言规范与学习研究大纲.md)：语言定位、品质判定和待完成的正式规范。
3. [编译器工程实施文档大纲](docs/X-Lang编译器工程实施文档大纲.md)：编译器、运行时、工具链、测试和发布路线。
4. [完整项目目录架构与模块说明](docs/X-Lang完整项目目录架构与模块说明.md)：D0、P0/P1、P2-P4、P5+ 的阶段化物理架构、依赖与拆分门禁。
5. [RFC 索引](rfcs/README.md)：核心语法/语义、模块、数据、JSON、包管理和构建的待评审规范提案。
6. [架构决策索引](docs/decisions/README.md)：XPM/XBuild、模块化单体、P0 剖面冻结、Rust/LLVM 基线等工程决策。
7. [实现设计索引](docs/design/README.md)：P0 切片、语义门禁、[XUI/平台](docs/design/xui-and-platforms.md)、[AI/学习](docs/design/ai-development-and-learning.md)与[证据矩阵](docs/design/evidence-and-platform-gates.md)等 Proposed 编码设计。
8. [文档索引](docs/README.md)：全部保留文档的职责和阅读入口。

## 当前仓库

```text
x/
├─ README.md                  # 项目入口
├─ rfcs/                      # Proposed 规范提案及状态索引
└─ docs/
   ├─ README.md               # 文档索引与最小维护规则
   ├─ X-Lang*.md              # 8 份保留大纲、矩阵与路线文档
   ├─ decisions/              # Proposed/Accepted 架构决策
   ├─ design/                 # 实现级设计（非第二语言规范）
   └─ 原始文档/               # 12 份历史原始需求，只读保留
```

除上述内容外，不创建重复规格、重复技术基线、临时方案或空目录。`specs/` 只在首份 RFC 被接受并生成正式规则时创建；代码和测试目录只在开始实际实现时创建。

## 当前状态

| 范围 | 状态 |
|---|---|
| 原始需求与追溯 | 已建立大纲基线 |
| 文档责任边界 | 已建立大纲基线 |
| X-Lang 1.0 语言剖面 | 已形成设计宪法、最小语法和语义边界候选；尚待 RFC 批准 |
| 语言语法与正式语义 | 已有 31 个候选关键字及词法→求值→所有权/Drop→错误清理的 `Proposed` RFC 链；尚待批准、实现和符合性验证 |
| 模块、模式、包与构建规则 | 已建立 `Proposed` RFC 和 ADR；数量及状态以各自索引为准，尚未批准或实现 |
| 项目架构 | 已形成 D0→P5+ 阶段化候选；P0/P1 采用 4～6 成员模块化单体；P0 实现设计与 Rust/LLVM 基线 ADR 已 Proposed |
| 编译器、运行时、标准库 | 尚未实现；实现设计见 `docs/design/` |
| XUI、Web/WASI、桌面/移动/微信与 AI SDK | 仅有 [RFC-0011](rfcs/0011-xui-typed-declarative-and-platform-capabilities.md) 等 Proposed 提案和设计；尚无适配器或应用实现 |
| 性能、安全、生态成熟度 | 尚无实现证据 |
| 许可证 | 待确定 |

在核心 RFC、实现和验证证据完成前，项目只能称为“X-Lang 文档与架构大纲”，不能称为已经实现的 X-Lang 1.0。
