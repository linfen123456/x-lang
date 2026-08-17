# X-Lang 原始功能全量追溯矩阵

> 总纲：[X-Lang 企业级完整文档体系总纲](./X-Lang企业级完整文档体系总纲.md)  
> 大纲版本：1.0-outline｜状态：ID 与来源基线已冻结｜初始基线：2026-08-14｜复审：2026-08-15  
> 目的：逐项证明 `docs/原始文档/1.txt` 至 `12.txt` 中的功能已被保留、分级和分配；“保留”不等于进入核心语言或形成产品承诺。  

## 1. 追溯规则

每个原始功能使用稳定编号 `XLF-首次出现的来源文件-序号`；后续文件重复或现实化同一需求时，以“来源别名”映射到首次出现的规范 ID，避免把同一功能重复计数。`XLF-*` 只表示 12 份原始材料中可追溯的需求，不得用于表示后来通过语言对标发现的缺口；后者统一使用 `XLC-*`，并在[《多语言对标与全栈能力补全大纲》](./X-Lang多语言对标与全栈能力补全大纲.md)管理。本表“分级·处置”列保留第一次审查历史，其中 `CORE治理·接受/重设计` 等值是历史分类与处置，不属于当前 `范围/状态` 字段；87 个非直接接受项的当前权威路线由[《未纳入与偏离内容再审核及回归路线》](./X-Lang未纳入与偏离内容再审核及回归路线.md)中的 `RETURN/CONDITIONAL/SPLIT/RESEARCH` 覆盖。功能关闭前必须补齐规范/RFC、目标项目、测试或研究报告；不得用文件级概括代替功能级证据。

| 处置 | 含义 | 必须证据 |
|---|---|---|
| 接受 | 已进入目标版本或工程路线 | 规范规则、任务、测试 |
| 重设计 | 用户价值保留，原技术方案因安全/可行性被替换 | ADR/RFC、替代方案、威胁模型 |
| 暂缓 | 有价值但不进入当前里程碑 | 前置依赖、重新评审条件 |
| 研究 | 不形成兼容承诺的独立探索 | 假设、原型、基准、退出条件 |
| 归档 | 仅保留历史，不计划实现 | 否决理由、可重新开启条件 |

## 2. `1.txt`：语言愿景与核心能力

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-01-001 | 可插拔三段式编译器 | x-compiler、架构 ADR | CORE·接受 | 前/中/后端接口与端到端测试 |
| XLF-01-002 | Lexer/Parser/Semantic→HIR | x-compiler-frontend | CORE·接受 | HIR 验证器与符合性语料 |
| XLF-01-003 | HIR 平台无关优化→MIR/LIR | x-compiler-middle | CORE·接受 | Pass 差分测试 |
| XLF-01-004 | LLVM 原生后端 | x-codegen-llvm | CORE·接受 | 三大 OS 目标测试 |
| XLF-01-005 | WASM 与交叉编译 | x-codegen-wasm、x-target | EXTENDED·暂缓 | WASI/移动端 RFC 与互操作测试 |
| XLF-01-006 | 所有权、借用、生命周期 | 语言规范、x-borrow | CORE·接受 | compile-pass/fail 套件 |
| XLF-01-007 | 无 GC 核心模式 | 内存模型 RFC | CORE·重设计 | 明确核心无 GC；可选 GC 独立实验 |
| XLF-01-008 | Comptime 与零成本抽象 | x-consteval、优化规范 | EXTENDED·暂缓 | 确定性、资源上限与基准 |
| XLF-01-009 | 协程、CSP、Channel | x-async、x-std-sync | EXTENDED·接受 | 取消、关闭、公平性测试 |
| XLF-01-010 | 简洁、显式、OOP+FP 表达力 | 语言设计原则 | CORE·接受 | 语法 RFC、学习性评审 |
| XLF-01-011 | 跨平台标准库 | x-std、x-pal | CORE·接受 | 平台能力矩阵 |
| XLF-01-012 | 声明式跨平台 UI | x-ui | EXPERIMENTAL·研究 | 独立框架原型，不进入核心 |
| XLF-01-013 | 包管理、构建、LSP、格式化一体化 | x-cli、xpm、x-lsp、xfmt | EXTENDED·接受 | 工具链 E2E |
| XLF-01-014 | IDE、增量/并行编译 | x-lsp、editors、x-query | EXTENDED·接受 | 延迟与正确失效基准 |
| XLF-01-015 | 分阶段路线与最终自举 | release、x-bootstrap | EXTENDED·暂缓 | 三阶段 bootstrap 复现 |

## 3. `2.txt`：编译器、运行时与开发框架

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-02-001 | 编译器+LSP+IDE+运行时四层架构 | workspace、ADR | CORE·接受 | 依赖方向检查 |
| XLF-02-002 | Token/AST/HIR/LIR/LLVM 全流水线 | x-compiler | CORE·接受 | 可逐层 dump/verify |
| XLF-02-003 | Rust 初始实现与自举 | x-bootstrap | CORE/EXTENDED·接受 | Rust MVP；1.0 后自举 |
| XLF-02-004 | 增量、并行编译与彩色诊断 | x-query、x-diagnostics | EXTENDED·接受 | 缓存失效与诊断快照 |
| XLF-02-005 | LSP 分析、补全、导航、格式化、诊断 | x-lsp | EXTENDED·接受 | LSP 协议测试 |
| XLF-02-006 | tree-sitter 增量解析候选 | x-syntax | EXPERIMENTAL·重设计 | 与共享 Parser 架构对比 ADR |
| XLF-02-007 | VS Code + TextMate + DAP | x-vscode、x-debug | EXTENDED·接受 | 扩展 E2E |
| XLF-02-008 | IntelliJ Grammar-Kit/JFlex/PSI | x-intellij | EXTENDED·重设计 | 优先共享 LSP；PSI 仅补平台能力 |
| XLF-02-009 | XRT 内存、协程、I/O、标准库 | x-runtime、x-std | CORE/EXTENDED·接受 | 模块与平台测试 |
| XLF-02-010 | RAII + 可选 GC | 内存 RFC、x-gc-experiment | EXPERIMENTAL·重设计 | GC 隔离堆原型；不进入 1.0 |
| XLF-02-011 | C ABI FFI | x-ffi | EXTENDED·接受 | ABI 黄金测试 |
| XLF-02-012 | 正式语法规范与示例 | specs、conformance | CORE·接受 | EBNF 与符合性套件 |
| XLF-02-013 | 标准用户项目结构和 `x.toml` | x-build、xpm | CORE·接受 | Schema 与模板测试 |
| XLF-02-014 | build/run/test/fmt/check/doc/publish 命令 | x-cli | CORE/EXTENDED·接受 | CLI 契约测试 |
| XLF-02-015 | 调试与性能分析 | x-debug、x-profiler | EXTENDED·接受 | DAP、DWARF/PDB、Profiler 测试 |

## 4. `3.txt`：AI 原生语言与 Agent 工具

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-03-001 | `#spec` 显式契约 | x-contracts | EXPERIMENTAL·研究 | 可执行契约 RFC |
| XLF-03-002 | `#example` 自然语言/示例测试 | x-test、x-contracts | EXPERIMENTAL·重设计 | 自然语言非规范；示例可执行 |
| XLF-03-003 | `pure` 与确定性标记 | x-effects | EXPERIMENTAL·研究 | Effect RFC 与静态规则 |
| XLF-03-004 | AST/Embedding 语义索引和 `x.meta` | x-semantic | EXPERIMENTAL·接受 | 版本化 Schema 与隐私测试 |
| XLF-03-005 | `x agent init/implement/explain/fix` | x-agent | EXPERIMENTAL·接受 | diff、权限、测试、人工确认 |
| XLF-03-006 | 本地向量检索与上下文构建 | x-semantic | EXPERIMENTAL·接受 | 检索质量与资源预算 |
| XLF-03-007 | 内置 MCP Resources/Tools | x-mcp | EXPERIMENTAL·接受 | 最小权限与审计测试 |
| XLF-03-008 | AI IDE 协驾驶面板 | editors/ai | EXPERIMENTAL·暂缓 | 用户研究与插件原型 |
| XLF-03-009 | 规范实时校验和依赖影响图 | x-contracts、x-analysis | EXPERIMENTAL·接受 | 误报率与影响分析测试 |
| XLF-03-010 | 标准库机器可读注释 | xdoc、x-std | EXTENDED·接受 | API 元数据 Schema |
| XLF-03-011 | 模板市场 | x-templates、x-registry | EXTENDED·暂缓 | 签名、审核和供应链策略 |
| XLF-03-012 | AI 驱动初始化→契约→实现→修复→发布 | x-agent-workflow | EXPERIMENTAL·接受 | 沙箱 E2E，不允许无审批生产发布 |

## 5. `4.txt`：AI 训练、微调与网络

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-04-001 | Tensor 类型与 Shape 推导 | x-ml-core、x-tensor-ir | EXPERIMENTAL·研究 | 类型/布局/数值测试 |
| XLF-04-002 | 编译期自动微分 | x-autograd | EXPERIMENTAL·研究 | 梯度对照与误差界 |
| XLF-04-003 | CUDA/ROCm/Metal Kernel 生成 | x-codegen-gpu | EXPERIMENTAL·研究 | CPU 回退与设备矩阵 |
| XLF-04-004 | 静态计算图优化与自动并行 | x-ml-compiler | EXPERIMENTAL·研究 | 图等价与性能基准 |
| XLF-04-005 | LoRA/QLoRA Adapter 注入 | x-ml-train | EXPERIMENTAL·研究 | 与成熟框架结果对照 |
| XLF-04-006 | 量化、混合精度和分布式训练 | x-ml-train | EXPERIMENTAL·研究 | 精度、吞吐、容错测试 |
| XLF-04-007 | io_uring/IOCP 网络引擎 | x-io、x-net | EXTENDED·接受 | 跨平台异步 I/O 测试 |
| XLF-04-008 | HTTP/1-3、QUIC、gRPC、WebSocket | x-net-protocols | EXTENDED·接受 | 标准互操作套件 |
| XLF-04-009 | Protocol as Type | x-protocol-types | EXPERIMENTAL·研究 | 包状态机 RFC 与诊断 |
| XLF-04-010 | 训练即服务 | x-ml-serve | EXPERIMENTAL·暂缓 | 安全、资源隔离、API 契约 |
| XLF-04-011 | 动态批处理 | x-ml-serve | EXPERIMENTAL·接受 | 延迟/吞吐/SLA 基准 |
| XLF-04-012 | `x agent train/finetune/serve` | x-agent-ml | EXPERIMENTAL·暂缓 | 可审计工作流 E2E |

## 6. `5.txt`：并发、进程、内存与 I/O

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-05-001 | `spawn`、作用域线程和 Send 检查 | x-async、x-borrow | CORE/EXTENDED·接受 | 生命周期与线程安全测试 |
| XLF-05-002 | M:N 调度、工作窃取和专用线程池 | x-scheduler | EXTENDED·接受 | 公平性、阻塞隔离、压力测试 |
| XLF-05-003 | fork/exec 安全封装 | x-process | EXTENDED·重设计 | Windows 等价 API 与多线程 fork 限制 |
| XLF-05-004 | 共享内存和 IPC | x-ipc | EXTENDED·接受 | 所有权、崩溃与权限测试 |
| XLF-05-005 | 自定义分配器、Arena | x-alloc | EXTENDED·接受 | OOM、对齐、泄漏测试 |
| XLF-05-006 | 原始指针与 Ghost Memory 调试 | x-unsafe、x-sanitizer | EXPERIMENTAL·重设计 | unsafe 契约；幽灵内存仅诊断工具 |
| XLF-05-007 | CPU/GPU 统一内存 | x-memory-gpu | EXPERIMENTAL·研究 | 设备一致性与回退 |
| XLF-05-008 | Async File/Direct I/O | x-io | EXTENDED·接受 | 对齐、取消和回退测试 |
| XLF-05-009 | sendfile/splice 零拷贝 | x-io-zero-copy | EXTENDED·接受 | 边界定义和平台基准 |
| XLF-05-010 | mmap 智能预取 | x-io-mmap | EXPERIMENTAL·研究 | 工作集与退化基准 |
| XLF-05-011 | AI 系统操作命令 | x-agent-sys | EXPERIMENTAL·重设计 | 建议/生成配置，不自动获取高权限 |

## 7. `6.txt`：全平台应用与系统开发

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-06-001 | 分层渲染引擎与声明式 UI | x-ui | EXPERIMENTAL·研究 | 渲染/状态/无障碍 RFC |
| XLF-06-002 | Windows/macOS/Linux 桌面 | x-ui-desktop | EXPERIMENTAL·暂缓 | 真机矩阵与打包测试 |
| XLF-06-003 | Skia、WebView、托盘和快捷键 | x-ui-render、x-platform-desktop | EXPERIMENTAL·研究 | 后端插件接口 |
| XLF-06-004 | Android/iOS 原生库和薄胶水 | x-mobile | EXPERIMENTAL·暂缓 | NDK/Apple SDK 样例 |
| XLF-06-005 | Metal/Vulkan、触控与传感器 | x-mobile-runtime | EXPERIMENTAL·研究 | 真机延迟与生命周期测试 |
| XLF-06-006 | 小程序 WASM 逻辑和模板转译 | x-miniapp | RESEARCH·研究 | 微信/支付宝/抖音原型 |
| XLF-06-007 | 服务端 HTTP3/gRPC/AI 推理 | x-server、x-ml-serve | EXTENDED/EXPERIMENTAL·暂缓 | 协议互操作与模型格式测试 |
| XLF-06-008 | 裸机、内核、驱动、嵌入式 | x-baremetal | EXPERIMENTAL·研究 | no_std 子集与模拟器测试 |
| XLF-06-009 | 中断、MMIO、RISC-V/x86 裸机目标 | x-codegen-baremetal | EXPERIMENTAL·研究 | ABI、volatile 与硬件实验 |
| XLF-06-010 | 多目标 Build Matrix/PAL | x-target、x-pal | EXTENDED·接受 | 目标能力矩阵 |
| XLF-06-011 | Agent 全场景脚手架 | x-templates、x-agent | EXPERIMENTAL·暂缓 | 模板签名与生成测试 |

## 8. `7.txt` 与 `8.txt`：前沿研究及现实化方案

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-07-001 | 因果回溯、确定性记录重演 | x-replay | RESEARCH·研究 | 可重放边界、开销和隐私报告 |
| XLF-07-002 | 增量内存快照 | x-snapshot | RESEARCH·研究 | Linux/Windows 原型与一致性测试 |
| XLF-07-003 | 能耗/碳感知调度 | x-energy | RESEARCH·重设计 | 仅提供观测和策略钩子，不自动跨中心迁移 |
| XLF-07-004 | 认知复杂度与重构建议 | x-lint-cognitive | EXTENDED·重设计 | 可配置 Lint；AI 建议不得自动提交 |
| XLF-07-005 | HLC 因果时间 | x-distributed-time | EXPERIMENTAL·研究 | 标准算法与分布式测试 |
| XLF-07-006 | Data Glacier/PMEM 持久变量 | x-pmem | RESEARCH·重设计 | 显式存储 API，不赋予普通变量隐式持久性 |
| XLF-07-007 | 后量子密码 | x-crypto-pqc | EXPERIMENTAL·暂缓 | 跟随 NIST 标准与独立审计 |
| XLF-07-008 | ZKP 闭包/电路后端 | x-codegen-zk | RESEARCH·研究 | 受限子集与证明系统审计 |
| XLF-07-009 | 空间锚点和 GPU 光线追踪 | x-spatial | RESEARCH·研究 | 坐标/设备/碰撞原型 |
| XLF-07-010 | 触觉与脑机接口 | x-hmi | RESEARCH·研究 | 设备适配、医疗安全和权限审查 |
| XLF-07-011 | 基因编程/策略搜索 | x-autotune | RESEARCH·重设计 | 仅沙箱产生候选，不自动合并生产代码 |
| XLF-07-012 | 混沌免疫与自修复 | x-resilience-lab | RESEARCH·重设计 | 建议/熔断策略；生产热补丁默认禁止 |
| XLF-07-013 | 法规注解和污点分析 | x-compliance-analysis | EXPERIMENTAL·重设计 | 规则包可审计；不宣称替代法律意见 |
| XLF-07-014 | 跨栈内存内省 | x-profiler-advanced | RESEARCH·研究 | 硬件能力、权限和数据开销报告 |
| XLF-07-015 | Omni-FFI | x-bindgen | EXPERIMENTAL·重设计 | C ABI 优先；C++/Python 按适配器处理 |
| XLF-07-016 | `.xbrain` 联邦项目记忆 | x-project-memory | RESEARCH·研究 | 本地优先、可删除、权限和版本控制 |
| XLF-07-017 | Living Docs | xdoc-test | EXTENDED·重设计 | 测试失败阻断；禁止自动篡改文档匹配错误代码 |
| XLF-07-018 | Intent/有界符号执行 | x-symbolic | RESEARCH·重设计 | 生成反例/候选实现，不承诺唯一算法或物理极限 |
| XLF-07-019 | eBPF 目标 | x-codegen-ebpf | EXPERIMENTAL·研究 | verifier、no_std 子集和内核版本矩阵 |

### 8.1 `8.txt` 现实化条目的来源别名

`8.txt` 是对 `7.txt` 脑洞需求的现实化改写，不新增重复功能 ID。下表逐项证明其 15 个实质主题均有规范 ID；实现时以 `8.txt` 的现实技术边界作为输入，但仍须重新验证其中的“100% 重现、固定微秒、自动消除”等绝对表述。

| `8.txt` 主题 | 规范功能 ID | 合并依据/现实化处置 |
|---|---|---|
| 因果回溯与确定性记录重演 | `XLF-07-001`、`XLF-07-002` | 拆为重演边界和增量快照；不保证所有外部非确定性均可捕获。 |
| HLC 标准库时间维度 | `XLF-07-005` | 改为显式库/协议能力，不为每个变量隐式追加时间戳。 |
| Data Glacier/PMEM | `XLF-07-006` | 改为显式持久存储 API；地址稳定和恢复延迟均需平台验证。 |
| RAPL/ACPI 能耗感知 | `XLF-07-003` | 先观测后策略；编译器不得在未授权时自动改变调度。 |
| GPU 空间光线追踪 | `XLF-07-009` | 归入 GPU/空间框架，不新增核心语法承诺。 |
| 后量子密码 | `XLF-07-007` | 跟随标准和算法迁移策略，不强制替换全部 TLS 套件。 |
| ZKP 受限后端 | `XLF-07-008` | 限制可编译子集，独立审计证明系统和密钥生命周期。 |
| 编译参数/策略搜索 | `XLF-07-011` | 只生成候选 Profile，不自动修改或合并业务逻辑。 |
| 熔断与混沌免疫 | `XLF-07-012` | 稳定韧性原语与自修复研究分层，生产热补丁默认禁止。 |
| 污点和合规分析 | `XLF-07-013` | 规则可审计且可配置，不声称替代法律判断。 |
| Living Docs/doc-test | `XLF-07-017` | 示例失败阻断；工具不得自动改文档来掩盖行为变化。 |
| `.xbrain` 项目记忆 | `XLF-07-016` | 本地优先、权限、可删除、数据来源和模型版本必须显式。 |
| Omni-FFI/绑定生成 | `XLF-07-015` | C ABI 优先；Python/C++ 分别处理对象布局、线程和版本风险。 |
| 受限符号执行 | `XLF-07-018` | 明确路径/时间预算和不完备性，不承诺自动生成唯一算法。 |
| eBPF 目标 | `XLF-07-019` | 使用 `no_std` 子集、Verifier 和内核版本矩阵。 |

## 9. `9.txt`：企业常用标准能力

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-09-001 | 编译期静态反射 | x-reflect | EXPERIMENTAL·研究 | 最小反射 RFC，避免泄漏布局 |
| XLF-09-002 | JSON/YAML/TOML/Protobuf/MessagePack | x-codec | EXTENDED·接受 | 格式互操作和流式测试 |
| XLF-09-003 | Schema Evolution | x-schema | EXTENDED·接受 | 前后兼容黄金测试 |
| XLF-09-004 | 结构化日志/OTLP | x-observability | EXTENDED·接受 | Schema、脱敏、互操作 |
| XLF-09-005 | Counter/Histogram/Gauge | x-metrics | EXTENDED·接受 | 并发、精度和开销基准 |
| XLF-09-006 | async Trace 自动上下文 | x-tracing | EXTENDED·重设计 | 显式 opt-in/属性，控制默认开销 |
| XLF-09-007 | 声明式 CLI 与配置层级 | x-cli-schema、x-config | EXTENDED·接受 | default→file→env→CLI 优先级测试 |
| XLF-09-008 | Fuzz/Property/Benchmark | x-test、x-fuzz、x-bench | CORE/EXTENDED·接受 | CI 与结果格式 |
| XLF-09-009 | Unicode、i18n 提取、复数/性别 | x-i18n | EXTENDED·接受 | CLDR/ICU 兼容测试 |
| XLF-09-010 | 2D 矢量和音视频编解码 | x-media | EXPERIMENTAL·暂缓 | 优先封装成熟库，许可证审计 |
| XLF-09-011 | 编译期 SQL 检查 | x-db | EXPERIMENTAL·研究 | 离线 Schema、迁移兼容 |
| XLF-09-012 | 异步连接池与迁移 | x-db | EXTENDED·接受 | 故障、事务和压力测试 |
| XLF-09-013 | Timer/Cron/Leader Election | x-scheduler-jobs | EXTENDED·接受 | 时区、漂移、幂等和故障测试 |
| XLF-09-014 | JWT/RBAC/Session | x-auth | EXTENDED·重设计 | 官方包，不作为语言内置；安全审计 |
| XLF-09-015 | 分布式构建缓存 | x-build-cache | EXTENDED·接受 | 内容寻址与污染防护 |
| XLF-09-016 | 二进制 `.xlib` 注册表 | x-registry | EXPERIMENTAL·重设计 | 来源证明、目标兼容和回退源码构建 |
| XLF-09-017 | PubGrub/SemVer 解析 | xpm-resolver | EXTENDED·接受 | 解析确定性与冲突解释 |

## 10. `10.txt`：语言人体工程、运维与生态

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-10-001 | 错误回溯和上下文链 | x-error、x-runtime | CORE/EXTENDED·接受 | 可配置捕获与开销测试 |
| XLF-10-002 | `defer` LIFO 清理 | 语言 RFC、x-lowering | EXPERIMENTAL·研究 | 与 RAII/return/panic 顺序测试 |
| XLF-10-003 | unwind/abort/no-exceptions | panic ABI、x-runtime | CORE/EXTENDED·接受 | 每种策略的清理与 ABI 测试 |
| XLF-10-004 | decimal32/64/128 | x-numeric-decimal | EXPERIMENTAL·研究 | IEEE 754-2008 符合性 |
| XLF-10-005 | 编译期正则/DFA | x-regex-compile | EXPERIMENTAL·研究 | 语义、代码体积和拒绝服务测试 |
| XLF-10-006 | Bitstream/Bitfield | x-bitfield | EXPERIMENTAL·研究 | 字节序、布局和协议黄金测试 |
| XLF-10-007 | 编译期 DI/Mock | x-test-mock | EXPERIMENTAL·重设计 | 库/代码生成优先，不污染 HIR 核心 |
| XLF-10-008 | 快照测试 | x-test-snapshot | EXTENDED·接受 | 审核式更新和稳定序列化 |
| XLF-10-009 | Stream/Generator/背压 | x-async-stream | EXTENDED·接受 | 状态机、取消和背压契约 |
| XLF-10-010 | Rc/Arc/Weak | x-std-memory | EXTENDED·接受 | 原子和生命周期测试 |
| XLF-10-011 | Cell/RefCell 内部可变性 | x-std-cell | EXTENDED·接受 | 动态借用冲突和线程限制 |
| XLF-10-012 | `build.x`、include、cfg | x-build-script、x-consteval | EXTENDED·重设计 | 沙箱、输入声明和可复现性 |
| XLF-10-013 | 信号和 Coredump 元数据 | x-os-signal、x-debug | EXTENDED·接受 | async-signal-safe 与调试器测试 |
| XLF-10-014 | 动态库、插件、符号版本 | x-plugin、x-ffi | EXTENDED·重设计 | 稳定 C ABI 子集和版本协商 |
| XLF-10-015 | C/Python/Node 绑定生成 | x-bindgen | EXPERIMENTAL·接受 | 所有权、错误和线程边界测试 |
| XLF-10-016 | SIMD、对齐、cache padding | x-simd | EXTENDED·接受 | ISA 回退与伪共享基准 |
| XLF-10-017 | xdoc 站点、依赖图、调用热图 | xdoc | EXTENDED·接受 | 可重复生成、链接和大项目性能 |
| XLF-10-018 | `x search` 符号/正则/语义搜索 | x-search、x-index | EXTENDED·接受 | 索引一致性和 CLI 契约 |

## 11. `11.txt`：治理、安全、调试与云原生

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-11-001 | SemVer API 差异发布门禁 | x-api-diff、xpm | EXTENDED·接受 | 破坏性变更测试 |
| XLF-11-002 | LTS 与发布节奏 | release governance | CORE治理·重设计 | 由资源/SLA 决定，不预设固定年限 |
| XLF-11-003 | `x rfc` 流程 | x-rfc、governance | EXTENDED·接受 | 模板、索引和审批状态机 |
| XLF-11-004 | SBOM/CVE/可复现构建 | x-supply-chain | CORE治理·接受 | CycloneDX/SPDX、审计和双构建 |
| XLF-11-005 | 管道、解构、命名/默认参数 | 语法 RFC、x-parser | SPLIT·解构为 CORE 候选，其余 1.0 后逐项研究 | 语法预算、求值顺序、格式化和兼容测试 |
| XLF-11-006 | 时间旅行调试 | x-replay | RESEARCH·研究 | RR/Intel PT 能力矩阵 |
| XLF-11-007 | Watch 与状态保持热重载 | x-watch、x-hot-reload | EXTENDED/EXPERIMENTAL·重设计 | Watch 先行；状态迁移独立 RFC |
| XLF-11-008 | 多调用约定 | x-ffi | EXTENDED·接受 | 平台 ABI 测试 |
| XLF-11-009 | C++ 名称修饰和模板互操作 | x-bindgen-cxx | EXPERIMENTAL·重设计 | libclang 生成 C shim，不承诺通用零拷贝 |
| XLF-11-010 | Serverless 快照启动 | x-serverless-snapshot | EXPERIMENTAL·研究 | 资源安全、连接重建和冷启动基准 |
| XLF-11-011 | FaaS 事件注解 | x-serverless-bindgen | EXPERIMENTAL·研究 | 云厂商适配器和生成代码审计 |
| XLF-11-012 | SpinLock/Fence/Atomic Ordering | x-std-atomic | EXTENDED·接受 | 内存模型和 loom 类测试 |
| XLF-11-013 | 错误码、`x explain`、Fix-it | x-diagnostics | CORE/EXTENDED·接受 | 离线文档和修复回归测试 |
| XLF-11-014 | `.x.tutor` 项目规则 | x-project-rules | EXPERIMENTAL·重设计 | 结构化规则、组织策略优先 |

## 12. `12.txt`：CLI、消息、ETL 与极限性能

| ID | 功能 | 目标项目/规范 | 分级·处置 | 验收证据 |
|---|---|---|---|---|
| XLF-12-001 | REPL/Readline/高亮/历史/自动导入 | x-repl | EXTENDED·接受 | 终端矩阵与交互测试 |
| XLF-12-002 | 彩色诊断和多进度条 | x-terminal、x-diagnostics | EXTENDED·接受 | TTY/非 TTY/无颜色测试 |
| XLF-12-003 | Shell 补全生成 | x-cli-schema | EXTENDED·接受 | bash/zsh/fish/PowerShell 黄金测试 |
| XLF-12-004 | Watch/守护热重启 | x-watch | EXTENDED·接受 | 文件事件合并与子进程清理 |
| XLF-12-005 | Pub/Sub 消息总线 | x-message-bus | EXTENDED·接受 | 进程内/IPC 契约测试 |
| XLF-12-006 | 共享内存 Ring Buffer 零拷贝 | x-ipc-ring | EXPERIMENTAL·研究 | 所有权、回压和崩溃测试 |
| XLF-12-007 | 持久消息与至少一次重放 | x-message-log | EXPERIMENTAL·研究 | 幂等、校验、恢复测试 |
| XLF-12-008 | Arrow/Parquet | x-data-columnar | EXTENDED·接受 | Arrow C Data 互操作 |
| XLF-12-009 | DataLoader 双缓冲 | x-data-loader | EXPERIMENTAL·接受 | I/O-计算重叠基准 |
| XLF-12-010 | 流式 JSON/CSV 反序列化 | x-codec-stream | EXTENDED·接受 | 有界内存和错误恢复测试 |
| XLF-12-011 | likely/unlikely 分支提示 | x-intrinsics | EXPERIMENTAL·研究 | 不改变语义；汇编和退化基准 |
| XLF-12-012 | 尾递归优化保证 | x-optimizer-tco | EXPERIMENTAL·研究 | 资格规则、诊断和栈测试 |
| XLF-12-013 | CPU affinity/NUMA | x-runtime-affinity | EXTENDED·接受 | 权限、回退和拓扑测试 |
| XLF-12-014 | no-exceptions | panic ABI、x-codegen | EXTENDED·接受 | 与 XLF-10-003 合并验收 |
| XLF-12-015 | 实时调度注解 | x-realtime | EXPERIMENTAL·研究 | 权限与 OS 能力矩阵，不承诺通用硬实时 |
| XLF-12-016 | 延迟预算与降级 | x-latency-contracts | EXPERIMENTAL·研究 | 计时开销和降级安全测试 |
| XLF-12-017 | Atomic<Option>/无锁热路径 | x-std-atomic | EXPERIMENTAL·研究 | 内存回收、ABA 和模型检查 |
| XLF-12-018 | `x env` 本地云环境 | x-environment | EXPERIMENTAL·重设计 | 只生成配置/短期凭据；禁止编译进二进制 |
| XLF-12-019 | 生产影子环境和远端日志 | x-dev-shadow | RESEARCH·重设计 | 默认隔离、脱敏、只读和审批 |
| XLF-12-020 | 性能基准承诺 | benchmark governance | CORE治理·重设计 | 历史数字全部降为候选基准 |

## 13. 价值回归复审摘要

87 个非直接接受项的 `RETURN/CONDITIONAL/SPLIT/RESEARCH` 结果、阶段和实现边界只在[《未纳入与偏离内容再审核及回归路线》](./X-Lang未纳入与偏离内容再审核及回归路线.md)维护；全局统计只在[总纲](./X-Lang企业级完整文档体系总纲.md)维护。本矩阵保留初审历史和来源，不复制复审明细。

## 14. 覆盖验收

- [ ] 每个 `XLF-*` 均链接到至少一个规范章节或 RFC。
- [ ] 每个 `接受/重设计` 功能均分配目标项目和负责人。
- [ ] 每个 `CORE/EXTENDED` 功能均有测试计划和目标版本。
- [ ] 每个 `EXPERIMENTAL/RESEARCH` 功能均有 Feature Gate、预算和退出条件。
- [ ] 每个危险原方案均保留需求、记录否决理由和安全替代，不静默删除。
- [ ] 每个 `RETURN/SPLIT` 回归部分均进入任务包；每个 `CONDITIONAL` 均有最迟决策阶段和 Go/No-Go 证据。
- [ ] 发布前生成 `功能 ID → 规范 → ADR/RFC → 代码模块 → 测试 → 版本` 双向报告。

当前矩阵完成了原始功能的“保留、处置和价值回归”基线；状态仍为草案，具体语义必须通过对应 RFC/ADR 后才能实现。
