# 原始需求登记册（生成物）

> 类型：Register｜**由 `tools/doccheck.py` 从 [registry.yaml](registry.yaml) 生成，请勿手改。** 字段含义见 [vision](../vision.md) §5–6；阶段定义见 [roadmap](../roadmap.md)。

## 1. 统计

- 总数：168
- 轨道：core 50 ｜ toolchain 45 ｜ eco 66 ｜ labs 7
- 处置：adopt 80 ｜ adapt 60 ｜ replace 24 ｜ research 4
- 首次交付阶段：M0 2 ｜ P0 15 ｜ P1 11 ｜ P2 27 ｜ P3 43 ｜ P4 21 ｜ P5 43 ｜ R 6

## 2. 不可行或不进核心条目（replace / research）及理由

| ID | 原始诉求 | 处置 | 替代落点 | 理由 / 说明 |
|---|---|---|---|---|
| XLF-01-012 | 声明式跨平台 UI | replace | XUI 库（View/UiIr/Capability）：P3 原型，P4 Web 样例，P5 桌面/移动 | UI 不进入核心语法；只承诺语义一致，不承诺像素一致 |
| XLF-02-010 | RAII + 可选 GC | replace | 共享所有权用 Rc/Arc/Weak；可选 GC 仅研究赛道 | GC 与“无隐式 GC”核心目标冲突 |
| XLF-03-002 | `#example` 自然语言/示例测试 | replace | doc-test：/// 中代码块编译运行 | 自然语言示例不进入编译语义 |
| XLF-04-001 | Tensor 类型与 Shape 推导 | replace | x-tensor 库：运行时 Shape；静态维度待 const 泛型评估 | 语言不内建 Tensor；成本为编译器级 ML 系统 |
| XLF-04-002 | 编译期自动微分 | replace | 库级 Tape Autograd；编译期 AD 为研究项 | 编译期 AD 需要宏或编译器插件，1.0 不提供；库级实现已能满足训练原型 |
| XLF-04-003 | CUDA/ROCm/Metal Kernel 生成 | replace | 经 FFI 调用成熟内核库/运行时；自研 Kernel 生成为研究项 | 三后端 Kernel 生成超出团队规模 |
| XLF-04-004 | 静态计算图优化与自动并行 | replace | 导出 ONNX 交给成熟图编译器 | 自动并行属研究 |
| XLF-04-005 | LoRA/QLoRA Adapter 注入 | replace | 经 Python 互操作调用成熟微调框架 | 不进入语言语法 |
| XLF-04-006 | 量化、混合精度和分布式训练 | replace | 经互操作使用成熟量化/分布式训练框架 | 自研分布式训练栈超出团队规模；复用成熟框架的成本最低 |
| XLF-04-010 | 训练即服务 | replace | x-ai-tools 编排外部训练服务 | 复用现有调度基础设施 |
| XLF-04-012 | `x agent train/finetune/serve` | replace | x-ai-tools train/serve 子命令编排外部服务 | 不隐式获取云权限 |
| XLF-05-007 | CPU/GPU 统一内存 | replace | 显式 ManagedBuffer + 同步/迁移 API | 不承诺 CPU/GPU 同一指针类型 |
| XLF-05-010 | mmap 智能预取 | replace | x-mmap 显式 madvise hint；自适应预取为研究项 | “智能”预取的收益依赖负载，无法给出通用保证；显式 hint 行为可预期 |
| XLF-06-006 | 小程序 WASM 逻辑和模板转译 | research | 实验：JS 胶水 + WASM 逻辑包（平台支持时） | 平台规则变化快；模板转译不作通用承诺 |
| XLF-07-006 | Data Glacier/PMEM 持久变量 | replace | 显式持久化事务库（PMEM/对象存储） | 普通变量不隐式持久化 |
| XLF-07-008 | ZKP 闭包/电路后端 | research | 与外部电路 DSL 互操作研究 | 通用程序转电路属研究 |
| XLF-07-009 | 空间锚点和 GPU 光线追踪 | replace | 图形/XR 绑定库（Vulkan/DXR/Metal/OpenXR） | 核心不加空间关键字 |
| XLF-07-010 | 触觉与脑机接口 | replace | HID/触觉/传感器适配；脑机接口为研究项 | 需伦理/法规审批 |
| XLF-07-011 | 基因编程/策略搜索 | replace | PGO + x tune 参数搜索（只调参数） | 拒绝自动改业务逻辑 |
| XLF-07-012 | 混沌免疫与自修复 | replace | 熔断/重试/隔离/故障注入库 | 拒绝无人审批热补丁 |
| XLF-07-018 | Intent/有界符号执行 | research | x verify：有界模型检查实验（外部 SMT） | 拒绝通用算法生成 |
| XLF-09-010 | 2D 矢量和音视频编解码 | replace | 绑定 Skia/FFmpeg 等成熟库 | 许可证/漏洞矩阵独立管理 |
| XLF-10-005 | 编译期正则/DFA | replace | x-regex 运行时编译 + 缓存；编译期 DFA 待 const 能力 | 防 ReDoS：线性时间引擎 |
| XLF-10-007 | 编译期 DI/Mock | replace | Trait + 测试替身库 | 不在 HIR 引入 DI 容器 |
| XLF-11-009 | C++ 名称修饰和模板互操作 | replace | C shim + bindgen 适配常见 C++ | 不承诺通用 C++ ABI |
| XLF-11-010 | Serverless 快照启动 | replace | 启动优化 + 平台快照能力适配 | 密钥/Socket 不得冻结 |
| XLF-12-019 | 生产影子环境和远端日志 | research | 脱敏只读流量回放研究 | 拒绝默认复制生产数据 |
| XLF-12-020 | 性能基准承诺 | replace | docs/performance.md 可测目标 + 版本化基准 | 原文数值无环境与对照，不作承诺 |

## 3. 全量表

| ID | 标题 | 来源 | 轨道 | 阶段 | 完成 | 处置 | 落点 | 说明 |
|---|---|---|---|---|---|---|---|---|
| XLF-01-001 | 可插拔三段式编译器 | 1.txt | core | P0 | P1 | adopt | 编译器分层管线：前端/中端/后端以 Codegen Trait 解耦 | — |
| XLF-01-002 | Lexer/Parser/Semantic→HIR | 1.txt | core | P0 | P1 | adopt | Lexer→无损 CST→AST→HIR（名称解析） | — |
| XLF-01-003 | HIR 平台无关优化→MIR/LIR | 1.txt | core | P1 | P3 | adopt | MIR 平台无关优化 Pass；P1 基础 Pass，P3 增强 | 原文 LIR 统一命名为 MIR |
| XLF-01-004 | LLVM 原生后端 | 1.txt | core | P0 | P4 | adopt | LLVM 后端（ADR-0001），Tier 1 目标 | — |
| XLF-01-005 | WASM 与交叉编译 | 1.txt | core | P3 | P5 | adapt | P3 交叉编译闭环与 wasm32-wasip2 探针；P5 WASM 升 Tier 2 | WASM 依赖 std/PAL 成熟，不进 P0–P2 |
| XLF-01-006 | 所有权、借用、生命周期 | 1.txt | core | P1 | P2 | adapt | P1 受限借用检查，P2 完整 NLL；1.0 采用隐式区域策略 | 1.0 无显式生命周期语法，见 specs/language/04 |
| XLF-01-007 | 无 GC 核心模式 | 1.txt | core | P0 | P2 | adopt | 所有权 + RAII，无隐式 GC | — |
| XLF-01-008 | Comptime 与零成本抽象 | 1.txt | core | P2 | P4 | adapt | const/static 初始化与 const fn 由 MIR 解释器求值，带资源预算 | 通用 comptime 进入研究赛道 |
| XLF-01-009 | 协程、CSP、Channel | 1.txt | core | P2 | P5 | adapt | 1.0：作用域线程 + 通道（CSP 风格）；P5：async/await Edition + M:N 执行器 | async 与所有权/取消/FFI 交织，1.0 前不承诺 |
| XLF-01-010 | 简洁、显式、OOP+FP 表达力 | 1.txt | core | P1 | P2 | adopt | struct/enum/impl/trait/闭包/模式匹配；无继承、无重载 | — |
| XLF-01-011 | 跨平台标准库 | 1.txt | core | P1 | P4 | adopt | core→alloc→std 分层 + PAL，Tier 矩阵见 platforms | — |
| XLF-01-012 | 声明式跨平台 UI | 1.txt | eco | P3 | P5 | replace | XUI 库（View/UiIr/Capability）：P3 原型，P4 Web 样例，P5 桌面/移动 | UI 不进入核心语法；只承诺语义一致，不承诺像素一致 |
| XLF-01-013 | 包管理、构建、LSP、格式化一体化 | 1.txt | toolchain | P0 | P3 | adopt | 单一 x 二进制：check/build/run/test/fmt → xpm → LSP | — |
| XLF-01-014 | IDE、增量/并行编译 | 1.txt | toolchain | P1 | P3 | adopt | P1 查询式 Driver（内存缓存），P3 落盘增量 + LSP | — |
| XLF-01-015 | 分阶段路线与最终自举 | 1.txt | core | P5 | P5 | adapt | 1.0 后启动自举；保留 Rust 实现为 bootstrap 编译器 | 自举不是 1.0 门禁 |
| XLF-02-001 | 编译器+LSP+IDE+运行时四层架构 | 2.txt | core | P0 | P3 | adopt | 编译器/工具链/运行时/编辑器四层，见 architecture | — |
| XLF-02-002 | Token/AST/HIR/LIR/LLVM 全流水线 | 2.txt | core | P0 | P1 | adopt | Token→CST→AST→HIR→MIR→LLVM | 原文 LIR 统一为 MIR |
| XLF-02-003 | Rust 初始实现与自举 | 2.txt | core | M0 | P5 | adopt | Rust 宿主实现（ADR-0001）；自举见 XLF-01-015 | — |
| XLF-02-004 | 增量、并行编译与彩色诊断 | 2.txt | toolchain | P0 | P3 | adopt | P0 彩色诊断；P1 查询骨架与并行编译；P3 落盘增量 | — |
| XLF-02-005 | LSP 分析、补全、导航、格式化、诊断 | 2.txt | toolchain | P3 | P4 | adopt | x lsp：诊断/补全/跳转/重命名/格式化 | — |
| XLF-02-006 | tree-sitter 增量解析候选 | 2.txt | toolchain | P3 | P4 | adapt | 从规范文法生成 tree-sitter 语法，仅用于高亮/编辑器结构 | 语义只来自编译器查询，不造第二套解析语义 |
| XLF-02-007 | VS Code + TextMate + DAP | 2.txt | toolchain | P3 | P4 | adopt | VS Code 扩展（TextMate/tree-sitter 高亮 + LSP + DAP） | — |
| XLF-02-008 | IntelliJ Grammar-Kit/JFlex/PSI | 2.txt | eco | P5 | P5 | adapt | IntelliJ 插件经平台 LSP 支持接入 x lsp | 不实现 Grammar-Kit/JFlex 第二套 Parser |
| XLF-02-009 | XRT 内存、协程、I/O、标准库 | 2.txt | core | P0 | P5 | adapt | xrt 最小运行时（启动/panic/分配/线程）；协程运行时 P5 | — |
| XLF-02-010 | RAII + 可选 GC | 2.txt | labs | R | R | replace | 共享所有权用 Rc/Arc/Weak；可选 GC 仅研究赛道 | GC 与“无隐式 GC”核心目标冲突 |
| XLF-02-011 | C ABI FFI | 2.txt | core | P1 | P2 | adopt | extern "C" 调用与导出、@repr(C) | — |
| XLF-02-012 | 正式语法规范与示例 | 2.txt | core | P0 | P2 | adopt | specs/language 规范 + 机器可读文法 | — |
| XLF-02-013 | 标准用户项目结构和 `x.toml` | 2.txt | toolchain | P1 | P2 | adopt | 标准项目结构 + x.toml（specs/packages） | — |
| XLF-02-014 | build/run/test/fmt/check/doc/publish 命令 | 2.txt | toolchain | P0 | P4 | adopt | P0 check/build/run；P1 test/fmt；P3 doc；P4 publish | — |
| XLF-02-015 | 调试与性能分析 | 2.txt | toolchain | P2 | P4 | adopt | P2 DWARF/PDB 行表；P3 x debug(DAP)；P4 x prof 集成 | — |
| XLF-03-001 | `#spec` 显式契约 | 3.txt | core | P2 | P5 | adapt | 1.0 前：assert + doc-test；1.0 后 Edition 候选：可执行契约 @requires/@ensures | ADR-0003：1.0 不扩核心语法 |
| XLF-03-002 | `#example` 自然语言/示例测试 | 3.txt | toolchain | P2 | P2 | replace | doc-test：/// 中代码块编译运行 | 自然语言示例不进入编译语义 |
| XLF-03-003 | `pure` 与确定性标记 | 3.txt | labs | P3 | R | adapt | P3 x vet 副作用启发式报告；Effect 系统为研究项 | pure 不进入 1.0（ADR-0003） |
| XLF-03-004 | AST/Embedding 语义索引和 `x.meta` | 3.txt | toolchain | P3 | P4 | adapt | 语义索引来自编译器查询（x query）；向量嵌入为可选插件 | 编译器不依赖嵌入模型 |
| XLF-03-005 | `x agent init/implement/explain/fix` | 3.txt | eco | P3 | P5 | adapt | x-ai-tools：P3 explain/fix 只读建议，P5 受控写操作 | AI 输出必须经测试与人工审查 |
| XLF-03-006 | 本地向量检索与上下文构建 | 3.txt | eco | P5 | P5 | adapt | x-ai-tools 可选本地检索组件 | 不进入编译关键路径 |
| XLF-03-007 | 内置 MCP Resources/Tools | 3.txt | toolchain | P3 | P4 | adapt | x mcp：只读 MCP 服务器，映射编译器查询 | 写操作走受控流程 |
| XLF-03-008 | AI IDE 协驾驶面板 | 3.txt | eco | P5 | P5 | adapt | VS Code 扩展可选 AI 面板：上下文预览、权限、diff | 模型供应商经适配器解耦 |
| XLF-03-009 | 规范实时校验和依赖影响图 | 3.txt | toolchain | P3 | P3 | adopt | LSP 实时诊断 + x why/x tree 依赖影响图 | — |
| XLF-03-010 | 标准库机器可读注释 | 3.txt | toolchain | P2 | P3 | adopt | std 文档注释 + 结构化 JSON 文档元数据 | — |
| XLF-03-011 | 模板市场 | 3.txt | eco | P5 | P5 | adapt | 签名模板仓库：x init --template | 模板执行默认沙箱 |
| XLF-03-012 | AI 驱动初始化→契约→实现→修复→发布 | 3.txt | eco | P5 | P5 | adapt | x-ai-tools 流水线：提案→测试→审查→发布 | 人工审批不可绕过 |
| XLF-04-001 | Tensor 类型与 Shape 推导 | 4.txt | eco | P5 | P5 | replace | x-tensor 库：运行时 Shape；静态维度待 const 泛型评估 | 语言不内建 Tensor；成本为编译器级 ML 系统 |
| XLF-04-002 | 编译期自动微分 | 4.txt | eco | P5 | R | replace | 库级 Tape Autograd；编译期 AD 为研究项 | 编译期 AD 需要宏或编译器插件，1.0 不提供；库级实现已能满足训练原型 |
| XLF-04-003 | CUDA/ROCm/Metal Kernel 生成 | 4.txt | eco | P5 | R | replace | 经 FFI 调用成熟内核库/运行时；自研 Kernel 生成为研究项 | 三后端 Kernel 生成超出团队规模 |
| XLF-04-004 | 静态计算图优化与自动并行 | 4.txt | labs | R | R | replace | 导出 ONNX 交给成熟图编译器 | 自动并行属研究 |
| XLF-04-005 | LoRA/QLoRA Adapter 注入 | 4.txt | eco | P5 | P5 | replace | 经 Python 互操作调用成熟微调框架 | 不进入语言语法 |
| XLF-04-006 | 量化、混合精度和分布式训练 | 4.txt | eco | P5 | P5 | replace | 经互操作使用成熟量化/分布式训练框架 | 自研分布式训练栈超出团队规模；复用成熟框架的成本最低 |
| XLF-04-007 | io_uring/IOCP 网络引擎 | 4.txt | core | P5 | P5 | adapt | async 执行器的 io_uring/IOCP/kqueue 适配器；用户态协议栈/DPDK/eBPF 加速改为可选生态适配器（P5 eco） | 依赖 async Edition；用户态协议栈不进 std：安全面与维护成本过高，内核协议栈 + 零拷贝 API 已覆盖主流场景 |
| XLF-04-008 | HTTP/1-3、QUIC、gRPC、WebSocket | 4.txt | eco | P3 | P5 | adopt | x-http：P3 HTTP/1.1+TLS，P4 HTTP/2/gRPC，P5 HTTP/3/QUIC/WebSocket | 协议互操作优先于自研协议栈 |
| XLF-04-009 | Protocol as Type | 4.txt | eco | P3 | P4 | adapt | Typestate 模式 + IDL 代码生成 | 语言级 Session Type 为研究项 |
| XLF-04-010 | 训练即服务 | 4.txt | eco | P5 | P5 | replace | x-ai-tools 编排外部训练服务 | 复用现有调度基础设施 |
| XLF-04-011 | 动态批处理 | 4.txt | eco | P5 | P5 | adopt | 推理服务库的动态批处理 | — |
| XLF-04-012 | `x agent train/finetune/serve` | 4.txt | eco | P5 | P5 | replace | x-ai-tools train/serve 子命令编排外部服务 | 不隐式获取云权限 |
| XLF-04-013 | ONNX/GGUF/safetensors 模型导入 | 4.txt | eco | P5 | P5 | adapt | x-ml 读取库：safetensors/GGUF/ONNX 解析 | v2 补登：原文“模型格式导入器” |
| XLF-05-001 | `spawn`、作用域线程和 Send 检查 | 5.txt | core | P2 | P2 | adopt | std::thread::scope/spawn + Send/Sync 检查 | — |
| XLF-05-002 | M:N 调度、工作窃取和专用线程池 | 5.txt | core | P5 | P5 | adapt | async 执行器：工作窃取 + 专用阻塞线程池 | 依赖 async Edition |
| XLF-05-003 | fork/exec 安全封装 | 5.txt | core | P2 | P3 | adapt | std::process::Command；不提供安全 fork | fork 在多线程下不安全 |
| XLF-05-004 | 共享内存和 IPC | 5.txt | eco | P3 | P4 | adopt | x-ipc：共享内存/管道/本地套接字/句柄传递 | — |
| XLF-05-005 | 自定义分配器、Arena | 5.txt | core | P3 | P4 | adapt | Allocator Trait、全局分配器替换、Arena 类型 | — |
| XLF-05-006 | 原始指针与 Ghost Memory 调试 | 5.txt | core | P2 | P3 | adapt | P2 unsafe/原始指针规范；P3 ASan/MIR 解释器 UB 检查 | Ghost Memory 改为 Sanitizer 方案 |
| XLF-05-007 | CPU/GPU 统一内存 | 5.txt | eco | P5 | P5 | replace | 显式 ManagedBuffer + 同步/迁移 API | 不承诺 CPU/GPU 同一指针类型 |
| XLF-05-008 | Async File/Direct I/O | 5.txt | core | P3 | P5 | adapt | P3 std::os 同步 Direct I/O；P5 async 文件 I/O | — |
| XLF-05-009 | sendfile/splice 零拷贝 | 5.txt | core | P3 | P3 | adopt | std::os::linux 等平台扩展 API | — |
| XLF-05-010 | mmap 智能预取 | 5.txt | eco | P3 | R | replace | x-mmap 显式 madvise hint；自适应预取为研究项 | “智能”预取的收益依赖负载，无法给出通用保证；显式 hint 行为可预期 |
| XLF-05-011 | AI 系统操作命令 | 5.txt | eco | P5 | P5 | adapt | x-ai-tools：计划→dry-run→审批→执行 | 拒绝默认提权 |
| XLF-05-012 | x inspect memory / x run --prefetch | 5.txt | toolchain | P4 | P5 | adapt | x inspect：core dump/堆剖析适配；--prefetch 并入 XLF-05-010 | v2 补登：原文 x inspect memory / x run --prefetch |
| XLF-06-001 | 分层渲染引擎与声明式 UI | 6.txt | eco | P3 | P5 | adopt | XUI 分层：View→UiIr→Renderer→Platform | — |
| XLF-06-002 | Windows/macOS/Linux 桌面 | 6.txt | eco | P5 | P5 | adopt | XUI 桌面宿主：Windows/Linux 先，macOS 后 | — |
| XLF-06-003 | Skia、WebView、托盘和快捷键 | 6.txt | eco | P5 | P5 | adopt | Skia/WebView/托盘/快捷键适配器 | — |
| XLF-06-004 | Android/iOS 原生库和薄胶水 | 6.txt | eco | P5 | P5 | adopt | Android/iOS 静态/动态库 + JNI/Swift 薄胶水 | — |
| XLF-06-005 | Metal/Vulkan、触控与传感器 | 6.txt | eco | P5 | P5 | adopt | 平台能力探测：Metal/Vulkan、触控、传感器 | — |
| XLF-06-006 | 小程序 WASM 逻辑和模板转译 | 6.txt | labs | R | R | research | 实验：JS 胶水 + WASM 逻辑包（平台支持时） | 平台规则变化快；模板转译不作通用承诺 |
| XLF-06-007 | 服务端 HTTP3/gRPC/AI 推理 | 6.txt | eco | P3 | P5 | adopt | x-server：HTTP/gRPC P3–P4；HTTP/3 与推理 P5 | — |
| XLF-06-008 | 裸机、内核、驱动、嵌入式 | 6.txt | core | P4 | P5 | adapt | P4 冻结 no_std（core/alloc）子集；P5 QEMU/开发板 | 内核驱动按目标评估 |
| XLF-06-009 | 中断、MMIO、RISC-V/x86 裸机目标 | 6.txt | core | P5 | P5 | adopt | @interrupt、volatile MMIO、链接脚本；RISC-V/x86 Tier 3 | — |
| XLF-06-010 | 多目标 Build Matrix/PAL | 6.txt | toolchain | P2 | P4 | adopt | PAL + [target] 构建矩阵 | — |
| XLF-06-011 | Agent 全场景脚手架 | 6.txt | eco | P5 | P5 | adapt | 按场景签名模板（CLI/Web/服务/嵌入式） | 禁止万能模板 |
| XLF-07-001 | 因果回溯、确定性记录重演 | 7.txt+8.txt | toolchain | P5 | R | adapt | 集成 rr/平台 TTD 记录重放；语言级通用重放为研究项 | 不承诺 100% 复现 |
| XLF-07-002 | 增量内存快照 | 7.txt+8.txt | toolchain | P4 | R | adapt | core dump/minidump 生成与解析；增量快照为研究项 | — |
| XLF-07-003 | 能耗/碳感知调度 | 7.txt+8.txt | eco | P5 | P5 | adapt | 能耗观测库（RAPL 等）；调度策略归应用 | 拒绝编译器自动迁移 |
| XLF-07-004 | 认知复杂度与重构建议 | 7.txt+8.txt | toolchain | P3 | P3 | adopt | x vet 认知复杂度 Lint | — |
| XLF-07-005 | HLC 因果时间 | 7.txt+8.txt | eco | P3 | P4 | adopt | x-time：HLC 实现，显式传播 | 不给所有变量隐式加字段 |
| XLF-07-006 | Data Glacier/PMEM 持久变量 | 7.txt+8.txt | eco | P5 | P5 | replace | 显式持久化事务库（PMEM/对象存储） | 普通变量不隐式持久化 |
| XLF-07-007 | 后量子密码 | 7.txt+8.txt | eco | P4 | P4 | adapt | x-crypto 绑定成熟 Provider（NIST 标准算法） | 不默认替换现有算法 |
| XLF-07-008 | ZKP 闭包/电路后端 | 7.txt+8.txt | labs | R | R | research | 与外部电路 DSL 互操作研究 | 通用程序转电路属研究 |
| XLF-07-009 | 空间锚点和 GPU 光线追踪 | 7.txt+8.txt | eco | P5 | P5 | replace | 图形/XR 绑定库（Vulkan/DXR/Metal/OpenXR） | 核心不加空间关键字 |
| XLF-07-010 | 触觉与脑机接口 | 7.txt+8.txt | eco | P5 | R | replace | HID/触觉/传感器适配；脑机接口为研究项 | 需伦理/法规审批 |
| XLF-07-011 | 基因编程/策略搜索 | 7.txt+8.txt | toolchain | P4 | P4 | replace | PGO + x tune 参数搜索（只调参数） | 拒绝自动改业务逻辑 |
| XLF-07-012 | 混沌免疫与自修复 | 7.txt+8.txt | eco | P4 | P4 | replace | 熔断/重试/隔离/故障注入库 | 拒绝无人审批热补丁 |
| XLF-07-013 | 法规注解和污点分析 | 7.txt+8.txt | toolchain | P4 | P4 | adapt | x vet 污点分析规则包 | 声明不构成法律意见 |
| XLF-07-014 | 跨栈内存内省 | 7.txt+8.txt | toolchain | P4 | P5 | adapt | x inspect 统一 core/heap/thread 视图 | — |
| XLF-07-015 | Omni-FFI | 7.txt+8.txt | eco | P3 | P5 | adapt | C 由核心提供（XLF-02-011）；Python/JVM/Node 绑定生成 P3–P5 | 拒绝任意 ABI |
| XLF-07-016 | `.xbrain` 联邦项目记忆 | 7.txt+8.txt | eco | P5 | P5 | adapt | x-ai-tools 本地项目记忆（opt-in） | 联邦同步默认关闭 |
| XLF-07-017 | Living Docs | 7.txt+8.txt | toolchain | P2 | P3 | adopt | doc-test + x doc 站点 | — |
| XLF-07-018 | Intent/有界符号执行 | 7.txt+8.txt | labs | R | R | research | x verify：有界模型检查实验（外部 SMT） | 拒绝通用算法生成 |
| XLF-07-019 | eBPF 目标 | 7.txt+8.txt | core | P5 | P5 | adopt | bpfel/bpfeb Tier 3 目标（no_std 子集） | — |
| XLF-09-001 | 编译期静态反射 | 9.txt | core | P2 | P5 | adapt | 1.0：内置 @derive 闭集；通用反射/用户派生 1.0 后 RFC | 无用户宏（ADR-0003） |
| XLF-09-002 | JSON/YAML/TOML/Protobuf/MessagePack | 9.txt | eco | P3 | P4 | adopt | x-json 官方包（P3）；YAML/TOML/Protobuf/MessagePack 生态包 | — |
| XLF-09-003 | Schema Evolution | 9.txt | eco | P4 | P4 | adopt | 序列化库版本化 Schema 与兼容测试 | — |
| XLF-09-004 | 结构化日志/OTLP | 9.txt | eco | P3 | P4 | adopt | x-log：结构化日志 + OTLP 导出 | — |
| XLF-09-005 | Counter/Histogram/Gauge | 9.txt | eco | P3 | P4 | adopt | x-metrics：Counter/Gauge/Histogram | — |
| XLF-09-006 | async Trace 自动上下文 | 9.txt | eco | P5 | P5 | adopt | async Trace Context 传播 | 依赖 async Edition |
| XLF-09-007 | 声明式 CLI 与配置层级 | 9.txt | eco | P3 | P4 | adapt | x-cli-args 参数/配置分层库（Trait + 代码生成，无宏） | — |
| XLF-09-008 | Fuzz/Property/Benchmark | 9.txt | toolchain | P2 | P4 | adopt | x test --bench、x fuzz（libFuzzer）、属性测试库 | — |
| XLF-09-009 | Unicode、i18n 提取、复数/性别 | 9.txt | core | P2 | P4 | adopt | str/char Unicode 基础（P2）；i18n 生态包（P4） | — |
| XLF-09-010 | 2D 矢量和音视频编解码 | 9.txt | eco | P5 | P5 | replace | 绑定 Skia/FFmpeg 等成熟库 | 许可证/漏洞矩阵独立管理 |
| XLF-09-011 | 编译期 SQL 检查 | 9.txt | eco | P4 | P4 | adapt | 离线 Schema 快照 + 查询检查生成工具 | 编译期不连数据库 |
| XLF-09-012 | 异步连接池与迁移 | 9.txt | eco | P4 | P5 | adopt | 同步连接池与迁移 P4；async 版 P5 | — |
| XLF-09-013 | Timer/Cron/Leader Election | 9.txt | eco | P4 | P4 | adopt | Timer/Cron/Leader Election 库 | — |
| XLF-09-014 | JWT/RBAC/Session | 9.txt | eco | P4 | P4 | adopt | x-auth：JWT/RBAC/Session 官方安全包 | 不进入语言 |
| XLF-09-015 | 分布式构建缓存 | 9.txt | toolchain | P4 | P4 | adapt | XBuild 远程只读缓存 | — |
| XLF-09-016 | 二进制 `.xlib` 注册表 | 9.txt | toolchain | P5 | P5 | adapt | 源码优先；二进制缓存按工具链指纹命中 | X ABI 未稳定前不发 binary-only 包 |
| XLF-09-017 | PubGrub/SemVer 解析 | 9.txt | toolchain | P2 | P3 | adopt | PubGrub 解析 + SemVer | — |
| XLF-10-001 | 错误回溯和上下文链 | 10.txt | core | P2 | P3 | adopt | panic 回溯（P2）；错误上下文链库（P3） | — |
| XLF-10-002 | `defer` LIFO 清理 | 10.txt | core | P2 | P5 | adapt | 1.0 用 RAII Guard（std::guard）；defer 1.0 后 RFC | ADR-0003：defer 不进 1.0 |
| XLF-10-003 | unwind/abort/no-exceptions | 10.txt | core | P0 | P4 | adapt | 1.0 只有 panic=abort（ADR-0008 K3）；unwind 1.0 后经 RFC 评估 | — |
| XLF-10-004 | decimal32/64/128 | 10.txt | eco | P3 | P4 | adopt | x-decimal 库 | — |
| XLF-10-005 | 编译期正则/DFA | 10.txt | eco | P3 | P5 | replace | x-regex 运行时编译 + 缓存；编译期 DFA 待 const 能力 | 防 ReDoS：线性时间引擎 |
| XLF-10-006 | Bitstream/Bitfield | 10.txt | eco | P3 | P4 | adapt | 位域库（显式字节序/位序）+ @repr | — |
| XLF-10-007 | 编译期 DI/Mock | 10.txt | eco | P3 | P4 | replace | Trait + 测试替身库 | 不在 HIR 引入 DI 容器 |
| XLF-10-008 | 快照测试 | 10.txt | toolchain | P2 | P2 | adopt | x test 快照断言 | — |
| XLF-10-009 | Stream/Generator/背压 | 10.txt | core | P1 | P5 | adapt | P1 同步 Iterator；P5 Stream/生成器随 async Edition | — |
| XLF-10-010 | Rc/Arc/Weak | 10.txt | core | P1 | P2 | adopt | Box/Rc/Weak（P1），Arc（P2） | — |
| XLF-10-011 | Cell/RefCell 内部可变性 | 10.txt | core | P2 | P2 | adopt | Cell/RefCell | — |
| XLF-10-012 | `build.x`、include、cfg | 10.txt | core | P2 | P5 | adapt | @cfg + include_str/include_bytes（P2）；沙箱构建脚本 1.0 后 RFC | 1.0 无通用构建脚本 |
| XLF-10-013 | 信号和 Coredump 元数据 | 10.txt | core | P3 | P4 | adopt | std::os 信号；崩溃元数据（P4） | — |
| XLF-10-014 | 动态库、插件、符号版本 | 10.txt | core | P4 | P5 | adapt | C ABI 动态库 + 版本协商 | X 原生 ABI 1.0 不稳定 |
| XLF-10-015 | C/Python/Node 绑定生成 | 10.txt | eco | P3 | P5 | adopt | x-bindgen：C 头文件生成（P3），Python/Node（P5） | — |
| XLF-10-016 | SIMD、对齐、cache padding | 10.txt | core | P3 | P4 | adopt | @repr(align)（P3）、std::simd 可移植 SIMD（P4） | — |
| XLF-10-017 | xdoc 站点、依赖图、调用热图 | 10.txt | toolchain | P3 | P4 | adopt | x doc 站点 + 依赖图 | — |
| XLF-10-018 | `x search` 符号/正则/语义搜索 | 10.txt | toolchain | P3 | P4 | adopt | x search：符号/文本搜索（基于查询索引） | — |
| XLF-11-001 | SemVer API 差异发布门禁 | 11.txt | toolchain | P4 | P4 | adopt | x publish 前 API diff + SemVer 门禁 | — |
| XLF-11-002 | LTS 与发布节奏 | 11.txt | toolchain | P4 | P4 | adapt | 6 周 stable 列车；1.0 起每年 1 个 LTS，提供 12 个月安全修复（ADR-0008 K10，见 release） | 只承诺安全与严重缺陷修复，资源有上限 |
| XLF-11-003 | `x rfc` 流程 | 11.txt | toolchain | M0 | P3 | adapt | RFC 模板与流程（M0）；x rfc 命令可选（P3） | — |
| XLF-11-004 | SBOM/CVE/可复现构建 | 11.txt | toolchain | P3 | P4 | adopt | SBOM、x audit、可复现构建 | — |
| XLF-11-005 | 管道、解构、命名/默认参数 | 11.txt | core | P1 | P5 | adapt | 解构（P1）；管道/命名/默认参数 1.0 后逐项 RFC | ADR-0003 |
| XLF-11-006 | 时间旅行调试 | 11.txt | toolchain | P5 | P5 | adapt | x debug 集成 rr/平台 TTD | — |
| XLF-11-007 | Watch 与状态保持热重载 | 11.txt | toolchain | P2 | R | adapt | x run --watch 进程重启（P2）；状态保持热重载为研究项 | — |
| XLF-11-008 | 多调用约定 | 11.txt | core | P2 | P5 | adopt | extern "C"（P2）；stdcall/vectorcall/sysv64 等（P5） | — |
| XLF-11-009 | C++ 名称修饰和模板互操作 | 11.txt | eco | P5 | P5 | replace | C shim + bindgen 适配常见 C++ | 不承诺通用 C++ ABI |
| XLF-11-010 | Serverless 快照启动 | 11.txt | eco | P5 | P5 | replace | 启动优化 + 平台快照能力适配 | 密钥/Socket 不得冻结 |
| XLF-11-011 | FaaS 事件注解 | 11.txt | eco | P5 | P5 | adapt | 厂商无关事件 Schema + 适配器生成 | — |
| XLF-11-012 | SpinLock/Fence/Atomic Ordering | 11.txt | core | P2 | P2 | adopt | std::sync::atomic + Ordering + SpinLock | — |
| XLF-11-013 | 错误码、`x explain`、Fix-it | 11.txt | toolchain | P0 | P3 | adopt | 稳定诊断码（P0）、x explain（P1）、Fix-it（P3） | — |
| XLF-11-014 | `.x.tutor` 项目规则 | 11.txt | toolchain | P3 | P3 | adapt | .x/rules.toml 项目规则 + lint 配置 | — |
| XLF-11-015 | x upgrade 升级命令 | 11.txt | toolchain | P3 | P4 | adapt | x update（依赖）+ 安装器自更新 | v2 补登：原文 x upgrade |
| XLF-12-001 | REPL/Readline/高亮/历史/自动导入 | 12.txt | toolchain | P3 | P4 | adopt | x repl（基于 MIR 解释器） | — |
| XLF-12-002 | 彩色诊断和多进度条 | 12.txt | toolchain | P0 | P3 | adopt | 彩色诊断（P0）、进度条（P3） | — |
| XLF-12-003 | Shell 补全生成 | 12.txt | toolchain | P3 | P3 | adopt | x completions <shell> | — |
| XLF-12-004 | Watch/守护热重启 | 12.txt | toolchain | P2 | P2 | adopt | x run --watch | — |
| XLF-12-005 | Pub/Sub 消息总线 | 12.txt | eco | P4 | P4 | adopt | x-bus 进程内/跨进程 Pub/Sub | — |
| XLF-12-006 | 共享内存 Ring Buffer 零拷贝 | 12.txt | eco | P4 | P4 | adopt | x-ipc SPSC/MPSC 共享内存环形缓冲 | — |
| XLF-12-007 | 持久消息与至少一次重放 | 12.txt | eco | P5 | P5 | adopt | 持久消息日志与至少一次重放 | 不冒充 exactly-once |
| XLF-12-008 | Arrow/Parquet | 12.txt | eco | P5 | P5 | adopt | Arrow/Parquet 绑定 | — |
| XLF-12-009 | DataLoader 双缓冲 | 12.txt | eco | P5 | P5 | adopt | DataLoader 双缓冲 | — |
| XLF-12-010 | 流式 JSON/CSV 反序列化 | 12.txt | eco | P3 | P4 | adopt | x-json 流式解析；CSV 生态包 | — |
| XLF-12-011 | likely/unlikely 分支提示 | 12.txt | core | P2 | P2 | adopt | std::hint::likely/unlikely + @cold | 不改变语义 |
| XLF-12-012 | 尾递归优化保证 | 12.txt | core | P2 | P2 | adapt | @tailcall：自尾调用保证，否则编译错误 | 互递归不作保证 |
| XLF-12-013 | CPU affinity/NUMA | 12.txt | core | P3 | P4 | adopt | std::os 线程亲和/NUMA API | — |
| XLF-12-014 | no-exceptions | 12.txt | core | P0 | P0 | adopt | 语言无异常；panic=abort 为默认 Profile | — |
| XLF-12-015 | 实时调度注解 | 12.txt | eco | P4 | R | adapt | OS 实时优先级 API 封装；硬实时认证为研究项 | — |
| XLF-12-016 | 延迟预算与降级 | 12.txt | eco | P4 | P4 | adopt | Deadline/Budget/Cancel 库 | — |
| XLF-12-017 | Atomic<Option>/无锁热路径 | 12.txt | core | P2 | P4 | adopt | 原子类型（P2）；无锁结构经模型检查后入生态（P4） | — |
| XLF-12-018 | `x env` 本地云环境 | 12.txt | eco | P5 | P5 | adapt | x-dev 环境模板（容器/模拟器） | 凭据不得编译进二进制 |
| XLF-12-019 | 生产影子环境和远端日志 | 12.txt | labs | R | R | research | 脱敏只读流量回放研究 | 拒绝默认复制生产数据 |
| XLF-12-020 | 性能基准承诺 | 12.txt | toolchain | P1 | P4 | replace | docs/performance.md 可测目标 + 版本化基准 | 原文数值无环境与对照，不作承诺 |
| XLF-12-021 | x proxy 内网镜像与 replace 依赖替换 | 12.txt | toolchain | P3 | P3 | adapt | XPM mirror/replace 源替换配置 | v2 补登：原文 x proxy 与 replace 语法 |
