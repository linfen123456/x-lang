---
doc_id: DOC-IMPLEMENTATION-TASK-DAG
authority: implementation
owner: role/documentation
backup_owner: role/architecture
version: "1.0"
maturity: EXTENDED
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF, XLC, XLE]
---
# X-Lang 实施任务依赖 DAG

> 状态：草案｜Owner：Program Management + Architecture Council｜追溯：XLF-*、XLC-*、XLE-*

## 主关键路径

    G0 规范冻结
      → Source/Lexer/Parser
      → Resolve/Types/Borrow
      → HIR/MIR + Verifier
      → TargetSpec + Codegen API
      → LLVM/Linker + Runtime ABI
      → Driver/CLI
      → Conformance/CI
      → Std/XPM
      → LSP/IDE/Incremental/Debug
      → 1.0 Release

PAL/Runtime、Testing/CI 和 Traceability 从 P0 并行；P5/P6 只能依赖稳定接口。

## 阶段任务与门禁

| 阶段 | 任务组 | 前置 | 主要输出 | 门禁/回滚 |
|---|---|---|---|---|
| P0 | SPEC、LEX、PARSE、LLVM-PROBE、E2E | RFC/ADR | EBNF、正反语料、AST、Hello World | G0；不可行则回退 ADR |
| P1 | RESOLVE、TYPE、HIR/MIR、CODEGEN、RUNTIME-MIN、DIAG、CI | P0 | 多文件 CLI、对象/链接、错误 JSON | G1；关闭新增语义 gate |
| P2 | BORROW、TRAIT、MODULE/XPM、CORE/STD、CLI、OPT | P1 | 安全核心库、x.toml、基础优化 | 回退上一 IR/Pass |
| P3 | XPM、LSP/IDE、QUERY/CACHE、DAP、RELEASE | P2 | 开发闭环、增量、安装回滚 | 禁用增量/实验插件 |
| P4 | SPEC-FREEZE、API、SECURITY、PERF、DOCS | P0-P3 | 1.0、SBOM、签名、迁移 | No-Go 保持 Beta/LTS |
| P5 | WASM、FFI SDK、Web、Server、DB、Mobile/UI | P4 接口 | 独立生态制品 | 单项目撤回，不影响 Core |
| P6 | AI/MCP、Tensor/GPU、eBPF、Realtime、ZKP、Replay、GC | RFC + P4/P5 | 原型、基准、威胁模型、退出报告 | 默认关闭，失败即归档 |

## 任务卡与验收

每卡必须有 task_id、阶段、Owner、XLF/XLC/XLE、范围/非范围、规范/RFC/ADR、输入输出 schema、不变量、依赖、资源/线程/取消限制、测试命令、性能/安全预算、制品保留、回滚动作、验收证据和下一门禁。每阶段必须提交追溯报告、单元/符合性/负向/fuzz/性能/安全测试、跨平台结果、可复现命令、制品 manifest 和 Go/No-Go ADR。

## 失败处理

编译器契约失败拒绝新 schema；运行时失败切换 PAL fallback 或旧 ABI；工具失败使用离线模式与旧 lockfile；CI/发布失败阻断晋级并保留日志、SBOM、签名和制品；研究失败解除稳定项目依赖并归档数据。
