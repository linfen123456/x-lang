---
doc_id: DOC-RUNTIME-OBSERVABILITY
authority: implementation
owner: role/runtime-team
backup_owner: role/architecture
version: "1.1"
maturity: EXTENDED
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-09-005, XLF-09-006, XLF-10-013, XLF-11-006, XLF-12-020]
---
# 运行时日志、指标、Trace 与故障制品

> 状态：草案｜Owner：`role/runtime-team`

## 观测接口

`LogEvent` 字段为 `timestamp:MonotonicDuration`、`level:Level`、`component:String`、`request_id:RequestId`、`task_id:TaskId?`、`message:String`、`attributes:Map<String,RedactedValue>`；`Metric` 为 `name:String`、`kind:Counter|Gauge|Histogram`、`value:f64`、`labels:BoundedMap`；`Span` 为 `trace_id:TraceId`、`span_id:SpanId`、`parent:SpanId?`、`start/end:MonotonicDuration`、`status`、`attributes`。标签键和值有长度/基数上限。

`Observer::emit(event, budget, cancel)->Result<(),ObserveError>` 前置是 sink 已初始化、字段通过脱敏与大小校验；后置是成功写入内存/批量队列或明确丢弃计数。观测不能阻塞业务线程；队列满执行采样/丢弃，不反向触发 panic。默认不记录秘密、完整 payload、token、路径中的用户数据和原始内存。

## Trace Context、Profiler 和 coredump

Task/Channel/HTTP/I/O 边界的 Trace Context 只在 Profile opt-in 时传播，并记录采样率和开销。Profiler 与 coredump 使用 quota、权限和保留期；coredump manifest 包含 runtime/compiler/target/ABI hash、panic code、脱敏线程栈和资源统计，不包含未授权堆内容。时间旅行 Replay 仅为研究能力，不进入稳定默认行为。

## 负向测试、资源和回滚

覆盖日志注入、超长属性、标签爆炸、trace 断链、时钟跳变、sink 失败、磁盘满、网络不可用、采样配置错误、panic 期间观测和 secrets 扫描。`TEST-RUNTIME-OBS-001` 验证脱敏，`TEST-RUNTIME-OBS-002` 验证高负载下无阻塞，`TEST-RUNTIME-OBS-003` 验证关联 ID。队列 64 MiB、单事件 64 KiB、属性 32 个、标签基数 10k、sample 10% 均为 `candidate_default`，遵循 [运行时 Budget 治理](./README.md#资源预算治理)；采样比例是策略候选，不是准确率承诺。观测 schema minor 追加，回滚时关闭 exporter/恢复上一 sink，不改变业务语义。
