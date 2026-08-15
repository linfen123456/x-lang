---
doc_id: DOC-OPERATIONS-PLATFORM-MATRIX
authority: evidence
owner: role/release-team
backup_owner: role/operations-team
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [QUALITY, XLF, XLC, XLE]
---
# 平台支持与发布矩阵

| Tier | 平台范围 | 支持级别 | 必须证据 |
|---|---|---|---|
| Tier 1 | Linux x86_64、Windows x86_64、macOS arm64/x86_64 | Stable/LTS 候选 | 构建、安装、运行、升级、回滚、性能和安全 |
| Tier 2 | WASM/WASI、Linux arm64、Windows arm64、主流容器 | Beta/Stable 子集 | 互操作、资源限制、浏览器/运行时 E2E、ARM64 真机与安装验证 |
| Tier 3 | Android/iOS、GPU、BSD、嵌入式/QEMU | Experimental | 能力探测、最小样例、明确缺口和退出条件 |
| Research | eBPF、ZK、脑机、硬实时认证、未知硬件 | Labs only | Charter、预算、威胁模型、Go/No-Go、退出报告 |

晋级按“平台×版本×架构”单独记录，不以一个平台的绿色结果代表整个 Tier。能力缺失必须返回结构化错误和可用替代，不得静默改变语义。Tier 1 的任何阻断性安全/数据损坏/回滚失败都阻断 Stable；Tier 3 失败不得阻断主线但必须保留证据。

## 平台记录字段

每个平台条目必须记录目标三元组、CPU 特性基线、端序与指针宽度、最小 OS/SDK、C ABI 与链接器、安装格式、调试器、线程与原子能力、文件系统语义、网络/TLS 后端、异步 I/O 后端、时区与 Unicode 数据版本、签名要求和已知限制。没有这些字段时，只能登记为探索目标，不能宣称支持。

## Tier 1 最低能力

Tier 1 必须支持编译器、运行时、核心标准库、`x build/check/run/test/fmt/doc`、C FFI、调试信息、安装/卸载、离线构建、升级和回滚。Windows 需要明确 MSVC/Windows SDK 和路径、控制台、DLL 规则；Linux 需要明确 glibc/musl 范围、ELF、动态加载和发行版基线；macOS 需要明确 SDK、Deployment Target、Mach-O、签名和公证。

同一操作系统的 x86_64 与 ARM64 是独立目标。交叉编译成功不能替代目标机运行验证；至少包含真机启动、文件与网络、线程与原子、异常/崩溃、动态库和调试器检查。

## Tier 2 与 WebAssembly

WASM/WASI 必须区分浏览器、WASI Preview 版本和边缘宿主，不把一个宿主的能力推断到其他宿主。矩阵需要记录线程、共享内存、文件系统、网络、时钟、随机数、动态加载和异常处理差异。缺失能力通过编译期 capability 或明确 `Unsupported` 返回，不以空实现伪装成功。

Linux ARM64 与容器支持需要覆盖基础镜像、libc、证书存储、时区数据、只读文件系统、非 root 运行、CPU/内存配额和优雅终止。容器镜像不是新的语言平台，但它会改变运行时能力和发布责任。

## 移动、GPU 与嵌入式

Android/iOS 分别记录 NDK/SDK、最低系统版本、应用生命周期、后台限制、权限、签名、商店政策和 FFI 边界。GPU 目标按 CUDA、ROCm、Metal 等后端独立登记，必须有 CPU 回退或明确拒绝路径。嵌入式目标记录芯片、内核/裸机、链接脚本、内存预算、中断、时钟、原子能力和硬件在环测试。

这些目标在进入 Tier 2 以前不得改变 CORE 语言语义，也不得要求核心标准库依赖专有 SDK。

## 晋级、降级与停止支持

平台晋级要求连续发布周期的绿色证据、明确 Owner、可用构建资源、安全更新渠道、安装与回滚验证以及已知限制文档。降级触发条件包括长期无维护者、上游 SDK EOL、关键安全问题无法修复、测试设备不可获得或 ABI 无法维持。

停止支持必须提前公告最后支持版本、替代平台、迁移步骤、安全补丁期限和制品保留期。EOL 后不得删除历史说明和校验信息；用户仍能判断旧制品来源及风险。

## 验收样例

一个“Windows x86_64 Stable”条目只有在指定 Windows/SDK 最低版本、MSVC ABI、安装器、签名、调试、运行时后端、测试设备和回滚证据后才成立。“Windows 已支持”或“可交叉编译”都不是合格证据。
