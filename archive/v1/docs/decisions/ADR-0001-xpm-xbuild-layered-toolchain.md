> 已归档：见 v2 [docs/decisions/ADR-0004-xpm-xbuild-layering.md](../../../../docs/decisions/ADR-0004-xpm-xbuild-layering.md)

# ADR-0001：XPM/XBuild 分层工具链与成熟技术复用

## 状态

Proposed

## 日期

2026-08-17

## 背景

X-Lang 需要管理包身份、版本、Lockfile、Git/Registry 来源、构建动作、缓存、外部语言依赖和供应链。如果将这些职责放入一个命令或直接照搬 Cargo/Bazel/npm，会把其他生态的历史语义和复杂权限引入核心；如果全部自研，又会重复实现 Resolver、下载、缓存、远程执行、Blob 和签名协议。

## 决策

采用统一 `x` CLI、内部 XPM/XBuild 两个稳定责任域和可替换 Adapter：

```text
x CLI
  ├─ XPM：Manifest、Package ID、Resolver、Lock、Fetch、Verify、Vendor、Publish、Audit
  │    └─ ForeignResolverAdapter：冻结外部坐标、图、原生态 Lock 与摘要
  └─ XBuild：Target/Action DAG、Sandbox、Scheduler、Artifact Key、Cache、Provenance
       ├─ Compiler/Linker
       ├─ Ninja local executor adapter（候选）
       ├─ Remote cache/execution adapter（后续）
       └─ C/C++/JVM/Node/Python/WASM ForeignBuildAdapters
```

依赖方向固定为：

```text
x.toml → XPM → x.lock/resolved graph → XBuild → compiler/linker/adapters → artifact
```

### XPM 负责

- Package/Source Identity；
- Manifest/Workspace 验证；
- 版本和 Feature Resolution；
- Lockfile、Fetch、Digest/Signature Verification；
- Vendor、Publish/Yank、Audit/SBOM 输入。
- 调用 `ForeignResolverAdapter`，将外部坐标、传递节点/边、原生态 Lock 摘要和 Artifact 摘要冻结为 `ForeignResolution`。

XPM 不负责编译 Action DAG、语言名称解析、C++ ABI 或任意 Build Script 执行；Resolver Adapter 不得编译或链接。

### XBuild 负责

- Target 和类型化 Action DAG；
- Sandbox、调度和资源预算；
- 增量失效、Artifact Key、本地/远程 Cache 接口；
- Compiler/Linker/ForeignBuildAdapter 调用；后者只消费冻结的 `ForeignResolution`；
- Artifact、SBOM 和 Provenance 输出。

XBuild 不重新选择版本、不管理 Registry 身份、不改变语言类型规则或发布策略。ForeignBuildAdapter 不得联网解析版本或修改 X/外部 Lockfile；Resolver/Build Adapter 即使共享实现，也必须按不同 Capability 接口运行。

### 技术复用

- Cargo：借鉴 CLI、Manifest、Workspace 和 Source-first UX；Cargo 只构建初始 Rust 编译器，不作为 X 用户包管理器。
- PubGrub：首个 Resolver 实现；规范不永久绑定算法。
- uv/Cargo/Go Modules：借鉴并行下载、内容缓存、Package Identity、摘要和离线模型。
- Ninja：P0/P1 可作为外部 Action 本地 Executor；不能决定语言增量语义。
- Bazel REAPI/Buck2/Nix：P3 后借鉴 Action、远程缓存/执行和可复现 Store，不作为首版强依赖。
- OCI Distribution：候选 Blob/Artifact 分发层；版本、Yank、搜索和策略仍由 X Registry 管理。
- TUF/Sigstore/in-toto/SLSA/SPDX/CycloneDX：供应链和来源标准，不自创密码协议。

## 阶段

| 阶段 | 交付 | 明确不做 |
|---|---|---|
| P0/P1 | Cargo 构建编译器；冻结最小 PackageId/Path Workspace/ResolvedGraph；本地确定 Action；源码构建 | SemVer/公共 Registry、远程执行、任意 Build Script |
| P2 | Manifest/Lock Schema、PubGrub 原型、Git/Path/Vendor、内容缓存 | 稳定二进制 ABI、公共发布承诺 |
| P3 | Registry Client、远程 Cache、外部 Adapter、签名/SBOM | Core 依赖生态框架 |
| P4 | Publish/Yank、透明日志、Provenance、灾备和发布门禁 | 未验证 Artifact 成为唯一来源 |
| P5+ | JVM/Node/Python/C++/WASM 联邦适配 | 将外部包管理语义塞入编译器核心 |

## 替代方案

### 直接使用 Cargo 作为 XPM

拒绝。Cargo 不能定义 X 的 Package Identity、Edition、ABI、Feature Domain、Public Dependency 和外部生态边界。

### 默认要求 Bazel/Buck2/Nix

拒绝。能力强但安装、服务和规则成本不适合 P0/P1；保留 Adapter 和协议兼容空间。

### 自研 Resolver、远程执行、Blob 和签名协议

拒绝。维护和安全成本过高，应复用成熟算法、协议和实现。

### 只分发预编译 `.xlib`

拒绝。稳定 ABI 和元数据格式不存在；X 包采用 Source-first、Artifact-accelerated，并在不匹配时回退源码。Foreign Dependency 可以按 RFC-0004 的摘要与 ABI 契约采用 Artifact-first。

## 后果

### 正面

- 职责和故障域清楚，Resolver/Executor/Registry 可独立测试和替换；
- P0 不被远期包市场和远程执行阻塞；
- 大型项目可以逐步获得内容缓存、远程执行和供应链证明；
- 外部生态保持各自 Resolver，X 只记录冻结结果并提供绑定。

### 代价

- 需要维护 XPM 与 XBuild 之间的版本化 Resolved Graph Contract；
- 双域和多个 Adapter 增加端到端测试矩阵；
- X 包的 Source-first 在冷构建时较慢，需要可靠缓存和并行下载；
- Public Dependency、Feature Domain 和受控多版本比简单 Lockfile 更严格。

## 接受门禁

- RFC-0003/0004 的责任无重叠且数据契约可版本化；
- P0 用至少三个包证明 Path Workspace → Action DAG → LLVM 链接；
- Resolver 小图差分、Lockfile 确定性和 Offline 测试通过；
- Artifact Key 输入敏感性、Cache Poison 回退和 Sandbox 负向测试通过；
- 对 Cargo-only、Bazel-required 和全自研方案形成可复现实验或成本记录。

## 后续 ADR

- Remote Cache Write 与 Remote Execution；
- Build Script Capability Model；
- Artifact Metadata/ABI 兼容；
- C++ Direct ABI Experimental；
- Cache Quarantine、淘汰与跨租户安全。

## 官方参考

- [Cargo Reference](https://doc.rust-lang.org/cargo/reference/index.html)：Manifest、Workspace、Source 与命令体验；
- [Dart Package Versioning](https://dart.dev/tools/pub/versioning)：版本约束和 PubGrub 冲突解释；
- [uv Resolution](https://docs.astral.sh/uv/concepts/resolution/)：解析策略、性能和缓存边界；
- [Go Modules Reference](https://go.dev/ref/mod)：模块身份、校验、Proxy 和 Vendor；
- [Ninja Manual](https://ninja-build.org/manual.html)：小型构建执行器和生成式构建图；
- [Bazel Remote Caching](https://bazel.build/remote/caching)：Action/内容寻址远程缓存；
- [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec)：不可变 Blob 和制品分发。

上述来源用于约束候选方向，不自动成为 X-Lang 构建依赖；实际采用的 Release/Commit、许可证、摘要、升级和回退必须在 ADR 接受前锁定。
