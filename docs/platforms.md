# 平台支持矩阵

> 类型：Platforms｜唯一负责：目标三元组、Tier 定义、晋级门禁、各阶段的平台范围。

## 1. 结论

1. P0 同时支持 `x86_64-unknown-linux-gnu` 与 `x86_64-pc-windows-msvc` 两个主机（[ADR-0008](decisions/ADR-0008-pre-kickoff-decisions.md) K5，主开发机是 Windows）；P1 增加 `aarch64-apple-darwin`；1.0 有 **4 个 Tier 1**。
2. Tier 的含义由门禁决定，不由意愿决定：门禁达不到就降级，绝不“名义支持”。
3. WASM 在 P3 做探针，P5 升为 Tier 2；移动、裸机、eBPF 都在 P5 按条目立项（[ADR-0007](decisions/ADR-0007-language-core-decisions.md) D4）。

## 2. Tier 定义

| Tier | 保证 | 门禁（每个发布版本） |
|---|---|---|
| Tier 1 | 官方二进制；完整 std；每个 PR 都跑 CI；阻断发布 | 全部符合性语料 + std 测试 + `xbench` 冒烟，在原生硬件或认可的 CI Runner 上全绿；调试器可用；安装器已签名 |
| Tier 2 | 官方二进制；std 可以是子集（需列明）；每夜 CI | 符合性语料全绿（允许登记豁免）；回归在 2 周内修复，否则降级 |
| Tier 3 | 可以构建，社区维护；不发布官方二进制 | 每周交叉编译构建 + 冒烟样例 |

## 3. 矩阵

| 目标三元组 | P0 | P1 | P2 | P3 | 1.0（P4） | P5 | 说明 |
|---|---|---|---|---|---|---|---|
| `x86_64-unknown-linux-gnu` | 主机 | 主机 | T1 | T1 | **T1** | T1 | 基准机；CI `ubuntu-24.04` |
| `x86_64-pc-windows-msvc` | 主机 | 主机 | T1 | T1 | **T1** | T1 | MSVC `link.exe`（自动发现），动态 UCRT；CI `windows-2025` |
| `aarch64-apple-darwin` | — | 主机 | T1 | T1 | **T1** | T1 | 需要签名与公证（P4）；CI `macos-15` |
| `aarch64-unknown-linux-gnu` | — | — | T2 | T2 | **T1** | T1 | ARM 服务器 |
| `x86_64-apple-darwin` | — | — | T2 | T2 | T2 | T2 | Intel Mac |
| `x86_64-unknown-linux-musl` | — | — | — | T2 | T2 | T2 | 静态发行 |
| `aarch64-pc-windows-msvc` | — | — | — | T3 | T2 | T2 | |
| `wasm32-wasip2`（具体 WASI 版本在 P3 探针开始时决定，这是唯一保留的决策时点） | — | — | — | 探针 | T3 | T2 | std 子集：没有线程（视 WASI 能力而定） |
| `aarch64-linux-android` | — | — | — | — | T3 | T2 | 以静态库/动态库 + JNI 薄胶水交付 |
| `aarch64-apple-ios` | — | — | — | — | T3 | T2 | 以静态库 + Swift 薄胶水交付 |
| `riscv64gc-unknown-linux-gnu` | — | — | — | T3 | T3 | T2 | |
| `thumbv7em-none-eabihf`（Cortex-M 裸机） | — | — | — | — | T3（`no_std`） | T2 | 只有 core/alloc；`@panic_handler` |
| `riscv32imac-unknown-none-elf` | — | — | — | — | — | T3 | 裸机 |
| `bpfel-unknown-none`（eBPF） | — | — | — | — | — | 研究 → T3 | 受验证器限制的子集，需单独 RFC |

“主机”表示该阶段的开发与 CI 主机，并且只能编译到本机（P0/P1 没有交叉编译）。所有“主机”都是阻断式 CI 项，门禁等同 Tier 1。

## 4. 平台抽象（PAL）

1. 平台差异只能出现在 `x-runtime::pal::{unix, windows, wasi}` 和 `std::os::*` 中。`core`/`alloc` 不得包含平台分支。
2. 条件编译统一用 `@cfg(target_os = "...")` 等谓词（[01](../specs/language/01-lexical-syntax.md) §7.1）。
3. 新增目标的步骤：在 `x-compiler::target` 中添加 `TargetSpec`；实现 PAL 或声明 `no_std`；提供 CI Runner；登记到本表。

## 5. 驱动行为

- [RULE-DRV-TARGET] `--target` 指定的目标不在本表中，或 LLVM 初始化该目标失败时，必须报 `X-E0005`，列出当前阶段受支持的目标，退出码为 2。
- 交叉编译从 P3 开始提供（`x build --target <triple>`），需要用户自备目标 sysroot 或链接器；从 1.0 起，Tier 1 目标之间可直接交叉编译。

## 6. 晋级与降级

- 晋级：提交 Issue，附 4 周连续 CI 绿的记录与 Owner 承诺，由 Platform Lead 批准。
- 降级：Tier 1 连续 2 个发布周期不达门禁，就降为 Tier 2，并写入 CHANGELOG 的 “Platform” 小节。
