# X-Lang 2026 技术基线

> 状态：草案参考
> 责任角色：编译器、工具链、发布工程
> 核验时间：2026-08-17（Asia/Shanghai）
> 上游依据：[X-Lang 2026 设计规格](../00-governance/x-lang-2026-design-spec.md)

本文件记录会随外部项目发布而变化的技术版本。它不是语言可观察语义；项目升级依赖时不应改动 X-Lang 程序的规范含义。

## 已核验基线

| 领域 | 官方当前稳定版 | 项目拟采用基线及理由 |
|---|---|---|
| Bootstrap | Rust 1.97.1 | 原型采用当前 stable；P0 后固定 MSRV，避免随 stable 漂移 |
| Native backend | LLVM 22.1.8；LLVM 23.1 仍为 RC | 采用 22.1.8；候选版只做兼容探针 |
| Unicode | Unicode 17.0 | 采用 17.0 形成标识符、正规化、Grapheme 和安全测试 Profile |
| WASI | WASI v0.3.1 + Component Model | 仅作为 P5 组件、插件和服务互操作实验，不进入 1.0 核心 |
| IDE | LSP 3.18 | 采用 3.18；扩展必须 namespaced 且具备能力协商 |
| Debug | DAP snapshot `bf8a5d27e8040044b84b863f90916e08925ee811` | 作为调试器适配边界，不自定义编辑器专属调试协议 |
| Supply chain | SLSA 1.2、SPDX 3.0.1 | 采用其构建来源、签名、SBOM 和发布审计模型 |
| Reproducibility | Reproducible Builds 当前定义 | 区分同 target 字节复现和跨 target 规范行为一致 |

## 官方来源

- Rust 1.97.1 dated manifest：<https://static.rust-lang.org/dist/2026-07-16/channel-rust-1.97.1.toml>
- LLVM 22.1.8 release tag：<https://github.com/llvm/llvm-project/releases/tag/llvmorg-22.1.8>
- Unicode 17.0：<https://www.unicode.org/versions/Unicode17.0.0/>
- WASI v0.3.1：<https://github.com/WebAssembly/WASI/releases/tag/v0.3.1>
- WASI 设计说明：<https://wasi.dev/>
- WebAssembly Component Model：<https://component-model.bytecodealliance.org/>
- Language Server Protocol 3.18：<https://microsoft.github.io/language-server-protocol/specifications/lsp/3.18/specification/>
- Debug Adapter Protocol：<https://microsoft.github.io/debug-adapter-protocol/specification>
- SLSA 1.2：<https://slsa.dev/spec/v1.2/>
- SPDX 3.0.1：<https://spdx.github.io/spdx-spec/v3.0.1/>
- Reproducible Builds：<https://reproducible-builds.org/docs/definition/>

## 不可变锚点与快照

| 对象 | 发布/修订时间 | 不可变锚点或内容摘要 |
|---|---|---|
| Rust 1.97.1 manifest | 2026-07-16 | SHA-256 `03569b1886ceb5c05276b50c8431ab111de944cd6140fe1fa7d821dd8e0f29cf` |
| LLVM 22.1.8 | 2026-06-16 | Git tag `llvmorg-22.1.8` |
| Unicode 17.0 | 2025-09 | Versioned URL `Unicode17.0.0` |
| WASI 0.3.1 | 2026-08-11 | GitHub release tag `v0.3.1` |
| LSP 3.18 | 核验于 2026-08-17 | Versioned specification path `/lsp/3.18/` |
| DAP | 2026-08-09 snapshot | Commit `bf8a5d27e8040044b84b863f90916e08925ee811` |
| SLSA 1.2 | 核验于 2026-08-17 | Versioned specification path `/spec/v1.2/` |
| SPDX 3.0.1 | 核验于 2026-08-17 | Versioned specification path `/spdx-spec/v3.0.1/` |
| Reproducible Builds definition | Last-Modified 2026-08-12 23:30:30 GMT | Retrieved HTML SHA-256 `67c75382073160d9cb1253b6991c361eab77309b29f7d2e9f1a6bb91e253eff0` |

DAP 快照：<https://github.com/microsoft/debug-adapter-protocol/commit/bf8a5d27e8040044b84b863f90916e08925ee811>。没有正式版本号的标准页面必须记录 commit 或内容哈希；仅记录“当前规范”不具备重放能力。

## 版本升级规则

- 只跟随正式稳定版本；RC、beta 和 nightly 只用于兼容探针；
- 每个采用版本记录首次核验日期、最后复核日期和计划复核窗口；
- 保存 release tag、commit 或下载内容 SHA-256；移动频道和 `latest` 页面不能作为唯一证据；
- Rust 升级验证 MSRV、构建、测试、依赖和 Bootstrap 可复现性；
- LLVM 升级验证 IR、对象、ABI、调试信息、优化正确性、性能和回滚；
- Unicode 升级必须评估标识符安全、正规化、分词和源码兼容；
- 协议升级必须使用能力协商，不假设所有客户端同时升级；
- 供应链标准升级必须保留旧制品的验证能力；
- 不以“最新版”为唯一采用理由，未通过验证则保持现有稳定基线。

## 更新检查清单

- [ ] 官方稳定版本与发布日期已经核验；
- [ ] 采用或暂缓理由已经记录；
- [ ] 与现有基线的兼容和迁移影响已经评估；
- [ ] 构建、测试、ABI、安全和性能探针已经执行；
- [ ] 回滚路径和旧版本验证能力仍然有效；
- [ ] 主规格只引用本文件，不复制易变版本号。
