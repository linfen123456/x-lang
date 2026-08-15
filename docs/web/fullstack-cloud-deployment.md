---
doc_id: DOC-WEB-FULLSTACK-CLOUD-DEPLOYMENT
authority: implementation
owner: role/web-platform
backup_owner: role/operations-team
version: "0.1"
maturity: EXTENDED
status: 草案
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [XLF, XLC, XLE, SECURITY]
---
# X-Lang 全栈服务、云原生与部署实施规范

> 文档性质：实施规范草案
> 成熟度：服务端基础 `EXTENDED`，Web/云平台适配 `EXTENDED`，Serverless 快照与生产影子 `EXPERIMENTAL`
> 目标阶段：P3 服务端最小切片，P4 Web/容器/Kubernetes，P5 Serverless 与多平台扩展
> 相关文档：[Web/WASM 宿主规范](./README.md)｜[系统与网络标准库](../stdlib/system-io-network.md)｜[运维规范](../operations/README.md)

## 1. 目标、读者与非目标

本文面向服务框架、Web 运行时、部署工具、平台工程和应用团队，规定从 HTTP 请求进入到构建、发布、扩缩容、观测、回滚的完整责任链。它把原始资料中的 HTTP/QUIC/gRPC、Web、SSR、Kubernetes、Serverless、FaaS、冷启动、本地云环境和影子环境设想，转成分阶段可交付的工程切片。

本文不把 Web 框架或云厂商注解加入核心语法，不自研 Kubernetes、TLS 或数据库，不承诺“一次编写在所有宿主行为完全一致”，也不把生产凭据编译进制品。固定冷启动、吞吐或尾延迟数字均是待测目标。

## 2. 架构边界

```text
Client/Browser
  → Edge/LB/TLS
  → HTTP Adapter
  → Router/Middleware
  → Application Service
  → Domain/Ports
  → DB/Message/Object Storage adapters
  → Observability + Policy

Source + lockfile + target manifest
  → x build/test
  → signed artifact/SBOM/provenance
  → image/package
  → deploy controller
  → canary/health/SLO
  → promote or rollback
```

框架负责协议适配、路由、middleware 生命周期、请求上下文和优雅停机；业务代码负责领域不变量和幂等；标准库负责网络、时间、取消和资源；平台适配器负责容器、Kubernetes、云事件与秘密引用；运维系统负责发布与恢复。任何层都不得通过隐式全局变量越过责任边界。

## 3. 服务应用契约

### 3.1 请求与响应

```x
struct RequestContext<'a> {
    request_id: RequestId,
    trace: TraceContext,
    deadline: Option<Instant>,
    cancel: &'a CancelToken,
    peer: PeerIdentity,
    quota: &'a RequestQuota,
}

trait Service<Req, Res> {
    async fn call(&self, request: Req, ctx: &RequestContext)
        -> Result<Res, ServiceError>
}
```

上述签名是非规范性接口草图；正式 RFC 必须补齐请求/响应所有权、阻塞与取消点、复杂度、资源上限和平台。请求体是有界流，不能默认读入内存；响应只有在 Header 提交前可以安全替换。框架必须区分解析失败、认证失败、授权失败、业务冲突、限流、上游失败、超时、取消和内部错误，并将稳定机器码映射到协议状态。内部堆栈、SQL、密钥和个人数据不返回客户端。

### 3.2 路由、中间件与状态

路由匹配顺序必须确定，冲突在构建或启动时报告。Middleware 顺序显式为：请求进入按注册顺序，响应/错误退出按逆序；认证在授权前，限流位置由威胁模型决定。共享状态必须声明线程安全和关闭顺序，禁止 request-local 数据泄漏到其他请求。

### 3.3 取消、deadline 与断连

客户端断连、服务器 shutdown、上游 deadline 与资源配额都可触发取消。取消沿调用图向下传播，但数据库提交、消息发布、文件写入等操作可能已产生效果；业务必须使用幂等键、事务或补偿处理未知结果。框架不能把 `Cancelled` 一律转换成“未执行”。

## 4. HTTP、RPC 与韧性

### 4.1 协议支持顺序

P3 先交付 HTTP/1.1 服务端与客户端；P4 增加 HTTP/2、WebSocket 与基于成熟 IDL 的 RPC；P5 在独立协议包中增加 HTTP/3/QUIC。每个版本均通过标准互操作套件，不共享未经验证的自研解析器。

限制至少包括：请求行、URL、Header 数/总大小、Body、并发流、压缩比、空闲时间、每连接请求数和响应队列。Chunked、Content-Length 冲突、请求走私、慢速请求和压缩炸弹必须有负向案例。

### 4.2 重试、超时、熔断和负载保护

超时预算从入口向下分配，不在每层重新开始完整时长。重试只用于幂等请求或显式幂等键，并使用指数退避、抖动、最大次数和总体 deadline。熔断器状态按目标服务/操作隔离，半开探针有并发上限。

服务器按并发、队列、内存和下游容量做 admission control；过载时快速返回结构化错误，而非无限排队。背压贯穿 Body Stream、RPC Stream、消息与数据库池。

### 4.3 API Schema 与演进

公开 API 使用版本化 Schema，记录字段 required/optional、默认、约束、错误码、分页、幂等和弃用。兼容策略覆盖 N-1/N 客户端；删除字段先废弃，未知枚举值必须可处理。生成 SDK 不能替代协议黄金测试。

### 4.4 反向代理与客户端身份

应用默认只信任直接 TCP 对端，不信任任意客户端提交的 `Forwarded`、`X-Forwarded-For`、`X-Forwarded-Proto` 或 Host。部署配置必须声明 trusted proxy 的 CIDR/身份、最大代理跳数和采用的标准头；入口代理先删除外部伪造头，再追加规范化 hop。应用从右向左剥离已信任 hop，遇到首个不可信 hop 即停止，并同时保留原始对端与解析后的客户端地址用于审计。

协议/安全决策（HTTPS redirect、Secure Cookie、Origin、绝对 URL、限流）只能使用经过 trusted-proxy 策略验证的 scheme/host/client IP。多个 `Forwarded` 值、IPv6/端口、混合旧头、超长链和代理配置漂移必须有负向测试；配置不明确时 fail closed 并使用直接对端。

## 5. Browser、SSR 与前后端协同

浏览器运行时、JS/WASM 边界、Worker、SourceMap 与 Web 安全以 [Web/WASM 宿主规范](./README.md)为唯一规则。本文件只规定全栈协同：

- SSR 与客户端使用同一 API Schema、locale、时区数据和 build manifest。
- Bootstrap 数据通过安全序列化嵌入，默认 HTML escape，并受 CSP/nonce 约束。
- Hydration mismatch 产生稳定诊断；可局部重建但不得静默吞错。
- BFF/Server Action 必须保留认证、CSRF、Origin 与权限检查，不能因“同仓代码”跳过边界。
- 静态资源文件名内容寻址，HTML 与 Service Worker 的缓存版本协调，避免新旧 bundle 混用。

CSS/样式语义由 [x-style 规范](../style/README.md)负责；服务框架不解释选择器、布局或无障碍规则。

## 6. 配置、秘密与环境

配置统一按 `default → system file → user file → project file → environment → CLI/平台覆盖` 合并，并可查询来源。部署平台注入属于最高优先级的显式 CLI/平台覆盖，不另造隐式层。启动时完成解析和验证；错误配置不进入部分运行状态。动态配置有版本、校验、审计和回滚，不能绕过代码支持的范围。

秘密只通过引用注入，例如文件描述符、挂载文件、KMS/Vault handle 或短期 Token；禁止写入源码、镜像层、命令行、构建日志、环境快照或浏览器 bundle。秘密轮换需要双版本读取窗口和连接重建策略。

`x env` 仅生成本地容器/模拟器配置和短期凭据引用，默认与生产隔离。访问远端只读数据也需要审批、脱敏和销毁；不得复制生产 Token 或把远端日志自动开启。

## 7. 构建制品与供应链

每个发布单元包含：应用制品、target/profile、依赖锁、SBOM、来源证明、配置 Schema、数据库迁移、健康探针版本和调试符号引用。构建固定时间戳来源、文件顺序和随机 seed；两次隔离构建用于验证可复现性。

容器镜像使用最小基础镜像、非 root 用户、只读根文件系统、明确入口与信号处理，不内置构建工具或秘密。依赖和基础镜像按 CVE/许可证策略扫描；例外有 Owner、期限和风险接受。

## 8. 容器与 Kubernetes

### 8.1 运行契约

进程响应 SIGTERM/平台终止通知：停止接收 → 标记 NotReady → 等待在途请求到 grace deadline → 取消剩余任务 → flush 有界遥测 → 退出。SIGKILL 和节点断电不保证清理，因此持久状态必须由事务与恢复保证。

Readiness 表示可接流量，Liveness 只检测无法自恢复的死锁/失活；Startup Probe 保护慢启动。健康检查不得依赖所有下游都健康，否则故障会放大重启风暴。

### 8.2 资源与扩缩容

CPU/内存 request/limit 与运行时线程、连接池、缓存和队列容量协调。检测容器配额而非宿主总资源。OOMKilled、CPU throttling、文件句柄和 ephemeral storage 都有独立告警。

HPA 的指标与业务容量相关，缩容先排空。PodDisruptionBudget、反亲和和滚动发布参数避免同时丢失多数副本。Stateful 组件另有数据迁移、备份与恢复流程，不能套用无状态回滚。

## 9. Serverless 与事件适配

FaaS 适配器将厂商事件转换为版本化中立 Schema，再调用普通 `Service`；生成胶水代码必须可审查、可离线测试。事件源、重试、死信、批次、最大并发、幂等键和部分失败语义逐适配器记录。

冷启动快照属于 P5 `EXPERIMENTAL`：只允许冻结无秘密、无活动 Socket、无线程、无未完成 I/O 的只读初始化状态。恢复后执行 hook 重建随机源、时钟、连接、TLS 和身份。若快照版本、CPU、运行时 ABI 或配置不匹配，则回退普通启动并记录原因。

不承诺固定毫秒冷启动；基准需记录平台、区域、内存规格、包大小、样本和 P50/P95/P99。

## 10. 可观测性与隐私

Trace Context 通过 HTTP/RPC/消息/Task 显式传播；来自外部的 trace ID 先验证。结构化日志包含时间、级别、service、version、environment、request/trace/change ID 和稳定事件码。Metrics 控制 label 基数，不能把用户 ID、URL 全路径或异常文本用作 label。

采样、日志级别和 Profile 动态可调但有策略上限。遥测失败不得阻塞业务主路径，严重审计事件除外。SourceMap、Core dump、请求 Body 和 AI 上下文是敏感制品，按最小权限、加密、保留期和删除策略管理。

## 11. 发布、迁移与回滚

```text
Build → Unit/Contract → Image scan → Staging E2E
→ Migration precheck → Canary → SLO observe
→ Progressive rollout → Post-verify → Close or rollback
```

Canary 按版本和租户/流量标识可区分，至少观察错误率、延迟、资源、业务正确性和安全事件。回滚优先回到上一签名制品；数据库采用 Expand → Migrate → Contract，应用 N 与 N-1 在迁移窗口均可读写。消息 Schema 使用兼容 Reader，不能依靠同时发布。

回滚触发包括数据损坏、认证绕过、显著 SLO 回归、无法诊断错误、迁移不一致和签名/来源异常。若回滚本身不安全，则停止写入、隔离流量并执行恢复 Runbook。

## 12. 平台矩阵

| 部署目标 | 稳定目标 | 特有边界 | 回退 |
|---|---|---|---|
| Linux 原生服务 | P3/P4 | POSIX Signal、证书、路径、日志 | 上一签名二进制 |
| Windows 原生服务 | P3/P4 | Service/Console、证书、路径、Event Log | 上一签名二进制 |
| macOS 原生服务 | P3/P4 | launchd/Signal、Keychain、路径、签名公证 | 上一签名二进制 |
| Linux 容器/Kubernetes | P4 | cgroup、只读 FS、非 root、graceful shutdown | ReplicaSet/镜像回滚 |
| 浏览器/WASM | P4 | Event Loop、CSP、Host capability | JS/服务端替代或 Unsupported |
| WASI/边缘 | P4/P5 | Preview/Host、文件/网络/时钟能力 | 普通服务部署 |
| FaaS | P5 | 事件、时限、冷启动、重试 | 无快照普通启动 |
| Android/iOS/小程序 | P5/P6 | 生命周期、权限、商店/厂商规则 | 独立适配器，不阻塞主线 |

## 13. 最小可落地切片

### P3-FS-1：单体 HTTP 服务

交付 Router、Service、RequestContext、HTTP/1.1、JSON、结构化错误、取消、优雅停机和基础 Trace。在 Linux、Windows、macOS 分别完成原生进程验证，不含 ORM、Kubernetes、HTTP/2 或 AI 推理。

### P4-FS-2：生产容器服务

增加 TLS adapter、HTTP/2、配置/秘密引用、连接池、迁移、容器、Kubernetes 探针、资源预算、Canary 和回滚。验收一个端到端示例：请求 → DB 事务 → 消息 outbox → Trace → 灰度发布 → 版本回滚。

### P4-FS-3：浏览器全栈

增加 WASM/JS bridge、SSR/Hydration、静态 bundle manifest、SourceMap 隐私和 CSP。验收无障碍基础、恶意输入、旧 bundle、慢网和客户端取消。

### P5-FS-4：边缘与 Serverless

增加 WASI/FaaS 中立事件 Schema、适配器、离线事件测试和可选快照。单一厂商先达标，再扩厂商；不以生成多个模板代替运行验证。

## 14. Planned 测试与验收

- `TEST-FS-HTTP-001`：请求走私、Header/Body 上限、慢请求、断连与短响应。
- `TEST-FS-PROXY-001`：伪造/混合 Forwarded 头、trusted proxy CIDR、最大跳数、Host/scheme 与直接对端回退。
- `TEST-FS-CANCEL-001`：入口 deadline 传播到 DB/消息，未知提交结果不误报未执行。
- `TEST-FS-RESILIENCE-001`：重试预算、熔断半开、过载拒绝和下游恢复。
- `TEST-FS-WEB-001`：SSR/Hydration、CSP、CSRF、XSS、旧缓存和 SourceMap 脱敏。
- `TEST-FS-K8S-001`：NotReady 排空、SIGTERM、OOM、CPU 限流和滚动发布。
- `TEST-FS-MIGRATE-001`：N-1/N 双版本、迁移中断、前滚与应用回滚。
- `TEST-FS-FAAS-001`：事件重复/乱序/部分失败、死信、普通与快照启动对照。
- `TEST-FS-SUPPLY-001`：签名、SBOM、恶意依赖、双构建与镜像回滚。

所有测试目前为 planned。Stable 候选要求真实环境记录、制品哈希、平台、负载、预期/实际、故障注入和回滚结果，并接受[CI 门禁](../ci/pipeline-and-gates.md)与[SLO/事故规范](../operations/slo-incident-rollback.md)检查。

## 15. 安全审查清单

- 入口协议解析、认证、授权、租户隔离、CSRF/XSS/SSRF 和请求走私。
- 构建脚本、容器、插件、模板、SourceMap、依赖与注册表供应链。
- 秘密创建、注入、轮换、撤销、日志/Core/Trace/AI 上下文脱敏。
- 数据分类、保留、跨区域、备份、恢复和删除。
- 云 API 最小权限、短期身份、审计和 Break-glass。

未通过安全审查时关闭相应适配器或发布能力，不影响本地核心编译器和语言语义。

## 16. 原始资料追溯

| 来源 | 需求回归 |
|---|---|
| `1.txt` | XLF-01-005、XLF-01-011～XLF-01-014：WASM、跨平台库、工具与 UI 边界 |
| `4.txt` | XLF-04-008、XLF-04-010～XLF-04-012：HTTP/QUIC/RPC、服务与可审计编排 |
| `6.txt` | XLF-06-007、XLF-06-010：服务端、推理入口、多目标 PAL |
| `9.txt` | XLF-09-004～XLF-09-007、XLF-09-012～XLF-09-015：观测、配置、DB、调度与构建缓存 |
| `10.txt` | XLF-10-001、XLF-10-009、XLF-10-013～XLF-10-017：错误、流、信号、插件、绑定、文档 |
| `11.txt` | XLF-11-004、XLF-11-007、XLF-11-010～XLF-11-011：供应链、Watch、Serverless 快照和事件 |
| `12.txt` | XLF-12-018～XLF-12-020：本地云环境、受控影子环境和基准治理 |

对原始材料的调整只发生在实现机制：保留用户价值，删除隐式提权、秘密固化、固定性能、通用热状态替换和“本地等同生产”等不安全承诺。
