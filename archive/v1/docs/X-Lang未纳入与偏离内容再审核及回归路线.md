> 已归档：见 v2 [docs/decisions/ADR-0003-scope-1.0-and-wedge.md](../../../docs/decisions/ADR-0003-scope-1.0-and-wedge.md)

# X-Lang 未纳入与偏离内容再审核及回归路线

> 总纲：[X-Lang 企业级完整文档体系总纲](./X-Lang企业级完整文档体系总纲.md)  
> 大纲版本：1.0-outline｜状态：复审路线已冻结｜复审基线：2026-08-15｜局部修订：2026-09-29（`XLF-10-002`→`CONDITIONAL`，ADR-0003 待审）
> 目的：对 164 个原始功能中 87 个“重设计、暂缓、研究或研究后接受”条目重新评估；凡有现实技术路径和明确用户价值者，默认回归实施。  
> 约束：[ADR-0003](./decisions/ADR-0003-p0-language-profile-and-labs-freeze.md) 仍为 Proposed，其新增剖面限制是待评审实施假设，不得声称已由 ADR 冻结；现有总纲与语言大纲的排除项仍有效；`RETURN` 不自动进入核心 Workspace，也不能阻塞 [P0 纵向切片](./design/p0-vertical-slice.md)。

## 1. 复审结论与优先规则

本文件是第二轮架构复审结论。原矩阵的处置用于保存第一次审查历史；若两者冲突，以本文件的“复审结论”作为后续路线、任务拆分和资源评估依据。回归实现不等于立即承诺稳定，也不等于把能力塞入核心语法。

| 复审代码 | 含义 | 工程要求 |
|---|---|---|
| `RETURN` | 技术成熟且价值明确，回归正式实施路线 | 必须进入 P0-P5 的任务包、物理项目、测试与文档，不再只停留在研究清单。 |
| `CONDITIONAL` | 可实现但依赖核心稳定、平台/硬件、标准或重大原型 | 立即做 RFC/探针/接口骨架；满足门禁后转 `RETURN`，不得无限期搁置。 |
| `SPLIT` | 需求中包含可落地部分和不可接受的自动/隐式部分 | 可落地部分回归实施；危险机制明确排除，不能以排除局部为由丢弃整体价值。 |
| `RESEARCH` | 现阶段缺少成熟技术、成本极高或安全责任不可控 | 独立 Labs 项目、预算和退出条件；不得阻塞主线。 |
| `REJECT-MECHANISM` | 只否决特定实现机制，不否决用户价值 | 必须同时记录替代方案；禁止仅写“太难”而无证据。 |

默认判断顺序：复用成熟标准/库 → 官方适配层 → 独立框架 → 实验后端 → 研究项目。只有跨越停机问题、依赖未普及硬件、涉及医疗/生命安全、要求通用形式化证明或允许无人监管修改生产系统时，才保留为研究或排除机制。

## 2. `1.txt` 与 `2.txt`：核心路线、工具和内存

| ID | 能力 | 复审结论 | 回归阶段与实施边界 |
|---|---|---|---|
| XLF-01-005 | WASM 与交叉编译 | `RETURN` | P3 仅做 WASI/Component Model 后端探针和通用交叉编译闭环；P5 再稳定 WASM 平台、浏览器宿主与 Web 工具链，不等待移动端。 |
| XLF-01-007 | 无 GC 核心模式 | `RETURN` | P0-P2 正式冻结所有权+RAII+无隐式 GC；该目标不再只是“冲突处理”。 |
| XLF-01-008 | Comptime 与零成本抽象 | `RETURN` | P2 实施受限常量解释、资源预算、缓存和诊断；“零成本”改为可验证降级。 |
| XLF-01-012 | 声明式跨平台 UI | `CONDITIONAL` | P3 定义 UI Tree/状态/事件契约，P5 实现 Web/桌面/移动适配；不进入核心关键字。 |
| XLF-01-015 | 分阶段路线与最终自举 | `RETURN` | P4 后启动三阶段 bootstrap；先交付自托管子集和可复现验证，不要求 1.0 首日自举。 |
| XLF-02-006 | tree-sitter 增量解析候选 | `RETURN` | P1 做共享 Parser 与 tree-sitter 语法生成/差分探针；ADR 决定编辑器是否采用，不另造语义。 |
| XLF-02-008 | IntelliJ Grammar-Kit/JFlex/PSI | `RETURN` | P3 先共享 LSP，必要功能用轻 PSI/索引补齐；保留 JetBrains 原生体验。 |
| XLF-02-010 | RAII + 可选 GC | `CONDITIONAL` | P6 做隔离 Managed Heap/FFI 原型；必须显式类型/区域、可关闭且不改变 CORE 默认语义。 |

## 3. `3.txt`：契约、Effect 和 AI 开发体验

| ID | 能力 | 复审结论 | 回归阶段与实施边界 |
|---|---|---|---|
| XLF-03-001 | `#spec` 显式契约 | `RETURN` | P2 先实现前置/后置/不变量及 Debug/Release 策略，P3 接属性测试与静态分析。 |
| XLF-03-002 | `#example` 自然语言/示例测试 | `SPLIT` | 可执行示例和 doc-test 在 P2 实现；自然语言只作说明，不作为编译语义。 |
| XLF-03-003 | `pure` 与确定性标记 | `RETURN` | P2 提供保守 Effect 检查和逃逸诊断，P3 供优化/并发/Agent 使用；不宣称完整效果证明。 |
| XLF-03-008 | AI IDE 协驾驶面板 | `RETURN` | P3 交付可关闭插件、上下文预览、权限和 diff；模型供应商通过适配器解耦。 |
| XLF-03-011 | 模板市场 | `RETURN` | P3 建签名模板、审核、版本、撤回和离线镜像；模板执行默认沙箱。 |

## 4. `4.txt`：Tensor、自动微分、GPU 与训练平台

| ID | 能力 | 复审结论 | 回归阶段与实施边界 |
|---|---|---|---|
| XLF-04-001 | Tensor 类型与 Shape 推导 | `RETURN` | P3 建独立 `x-tensor` 和 Shape/Device/Layout 类型；编译期静态 Shape 与运行时动态 Shape 并存。 |
| XLF-04-002 | 编译期自动微分 | `CONDITIONAL` | P4 先做独立 Autograd Tape，P5 再验证 MIR/图级 AD；数值梯度对照和不可微诊断是门禁。 |
| XLF-04-003 | CUDA/ROCm/Metal Kernel 生成 | `CONDITIONAL` | P4 冻结设备 IR 和 CPU 回退，P5 分别接入后端；不要求首版三后端完全等价。 |
| XLF-04-004 | 静态计算图优化与自动并行 | `RETURN` | P4 实施独立图 IR、融合、布局和调度 Pass；每个 Pass 有等价验证和关闭开关。 |
| XLF-04-005 | LoRA/QLoRA Adapter 注入 | `RETURN` | P5 基于成熟模型格式和框架互操作实现，不进入语言语法。 |
| XLF-04-006 | 量化、混合精度和分布式训练 | `CONDITIONAL` | 量化/混合精度 P4 回归；分布式训练 P5 依赖通信、容错和数值一致性门禁。 |
| XLF-04-009 | Protocol as Type | `CONDITIONAL` | P3 先交付库级类型状态机/代码生成，P6 再评估语言级 Session Type；避免扩大核心求解器。 |
| XLF-04-010 | 训练即服务 | `RETURN` | P5 实现鉴权、队列、配额、检查点、模型注册和可观测 API；复用容器/调度基础设施。 |
| XLF-04-012 | `x agent train/finetune/serve` | `RETURN` | P5 作为对训练服务的可审计 CLI 编排；不在本地 CLI 隐式取得云权限。 |

## 5. `5.txt` 与 `6.txt`：系统、桌面、移动和嵌入式

| ID | 能力 | 复审结论 | 回归阶段与实施边界 |
|---|---|---|---|
| XLF-05-003 | fork/exec 安全封装 | `RETURN` | P2 交付跨平台 Process API；Unix `fork` 限定 unsafe/单线程规则，Windows 用 CreateProcess 适配。 |
| XLF-05-006 | 原始指针与 Ghost Memory 调试 | `SPLIT` | 原始指针/unsafe 规范 P2；Poison/Guard Page/ASan/MIR UB 检查 P3；不伪装成零开销语义。 |
| XLF-05-007 | CPU/GPU 统一内存 | `CONDITIONAL` | P5 以显式 ManagedBuffer、同步和迁移 API 实施；无硬件支持时回退复制，不承诺地址透明。 |
| XLF-05-010 | mmap 智能预取 | `RETURN` | P3 提供显式 hint、观测和自适应策略；默认策略可关闭且必须有退化检测。 |
| XLF-05-011 | AI 系统操作命令 | `SPLIT` | P3 实现计划生成、Dry-run、策略检查和审批；拒绝 Agent 默认提权或绕过 OS 权限。 |
| XLF-06-001 | 分层渲染引擎与声明式 UI | `RETURN` | P3 冻结 UI/Render/Platform 边界，P5 交付至少 Web 与一个桌面后端。 |
| XLF-06-002 | Windows/macOS/Linux 桌面 | `CONDITIONAL` | P5 逐平台 Tier 晋级；先 Windows/Linux，再 macOS 签名公证，均需真机打包测试。 |
| XLF-06-003 | Skia、WebView、托盘和快捷键 | `RETURN` | P5 作为可替换适配器实施；Skia/WebView 版本、许可证和安全更新独立管理。 |
| XLF-06-004 | Android/iOS 原生库和薄胶水 | `CONDITIONAL` | P5 先交付静态/动态库、JNI/Swift bridge 和最小示例，再扩 UI。 |
| XLF-06-005 | Metal/Vulkan、触控与传感器 | `CONDITIONAL` | P5 分平台能力探测、权限和生命周期；无能力时有降级诊断。 |
| XLF-06-006 | 小程序 WASM 逻辑和模板转译 | `CONDITIONAL` | P6 建厂商适配器和生成器；因平台规则变化快，独立版本且不承诺统一行为。 |
| XLF-06-007 | 服务端 HTTP3/gRPC/AI 推理 | `RETURN` | HTTP/gRPC P3-P4，HTTP/3/QUIC 与推理 P5；协议互操作优先于自研协议栈。 |
| XLF-06-008 | 裸机、内核、驱动、嵌入式 | `CONDITIONAL` | P4 冻结 `no_std`/panic/allocator 子集，P5 先 QEMU+开发板，再评估内核驱动。 |
| XLF-06-009 | 中断、MMIO、RISC-V/x86 裸机目标 | `CONDITIONAL` | P5 实施 volatile、对齐、链接脚本、启动和中断 ABI；硬件在环后晋级。 |
| XLF-06-011 | Agent 全场景脚手架 | `RETURN` | P3-P5 按 CLI/Web/服务/ML/嵌入式分别交付签名模板，禁止万能模板隐藏安全选择。 |

## 6. `7.txt` 与 `8.txt`：前沿能力现实化回归

| ID | 能力 | 复审结论 | 回归阶段与实施边界 |
|---|---|---|---|
| XLF-07-001 | 因果回溯、确定性记录重演 | `CONDITIONAL` | P5 先记录外部输入、调度事件和重放受限程序；明确不可捕获源，不宣称通用 100% 重现。 |
| XLF-07-002 | 增量内存快照 | `CONDITIONAL` | P4 接入 OS Snapshot/Core/Minidump，P5 做脏页增量；隐私、停顿和保留策略前置。 |
| XLF-07-003 | 能耗/碳感知调度 | `SPLIT` | P4 回归功耗观测、策略 API 和离线调度；拒绝编译器未经授权自动跨数据中心迁移。 |
| XLF-07-004 | 认知复杂度与重构建议 | `RETURN` | P3 交付稳定 Lint ID、阈值配置、Fix-it/AI 候选和抑制机制。 |
| XLF-07-005 | HLC 因果时间 | `RETURN` | P3 在分布式时间/消息库实现标准 HLC；显式传播，不给所有变量隐式增加字段。 |
| XLF-07-006 | Data Glacier/PMEM 持久变量 | `SPLIT` | P5 回归显式 PMEM/对象存储事务 API；拒绝普通变量隐式持久化和跨重启裸地址保证。 |
| XLF-07-007 | 后量子密码 | `RETURN` | P4 采用 NIST 标准算法/成熟 Provider，支持算法协商和迁移；独立审计后晋级。 |
| XLF-07-008 | ZKP 闭包/电路后端 | `RESEARCH` | P6 只实现受限纯函数→电路原型、约束计数和审计；通用程序降级仍属高难研究。 |
| XLF-07-009 | 空间锚点和 GPU 光线追踪 | `CONDITIONAL` | P5 先以框架 API 接 Vulkan/DXR/Metal 和 OpenXR；核心语言不新增空间关键字。 |
| XLF-07-010 | 触觉与脑机接口 | `SPLIT` | P5 回归通用 HID/触觉/传感器适配；侵入式脑机和医疗控制保留 `RESEARCH` 并要求伦理/法规审批。 |
| XLF-07-011 | 基因编程/策略搜索 | `SPLIT` | P4 回归 PGO/贝叶斯参数搜索和候选 Profile；拒绝自动修改业务逻辑及自动合并生产分支。 |
| XLF-07-012 | 混沌免疫与自修复 | `SPLIT` | P4 回归熔断、退避、隔离、故障注入和修复建议；拒绝无人审批的生产热补丁。 |
| XLF-07-013 | 法规注解和污点分析 | `RETURN` | P3 建可审计规则包、Source/Sink、跨过程污点和误报抑制；声明不是法律意见。 |
| XLF-07-014 | 跨栈内存内省 | `CONDITIONAL` | P4 统一 Core/Heap/Task/Perf/ETW/eBPF 适配；硬件缺失时降级，不承诺无停顿。 |
| XLF-07-015 | Omni-FFI | `SPLIT` | P3-P5 回归 C/Python/JNI/JS/有限 C++ 绑定；拒绝任意 ABI、任意对象和普遍零拷贝承诺。 |
| XLF-07-016 | `.xbrain` 联邦项目记忆 | `RETURN` | P4 实现本地索引、来源、版本、权限、导出和遗忘；联邦同步必须 opt-in。 |
| XLF-07-017 | Living Docs | `RETURN` | P2 实施 doc-test、链接/API/示例同步和版本站点；禁止自动改文档以迎合错误实现。 |
| XLF-07-018 | Intent/有界符号执行 | `SPLIT` | P5 实现预算化符号执行、反例和有限代码候选；拒绝通用自动算法生成与物理极限承诺。 |
| XLF-07-019 | eBPF 目标 | `CONDITIONAL` | P4 冻结受限 `no_std` 子集，P5 实现 LLVM BPF、Verifier 诊断、CO-RE/BTF 和内核矩阵。 |

## 7. `9.txt` 与 `10.txt`：企业库与语言人体工程

| ID | 能力 | 复审结论 | 回归阶段与实施边界 |
|---|---|---|---|
| XLF-09-001 | 编译期静态反射 | `RETURN` | P2 实现受限类型/字段/属性查询和派生代码生成；运行时元数据显式保留。 |
| XLF-09-006 | async Trace 自动上下文 | `RETURN` | P3 在 Task/Channel/HTTP 边界传播 Trace Context；默认策略和采样开销可配置。 |
| XLF-09-010 | 2D 矢量和音视频编解码 | `RETURN` | P5 优先封装 Skia/FFmpeg 等成熟库，建立许可证、漏洞和版本矩阵。 |
| XLF-09-011 | 编译期 SQL 检查 | `RETURN` | P3 实施离线 Schema 快照、参数/结果类型检查、迁移兼容和无数据库 CI。 |
| XLF-09-014 | JWT/RBAC/Session | `RETURN` | P3 作为官方安全包实现，不放入语言内置；默认算法、轮换、撤销和审计齐全。 |
| XLF-09-016 | 二进制 `.xlib` 注册表 | `CONDITIONAL` | P4 先发布源码包+签名，二进制包仅对明确 Target/ABI/工具链指纹命中，失败回退源码构建。 |
| XLF-10-002 | `defer` LIFO 清理 | `CONDITIONAL` | **P0–P4 / 1.0 不实现**（总纲 §12 的既有范围约束；[ADR-0003](./decisions/ADR-0003-p0-language-profile-and-labs-freeze.md) 尚待接受）。仅当 Drop/panic 模型 Stable 后，经独立 RFC 证明无双重释放与可测试顺序，方可进入 **1.0 之后 Edition** 候选；此前语法必须拒绝或 `X-E9001`。 |
| XLF-10-004 | decimal32/64/128 | `RETURN` | P3 先库类型和软件实现，硬件支持通过能力探测；符合 IEEE 754 十进制语义。 |
| XLF-10-005 | 编译期正则/DFA | `RETURN` | P3 受限常量模式编译、大小预算和运行时回退；防止代码膨胀与 ReDoS。 |
| XLF-10-006 | Bitstream/Bitfield | `RETURN` | P2-P3 以显式字节序、位序、布局和协议黄金测试实施。 |
| XLF-10-007 | 编译期 DI/Mock | `RETURN` | P3 以 Trait、代码生成和测试库实现，不向 HIR 引入 DI 容器语义。 |
| XLF-10-012 | `build.x`、include、cfg | `SPLIT` | P2-P3 回归声明式 cfg/include 和沙箱构建脚本；拒绝未声明网络/文件/环境输入。 |
| XLF-10-014 | 动态库、插件、符号版本 | `RETURN` | P3 基于稳定 C ABI、句柄和版本协商实施；进程外插件作为不可信默认。 |

## 8. `11.txt` 与 `12.txt`：治理、调试、实时和极限性能

| ID | 能力 | 复审结论 | 回归阶段与实施边界 |
|---|---|---|---|
| XLF-11-002 | LTS 与发布节奏 | `RETURN` | P3 起定义 Nightly/Beta/Stable，P4 决定 LTS 人力/SLA/补丁政策；不预写无法保障的年限。 |
| XLF-11-005 | 管道、解构、命名/默认参数 | `SPLIT` | P1-P2 只回归有限解构；管道、命名/默认参数延期至 1.0 后逐项 RFC，不能因原始材料提及而整体进入核心。 |
| XLF-11-006 | 时间旅行调试 | `CONDITIONAL` | P5 在受支持 OS 上组合 Replay、Snapshot、Intel PT/ETW；能力探测和开销预算公开。 |
| XLF-11-007 | Watch 与状态保持热重载 | `SPLIT` | P2 Watch/进程重启回归实施；P5 状态迁移只支持版本化 Schema 和可回滚边界。 |
| XLF-11-009 | C++ 名称修饰和模板互操作 | `SPLIT` | P4 回归 libclang+C Shim+常见 STL 适配；拒绝通用 C++ ABI 和任意模板自动零拷贝。 |
| XLF-11-010 | Serverless 快照启动 | `CONDITIONAL` | P5 实现无连接资源的初始化快照、恢复 Hook 和基准；密钥/Socket/线程不得直接冻结。 |
| XLF-11-011 | FaaS 事件注解 | `RETURN` | P5 通过厂商无关事件 Schema 和适配器生成代码；生成物可审查、可离线测试。 |
| XLF-11-014 | `.x.tutor` 项目规则 | `RETURN` | P3 采用结构化 `rules.toml`、Schema、继承和组织策略上限；规则变更有审计。 |
| XLF-12-006 | 共享内存 Ring Buffer 零拷贝 | `RETURN` | P3 实施 SPSC/MPSC 明确变体、所有权转移、回压、崩溃恢复和跨进程测试。 |
| XLF-12-007 | 持久消息与至少一次重放 | `RETURN` | P3 实施日志格式、校验、幂等键、截断/恢复和 Schema 版本；不冒充 exactly-once。 |
| XLF-12-011 | likely/unlikely 分支提示 | `RETURN` | P2 作为不改变语义的 Hint 实施，诊断滥用并用汇编/基准验证。 |
| XLF-12-012 | 尾递归优化保证 | `SPLIT` | P2 对满足资格的自尾调用提供保证/诊断；互递归和复杂析构先作为优化，不作普遍保证。 |
| XLF-12-015 | 实时调度注解 | `SPLIT` | P4 回归软实时预算、优先级和能力查询；通用硬实时保证保留研究，需 RTOS/内核/硬件证据。 |
| XLF-12-016 | 延迟预算与降级 | `RETURN` | P4 实现结构化 Deadline/Budget/Cancel、可观察降级和策略测试。 |
| XLF-12-017 | `Atomic<Option>`/无锁热路径 | `CONDITIONAL` | P3 提供安全原子组合，P4 经 Loom/模型检查、ABA 和内存回收验证后稳定。 |
| XLF-12-018 | `x env` 本地云环境 | `RETURN` | P3 实现配置生成、短期凭据引用、容器/模拟器和销毁；秘密不得编译进二进制。 |
| XLF-12-019 | 生产影子环境和远端日志 | `SPLIT` | P5 回归脱敏、采样、只读回放和审批；拒绝默认复制生产秘密和写流量。 |
| XLF-12-020 | 性能基准承诺 | `RETURN` | P0 建基准治理，P1 起形成版本化基线；只有可复现数据才升级为支持目标。 |

## 9. 明确排除的机制，而非排除的价值

以下机制不进入稳定实现；其对应价值已经由上表中的替代方案保留。

| 排除机制 | 原因 | 保留的替代价值 |
|---|---|---|
| 编译器静默自动插锁 | 改变并发语义，可能引入死锁和不可预测尾延迟 | 所有权/数据竞争检查、显式锁、Channel、Actor、结构化并发。 |
| 普通变量隐式持久化及跨重启裸地址稳定 | 崩溃一致性、Schema 和设备差异无法隐藏 | 显式 PMEM/对象存储事务和迁移。 |
| 任意 C++/Python/JS 对象自动零拷贝 | ABI、布局、GC/引用和线程模型不兼容 | 分语言 SDK、Buffer/DLPack、句柄和生成 C Shim。 |
| 无人审批自动修改业务逻辑或生产热补丁 | 供应链、安全、责任和回滚风险不可接受 | 候选补丁、diff、测试、灰度、审批和自动回滚。 |
| 通用程序 100% 确定性重放 | 外设、竞态、内核和外部系统不可完全捕获 | 明确支持边界的输入记录、调度日志、快照和硬件 Trace。 |
| 任意程序自动生成唯一最优算法 | 停机问题、搜索空间和规格不完备 | 有界符号执行、反例、有限领域代码候选和自动调优。 |
| 所有平台通用硬实时保证 | OS、调度器、驱动和硬件不可控 | 软实时契约；特定 RTOS/硬件的认证子集。 |
| 侵入式脑机/医疗控制直接作为通用标准库 | 医疗安全、伦理和法规责任远超语言核心 | 通用 HID/触觉/传感器接口；医疗适配独立研究和认证。 |

## 10. 回归实施门禁

每项 `RETURN` 或 `SPLIT` 的回归部分必须满足：有规范/RFC、物理项目、负责人角色、输入输出契约、依赖、威胁模型、测试、平台矩阵、性能预算、迁移和回滚。`CONDITIONAL` 必须在目标阶段前至少完成探针和 Go/No-Go ADR，连续两个里程碑无证据则重新评审，不允许永久挂起。

验收链统一为：`原始文件 → XLF → 本复审结论 → 规范规则 → 工程任务 → 物理项目 → 测试/基准/审计 → 发布状态`。
