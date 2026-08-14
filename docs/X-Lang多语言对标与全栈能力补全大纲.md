# X-Lang 多语言对标与全栈能力补全大纲

> 总纲：[X-Lang 企业级完整文档体系总纲](./X-Lang企业级完整文档体系总纲.md)  
> 大纲版本：1.0-outline｜状态：派生 Backlog 已冻结｜初始基线：2026-08-14｜复审：2026-08-15  
> 性质：基于 Go、Rust、C、Python、Java、JavaScript 与 CSS 的派生需求，不属于 12 份原始文档本身。  
> 目标：补齐工业语言的核心语义、生产工具、互操作、服务器、Web/CSS 和平台交付能力，同时避免把所有语言特性无原则堆入核心。  

## 1. 定位与取舍

X-Lang 的可实现定位是：以所有权和静态类型提供 Rust 级安全方向，以 LLVM/AOT 提供 C 级原生性能，以结构化并发提供 Go 级服务端体验，以统一工具链和稳定生态吸收 Java 的工程优势，以受限动态边界和高质量 REPL/Notebook 吸收 Python 的开发效率，通过 WASM、JS/DOM 互操作和独立样式系统覆盖 Web。目标不是复制 JVM、Python 元类、JavaScript 原型链或 CSS 全部历史行为。

### 1.1 采用、改造和拒绝原则

| 来源 | 直接采用 | 受限改造 | 不进入核心 |
|---|---|---|---|
| Go | 简单工具链、Channel、结构化并发、诊断工具 | 接口满足、调度器可观察性 | 隐式运行时魔法 |
| Rust | 所有权、Trait、Result、no_std、Cargo 经验 | 宏、unsafe、复杂泛型按阶段引入 | 无收益的语法复杂度 |
| C | ABI、原生布局、裸机、硬件控制 | 仅在 unsafe/FFI 暴露危险语义 | 预处理器文本替换和普遍 UB |
| Python | REPL、Notebook、数据/AI、FFI | `Dynamic` 仅作边界类型 | Monkey Patch、全局动态语义 |
| Java | 企业兼容、诊断、制品、LTS | Managed 模式需单独 RFC | 为兼容而复制 JVM/class 继承 |
| JavaScript | Event Loop、Promise 桥、DOM/Web API、ESM | 动态对象仅在 JS 边界 | 原型链和隐式类型转换 |
| CSS | 布局、响应式、主题、动画、无障碍 | 设计为 `x-style` 独立 DSL | 把 CSS 级联塞入核心语言 |

### 1.2 派生需求成熟度、状态与关闭规则

`XLC-*` 是对标派生需求，不能证明其来自 12 份原始材料，也不自动形成路线承诺。下表为各系列的默认分级/状态；单项另有说明时以单项为准。

| ID 范围 | 默认成熟度/状态 | 例外与进入稳定条件 |
|---|---|---|
| `XLC-CORE-001~020` | `CORE/待决策` | `009 Specialization` 为 `EXPERIMENTAL/待决策`；未通过 RFC、形式规则和符合性设计不得实现为稳定语义。 |
| `XLC-EXEC-001~012` | `EXTENDED/待阶段实施` | MIR 参考执行可作为 CORE 验证基础；快速后端须经 ADR，所有工具须有统一 SourceMap。 |
| `XLC-FFI-001~012` | `EXTENDED/待阶段实施` | C ABI 稳定子集可先行；Python/JNI/JS 分别版本化，不共享“全兼容”承诺。 |
| `XLC-WEB-001~015` | `EXTENDED/待阶段实施` | WASM 可先于框架；浏览器宿主、SSR 和工具链通过 G4 后才能标记稳定。 |
| `XLC-STYLE-001~015` | `EXTENDED/待阶段实施` | 始终属于独立 DSL/生态；不因实现成熟而转入核心语法。 |
| `XLC-SERVER-001~010` | `EXTENDED/待阶段实施` | 标准库只保留底层 I/O；框架和云适配独立发布。 |
| `XLC-PLATFORM-001~010` | `CORE治理/草案` | Tier 1 的最低版本、签名和支持期必须在 1.0 前转为已决策并有 CI 证据。 |

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

## 3. `XLC-CORE`：核心语言派生需求

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
| XLC-WEB-006 | 组件模型 | Props、State、Lifecycle、Context、Error Boundary | x-web-ui | 行为契约和可访问性 |
| XLC-WEB-007 | 响应式状态 | Signal/Computed/Effect、批处理、循环检测 | x-reactivity | 确定更新和泄漏测试 |
| XLC-WEB-008 | Router/Form | 路由、导航、表单、验证、提交和错误 | x-web-framework | 浏览器 E2E |
| XLC-WEB-009 | SSR/Hydration | 同构输出、序列化、安全、Mismatch | x-web-ssr | SSR/CSR 一致性 |
| XLC-WEB-010 | HMR | 模块边界、状态保留和失败回滚 | x-web-dev-server | 编辑到更新延迟基准 |
| XLC-WEB-011 | Bundler | 依赖图、资产、插件沙箱、缓存 | x-web-bundler | 可复现构建 |
| XLC-WEB-012 | Tree Shaking/Code Split | ESM 图、副作用、动态导入、Chunk | x-web-bundler | 体积和加载测试 |
| XLC-WEB-013 | SourceMap | X→MIR/WASM/JS/CSS 多级映射 | x-source-map | 浏览器断点准确 |
| XLC-WEB-014 | Dev/Deploy Adapter | 本地服务器、代理、静态/边缘/Node 部署 | x-web-cli | 模板 E2E |
| XLC-WEB-015 | Web 安全默认 | XSS、CSP、Trusted Types、CSRF、依赖完整性 | x-web-security | OWASP 场景测试 |

## 7. `XLC-STYLE`：CSS、布局、主题和无障碍

样式系统属于 `ecosystem/x-style`，不改变 X-Lang 核心求值语义。首版可编译为浏览器 CSS，也可降级为桌面/移动渲染树属性。

| ID | 能力 | 关键内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLC-STYLE-001 | 选择器 | type/class/id/attribute、组合器、伪类/伪元素 | x-style-selector | CSS Selector 对照测试 |
| XLC-STYLE-002 | 级联 | origin、specificity、source order、important 策略 | x-style-cascade | 确定性级联测试 |
| XLC-STYLE-003 | 继承与初始值 | inherited/non-inherited、unset/revert | x-style-cascade | 属性矩阵 |
| XLC-STYLE-004 | 变量与 Design Token | 自定义属性、类型 Token、fallback、主题 | x-style-token | 循环和作用域测试 |
| XLC-STYLE-005 | 单位与颜色 | 长度、角度、时间、百分比、色彩空间 | x-style-values | 解析/插值/平台测试 |
| XLC-STYLE-006 | Block/Inline | Formatting Context、盒模型、margin collapse | x-layout | WPT 布局子集 |
| XLC-STYLE-007 | Flexbox | 主/交叉轴、flex basis、wrap、gap | x-layout-flex | 浏览器截图差分 |
| XLC-STYLE-008 | Grid | track、area、auto placement、subgrid 取舍 | x-layout-grid | 布局黄金测试 |
| XLC-STYLE-009 | 定位和层叠上下文 | relative/absolute/fixed/sticky、z-index | x-layout | 滚动/嵌套测试 |
| XLC-STYLE-010 | 响应式查询 | media/container、viewport、DPI、能力查询 | x-style-query | 多尺寸/设备测试 |
| XLC-STYLE-011 | 动画与过渡 | keyframe、transition、transform、取消、reduced-motion | x-style-animation | 时间线和合成测试 |
| XLC-STYLE-012 | 样式隔离 | scoped/module/shadow boundary、全局逃逸 | x-style-scope | 组件冲突测试 |
| XLC-STYLE-013 | SSR 样式 | 提取、去重、关键 CSS、hydration 顺序 | x-style-ssr | 无闪烁和一致性测试 |
| XLC-STYLE-014 | 无障碍样式 | 对比度、焦点、缩放、高对比、reduced-motion | x-a11y | WCAG 自动和人工检查 |
| XLC-STYLE-015 | 多后端降级 | CSS、Skia、原生视图属性和不支持诊断 | x-style-codegen | 平台能力矩阵 |

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
