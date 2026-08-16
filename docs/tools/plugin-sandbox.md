---
doc_id: DOC-TOOLS-PLUGIN-SANDBOX
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.2"
maturity: EXTENDED
status: 草案
phase: P3
last_reviewed: 2026-08-16
traceability_scope: [XLF-03-005, XLF-03-007, XLF-03-012, XLF-10-012, XLF-10-014]
---
# 插件与 `build.x` 沙箱

> 状态：草案｜Owner：`role/tooling-team`

## 目标、边界与依赖

本专题规定编译器插件、宏宿主和 `build.x` 的最小权限执行模型。它解决“不可信扩展需要参与构建，但不能获得宿主进程权限”的问题；不规定插件业务 API，也不承诺任意第三方二进制都能被安全兼容。实施依赖统一 CLI 请求、XPM 签名策略、操作系统平台抽象层（Platform Abstraction Layer，PAL）和制品清单。

插件永远运行在独立进程中，不得链接进编译器地址空间。默认能力集合为空：无网络、无宿主环境变量、无任意子进程、无原始操作系统句柄；工作区只读，只能向独立 staging 目录写入声明的输出。交互模式可以请求提升权限，但无 TTY、CI、离线和可复现模式必须安全拒绝，不能用隐式默认批准。

## Manifest 验证与能力闭包

`PluginManifest` 至少声明 `id`、`version`、`entry`、`api_version`、`permissions`、`inputs`、`outputs`、`network`、`limits`、`signature` 和目标平台。宿主必须按以下顺序验证，任一步失败均不得创建插件进程：

1. 以有界解析器检查编码、大小、必需字段、重复字段和未知主版本。
2. 验证包摘要、签名、撤回状态、发布者和 registry policy；离线时只接受已验证且未过策略有效期的本地证据。
3. 对 `entry`、输入和输出做词法规范化，再以目录句柄打开并验证打开后的文件身份；拒绝绝对路径、父级穿越、设备路径、重解析点或符号链接逃逸。
4. 计算权限闭包。例如 `process.spawn` 必须同时声明可执行文件、参数模板和子进程配额；网络权限必须闭包到协议、主机、端口和 TLS 策略；写权限必须闭包到声明输出。
5. 将请求权限与工具链、工作区、用户批准及运行 Profile 求交集。最终能力只能减少，不能由插件自行扩大。
6. 验证 API 主版本、目标三元组和宿主能力；缺少能力时返回结构化拒绝或使用明确声明的 fallback，不做静默降级。

Manifest、策略和批准记录的摘要写入本次运行的 `SandboxPlan`。TOCTOU 防护要求实际启动使用验证过的文件句柄或等价平台能力，不能验证路径后重新按字符串打开。

## 生命周期与失败语义

沙箱实例遵循：

```text
Created → Validated → Starting → Running → Cancelling
    │          │           │         │          ├→ Exited → Reaped
    │          │           │         │          ├→ Crashed → Reaped
    │          │           │         │          └→ Killed → Reaped
    └──────────┴───────────┴─────────┴────────────→ Reaped
```

- `Validated` 后 Manifest、输入指纹、权限和资源 Profile 冻结；修改请求必须新建实例。
- `Starting` 期间先建立隔离和 IPC，再启动插件；隔离后端建立失败不得退化为普通进程。
- `Running` 只接受协商过的方法。超限、协议违规、签名撤回或宿主取消进入 `Cancelling`。
- `Cancelling` 先发送协作取消并停止接收新请求；候选宽限到期后终止整个进程树。取消与正常退出竞态只能产生一个用户可见终态。
- `Reaped` 必须回收进程、管道、临时句柄和 staging lease；审计摘要与允许保留的最小失败证据独立保存。

错误码至少区分 `invalid_manifest`、`signature`、`permission_denied`、`unsupported`、`timeout`、`quota`、`crash`、`protocol`、`cancelled` 和 `cleanup_failed`。运行失败不得提交部分输出。

## 各平台隔离后端

| 平台 | 目标隔离机制 | 必须验证的回退边界 |
|---|---|---|
| Windows | Job Object 管理进程树和配额；受限令牌、AppContainer 或等价能力控制文件/网络 | 目标系统无法提供所需令牌或网络隔离时拒绝启动，不退化为仅 Job Object |
| Linux | namespace、只读 bind mount、`no_new_privs`、seccomp 和 cgroup v2（可用时） | user namespace、seccomp 或资源控制缺失必须体现在能力探测和策略结果中 |
| macOS | 独立进程、受限 sandbox profile、最小文件描述符和进程组 | 平台版本不支持批准的限制集合时拒绝高风险插件，只允许策略明确的低风险子集 |

上述均是目标实现契约，状态为 `planned`，不表示当前平台已经通过验证。后端必须输出可审计的实际能力集合，不能只记录请求能力。

## `build.x` 的可复现执行规则

`build.x` 只能读取 Manifest 声明的源码、配置、工具链属性和显式环境键。时间、随机数、主机名、用户目录、未声明 Git 状态和隐式网络默认不可见。网络下载应由 XPM 在受信下载阶段完成，并将摘要锁定的文件作为显式输入交给构建脚本。

执行前生成包含输入路径、内容摘要、工具链、TargetSpec、声明环境和脚本摘要的输入指纹；执行后只接受声明输出。构建缓存键必须包含该指纹和实际能力集合，不包含 wall-clock 时间或临时目录。脚本尝试读取未声明输入时应报告精确路径和缺失能力，不得将其自动加入依赖。

## IPC、顺序、取消与背压

IPC `Envelope` 包含 `schema_version`、`session_id`、单调递增 `sequence`、`request_id`、`kind`、`method`、`payload` 和 deadline。握手协商 API 主/次版本、消息上限和能力；握手完成前只允许 `hello`、`reject` 和 `close`。

- 同一 session 的 sequence 必须连续；重复、回退或越过窗口的消息是协议错误。
- 每个 request 最多对应一个终结响应；进度消息必须引用存活 request，终结后到达的消息被丢弃并审计。
- `cancel(request_id)` 是幂等的；宿主取消后不再接受该请求的新输出，但仍需排空和回收底层 IPC。
- 发送队列和未决请求均有 Profile 上限。达到上限时暂停读取或返回 `quota`，不得无界缓存。
- payload 先校验长度和 schema，再解析内部路径、命令或诊断；插件文本不能被解释为终端控制、编译参数或 Agent 指令。

资源数值遵循 [工具链 Budget 治理](./README.md#安全profile-与完成定义)：当前 CPU、内存、输出、进程和 IPC 数字仅为 `candidate_default`，由 Profile 提供，P4 前需以 Budget ADR 冻结。

## 输出 staging 与提交

插件只写 staging。进程成功退出后，宿主依次执行：枚举输出、拒绝未声明文件和链接逃逸、检查总量与单文件预算、校验格式/schema、扫描可执行内容和秘密、验证内容摘要，再生成 `OutputProposal`。编译产物只能在完整验证后以原子重命名或 generation manifest 提交；源码变更默认形成 patch proposal，必须由用户或批准的 CI policy 应用。

失败、取消、超限或宿主崩溃恢复时，未提交 generation 不可见。清理失败进入 quarantine 并记录位置和访问权限，后续清理器不得执行其中内容。

## 测试、验收与回滚

- `TEST-TOOLS-PLUGIN-001`（planned）：路径逃逸、句柄泄露、非法系统调用、协议乱序和输出二次验证。
- `TEST-TOOLS-PLUGIN-NET-001`（planned）：默认断网、allowlist、DNS 重绑定、代理和 TLS 策略。
- `TEST-TOOLS-PLUGIN-QUOTA-001`（planned）：CPU/内存/进程/输出/IPC 超限、取消竞态、杀死进程树与残留回收。

验收要求是三平台目标后端分别给出能力探测和负向证据；Manifest 同输入产生相同 `SandboxPlan`；失败不会修改工作区或公开缓存；审计中不含秘密。API 主版本变化必须经 adapter 或 Feature Gate。回滚时全局关闭 plugin/build gate，隔离未审计缓存，恢复上一已签名宿主；核心编译路径不得依赖插件才能工作。

## 追溯与待决策事项

本专题映射 `XLF-03-005`、`XLF-03-007`、`XLF-03-012`、`XLF-10-012`、`XLF-10-014`，实施任务为 `TASK-P3-TOOLS-004`。待 RFC/ADR 决定的事项包括各平台最低隔离能力、交互批准的有效期、插件 API 稳定周期和发布 Profile 预算；在这些事项决策前，不得将插件沙箱标为“已验证”。
