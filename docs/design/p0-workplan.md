# P0 工作分解：纵向骨架

> 类型：Workplan｜唯一负责：M0 与 P0 的任务、顺序、DoD、样例。阶段目标与退出门禁以 [roadmap](../roadmap.md) 为准。

## 1. 结论

- 目标：单个 `.x` 文件经完整管线（CST→AST→HIR→类型检查→MIR→移动检查→LLVM→链接）生成可执行文件，在 **Linux x86_64 与 Windows x86_64（MSVC）双主机**上行为一致（[ADR-0008](../decisions/ADR-0008-pre-kickoff-decisions.md) K5）。
- 开工前的决策已经全部闭环（ADR-0001～0008 Accepted），工具链版本已锁定（[TOOLCHAIN](../toolchain.md)）。M0 第 1 天就可以按 §7 初始化仓库。
- 关键路径：M0 → T01 Lexer → T02 Parser/CST → T04 HIR/解析 → T05 类型检查 → T06 MIR → T08 代码生成 → T09 链接/xrt（Linux + Windows）→ T11 gate。
- 规模【推断】：2–3 人，M0 4 周 + P0 12 周（Windows 部分约 +1 周，已计入）。在 P0 结束时按实测速度校准（K12）。

## 2. P0 语言子集（以 [roadmap](../roadmap.md) §4 为准）

- Item：`fn`、`struct`（无方法）、`const`（字面量初始化）。
- 语句与表达式：`let/var`、赋值、`if/while/loop/break/continue/return`、块表达式、函数调用、字段访问、算术/比较/逻辑/位运算、`as`。
- 类型：`i8…i64 u8…u64 isize usize bool ()`、`&str`（仅作为字面量类型）、`never`、用户 struct。`i128/u128/f32/f64/char` 在词法与类型层被接受，代码生成留到 P1，P0 阶段报 `X-E9001`。
- 内建（P0 桩）：
  - `print(s: &str)`、`println(s: &str)`、`eprintln(s: &str)`：只接受 `&str`；
  - `panic(msg: &str) -> never`；
  - `std::process::exit(code: i32) -> never`：P0 中由解析器特判此路径，P1 起由真正的 std 提供。
- 检查：类型检查、溢出/除零检查、移动后使用（`X-E4001`）、`let` 重新赋值（`X-E4008`）。
- 其他语法（`enum`、`match`、`impl`、`&`、泛型等）可以被解析，但必须报 `X-E9001`。排除项报 `X-E9002`。

## 3. M0 任务（4 周）

| ID | 任务 | 依赖 | DoD |
|---|---|---|---|
| M0-01 | 按 §7 初始化仓库：5 个成员 + 根目录文件 | — | §7.1 清单的每一项都存在；`cargo build --workspace` 在 Linux 与 Windows 上都通过 |
| M0-02 | `xtask setup-llvm`、`doctor`、`toolchain-check`（按 [TOOLCHAIN](../toolchain.md) §2 下载 LLVM 23.1.3 并校验 SHA-256） | M0-01 | 在全新的 Windows 机器（只装了 VS Build Tools 与 rustup）上，执行 `cargo xtask setup-llvm` 后 `cargo xtask doctor` 全绿 |
| M0-03 | `xtask check-deps`（源码扫描 `use`，以及 `llvm_sys`、`rowan`、`salsa` 的引用位置） | M0-01 | 故意制造的违规样例使 CI 失败 |
| M0-04 | `xtask llvm-probe`：用 llvm-sys 生成 `main` 返回 42，并完成链接 | M0-02 | 在 `ubuntu-24.04` 与 `windows-2025` 两个 CI 上运行，退出码都是 42 |
| M0-05 | CI：fmt、clippy `-D warnings`、test、doccheck、cargo-deny（§7.3） | M0-01 | 5 个检查都阻断合并；LLVM 缓存命中后，单次 PR 运行 ≤ 15 分钟 |
| M0-06 | `xtask diag-check`：扫描源码中的 `X-E\d{4}`，与 registry.yaml 比对 | M0-01 | 未登记的码使 CI 失败 |
| M0-07 | 治理落地：CODEOWNERS（所有角色暂由 Project Lead 兼任）、分支保护、DCO 检查、`AGENTS.md` | M0-01 | `main` 禁止直接推送；未签署 DCO 的 PR 被阻断 |

## 4. P0 任务

| ID | 任务 | 依赖 | 周【推断】 | DoD |
|---|---|---|---|---|
| T01 | Lexer：Token + trivia、全部字面量、`X-E1001…1008/1015` | M0 | 2 | 词法单测 ≥ 150 条；每个 X-E10xx 至少有 1 条 compile-fail 语料 |
| T02 | Parser → 无损 CST，Pratt 表达式解析，错误恢复 | T01 | 3 | `x dump cst` 往返逐字节一致；优先级表的每一行都有快照；一个文件中有 3 处语法错误时报告 3 条诊断 |
| T03 | AST 类型化视图 + `x dump ast` | T02 | 1 | AST 快照覆盖 P0 子集的全部语法节点 |
| T04 | HIR lowering + 单文件名称解析（`X-E2004/2010`）+ `X-E9001/9002` 阶段门禁 | T03 | 1.5 | RULE-MOD-NS、RULE-MOD-UNRESOLVED、RULE-STAGE-* 语料通过 |
| T05 | 类型检查（P0 子集）：字面量推断、`X-E3001…3010` | T04 | 2.5 | RULE-TYPE-*、RULE-EVAL-CAST（P0 部分）语料通过 |
| T06 | MIR 构建 + 校验器 + `x dump mir` | T05 | 2 | 每个 run-pass 样例的 MIR 快照稳定；校验器对全部语料零报错 |
| T07 | 移动检查（局部变量、struct 字段整体移动）`X-E4001/4008` | T06 | 1 | RULE-OWN-USEMOVED、RULE-OWN-LETASSIGN 语料通过 |
| T08 | LLVM 代码生成（`Backend` trait、`-O0/-O2`、`-g` 行号表；Linux 输出 ELF，Windows 输出 COFF + PDB） | T06 | 2.5 | run-pass 语料在 `-O0` 与 `-O2` 下 stdout/退出码一致；双主机输出一致 |
| T09 | xrt 最小运行时（入口、write、panic、exit）：`pal/unix.rs` 与 `pal/windows.rs`（`WriteConsoleW`/`WriteFile`、`ExitProcess`、abort）；链接器调用：Linux 用 `cc`，Windows 用 `link.exe` 并通过 `cc::windows_registry::find_tool` 发现（`X-E0004`） | T08 | 2 | 双主机上 `x run hello.x` 都输出 `Hello, X!`；panic 样例退出类别正确（Unix 为 SIGABRT，Windows 为退出码 3）；Windows 控制台中中文 panic 消息不乱码 |
| T10 | Driver/CLI：`x check/build/run/dump`，`X-E0001…0005`，JSON 诊断 v1 | T02 | 并行 2 | RULE-DRV-* 语料通过；JSON 输出符合 schema |
| T11 | `x-conformance` runner + `gates/p0.toml` + `x test conformance` | T02 | 并行 2 | 破坏 Hello 后 gate 失败；报告按 Rule ID 汇总 |
| T12 | ABI 探针：C harness 调用 `@export("x_add") pub extern "C" fn x_add(a: i32, b: i32) -> i32`；harness 由 `cc` crate 编译（Windows 上是 `cl.exe`） | T09 | 0.5 | 双主机上 C 都打印 `5`。注意：P0 仅为此探针特许 `extern "C"` 与 `@export`，完整 FFI 在 P1 |
| T13 | fuzz 冒烟：lexer/parser 用 `cargo fuzz` | T02 | 0.5 | Linux CI 运行 10 分钟无崩溃（fuzz 只在 Linux 上运行） |

顺序：T01→T02→（T03、T10、T11 并行）→T04→T05→T06→（T07、T08 并行）→T09→T12→gate。

## 5. 样例与期望输出

### 5.1 Hello（run-pass）

```x
// tests/conformance/p0/run-pass/hello.x
fn main() {
    print("Hello, X!\n");
}
```

期望：stdout 为 `Hello, X!` 加换行，退出码 0。

### 5.2 算术与控制流（run-pass，用退出码验证）

```x
// tests/conformance/p0/run-pass/fib.x
fn fib(n: i64) -> i64 {
    var a: i64 = 0;
    var b: i64 = 1;
    var i: i64 = 0;
    while (i < n) {
        let t = a + b;
        a = b;
        b = t;
        i = i + 1;
    }
    a
}

fn main() {
    if (fib(10) == 55) {
        println("ok");
    } else {
        std::process::exit(1);
    }
}
```

期望：stdout 为 `ok`，退出码 0。

### 5.3 溢出 panic（run-fail）

```x
// tests/conformance/p0/run-fail/overflow.x
fn main() {
    let x: u8 = 255;
    let y = x + 1;
    print("unreachable\n");
}
```

期望：stdout 为空；stderr 包含 `panic at tests/conformance/p0/run-fail/overflow.x:3:13: attempt to add with overflow`（两个平台上路径都用 `/`）；退出类别为 abort（runner 统一归类：Unix 上是 SIGABRT，Windows 上是退出码 3）。

### 5.4 移动后使用（compile-fail）

```x
// tests/conformance/p0/compile-fail/use-moved.x
struct Buf { len: usize }

fn take(b: Buf) -> usize { b.len }

fn main() {
    let b = Buf { len: 3 };
    let n = take(b);
    let m = take(b); //~ ERROR X-E4001
}
```

期望诊断：

```text
error[X-E4001]: 使用了已移动的值 `b`
 --> tests/conformance/p0/compile-fail/use-moved.x:8:18
  |
7 |     let n = take(b);
  |                  - 值在此处被移动
8 |     let m = take(b);
  |                  ^ 移动后在此处使用
```

### 5.5 阶段门禁（compile-fail）

```x
fn main() {
    defer print("x"); //~ ERROR X-E9002
}
```

期望：`error[X-E9002]: `defer` 不属于 X 1.0；请使用 RAII Guard（std::guard::on_exit）`。

## 6. 语料格式

见 [testing](../testing.md) §3。每个样例使用 `//~ ERROR X-Exxxx` 标注期望诊断，用 `// RULE: RULE-…` 标注覆盖的规则（runner 也会从诊断码反查规则）。

## 7. 仓库初始化清单（M0-01，可直接执行）

### 7.1 文件清单

| 路径 | 内容要求 |
|---|---|
| `Cargo.toml` | Workspace，包含 5 个成员与统一依赖版本（§7.2） |
| `Cargo.lock` | 入库 |
| `rust-toolchain.toml` | 锁定 Rust 1.99.1（§7.2） |
| `compiler/`、`runtime/`、`cli/`、`conformance/`、`xtask/` | 各含 `Cargo.toml` 与 `src/lib.rs` 或 `src/main.rs`。crate 名分别为 `x-compiler`、`x-runtime`（`crate-type = ["staticlib"]`，`lib.name = "xrt"`）、`x-cli`（`[[bin]] name = "x"`）、`x-conformance`、`xtask`；模块目录按 [repository](../repository.md) §2 建空模块（每个空模块都有 `//! 职责` 文档注释） |
| `LICENSE-APACHE`、`LICENSE-MIT` | Apache License 2.0 与 MIT 的官方原文；README 中写明 “Licensed under either of Apache-2.0 or MIT at your option” |
| `.editorconfig` | 见 §7.2 |
| `.gitattributes` | 见 §7.2；保证 CST 往返和快照测试在 Windows 上逐字节一致 |
| `.gitignore` | `/target`、`/.x-dev`、`.cargo/config.local.toml`、`*.pdb`、`target/x-ice-*` |
| `rustfmt.toml` | `edition = "2024"`、`max_width = 100`、`newline_style = "Unix"` |
| `clippy.toml` | `msrv = "1.99.1"` |
| `deny.toml` | 许可证白名单：`Apache-2.0`、`MIT`、`BSD-2-Clause`、`BSD-3-Clause`、`ISC`、`Unicode-3.0`、`Apache-2.0 WITH LLVM-exception`、`Zlib`；`advisories` 设为 deny；禁止 git 依赖与通配版本 |
| `.cargo/config.toml` | `[alias] xtask = "run -p xtask --"`；`[env]` 从不入库的 `config.local.toml` 读取 `LLVM_SYS_231_PREFIX`（由 `xtask setup-llvm` 生成） |
| `.github/workflows/ci.yml` | 见 §7.3 |
| `.github/workflows/nightly.yml` | M0 只放一个占位任务：每夜构建 nightly 工件；fuzz 与 bench 在 P0/P2 补充 |
| `.github/dependabot.yml` | `cargo` 与 `github-actions` 两个生态，每周更新；`rowan`、`salsa`、`llvm-sys` 设为 ignore（由人工升级，见 TOOLCHAIN §4） |
| `.github/CODEOWNERS` | `/compiler/ @project-lead`（所有角色暂由 Project Lead 兼任，到位后按角色替换） |
| `.github/pull_request_template.md` | 动机、方案、测试证据、影响的 Rule ID、`ai-assisted` 勾选项、DCO 提示 |
| `README.md`、`CONTRIBUTING.md` | 构建步骤（链接到 §8）、DCO、Conventional Commits |
| `SECURITY.md` | 漏洞报告渠道（GitHub Private Vulnerability Reporting）、90 天披露期 |
| `AGENTS.md` | [GOVERNANCE](../governance.md) §6 的一页摘要，以及“先读后改、跑 `cargo test` 与 doccheck、禁止修改 TOOLCHAIN 锁定版本” |
| `docs/` | 本文档体系（x-docs-v2 原样拷入）；`python3 docs/tools/doccheck.py --check` 进 CI |
| `tests/conformance/p0/`、`gates/p0.toml` | 先放 §5 的 5 个样例；开始时 gate 允许失败（`allow_fail = true`），T11 完成后去掉 |

### 7.2 关键文件内容

```toml
# Cargo.toml
[workspace]
resolver = "3"
members = ["compiler", "runtime", "cli", "conformance", "xtask"]

[workspace.package]
version = "0.0.0"
edition = "2024"
rust-version = "1.99.1"
license = "Apache-2.0 OR MIT"

[workspace.dependencies]
llvm-sys = { version = "=231.0.1", features = ["prefer-static"] }
rowan = "=0.17.0"
# salsa = "=0.28.5"   # P1 启用（ADR-0005）
cc = "1"             # x-cli 用于发现 MSVC link.exe；xtask 用于编译 C harness

[workspace.lints.rust]
unsafe_op_in_unsafe_fn = "deny"
missing_docs = "warn"

[workspace.lints.clippy]
all = { level = "deny", priority = -1 }

[profile.xrt]               # 只用于构建 x-runtime：cargo build -p x-runtime --profile xrt
inherits = "release"
panic = "abort"
```

```toml
# rust-toolchain.toml
[toolchain]
channel = "1.99.1"
components = ["rustfmt", "clippy", "llvm-tools"]
profile = "minimal"
```

```ini
# .editorconfig
root = true
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4
[*.{yml,yaml,toml,json}]
indent_size = 2
[*.md]
trim_trailing_whitespace = false
```

```text
# .gitattributes
* text=auto eol=lf
*.x text eol=lf
*.snap text eol=lf
tests/conformance/**/crlf-*.x -text   # 专门测试 CRLF 输入的语料：git 不做任何转换
*.png binary
```

说明：`x-compiler` 的 ICE 捕获依赖 `catch_unwind`，所以除 `x-runtime` 以外，所有 crate 都使用默认的 `panic = "unwind"`。`xtask` 负责用 `--profile xrt` 单独构建 xrt。

### 7.3 CI 工作流样例（`.github/workflows/ci.yml`）

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  docs:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@<commit-sha>   # 所有 Action 均按 commit SHA 锁定，由 Dependabot 更新
      - run: python3 docs/tools/doccheck.py --check

  build-test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-24.04, windows-2025]      # P1 增加 macos-15
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@<commit-sha>
      - name: Toolchain（由 rust-toolchain.toml 决定版本）
        run: rustup show
      - uses: actions/cache@<commit-sha>
        with:
          path: ~/.x-dev/llvm-23.1.3
          key: llvm-23.1.3-${{ runner.os }}
      - name: LLVM（下载并校验 SHA-256，写入 GITHUB_ENV）
        run: cargo xtask setup-llvm --ci
      - run: cargo xtask doctor
      - run: cargo fmt --all --check
      - run: cargo clippy --workspace --all-targets
      - run: cargo test --workspace
      - run: cargo xtask check-deps
      - run: cargo xtask diag-check
      - run: cargo xtask llvm-probe            # 期望退出码 42
      - run: cargo run -p x-cli -- test conformance --gate p0   # T11 完成后成为阻断项

  deny:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@<commit-sha>
      - uses: EmbarkStudios/cargo-deny-action@<commit-sha>
```

`<commit-sha>` 由 M0-05 在首次提交时填入当时最新发布版本对应的 commit SHA。这些 SHA 是外部事实，不能在文档中预先编造。

## 8. Windows 开发环境（本机 `D:\IdeaProjects\project\x`）

在 PowerShell 中按顺序执行：

```powershell
# 1. MSVC 与 Windows SDK（也可以在 VS Installer 中勾选“使用 C++ 的桌面开发”；VS 2026 Build Tools 同样可用）
winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive"
# 2. rustup（进入仓库后，会按 rust-toolchain.toml 自动安装 1.99.1）
winget install --id Rustlang.Rustup
# 3. Git 设置：换行交给 .gitattributes 处理；打开长路径支持
git config --global core.autocrlf false
git config --global core.longpaths true
# 4. 克隆并初始化
git clone <仓库地址> D:\IdeaProjects\project\x
cd D:\IdeaProjects\project\x
cargo xtask setup-llvm --dir D:\toolchains\llvm-23.1.3   # 下载 clang+llvm-23.1.3-x86_64-pc-windows-msvc 并校验
cargo xtask doctor                                        # 检查 link.exe、SDK、LLVM、Rust 版本
cargo test --workspace
cargo xtask llvm-probe                                    # 期望输出：probe exit code = 42
```

建议：
- 把仓库与 `target` 目录放在 Dev Drive 上，或者在 Defender 中排除它们，可以明显缩短构建时间；
- IDE 可以用 IntelliJ IDEA 或 RustRover 打开仓库根目录；
- 不需要 WSL。WSL 只是可选的第二个 Linux 主机，用于本地复现 Linux CI。
