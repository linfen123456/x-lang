# 宿主工具链锁定

> 状态：Accepted｜版本：2.1.0｜负责人：Release Lead｜最后更新：2026-10-22
> 类型：Governance｜唯一负责：宿主工具链与关键第三方依赖的版本。决策依据：[ADR-0008](docs/decisions/ADR-0008-pre-kickoff-decisions.md) K4、K6。

## 1. 版本表（2026-10-22 联网核实）

| 组件 | 锁定版本 | 核实来源 | 备注 |
|---|---|---|---|
| Rust（stable） | **1.99.1**（2026-10-15） | Rust 发布公告列表 https://blog.rust-lang.org/releases/ ；https://blog.rust-lang.org/2026/10/15/Rust-1.99.1/ | 写入 `rust-toolchain.toml`，组件 `rustfmt`、`clippy`、`llvm-tools` |
| LLVM | **23.1.3**（2026-10-06，23.1.x 线） | https://llvm.org/ 发布日程；https://github.com/llvm/llvm-project/releases/tag/llvmorg-23.1.3 （带 Linux X64/ARM64、macOS ARM64、Windows x64 官方包） | 23.1.4 于 2026-10-20 发布，但公告说明“官方二进制稍后提供”；官方包齐备后可以经普通 PR 升级到 23.1.x 的更新补丁版本 |
| `llvm-sys` | **=231.0.1**（2026-10-09） | https://crates.io/crates/llvm-sys | 版本号 231 对应 LLVM 23.1.x；启用 `prefer-static` |
| `rowan` | **=0.17.0**（2026-08-02） | https://crates.io/crates/rowan | 不使用 0.18 alpha |
| `salsa` | **=0.28.5**（2026-09-24，P1 起） | https://crates.io/crates/salsa ；https://github.com/salsa-rs/salsa/releases | 修复了 GHSA-xc3w-55vh-cw3w，禁止低于 0.28.5 |
| CI 镜像 | `ubuntu-24.04`、`windows-2025`、`macos-15`（arm64） | https://docs.github.com/en/actions/reference/runners/github-hosted-runners | `windows-2025` 自 2026-06 起默认使用 Visual Studio 2026 |
| Python（仅用于文档工具） | ≥ 3.10，只用标准库 | 本仓库 `tools/doccheck.py` | — |

## 2. 各主机的 LLVM 获取方式（`cargo xtask setup-llvm` 自动完成并校验）

| 主机 | 包 | 说明 |
|---|---|---|
| Linux x86_64 | `LLVM-23.1.3-Linux-X64.tar.xz` | 解压到 `~/.x-dev/llvm-23.1.3` |
| Windows x86_64 | `clang+llvm-23.1.3-x86_64-pc-windows-msvc.tar.xz` | **必须用这个包，不能用 `.msi` 安装器**：只有前者带开发库与 `llvm-config`。例如解压到 `D:\toolchains\llvm-23.1.3` |
| macOS arm64（P1） | `LLVM-23.1.3-macOS-ARM64.tar.xz` | — |

校验方式：
- 用 `.sig` 文件做 GPG 校验，或运行 `gh attestation verify --repo llvm/llvm-project <包>`；
- `xtask` 中内置每个包的 SHA-256，下载后必须比对。

然后设置环境变量 `LLVM_SYS_231_PREFIX=<解压目录>`，`xtask` 会写入 `.cargo/config.toml` 的本地覆盖文件（该文件不入库）。

## 3. 其他主机依赖

| 主机 | 依赖 |
|---|---|
| Windows | Visual Studio Build Tools 2022 或 2026，包含“使用 C++ 的桌面开发”工作负载（MSVC 工具集与 Windows SDK）。`link.exe` 由 `cc` crate 的 `windows_registry::find_tool` 自动发现，不要求开发者手动打开 Developer Prompt |
| Linux | 系统 C 编译器驱动 `cc`（gcc 或 clang）与 glibc 开发包 |
| macOS（P1） | Xcode Command Line Tools |

具体的 MSVC、gcc、Xcode 版本不锁定，由 `cargo xtask doctor` 输出并记录在 CI 日志中。

## 4. 升级规则

1. Rust：每季度评估一次，升级到当时最新的 stable 补丁版本；升级走普通 PR，要求全部 CI 通过；`rust-toolchain.toml` 必须与本表一致（由 `cargo xtask toolchain-check` 校验）。
2. LLVM：同一主版本内的补丁升级走普通 PR，要求差分测试与基准测试全部通过；主版本升级必须走 ADR（[ADR-0001](docs/decisions/ADR-0001-host-and-backend.md)），且只能在新主版本的 `x.1.2` 发布之后进行。
3. `rowan`、`salsa`、`llvm-sys` 使用 `=` 精确版本，升级必须单独提交 PR；其他依赖由 Cargo.lock 锁定，Dependabot 每周提交更新 PR。
4. 安全公告（RUSTSEC 或 GHSA）涉及本表中的组件时，必须在 7 天内升级。
