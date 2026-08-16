---
doc_id: DOC-TOOLS-TEST-RUNNER
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.2"
maturity: CORE
status: 草案
phase: P3
last_reviewed: 2026-08-16
traceability_scope: [XLF-02-014, XLF-03-002, XLF-11-004, XLF-11-013, XLF-12-020]
---
# `xtest` 测试运行器

> 状态：草案｜Owner：`role/tooling-team`

## 目标、边界与依赖

`xtest` 将可重复的测试发现、调度、隔离、判定和证据收集统一到一个执行模型，供语言一致性、编译器、运行时、标准库和工具链复用。它不把“测试已定义”误写为“产品已通过测试”，也不允许用重试后的偶然成功覆盖首次失败。

运行器依赖冻结的工具链、TargetSpec、测试清单、资源 Profile 和制品格式。基准测试只负责测量与报告，阈值由批准的性能 Budget ADR 或基线策略提供；模糊测试只负责执行给定预算，不以单次“未发现崩溃”证明安全。

## 发现、指纹与计划冻结

发现器从工作区 Manifest、测试属性和批准的测试目录读取用例。测试 ID 必须在工作区内唯一且稳定，不得由枚举顺序生成。路径通过目录句柄解析并限制在授权根内；symlink、重解析点和动态生成清单不得绕过工作区边界。

`DiscoveryFingerprint` 至少包含 Manifest、测试源、生成器、工具链、Edition、Feature、TargetSpec 和发现配置摘要。发现结果按规范化 ID 排序，再形成 `TestPlan`：

```text
TestPlan = frozen cases + dependencies + target/profile + seed
         + isolation + resource leases + expected outcomes
```

计划冻结后，调度器不得因文件系统变化静默增加、删除或修改用例。输入变化应使本轮报告标为 `workspace_changed`，并由调用方决定继续冻结快照或取消后重新发现。分片执行必须携带完整计划摘要、分片算法版本和分片索引，使各分片并集等于原计划且不重复。

## 用例状态机与统一结果

```text
Discovered → Queued → Running → Passed
                         ├────→ Failed
                         ├────→ TimedOut
                         ├────→ Cancelled
                         └────→ EnvironmentFailed
```

- `Queued` 前必须取得声明的资源 lease；取得失败属于 `EnvironmentFailed`，不能归咎于被测程序。
- `Running` 后每次 attempt 独立记录命令、环境摘要、seed、开始/结束单调时钟、退出原因和制品。
- 超时与取消只能发布一个终态；终止后仍需回收进程树、端口、临时目录和资源 lease。
- 被测程序越过已授予预算为 `Failed(resource_exhausted)`；宿主无法兑现计划资源为 `EnvironmentFailed`。
- `Passed` 仅表示本次冻结输入满足该 kind 的判定器，不等于功能已稳定或需求已完成。

`TestResult` 必须保留稳定的 case ID、kind、final status、attempt 列表、诊断、artifact references 和环境指纹。JUnit、JSON 和文本只是同一语义模型的不同呈现；文本可本地化，机器字段和错误码不可依赖本地化全文。

## 各类测试的判定规则

| Kind | 通过条件 | 必须保留的失败证据 |
|---|---|---|
| `compile-pass` | 编译成功；预期 warning/制品属性匹配；必要时链接或运行成功 | 源输入、参数、诊断、ArtifactManifest、链接/运行结果 |
| `compile-fail` | 编译失败，诊断 code、主 span、标签和必要的消息 pattern 匹配 | 实际与期望诊断的结构化差异；不得比较完整本地化文本 |
| `diagnostic-snapshot` | 规范化后的诊断结构匹配批准快照 | 新旧快照 diff；更新快照必须是显式操作，普通 test 不得覆盖 |
| `unit/integration/runtime` | 进程按协议结束，断言通过且无泄漏/崩溃信号 | stdout/stderr、退出原因、运行时诊断、资源回收结果 |
| `doc` | 文档代码块按声明编译或运行，隐藏前导代码和行映射正确 | 文档位置、展开后的输入、诊断和结果 |
| `fuzz/property` | 给定 seed、corpus 和预算内没有违反 oracle/invariant | 首个失败输入、seed、shrinking 轨迹和最小复现 |
| `bench` | 测量有效、环境合格、样本与统计报告完整；是否回归由外部基线策略判断 | 原始样本、预热、噪声判定、环境和基线引用 |

测试依赖若失败，后继用例记录 `EnvironmentFailed(dependency_failed)` 或计划定义的 `skipped`，不得伪装为通过。快照、golden 和基线更新必须经独立命令与代码评审，运行器默认只读。

## 并行、隔离与确定性

每个用例默认获得独立工作目录、环境 allowlist、seed、端口 lease 和进程组。需要共享数据库、设备或全局服务的用例必须声明命名资源；调度器对同名排他 lease 串行化，不能依靠测试名称约定。动态端口必须先由 lease manager 预留并把句柄传给用例，避免“探测空闲后关闭再绑定”的竞态。

虚拟时钟只用于明确支持时钟注入的用例；操作系统超时和进程清理使用单调真实时钟。随机测试的根 seed 写入计划，子 seed 由稳定的 `hash(root_seed, case_id, attempt)` 派生，改变并发度不能改变首轮输入。

取消先停止派发，再通知运行中用例，最后按 Profile 宽限终止整个进程树。`--jobs` 只是并发上限；实际并发同时受 CPU、内存、端口、设备和平台 lease 限制。

## 重试与 Flaky 规则

重试默认关闭，其次数属于 `candidate_default`。只允许对策略明确的非破坏性用例重试；安全、迁移、基准和有外部副作用的用例默认禁止自动重试。

首次失败后即保留 `first_failure`。后续 attempt 成功时最终状态仍不得改为普通 `Passed`，而应为 `Failed(flaky_detected)` 或专用隔离状态，并进入 Flaky 队列。发布门禁只能按批准策略隔离已登记 Flaky，不能在报告阶段删除失败 attempt。用例在没有输入变化时持续失败不属于 Flaky。

## 资源预算、证据与最小复现

单用例时间、进程、内存、输出和 artifact 数字全部遵循 [工具链 Budget 治理](./README.md#安全profile-与完成定义)，当前值仅是 Profile 的 `candidate_default`，不是 SLA 或容量承诺。预算需区分运行器自身、被测程序和共享 fixture，防止把宿主故障误分类为产品失败。

成功用例默认保留摘要和必要报告；失败用例保留输入引用、命令、声明环境、工具链与 TargetSpec 指纹、seed、首失败日志和诊断。秘密、绝对用户路径和凭据必须脱敏。大制品按内容寻址、配额和保留策略存储，报告只引用摘要；清理失败进入 quarantine。

最小复现包含单个 case 或最小依赖闭包，默认使用 `--jobs 1 --retry 0 --seed <recorded>`。fuzz/property 可附最小化输入；并发错误若无法串行复现，必须保留原调度 seed、事件轨迹和资源配置，不得声称已经最小化。

## 退出码、测试与验收

CLI 退出码遵循工具链总则：全部通过为 `0`；用例失败为 `2`；环境失败为 `3`；用户取消或全局 deadline 为 `4`；运行器内部不变量破坏为 `5`。报告中的逐用例状态是权威信息，调用方不得仅靠进程退出码反推具体失败原因。

- `TEST-TOOLS-RUNNER-001`（planned）：发现顺序、分片并集、并发 lease、固定 seed 和不同 `jobs` 的结果一致性。
- `TEST-TOOLS-RUNNER-002`（planned）：首次失败保留、重试成功不掩盖、Flaky 隔离和发布门禁。
- `TEST-TOOLS-RUNNER-003`（planned）：超时/取消竞态、孤儿进程、磁盘满、坏快照、artifact retention 和最小复现。

验收要求包括：相同冻结输入产生相同 TestPlan 摘要；任何失败都能定位到用例、阶段和判定器；取消后没有可观察的孤儿进程或未释放 lease；报告 schema 能表达全部状态；所有证据明确标记为 `planned`，直到真实运行产生可复核结果。

## 版本、回滚与追溯

报告 schema 的 minor 版本只追加可选字段；改变状态语义、退出码或必需字段必须升级 major 并提供 reader adapter。回滚恢复上一已签名 runner 和 schema writer，但保留新报告原件，不能用旧 writer 覆盖。测试计划必须记录 runner、判定器和 schema 版本，以便历史复现。

本专题映射 `XLF-02-014`、`XLF-03-002`、`XLF-11-004`、`XLF-11-013`、`XLF-12-020`，实施任务为 `TASK-P3-TOOLS-003`。资源默认值、Flaky 隔离时限和基准统计方法仍需 Budget ADR/测试 RFC 决策，不得在当前草案中当作稳定承诺。
