# ADR-0001 宿主语言 Rust 与 LLVM 后端

> 状态：Accepted｜版本：2.1.0｜负责人：Compiler Lead｜最后更新：2026-10-22
> 类型：ADR｜取代：旧 ADR-0004（内容保留并修订）

## 背景

需要一个能尽快产出原生代码、覆盖三大桌面 OS，并且之后能扩展到 WASM、移动和裸机的实现路线（原始需求 1.txt、2.txt）。

## 决策

1. 编译器、运行时 xrt、CLI 都用 **Rust stable** 实现。版本通过 `rust-toolchain.toml` 锁定，并在 [TOOLCHAIN](../../TOOLCHAIN.md) 中登记。
2. 后端使用 **LLVM**，通过 `llvm-sys` 绑定，外加一层薄的安全封装。LLVM 类型只能出现在 `x-compiler::codegen::llvm` 中。
3. 前端与后端之间的契约是 `trait Backend { fn compile(&self, mir: &MonoProgram, target: &TargetSpec) -> Result<ObjectFile, CodegenError>; }`。
4. P0 同时支持两个主机与目标：`x86_64-unknown-linux-gnu` 与 `x86_64-pc-windows-msvc`，两者都是 CI 阻断项（[ADR-0008](ADR-0008-pre-kickoff-decisions.md) K5）。P1 增加 `aarch64-apple-darwin`。
5. 链接：Linux/macOS 调用系统 C 编译器驱动（`cc`）；Windows 调用 MSVC `link.exe`，通过 `cc` crate 的 `windows_registry::find_tool` 自动发现，CRT 使用动态 UCRT（`/MD`，与 Rust MSVC 目标默认一致）。1.0 **不随附** lld；用户可以用 `--linker <路径>` 覆盖，例如指定 `lld-link`。
6. 第二后端（Cranelift，用于加快 Debug 构建）只有在 P2 之后，并且同时满足“差分测试一致”和“编译时间收益 ≥ 30%”时，才能经新 ADR 立项。

## 备选方案

| 方案 | 不选的原因 |
|---|---|
| C++ 宿主 | 内存安全和开发效率都不如 Rust，生态工具（cargo、fuzz）也较弱 |
| 自研后端 | 成本极高，目标覆盖面差 |
| 只用 Cranelift | 生成代码的优化水平和目标覆盖面都不足以支撑 1.0 的性能目标 |
| 编译到 C | 调试信息、ABI 和优化控制都较弱，只能作为备选 |

## 后果

- 构建依赖 LLVM 开发库。CI 必须缓存 LLVM，或使用预编译版本。
- LLVM 升级主版本必须走 ADR，并通过全部差分测试与基准测试。
- 版本已经联网核实并锁定为 Rust 1.99.1、LLVM 23.1.3、`llvm-sys` 231.0.1，见 [TOOLCHAIN](../../TOOLCHAIN.md)。旧文档中的“Rust 1.97.1、LLVM 22.1.8”作废：两者都是真实存在的版本，但已经不是最新的稳定版本。
- Windows 开发者必须使用 `clang+llvm-*-x86_64-pc-windows-msvc` 归档包，因为 `.msi` 安装器里没有 `llvm-config` 和开发库；`cargo xtask setup-llvm` 会自动完成下载与校验。
