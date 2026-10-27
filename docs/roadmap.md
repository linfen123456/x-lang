# 路线图：阶段、交付物与门禁

> 类型：Plan｜唯一负责：阶段定义（M0、P0–P5、R）、各阶段交付物、验收标准、退出门禁、语言特性的阶段归属。

## 1. 结论

- 共 8 个阶段标识：`M0 → P0 → P1 → P2 → P3 → P4(=1.0) → P5(1.0 后)`，另加不设日期的研究赛道 `R`。全体系不再使用其他阶段编号。
- **初级稳定需求（MVP）= P2 末的 Core-CLI 0.x 稳定子集**：可以用 X-Lang 写出并维护两个真实 CLI 工具，并具备安全保证。
- 每个阶段都以**可执行门禁**结束，不以日期结束。时长都是【推断】，在 P0 结束时按实测速度校准一次（[ADR-0008](decisions/ADR-0008-pre-kickoff-decisions.md) K12）。人员到位之前，所有 Lead 角色都由 Project Lead 兼任（K11）。

## 2. 阶段总览

| 阶段 | 名称 | 核心交付 | 规模/时长【推断】 | 依赖 |
|---|---|---|---|---|
| M0 | 启动 | 治理落地、工具链锁定、仓库骨架、CI、LLVM 探针 | 2–3 人，4 周 | 无 |
| P0 | 纵向骨架 | 单文件 `.x` → 原生可执行文件（Linux x86_64 + Windows x86_64 MSVC 双主机）；CST 解析；符合性 runner | 2–3 人，3 个月 | M0 |
| P1 | Core-CLI 0.1 | 多文件模块、单包 + Path 依赖、泛型/Trait 基础、受限借用检查、`Result/?`、最小 std、`x test/fmt`、查询式 Driver、MIR 解释器 | 4–6 人，6–9 个月 | P0 |
| P2 | Core 0.x 稳定子集（MVP） | 完整 NLL、Trait 全最小集、闭包/Fn、`@derive`、作用域线程/通道/原子、core/alloc/std 分层、`static`/const、`@cfg`、doc-test、PubGrub 原型 | 8–12 人，12 个月 | P1 |
| P3 | Alpha 工程化 | LSP + VS Code、落盘增量、Registry 客户端与签名、DAP 调试、交叉编译、WASI 探针；生态并行：XUI 原型、x-json、x-http、MCP 只读 | 12–20 人，12 个月 | P2；稳定查询 API |
| P4 | 1.0 | 规范冻结、首个稳定 Edition、Tier 1 × 4、性能/安全基线、`x publish`、API diff、SBOM/可复现、no_std 子集冻结 | 15–25 人，9–12 个月 | P3 |
| P5 | 1.0 后 | async/await Edition、WASM Tier 2、移动/桌面、裸机/eBPF、SDK 绑定、自举、生态扩展 | 按目标立项，每项 3–6 人 | P4 |
| R | 研究赛道 | GC、ZKP、Effect、硬实时、通用重放等 | 每项独立预算 | 仅依赖公开 API |

```mermaid
flowchart LR
  M0 --> P0 --> P1 --> P2 --> P3 --> P4 --> P5
  P3 -. 生态并行 .-> ECO[eco: XUI 原型 / x-json / x-http / MCP]
  P4 -. 1.0 后 .-> P5
  R[[R 研究赛道：不阻塞主线]]
```

## 3. 各阶段验收与退出门禁

所有命令以仓库根目录为工作目录。“门禁”指 CI 中必须为绿的检查。

### M0 启动

| 交付物 | 验收（可执行） |
|---|---|
| 开工决策已闭环（ADR-0001～0008 Accepted，见 [ADR-0008](decisions/ADR-0008-pre-kickoff-decisions.md)） | 已完成（2026-10-22）；M0 只核对仓库中各 ADR 的状态 |
| `rust-toolchain.toml`（Rust 1.99.1）+ `cargo xtask setup-llvm`（LLVM 23.1.3） | 在 Linux 与 Windows 上，`cargo xtask toolchain-check` 输出的版本都等于 [TOOLCHAIN](toolchain.md) 中的值 |
| 仓库初始化（[p0-workplan](design/p0-workplan.md) §7 清单）+ Cargo Workspace 骨架（5 成员） | 清单中的每一项都存在；`cargo build --workspace` 通过；`cargo xtask check-deps` 无违规 |
| LLVM 探针 | `cargo xtask llvm-probe` 生成并运行一个返回 42 的可执行文件，在 Linux 与 Windows（MSVC `link.exe`）上退出码都是 42 |
| CI（GitHub Actions，`ubuntu-24.04` + `windows-2025`） | PR 上运行 fmt、clippy、单元测试、doccheck、cargo-deny，全部阻断式 |
| 诊断登记册接入 | `cargo xtask diag-check`：代码中出现的 `X-E` 码全部已登记 |

**退出门禁**：上述 6 项全部为绿。

### P0 纵向骨架

| 交付物 | 验收 |
|---|---|
| Lexer + 无损 CST + AST | `x dump cst <file>` 往返无损：从 CST 打印出的文本与源文件逐字节一致 |
| 名称解析（单文件）+ 类型检查（P0 子集） | `tests/conformance/p0/` 中 compile-fail 语料全部输出预期诊断码 |
| MIR 构建 + LLVM 代码生成 + 链接 | `x run hello.x` 输出 `Hello, X!`，退出码 0 |
| 符合性 runner + gate manifest | `x test conformance --stage p0 --gate p0` 返回 0；故意破坏 Hello World 后返回非 0 |
| ABI 探针 | 由 C harness 调用 X 导出的 `i32` 加法函数，结果正确 |
| 诊断 JSON v1 | `x check --message-format json` 输出符合 schema v1 |

**退出门禁**：
- p0 gate 为绿；
- lexer/parser fuzz 冒烟 10 分钟无崩溃；
- Linux x86_64 与 Windows x86_64（MSVC）双主机 CI 全绿，且两者的 run-pass 输出一致（除平台规定的 abort 退出码外）。
详细任务见 [p0-workplan](design/p0-workplan.md)。

### P1 Core-CLI 0.1

| 交付物 | 验收 |
|---|---|
| 多文件模块、`use`、可见性 | RULE-MOD-* 语料全部通过 |
| 单包 + Path 依赖 + `x.lock` v1 | 三包 Path Workspace 构建运行；随机目录枚举顺序下 Lockfile 字节一致 |
| 泛型 + Trait（无 Fn 系列）+ 关联类型 | RULE-TRAIT-*（P1 子集）语料通过 |
| 受限借用检查（见 spec 04 §6） | RULE-OWN-*（P1 子集）语料通过；P1 中不存在未经检查的引用 |
| `Result/?`、`panic=abort` | RULE-ERR-* 语料通过 |
| 最小 std：`String/Vec/Box/Rc/Option/Result/HashMap`、`io/fs/env/process` | 参考 CLI #1（`xwc`）在测试语料上与 GNU `wc` 计数一致（比较前把空白归一化） |
| 查询式 Driver（内存缓存） | 二次 `x check` 未改动文件时，零个查询被重算（查询计数器） |
| MIR 解释器 | `x test conformance --oracle` 的解释器结果与 LLVM `-O0/-O2` 三方一致 |
| `x test`（`@test`）、`x fmt` | `x fmt --check` 幂等；`@test` 用例可运行 |

**退出门禁**：
- p1 gate 为绿；
- fuzz 每晚 1 CPU 小时无新增未分诊崩溃；
- Linux x86_64、Windows x86_64、macOS arm64 三主机 CI 为绿。
详细任务见 [p1-workplan](design/p1-workplan.md)。

### P2 Core 0.x 稳定子集（MVP）

| 交付物 | 验收 |
|---|---|
| 完整 NLL 借用、闭包捕获、Fn 系列 | RULE-OWN-*、RULE-OWN-CAPTURE 全量语料通过 |
| `@derive` 闭集、`static`、`const fn` | RULE-TRAIT-DERIVE、RULE-TYPE-STATIC、RULE-EVAL-CONST 通过 |
| 并发：作用域线程、通道、`Mutex/RwLock`、原子 | RULE-CONC-* 通过；并发 stress 测试在 TSan 下零报告 |
| core/alloc/std 分层、`@cfg`、`include_str` | `--no-std` 构建 core/alloc 通过 |
| unsafe/FFI 规范实现 | RULE-UNSAFE-*、RULE-FFI-* 通过；C 库调用示例通过 |
| doc-test、快照测试、`x test --bench` | std 文档示例 100% 可执行 |
| PubGrub 解析原型 + Git 依赖 | 与小图穷举 Oracle 差分一致 |
| 参考 CLI #2（`xgrep`：正则以外的子串/行过滤） | 与参考输出一致；性能达到 [performance](performance.md) 中 P2 列 |
| 易学实验（20 人） | 达到 vision 中 G-SIMPLE 的 P2 试点指标 |

**退出门禁**：
- p2 gate 为绿；
- 规范 01–08 中 phase ≤ P2 的规则全部 Implemented（每条都有语料覆盖）；
- 发布 `0.x preview` 渠道版本（见 [release](release.md)）。

### P3 Alpha 工程化

| 交付物 | 验收 |
|---|---|
| `x lsp` + VS Code 扩展 | 5 万行工作区中，补全 p95 ≤ 200 ms，诊断更新 p95 ≤ 500 ms |
| 落盘增量缓存 | 增量结果与全量结果 100% 一致（差分 CI）；单函数编辑后重新检查 ≤ 300 ms |
| Registry 客户端 + 签名 + SBOM | 篡改摘要演练被阻断（X-E8010） |
| `x debug`（DAP）、DWARF/PDB | VS Code 中可以断点、单步、查看变量 |
| 交叉编译 + wasm32-wasip2 探针 | 在 Linux x86_64 上产出 aarch64-linux 可执行文件并在模拟器中运行 |
| 生态：XUI 原型、x-json、x-http、x-ai-tools 只读 MCP | 各包有独立 CI；不依赖编译器私有 API（依赖检查） |

**退出门禁**：Alpha 发布；1 个外部试点团队用 X 开发并维护一个服务 ≥ 4 周。

### P4 1.0

| 交付物 | 验收 |
|---|---|
| 规范冻结 + 首个稳定 Edition | specs 全部 Stable；Edition 迁移工具可用 |
| Tier 1 × 4 | [platforms](platforms.md) 中 Tier 1 门禁全部为绿 |
| 性能基线 | 达到 [performance](performance.md) 中 1.0 列 |
| 安全 | 外部安全审计无未关闭的 Critical/High；构建达到 SLSA L3 |
| `x publish`、API diff、yank | 发布演练（含撤回、回滚）通过 |
| no_std 子集冻结 | 在一块 Tier 3 裸机目标上运行示例 |

**退出门禁**：1.0 发布评审通过（[release](release.md) §6）。

### P5 1.0 后（按条目独立立项）

每个条目都必须有 RFC 或 ADR、Owner、独立 CI，并按 [platforms](platforms.md) 晋级。主要条目：
- async/await Edition（执行器适配 io_uring/IOCP/kqueue）；
- WASM Tier 2；
- Android/iOS；
- 桌面 XUI；
- 裸机/eBPF；
- Python/JVM/Node 绑定；
- 自举。

### R 研究赛道

每个研究项都必须有：假设、预算（人月）、退出条件、只依赖公开 API 的原型、退出报告。研究失败只归档，不影响主线。

## 4. 语言特性阶段表（唯一来源）

| 特性 | 阶段 | 规范 |
|---|---|---|
| 词法全集、`fn`、`let/var`、`if/while/loop/return/break/continue`、整数/`bool`/`()` | P0 | [01](../specs/language/01-lexical-syntax.md)、[03](../specs/language/03-expressions-patterns.md) |
| `struct`（无方法）、算术溢出检查、`as` 白名单 | P0 | [02](../specs/language/02-types-traits.md) |
| 移动语义（use-after-move 检查） | P0 | [04](../specs/language/04-ownership-borrowing.md) |
| `enum`、`match`、模式解构、`impl` 方法、多文件模块 | P1 | 02、03、[06](../specs/language/06-modules.md) |
| 泛型、Trait、关联类型、孤儿规则、`Copy/Clone/Drop/Eq/Ord/Hash/Default/Display/Debug/Iterator` | P1 | 02 |
| `&`/`&mut` + 受限借用检查、省略规则 | P1 | 04 |
| `Result/Option/?`、`panic=abort`、`main` 返回 `Result` | P1 | [05](../specs/language/05-errors-panics.md) |
| `extern "C"`、`@repr(C)`、`@export`、`unsafe`、原始指针（基础） | P1 | [07](../specs/language/07-unsafe-ffi.md) |
| `for`、`range()`、`@test`、`f"..."` 插值字符串 | P1 | 01、03 |
| 完整 NLL、闭包捕获、`Fn/FnMut/FnOnce` | P2 | 04、02 |
| `@derive`、`static`、`const fn`、`@cfg`、`@tailcall`、`@deprecated`、`@must_use`、`@non_exhaustive` | P2 | 01、02、03 |
| 线程/通道/原子/`Send/Sync` | P2 | [08](../specs/language/08-concurrency.md) |
| unsafe 完整 UB 清单、MIR 解释器 UB 检测 | P2 | 07 |
| `@repr(align)`、全局分配器替换 | P3 | 07 |
| async/await、生成器、`defer`、契约、管道、命名参数、`dyn`、显式生命周期、`panic=unwind` | P5（各自 RFC，经 Edition） | — |

## 5. 阶段命名约束

- 文档、Issue、标签只能使用第 2 节的阶段标识。
- 旧体系中的 G0–G6、R0–R5、GAP 波次 A–D、D0 已废止，映射关系见 [MIGRATION](migration.md)。
- 缺口优先级改用 `Blocker/High/Medium/Low`，不得写成 `P0/P1/P2`。
- [RULE-STAGE-UNIMPL] 如果源码使用了第 4 节中属于后续阶段的特性，当前阶段的编译器必须报 `X-E9001`，并在诊断中写明“该特性计划于 <阶段> 提供”。不得报普通语法错误，也不得静默接受。
