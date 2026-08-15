---
doc_id: DOC-STDLIB-SYSTEM-IO-NETWORK
authority: normative
owner: role/standard-library
backup_owner: role/runtime-team
version: "0.1"
maturity: EXTENDED
status: 草案
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [XLF, XLC, XLE]
---
# X-Lang 系统、I/O、网络与消息标准库实施规范

> 文档性质：候选规范（Normative Draft）
> 成熟度：基础系统能力 `EXTENDED`，协议与消息扩展 `EXTENDED`，高级零拷贝能力 `EXPERIMENTAL`
> 目标阶段：P2 冻结接口边界，P3 交付系统与基础网络，P4/P5 扩展协议和数据通道
> 权威入口：[标准库索引](./README.md)｜[运行时 I/O](../runtime/io.md)｜[平台矩阵](../operations/platform-matrix.md)

## 1. 目标与非目标

本规范把原始材料中的文件、路径、进程、信号、网络、异步 I/O、IPC、消息总线与零拷贝设想，收敛成能够分阶段实现的库边界。调用者应能在 Windows、Linux、macOS 上使用一致的资源与错误模型，同时显式识别平台差异。

本规范不要求 X-Lang 自研 TLS、HTTP/3、QUIC 或数据库协议；优先封装成熟实现并通过互操作套件验收。它也不承诺“所有 I/O 都异步”“所有传输都零拷贝”或固定纳秒级延迟。原始材料中的性能数字只能进入基准候选，不能成为 API 语义。

## 2. 分层和责任边界

| 层 | 责任 | 不负责 |
|---|---|---|
| `std::path` / `std::fs` | 路径、文件、目录、元数据、原子替换 | 绕过 OS 权限、隐式字符集转换 |
| `std::io` | 同步 Reader/Writer、缓冲、复制、取消上下文 | 选择全局异步执行器 |
| `std::async_io` | Future 化 I/O、超时、取消、背压 | 保证底层系统调用可立即取消 |
| `std::process` / `std::signal` | 子进程、环境、退出和安全信号接口 | 在多线程进程中提供无约束 `fork` |
| `std::net` | DNS、TCP、UDP、Unix/Named Pipe 抽象 | 把浏览器 `fetch` 伪装成原生 Socket |
| 官方协议包 | TLS、HTTP/1.1/2/3、QUIC、WebSocket、RPC | 将快速演进协议冻结进 `core` |
| `std::ipc` / 官方消息包 | 共享内存、管道、Pub/Sub、持久消息 | 宣称跨故障 exactly-once |
| XRT/PAL | IOCP、epoll、kqueue、io_uring 等后端 | 暴露后端句柄为跨平台公共语义 |

依赖方向必须为“公共 API → XRT/PAL → OS”。标准库不得反向依赖云厂商 SDK、Web 框架或 AI 运行时。

## 3. 公共上下文与错误模型

以下签名只用于表达候选接口形状，并非已冻结语法或 ABI。每个接口进入 RFC 时必须补齐参数/返回值所有权、是否阻塞、取消点、复杂度、分配行为和平台支持；在这些字段齐全前不得作为稳定公共 API。所有可能阻塞或等待的候选 API 接受显式操作上下文：

```x
struct IoContext<'a> {
    cancel: Option<&'a CancelToken>,
    deadline: Option<Instant>,
    quota: Option<&'a ResourceQuota>,
}

enum IoErrorKind {
    NotFound, PermissionDenied, AlreadyExists, InvalidInput,
    WouldBlock, TimedOut, Cancelled, Interrupted, Closed,
    ResourceExhausted, Unsupported, Integrity, Other,
}

struct IoError {
    kind: IoErrorKind,
    operation: &'static str,
    path_or_endpoint: Option<RedactedText>,
    os_code: Option<i32>,
    partial: usize,
}
```

约束如下：

- `Cancelled` 表示库观察到取消请求，不表示操作一定没有产生外部效果；是否提交必须由具体 API 说明。
- `partial` 记录已读写字节，调用者不得假设失败时总是零进度。
- 原始路径、URL 凭据、环境变量值和报文内容默认不得进入错误文本。
- OS 错误码仅用于诊断，跨平台分支必须匹配稳定的 `IoErrorKind`。
- 资源耗尽必须可区分文件描述符、句柄、内存、队列、磁盘配额和连接限制。

## 4. 路径、文件与流

### 4.1 路径语义

`Path` 保存平台原生路径表示，`Utf8Path` 只接受 UTF-8。两者不能隐式互转。Windows 盘符、UNC、保留设备名与大小写规则，Unix 原始字节路径和符号链接都必须保持宿主语义；库不得静默规范化导致权限边界变化。

```x
fn canonicalize(path: &Path) -> Result<PathBuf, IoError>
fn join(base: &Path, child: &Path) -> Result<PathBuf, PathError>
fn file_name(path: &Path) -> Option<&OsStr>
```

安全敏感代码不能采用“先 canonicalize/检查，再按字符串路径打开”的两步流程，因为检查后目标可能被符号链接或 rename 替换。调用者先取得已授权目录的 capability/目录句柄，再逐组件相对解析并原子打开：Unix 使用 `openat`/`openat2` 类语义与 `O_NOFOLLOW`/解析限制，Windows 使用目录 handle、reparse-point 拒绝和最终对象身份校验的等价机制。每个组件均拒绝 `..` 越界、意外符号链接/reparse point 和挂载点逃逸；创建临时文件、rename 和删除也相对同一目录句柄执行。仅字符串前缀或打开前 canonicalize 都不是合格防护。

### 4.2 文件句柄和打开选项

```x
struct OpenOptions {
    read: bool, write: bool, append: bool,
    create: CreateMode,
    truncate: bool,
    follow_symlinks: bool,
}

fn open(path: &Path, options: OpenOptions) -> Result<File, IoError>
fn read(&mut self, out: &mut [u8], ctx: &IoContext) -> Result<usize, IoError>
fn write(&mut self, input: &[u8], ctx: &IoContext) -> Result<usize, IoError>
fn flush(&mut self, ctx: &IoContext) -> Result<(), IoError>
fn close(self) -> Result<(), IoError>
```

`File` 拥有句柄，移动后原变量不可用；`Drop` 尝试关闭但无法返回错误，因此需要持久性保证时必须显式 `flush`/`close`。重复关闭在类型安全路径不可表达；FFI 句柄重复关闭返回 `Closed`。`write` 可以短写，便利函数 `write_all` 才保证循环至完成或返回部分进度。

### 4.3 原子文件更新

配置、锁文件和注册表元数据使用“同一目录 capability 下创建独占临时文件 → 写入 → flush 文件数据/元数据 → 原子 rename/replace → 同步父目录”的流程。持久性不是一个布尔承诺，而是显式 Profile：`BestEffort` 只保证进程内可见顺序，`DataDurable` 要求文件数据落盘，`MetadataDurable` 还要求 rename 与父目录项可恢复。调用者选择的 Profile 必须映射到平台能力；平台或文件系统不能提供时返回 `UnsupportedDurability`，不得宣称持久成功。跨文件系统 rename、网络文件系统语义和 Windows sharing/replace 冲突必须返回明确错误，不能退化成无提示复制；崩溃注入测试分别验证 rename 前后可接受状态。

### 4.4 映射和零拷贝

`mmap`、Direct I/O、`sendfile`、`splice` 属于 `EXTENDED`/`EXPERIMENTAL` 能力：

- 映射对象的 lifetime 不得超过文件/映射资源；截断竞态必须记录为平台风险。
- Direct I/O 暴露对齐和块大小要求，失败可选择显式 buffered fallback。
- 零拷贝 API 返回实际采用的路径；普通复制 fallback 不得仍标记为 zero-copy。
- 预取只接受 `Sequential/Random/WillNeed/DontNeed` 等 hint，不改变正确性。

## 5. 异步 I/O、取消与背压

同步和异步 API 共享错误与资源契约，但不是同一函数的隐式模式。异步对象绑定 Reactor/Proactor 能力，由 XRT 在 IOCP、epoll/kqueue、io_uring 或受控线程池之间选择。

```x
async fn read_async(
    stream: &mut AsyncRead,
    out: &mut [u8],
    ctx: &IoContext,
) -> Result<usize, IoError>
```

端到端状态为：`Created → Submitted → {Completed | CancelRequested} → Reaped`。取消与完成竞态时只能有一个终态对调用者可见；后端仍产生的完成事件必须被回收，不得访问已释放缓冲区。缓冲区借用至少持续到 Future 完成或安全取消确认。

背压规则：

- 有界队列是默认值，容量由调用者或运行时 Profile 指定。
- 队列已满时显式选择等待、返回 `WouldBlock`、丢弃或覆盖；不得默认无限增长。
- 超时由单调时钟计算；系统时间回拨不影响 deadline。
- 将阻塞文件或 DNS 调用放入异步路径时，必须隔离在线程池并占用配额。

## 6. 进程、环境和信号

```x
struct Command {
    program: PathBuf,
    args: Vec<OsString>,
    env: EnvPolicy,
    cwd: Option<PathBuf>,
    stdin: Stdio, stdout: Stdio, stderr: Stdio,
}

fn spawn(command: Command, ctx: &IoContext) -> Result<Child, SpawnError>
fn wait(&mut self, ctx: &IoContext) -> Result<ExitStatus, WaitError>
fn terminate(&mut self, grace: Duration) -> Result<Termination, ProcessError>
```

参数以数组传递，不经过 Shell；只有显式 `ShellCommand` 才允许 Shell 解释，并要求调用方标注注入风险。环境策略默认为继承白名单，而不是把秘密全部复制给子进程。Unix `fork` 仅作为受限 unsafe API，必须说明多线程和 async-signal-safe 限制；跨平台主路径使用 spawn/CreateProcess/posix_spawn 类后端。

信号处理器只执行 async-signal-safe 操作，通常只写入无锁标志或 self-pipe，再由正常任务执行清理。SIGKILL、TerminateProcess、断电和进程 abort 不保证 Drop 或优雅停机。

## 7. 基础网络

### 7.1 地址、DNS 与连接

```x
async fn resolve(host: &str, service: &str, ctx: &IoContext)
    -> Result<Vec<SocketAddr>, ResolveError>
async fn connect(addrs: &[SocketAddr], options: ConnectOptions, ctx: &IoContext)
    -> Result<TcpStream, ConnectError>
```

DNS 结果有 TTL 和来源；错误区分不存在、临时失败、策略拒绝和超时。连接策略可实现 Happy Eyeballs，但必须限制并发探测和总 deadline。Endpoint 日志默认脱敏用户信息和 Token。

### 7.2 TCP、UDP 和监听器

TCP 是字节流，不保留消息边界；`read` 返回 0 表示有序 EOF。半关闭、Nagle、keepalive、缓冲区与 linger 均为显式选项。UDP 保留数据报边界，返回实际来源；超长数据报不得静默拼接。服务器接受循环必须支持取消、并发上限、连接配额和优雅排空。

```x
async fn serve(listener: TcpListener, service: impl Service, shutdown: Shutdown) {
    // accept -> quota -> task scope -> request -> drain -> close
}
```

### 7.3 TLS 与应用协议

TLS 作为官方安全包，默认验证证书链、主机名、有效期和撤销策略；禁止默认跳过验证。密钥由安全存储句柄引用，不以字符串复制。HTTP、QUIC、gRPC、WebSocket 必须分别通过标准互操作套件；协议版本、最大头部、最大帧、并发流、空闲超时和重试策略均有上限。

自动重试只允许幂等操作或带幂等键的显式操作；网络错误不等于服务端未执行。HTTP/3/QUIC 失败可回退 HTTP/2，但必须暴露协商结果且不能降低 TLS 安全策略。

## 8. IPC、消息总线和持久重放

Pub/Sub 是官方扩展包，不是语言关键字。最小接口包含：

```x
fn publish<T: Message>(&self, topic: &Topic<T>, value: T, ctx: &IoContext)
    -> Result<PublishAck, MessageError>
fn subscribe<T: Message>(&self, topic: &Topic<T>, options: SubscribeOptions)
    -> Result<Subscription<T>, MessageError>
```

消息必须有 schema/version、message_id、producer_id 和可选幂等键。P3 最小切片只承诺进程内有界队列和本机 IPC 的 at-most-once；持久日志在独立里程碑提供 at-least-once。消费者应在副作用提交后确认，重复消息由业务幂等键处理。

共享内存 Ring Buffer 必须选择明确变体（SPSC 或 MPSC），记录槽位状态、生产/消费序号、内存顺序、所有权转移和崩溃恢复。大消息可通过共享区域句柄传递，但发送方在接收确认前不能重用区域。无法满足对齐、权限或同机条件时，显式回退复制通道。

持久日志需要校验和、段编号、原子截断、恢复扫描、保留策略和 schema 迁移。它不提供跨数据库与消息日志的通用 exactly-once。

## 9. 安全与资源控制

- 文件、网络、进程和共享内存能力默认最小权限；沙箱环境由 capability handle 授权。
- 服务器必须设置最大连接、请求、帧、头部、队列、文件句柄、内存和处理时间。
- TLS、压缩、正则、解析器和反序列化器都需防止放大与拒绝服务。
- 临时文件使用不可预测名称和安全权限；禁止先检查后打开的 TOCTOU 模式。
- 日志不得记录认证头、Cookie、密钥、完整查询参数或未经脱敏的消息体。
- IPC 对端需要身份、权限和协议版本验证；共享内存不能仅凭路径名建立信任。

## 10. 平台矩阵与降级

| 能力 | Windows | Linux | macOS | WASI | 浏览器 |
|---|---|---|---|---|---|
| 文件/目录 | Win32/NT | POSIX | POSIX | capability FS | 不提供通用 FS |
| 异步网络 | IOCP | epoll/io_uring | kqueue | 宿主决定 | fetch/WebSocket |
| 子进程 | CreateProcess | posix_spawn/fork 受限 | posix_spawn | 通常不支持 | 不支持 |
| 信号 | Console/Job Object 子集 | POSIX | POSIX | 宿主决定 | 不支持 |
| Unix Socket/Named Pipe | Named Pipe | Unix Socket | Unix Socket | 受宿主限制 | 不支持 |
| mmap/zero-copy | 部分支持 | 支持 | 部分支持 | 通常不支持 | SharedArrayBuffer 受策略 |
| 原生 TCP/UDP | 支持 | 支持 | 支持 | Socket capability | 不直接提供 |

能力缺失返回 `Unsupported` 或编译期 `cfg` 诊断。只有调用者显式允许时才能使用语义等价的 fallback；安全级别降低、持久性降低或消息保证降低不属于可静默 fallback。

## 11. 最小可用切片与阶段

| 切片 | 交付内容 | 不包含 | 通过条件 |
|---|---|---|---|
| P2-SYS-0 | 仅冻结 Path/File/Reader/Writer/Process 的 RFC、所有权、错误和 PAL 接口 | 不宣称可用标准库实现 | 规范审查、平台探针和契约测试设计通过 |
| P3-SYS-1 | Path、File、Reader/Writer、安全临时目录、同步进程 | async、TLS、消息持久化 | 三大 OS 文件/进程契约测试 |
| P3-SYS-2 | TCP/UDP/DNS、deadline、基础 async I/O | HTTP/3、io_uring 专属优化 | 取消竞态、资源耗尽、互操作通过 |
| P3-SYS-3 | 进程内 Channel、Pipe/Unix Socket/Named Pipe | 共享内存零拷贝 | 背压、关闭、崩溃测试通过 |
| P4-NET-1 | TLS、HTTP/1.1/2、WebSocket、RPC | 自研密码原语 | 标准服务器互操作与安全审计 |
| P5-NET-2 | HTTP/3/QUIC、持久消息、Ring Buffer | exactly-once 承诺 | Feature Gate、回退和平台基准 |

## 12. Planned 测试与验收证据

以下均为计划案例，不表示代码或结果已存在：

- `TEST-STD-IO-001`：短读、短写、EOF、Interrupted 与 partial 进度。
- `TEST-STD-IO-002`：取消和完成同时发生，缓冲区无 UAF、完成只交付一次。
- `TEST-STD-FS-001`：目录 capability、逐组件 no-follow、符号链接/reparse point 竞态、原子替换、磁盘满和权限撤销。
- `TEST-STD-FS-002`：在 rename/fsync 各阶段注入崩溃，分别验证 BestEffort/DataDurable/MetadataDurable 的允许状态。
- `TEST-STD-PROC-001`：参数无 Shell 注入、环境白名单、超时终止和子进程回收。
- `TEST-STD-NET-001`：IPv4/IPv6、DNS 临时失败、连接 deadline 和半关闭。
- `TEST-STD-NET-002`：TLS 证书、主机名、过期、协议降级与密钥脱敏。
- `TEST-STD-MSG-001`：有界背压、重复投递、崩溃恢复、校验损坏和 schema 迁移。
- `TEST-STD-ZC-001`：零拷贝资格、copy fallback、跨进程所有权与异常退出。

验收需要测试卡、真实平台、工具链版本、输入、期望、实际结果和日志；仅有 API 文档不构成“已验证”。性能验收遵循[性能与兼容测试](../testing/performance-and-compatibility.md)，禁止复用原始材料的绝对数字。

## 13. 回滚与兼容

协议包、io_uring、零拷贝和持久消息均由 Feature Gate 隔离。后端失败时可回滚到已验证的同步/通用实现；公共错误类别、取消语义和持久性保证不得随回滚改变。磁盘日志格式采用版本字段和先读后写迁移，保留 N-1 读取器。若某平台连续无法满足正确性或安全门禁，则降级 Tier，而不是让其他平台改变语义。

## 14. 原始资料追溯

| 来源 | 回归内容 |
|---|---|
| `1.txt` | XLF-01-009、XLF-01-011：Channel、跨平台标准库 |
| `2.txt` | XLF-02-009：XRT I/O 与标准库 |
| `4.txt` | XLF-04-007、XLF-04-008：跨平台异步 I/O、HTTP/QUIC/gRPC/WebSocket |
| `5.txt` | XLF-05-003、XLF-05-004、XLF-05-008、XLF-05-009、XLF-05-010：进程、IPC、异步文件与零拷贝 |
| `9.txt` | XLF-09-013、XLF-09-014：任务调度、认证安全包 |
| `10.txt` | XLF-10-009、XLF-10-013：Stream 背压、信号与 Coredump |
| `11.txt` | XLF-11-012：锁、Fence 与原子顺序（具体内存语义见并发规范） |
| `12.txt` | XLF-12-005～XLF-12-010、XLF-12-013：消息、Ring Buffer、重放、数据加载、NUMA |

这些来源只证明需求价值，不自动接受其中的实现断言；最终状态以[回归路线](../X-Lang未纳入与偏离内容再审核及回归路线.md)为准。
