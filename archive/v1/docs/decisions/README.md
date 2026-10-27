> 已归档：见 v2 [README.md](../../../../README.md)

# X-Lang 架构决策索引

本目录保存会显著影响工程结构、公共接口、依赖、安全或可替换性的 ADR。ADR 记录为什么选择某个方向；正式语言规则仍由已接受 RFC 和 `specs/` 负责。

| ADR | 状态 | 决策 |
|---|---|---|
| [ADR-0001](ADR-0001-xpm-xbuild-layered-toolchain.md) | Proposed | XPM/XBuild 分层并复用成熟解析、执行和供应链标准 |
| [ADR-0002](ADR-0002-staged-modular-monolith.md) | Proposed | D0 保持文档最小集，P0/P1 使用 4～6 成员模块化单体，后续按证据拆分 |
| [ADR-0003](ADR-0003-p0-language-profile-and-labs-freeze.md) | Proposed | P0–P4 语言剖面冻结、`defer` 不进入 1.0、Labs 隔离与 CLI/服务端楔子 |
| [ADR-0004](ADR-0004-rust-llvm-host-baseline.md) | Proposed | P0–P2 宿主 Rust + LLVM 后端基线；LLVM 类型不泄漏到前端 |

状态采用 `Proposed → Accepted → Superseded/Deprecated`。未接受 ADR 不得被写成已冻结工程事实。

实现级模块/接口/门禁设计见 [docs/design/](../design/README.md)；设计服从已批准 RFC/ADR，不构成第二语言规范。
