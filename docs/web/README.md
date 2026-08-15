---
doc_id: DOC-WEB-CONTRACT
title: X-Lang Web、WASM 与浏览器宿主规范
authority: normative
owner: role/web-platform
backup_owner: role/security-team
version: "0.2.0"
maturity: EXTENDED
status: 草案
phase: P4
last_reviewed: 2026-08-15
applies_to: [wasm, wasi, javascript-bridge, dom, worker, ssr, bundler]
traceability_scope: [XLF, XLC, XLE, SECURITY]
supersedes: [DOC-WEB-CONTRACT-LEGACY]
---

# X-Lang Web、WASM 与浏览器宿主规范

## 1. 范围与目标

本文规定 X 编译到 WASM/WASI 和浏览器时的能力、任务队列、JS/DOM 边界、Worker、SSR/Hydration、打包、SourceMap 与安全降级。浏览器框架、样式 DSL、小程序和云厂商部署是独立适配器；不承诺浏览器像素或全部 Web API 一致。

## 2. 宿主和任务模型

**Profile 能力基线。** Browser 提供 DOM/fetch/storage（受权限策略）、WASI 只提供 manifest 声明的 preopen/clock/random/线程能力、Worker 禁止 DOM 且只允许 clone/transfer/shared memory 规定的值、SSR/Node 提供 server I/O 但禁止浏览器副作用。每个 profile 必须导出 capability manifest；缺失能力统一返回 `Unsupported`，安全策略拒绝统一返回 `SecurityError`，不得静默改用更宽权限。

### RULE-WEB-001：WASM 能力与线性内存

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** 每个 WASM 模块必须声明 imports、exports、线性内存初始/最大页、memory growth、WASI 权限和 feature。未声明的文件、网络、时钟、线程和随机能力必须拒绝。指针只能在模块线性内存有效范围内解引用；JS 不能保存增长前的裸 view 而继续使用。

**解释。** WASM 是能力沙箱，不等于操作系统；WASI 与浏览器宿主能力不同。

**正例。** 模块 manifest 声明只读预打开目录和 fetch adapter，初始化时验证 capability。

**反例。** 未声明的文件 import 被静默提供，报告 X-E8001 undeclared host capability。

**边界。** 浏览器可能禁用 shared memory、SIMD 或 threads；编译器必须生成能力探测和降级分支，不能假设 COOP/COEP。

**诊断/测试/追溯。** X-E8001；TEST-WEB-WASM-001..006；来源 XLF-01-005、XLF-06-007、XLC-WEB-001..003；RFC-WEB-WASM-01（P4）。

### RULE-WEB-002：Event Loop、Task 和 Microtask

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** X async task 必须明确映射到宿主 Promise/microtask 或 timer/task；同步回调不得执行无界阻塞 I/O、长计算或重入 DOM。Promise rejection 必须转为 Result/显式错误；Event Loop 每轮必须允许宿主渲染和取消检查。await 不改变 X 所有权/Drop 规则。

**解释。** microtask 过量会饿死渲染；适配器可分片或转 Worker，但必须保持可观察顺序。

**正例。** fetch(url).await? 后检查 HTTP status 和 AbortSignal。

**反例。** UI click handler 中同步读取 TB 文件，报告 X-W8002 blocking main loop。

**边界。** 浏览器调度顺序由 HTML 标准和宿主决定；X 只保证自身 task 的注册/取消契约，不保证帧率。

**诊断/测试/追溯。** X-W8002、X-E8003 unhandled rejection；TEST-WEB-LOOP-001..005；来源 XLF-12-001、XLC-WEB-004..006；RFC-WEB-LOOP-01（P4）。

### RULE-WEB-003：JS 类型、字符串和 Promise 边界

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** X String 与 JS string 转换必须验证 UTF-8/Unicode scalar 和长度上限；JS number 映射必须说明安全整数范围；Object、Array、BigInt、Error 和 null/undefined 使用显式转换。Promise 只能映射为 Future/Result，并声明 abort、异常和 owner。

**解释。** 动态 JS 值不能自动推断为任意 X 类型。大型 buffer 优先使用受控 ArrayBuffer view，view lifetime 不得超过底层内存。

**正例。** JsValue::as_u64_checked()；Future::from_promise(p, abort_signal)。

**反例。** 直接把 JS number 转 u64 导致精度丢失，报告 X-E8004 unsafe numeric conversion。

**边界。** BigInt 在 WASM ABI 中可用性依浏览器 Tier；不支持时返回 Unsupported，而不是转 f64。

**诊断/测试/追溯。** X-E8004；TEST-WEB-JS-001..006；来源 XLF-06-007、XLC-WEB-007..009、XLC-FFI-010；RFC-WEB-JS-01（P4）。

## 3. DOM、Worker 和组件生命周期

### RULE-WEB-004：DOM 线程与 Worker

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** DOM 对象只能在拥有该文档的宿主线程访问；Worker 只能使用可转移、可结构化克隆或 SharedArrayBuffer 且满足安全隔离的值。跨线程消息必须定义 clone/transfer owner、关闭和取消。X 编译器不得将不可 Send 的 DOM 引用捕获到 Worker。

**解释。** Worker 不是自动共享内存；Transfer 会使发送方失效，SharedArrayBuffer 需要宿主隔离头。

**正例。** post_message(move bytes) 后发送方不再使用 bytes。

**反例。** 把 Element 引用传入 Worker，报告 X-E8010 DOM not Send。

**边界。** Worker terminate 可跳过 JS finally；X 资源必须在可达范围内 Drop，宿主强制终止不作保证。

**诊断/测试/追溯。** X-E8010；TEST-WEB-WORKER-001..005；来源 XLF-06-007、XLC-WEB-010..011；RFC-WEB-WORKER-01（P4）。

### RULE-WEB-005：SSR、Hydration 与组件资源

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** SSR 输出必须由同一输入、locale、时区、随机种子和 feature manifest 生成可重现 HTML/属性；Hydration 必须检测结构/文本/事件绑定不一致并产生可诊断错误。组件卸载必须取消事件订阅、任务和 observer；服务端不得执行浏览器专属副作用。

**解释。** hydration mismatch 不是静默修复的理由；适配器可选择局部重建，但必须报告并保留错误边界。

**正例。** SSR 将 locale、build id 和 data version 注入受校验的 bootstrap 数据，客户端复用同一版本。

**反例。** SSR 使用当前时间，客户端立即不同，报告 X-E8011 nondeterministic hydration。

**边界。** 浏览器扩展、时区数据库和字体渲染可能造成非结构差异；结构性 mismatch 必须可定位。

**诊断/测试/追溯。** X-E8011；TEST-WEB-SSR-001..006；来源 XLF-06-007、XLC-WEB-012..013、XLE-DATA-003；RFC-WEB-SSR-01（P4）。

## 4. Bundler、SourceMap 和安全

### RULE-WEB-006：构建、版本和 SourceMap

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** Bundler 必须记录输入文件 hash、X/LLVM/wasm-bindgen 版本、target、feature、依赖 lockfile、tree-shaking/code-split 结果和 source map 版本。SourceMap 必须将 X span 映射到 JS/WASM/生成模板，路径可脱敏；HMR 仅可替换兼容模块，状态迁移不确定时必须回滚整模块。

**解释。** 可复现 bundle 是调试和供应链证据。HMR 是开发能力，不是生产热补丁承诺。

**正例。** 生产默认不上传源码 SourceMap，内部符号制品按访问控制保存。

**反例。** SourceMap 暴露绝对路径和秘密，报告 X-E8020 source map privacy。

**边界。** 浏览器缓存、CDN、动态 import 和 service worker 版本需 manifest；旧 bundle 必须可回滚。

**诊断/测试/追溯。** X-E8020；TEST-WEB-BUNDLE-001..006；来源 XLF-11-004、XLF-11-005、XLC-WEB-014..015、XLE-OPS-008；RFC-WEB-BUNDLE-01（P4）。

### RULE-WEB-007：Web 安全默认

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** 适配器不得默默放宽 CSP、CORS、Origin、Trusted Types、COOP/COEP、Permissions Policy 或 cookie SameSite。网络/DOM API 必须声明来源、凭据、CSRF/XSS 编码和用户授权；HTML/URL/JS/CSS 注入默认拒绝或显式 escape。

**解释。** 安全策略由部署宿主决定，语言只能提供安全默认和诊断，不能替用户选择允许任意 origin。

**正例。** fetch 使用受限 origin allowlist 和 AbortSignal；模板默认 escape。

**反例。** 为了让跨域请求成功自动设置 wildcard + credentials，报告 X-E8021 insecure policy widening。

**边界。** WebView/小程序权限是平台特定；能力不可用返回 SecurityError/Unsupported。

**诊断/测试/追溯。** X-E8021；TEST-WEB-SEC-001..008；来源 XLF-06-007、XLF-11-006、XLC-WEB-014、XLE-AI-004；RFC-WEB-SEC-01（P4）。

## 5. 平台矩阵、降级和验证

| 能力 | 浏览器 Tier 1 | WASI | Web Worker | SSR/Node | 降级 |
|---|---|---|---|---|---|
| DOM | supported | unsupported | 主线程 proxy | adapter | explicit Unsupported |
| fetch | supported | host capability | supported | node adapter | Result<Unsupported> |
| File | user picker/OPFS | preopen | transferable | fs adapter | no silent host file |
| thread | Worker/shared memory 条件 | threads 条件 | worker | OS thread | serial executor |
| timer | browser task | wasi clock | supported | OS clock | virtual clock tests |
| SourceMap | devtools | custom debugger | worker map | node inspector | internal artifact |

测试必须使用 WPT 子集、浏览器 E2E、SSR/CSR 黄金、Worker race/取消、CSP/CORS/Trusted Types、恶意 URL/HTML、bundle 重现和 source map 隐私测试。性能只记录首屏/交互 P50/P95/P99、WASM 体积和内存峰值，不作所有设备承诺。

## 6. 待决 RFC

| RFC | 候选 | 门禁 | 最迟 |
|---|---|---|---|
| RFC-WEB-WASM-01 | WASI Preview/Component Model | capability、memory、host matrix | P4 |
| RFC-WEB-LOOP-01 | Future 到 microtask/task 映射 | ordering、cancel、长任务 | P4 |
| RFC-WEB-JS-01 | JsValue 显式转换 API | numeric/UTF-8/Promise | P4 |
| RFC-WEB-WORKER-01 | clone/transfer/shared memory | Send、COOP/COEP、泄漏 | P4 |
| RFC-WEB-SSR-01 | hydrate mismatch 与状态迁移 | determinism、a11y、回滚 | P5 |
| RFC-WEB-BUNDLE-01 | manifest/source map/HMR | reproducibility、privacy、rollback | P4 |
| RFC-WEB-SEC-01 | 安全策略 helper | OWASP/WPT、CSP/CORS | P4 |

原始愿景中的小程序转译、WebGPU、冷启动快照和 HMR 均保持独立适配器；未通过 RFC 不得写入核心语言或默认 Web runtime。

## 7. 全栈与部署专题

HTTP/RPC 服务、可信代理、容器、Kubernetes、Serverless、配置秘密、Canary 和回滚的实施边界见[全栈服务、云原生与部署实施规范](./fullstack-cloud-deployment.md)。该专题消费本文件的宿主语义，不改变 X-Lang 核心语言规则。
