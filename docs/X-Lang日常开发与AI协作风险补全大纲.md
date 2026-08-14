# X-Lang 日常开发与 AI 协作风险补全大纲

> 总纲：[X-Lang 企业级完整文档体系总纲](./X-Lang企业级完整文档体系总纲.md)  
> 大纲版本：1.0-outline｜状态：工程治理 Backlog 已冻结｜审查基线：2026-08-15  
> 性质：来自日常开发、生产故障和 AI 编码失效模式的派生需求，不属于 12 份原始材料。  
> 目标：补齐“语言能编译”之外经常导致项目失败的需求治理、环境、数据、测试、运维和 AI 协作问题。  

## 1. 最终确定程度

冻结状态和正式规范门禁只在[总纲](./X-Lang企业级完整文档体系总纲.md)维护。本文件仅维护 `XLE-*`（Engineering Blind-spot）明细；默认成熟度为 `CORE治理/草案` 或 `EXTENDED/待阶段实施`，每项必须有负责人、项目、自动检查和事故/回归证据。

## 2. `XLE-GOV`：需求、决策和变更治理

| ID | 常见遗漏 | 必须补充的内容 | 目标项目/文档 | 验收 |
|---|---|---|---|---|
| XLE-GOV-001 | 需求不断变化 | Problem/Goal/Non-goal、用户场景、优先级、验收和取消条件 | specs/requirements | 需求变更能追到 RFC/Issue/版本。 |
| XLE-GOV-002 | 规范与代码冲突 | 规范、ADR、实现、测试的权威顺序和冲突升级流程 | specs/governance | 冲突不会被 Agent 或开发者静默选择。 |
| XLE-GOV-003 | 隐含需求 | 未定义行为、边界值、失败路径、权限和数据保留必须显式 | x-rfc/spec-lint | 每个稳定功能有异常与非目标章节。 |
| XLE-GOV-004 | 范围膨胀 | MVP/1.0/扩展/研究预算和进入退出门禁 | release/roadmap | 新需求不能绕过阶段和资源评审。 |
| XLE-GOV-005 | 决策反复 | ADR 状态、替代方案、后果和 supersede 链 | docs/decisions | 重大选择有不可变历史。 |
| XLE-GOV-006 | 技术债失控 | 债务类型、利息、所有者、偿还版本和阻断阈值 | governance/debt | 发布复审包含债务预算。 |
| XLE-GOV-007 | 所有权不清 | CODEOWNERS、Bus Factor、值班、交接和备用负责人 | governance/ownership | 核心模块至少两个可维护角色。 |
| XLE-GOV-008 | 完成定义含糊 | 代码、测试、文档、安全、性能、兼容、回滚和追溯统一 DoD | governance/dod | 未满足项不能标记完成。 |

## 3. `XLE-DEV`：日常开发环境与代码变更

| ID | 常见遗漏 | 必须补充的内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLE-DEV-001 | 环境“只在我机器可用” | `x doctor`、工具版本、SDK、代理、证书、路径和权限诊断 | x-doctor | 干净机可定位缺失依赖。 |
| XLE-DEV-002 | 环境配置漂移 | 锁定工具链、容器/Devbox、离线缓存和环境指纹 | x-environment | 两台机器产生相同构建计划。 |
| XLE-DEV-003 | 工作区已有用户修改 | 脏工作区检测、变更归属、重叠编辑和非破坏原则 | x-workspace-guard | 工具不覆盖未授权修改。 |
| XLE-DEV-004 | 分支与合并冲突 | 小变更、堆叠变更、冲突语义复核和生成文件策略 | git workflow | 合并后重新运行语义测试。 |
| XLE-DEV-005 | 部分实现无法构建 | Feature Gate、内部实验标记和可回滚增量切片 | x-build | 每个合并点可构建、可测试。 |
| XLE-DEV-006 | 依赖升级破坏行为 | 更新策略、兼容窗口、Changelog、API diff、回归和回滚 | xpm/x-api-diff | 自动更新不能绕过兼容测试。 |
| XLE-DEV-007 | 依赖供应链风险 | 维护度、许可证、漏洞、体积、替代和撤回 | xpm-audit | 新依赖有评估记录和 SBOM。 |
| XLE-DEV-008 | 生成文件手工修改 | 生成源、命令、版本、不可手改标识和漂移检测 | x-codegen-manifest | CI 可重新生成并零差异。 |
| XLE-DEV-009 | 死代码与废弃物残留 | 引用分析、废弃期、迁移和删除审批 | x-vet/x-api-diff | 无不可解释的孤立公共接口。 |
| XLE-DEV-010 | 调试不可复现 | 最小复现、环境快照、随机种子、输入缩减和工件保留 | x-repro | 缺陷可一键重放或列明外部依赖。 |
| XLE-DEV-011 | 大重构行为漂移 | Characterization Test、API/IR diff 和分批迁移 | x-test-runner | 重构前后可观察行为一致。 |
| XLE-DEV-012 | 文档与命令过期 | 文档命令测试、链接、示例、版本选择和离线文档 | xdoc | 文档代码和命令在 CI 执行。 |

## 4. `XLE-DATA`：数据、时间、文件和兼容边界

| ID | 常见遗漏 | 必须补充的内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLE-DATA-001 | 数据库迁移只考虑升级 | Expand/Migrate/Contract、双写、回填、校验、回滚和长事务 | x-db-migrate | N-1/N/N+1 滚动兼容演练。 |
| XLE-DATA-002 | Schema 演进丢数据 | 未知字段、默认值、字段重命名、枚举扩展和降级读取 | x-schema | 前后兼容黄金数据集。 |
| XLE-DATA-003 | 时区/DST/闰秒错误 | Instant/Duration/LocalDateTime 区分、TZDB 版本和歧义策略 | x-time | DST 跳变和跨版本测试。 |
| XLE-DATA-004 | Unicode 和本地化错误 | 编码、正规化、Grapheme、大小写、排序、路径和 IDN | x-text/x-i18n | Unicode conformance 与恶意文本测试。 |
| XLE-DATA-005 | 路径和文件系统差异 | 大小写、保留名、长路径、符号链接、权限、原子替换和锁 | x-fs | Windows/Linux/macOS 文件语料。 |
| XLE-DATA-006 | 浮点/数值跨平台不一致 | NaN、舍入、FMA、溢出、确定性和序列化 | x-numeric | 不同后端结果容差和严格模式。 |
| XLE-DATA-007 | 缓存失效错误 | Key 完整性、版本、TTL、负缓存、并发填充和污染恢复 | x-cache | 依赖变化必然失效，故障可清除。 |
| XLE-DATA-008 | 重试造成重复副作用 | 幂等键、去重窗口、事务边界和至少一次语义 | x-resilience | 超时/重放不会重复扣款类副作用。 |
| XLE-DATA-009 | 大数据耗尽内存 | 分页、Streaming、有界队列、背压、取消和临时文件配额 | x-stream | 超大/恶意输入保持有界资源。 |
| XLE-DATA-010 | 秘密和个人数据泄漏 | 分类、最少收集、脱敏、保留、删除、导出和审计 | x-data-governance | 日志/Trace/Core/AI 上下文均扫描。 |

## 5. `XLE-OPS`：故障、测试、发布和运维现实

| ID | 常见遗漏 | 必须补充的内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLE-OPS-001 | 网络分区和半失败 | Timeout、Cancel、Retry、Circuit、Bulkhead、DNS/TLS 失败 | x-resilience | 故障注入覆盖半开连接和分区。 |
| XLE-OPS-002 | 磁盘满/只读/文件损坏 | ENOSPC、权限变化、原子写、校验、恢复和告警 | x-fault-injection | 不产生静默数据损坏。 |
| XLE-OPS-003 | OOM/句柄/线程耗尽 | 配额、Admission、Load Shed、连接池和优雅退化 | x-resource-governor | 压力下保持控制面可用。 |
| XLE-OPS-004 | 时间和外部服务异常 | 时钟回拨、慢服务、限流、过期证书、DNS 和凭据轮换 | x-chaos | 定期混沌场景可复现。 |
| XLE-OPS-005 | 测试互相污染 | 临时目录、端口、时钟、随机数、环境、数据库和全局状态隔离 | x-test-isolation | 测试任意顺序和并行稳定。 |
| XLE-OPS-006 | Flaky 被重试掩盖 | 隔离、根因、重试上限、负责人、SLA 和历史趋势 | x-test-runner | 不允许无限重试通过门禁。 |
| XLE-OPS-007 | 测试只覆盖 Happy Path | 边界、失败、升级、降级、安全、性能、恢复和兼容测试矩阵 | tests/ | 每个公共契约有负向测试。 |
| XLE-OPS-008 | 发布无法安全撤回 | Feature Flag、Canary、灰度、Kill Switch、数据兼容和回滚 | x-release-control | 发布/回滚演练和指标门禁。 |
| XLE-OPS-009 | 可观测但不可行动 | SLI/SLO、告警去重、Runbook、关联 ID、采样和成本预算 | x-observability | 告警有负责人、步骤和验证。 |
| XLE-OPS-010 | 事故后重复发生 | 事件时间线、无责复盘、根因、行动项、所有者和验证 | docs/incidents | 高严重度事故形成回归测试。 |

## 6. `XLE-AI`：AI 写作、编码与 Agent 协作

| ID | 常见遗漏 | 必须补充的内容 | 目标项目 | 验收 |
|---|---|---|---|---|
| XLE-AI-001 | 上下文不足导致幻觉 | 规则文件→相关规范→源码/测试→错误输出的分层上下文 | x-context-pack | Agent 引用真实路径/API。 |
| XLE-AI-002 | 上下文过多导致失焦 | 任务相关选择、摘要索引、Token 预算和过期上下文淘汰 | x-context-pack | 上下文清单可见且可复现。 |
| XLE-AI-003 | 规范、代码和用户指令冲突 | 冲突检测、权威顺序、显式升级和禁止静默猜测 | x-ai-policy | 冲突产生结构化阻塞说明。 |
| XLE-AI-004 | 外部内容提示注入 | 源码/配置/网页/Issue 的信任级别；外部指令按数据处理 | x-ai-policy | Prompt Injection 红队语料通过。 |
| XLE-AI-005 | 幻觉 API/依赖/版本 | 本地搜索、官方来源、锁文件、编译探针和存在性校验 | x-agent-verify | 不存在符号在写入前被拒绝。 |
| XLE-AI-006 | 未读文件直接修改 | 编辑前读取目标、测试、类型和相似实现 | x-agent | 每次补丁记录上下文清单。 |
| XLE-AI-007 | 擅自扩大范围 | 任务边界、非目标、允许目录、写入/外部操作授权 | x-ai-policy | 越界工具调用被阻止并审计。 |
| XLE-AI-008 | 覆盖用户已有修改 | 变更归属、脏工作区、重叠 diff 和非破坏合并 | x-workspace-guard | 用户修改不被静默覆盖。 |
| XLE-AI-009 | 大补丁无法审查 | 计划、增量切片、每片验证、变更规模和停止条件 | x-agent | 每个切片独立可回滚。 |
| XLE-AI-010 | 测试通过但实现错误 | 先核对规格，再审查正确性/架构/安全/性能和测试有效性 | x-ai-review | 审查结论带证据和严重级别。 |
| XLE-AI-011 | AI 生成不安全代码 | 不可信输入、权限、认证、并发、内存、命令和秘密专项检查 | x-ai-review | 安全敏感补丁必须双重评审。 |
| XLE-AI-012 | 生成代码来源和许可证不明 | 模型/工具、提示摘要、引用来源、许可证、相似度和 SBOM | x-provenance | 发布代码可追到生成/人工审查记录。 |
| XLE-AI-013 | 模型/提示变化导致结果漂移 | 模型版本、参数、规则版本、工具版本和随机性记录 | x-ai-eval | 关键任务可重复评测。 |
| XLE-AI-014 | 没有 AI 质量评测 | 代表性任务集、正确率、编译率、测试通过率、安全和成本 | x-ai-eval | 模型/Prompt 升级前后有对照门禁。 |
| XLE-AI-015 | 多 Agent 同时改同一内容 | 文件/模块租约、任务 DAG、消息、冲突检测和所有权 | x-agent-coordinator | 不产生静默 Last-writer-wins。 |
| XLE-AI-016 | Agent 无限循环或成本失控 | 迭代、Token、时间、工具调用、网络和制品预算 | x-agent-budget | 超限安全停止并保留进度。 |
| XLE-AI-017 | 工具返回恶意或错误数据 | Schema 校验、来源、信任边界、大小限制和二次验证 | x-tool-gateway | 非法/超大/注入输出被隔离。 |
| XLE-AI-018 | AI 接触秘密和个人数据 | 上下文最小化、脱敏、驻留、供应商策略、删除和审计 | x-ai-privacy | 默认不上传秘密；可证明删除。 |
| XLE-AI-019 | 自动修复掩盖根因 | 根因报告、回归测试、补丁 diff、失败次数和人工批准 | x-agent | 禁止只改测试/文档迎合错误行为。 |
| XLE-AI-020 | 会话结束知识丢失或污染 | 事实/推测/决策分离，来源、有效期、遗忘和交接摘要 | x-project-memory | 新会话能加载最小可信上下文。 |

## 7. 冻结门禁与验收

| 冻结级别 | 可以确定的内容 | 仍不能确定的内容 |
|---|---|---|
| Architecture Baseline 0.2 | 文档结构、责任域、ID、阶段、物理项目和门禁 | 具体语法细节、ABI、性能数值和支持期限。 |
| MVP Spec Freeze | 最小语法、类型、错误、所有权、模块、IR 契约 | 扩展框架和研究能力。 |
| 1.0 Spec Freeze | 全部 CORE 规则、稳定 std、Tier 1、兼容/Edition | `EXPERIMENTAL/RESEARCH`。 |
| LTS Commitment | 支持期限、补丁范围、平台和安全 SLA | 无资源证据的长期承诺。 |

最终冻结前必须自动生成：`XLF/XLC/XLE → 规范 → ADR/RFC → 项目 → 测试 → 平台 → 发布状态`。缺少任何一段，只能称为大纲或候选规范，不能称为已经实现或正式稳定。
