---
doc_id: WEB-CONTRACT
title: X-Lang Web 与浏览器宿主契约
status: draft
maturity: EXTENDED
owner: web-platform
trace: [XLF-01-005, XLF-06-007, XLC-WEB-001..015, XLC-SERVER-001..010]
---

# X-Lang Web 与浏览器宿主契约

## 目标与非目标

定义 WASM/WASI、JS/DOM、Event Loop、Worker、SSR/Hydration、SourceMap、打包和 Web 安全边界。浏览器框架、样式 DSL 和云厂商部署是独立生态；不承诺所有浏览器像素或行为完全一致。

## 宿主契约

同步 X-Lang 代码不得阻塞浏览器主线程；Promise/Task 映射必须明确取消、异常和微任务顺序。WASM 线性内存、导入导出、能力权限和资源释放必须显式声明。SSR 与 Hydration 对同一输入应产生可诊断的不一致错误。

## 正反例

正例：`fetch(url).await?` 显式处理网络错误和取消。反例：在 UI 回调中执行无界同步 I/O，导致事件循环饥饿。

## 边界、安全与性能

CORS、CSP、Trusted Types、Origin、Worker 隔离和凭据策略由宿主配置，不由编译器默默放宽。每个浏览器 Tier 记录最低版本、WPT 子集、首屏/交互 P95、WASM 体积和 SourceMap 隐私。

## 测试与回滚

使用 `tests/web-platform`、浏览器 E2E、SSR/CSR 黄金快照、WPT 子集和安全场景测试。浏览器 API 变更通过适配器和能力探测回滚到降级实现；旧 bundle 保留可复现构建。

## P3–P6 入口

- P3：WASM/WASI、JS 胶水、Bundler、SourceMap。
- P4：DOM/Worker、SSR/Hydration、HTTP API 与部署。
- P5：组件框架、HMR、边缘运行时和移动 WebView。
- P6：小程序适配器、实验性 WebGPU 与跨设备研究。
