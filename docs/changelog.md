# 变更日志

> 类型：Log｜格式：Keep a Changelog；小节 Added / Changed / Deprecated / Removed / Fixed / Security / Platform。

## [Unreleased]

### Changed
- 将治理、工具链、迁移说明和变更日志集中到 `docs/`；新增文档架构索引，补全项目 README 的目录、内容归属和检查命令。
- 移除当前文档页头的版本、状态标记及 README 中的状态词表；登记册生成器和文档检查同步适配。
- 将 v2.1.0 文档提升到 main 分支根目录；旧文档与原始需求按 [迁移说明](migration.md) 仅保留在 `v1.0.0` 历史分支，`main` 不再保存历史文档及导入包。

### Fixed
- `doccheck` 跳过历史归档及 Git 元数据，统一生成跨平台的 `/` 链接，避免 Windows 检查误报生成物过期。

## [2.1.0] 开工前决策闭环 — 2026-10-22

### Added
- [ADR-0008](decisions/ADR-0008-pre-kickoff-decisions.md)：开工前的 12 项决定（K1–K12），v2.0 遗留的待决事项全部关闭。
- P0 工作分解新增 §7 仓库初始化清单（Cargo workspace、`rust-toolchain.toml`、`.editorconfig`、`.gitattributes`、`deny.toml`、CI 工作流样例、许可证等）和 §8 Windows 开发环境步骤。
- 风险 R15（Windows 开发环境配置）、R16（第三方 crate 风险）。
- doccheck 新增检查：文档中不得残留“待用户决定 / 待指定 / 开放问题”这类未关闭项。

### Changed
- 工具链锁定为 Rust 1.99.1、LLVM 23.1.3、`llvm-sys` 231.0.1、`rowan` 0.17.0、`salsa` 0.28.5（2026-10-22 联网核实），取代旧文档中的 Rust 1.97.1 / LLVM 22.1.8。
- P0 改为 Linux x86_64 与 Windows x86_64（MSVC）双主机；macOS arm64 仍在 P1 加入。
- panic 策略：1.0 只有 `abort`，unwind 移到 1.0 之后；`X-E5003` 的阶段改为 P5；P3 交付物中删除“unwind 决策”。
- CI 确定为 GitHub Actions，锁定 Runner 标签；签名确定为 cosign 无密钥签名 + GitHub Attestations；SBOM 确定为 CycloneDX；这三项都从 P2 preview 开始。
- Edition 命名与 LTS 策略已定；许可证为 Apache-2.0 OR MIT。
- 状态：ADR-0001～0008、specs 01–08、std-core、packages 以及核心 docs 改为 Accepted；ecosystem 保持 Proposed（按阶段门禁在 P3 冻结）。
- 负责人字段统一为角色名，版本号升到 2.1.0。

## [2.0.0-draft] 文档体系 v2 — 2026-10-22

### Added
- 全新的 v2 文档体系：README 索引、vision、roadmap、architecture、repository、compiler 设计、P0/P1 工作分解、testing、performance、platforms、release、risks、ecosystem、GOVERNANCE、TOOLCHAIN。
- 语言规范 01–08（其中新增 RFC-0005/0006 未覆盖的类型与 Trait、并发、unsafe/FFI 规范）、std-core、包与构建规范。
- 需求登记册 `registry.yaml`（168 条：原 164 条 + 新增 4 条遗漏需求）与诊断登记册（111 个码）。
- ADR-0005（查询式编译器与无损 CST）、ADR-0006（MIR 解释器 Oracle）、ADR-0007（语言核心取舍）。
- `tools/doccheck.py` 自检脚本。

### Changed
- 原始类型名统一为小写；unit 只写作 `()`（ADR-0007 D1）。
- 赋值求值顺序改为先左后右（D2）；运算符优先级改为位运算高于比较（D14）。
- 阶段体系统一为 `M0、P0–P5、R`；G0–G6、R0–R5、GAP 波次、D0 已废止。
- ADR 重新编号：旧 ADR-0004 → ADR-0001，旧 ADR-0001 → ADR-0004。
- P1 起引用必须经过借用检查（取代旧方案“P2 才有借用检查”）。

### Removed
- 旧 `docs/`、`rfcs/` 退为归档，见 [MIGRATION](migration.md)。
