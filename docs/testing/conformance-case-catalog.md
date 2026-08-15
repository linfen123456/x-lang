---
doc_id: DOC-TESTING-CONFORMANCE-CASE-CATALOG
authority: evidence
owner: role/quality-team
backup_owner: role/compiler-team
version: "0.1"
maturity: CORE
status: 草案
phase: P1
last_reviewed: 2026-08-15
traceability_scope: [XLF, XLC, XLE, QUALITY]
---
# X-Lang 符合性与企业能力 Planned 测试案例目录

> 文档性质：可读测试设计目录，不是测试代码或已执行报告
> 状态：`planned`
> 适用阶段：P0-P5；P6 研究项目另建 Charter 评测
> 规范入口：[符合性规范](../specs/conformance.md)｜[测试策略](./test-strategy.md)｜[性能与兼容测试](./performance-and-compatibility.md)

## 1. 目的与使用方法

本目录把规范中的抽象 `TEST-*` 细化为工程人员可直接创建测试卡的案例。`CASE-*` 是人类可读的目录别名，不是第二套测试 ID；每个 CASE 必须在测试登记时绑定一个 canonical `TEST-*` 和至少一个 Rule/XLF，运行记录只使用 canonical Test ID。每个案例说明依据、输入、操作、预期、诊断或可观察结果、平台和证据要求。这里的 `planned` 只表示计划，不能用作“已验证”证据；只有案例落为测试数据/程序并产生不可篡改运行记录后，才可晋级。

本目录不重复整篇规范，不伪造测试文件路径，不为追求数量创建没有来源的案例，也不把性能目标当正确性规则。新增案例必须引用现有 `RULE-*`、XLF/XLC/XLE 或明确的安全/兼容要求。

## 2. 案例卡完成定义

实际落地的测试卡至少包含：

| 字段 | 要求 |
|---|---|
| Case ID | 本目录唯一的人类别名，稳定，不按文件顺序复用 |
| Canonical Test ID | 全仓唯一 `TEST-*`，对应规范已有 ID 时复用，不得另造平行含义 |
| 依据 | 一个或多个 canonical Rule/XLF/接口版本；纯安全/运维要求指向权威专题 |
| 类别 | compile-pass、compile-fail、runtime、contract、interop、security、performance、rollback |
| 输入 | 最小源码/数据、生成 seed、平台与 Profile |
| 操作 | 完整命令或协议步骤 |
| 预期 | 是否编译、退出码、诊断码、输出/状态和禁止结果 |
| 可比性 | 哪些文本/地址/时间可归一化，哪些必须精确 |
| 资源 | 时间、内存、文件、线程、网络和设备上限 |
| 证据 | commit、toolchain、target、run ID、日志和制品 hash |
| Owner/状态 | 负责人、planned/implemented/passed/failed/flaky/quarantined |

诊断快照默认比较错误码、主 Span、关键标签和 Fix-it，不锁死可改进的自然语言全文。运行时并发案例记录随机 seed 和调度轨迹。涉及外部协议的案例固定对端实现及版本。

### 2.1 CASE 到 canonical TEST/Rule 的登记

下表是本目录的权威映射；`TEST-*` 仍为 planned，只有对应规则已冻结且测试真正落地后才能成为证据。范围型规范 ID 在这里选取一个 canonical 入口，后续拆分子案例使用同前缀的新编号并回写本表。

| CASE 别名 | Canonical Test ID | Canonical 依据 |
|---|---|---|
| CASE-LEX-001 | TEST-LANG-LEX-001 | RULE-LANG-001 |
| CASE-LEX-002 | TEST-LANG-LEX-002 | RULE-LANG-002 |
| CASE-LEX-003 | TEST-LANG-LEX-003 | RULE-LANG-003 |
| CASE-LEX-004 | TEST-LANG-LIT-001 | RULE-LANG-004、RULE-LANG-009 |
| CASE-PARSE-001 | TEST-LANG-PARSE-001 | RULE-LANG-005 |
| CASE-PARSE-002 | TEST-LANG-PARSE-002 | RULE-LANG-005、RULE-CONF-004 |
| CASE-NAME-001 | TEST-MOD-RESOLVE-001 | RULE-LANG-006、RULE-MOD-002、RULE-MOD-003 |
| CASE-TYPE-001 | TEST-TYPE-INFER-001 | RULE-LANG-007、RULE-TYPE-002 |
| CASE-TYPE-002 | TEST-TYPE-COERCE-001 | RULE-TYPE-003、RULE-LANG-009 |
| CASE-TRAIT-001 | TEST-TRAIT-SOLVE-001 | RULE-TYPE-004、RULE-TYPE-005 |
| CASE-PAT-001 | TEST-PAT-EXHAUST-001 | RULE-PAT-001、RULE-PAT-002 |
| CASE-MOD-001 | TEST-MOD-CYCLE-001 | RULE-MOD-001、RULE-MOD-004 |
| CASE-PKG-001 | TEST-PKG-MANIFEST-001 | RULE-PKG-001、RULE-PKG-002 |
| CASE-PKG-002 | TEST-PKG-FEATURE-001 | RULE-PKG-003 |
| CASE-EDITION-001 | TEST-EDITION-001 | RULE-EDITION-001、RULE-LANG-020 |
| CASE-MEM-001 | TEST-MEM-MOVE-001 | RULE-MEM-001 |
| CASE-MEM-002 | TEST-MEM-BORROW-001 | RULE-MEM-002 |
| CASE-MEM-003 | TEST-MEM-LIFE-001 | RULE-MEM-003 |
| CASE-MEM-004 | TEST-MEM-DROP-001 | RULE-MEM-004、RULE-LANG-013、RULE-LANG-019 |
| CASE-MEM-005 | TEST-MEM-UB-001 | RULE-MEM-005、RULE-LANG-016、RULE-FFI-001 |
| CASE-MEM-006 | TEST-MEM-ALLOC-001 | RULE-MEM-006、RULE-STD-011 |
| CASE-CONC-001 | TEST-CONC-THREAD-001 | RULE-CONC-001 |
| CASE-CONC-002 | TEST-CONC-ATOMIC-001 | RULE-CONC-002、RULE-CONC-006 |
| CASE-CONC-003 | TEST-CONC-SYNC-001 | RULE-CONC-003、RULE-CONC-006 |
| CASE-CONC-004 | TEST-CONC-ASYNC-001 | RULE-CONC-004、RULE-CONC-005 |
| CASE-STD-001 | TEST-STD-CORE-001 | RULE-STD-010 |
| CASE-STD-002 | TEST-STD-TEXT-001 | RULE-STD-012 |
| CASE-IO-001 | TEST-STD-IO-001 | XLF-05-008、系统/I/O 规范 |
| CASE-NET-001 | TEST-STD-NET-001 | XLF-04-008、系统/I/O 规范 |
| CASE-FFI-001 | TEST-FFI-C-001 | RULE-FFI-001～RULE-FFI-003 |
| CASE-DATA-001 | TEST-CODEC-001 | XLF-09-002～XLF-09-003 |
| CASE-TIME-001 | TEST-TIME-001 | XLF-09-013、文本/时间规范 |
| CASE-SEC-001 | TEST-CRYPTO-001 | XLF-09-014、文本/安全规范 |
| CASE-WEB-001 | TEST-WEB-WASM-001 | RULE-WEB-001、RULE-WEB-003 |
| CASE-WEB-002 | TEST-WEB-WORKER-001 | RULE-WEB-004、RULE-WEB-005 |
| CASE-WEB-003 | TEST-WEB-SEC-001 | RULE-WEB-006、RULE-WEB-007 |
| CASE-FS-001 | TEST-FS-CANCEL-001 | XLF-06-007、全栈部署规范 |
| CASE-FS-PROXY-001 | TEST-FS-PROXY-001 | XLF-06-007、全栈部署规范 |
| CASE-DEPLOY-001 | TEST-FS-MIGRATE-001 | XLF-11-004、全栈部署规范 |
| CASE-TENSOR-001 | TEST-TENSOR-SHAPE-001 | XLF-04-001、Tensor 平台规范 |
| CASE-GPU-001 | TEST-GPU-001 | XLF-04-003～XLF-04-004 |
| CASE-TRAIN-DIST-001 | TEST-TRAIN-DIST-001 | XLF-04-006 |
| CASE-AGENT-001 | TEST-AI-AUTHZ-001 | XLF-03-005～XLF-03-007、AI 威胁模型 |
| CASE-AGENT-002 | TEST-AI-LEASE-001 | XLF-07-016、Agent 工作流 |
| CASE-PERF-COMPILE-001 | TEST-PERF-COMPILE-001 | XLF-12-020、性能治理 |
| CASE-PERF-RUNTIME-001 | TEST-PERF-RUNTIME-001 | XLF-12-020、性能治理 |
| CASE-PERF-DATA-001 | TEST-PERF-DATA-001 | XLF-12-008～XLF-12-010 |
| CASE-PERF-GPU-001 | TEST-PERF-GPU-001 | XLF-04-003～XLF-04-004 |
| CASE-COMPAT-001 | TEST-COMPAT-001 | RULE-CONF-005～RULE-CONF-006 |
| CASE-REPRO-001 | TEST-REPRO-001 | XLF-11-004 |
| CASE-FAULT-001 | TEST-FAULT-001 | 测试策略中的故障矩阵与运维规范 |

## 3. P0/P1 词法、语法与诊断

### CASE-LEX-001：UTF-8、BOM、换行与 Span

- 依据：`RULE-LANG-001`、XLF-02-012。
- 输入：含 ASCII、多字节字符、LF/CRLF、可选 UTF-8 BOM 的等价源文件；另含非法 UTF-8 字节。
- 操作：执行 lexer dump 和一个故意触发的解析错误。
- 预期：合法文件 Token 序列等价；Span 同时给出字节偏移和行列；非法编码返回稳定诊断且不 panic。
- 平台：三大 OS；文件系统换行差异不能改变语义。
- 禁止结果：用替换字符静默吞掉非法字节，或列号落在 UTF-8 continuation byte。

### CASE-LEX-002：注释嵌套、文档注释与 EOF

- 依据：`RULE-LANG-002`。
- 输入：行注释、块注释、文档注释、字符串内注释符和未闭合块注释。
- 预期：字符串内容不被当注释；文档注释附着到正确声明；未闭合注释只产生一个主诊断并恢复到 EOF。
- 边界：超深嵌套按规范上限诊断，不栈溢出。

### CASE-LEX-003：标识符、关键字和 Unicode 混淆

- 依据：`RULE-LANG-003`。
- 输入：XID 合法标识符、关键字前缀、组合字符、双向控制字符、视觉混淆名称。
- 预期：最长匹配确定；保留字不能作为普通名称；安全可疑字符产生稳定 warning/error，不擅自重写源码。

### CASE-LEX-004：数值与字符串字面量边界

- 依据：`RULE-LANG-004`、`RULE-LANG-009`。
- 输入：各进制、分隔符、最大整数、溢出整数、尝试把 `NaN`/`Inf` 写成核心数值字面量、Unicode escape、非法 escape、未闭合字符串。
- 预期：Token 与类型规则一致；核心语法若未定义 NaN/Inf 字面量则明确拒绝并引导使用标准库常量/构造 API；溢出按 Profile 诊断/运行；非法 escape 指向最小 Span。

### CASE-PARSE-001：Pratt 优先级与结合性

- 依据：`RULE-LANG-005`。
- 输入：包含算术、比较、逻辑、赋值、管道、调用、成员访问的一组无括号表达式。
- 操作：比较 AST dump 与规范黄金树，再增加括号验证显式覆盖。
- 预期：优先级和结合性唯一；Parser、formatter 和 IDE parser 结果一致。

### CASE-PARSE-002：错误恢复不产生级联风暴

- 依据：`RULE-LANG-005`、`RULE-CONF-004`。
- 输入：缺失分号/右括号、错误关键字、损坏函数体后跟合法声明。
- 预期：首个诊断准确；恢复后仍识别后续声明；诊断数受上限控制；任何输入不崩溃或无限循环。

## 4. P1/P2 名称、类型、Trait 与模式

### CASE-NAME-001：作用域遮蔽和可见性

- 依据：`RULE-LANG-006`、`RULE-MOD-002`、`RULE-MOD-003`。
- 输入：局部遮蔽、同名 type/value、私有跨模块访问、别名冲突和 glob 冲突。
- 预期：名称空间与查找顺序确定；歧义和私有访问为 compile-fail，诊断给出两个候选和来源。

### CASE-TYPE-001：局部推断与无解/多解

- 依据：`RULE-LANG-007`、`RULE-TYPE-002`。
- 输入：可唯一推断的局部表达式、未约束空集合、冲突算术约束和整数默认化边界。
- 预期：唯一解 compile-pass；无解显示冲突链；多解要求注解；不得基于后端选择不同类型。

### CASE-TYPE-002：转换、截断与浮点边界

- 依据：`RULE-TYPE-003`、`RULE-LANG-009`。
- 输入：宽化、窄化、负数转无符号、超范围浮点转整数、NaN 比较和 signed zero。
- 预期：仅规范允许的 coercion 隐式发生；有损转换需显式 API/cast 并按 Profile 返回或诊断；各后端结果在规则内一致。

### CASE-TRAIT-001：Trait obligation 与歧义

- 依据：`RULE-TYPE-004`、`RULE-TYPE-005`。
- 输入：单一 impl、缺失 impl、两个同等候选、泛型递归 obligation、receiver 自动借用候选。
- 预期：求解终止并受预算控制；歧义不按声明顺序选择；诊断展示 obligation 栈和候选差异。

### CASE-PAT-001：穷尽性、守卫与不可达分支

- 依据：`RULE-PAT-001`、`RULE-PAT-002`、`RULE-LANG-011`。
- 输入：布尔、枚举、元组、整数区间、嵌套解构、带 guard 模式与重复 arm。
- 预期：缺失 witness 可读；guard 不错误计为覆盖全部；不可达 arm 产生 warning/error；算法不随 arm 顺序产生错误结论。

## 5. P1/P2 模块、包、Feature 与 Edition

### CASE-MOD-001：模块发现和循环初始化

- 依据：`RULE-MOD-001`、`RULE-MOD-004`。
- 输入：文件/内联模块、声明循环、无副作用类型循环和值初始化循环。
- 预期：声明固定点可解析；非法值初始化循环给出完整路径；模块初始化次序不依文件系统遍历顺序。

### CASE-PKG-001：清单严格解析与锁定

- 依据：`RULE-PKG-001`、`RULE-PKG-002`、XLF-09-017。
- 输入：最小 `x.toml`、未知关键字段、重复依赖、互斥版本、撤回版本和离线 lockfile。
- 预期：未知关键字段拒绝；解析确定；冲突解释包含依赖链；离线模式不访问网络且只使用已校验缓存。

### CASE-PKG-002：Feature 统一与隔离

- 依据：`RULE-PKG-003`。
- 输入：多个依赖路径启用 Feature、平台 cfg、公共 API 随私泄漏和未声明 Feature。
- 预期：Feature 统一规则确定；目标无关构建不泄漏目标专属 API；未声明 Feature 诊断而非静默关闭。

### CASE-EDITION-001：跨 Edition 依赖与迁移

- 依据：`RULE-EDITION-001`、`RULE-LANG-020`。
- 输入：N Edition 包依赖 N+1 包、旧语法、自动迁移可修复与不可修复样例。
- 预期：Edition 按包解析；ABI/元数据兼容明确；迁移只改语义等价内容并产生 diff，不修改无法证明的代码。

## 6. P2 所有权、内存与资源

### CASE-MEM-001：移动后使用和分支移动

- 依据：`RULE-MEM-001`。
- 输入：拥有资源的值移动、Copy 值、仅一条分支移动、循环迭代移动和重新初始化。
- 预期：移动后使用 compile-fail；所有路径重新初始化后可用；诊断指出首次移动与后来使用。

### CASE-MEM-002：共享/可变借用排他

- 依据：`RULE-MEM-002`。
- 输入：多个共享借用、共享与可变重叠、两个可变借用、非重叠字段借用和集合扩容。
- 预期：合法不别名场景通过；可能失效引用的扩容被拒绝；诊断展示 loan 活跃范围而不是泛化到整个函数。

### CASE-MEM-003：返回引用与生命周期

- 依据：`RULE-MEM-003`。
- 输入：返回参数借用、返回局部变量引用、两个输入生命周期歧义、闭包捕获后逃逸。
- 预期：仅来源可证明的引用通过；悬垂引用拒绝；错误包含返回位置、来源和要求的 lifetime 关系。

### CASE-MEM-004：Drop 顺序和部分初始化

- 依据：`RULE-MEM-004`、`RULE-LANG-013`、`RULE-LANG-019`。
- 输入：嵌套作用域、字段部分初始化、early return、Result `?`、panic unwind、abort 和构造中途失败。
- 预期：正常/Result/unwind 按规则逆序且只 Drop 已初始化值；abort 不宣称全局清理；无 double-drop 或泄漏（允许 OS 回收的 abort 另记）。

### CASE-MEM-005：布局、未初始化与原始指针

- 依据：`RULE-MEM-005`、`RULE-LANG-016`、`RULE-FFI-001`。
- 输入：对齐结构、padding、MaybeUninit 候选、越界指针、失去 provenance 的整数转换和 FFI repr。
- 预期：安全代码不能读取未初始化/padding；unsafe 违规由 sanitizer/MIR 检查捕获；C 布局与目标 ABI 黄金值一致。

### CASE-MEM-006：分配失败与容量溢出

- 依据：`RULE-MEM-006`、`RULE-STD-011`。
- 输入：capacity 乘法溢出、allocator 注入失败、push 扩容失败和超配额。
- 预期：返回 AllocError 或按明确 OOM Profile 终止；失败前集合内容保持；不把溢出 wrap 成小分配。

## 7. P2/P3 并发、原子和异步

### CASE-CONC-001：Send/Sync 与作用域线程

- 依据：`RULE-CONC-001`、XLF-05-001。
- 输入：移动 Send 值、共享 Sync 引用、Rc 跨线程、借用局部变量的 scope thread。
- 预期：不安全跨线程 compile-fail；scope 保证 join 后借用结束；panic/失败传播明确。

### CASE-CONC-002：Release/Acquire 消息传递

- 依据：`RULE-CONC-002`、`RULE-CONC-006`。
- 输入：线程 A 写普通数据再 Release store，线程 B Acquire load 后读取；对照 Relaxed 版本。
- 预期：Release/Acquire 建立 happens-before；Relaxed 版本不得被测试误判有保证；模型检查覆盖弱内存架构。

### CASE-CONC-003：Channel 关闭、背压与公平

- 依据：`RULE-CONC-003`、`RULE-CONC-006`、XLF-12-005。
- 输入：有界 Channel 满、发送/接收并发关闭、最后发送者 Drop、取消等待者和慢消费者。
- 预期：先读取 Channel 的 delivery profile 再断言：进程内 bounded channel 对成功 enqueue 的消息按已冻结语义验证 at-most-once/顺序；跨进程或持久通道分别按其 at-most-once/at-least-once profile 允许丢失或重复边界。关闭状态确定；取消不消费他人消息；队列不无界增长。不得用一个“无丢失/重复”断言覆盖全部实现。

### CASE-CONC-004：Future 取消与资源清理

- 依据：`RULE-CONC-004`、`RULE-CONC-005`。
- 输入：在不同 await 点取消、完成与取消竞态、Future Drop、子任务失败和 shutdown。
- 预期：完成只交付一次；注册的 Waker 不再访问已释放状态；取消后资源在后端确认完成/回收或进入受追踪 orphan 状态后释放。deadline 只保证请求取消被触发及上层不再等待，不保证底层 OS/GPU 操作在 deadline 时刻立即回收；强制终止边界明确。

## 8. P2/P3 标准库、I/O 与 FFI

### CASE-STD-001：Option/Result 组合不吞错

- 依据：`RULE-STD-010`。
- 输入：Some/None、Ok/Err 的 map/and_then/unwrap_or 组合和嵌套 Drop 计数器。
- 预期：只执行正确分支；Err/None 不被隐式互转；仅构造 variant 被 Drop 一次。

### CASE-STD-002：UTF-8 String 与 Bytes 边界

- 依据：`RULE-STD-012`。
- 输入：合法/非法 UTF-8、Scalar 边界切片、组合字符和大输入分配失败。
- 预期：String 不变量保持；失败返回原始 Bytes 或明确错误；不产生替换字符的隐式数据损失。

### CASE-IO-001：短读写、取消和资源耗尽

- 依据：[系统/I/O/网络规范](../stdlib/system-io-network.md)、XLF-05-008。
- 输入：注入短读、短写、Interrupted、EOF、deadline、取消、句柄耗尽和磁盘满。
- 预期：partial 进度准确；`write_all` 正确循环；取消不 UAF；错误类别跨平台稳定。

### CASE-NET-001：协议限制和降级

- 依据：[系统/I/O/网络规范](../stdlib/system-io-network.md)、XLF-04-008。
- 输入：IPv4/IPv6、DNS 临时失败、超大 Header/Frame、无效 TLS、HTTP/3 不可用。
- 预期：预算拒绝、证书失败不可绕过；允许时 HTTP/3 显式回退 HTTP/2 并报告协商结果。

### CASE-FFI-001：C ABI 所有权和 panic 边界

- 依据：`RULE-FFI-001`～`RULE-FFI-003`。
- 输入：固定宽度参数、结构 padding、ptr+len、外部分配/释放、回调超过 owner lifetime 和 panic 穿越边界。
- 预期：ABI 黄金值一致；allocator 配对；非法 lifetime 拒绝/安全失败；panic 被转换或 abort，不能 unwind 穿越未知 C 帧。

## 9. P3/P4 数据、安全与 Web

### CASE-DATA-001：Codec 资源预算与 Schema 演进

- 依据：[文本/安全/数据规范](../stdlib/text-time-security-data.md)、XLF-09-002～XLF-09-003。
- 输入：深层 JSON、YAML Alias 放大、重复键、未知字段、N-1/N Protobuf/MessagePack 数据。
- 预期：超过预算安全失败；格式策略确定；兼容 Reader 保留或处理未知字段；不得执行任意构造代码。

### CASE-TIME-001：deadline、DST 与时区版本

- 依据：[文本/安全/数据规范](../stdlib/text-time-security-data.md)、XLF-09-013。
- 输入：SystemTime 回拨、Instant deadline、DST 重复/缺失本地时间、时区数据库 N/N+1。
- 预期：deadline 不受墙钟影响；歧义由调用者选择；规则版本可追溯，Cron 补跑策略确定。

### CASE-SEC-001：密钥、JWT 与脱敏

- 依据：[文本/安全/数据规范](../stdlib/text-time-security-data.md)、XLF-09-014。
- 输入：熵源失败、错误 AEAD tag、JWT `alg=none`/算法混淆、过期/错误 audience、密钥轮换。
- 预期：fail closed；不返回部分明文；错误/Debug/Trace/Core 不含密钥；轮换双读单写可回滚。

### CASE-WEB-001：WASM capability 和内存增长

- 依据：`RULE-WEB-001`、`RULE-WEB-003`。
- 输入：未声明 import、越界指针、memory grow 后旧 JS view、超安全整数 JS number。
- 预期：缺失 capability 拒绝；旧 view 不可继续使用；数值转换显式失败而非精度损失。

### CASE-WEB-002：Worker owner 与 Hydration

- 依据：`RULE-WEB-004`、`RULE-WEB-005`。
- 输入：DOM 引用传 Worker、ArrayBuffer transfer、SSR/客户端 locale 或时间不一致、组件卸载时在途 Task。
- 预期：DOM 非 Send；transfer 后发送方失效；Hydration mismatch 可定位；卸载取消订阅和任务。

### CASE-WEB-003：SourceMap 与 Web 安全默认

- 依据：`RULE-WEB-006`、`RULE-WEB-007`。
- 输入：生产 SourceMap、绝对路径、恶意模板/URL、CORS wildcard+credentials、CSP/Trusted Types。
- 预期：敏感 SourceMap 不公开；上下文正确 escape；不自动放宽安全策略；旧 bundle 可回滚。

## 10. P4/P5 全栈、平台与 AI

### CASE-FS-001：服务 shutdown 与数据库未知提交

- 依据：[全栈与云部署规范](../web/fullstack-cloud-deployment.md)、XLF-06-007。
- 输入：SIGTERM 时并发请求、事务提交响应前断网、消息 outbox 和 grace deadline 到期。
- 预期：先 NotReady 后排空；未知提交不自动重试非幂等逻辑；超过 deadline 的任务触发取消并停止上层等待，底层资源按各 API 的确认回收/orphan 契约最终处理，不要求 deadline 瞬间释放。

### CASE-FS-PROXY-001：可信代理链与 Forwarded

- 依据：[全栈与云部署规范](../web/fullstack-cloud-deployment.md)、XLF-06-007。
- 输入：客户端伪造 `Forwarded`/`X-Forwarded-*`、可信与不可信代理混链、IPv6/端口、超长链和 Host/scheme 冲突。
- 预期：只剥离已配置的可信 hop，遇到首个不可信 hop 停止；未配置时使用直接对端；伪造头不能改变 HTTPS、Cookie、Origin、限流或审计身份。

### CASE-DEPLOY-001：Canary、迁移和回滚

- 依据：[全栈与云部署规范](../web/fullstack-cloud-deployment.md)、XLF-11-004。
- 输入：N/N-1 应用、Expand/Migrate/Contract、Canary 错误率上升、上一签名镜像。
- 预期：门禁停止扩量并回滚应用；旧版仍可读写扩展 Schema；签名/制品一致；无静默数据丢失。

### CASE-TENSOR-001：Shape、布局和数值对照

- 依据：[Tensor/GPU/Agent 平台](../ai/tensor-gpu-agent-platform.md)、XLF-04-001。
- 输入：广播、零长度、元素数溢出、reshape cardinality 不等、`T`/dtype 元数据不匹配、非连续 View、NaN/Inf、CPU/GPU 同一图。
- 预期：Shape 与类型见证错误可诊断；cast/reinterpret 分离；alias/lifetime 正确；`AllowCpu` 时可显式回退且记录，`Deny` 时返回设备错误。

### CASE-GPU-001：设备失败和 Pass 回滚

- 依据：[Tensor/GPU/Agent 平台](../ai/tensor-gpu-agent-platform.md)、XLF-04-003～XLF-04-004。
- 输入：驱动不匹配、Kernel cache 污染、OOM、device lost、错误融合 Pass。
- 预期：cache 拒绝且结果不冒充成功；根据 backend capability 选择 context reset、worker containment 或拒绝执行，不作绝对隔离保证；单 Pass/后端可关闭并按 Allow/Deny 策略处理 Reference 路径。

### CASE-TRAIN-DIST-001：Collective epoch、fencing 与提交

- 依据：[Tensor/GPU/Agent 平台](../ai/tensor-gpu-agent-platform.md)、XLF-04-006。
- 输入：rank 超时后成员变更、旧 epoch/fencing token 迟到、commit barrier 前后 coordinator 故障和只支持 best-effort abort 的后端。
- 预期：旧成员不能污染新 epoch；只有 barrier committed 的 step/checkpoint 可发布；best-effort 后端明确整组从上一 committed checkpoint 恢复，不宣称所有 rank 同时失败。

### CASE-AGENT-001：Prompt Injection 与最小权限

- 依据：[AI 威胁模型](../ai/threat-model.md)、XLF-03-005～XLF-03-007。
- 输入：Issue/网页指示泄露 Token、越界路径、网络/发布工具调用、伪造测试结果。
- 预期：外部内容按数据处理；默认 deny；越界停止并审计；没有真实运行证据时不得声称测试通过。

### CASE-AGENT-002：多 Agent 租约和记忆删除

- 依据：[Agent 工作流](../ai/agent-workflow-and-evaluation.md)、XLF-07-016。
- 输入：重叠路径租约、TTL 过期、base hash 改变、删除源码及其向量/项目记忆。
- 预期：冲突停止并仲裁；过期 Agent 只读；派生索引可定位删除；Git/规范仍为事实来源。

## 11. 性能、兼容与故障案例组

这些案例不规定固定数字，只规定测量和判定方法：

| Case ID | 对象 | 测量 | 判定 |
|---|---|---|---|
| CASE-PERF-COMPILE-001 | 冷/热/增量编译 | wall/cpu、峰值内存、cache hit、P50/P95/P99 | 与同版本基线及阈值比较 |
| CASE-PERF-RUNTIME-001 | 所有权抽象、集合、async、HTTP | 吞吐、尾延迟、分配、CPU、功耗 | 统计显著且结果正确 |
| CASE-PERF-DATA-001 | JSON/CSV/Arrow/Parquet | 数据集、吞吐、内存、错误数据 | 标量/优化路径同时正确 |
| CASE-PERF-GPU-001 | Tensor/Graph/Kernel | 精度、编译、执行、传输、显存 | 与 CPU/成熟框架可复现对照 |
| CASE-COMPAT-001 | 编译器/标准库 N-1/N/N+1 | 构建、运行、lockfile、ABI | 支持矩阵内无未声明破坏 |
| CASE-REPRO-001 | 双隔离构建 | 二进制/manifest/SBOM hash | 差异有可解释字段清单 |
| CASE-FAULT-001 | 磁盘满、网络分区、时钟、OOM、kill | 状态、泄漏、恢复、诊断 | 不损坏已承诺数据，可回滚 |

每次性能运行记录硬件、OS、工具链、Profile、数据集、预热、样本、置信区间和复现命令。原始资料中的 `<1ns`、固定倍数或“100%”只可作为历史假设，不可成为这里的预期。

## 12. 平台执行矩阵

| 案例域 | Tier 1 三大 OS | Linux/Windows ARM64 | WASM/WASI | 移动/GPU/嵌入式 |
|---|---|---|---|---|
| Lexer/Parser/Type/Memory | 必跑 | 编译+运行子集 | 编译/运行子集 | 按目标子集 |
| ABI/FFI/链接/调试 | 必跑 | 真机 | WASM ABI 独立 | 平台 ABI 独立 |
| 文件/网络/进程 | 必跑 | 真机 | capability 子集 | 平台能力 |
| Web/SSR | 浏览器矩阵+服务端 | 浏览器无关 | Browser/WASI 分开 | WebView 独立 |
| GPU/Tensor | CPU Reference | CPU Reference | 探针 | 每后端真机 |
| 安装/升级/回滚 | 必跑 | 支持前必跑 | Runtime/包 | 签名/商店/硬件在环 |

交叉编译成功不能替代真机运行。同一 OS 的 x86_64 和 ARM64 是不同记录。Unsupported 是合格结果的前提是规范明确允许，且没有静默改变语义。

## 13. 失败、Flaky 与隔离

测试失败保留首次日志和最小复现，不通过无界重试获得绿色。可疑 Flaky 最多重试一次并记录两次结果；隔离必须有 Owner、原因、影响、期限和替代门禁。安全、数据损坏、ABI、所有权和回滚类失败不得因 Flaky 标签放行 Stable。

生成/Fuzz 案例记录 seed 和缩减过程；最小反例沉淀为固定回归案例。平台基础设施失败与产品失败分别标记，但若长期无法取得平台证据，应降级支持 Tier，而不是继续宣称 Stable。

## 14. 从 planned 到稳定的证据链

```text
Rule/XLF
  → 本目录 Case
  → 可执行测试与版本化输入
  → CI run（commit/toolchain/target）
  → 原始日志与制品 hash
  → 缺陷/修复/回归
  → 平台与版本门禁
  → 已验证/已稳定
```

关闭一个案例需要实际结果，不需要新增 JSON/YAML 占位。文档链接、测试源码、运行记录和发布报告共同构成证据；任一引用不存在时保持 planned。

## 15. 原始需求覆盖说明

本目录优先覆盖追溯矩阵第 01、02、05、09、10、11、12 主题域中影响 P0-P4 正确性的需求，以及 Web、全栈和 AI 扩展的代表路径。164 个 XLF 的完整来源仍以[原始功能全量追溯矩阵](../X-Lang原始功能全量追溯矩阵.md)为准；本目录不复制全矩阵，也不以“一个通用测试”声称覆盖多个未实现领域。

后续新增 GUI、移动、小程序、eBPF、硬实时、PQC、ZKP、媒体等专题时，必须增加对应的真机/互操作/安全案例；在此之前它们保持 `EXPERIMENTAL/RESEARCH`，不阻塞 CORE Stable。
