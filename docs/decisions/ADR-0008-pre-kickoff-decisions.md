# ADR-0008 开工前决策汇总

> 类型：ADR｜新增（v2.1）｜决策原则：用户授权“按最优最稳实现方案”拍板，即优先选业界成熟、可回退、风险最低的做法。本 ADR 关闭 v2.0 遗留的全部待决事项。

## 1. 结论

12 项决定（K1–K12）立即生效，各项已回写到下表所列文档。今后只有一项“需要未来数据才能定”的事项：`wasm32` 目标的具体 WASI 版本，在 P3 WASI 探针开始时决定，见 [platforms](../platforms.md)。

## 2. 决定

| # | 决定 | 理由（一句话） | 回写到 |
|---|---|---|---|
| K1 | **维持 ADR-0007 全部 26 项取舍**，不做调整；ADR-0007 转为 Accepted | 每项都有成熟先例（Rust/Swift/Zig），且已登记可推翻条件；在没有实验数据时改动的风险高于维持 | [ADR-0007](ADR-0007-language-core-decisions.md) |
| K2 | **维持**新增关键字 `static`、8 个保留字、位运算优先级高于比较且比较不可结合（D10/D14/D26） | 现在还没有用户代码，这时做破坏性调整的成本为零；1.0 之后再改就必须换 Edition | [01](../../specs/language/01-lexical-syntax.md) |
| K3 | **1.0 只提供 `panic=abort`**；`unwind` 不进入 1.0，1.0 之后（P5）可以经 RFC + Edition 评估 | 运行时、FFI 边界、代码体积与测试矩阵都最简单（参照 Rust 嵌入式与 Zig 的做法）；`JoinHandle::join` 保留 `Result` 返回类型，以后增加 unwind 不会破坏 API | [05](../../specs/language/05-errors-panics.md)、[08](../../specs/language/08-concurrency.md)、[roadmap](../roadmap.md) |
| K4 | **第三方库**：CST 采用 `rowan` 0.17.x（P0 起）；查询框架采用 `salsa` 0.28.x（≥ 0.28.5，P1 起）；两者都只能经内部门面（`syntax::tree`、`driver::db`）使用；Cargo.lock 入库，关键依赖用 `=` 精确锁定；`cargo-deny` 与 `cargo-audit` 进 CI | 两者都是 rust-analyzer 在生产中验证过的方案；门面隔离使替换成本可控；0.28.5 修复了 GHSA-xc3w-55vh-cw3w 中的 use-after-free 问题 | [ADR-0005](ADR-0005-query-compiler-and-lossless-cst.md)、[TOOLCHAIN](../toolchain.md)、[repository](../repository.md) |
| K5 | **P0 同时支持两个主机/目标**：`x86_64-unknown-linux-gnu` 与 `x86_64-pc-windows-msvc`，两者在 CI 中都是阻断项；macOS arm64 在 P1 加入 | 用户的主开发机是 Windows，如果 P0 只支持 Linux，开发者就无法在本机运行端到端测试；P0 中 Windows 部分的增量只有链接器发现与 xrt 的写入/退出，属于可控工作 | [ADR-0001](ADR-0001-host-and-backend.md)、[platforms](../platforms.md)、[roadmap](../roadmap.md)、[p0-workplan](../design/p0-workplan.md) |
| K6 | **工具链锁定**：Rust **1.99.1**、LLVM **23.1.3**（23.1.x 线）、`llvm-sys` **231.0.1** | 这些都是 2026-10-22 联网核实的最新稳定版本；LLVM 选 23.1.3 而不选 23.1.4，是因为 23.1.4 的官方二进制尚未发布，而 23.1.3 已提供 Linux、Windows、macOS 三个平台的官方包 | [TOOLCHAIN](../toolchain.md) |
| K7 | **许可证**：`Apache-2.0 OR MIT` 双许可（编译器、运行时、std、官方生态包都适用），同时使用 DCO | 这是 Rust 生态的惯例；Apache-2.0 带专利授权，MIT 兼容性最好；`rowan`、`salsa`、`llvm-sys`（MIT）以及 LLVM（Apache-2.0 WITH LLVM-exception）都与之兼容 | [GOVERNANCE](../governance.md) |
| K8 | **CI**：GitHub Actions，锁定镜像标签 `ubuntu-24.04`、`windows-2025`、`macos-15`（arm64）；不使用 `*-latest` | 托管 Runner 覆盖全部 Tier 1 主机；锁定标签可以避免镜像漂移（`macos-latest`、`ubuntu-latest` 在 2026 年都发生过迁移） | [release](../release.md)、[p0-workplan](../design/p0-workplan.md) §7 |
| K9 | **签名与供应链**：发布工件使用 Sigstore `cosign` 无密钥签名（GitHub OIDC），加上 GitHub Artifact Attestations（SLSA Provenance）；SBOM 采用 CycloneDX JSON；P4 起增加 Windows Authenticode 与 Apple 公证 | 无密钥签名不需要保管长期私钥，泄露风险最低；这些都是 OpenSSF 推荐的成熟做法 | [release](../release.md) |
| K10 | **Edition 与 LTS**：1.0 之前只有 `"preview"`；首个稳定 Edition 以 1.0 发布的年份命名（例如 `"2028"`），之后两个 Edition 至少间隔 3 年；1.0 之前不提供 LTS；1.0 起每年指定 1 个 stable 版本为 LTS，提供 12 个月的安全与严重缺陷修复 | 与 Rust 的 Edition 节奏一致；LTS 只承诺安全修复，资源压力有上限 | [release](../release.md)、[ADR-0007](ADR-0007-language-core-decisions.md) D25 |
| K11 | **负责人**：所有文档的负责人字段统一写成角色名（如 `Compiler Lead`）；在人员到位之前，由 Project Lead 兼任所有角色 | 角色名稳定，不会因为人员变动而改文档；“兼任”保证每份文档在任何时候都有人负责 | 全部文档头部、[GOVERNANCE](../governance.md) §1 |
| K12 | **人力与时长**：维持 [roadmap](../roadmap.md) 中【推断】的规模估计；在 P0 结束时按实测速度校准一次，校准结果写进 roadmap | 没有历史数据时，任何改动都只是另一种猜测；需要数据的事项要定在固定的时点做决定 | [roadmap](../roadmap.md) |

## 3. 文档状态变更

- Accepted：ADR-0001 至 0008；specs/language 01–08、std-core、packages；README、GOVERNANCE、TOOLCHAIN、vision、roadmap、architecture、repository、compiler、P0/P1 工作分解、testing、performance、platforms、release、risks；两份登记册。
- 保持 Proposed：[ecosystem](../ecosystem.md)。XUI 与 x-json 的接口按设计在 P3 原型通过后才冻结，这属于阶段门禁，不是待决事项。

## 4. 可推翻条件

- K3：1.0 之后，如果有 ≥ 3 个生产用户报告“abort 无法满足服务端隔离需求”，就启动 unwind RFC。
- K4：如果 `salsa` 在 P1 探针中无法覆盖 [compiler](../design/compiler.md) §3 的查询清单，或连续 2 个小版本出现阻断性回归，就替换为门面后面的自研薄层（ADR-0005 的回退方案）。
- K6：LLVM 主版本只能经新 ADR 升级；评估下一个主版本的时间点是它的 `x.1.2` 发布之后。
