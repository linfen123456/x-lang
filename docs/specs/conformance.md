---
doc_id: DOC-SPECS-CONFORMANCE
title: X-Lang 符合性、诊断与实现状态规范
authority: normative
owner: role/qa-team
backup_owner: role/language-council
version: "0.2.0"
maturity: CORE
status: 草案
phase: P0
last_reviewed: 2026-08-15
applies_to: [compiler, interpreter, runtime, conformance-suite, release]
traceability_scope: [XLF, XLC, XLE, GOVERNANCE, QUALITY]
supersedes: [DOC-SPECS-CONFORMANCE-LEGACY]
---

# X-Lang 符合性、诊断与实现状态规范

## 1. 目标与术语

本文定义如何判断实现是否符合语言规则、如何报告诊断以及何时可以使用 Core/Extended 等成熟度标签。符合性是对可观察语义的判断，不等同于通过某个后端编译。实现等级与文档状态分离：Core 可以仍为草案，草案不能被宣称为已稳定。

术语：参考实现是通过规则测试且可复现构建的实现；实现定义是规范允许实现选择且必须在 target/profile 中公开的结果；未指定是程序不得依赖的结果；禁止行为是实现必须诊断或拒绝的行为；符合性套件是版本化 pass/fail/boundary 测试集合。

## 2. 符合性规则

### RULE-CONF-001：实现等级

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** Core 实现必须具备已决策规则文本、至少一个参考实现、pass/fail/diagnostic 测试、三大首批 OS 中至少一个 Tier 1 目标和无已知高危安全缺陷。Extended 必须不改变 Core 语义并具备 feature gate、降级方案和平台矩阵。Experimental 必须有 RFC、原型、资源预算、基准、安全边界和退出条件。Research 必须位于独立 labs，禁止成为 Stable 必需依赖。

**解释。** 成熟度描述能力，不表示所有接口已实现。缺少证据时最多标 Experimental。

**正例。** 规则在 MIR、LLVM 和至少一个解释器通过三类测试，发布报告标 Core。

**反例。** 仅 Windows Debug 原型通过却声明跨平台稳定，报告 X-E5001 maturity evidence missing。

**边界。** 平台能力不足可标 unsupported 或 degraded；不能把跳过测试当 pass。

**诊断/测试/追溯。** X-E5001；TEST-CONF-MATURITY-001..003；来源 XLF-11-001、XLE-GOV-002；RFC/ADR：无，沿用治理状态机。

### RULE-CONF-002：规则 ID 与状态

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 规范规则必须使用全仓库唯一 RULE-域-NNN 格式；历史规则前缀不再作为规范 ID 使用。规则定义表只能有一个权威行；每个规则必须有成熟度、状态、追溯、测试和 RFC/ADR 字段；ID 不得复用，替代使用 supersedes。

**解释。** 统一 ID 使编译器、测试和文档双向追溯。旧文档中的 XSP 名称属于历史别名，不能写入新规则。

**正例。** RULE-MEM-001 在内存规范定义，测试和编译器错误引用该 ID。

**反例。** 新增历史前缀规则或重复定义 RULE-MEM-001，报告 X-E5002。

**边界。** 规则域可扩展但必须登记；示例字符串不算规则定义，检查器仍应提示疑似旧 ID。

**诊断/测试/追溯。** X-E5002；TEST-CONF-ID-001..004；来源 governance/status-and-id-rules、XLF-01-002；RFC：无（治理已决策）。

### RULE-CONF-003：测试映射和三类样例

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 每个 CORE/EXTENDED 规则至少有一个 pass、一个 fail 或 diagnostic、一个 boundary 测试；测试必须记录 target、profile、预期退出码或诊断码。规则缺少映射时 Stable 门禁必须失败。

**解释。** 单一正例不能证明拒绝错误程序，也不能覆盖资源/平台边界。测试可共享，但 manifest 必须逐规则列出。

**正例。** RULE-LANG-001 映射 UTF-8 合法、非法和 CRLF span 三个测试。

**反例。** 只有 README 示例没有 compile-fail 测试，报告 X-E5003。

**边界。** 平台不支持的测试必须记录 skip、原因和 Issue；无理由跳过等同缺失。

**诊断/测试/追溯。** X-E5003；TEST-CONF-MAP-001..003；来源 XLF-12-020、XLE-OPS-007；RFC：无。

### RULE-CONF-004：诊断稳定性

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 编译诊断必须有稳定 X-E####/X-W#### 代码、严重级别、主 span、结构化参数和可选 fix-it。文本可本地化，代码不能依赖语言。fix-it 只有在可证明不改变语义或取得用户确认时才可自动应用；诊断 JSON Schema 只追加字段，破坏性变化必须升级版本。

**解释。** IDE/LSP/Agent 消费代码和 span，而不是自然语言。

**正例。** 借用冲突输出 X-E4002、两个 span 和候选重构建议。

**反例。** 只输出 type error 或根据语言环境变化代码，报告 X-E5004。

**边界。** 解析错误可有多个候选 span；主 span 应最小，JSON 可列 related spans。

**诊断/测试/追溯。** X-E5004；TEST-CONF-DIAG-001..005；来源 XLF-02-002、XLF-11-008、XLE-AI-005；RFC-DIAG-01（P1）。

### RULE-CONF-005：跨实现与跨后端

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 对声明为确定的程序，解释器、MIR 执行器、LLVM 后端和未来 WASM 后端必须产生相同可观察结果；实现定义结果必须在 target/profile 中列明并分组测试。优化失败不得静默改变结果，必须回退或拒绝编译。

**解释。** 差分测试发现 lowering 错误，不要求所有后端支持同样系统能力。性能或栈回溯差异只有在规则明确规定时才是语义差异。

**正例。** -O0 与 -O2 的 Result、Drop 顺序和输出一致。

**反例。** LLVM release 溢出依赖 poison 导致与解释器不同，报告 X-E5005。

**边界。** 时间、随机、OS errno、线程调度和 fast-math 只在严格模式差分；非确定性必须记录种子/输入。

**诊断/测试/追溯。** X-E5005；TEST-CONF-DIFF-001..006；来源 XLF-01-001、XLF-12-012、XLC-CORE-010；RFC-EVAL-01、RFC-NUM-01。

### RULE-CONF-006：发布门禁与回滚

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** Stable/LTS 发布必须生成 RULE→实现→测试→版本→平台报告，包含未覆盖项、已知问题、SBOM、签名和可复现结果。任何 CORE 规则缺测试、权限/安全高危问题、不可解释差分失败或不可回滚迁移都阻止发布。降级须保留旧规则、失败证据和迁移/RFC 记录。

**解释。** 回滚保留历史，不是删除新实现；旧 Edition 和制品保留到支持期结束。

**正例。** 规则回归后通道退回 Beta，并保留失败快照和修复任务。

**反例。** 删除失败测试或把 skipped 改为 passed，报告 X-E5006。

**边界。** Nightly 可含 Experimental，但必须显式标记且不污染 Stable lockfile；安全紧急修复需事后复核。

**诊断/测试/追溯。** X-E5006；TEST-CONF-RELEASE-001..005；来源 XLF-11-001、XLF-11-002、XLE-OPS-008；ADR-RELEASE-01。

## 3. 测试层级、性能和安全

当前仓库处于“文档规范阶段”，尚未创建编译器源码与 `tests/` 目录。正文中的 `TEST-*` 都是计划测试标识，不是已执行证据；编号范围（例如 `001..006`）表示后续必须逐一建立的独立案例。任何专题不得因列出了 TEST 字符串就把状态提升为“已验证”。P0 开始实现时，质量团队需为每个标识补充下列可读测试卡，并在运行后附上真实命令、目标、结果和制品位置。

| 字段 | 要求 |
|---|---|
| Test ID / Rule | 唯一测试 ID 与所验证的 RULE；共享案例需列出全部规则 |
| Kind | compile-pass、compile-fail、diagnostic、boundary、runtime、differential 或 platform |
| Source / Input | 最小输入、Edition、Feature、依赖和数据来源 |
| Target / Profile | 目标三元组、Debug/Release/checked、优化级别及实现版本 |
| Expected | 退出码、诊断码与 span、stdout/stderr、所有权/Drop/状态机后置条件 |
| Limits | 时间、内存、递归、线程、输出和取消 deadline |
| Evidence | 实际运行命令、环境摘要、结果与失败制品；未运行时必须写 planned |

首批符合性切片如下，它们是后续实现的最低任务边界：

| Test ID | Kind | 最小输入与预期 |
|---|---|---|
| TEST-LANG-LEX-001 | pass | UTF-8、CRLF 与 Unicode 标识符产生稳定 Token/Span |
| TEST-LANG-LEX-002 | fail | 非法 UTF-8 返回 X-E1001，不崩溃、不产生可发布 AST |
| TEST-LANG-PARSE-001 | pass | inherent impl、trait impl、receiver、slice、lifetime、closure 与 gated async 示例均按 Edition 解析 |
| TEST-LANG-PARSE-002 | boundary | 深度/节点上限触发资源诊断，不栈溢出或提交部分工件 |
| TEST-LANG-TYPE-001 | pass/fail | 推断、显式转换、穷尽匹配各含一正一反案例，诊断 span 指向最小表达式 |
| TEST-MEM-BORROW-001 | pass/fail | 移动后使用、共享/可变借用冲突、返回悬垂引用和字段借用 |
| TEST-CONC-MODEL-001 | differential | Release/Acquire、Fence、Relaxed 反例和 Channel 同步边按 litmus 结果分组 |
| TEST-LANG-PANIC-001 | runtime | normal/Result/unwind/abort 的 Drop 次序及 FFI 边界行为符合 Profile |
| TEST-FFI-C-001 | platform | LLP64/LP64 的 repr(C)、ptr+len、callback destroy 竞态和错误 shim golden |
| TEST-COMPILER-E2E-001 | end-to-end | Hello World 经 Source→MIR→O0 Backend→Linker→CLI，失败不留下半成品 |

| 层级 | 输入 | 必须证明 | 典型 ID |
|---|---|---|---|
| Lexer/Parser | token、语法、恶意深度 | 不崩溃、span、AST | TEST-LANG-LEX/PARSE |
| Semantic | 类型、Trait、借用 | pass/fail、诊断、无级联失控 | TEST-LANG-TYPE、TEST-MEM |
| MIR/IR | verifier、优化前后 | 不变量、Drop、差分 | TEST-COMP-IR |
| Runtime | OOM、取消、线程、I/O | 清理、错误、资源界限 | TEST-RUNTIME-* |
| Integration | 包、FFI、Web、平台 | 协议/ABI/降级 | TEST-FFI/WEB-* |
| Release | lock、SBOM、签名、复现 | 供应链和回滚 | TEST-RELEASE-* |

性能数字必须记录硬件、OS、X/LLVM/Rust 版本、profile、输入、预热、样本、P50/P95/P99、置信区间和复现命令。原始资料中“函数调用 <1ns”“协程 20ns”“冷启动 <50ms”等数字只能作为候选基准，不能写成保证。

安全测试必须覆盖不可信源码、宏/构建脚本、包注册表、FFI、浏览器输入、路径、秘密、Prompt Injection 和资源耗尽。高危错误必须阻止 Stable 或降级 maturity。

## 4. 待决事项

| RFC | 候选 | 门禁 | 最迟阶段 |
|---|---|---|---|
| RFC-DIAG-01 | 稳定 JSON、fix-it 语义 | LSP/CLI/Agent schema 兼容 | P1 |
| RFC-EVAL-01 | 严格差分边界 | MIR interpreter 与优化证明 | P1 |
| ADR-RELEASE-01 | Nightly/Beta/Stable/LTS | 签名、复现、回滚演练 | P3 |
| RFC-CONF-01 | 参考解释器长期保留与否 | 成本、差分收益、bootstrap | P2 |

在 RFC 通过前，规则 ID 和测试门禁有效，但实现等级只能按证据标注。
