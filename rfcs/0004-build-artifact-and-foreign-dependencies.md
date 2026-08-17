# RFC-0004：构建图、源码/制品缓存与外部生态依赖

> 状态：Proposed
> 日期：2026-08-17
> 目标阶段：P0 最小纵向链路，P2/P3 缓存与外部依赖
> 依赖：RFC-0003 的已解析包图
> 相关缺口：`GAP-COMP-04`、`GAP-COMP-07`、`GAP-COMP-09`、`GAP-DX-06`
> 正式产物：接受后生成 `specs/build/actions.md`、`artifacts.md` 和 `foreign-dependencies.md`。

## 1. 摘要

本提案定义 XBuild 的类型化 Action DAG、沙箱、构建键、Source-first/Artifact-accelerated 模型、缓存、Vendor/Offline、Git 输入，以及 C/C++、JAR/JVM 等外部依赖适配。XBuild 消费 XPM 产生的锁图，绝不重新选择依赖版本。

## 2. 核心数据流

```text
x.toml
  → XPM Resolver/Fetch/Verify
    → x.lock + ResolvedPackageGraph
      → XBuild Action Planner
        → Compiler/Linker/ForeignBuildAdapter
          → Artifact + SBOM + Provenance
```

禁止反向调用：Compiler 不回调 Resolver，XBuild 不重选版本，ForeignBuildAdapter 不修改 Lockfile，Artifact Cache 不成为源码唯一来源。P0 直接消费 RFC-0003 的 Path Workspace 最小 ResolvedGraph；P2 以后消费其完整锁图，不引入第二套临时输入协议。

## 3. 类型化 Action DAG

每个 Action 必须声明：

```text
action kind
tool identity and digest
arguments
working directory
declared inputs
declared outputs
environment allowlist
host/target platform
capabilities
timeout/memory/output limits
cache policy
```

- 未声明文件、环境、时间、随机和网络不得影响可缓存 Action；
- 非确定输入必须显式标记并禁用共享缓存；
- Host Tool 与 Target Artifact 分域，交叉编译不得误用主机探测结果；
- Action Graph 无环，诊断必须报告最小环和来源配置；
- `x build --plan --format json` 输出稳定、版本化、可审计的 Action DAG。

## 4. 构建键

Artifact/Action Key 至少包含：

```text
package/source tree digest
manifest/lock/policy digest
compiler and standard library identity
sysroot/SDK/linker digest
target triple and CPU features
profile and panic strategy
Feature Resolution Domain
dependency interface/artifact IDs
build tool/script digest
declared environment and cfg
generator version and inputs
```

不能只使用“包名 + 版本”。任何输入变化应导致必要的 Cache Miss；不相关输入不应触发重建。

## 5. Source-first、Artifact-accelerated

1. X Registry Package 和具有规范源码来源的 X Git Package 必须 Source-first；其规范真相是源码快照、Manifest、Digest、签名和 Provenance。
2. 这类 X 包的预编译 Artifact 是可删除缓存，不是唯一分发形态或包身份；Cache Miss、摘要/签名失败、Target/Profile/Feature/工具链不匹配时必须安全回退源码构建。
3. X-Lang ABI/元数据格式未稳定前，普通 X 库不得以 binary-only 方式发布。
4. Foreign Dependency 可以 Artifact-first，包括 JAR、系统库和闭源 SDK；但必须固定内容摘要、来源、签名/Provenance、Host/Target、ABI/Runtime 契约和可验证离线获取方式。
5. Artifact-first Foreign Dependency 不得声称支持源码回退；验证失败或契约不匹配时必须阻断构建。只有同时锁定规范源码快照和构建契约的 Foreign Dependency 才可声明源码回退。

Artifact Manifest 至少记录：

```text
format version
Package ID and source digest
compiler/stdlib/ABI identity
target/CPU/profile/features
dependency artifact IDs
exports and link inputs
debug info/SourceMap
SBOM/provenance/signature/content digest
```

## 6. 缓存与远程执行

- 本地 Cache 内容寻址、原子写入、读取验摘要；损坏条目进入 Quarantine 后回退构建；
- 远程 Cache 第一阶段只读，写入、跨租户共享和远程执行分别通过后续 ADR 开启；
- 缓存失败不得改变构建语义；统计包括命中、Miss、拒绝原因、下载量和尾延迟；
- 清理只删除可重建 Artifact，不删除唯一源码、Lockfile、审计或签名证据；
- 远程执行采用声明式 Action 协议，执行器不能获得未声明 Workspace 文件或凭据。

## 7. Build Script 与生成代码

1. 1.0 无通用 Build Script；必要任务只能通过登记制 Generation Action/Adapter 执行。
2. Generation Action 的工具必须是 RFC-0003 Host Tool Domain 中的锁图节点，不能是 PATH 上偶然找到的命令。
3. 每个 Generation Action 显式声明：Tool Package/Artifact ID、参数、工作目录、输入、输出、环境白名单、Capability、Host/Target、超时、内存、进程和输出上限。
4. 时间、随机、网络、未声明文件和未声明环境默认不可见；确需非确定输入时必须标为不可共享缓存且不得进入可复现发布。
5. 工具、输入、参数、环境、Capability、Target 和输出摘要全部进入构建键；生成物记录 Generator Version、SourceMap、License 和 Provenance。
6. Action 不得修改 Manifest/Lockfile、用户源码或依赖缓存；输出只能原子写入声明目录。
7. 同输入生成结果不一致时隔离结果，阻断共享缓存和发布。

后续若研究 `build.x`，必须通过新 RFC 扩大 Capability；它不能绕过上述 Action Contract。

## 8. Git、Vendor 与离线

- 构建读取 Exact Commit + Tree Digest 的不可变快照，不读取 Branch、Hook、脏工作树或可变 `.git` 状态；
- `git describe`、提交时间等只有显式声明后才能成为不可缓存的构建输入；
- Git Credential 只在 Fetch 边界使用，不传给 Action；
- XPM 的 `x vendor` 从锁图生成并验证只读树和 Vendor Manifest，记录来源、版本/Commit、摘要、许可证和签名状态；XBuild 只消费冻结的 Vendor Source，不实现 Vendor Writer；
- `x build --offline --locked` 不产生 DNS/网络请求；缺包时列出精确 Package ID；
- Air-gapped 导入使用签名清单并在目标环境再次验摘要。

## 9. 外部依赖通则

```text
ForeignResolverAdapter → 由 XPM 调用，只解析坐标/原生态 Lockfile/来源/摘要并输出冻结 ForeignResolution
ForeignBuildAdapter    → 由 XBuild 调用，只消费 ForeignResolution 进行获取、构建、链接或定位
x-bindgen              → 由 XBuild 作为生成 Action 调用，只消费冻结输入并生成版本化绑定
Compiler               → 只处理已声明 ABI，不解析 Maven/CMake/Conan 生态
```

两类 Adapter 是不同的版本化接口，进程实现可以共享代码但单次调用的 Capability 不能兼具解析和构建：

- `ForeignResolverAdapter` 可以调用原生态 Resolver，不能编译、链接或写构建输出；XPM 验证结果后才可更新 `x.lock`；
- `ForeignBuildAdapter` 不能联网选版本、修改 X/外部 Lockfile 或接受未冻结传递边，只能按冻结图生成 Action 输入；
- `x-bindgen` 的生成器版本、Header/Schema、Flag、Host/Target 和输出摘要全部进入 Action Key；
- 外部包管理器的 Lockfile、Adapter 身份和最终制品摘要必须进入 X 构建输入，任何漂移在 `--locked` 下失败。

### 9.1 Foreign Lock Contract

每个 `ForeignResolution` 必须使用版本化 Schema，并至少记录：

```text
id, ecosystem, resolver adapter identity/version
root coordinate/source and external lock digest
host, target, ABI/runtime contract
nodes: coordinate, source/repository, license, artifact/source digests, signature/provenance
edges: from, to, dependency kind/scope, exclusions and activation condition
native contract: compiler, sysroot, language standard, stdlib, ABI flags, link mode
binding inputs: headers/schema digest, flags and generator identity
```

`x.lock` 内嵌稳定排序的节点/边和制品摘要，并可另外保存原生态 Lockfile 的内容寻址 Blob 或 Vendor 相对引用。仅保存外部 Lockfile 摘要不合格，因为 `x tree/why/audit/SBOM` 必须离线解释传递边；若 Blob 缺失，`--offline` 只能在内嵌图和所有 Artifact 均完整时继续。Foreign Resolution ID 包含 Ecosystem、Adapter Schema、Host/Target、ABI 和图摘要。

JVM 节点记录 GAV/Classifier/Packaging/Repository/POM/BOM 与 JAR Digest；C/C++ 节点额外记录 Compiler、Sysroot、Standard、Stdlib、ABI Flag、Link Mode、Header 和 Library Digest。Node/Python/.NET/WASM 适配器提供同等信息，不得把不透明原生态 Lockfile 当作唯一审计来源。

## 10. JAR/JVM

优先使用 Maven/Gradle 发布坐标，不从 Git 仓库猜测 Java 构建：

```toml
[foreign.jvm.dependencies]
json = {
    coordinate = "com.example:json:2.4.1",
    repository = "company",
    sha256 = "..."
}
```

- 身份包含 Group/Artifact/Version/Classifier/Packaging/Repository 和 SHA-256；
- 锁定 POM/BOM 解析后的完整传递图、排除和 Mirror；
- 优先声明式读取 POM/BOM；必须执行 Plugin 时进入受限沙箱；
- 记录最低 JVM、Bytecode Level、Module Name、Classpath/Module Path 和 JNI 边界；
- 重复 Class/Module 稳定报错，禁止 Classpath First-wins；
- 本地私有 JAR 必须声明相对路径和摘要，不得放入 `src/` 或全局手工 Classpath。

## 11. C 与 C++

### 11.1 C

- 锁定 Header、Library/Object、Target ABI、Calling Convention、编译器/Sysroot 身份；
- 优先 `pkg-config` 或 CMake Package Config 的只读发现，结果规范化进 Artifact Metadata；
- X 只稳定承诺 `extern "C"`、`@repr(C)`、固定宽度标量、Pointer+Length 和 Opaque Handle；
- 所有权、Allocator、线程、错误和 Unwind 边界必须有桥接契约。

### 11.2 C++

- 不承诺通用 C++ ABI，默认使用 C Shim/Opaque Handle；
- 直接 C++ ABI 保持 Experimental，并锁定编译器、Target、C++ Standard、Stdlib、ABI Flag、Exception/RTTI、Runtime 和 Linker；
- Conan/vcpkg/CMake 是 Adapter，不成为 XPM 核心语义；其 Lockfile 和下载摘要被 X Lock/Artifact 引用；
- Bindgen 记录输入 Header Digest、Flag、Target 和 Generator Version，漂移阻断 CI。

## 12. 其他生态

- Node 由 npm/pnpm，Python 由 PyPI/uv，.NET 由 NuGet，WASM 由 WASI Component/OCI 管理各自依赖；
- XPM 调用受控 `ForeignResolverAdapter` 并记录冻结结果，不重新实现外部生态全部 Resolver 语义；XBuild 调用相应 `ForeignBuildAdapter` 和绑定生成 Action；
- 外部运行时对象通过明确 SDK/FFI 边界，不进入 X-Lang 核心类型或包身份。

## 13. 命令契约

```text
x build/check/run/test [--locked|--offline|--frozen]
x build --plan [--format json]
x build --explain-rebuild <target>
x artifact inspect|verify|provenance
x bundle build|inspect|verify
x cache status|verify|prune
x vendor|vendor verify
x foreign add jar|c|cxx
x foreign doctor
x bindgen --locked
x repro pack
```

命令输出提供人类文本和版本化 JSON；失败包含 Action ID、输入摘要、Sandbox/Cache 状态和安全回退结果。`x bundle build` 只汇集已验证 Artifact，不重新编译或解析依赖。

## 14. 多目标分发 Bundle

发布单元是版本化 Distribution Bundle，而不是未注明目标的散装二进制。Bundle Manifest 至少记录：

```text
bundle schema and package identity/version
supported target triples and CPU baseline
artifact kind/path/content digest/size
compiler, stdlib, runtime and ABI requirements
profile, panic strategy and enabled features
dynamic libraries, SDK and platform minimum versions
SBOM and license references
build provenance and source/lock digests
signature, signer identity and verification policy
debug symbols and SourceMap references
```

一个 Bundle 可以包含多个 Target Artifact，但每个 Artifact 的 Host/Target、摘要和运行时契约独立验证。安装器只能选择精确兼容项；不允许把 `-march=native` 产物标为通用 CPU，也不承诺不同 Host 对 native 优化产生相同字节。

Bundle 可以通过 Registry、OCI 或离线介质传输；传输位置不构成包身份，也不允许宣称单一网络或 IPFS 地址永久可用。

## 15. 工具复用策略

| 能力 | 首选借鉴/复用 | 边界 |
|---|---|---|
| Manifest/Workspace UX | Cargo | 不复制 Cargo Feature 和 Build Script 历史语义 |
| Resolver | PubGrub/Dart Pub | 算法可替换，规范冻结行为 |
| 下载/缓存 | uv/Cargo | X Package ID 和 Policy 自定义 |
| 模块身份/校验 | Go Modules | 不照搬 MVS |
| 本地外部执行 | Ninja | 只是 Adapter，不决定 X 构建语义 |
| Action/远程缓存 | Bazel REAPI/Buck2 思路 | P3 后按证据采用 |
| 可复现 Store | Nix 思路 | 不要求用户安装 Nix |
| Blob 分发 | OCI Distribution | XPM 管理版本、Yank 和索引 |
| 供应链 | TUF、Sigstore、in-toto/SLSA、SPDX/CycloneDX | 不自创密码协议 |

## 16. 验收

- 两个隔离环境构建结果可比较，差异有输入级解释；
- 修改每类声明输入产生必要 Cache Miss，无关输入不重建；
- Cache Poison、截断写、错误签名和跨 Target/Profile/Feature 命中全部拒绝并回退源码；
- Offline/Locked 网络探针为零；Git Branch 移动不改变 Locked Build；
- Vendor 与 Registry 构建的语义、SBOM 和测试一致；
- JAR 传递冲突、重复 Class、POM 篡改具有负向语料；
- C/C++ ABI 不匹配、Allocator/Exception 跨边界和 Debug/Release Runtime 混用被拒绝；
- Generation Action 越权、未声明输入、超时、OOM 和非确定输出不污染 Cache；
- 多目标 Bundle 的 Target 选择、摘要、签名、运行时最低版本、SBOM 和 Provenance 具有正反语料；
- 至少一个 100 包/10,000 文件 Workspace 验证全量、单包增量和远程 Cache 收益。

## 17. 未决问题

| 问题 | Owner | 截止阶段 | 未达成一致时的失败回退 |
|---|---|---|---|
| P0 使用 Ninja 图还是内置轻量 Executor | Build WG | P0 纵向链路前 | 使用内置单机 Executor，保留稳定 Action JSON |
| 远程 Cache 采用 REAPI 兼容协议还是 OCI Artifact | Build + Infra WG | P3 远程 Cache 开启前 | 远程写入/执行保持关闭，只用本地 Cache |
| `.xlib` 在 ABI 稳定前包含哪些中间表示 | Compiler WG | P3 Artifact 发布前 | 不发布 `.xlib`，只缓存同工具链私有 Artifact |
| `build.x` 是否进入 1.0 后扩展 | Security + Build WG | P4 API Freeze 前 | 1.0 不提供通用 Build Script，只允许登记 Adapter |
