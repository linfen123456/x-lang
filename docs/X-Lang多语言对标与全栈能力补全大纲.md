# X-Lang 多语言对标与全栈能力补全大纲

> 总纲：[X-Lang 企业级完整文档体系总纲](./X-Lang企业级完整文档体系总纲.md)  
> 大纲版本：1.0-outline｜状态：派生 Backlog 已冻结｜初始基线：2026-08-14｜复审：2026-08-15  
> 性质：基于 Go、Rust、C、Python、Java、JavaScript 与 CSS 的派生需求，不属于 12 份原始文档本身。  
> 目标：补齐工业语言的核心语义、生产工具、互操作、服务器、Web/CSS 和平台交付能力，同时避免把所有语言特性无原则堆入核心。  

## 1. 定位与取舍

X-Lang 的待验证设计假设是：借鉴 Rust 的所有权安全、C/LLVM 的原生代码生成、Go 的服务端工作流、Java 的工程治理和 Python 的交互式开发体验，并通过 WASM 与 JS/DOM 互操作研究 Web 能力。这里的对标只表示研究来源，不表示已经达到相同安全性、性能、体验或生态；每项结论必须给出对照版本、平台、工作负载、指标、阈值和失败条件。目标不是复制 JVM、Python 元类、JavaScript 原型链或 CSS 全部历史行为。

### 1.1 采用、改造和拒绝原则

| 来源 | 直接采用 | 受限改造 | 不进入核心 |
|---|---|---|---|
| Go | 简单工具链、Channel、结构化并发、诊断工具 | 接口满足、调度器可观察性 | 隐式运行时魔法 |
| Rust | 所有权、Trait、Result、no_std、Cargo 经验 | 宏、unsafe、复杂泛型按阶段引入 | 无收益的语法复杂度 |
| C | ABI、原生布局、裸机、硬件控制 | 仅在 unsafe/FFI 暴露危险语义 | 预处理器文本替换和普遍 UB |
| Python | REPL、Notebook、数据/AI、FFI | `Dynamic` 仅作边界类型 | Monkey Patch、全局动态语义 |
| Java | 企业兼容、诊断、制品、LTS | Managed 模式需单独 RFC | 为兼容而复制 JVM/class 继承 |
| JavaScript | Event Loop、Promise 桥、DOM/Web API、ESM | 动态对象仅在 JS 边界 | 原型链和隐式类型转换 |
| CSS | 布局、响应式、主题、动画、无障碍 | 标准 CSS + CSS Modules + XStyle Token/CoreStyle 互操作 | 把 CSS 级联塞入核心语言或重写浏览器样式引擎 |

### 1.2 派生需求成熟度、状态与关闭规则

`XLC-*` 是对标派生需求，不能证明其来自 12 份原始材料，也不自动形成路线承诺。下表为各系列的默认分级/状态；单项另有说明时以单项为准。

| ID 范围 | 默认成熟度/状态 | 例外与进入稳定条件 |
|---|---|---|
| `XLC-CORE-001~020` | 单项判定/`待决策` | `010~014`、`018~020` 为 CORE 候选；`001~009`、`015~017` 为 1.0 后 EXTENDED/EXPERIMENTAL 候选。`XLC-CORE` 是追踪命名空间，不代表每项都属于 1.0 核心。 |
| `XLC-EXEC-001~012` | `EXTENDED/待决策` | MIR 参考执行可作为 CORE 验证基础；快速后端须经 ADR，所有工具须有统一 SourceMap。 |
| `XLC-FFI-001~012` | `EXTENDED/待决策` | C ABI 稳定子集可先行；Python/JNI/JS 分别版本化，不共享“全兼容”承诺。 |
| `XLC-WEB-001~015` | `EXTENDED/待决策` | WASM 可先于框架；浏览器宿主、SSR 和工具链通过 G4 后才能标记稳定。 |
| `XLC-STYLE-001~015` | `EXTENDED/待决策` | 始终属于 P5+ 联邦生态；采用标准 CSS/CSS Modules 与受限 XStyle IR，不因实现成熟而转入核心语法。 |
| `XLC-SERVER-001~010` | `EXTENDED/待决策` | 标准库只保留底层 I/O；框架和云适配独立发布。 |
| `XLC-PLATFORM-001~010` | `CORE/草案` | 作为治理能力，Tier 1 的最低版本、签名和支持期必须在 1.0 前转为已决策并有 CI 证据。 |

每个 ID 的关闭证据固定为：章节目标、目标读者、规范/接口内容、关键决策、输入依赖、输出物、测试/审计验收、目标项目、RFC/ADR 和状态变更记录。表格中的“能力、关键内容、目标项目、验收”是该模板的压缩索引，详细任务由工程大纲任务卡承载。

### 1.3 与 12 份原始需求的一致性结论

- `XLF-*` 的 164 项是对原始材料的完整追溯基线；`XLC-*` 的 94 项是审查 Go/Rust/C/Python/Java/JavaScript/CSS 后新增的工程缺口，两类 ID 不合并、不互相冒充来源。
- 对标结论与原始材料的总体方向一致：原生性能、所有权/RAII、并发、跨平台、AI、工具链和企业生态均保留；差异来自对绝对指标、隐式插锁、可选 GC、万能互操作和自动修复等表述的工程化降级。
- “涵盖所有操作系统/服务器/网页”被改写为 Tier、最低版本和分阶段支持矩阵；未通过目标平台测试的能力只表示方向，不表示已支持。
- 完整证据链为 `原始文件 → XLF → 规范章节 → 工程工作包 → 物理项目 → 测试/发布证据`；对标补充链为 `来源语言痛点/优点 → XLC → 同一后半段证据链`。

## 2. 对标结论矩阵

| 维度 | 当前基础 | 主要缺口 | 目标层 |
|---|---|---|---|
| 核心语义 | 语法、类型、Trait、所有权大纲 | 宏、进阶泛型、模块初始化、形式内存模型 | CORE |
| 开发速度 | 增量编译、REPL 需求 | MIR 解释器/快速后端、状态重定义 | CORE/EXTENDED |
| 生产诊断 | Profiler、Coverage 上位规划 | Race、Vet、统一 Coverage、Heap/Task Dump | EXTENDED |
| C 互操作 | C ABI、调用约定、Bindgen | 完整 C 数据模型、varargs、布局探针 | EXTENDED |
| Python 互操作 | Omni-FFI/Tensor 设想 | GIL、异常、Buffer/DLPack、Wheel、asyncio | EXTENDED |
| Java 企业能力 | LTS、包、安全和治理 | BOM、依赖洞察、运行诊断、框架契约 | EXTENDED |
| JS/Web | WASM、Node 绑定、小程序 | Event Loop、DOM、Web API、ESM/npm、SSR | EXTENDED |
| CSS/UI | VNode、Skia、静态布局 | Selector、Cascade、Flex/Grid、响应式、动画 | EXTENDED |
| 平台 | 三大 OS+移动/WASM/裸机目标 | Tier、最低版本、安装/签名/真机测试 | CORE/EXTENDED |

## 3. `XLC-CORE`：核心语言相关派生需求

本节编号保持不变以保护追溯，但按 1.0 候选剖面重新分层：`001~009` 的宏与高级泛型、`015` 的 async 生命周期、`016~017` 的 Dynamic/反射不进入 1.0 核心。目标项目仅表示未来归属，未到阶段不得预建空项目。

| ID | 能力 | 关键决策与内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLC-CORE-001 | 通用宏模型 | Token Tree、展开阶段、递归/资源上限、Span | x-macro-model | 宏语法和阶段 RFC |
| XLC-CORE-002 | 卫生声明式宏 | 定义/调用上下文、名称捕获、导入规则 | x-macro-expand | 正反例和 SourceMap 测试 |
| XLC-CORE-003 | 过程宏沙箱 | 独立进程、权限清单、确定输入、缓存键 | x-macro-host | 逃逸/超时/可复现测试 |
| XLC-CORE-004 | Const Generics | 支持类型、表达式子集、相等性与单态化 | x-types/x-traits | 数组/Shape 和诊断测试 |
| XLC-CORE-005 | Associated Types/GAT | 约束、归一化、循环和对象安全 | x-traits | 求解器符合性套件 |
| XLC-CORE-006 | Trait Object | vtable、对象安全、upcast、ABI 稳定边界 | x-types/x-codegen | 动态分派 ABI 测试 |
| XLC-CORE-007 | Variance/HRTB | 引用、函数、生命周期高阶量化 | x-types/x-borrow | 形式规则和借用测试 |
| XLC-CORE-008 | Auto/Negative Trait | Send/Sync 类推导和显式否定 | x-traits/x-borrow | 一致性和跨线程测试 |
| XLC-CORE-009 | Specialization 处置 | 默认不稳定；证明一致性后方可实验 | x-traits | RFC 或明确否决记录 |
| XLC-CORE-010 | 模块初始化 | 全局常量/静态、初始化顺序、循环和失败 | x-resolve/x-consteval | 确定顺序和循环诊断 |
| XLC-CORE-011 | 求值顺序 | 参数、运算符、短路、析构、panic 路径 | language spec | 同程序跨后端一致 |
| XLC-CORE-012 | 正式内存模型 | 对象生命周期、别名、padding、未初始化、UB 分类 | memory-model spec | 规则 ID 和模型测试 |
| XLC-CORE-013 | Pointer Provenance | 指针来源、整数转换、暴露地址、FFI | x-borrow/x-mir-interpreter | UB 正反例 |
| XLC-CORE-014 | 正式并发模型 | data race、happens-before、原子顺序、Fence | concurrency spec | Litmus tests |
| XLC-CORE-015 | Async 生命周期 | Future、Pin 候选、取消安全、结构化作用域 | x-async spec/runtime | 取消/泄漏/析构测试 |
| XLC-CORE-016 | Dynamic 边界类型 | JSON/FFI/脚本使用；显式检查，无隐式鸭子类型 | x-dynamic | downcast/错误/性能测试 |
| XLC-CORE-017 | 受限反射 | 编译期类型/字段查询；运行时元数据显式保留 | x-reflect | 裁剪和兼容测试 |
| XLC-CORE-018 | Edition 与迁移 | 解析/语义变更隔离、自动修复、跨 Edition 依赖 | x-migrate | N-1/N-2 迁移项目 |
| XLC-CORE-019 | 可观察行为目录 | 顺序、诊断稳定性、布局、时间和实现自由 | specs/reference | 兼容审查清单 |
| XLC-CORE-020 | 核心非目标 | 不复制原型链、元类、文本预处理器、隐式 GC | governance RFC | 所有新增特性先做归属审查 |

## 4. `XLC-EXEC`：快速执行、调试与质量工具

| ID | 能力 | 内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLC-EXEC-001 | MIR 解释器 | 执行核心 MIR、常量、测试和 REPL | x-mir-interpreter | 与 LLVM 结果差分 |
| XLC-EXEC-002 | UB 检测器 | 借用、越界、未初始化、无效布局、泄漏 | x-ub-check | 故障语料无漏报基线 |
| XLC-EXEC-003 | 快速 Debug 后端 | 评估 Cranelift/Bytecode；不改变语义 | x-codegen-fast | 冷/增量编译基准和 ADR |
| XLC-EXEC-004 | REPL 状态模型 | 定义重定义、导入、变量历史、失败恢复 | xrepl | 多单元交互测试 |
| XLC-EXEC-005 | Notebook Kernel | Jupyter 协议、富媒体、隔离、包环境 | x-kernel | Notebook E2E |
| XLC-EXEC-006 | `x vet` | 错误忽略、资源泄漏、并发、API 误用规则 | x-vet | 规则稳定 ID 和抑制机制 |
| XLC-EXEC-007 | `x race` | 编译插桩、同步事件、竞态报告 | x-race/x-instrumentation | 已知竞态基准 |
| XLC-EXEC-008 | `x coverage` | 语句/分支/函数/泛型覆盖、LCOV/JSON | x-coverage | SourceMap 和 CI 阈值 |
| XLC-EXEC-009 | 统一 Profiler | CPU、Heap、Alloc、Lock、Task、I/O | x-profiler | 低开销和多平台格式 |
| XLC-EXEC-010 | Runtime Dump | 线程、任务、锁等待、堆和模块报告 | x-debug/x-runtime | 无调试器生产诊断 |
| XLC-EXEC-011 | Sanitizer 矩阵 | ASan/TSan/MSan/LSan/UBSan/CFI 能力 | x-instrumentation | 目标支持和冲突矩阵 |
| XLC-EXEC-012 | PGO/LTO/BOLT | 采样、Profile 合并、确定性和回归 | x-optimizer/x-build | 真实工作负载基准 |

## 5. `XLC-FFI`：C、Python、Java 与 JavaScript 互操作

| ID | 能力 | 关键内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLC-FFI-001 | C 数据模型 | LP64/LLP64、整数提升、union、packed、flex-array | x-ffi-c | Clang ABI 探针 |
| XLC-FFI-002 | C varargs/restrict/TLS | unsafe 限定、平台差异、优化承诺 | x-ffi-c | C 双向调用测试 |
| XLC-FFI-003 | Header Import/Export | 宏常量、inline、条件头、生成头文件 | x-bindgen | 大型真实头文件回归 |
| XLC-FFI-004 | Python 对象模型 | GIL/free-threaded、refcount、异常、回调 | x-python | CPython 版本矩阵 |
| XLC-FFI-005 | Python 数据协议 | Buffer、NumPy Array Interface、DLPack | x-python/x-tensor | 零拷贝资格与生命周期测试 |
| XLC-FFI-006 | Python 包发布 | Wheel、PyPI、平台标签、abi3 评估 | x-python-pack | 安装/升级/卸载测试 |
| XLC-FFI-007 | Python async/Notebook | asyncio/Future、取消、上下文 | x-python/x-kernel | 双向异步测试 |
| XLC-FFI-008 | Java/JNI 适配 | JVM attach、引用、异常、线程、类加载器 | x-jni | JVM 版本与泄漏测试 |
| XLC-FFI-009 | JS 值与异常 | JS Object、TypedArray、Callback、Result/Exception | x-js | Browser/Node 矩阵 |
| XLC-FFI-010 | Promise/Future | 调度、取消、微任务和生命周期 | x-js/x-web-runtime | 双向 async 测试 |
| XLC-FFI-011 | ESM/npm 发布 | ESM 优先、CJS 适配、类型定义、npm 包 | x-js-pack | Node/Bundler 互操作 |
| XLC-FFI-012 | FFI 安全规范 | 所有权、线程、panic、字符串、句柄、版本 | specs/ffi | 每种桥接都有资源图 |

## 6. `XLC-WEB`：浏览器和现代 Web 工程

| ID | 能力 | 关键内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLC-WEB-001 | 浏览器 Event Loop | task/microtask、timer、render phase | x-web-runtime | 与浏览器行为对照 |
| XLC-WEB-002 | DOM 绑定 | Node/Element/Event、生命周期、批量更新 | x-dom | Web Platform Tests 子集 |
| XLC-WEB-003 | Web API | Fetch、Streams、Storage、IndexedDB、Clipboard/File | x-web-api | 浏览器版本矩阵 |
| XLC-WEB-004 | Worker | Web/Service Worker、消息、共享内存权限 | x-web-worker | 隔离和取消测试 |
| XLC-WEB-005 | Canvas/WebGL/WebGPU | 资源、错误、设备丢失和 Shader | x-web-graphics | 浏览器/GPU 测试 |
| XLC-WEB-006 | 组件模型 | Props、State、Lifecycle、Context、Error Boundary | `x-web::ui` | 行为契约和可访问性 |
| XLC-WEB-007 | 响应式状态 | Signal/Computed/Effect、批处理、循环检测 | x-reactivity | 确定更新和泄漏测试 |
| XLC-WEB-008 | Router/Form | 路由、导航、表单、验证、提交和错误 | x-web-framework | 浏览器 E2E |
| XLC-WEB-009 | SSR/Hydration | 同构输出、序列化、安全、Mismatch | `x-web::ssr` | SSR/CSR 一致性 |
| XLC-WEB-010 | HMR | 模块边界、状态保留和失败回滚 | `x-web::tooling` | 编辑到更新延迟基准 |
| XLC-WEB-011 | Bundler | 依赖图、资产、插件沙箱、缓存 | `x-web::tooling` | 可复现构建 |
| XLC-WEB-012 | Tree Shaking/Code Split | ESM 图、副作用、动态导入、Chunk | `x-web::tooling` | 体积和加载测试 |
| XLC-WEB-013 | SourceMap | X→MIR/WASM/JS/CSS 多级映射 | x-source-map | 浏览器断点准确 |
| XLC-WEB-014 | Dev/Deploy Adapter | 本地服务器、代理、静态/边缘/Node 部署 | `x-web::tooling` | 模板 E2E |
| XLC-WEB-015 | Web 安全默认 | XSS、CSP、Trusted Types、CSRF、依赖完整性 | x-web-security | OWASP 场景测试 |

## 7. `XLC-STYLE`：CSS、布局、主题和无障碍

样式能力属于 P5+ 联邦生态：XUI 使用普通类型/函数，Web 以标准 CSS 和 CSS Modules 为权威，`x-ui::style` 只提供 Token、类型化值、主题和受限 CoreStyle IR。下表保留能力追踪，但 Selector/Cascade/Flex/Grid 在 Web 上由浏览器实现，不预建对应引擎 crate；原生布局必须另有需求、ADR 和平台测试。

| ID | 能力 | 关键内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLC-STYLE-001 | 选择器 | type/class/id/attribute、组合器、伪类/伪元素 | 标准 CSS / `x-web::ui` | 浏览器/WPT Selector 对照测试 |
| XLC-STYLE-002 | 级联 | origin、specificity、source order、important 策略 | 标准 CSS / `x-web::ui` | 浏览器级联结果，不实现第二套规则 |
| XLC-STYLE-003 | 继承与初始值 | inherited/non-inherited、unset/revert | 标准 CSS / `x-web::ui` | WPT 属性矩阵 |
| XLC-STYLE-004 | 变量与 Design Token | 自定义属性、类型 Token、fallback、主题 | `x-ui::style` | 循环、作用域和 CSS 生成测试 |
| XLC-STYLE-005 | 单位与颜色 | 长度、角度、时间、百分比、色彩空间 | `x-ui::style` | 类型、序列化和平台降级测试 |
| XLC-STYLE-006 | Block/Inline | Formatting Context、盒模型、margin collapse | 标准 CSS；原生 Renderer 待 ADR | WPT 布局子集 |
| XLC-STYLE-007 | Flexbox | 主/交叉轴、flex basis、wrap、gap | 标准 CSS；原生 Renderer 待 ADR | 浏览器截图差分 |
| XLC-STYLE-008 | Grid | track、area、auto placement、subgrid 取舍 | 标准 CSS；原生 Renderer 待 ADR | WPT/布局黄金测试 |
| XLC-STYLE-009 | 定位和层叠上下文 | relative/absolute/fixed/sticky、z-index | 标准 CSS；原生 Renderer 待 ADR | 滚动/嵌套测试 |
| XLC-STYLE-010 | 响应式查询 | media/container、viewport、DPI、能力查询 | 标准 CSS / `x-web::ui` | 多尺寸/设备测试 |
| XLC-STYLE-011 | 动画与过渡 | keyframe、transition、transform、取消、reduced-motion | 标准 CSS / `x-web::ui` | 时间线和合成测试 |
| XLC-STYLE-012 | 样式隔离 | CSS Modules/Shadow boundary、全局逃逸 | `x-web::ui` | 类型化 class 和组件冲突测试 |
| XLC-STYLE-013 | SSR 样式 | 提取、去重、关键 CSS、hydration 顺序 | `x-web::{ui,tooling}` | 无闪烁和一致性测试 |
| XLC-STYLE-014 | 无障碍样式 | 对比度、焦点、缩放、高对比、reduced-motion | `x-ui::a11y` | WCAG 自动和人工检查 |
| XLC-STYLE-015 | 多后端降级 | CSS、Skia、原生视图属性和不支持诊断 | `x-ui::{style,native}` | 平台能力矩阵；禁止静默忽略 |

## 8. `XLC-SERVER`：生产服务器补全

| ID | 能力 | 内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLC-SERVER-001 | HTTP Framework | Router、Middleware、Context、Body Stream | x-web-server | HTTP 互操作和 fuzz |
| XLC-SERVER-002 | API Schema | OpenAPI、gRPC/Protobuf、版本和错误体 | x-api-schema | 生成/兼容测试 |
| XLC-SERVER-003 | Validation | 边界 Schema、结构化错误、敏感字段 | x-validation | 恶意输入测试 |
| XLC-SERVER-004 | Resilience | Timeout、Retry、Circuit Breaker、Bulkhead | x-resilience | 故障注入与预算 |
| XLC-SERVER-005 | Traffic Control | Rate Limit、Load Shed、Backpressure | x-traffic-control | 过载和公平性测试 |
| XLC-SERVER-006 | Service Lifecycle | Health/Ready、优雅关闭、Drain、信号 | x-server-runtime | 部署滚动测试 |
| XLC-SERVER-007 | Discovery/Config/Secrets | 动态配置、短期凭据、轮换、审计 | x-cloud-runtime | 权限和失效测试 |
| XLC-SERVER-008 | Database Contract | 事务、池、迁移、SQL 检查、遥测 | x-db | 故障与兼容测试 |
| XLC-SERVER-009 | Observability Contract | Trace Context、Metrics、Log、采样、脱敏 | x-observability | OTel 互操作 |
| XLC-SERVER-010 | Container/K8s | 最小镜像、SBOM、探针、资源限制、部署模板 | x-deploy | 集群 E2E 和回滚 |

## 9. `XLC-PLATFORM`：平台支持和发布契约

| ID | 能力 | 内容 | 目标项目/责任域 | 验收 |
|---|---|---|---|---|
| XLC-PLATFORM-001 | Tier 模型 | Tier 1 每 PR 全测；Tier 2 定期；Tier 3 仅构建；实验无承诺 | x-target-spec/release | 发布矩阵机器可读 |
| XLC-PLATFORM-002 | 最低版本 | Windows/Server、glibc/musl/kernel、macOS/Xcode、浏览器、WASI | x-target-spec/x-installer | 安装前检查和清晰诊断 |
| XLC-PLATFORM-003 | CPU 基线 | x86_64/ARM64/RISC-V 指令集、Feature 探测、回退 | x-target-spec | 真机/模拟器测试 |
| XLC-PLATFORM-004 | SDK/Sysroot | 获取、缓存、校验、许可证、离线 | x-build/x-installer | 可复现交叉编译 |
| XLC-PLATFORM-005 | 安装与签名 | MSI/pkg/deb/rpm/archive、签名、公证、卸载 | x-installer/distribution | 干净机 E2E |
| XLC-PLATFORM-006 | 移动打包 | Android API/ABI、iOS Deployment Target、签名 | x-mobile/distribution | 真机安装和升级 |
| XLC-PLATFORM-007 | 浏览器矩阵 | Chromium/Firefox/WebKit 最低版本和降级 | x-web-runtime/platform-ci | Web Platform CI |
| XLC-PLATFORM-008 | 嵌入式 | linker script、startup、PAC/HAL、OpenOCD/QEMU | x-codegen-baremetal/x-installer | 硬件在环 |
| XLC-PLATFORM-009 | 崩溃工件 | Core/Minidump、符号服务器、隐私和保留 | x-debug/x-release-metadata | 跨平台定位演练 |
| XLC-PLATFORM-010 | EOL | 提前通知、迁移、最后安全版本、归档 | release/x-migrate | 生命周期政策 |

## 10. 实施顺序与门禁

| 阶段 | 必须完成 | 禁止提前进入 |
|---|---|---|
| G0 语言冻结 | XLC-CORE-001~020 的接受/否决、形式规则和测试设计 | Web/ML 新核心关键字 |
| G1 可运行核心 | MIR 解释器或快速后端、LLVM E2E、核心 std | 多平台同时铺开 |
| G2 生产工具 | Vet/Race/Coverage/Profiler/Sanitizer、C FFI | “生产级”宣传 |
| G3 服务端 | HTTP/API/Resilience/Observability/K8s | 未经压测发布 1.0 服务器框架 |
| G4 Web 平台 | JS/DOM/Event Loop/Bundler/SSR | CSS 语义未确定时承诺全栈 UI |
| G5 样式与 UI | Selector/Cascade/Flex/Grid/响应式/A11y | 宣称跨平台像素/行为完全一致 |
| G6 生态扩展 | Python/JVM/移动/桌面/AI/研究项目 | CORE 反向依赖 Labs |

每个阶段的 Go/No-Go 必须同时满足：规范已决策、接口已版本化、项目已映射、自动测试存在、性能/安全有证据、失败和迁移路径已文档化。

## 11. 补全验收清单

- [ ] 所有 `XLC-*` 具有唯一 ID、成熟度、目标项目、RFC/ADR 和测试。
- [ ] 宏、进阶泛型、内存模型、并发模型不再只有上位概念。
- [ ] REPL 有明确执行后端，LLVM 与解释/快速后端通过差分测试。
- [ ] Vet、Race、Coverage、Profiler 和 Sanitizer 形成统一生产诊断体系。
- [ ] C/Python/Java/JS 每种互操作均有对象、错误、线程和版本契约。
- [ ] Web 覆盖 Event Loop、DOM、Web API、SSR、HMR、Bundler 和部署。
- [ ] 样式覆盖 Selector、Cascade、Flex/Grid、响应式、动画、隔离和 A11y。
- [ ] 服务器覆盖 API、韧性、流量、生命周期、可观测和部署闭环。
- [ ] 所有平台有 Tier、最低版本、打包、签名、真机/模拟器和 EOL 政策。
- [ ] 不以功能数量或未复现指标宣称“最强语言”；正式声明只引用通过测试和审计的能力。

## 12. 2026 设计缺口与可借鉴技术

### 12.1 完整缺口清单

本节的 `P0/P1/P2` 是关闭优先级，不等同于工程路线中的产品阶段：P0 阻断最小可信实现，P1 阻断可用性与核心竞争力，P2 阻断 1.0、长期演进或生态可信度。缺口关闭后必须链接唯一 RFC/ADR、实现、测试和原始证据，不能只修改状态文字。

#### 12.1.1 定位、语言与安全

| 优先级 | 缺口 | 必须交付 | 可证伪关闭条件 |
|---:|---|---|---|
| P0 | `GAP-LANG-01` 身份、目标用户与取舍未冻结 | 项目章程、首要场景、非目标、冲突排序 | CLI/系统工具/服务端优先级获批准；Web、GUI、ML、AI 不进入 1.0 核心 |
| P0 | `GAP-LANG-02` 语法和词法规范缺失 | 以 1.0 候选剖面为输入，冻结 Unicode/标识符、关键字与语法预算、Token、EBNF、优先级、分号、歧义、恢复和规范格式 | 完整语法可被工具解析；`parse-format-parse` 等价且幂等；规范 Parser、语法语料和编辑器 Parser 差分无未解释分歧 |
| P0 | `GAP-LANG-03` 类型与求值语义缺失 | 冻结名义类型、公开显式/局部推断边界、显式转换、求值顺序、常量和溢出规则 | 每条规则有 ID、正反例、诊断和解释器/编译器一致性测试；无跨模块推断、用户隐式转换或基于返回上下文猜测 |
| P0 | `GAP-LANG-04` 核心错误与控制流语义缺失 | `Result`、传播、return、panic、unwind/abort、Drop 和进程退出模型 | 固定控制流矩阵覆盖正常、传播、提前返回、panic 与进程退出；每个路径的值、诊断和 Drop 顺序与规范一致。取消归 `GAP-DX-04`，FFI 清理归 `GAP-COMP-09` |
| P0 | `GAP-LANG-05` Safe X 与 unsafe 契约未闭合 | UB 分类、Provenance、别名、生命周期、布局和 unsafe 义务 | 完备性评审通过；差分、属性、反例和 Sanitizer 证据覆盖全部稳定规则 |
| P0 | `GAP-LANG-06` 并发内存模型未闭合 | 原子、内存序、Happens-before、数据竞争、线程与取消模型 | litmus test、有界 model-check 和多后端结果满足正式模型 |
| P0 | `GAP-LANG-07` 模块、名称与可见性规则缺失 | 模块树、导入、循环、命名空间、可见性与初始化顺序 | 多文件正反例、确定解析和循环诊断通过 |
| P1 | `GAP-LANG-08` 泛型、Trait 与一致性边界未冻结 | 1.0 先冻结类型参数、简单约束、孤儿/禁止重叠、单态化和静态分派；高级能力逐项 RFC；规定求解步数/内存/代码体积预算 | 核心一致性与压力语料在预算内结束；歧义、超预算和代码膨胀产生稳定诊断；高级泛型缺失不阻断 1.0 |
| P2 | `GAP-LANG-09` 宏与编译期执行边界未冻结 | 1.0 明确无用户宏/过程宏/通用 comptime；后续能力逐项规定卫生、展开顺序、确定性、沙箱、I/O 权限和资源预算 | 1.0 无宏依赖；实验开启后相同输入可复现，超时/OOM/越权可诊断且不能污染稳定编译 |

#### 12.1.2 ABI、编译器与平台

| 优先级 | 缺口 | 必须交付 | 可证伪关闭条件 |
|---:|---|---|---|
| P0 | `GAP-COMP-01` ABI 与数据布局模型缺失 | target 数据布局、标量宽度/对齐、结构体 Padding、调用约定、符号和最小 `extern C` 探针 | 选定一个主机 target 与 C 编译器版本；机器可读布局契约、黄金对象和标量/结构体双向调用探针一致，不形成稳定 ABI 承诺 |
| P0 | `GAP-COMP-02` MVP 架构仍可能过度拆分 | compiler/runtime/cli/library-core/conformance 等 4～6 个 Workspace 成员、阶段化结构和拆分 ADR 门禁 | 端到端编译闭环存在；无空 crate、循环依赖和无消费者接口 |
| P1 | `GAP-COMP-03` 没有参考执行与优化正确性证据 | MIR 解释器、verifier、reducer、LLVM 差分和优化不变量 | `-O0/-O2`、解释器和后端在定义行为内结果一致，失败可最小化 |
| P1 | `GAP-COMP-04` 增量编译和缓存模型缺失 | P2 冻结查询键/依赖/失效模型并做本地探针；P3 实现并发、身份/租户、签名与远程缓存威胁模型 | P3 固定变更语料的增量/全量结果 100% 一致；跨版本、越权、篡改和错误签名缓存被拒绝并可安全回退全量构建；收益达到 Benchmark RFC 门槛 |
| P1 | `GAP-COMP-05` 平台 Tier 契约未实体化 | target triple、CPU/ABI、OS/SDK/linker、证据、降级和退役 Schema | 候选 target 均生成机器可读条目，CI 无静默跳过；连续发布证据是 P4 晋级 Stable 的附加门禁，不阻断 P2 的契约关闭 |
| P1 | `GAP-COMP-06` 性能没有可复现基线 | 编译、增量、内存、制品、运行时、吞吐和尾延迟基准 | 固定 reference/环境/数据/统计；P50/P95/P99 和回归阈值可复跑 |
| P1 | `GAP-COMP-07` 可复现构建与发布输入未锁定 | P2 建工具链/依赖/flags/SDK/linker/locale/时间输入探针；P3/P4 接入签名例外、制品证明和发布阻断 | 两个隔离环境的发布候选制品可比较；例外有 Schema、Owner 和到期日；无法解释的差异阻断发布 |
| P2 | `GAP-COMP-08` 调试、分析与故障定位不完整 | 调试信息、DAP、堆栈、变量、Profiler、Coverage、Race/UB 工具 | 优化构建和跨平台样例的断点、回溯、SourceMap 与崩溃定位通过 |
| P2 | `GAP-COMP-09` 稳定 C ABI 与 FFI 子集缺失 | 支持 target/编译器/linker 矩阵；`repr(C)`、宽度/对齐/Padding、enum/struct、varargs、回调、线程、句柄、UTF 编码、panic/unwind/abort、动态库和符号版本 | P3/P4 完成 C 双向调用、黄金布局/对象、负向边界、泄漏/线程/错误/升级矩阵；不在子集内的能力明确拒绝或保持 Experimental |

#### 12.1.3 开发体验、标准库与生态

| 优先级 | 缺口 | 必须交付 | 可证伪关闭条件 |
|---:|---|---|---|
| P1 | `GAP-DX-01` 诊断体系没有质量基线 | 不可复用错误码、根因排序、级联抑制、带适用条件的 Fix-it、版本化 JSON Schema 和 `x explain` | 体验 RFC 冻结错误语料 ID 与硬件；首诊根因命中 ≥85%、适用 Fix-it 后语义正确 ≥95%、文本/JSON Schema 100% 通过，阈值变更保留原始数据并重新批准 |
| P1 | `GAP-DX-02` 简洁性与可学性没有用户证据 | 语法预算、统一任务、新手实验、与 Go/Rust/Gleam 的固定版本迁移对照和失败分类 | 体验 RFC 冻结任务集 ID；P2 至少 20 名未参与设计的目标用户完成项目创建、CLI、错误处理和测试，首次完成率 ≥80%；同时记录源码/标注量、用时、求助、修复轮次和失败阶段，只能对已测场景给出易读/易学结论 |
| P1 | `GAP-DX-03` 标准库稳定边界不清 | `core/alloc/std` 分层、复杂度、错误、平台差异和 API 稳定政策 | 两个维护型参考 CLI（各 ≥20 模块，覆盖参数、文件/配置、网络、错误与测试）只用公开 API；文档测试和平台契约通过 |
| P1 | `GAP-DX-04` 并发 Runtime 与语言语义可能耦合 | 结构化并发、取消、阻塞和语言/Executor 契约；P2 使用最小参考 Executor，优化调度器后续实现 | 更换参考 Executor 不改变定义行为；固定取消/Drop/泄漏语料通过。公平性、压力和故障注入是 P3/P4 Runtime 晋级门禁 |
| P2 | `GAP-DX-05` 工具链闭环未形成 | `check/build/run/test/fmt/doc`、LSP、DAP、包和统一配置 | 新项目从创建到签名发布可在三大 OS 和离线环境复现 |
| P2 | `GAP-DX-06` 包管理与注册表治理未落地 | resolver、lockfile、缓存、签名、yank、恢复、命名和恶意包策略 | 确定解析、供应链攻防、撤回/恢复和 N-1/N-2 升级演练通过 |
| P2 | `GAP-DX-07` 生态仍是能力地图 | `governance/ecosystem-adoption.yaml` 登记联邦仓库/项目 ID、维护者确认、版本、平台、使用周期、升级结果和证据链接 | 至少 10 个非模板公开项目，其中 3 个由核心组织之外的维护者独立维护 ≥90 天；3 个间隔 ≥30 天的连续发布周期、两个 Tier 1 OS；固定项目集 N-1 升级成功率 ≥90%。仅称“早期验证生态”，不称成熟生态 |
| P2 | `GAP-DX-08` AI/Agent 接口缺少稳定边界 | 版本化机器可读诊断、Rule ID、确定名称解析/语义索引、最小权限、diff/审计与可撤销写操作 | Agent 默认本地只读；写入可追踪、可测试、可回滚且不能覆盖规范；AI 输出不进入编译语义 |

#### 12.1.4 演进、治理与可信度

| 优先级 | 缺口 | 必须交付 | 可证伪关闭条件 |
|---:|---|---|---|
| P0 | `GAP-GOV-01` RFC/ADR 和状态治理尚未实际运行 | 编号、状态机、Owner、反对意见、取代和证据模板 | 至少 3 个核心 RFC 与 2 个架构 ADR 完整走通提案、评审、批准/拒绝、证据和取代流程；未批准规则不能进入 Stable |
| P2 | `GAP-GOV-02` 兼容与 Edition 机制未实现 | SemVer、Edition、API/ABI/lockfile/Schema diff、弃用周期、迁移和回滚 | 固定不少于 5 个 N-1/N-2 参考项目，预期兼容/拒绝分类 100% 匹配；自动迁移可回滚，失败不得改坏工作区 |
| P2 | `GAP-GOV-03` 安全与供应链运营尚无证据 | 非空发布策略实例：固定 CVSS/项目影响分类、Critical/High 审批规则、target→sanitizer 清单、Fuzz 预算、SPDX 3.0.1 必填字段、SLSA Build 等级、签名/撤回、CVE、密钥轮换和恢复 | Stable 无未豁免 Critical/High；每个 Tier 1 target 在批准 sanitizer 清单上累计 ≥24 CPU-hours 且无未归档唯一崩溃；SBOM 校验通过；Beta 至少达到 SLSA Build L2，Stable 必须达到 L3；Critical 24h 分诊/7 天修复，High 3 天分诊/30 天修复；签名撤回、轮换和恢复固定夹具演练通过。豁免必须有 Owner、理由和 ≤30 天到期日 |
| P2 | `GAP-GOV-04` 许可证、商标和贡献治理未确定 | 代码/文档许可证、CLA/DCO 选择、商标与治理章程 | 法律评审完成；用户可明确判断使用、分发和贡献权利 |
| P2 | `GAP-GOV-05` 成熟度和宣传缺少自动约束 | 根 `governance/claims.yaml` 为唯一 Claim Registry，Schema 必填声明 ID、同义词、范围、版本、对照、环境、指标、证据哈希、Owner 和到期日；首份声明出现时才创建 | CI 用受版本控制的覆盖清单扫描 README、官网源码与部署快照、发布说明和生成文档；中英文同义宣传语夹具必须命中；证据不存在、哈希变化、版本越界、Registry 为空或声明过期均阻断 |
| P2 | `GAP-GOV-06` 长期维护和退出机制缺失 | LTS 条件、EOL、Bus Factor、事故响应、研究停止和归档规则 | 发布、弃用、事故和研究退出均有 Owner、SLO 与演练记录 |

#### 12.1.5 GAP 与既有需求的追溯

`GAP-*` 是对 XLF/XLC/XLE 的审计聚合视图，不是第四套需求，不计入总纲的 319 个唯一需求 ID。下表给出每个 GAP 的主要上游；发现新的独立需求时，必须先进入 XLF/XLC/XLE 或 RFC，再更新映射。GAP 关闭不能替代上游需求逐项验收。

| GAP | 主要上游 ID |
|---|---|
| `GAP-LANG-01` | `XLF-01-010`、`XLC-CORE-020`、`XLE-GOV-001`、`XLE-GOV-004` |
| `GAP-LANG-02` | `XLF-02-012`、`XLC-CORE-010~011`、`XLE-DATA-004` |
| `GAP-LANG-03` | `XLF-11-005`、`XLC-CORE-004~009`、`XLC-CORE-011`、`XLC-CORE-019` |
| `GAP-LANG-04` | `XLF-10-001~003`、`XLF-12-014`、`XLC-CORE-011` |
| `GAP-LANG-05` | `XLF-01-006`、`XLF-05-006`、`XLC-CORE-012~013` |
| `GAP-LANG-06` | `XLF-05-001`、`XLF-11-012`、`XLF-12-017`、`XLC-CORE-014~015` |
| `GAP-LANG-07` | `XLF-02-012`、`XLC-CORE-010`、`XLC-CORE-018~019` |
| `GAP-LANG-08` | `XLC-CORE-004~009` |
| `GAP-LANG-09` | `XLC-CORE-001~003` |
| `GAP-COMP-01` | `XLF-02-011`、`XLF-11-008`、`XLC-FFI-001`、`XLC-FFI-012` |
| `GAP-COMP-02` | `XLF-01-001~004`、`XLE-GOV-004`、`XLE-GOV-008` |
| `GAP-COMP-03` | `XLF-01-003`、`XLC-EXEC-001~003`、`XLC-EXEC-012`、`XLE-DEV-011` |
| `GAP-COMP-04` | `XLF-01-014`、`XLF-02-004`、`XLE-DATA-007` |
| `GAP-COMP-05` | `XLF-01-011`、`XLC-PLATFORM-001~010` |
| `GAP-COMP-06` | `XLF-12-020`、`XLC-EXEC-003`、`XLC-EXEC-009`、`XLC-EXEC-012` |
| `GAP-COMP-07` | `XLF-11-004`、`XLE-DEV-002`、`XLE-DEV-008`、`XLE-DEV-010` |
| `GAP-COMP-08` | `XLF-11-006`、`XLF-11-013`、`XLC-EXEC-006~011` |
| `GAP-COMP-09` | `XLF-02-011`、`XLF-07-015`、`XLF-10-014~015`、`XLF-11-008`、`XLC-FFI-001~003`、`XLC-FFI-012` |
| `GAP-DX-01` | `XLF-11-013`、`XLF-12-002`、`XLC-EXEC-006` |
| `GAP-DX-02` | `XLF-01-010`、`XLE-GOV-003` |
| `GAP-DX-03` | `XLF-01-011`、`XLF-02-009`、`XLF-03-010` |
| `GAP-DX-04` | `XLF-05-001~002`、`XLF-05-008`、`XLC-CORE-015` |
| `GAP-DX-05` | `XLF-01-013~014`、`XLF-02-005`、`XLE-DEV-001~002`、`XLE-DEV-012` |
| `GAP-DX-06` | `XLF-11-001`、`XLF-11-004`、`XLE-DEV-006~007` |
| `GAP-DX-07` | `XLC-SERVER-001~010`、`XLC-WEB-001~015`、`XLC-STYLE-001~015`、`XLC-PLATFORM-001~010` |
| `GAP-DX-08` | `XLF-05-011`、`XLF-11-014`、`XLE-AI-001~020` |
| `GAP-GOV-01` | `XLF-11-003`、`XLE-GOV-001~008` |
| `GAP-GOV-02` | `XLF-11-001~002`、`XLC-CORE-018~019`、`XLE-DEV-006` |
| `GAP-GOV-03` | `XLF-11-004`、`XLE-DEV-007`、`XLE-OPS-005~010` |
| `GAP-GOV-04` | `XLE-GOV-009`、`XLE-DEV-007`、`XLE-AI-012` |
| `GAP-GOV-05` | `XLF-12-020`、`XLE-GOV-008`、`XLE-AI-014` |
| `GAP-GOV-06` | `XLF-11-002`、`XLE-GOV-006~007`、`XLE-OPS-008~010` |

### 12.2 缺口关闭契约

1. 每个缺口只能有一个责任文档和一个证据 Owner；跨领域内容用链接关联，不复制正文。
2. 状态必须按 `草案 → 待决策 → 已决策 → 原型验证中 → 已验证 → 已稳定` 前进；“已决策”需要批准 RFC/ADR，“已验证”需要实现和自动证据。
3. 关闭证据固定形成 `缺口 ID → RFC/ADR → 规则 ID/接口 → 实现 → 自动测试/基准/审计 → 发布版本` 链路。
4. P0 未关闭不得扩大核心语法或预建生态项目；P1 未关闭不得宣称可用性或性能领先；P2 未关闭不得宣称 1.0、生产级或成熟生态。
5. 借鉴技术必须先通过隔离探针和退出评审；不能因为上游成熟就推定 X-Lang 集成后同样成熟。

### 12.3 借鉴原则

- 借鉴已经被生产验证的机制和工程经验，不复制其他语言的全部表面语法。
- 每个借鉴项必须回答：解决哪个 X-Lang 问题、引入何种复杂度、是否属于语言/库/工具、如何退出。
- 核心只吸收能形成正交语义的能力；编辑器、Web、GPU、AI 和供应链能力优先通过协议、库或独立工具接入。
- 对仍快速变化的技术只做隔离探针，不将其版本或实现细节写进语言可观察语义。

### 12.4 推荐借鉴矩阵

| 来源/技术 | 值得借鉴 | X-Lang 边界 |
|---|---|---|
| Rust | 所有权/借用、Trait、一致性、Edition、Cargo 工作流、错误诊断 | 不照搬全部生命周期语法、宏复杂度和慢编译路径；先证明更小核心 |
| Go | 小语法、快速构建、统一工具链、交叉编译和部署闭环 | 不引入隐式 GC 作为核心；错误、泛型和资源语义保持更强表达力 |
| ML/OCaml 系 | ADT、模式穷尽、局部类型推断和表达式组合 | 公开边界保持显式；不引入难以解释的全程序推断 |
| Swift | 严格并发、值语义、不可复制类型、渐进迁移和优秀诊断 | 只吸收经 RFC 验证的所有权/并发思想，不复制复杂 ABI 历史 |
| Zig | 显式分配器、交叉编译、C 互操作和受控 comptime | 1.0 只保留最小 const-eval；通用 comptime 必须沙箱、确定且有预算 |
| Kotlin/现代协程 | Null Safety、结构化并发、取消和开发体验 | 运行时调度不是语言语义；避免隐藏线程、锁和阻塞 |
| LLVM 22.1.x | 成熟原生优化、对象格式、调试信息和目标覆盖 | 只位于后端适配层；LLVM 类型不得泄漏到前端规范 |
| Cranelift | 快速 Debug/开发构建候选 | 通过 MIR/LLVM 差分和真实编译收益后才加入，不阻塞 P1 |
| MLIR | Tensor/GPU/领域 IR 研究 | 仅用于 P5+ ML/GPU，不反向改变核心 HIR/MIR |
| WebAssembly Component Model + WASI 0.3 | 组件接口、能力边界、可移植插件和异步组件 | 用于后期插件/服务互操作，不进入 1.0 核心或默认 Runtime |
| Tree-sitter | 编辑器增量解析和多编辑器复用 | 作为工具层解析候选，不替代规范 Parser 和符合性语法 |
| LSP 3.18 + DAP | 标准 IDE 与调试协议 | 扩展使用命名空间和能力协商，不发明编辑器专属核心协议 |
| SLSA 1.2 + SPDX 3.0.1 | 来源证明、构建等级、SBOM 和供应链审计 | 属于构建/发布门禁，不污染语言语法 |
| 属性测试、Fuzz、模型检查 | 解析器鲁棒性、内存/并发反例和优化等价 | 与规则 ID 绑定；测试不能替代正式语义，但必须能证伪实现 |

### 12.5 2026 核验入口

下列版本仅作为 2026-08-17 的工程调研基线，不属于语言兼容承诺：Rust 1.97.1、LLVM 22.1.8、Unicode 17.0、WASI v0.3.1、LSP 3.18、SLSA 1.2、SPDX 3.0.1。采用前仍需锁定版本、校验和和升级 ADR。

- Rust：<https://static.rust-lang.org/dist/2026-07-16/channel-rust-1.97.1.toml>
- LLVM：<https://github.com/llvm/llvm-project/releases/tag/llvmorg-22.1.8>
- Unicode：<https://www.unicode.org/versions/Unicode17.0.0/>
- WASI：<https://github.com/WebAssembly/WASI/releases/tag/v0.3.1>
- WebAssembly Component Model：<https://component-model.bytecodealliance.org/>
- Cranelift：<https://cranelift.dev/>
- MLIR：<https://mlir.llvm.org/>
- Tree-sitter：<https://tree-sitter.github.io/tree-sitter/>
- LSP 3.18：<https://microsoft.github.io/language-server-protocol/specifications/lsp/3.18/specification/>
- DAP：<https://microsoft.github.io/debug-adapter-protocol/specification>
- SLSA 1.2：<https://slsa.dev/spec/v1.2/>
- SPDX 3.0.1：<https://spdx.github.io/spdx-spec/v3.0.1/>

### 12.6 不可变调研锚点与升级规则

| 对象 | 核验时间 | 2026-08-17 调研锚点 |
|---|---|---|
| Rust 1.97.1 manifest | 2026-07-16 | SHA-256 `03569b1886ceb5c05276b50c8431ab111de944cd6140fe1fa7d821dd8e0f29cf` |
| LLVM 22.1.8 | 2026-06-16 | Git tag `llvmorg-22.1.8` |
| Unicode 17.0 | 2025-09 | Versioned URL `Unicode17.0.0` |
| WASI 0.3.1 | 2026-08-11 | Release tag `v0.3.1` |
| LSP 3.18 | 2026-08-17 | Versioned path `/lsp/3.18/` |
| DAP snapshot | 2026-08-09 | Commit [`bf8a5d27e8040044b84b863f90916e08925ee811`](https://github.com/microsoft/debug-adapter-protocol/commit/bf8a5d27e8040044b84b863f90916e08925ee811) |
| SLSA 1.2 / SPDX 3.0.1 | 2026-08-17 | Versioned paths `/spec/v1.2/`、`/spdx-spec/v3.0.1/` |
| Reproducible Builds definition | 2026-08-12 | Retrieved HTML SHA-256 `67c75382073160d9cb1253b6991c361eab77309b29f7d2e9f1a6bb91e253eff0` |

以上只是可重放的调研证据，不自动成为构建依赖。正式采用时必须在 RFC/ADR 中锁定 release tag、commit 或下载 SHA-256，并记录核验日期、升级验证和回滚方案；移动频道、`latest`、RC、beta 和 nightly 不能作为稳定基线的唯一证据。Rust/LLVM 升级必须重跑 Bootstrap、IR/ABI、调试信息、正确性与性能验证；Unicode、协议和供应链标准升级必须评估源码兼容、能力协商和旧制品验证。
