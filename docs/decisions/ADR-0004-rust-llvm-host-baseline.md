# ADR-0004：宿主编译器 Rust 与 LLVM 后端基线

## 状态

Proposed

## 日期

2026-08-18

## 背景

工程大纲 §0.2 将「初始编译器使用 Rust」「首个原生后端使用 LLVM」标为 `待决策`，但 P0 纵向切片（Hello World → 可执行文件）与 ABI 探针依赖锁定的宿主工具链。长期不做 ADR 会导致 CI、贡献者环境与 LLVM API 漂移无法审计。

本决策只冻结 **P0–P2 宿主实现基线**，不把 Rust/LLVM 写入 X-Lang 可观察语言语义。

## 决策

### 1. 宿主编译器

- P0–P2 使用 **Rust** 实现 `compiler` / `runtime` / `cli` / `library-core` / `conformance`；
- 通过 `rust-toolchain.toml` 锁定 **stable** 工具链通道与具体版本（首次建仓时写入精确 `channel`/`version`，升级走 PR）；
- Edition：Rust 2021 或建仓时最新稳定 Edition；升级另开 ADR 补丁；
- 自举（用 X-Lang 重写编译器）不早于 1.0 Stable 核心之后，且不阻塞 P0–P4。

### 2. 原生后端

- 首个原生后端为 **LLVM**；
- LLVM 类型与 API **仅**允许出现在 `compiler::codegen` 的 LLVM adapter 内；前端、semantic、IR、driver 门面不得暴露 LLVM 类型（呼应 ADR-0002 / 目录架构）；
- 通过 `llvm-sys` 或官方维护的等价安全绑定接入；具体 crate 在建仓 PR 选定并写入 `Cargo.lock`；
- 主版本升级（如 18→19）必须有：探针测试、至少一个主机 target 的 compile/run 绿、已知破坏项清单。

### 3. 目标与链接

- P0：单一主机 triple（CI 首行 OS/Arch）；
- 链接器：该平台默认链接器 + LLVM 产物；不在 P0 引入自定义链接器框架；
- 额外后端（WASM、快速 Debug、MIR 解释器）按工程大纲双后端路线，**不得**在未过 ADR 前成为默认发布路径。

### 4. 版本文件

建仓时必须存在：

```text
rust-toolchain.toml
Cargo.lock
docs 或 repo 内 TOOLCHAIN.md 一节：Rust 版本、LLVM 版本、探针命令
```

## 替代方案

### 使用 C++/Clang 写编译器

拒绝。与现有大纲、人才假设和 ADR-0002 Workspace 规划冲突；无足够收益。

### 首后端使用 Cranelift / 自研后端

拒绝作为 P0 默认。可作为 P2+ 实验后端，须独立 ADR 与差分测试。

### 不锁定版本，随滚动 latest

拒绝。破坏可复现与 ABI 探针。

## 后果

### 正面

- P0 M0 LLVM 探针可立即开工；
- 工程大纲 §0.2 两项由「待决策」升为「有 ADR 的 Proposed 基线」；
- 前端与 LLVM 解耦规则可审查。

### 负面 / 风险

- LLVM 绑定与 Windows 构建成本高——用 M0 探针尽早暴露；
- 锁定版本带来升级滞后——接受，优先可复现。

## 关联

- [p0-vertical-slice.md](../design/p0-vertical-slice.md) M0
- `GAP-COMP-01`、`GAP-COMP-02`
- 工程大纲 §2.1、§6.1
