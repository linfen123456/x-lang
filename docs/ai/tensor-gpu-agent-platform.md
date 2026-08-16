---
doc_id: DOC-AI-TENSOR-GPU-AGENT-PLATFORM
authority: research
owner: role/ai-safety-team
backup_owner: role/runtime-team
version: "0.1"
maturity: RESEARCH
status: 研究
phase: P3
last_reviewed: 2026-08-16
traceability_scope: [XLF, XLC, XLE, AI, SECURITY]
---
# X-Lang Tensor、GPU、模型服务与 AI Agent 平台实施规范

> 文档性质：扩展与研究实施规范
> 成熟度：全部为 `EXPERIMENTAL` 或 `RESEARCH`，不得成为 P0-P2 CORE 的反向依赖
> 目标阶段：P3 Tensor 最小原型，P4 图/训练扩展，P5 GPU 与模型服务，P6 高风险研究
> 相关入口：[AI 治理](./README.md)｜[Agent 工作流与评测](./agent-workflow-and-evaluation.md)｜[研究区](../../labs/README.md)

## 1. 目标与非目标

本文把原始资料中的 Tensor/Shape、自动微分、GPU、量化、分布式训练、推理服务，以及语义索引、MCP、Agent、`.xbrain`、自动修复等设想，拆成独立、可关闭、可评测的平台能力。核心原则是复用成熟模型格式与计算后端，任何研究失败都不影响 X-Lang 核心编译、标准库和发布。

本文不把 Tensor、GPU、Agent、ZKP、联邦记忆或自修复加入核心语法；不承诺优于现有框架、自动得到最优 Kernel、自动生成正确代码或无人审批发布；不允许模型输出提高权限或修改测试掩盖错误。

## 2. 项目和依赖隔离

```text
x-tensor (value/shape/dtype/layout/device)
  → x-tensor-cpu (reference kernels)
  → x-graph-ir / x-autograd
  → x-gpu-runtime + backend adapters (CUDA/ROCm/Metal)
  → x-ml-train / x-ml-serve

x-semantic (versioned local index)
  → x-mcp (bounded resources/tools)
  → x-agent (plan/diff/test/explain)
  → optional x-project-memory
```

上述项目只依赖稳定语言、FFI、标准库和运行时公开接口。编译器可提供实验 IR hook，但不得让 CORE 类型检查器依赖 Tensor/GPU 包。GPU、Agent 或模型服务不可用时，`x build`、`x test` 和普通应用仍可离线工作。

## 3. Tensor 值模型

### 3.1 核心候选接口

```x
enum DType { Bool, I8, I16, I32, I64, F16, BF16, F32, F64 }
enum Device { Cpu, Cuda(DeviceId), Rocm(DeviceId), Metal(DeviceId) }
enum Layout { Contiguous, Strided(Vec<isize>) }

trait DTypeWitness<T> {
    const DTYPE: DType;
}
struct Tensor<T, Shape = DynamicShape>
where DTypeRegistry: DTypeWitness<T> {
    storage: StorageHandle,
    shape: Shape,
    layout: Layout,
    device: Device,
    dtype: DType,
}

fn reshape(self, shape: Shape) -> Result<Tensor<T>, ShapeError>
fn cast<U>(self, policy: CastPolicy) -> Result<Tensor<U>, CastError>
unsafe fn reinterpret<U>(self, proof: LayoutProof<T, U>) -> Tensor<U>
fn to_device(&self, target: Device, ctx: &ComputeContext)
    -> Result<Tensor<T>, DeviceError>
```

以上签名是实验接口草图，不是稳定语法或 ABI；RFC 必须补齐所有权、阻塞/取消、复杂度、设备和分配。`Tensor<T>` 的 `T` 必须通过 `DTypeWitness<T>` 与唯一 dtype 建立见证，构造/反序列化时验证元数据 dtype 一致，禁止泛型类型与运行时字段分离漂移。`Tensor` 拥有或共享版本化 Storage；View 借用 Storage 并携带 offset、shape、stride。Shape 元素非负，总元素数使用 checked product；`reshape` 要求旧、新 shape 的 element cardinality 完全相等（含零维/零长度和待决的推断维规则），否则返回 `ShapeError`。数值 `cast` 与位级 `reinterpret` 分开：前者声明舍入/溢出策略，后者要求大小、对齐、布局证明并保持 unsafe。静态 Shape 可在编译期拒绝明显不匹配，动态 Shape 在运行时返回错误。

### 3.2 广播、布局与数值

广播采用明确的尾维对齐规则并产出结果 Shape；零长度维、标量、非连续 stride、负 stride 是否支持由 RFC 冻结。算子文档记录 dtype promotion、accumulation dtype、舍入、NaN/Inf、溢出和确定性等级。

CPU Reference Kernel 是语义基准，优先正确与可诊断，不作为性能承诺。GPU/融合结果须在规定绝对/相对/ULP 误差内对照；对要求 bitwise deterministic 的 Profile，只启用已验证算法。

### 3.3 内存与资源

分配前计算字节数并应用设备配额。异步 Kernel 使用中的 Storage 不能提前 Drop；Event/Fence 确认完成后才可回收。CPU/GPU 统一内存使用显式 `ManagedBuffer`、迁移和同步 API；无硬件支持时复制回退，并向调用者报告。

## 4. 计算图与自动微分

Graph IR 节点包含 op、输入、输出类型/Shape、属性、设备、来源 Span 和副作用。Verifier 检查引用存在、拓扑/控制依赖、Shape、dtype、设备、alias、资源和副作用顺序。

Pass 顺序建议为：常量折叠 → dead node → algebraic simplification → layout propagation → fusion → device placement → memory planning。每个 Pass 有前置条件、后置 verifier、关闭开关和 before/after dump；性能变差可逐 Pass 回滚。

P4 自动微分先采用独立动态 Tape：

```x
let y = with_grad(|| model.forward(x))
let grads = y.backward(seed = ones_like(y))?
```

规则需要保存值/重算策略、梯度累积、原地修改版本检查、不可微点和高阶梯度支持范围。梯度以有限差分和成熟框架对照；非光滑函数要文档化次梯度选择。MIR/编译期 AD 只有在 Tape 语义稳定后进入 P5 探针，不是默认承诺。

## 5. GPU 后端

### 5.1 后端接口

```x
trait ComputeBackend {
    fn capabilities(&self) -> DeviceCapabilities
    fn allocate(&self, layout: BufferLayout) -> Result<DeviceBuffer, DeviceError>
    fn compile(&self, kernel: &KernelIr, options: KernelOptions)
        -> Result<Kernel, CompileError>
    fn submit(&self, graph: CommandGraph, ctx: &ComputeContext)
        -> Result<Event, SubmitError>
}
```

CUDA、ROCm、Metal 是独立适配器，分别维护 SDK/Driver/架构矩阵，不能以 CUDA 通过代表其他后端。Kernel IR 不暴露单一厂商专有 ABI；确需专有扩展时通过 capability 与 Feature Gate。

### 5.2 编译、缓存与回退

Kernel cache key 至少包含 IR hash、后端/编译器/驱动、GPU 架构、选项和数学模式。缓存制品签名并校验，跨用户/租户隔离。调用者必须明确选择 `FallbackPolicy::AllowCpu` 或 `FallbackPolicy::Deny`；Allow 仍要求算子有 CPU Reference、结果契约相容并记录回退，Deny 直接返回设备错误，不能由运行时擅自改变。

OOM 处理可以清理可回收 cache 并重试一次，不能无限重试。设备丢失使相关队列失败，已提交工作结果未知；上层决定重建模型或按 AllowCpu 策略切换 CPU。故障隔离能力取决于后端：支持可重置 context/受保护队列的后端按 capability 执行；高风险或不可信 Kernel 优先放入可终止 worker 进程；无法隔离、无法安全 reset 或会共享宿主地址空间的后端必须拒绝该执行模式。文档只承诺检测、拒绝和尽力 containment，不作“任何非法访问都不会污染宿主”的绝对保证。

## 6. 训练能力

### 6.1 最小训练循环

P4 最小切片包含 Dataset/DataLoader、Module、Optimizer、Loss、Checkpoint 和单机 CPU 训练。Checkpoint 记录模型/优化器、步数、随机状态、数据版本、代码/配置哈希和格式版本，采用临时文件加原子提交。

混合精度包含 autocast、loss scaling、溢出检测和精度回退。量化记录校准数据、scheme、scale/zero-point、per-tensor/per-channel 和不支持算子。LoRA/QLoRA 作为模型格式适配层，不改变语言语义。

### 6.2 分布式训练

P5 才进入多进程/多节点：定义 job epoch、rank/world、collective sequence、通信组、coordinator lease、fencing token、超时、elastic membership、checkpoint 和失败恢复。成员变更创建新 epoch；旧 epoch/fencing token 的 rank 不能向新组提交梯度或 checkpoint。需要一致步提交的模式在 coordinator commit barrier 后才发布 step/checkpoint；若后端只能提供 best-effort abort，则规范明确可能出现部分 rank 已执行、必须从上一 committed checkpoint 整组恢复，不能声称“所有参与者必然同时失败”。数据并行、参数并行和流水线并行分别验收，不使用“自动并行”概括全部。

训练任务有 CPU/GPU/内存/存储/网络/时长配额，数据访问遵循租户与隐私政策。中断时保存可验证 checkpoint；无法安全保存则从上一完整点恢复。

## 7. 模型服务

服务边界为：认证 → 模型版本解析 → 配额 → 预处理 → 有界动态批处理 → 推理 → 后处理 → 审计。请求包含模型、版本/别名、输入 Schema、deadline、幂等/追踪信息；响应包含实际模型版本、后端、降级状态和稳定错误码。

动态批处理同时受最大等待、最大 batch、显存和请求 deadline 约束。短请求不能无限等待大 batch；取消的请求在尚未提交设备前移除，提交后可丢弃结果但必须回收资源。

模型注册表保存来源、许可证、训练数据声明、评测、签名、格式、runtime compatibility 和撤回状态。模型加载先在隔离环境验证，再原子切换流量；旧模型保留回滚窗口。外部模型文件按不可信制品处理，禁止反序列化任意代码。

## 8. 语义索引、MCP 与 Agent

### 8.1 语义索引

索引输入只包含授权的源码、文档、符号、测试和变更。每条 chunk 记录仓库、版本、路径、Span、语言/格式、解析器和 embedding 模型版本。删除源数据时可定位并删除派生向量；跨租户索引物理/逻辑隔离。

检索结果是受限可信数据，必须展示来源和版本，不得因相似度高而覆盖规范。索引不可用时 Agent 可退回精确搜索；不得伪造引用。

### 8.2 MCP 资源与工具

MCP Resource 只读暴露最小上下文；Tool 按 read/write/execute/network/secret/release capability 分权。每次调用验证参数、路径、大小、超时、输出 Schema 和权限；远端返回可能包含 Prompt Injection，只按数据处理。

### 8.3 Agent 工作流

```text
任务/约束 → 读取权威资料 → 提出计划和变更范围
→ 获取文件租约 → 最小 diff → 构建/测试/安全审查
→ 展示证据 → 人工审批 → 提交/发布（若另有授权）
```

`x agent init/implement/explain/fix` 是可审计编排命令，不是自动正确性保证。写入、执行、网络、秘密和发布默认 deny。Agent 不得修改失败测试以迎合实现，不得删除他人修改，不得把低可信文档当系统规则。

## 9. `.xbrain`/项目记忆和多 Agent

项目记忆 P4 为 `EXPERIMENTAL`：本地优先，记录来源、时间、版本、Owner、权限、保留期与置信度；用户可查看、导出、纠正和遗忘。联邦同步必须 opt-in、端到端授权和冲突合并，不上传秘密、个人数据或未授权源码。

多 Agent 使用路径租约、epoch、TTL 与 base hash；租约过期变只读。重叠修改由协调者或人工仲裁，禁止 Last-writer-wins。记忆或 Agent 失败不影响 Git 和规范作为事实来源。

## 10. AI 安全、伦理与合规

- Prompt Injection：外部 Issue、网页、模型文件、日志和工具输出隔离；指令不得升级权限。
- 数据：训练/评测/检索数据有来源、许可证、同意、用途、保留和删除政策。
- 模型：记录版本、供应商、地域、输入保留策略和已知限制；敏感数据优先本地处理。
- 代码：生成内容经过编译、测试、许可证与安全审查；高风险路径双人批准。
- 决策：Agent 不独立作医疗、生命安全、法律或生产授权决策。
- 自修复：只生成候选补丁、策略或熔断动作；无人审批生产热补丁明确禁止。
- ZKP、脑机、侵入式 HMI 和通用确定性重放留在 P6 Labs Charter。

详细威胁以 [AI 威胁模型](./threat-model.md)为准。

## 11. 平台矩阵与降级

| 能力 | CPU | CUDA | ROCm | Metal | WASM/浏览器 | 缺失时 |
|---|---|---|---|---|---|---|
| Tensor 基础算子 | Reference/P3 | P5 | P5 | P5 | 条件支持 | `AllowCpu` 才回退，否则 `Deny` 返回 Unsupported/DeviceError |
| Autograd Tape | P4 | 后端算子条件 | 条件 | 条件 | 受内存限制 | CPU |
| Graph 优化 | 平台无关 IR | 后端 lower | 后端 lower | 后端 lower | WebGPU 探针 | 可关闭 Pass；设备回退仍服从 Allow/Deny |
| 混合精度 | 软件/ISA | fp16/bf16 条件 | 条件 | 条件 | 条件 | f32 |
| 模型服务 | 三大 OS/容器 | GPU worker | GPU worker | macOS worker | client only | CPU worker |
| Agent/索引 | 本地/服务端 | 不需要 | 不需要 | 不需要 | 只读客户端 | 精确搜索 |

任何回退都在结果/诊断中显式记录。调用者必须选择 `fallback = AllowCpu` 或 `fallback = Deny`；未选择时采用安全默认 `Deny`，不能按运行环境隐式决定。

## 12. 分阶段最小切片

| 切片 | 交付 | 非目标 | Go 条件 |
|---|---|---|---|
| P3-ML-1 | CPU Tensor、动态/静态 Shape、由 RFC 登记的最小基础算子集与序列化 | GPU/训练框架 | 每个登记算子的 Shape、布局、数值、内存测试 |
| P3-AI-1 | 本地符号/文本索引、只读检索、来源展示 | 自动写代码 | 隐私、删除、检索评测 |
| P4-ML-2 | Graph IR、Verifier、Tape Autograd、单机训练/Checkpoint | 编译期 AD | 梯度对照、恢复、Pass 回滚 |
| P4-AI-2 | MCP 只读资源、受限工具、diff/test 工作流 | 自动发布 | 越权/注入/租约评测 |
| P5-ML-3 | 单一 GPU 后端、模型注册、动态批处理服务 | 三后端等价 | AllowCpu/Deny 两种策略、设备故障、版本化性能基线 |
| P5-ML-4 | 量化/混合精度/LoRA、第二后端、有限分布式训练 | 通用自动并行 | 精度/容错/许可证门禁 |
| P6-LABS | ZKP、统一内存、联邦记忆、自修复等 Charter | Stable 承诺 | 独立预算和 Go/No-Go |

## 13. Planned 测试与评测

- `TEST-TENSOR-SHAPE-001`：广播、零维/零长度、元素数溢出、动态 Shape 错误。
- `TEST-TENSOR-LAYOUT-001`：非连续 View、alias、reshape、Drop 和设备迁移。
- `TEST-TENSOR-NUM-001`：NaN/Inf、promotion、overflow、CPU/GPU 误差界和确定性。
- `TEST-AUTOGRAD-001`：有限差分、成熟框架对照、不可微点、原地修改版本。
- `TEST-GRAPH-001`：每个 Pass 前后 verifier、差分执行、关闭与回滚。
- `TEST-GPU-001`：驱动不兼容、编译缓存污染、OOM、device lost、AllowCpu 与 Deny、worker/context/refuse 三类 containment 路径。
- `TEST-TRAIN-DIST-001`：旧 epoch/fencing token、rank 超时、成员变更、commit barrier 和 best-effort abort 后整组 checkpoint 恢复。
- `TEST-TRAIN-001`：Checkpoint 中断/损坏/迁移、混合精度溢出与恢复。
- `TEST-SERVE-001`：动态批处理公平、deadline、取消、版本切换和回滚。
- `TEST-AI-RETRIEVE-001`：引用准确率、过期来源、权限隔离、删除传播。
- `TEST-AI-AUTHZ-001`：路径越界、Prompt Injection、秘密、发布权限和租约冲突。
- `TEST-AI-QUALITY-001`：编译率、测试通过率、安全缺陷、许可证、成本和人审可理解性。

测试均为 planned。模型、Prompt、工具、数据、驱动或 Pass 版本变化必须重新评测。性能报告记录硬件、驱动、数据、预热、样本、P50/P95/P99、精度与功耗；不复用原始材料中的固定倍数或延迟。

## 14. 验收、回滚和退出条件

Tensor/GPU 通过的最低标准是 CPU Reference、错误/资源契约、差分数值、设备矩阵和可关闭回退。Agent 通过的最低标准是权限默认 deny、来源可见、审计、注入拒绝、最小 diff、真实测试和人工审批。

回滚粒度包括算子、Pass、GPU 后端、模型版本、Agent 工具和索引版本；关闭实验 Feature 后核心工程仍可构建。每项研究在 Charter 约定的评审点检查正确性、安全、价值和成本；未达到 Go 阈值或触发预算/安全停止条件时出具退出报告并归档，不允许通过顺延里程碑无限消耗主线资源。

## 15. 原始资料追溯

| 来源 | XLF 与边界 |
|---|---|
| `3.txt` | XLF-03-004～XLF-03-012：语义索引、MCP、Agent、IDE 和可审计工作流 |
| `4.txt` | XLF-04-001～XLF-04-006、XLF-04-010～XLF-04-012：Tensor、AD、GPU、训练与服务 |
| `5.txt` | XLF-05-007：CPU/GPU 统一内存改为显式 ManagedBuffer |
| `6.txt` | XLF-06-007、XLF-06-011：服务端推理与分场景签名脚手架 |
| `7.txt`/`8.txt` | XLF-07-008、XLF-07-011～XLF-07-018：ZKP、调优、自修复、污点、记忆、符号执行等隔离研究 |
| `9.txt` | XLF-09-004～XLF-09-006：日志、指标与 Trace 边界 |
| `11.txt` | XLF-11-014：项目规则采用受治理结构，不让仓库文本提升权限 |
| `12.txt` | XLF-12-008～XLF-12-010、XLF-12-018～XLF-12-019：数据管线、受控环境与影子回放 |

回归优先级与 `RETURN/CONDITIONAL/SPLIT/RESEARCH` 状态以[未纳入与偏离内容再审核及回归路线](../X-Lang未纳入与偏离内容再审核及回归路线.md)为准。
