---
doc_id: DOC-STDLIB-INDEX
title: X-Lang 标准库公共 API 契约索引
authority: normative
owner: role/standard-library
backup_owner: role/runtime-team
version: "0.2.0"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
applies_to: [x-core, x-alloc, x-std, official-packages]
traceability_scope: [XLF, XLC, XLE]
supersedes: [DOC-STDLIB-INDEX-LEGACY]
---

# X-Lang 标准库公共 API 契约索引

## 1. 范围、层次和稳定性

标准库提供与核心语言一致的值语义、资源清理、错误处理和线程安全；平台差异通过能力查询和显式模块暴露。核心库不依赖操作系统，alloc 提供分配抽象，std 提供平台服务，官方扩展包提供快速演进协议和领域能力。GUI、云厂商 SDK、Tensor、完整协议栈和实验后端不自动成为核心标准库。

| 层 | 内容 | 依赖 | 成熟度/发布 |
|---|---|---|---|
| core | Option、Result、基础 Trait、Slice、迭代器、数值和字符 | 无 OS、可 no_std | CORE，P2 |
| alloc | Vec、String、Box、分配器 | allocator、core | CORE，P2 |
| alloc::shared | Rc、Arc、Weak 与循环所有权工具 | alloc、原子/线程模型 | EXTENDED，P3；RFC 通过前不进入稳定 Prelude |
| std | fs、path、time、thread、sync、process、net、term、log | PAL、XRT | EXTENDED；P2 只冻结 RFC/接口，P3 才交付实现 |
| official | http、tls、serde、db、cli、observability、arrow | std/外部标准 | EXTENDED，P4/P5 |
| experimental | tensor、gpu、gui、media、replay、zk | feature gate | EXPERIMENTAL/RESEARCH |

公开 API 的稳定性由 Semantic Version + Edition 共同决定；删除或改变错误/取消/线程契约必须通过主版本或新 Edition，不能仅修改实现。

## 2. 统一 API 条文

### RULE-STD-001：签名与错误

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** 每个公共函数必须写出参数类型、返回类型、所有权借用、错误类型、取消点、阻塞行为、线程安全、复杂度、分配和平台矩阵。专题中的代码块默认只是非规范性接口草图，只有上述字段齐全并通过 API RFC 后才成为候选公共契约。可恢复失败必须使用 Result 或 Option；不得用空值、哨兵数字或字符串错误替代。错误类型的 variant 名和机器码稳定，文本可本地化。

**解释。** API 文档是编译器、IDE 和 Agent 的机器可消费契约，示例不能取代签名。

**正例。** pub fn read(path: Path) -> Result<Bytes, IoError>；文档注明权限、EOF、取消和 O(n)。

**反例。** 返回 -1 表示权限失败，或文档只写“可能失败”，报告 X-E6001 incomplete API contract。

**边界。** OOM、进程 abort、信号、系统断电不能伪装成普通 Result；必须在 failure model 章节声明。

**诊断/测试/追溯。** X-E6001；TEST-STD-CONTRACT-001..003；来源 XLF-09-001、XLE-GOV-003；RFC-STD-API-01（P2）。

### RULE-STD-002：取消、阻塞与线程安全

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** 可能等待 I/O、锁、队列或外部服务的 API 必须标注 blocking/async 和取消点；取消是协作式，API 必须说明操作已完成、已取消、不可取消或部分结果。公共类型必须声明 Send/Sync；非线程安全类型不得通过共享引用跨线程。所有资源句柄必须有 Drop 或显式 close，并定义 double-close。

**解释。** async 不等于自动非阻塞；同步 API 可以阻塞但必须可识别。关闭通常幂等，但若不是必须返回明确错误。

**正例。** async fn read(cancel: &CancelToken) -> Result<Bytes, ReadError>，取消后返回 Cancelled。

**反例。** 网络 API 未提供 timeout 也未写阻塞行为，报告 X-E6002；把 Rc 放入跨线程 API 产生类型错误。

**边界。** OS 强制终止、SIGKILL 和硬件断电不保证 Drop；WASM/浏览器的 abort 由宿主定义。

**诊断/测试/追溯。** X-E6002；TEST-STD-CANCEL-001..005；来源 XLF-05-006、XLF-10-004、XLE-OPS-001；RFC-STD-ASYNC-01（P3）。

### RULE-STD-003：复杂度、分配和平台矩阵

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** 文档必须用输入规模 n 说明时间复杂度、空间复杂度、平均/最坏情形、是否分配和是否复制；不允许以“零成本”“纳秒级”替代测量。平台矩阵至少列 Windows/Linux/macOS × x86_64/ARM64，并列出 supported、degraded、unsupported、emulated。

**解释。** 复杂度是 API 使用契约，绝对性能是基准结果，不是语言语义。

**正例。** Vec::push：摊销 O(1)，扩容 O(n)，可能分配，旧引用失效规则列明。

**反例。** 在所有平台宣称 sendfile 低于固定延迟，报告 X-E6003 unsupported performance claim。

**边界。** 外部服务、磁盘、浏览器和 GPU 的性能只能按环境报告；能力缺失应返回 Unsupported 而非 silently fallback。

**诊断/测试/追溯。** X-E6003；TEST-STD-MATRIX-001..004；来源 XLF-12-012、XLE-DATA-009；RFC-STD-MATRIX-01（P3）。

## 3. 模块目录

| 模块 | 核心签名示例 | 失败/取消 | 线程安全与复杂度 | 平台 |
|---|---|---|---|---|
| core::option | Option<T>::some/none/get/map | 无异常；get 返回 None | 只读 T 时可 Send/Sync；get O(1) | 全部 |
| core::result | Result<T,E>::map/and_then/unwrap_or | E 显式传播；unwrap 可能 panic | 依 T/E auto traits；O(1) | 全部 |
| alloc::vec | Vec<T>::new/try_with_capacity/push/pop/get | OOM 为 AllocError；push 不取消 | 非共享 Vec 非 Sync；push 摊销 O(1) | 全部 |
| alloc::string | String::from_utf8/try_push_str/as_str | InvalidUtf8/AllocError | UTF-8 invariant；非共享 | 全部 |
| alloc::boxed | Box<T>::new/into_inner | OOM；Drop 释放 | T 为 Send 才可 Send；O(1) move | 全部 |
| alloc::rc | Rc/Weak、upgrade | Weak::upgrade 返回 Option | 单线程；计数增减 O(1) | 全部 |
| alloc::sync | Arc/Weak、clone/downgrade | 分配失败/upgrade None | T: Send+Sync 才跨线程；原子计数 | 全部 |
| std::path/fs | Path、File::open/read/write/rename | IoError、权限、EOF；async 版本可取消 | File 句柄 Send 条件列明；读 O(n) | OS，WASI 能力化 |
| std::time | Instant、Duration、SystemTime | ClockError；单调时钟不可回拨 | Copy 值；O(1) | OS/WASI |
| std::sync | Mutex/RwLock/Atomic/Channel | Poison/Timeout/Closed/Cancelled | guard/ordering 明确；锁 O(1) 非保证 | OS/WASI/wasm 受限 |
| std::thread | spawn/join/scope | JoinError、panic 传播 | Send/Sync 检查；调度实现定义 | OS；浏览器 unsupported |
| std::process | Command/spawn/wait | Spawn/Exit/Signal；wait 可取消 | Child handle 资源 owner | OS；WASI 权限 |
| std::net | Tcp/ Udp/ Resolver | NetError/Timeout/Cancelled | stream Send 条件；吞吐依 OS | OS/WASI socket |
| std::term | Args/Progress/Completion | IoError；终端断开可降级 | 单线程输出 guard；O(n) | TTY/CI |
| std::log | Logger/Span/Counter | SinkError 可采样 | Logger 配置一次后 Sync | OS/WASI |

## 4. 平台能力矩阵

| 能力 | Windows | Linux | macOS | WASI/浏览器 | 缺失行为 |
|---|---|---|---|---|---|
| 文件读写 | supported | supported | supported | wasi capability | Unsupported 或权限错误 |
| async 文件 | IOCP/线程池 | io_uring/epoll | kqueue/线程池 | 宿主异步 API | 保守阻塞 fallback 需显式 |
| 进程/信号 | supported/受权限 | supported | supported | unsupported/受宿主 | CapabilityError |
| 线程 | supported | supported | supported | worker 受限 | compile-time cfg 或 Unsupported |
| TCP/UDP | supported | supported | supported | WASI socket/浏览器 fetch | 不能伪装 Socket |
| mmap/direct I/O | 部分 | supported | 部分 | unsupported | Unsupported |
| TTY/颜色 | Console | TTY | TTY | DevTools/CI | plain text fallback |

## 5. 版本、测试和发布

核心 API 的测试目录为 tests/stdlib/core；平台 API 为 tests/stdlib/platform；官方包为 tests/stdlib/official。每个函数至少有 doc-test、错误注入、边界输入和线程/取消测试；网络和文件测试必须支持临时目录、虚拟时钟和可注入 PAL，禁止连接真实生产服务。

API 变更流程：提交 API diff → 检查错误/取消/线程/复杂度/平台字段 → RFC/ADR → N-1/N/N+1 示例和迁移 → 文档测试 → 版本发布。失败时保留旧实现和签名，扩展包可回滚；不修改核心语言规则。

### 详细专题入口

- [核心容器、错误与所有权 API](./core-api.md)
- [系统、I/O、网络与消息 API](./system-io-network.md)
- [文本、时间、安全、序列化与数据 API](./text-time-security-data.md)

### 待决 RFC

| RFC | 候选 | 门禁 | 最迟 |
|---|---|---|---|
| RFC-STD-API-01 | 错误 enum 与机器码 | API diff、doc schema、兼容 | P2 |
| RFC-STD-ASYNC-01 | executor-independent cancellation | async I/O matrix、泄漏、背压 | P3 |
| RFC-STD-MATRIX-01 | fallback 与 capability 细度 | 六平台实测、权限和故障注入 | P3 |
| RFC-STD-DECIMAL-01 | decimal 库还是内建类型 | IEEE/金融舍入/跨 FFI | P3 |
