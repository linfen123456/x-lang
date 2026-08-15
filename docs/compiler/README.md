---
doc_id: DOC-COMPILER-README
authority: implementation
owner: role/compiler-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-001, XLF-01-002, XLF-02-001, XLF-02-002, XLF-02-004, XLF-02-009, XLF-02-012, XLF-02-014, XLF-10-001, XLF-10-002, XLF-11-013]
---
# X-Lang 编译器工程实施规范

> 状态：草案｜Owner：`role/compiler-team`｜本专题所有实现承诺必须回到规范、RFC/ADR、测试与制品证据。

## 目标、非目标和边界

本专题把源文件稳定地编译为可验证的 AST、HIR、MIR、对象和可安装制品，并为 CLI、LSP、DAP 与增量查询提供同一套接口。编译器分为 SourceManager、Lexer/Parser、AST、Name/Type/Trait/Borrow 分析、HIR/MIR、Query/Cache、Optimizer、Target/Backend、Driver/Diagnostics；每个边界只能消费上游公开工件。

非目标：本专题不重新定义语言语义，不把 LLVM、宿主环境、运行时私有结构或 IDE 协议泄漏进前端，不对实验性 GC、GPU、eBPF、硬实时和自动 AI 优化作 CORE 承诺。实验能力必须有独立 feature gate、资源预算、退出条件和回滚方案。

## 工程不变量

1. 同一 `source_fingerprint + edition + compiler_version + target_fingerprint + profile + features` 必须得到同一语义结果；未声明的环境变量、时间、网络和随机数不能进入查询键。
2. 阶段只能生成通过 verifier 的工件。验证失败是结构化编译错误，不得通过 `unwrap`、静默修复或降级继续生成后端制品。
3. Span 以 UTF-8 字节偏移为主、以行列为派生视图；任何诊断都不得引用不存在的文件或越过源文件边界。
4. 取消、超时、配额拒绝和内部错误都不能提交部分查询结果、缓存索引或最终制品；临时文件必须可安全清理。
5. 优化只能保持语言可观察行为、Drop 顺序、panic/错误边界、布局和 ABI；不能用优化结果替代规范规则。

## 公共 Profile（唯一 schema 与优先级）

所有编译器、XRT 和工具共享 `ProfileSpec{name:ProfileId,base:ProfileId?,optimization:OptimizationLevel,limits:ResourceLimits,capabilities:BTreeSet<Capability>,network:NetworkPolicy,determinism:Determinism,diagnostics:DiagnosticPolicy}`。`ResourceLimits` 字段为 `max_source_bytes:u64`、`max_ir_nodes:u64`、`max_cpu_ms:u64`、`max_memory_bytes:u64`、`max_parallelism:u16`、`cancel_grace_ms:u64`。优先级固定为 `CLI 显式值 > x.toml [profile.<name>] > TargetSpec 默认 > 工具链默认`；环境变量只能作为 `DeclaredInputs` 显式加入，不能覆盖 Profile。`dev` 默认诊断完整、`O0`、IR 可倾印；`release` 使用显式 `O2`；`ci` 固定随机种子、禁止网络；`conformance` 禁止未决 feature；`cross` 使用显式 sysroot。未知 Profile/字段拒绝；提高上限需审计，降低上限必须报告。

## 阶段和完成定义

| 阶段 | 输入→输出 | 必须验证 | 失败与回滚 |
|---|---|---|---|
| Source/Lex/Parse | 文件→Token/AST | 编码、Span、AST 结构 | 保留旧 AST，返回诊断 |
| Semantic | AST→Def/Type/Trait/Borrow | 名称、类型、能力和借用 | 不写入增量缓存 |
| Lowering | AST→HIR→MIR | CFG、Place、Drop、类型 | 回退上一 schema |
| Optimize | MIR→MIR | Pass 前后 verifier 与差分 | 关闭单 Pass，回到 O0 |
| Backend | MIR+TargetSpec→Object | 目标、ABI、汇编和链接 | 切换已验证后端或失败 |
| Driver | 工件→ArtifactManifest | 原子输出、签名和重现 | 删除临时目录，保留日志 |

完成定义必须包括：实现提交、正/负/边界测试、fuzz、性能 P50/P95/P99 与内存峰值、跨 Tier 1 结果、诊断快照、SBOM/签名（适用时）、真实 XLF 追溯和可执行回滚演练。

## 文档索引

- [架构与阶段边界](./architecture.md)
- [前端与语义分析](./frontend.md)
- [HIR/MIR 与验证器](./hir-mir.md)
- [优化 Pass](./optimizer.md)
- [TargetSpec、Backend 与代码生成](./codegen.md)
- [Driver、查询和制品](./driver.md)
- [公共接口契约](./interfaces/contract.md)

## 统一负向验收集

至少覆盖非法 UTF-8、未闭合 token、深嵌套、恢复后重复错误、重复定义、歧义 trait、递归类型、借用冲突、未知工件 schema、错误 fingerprint、查询循环、缓存污染、Pass 误变换、未知 target、链接器失败、磁盘满、并发取消和诊断输出超限。规划中的案例使用明确注册项 `TEST-COMPILER-NEG-001` 至 `TEST-COMPILER-NEG-003`，状态为 `planned`，不得在测试实现前声称已有证据。

## 版本与回滚

公开结构使用 `schema_version: "1.0"` 的主版本/次版本策略：次版本只追加字段并给出默认值，主版本不兼容时拒绝读取并提示迁移命令。编译器版本回滚必须能读取上一稳定锁文件和源文件；缓存可整体失效，不能以旧缓存冒充新语义。规则改变只能在新 Edition 或 feature gate 中启用。
