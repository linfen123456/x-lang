---
doc_id: DOC-RUNTIME-PLATFORM-BACKENDS
authority: implementation
owner: role/runtime-team
backup_owner: role/platform-team
version: "1.0"
maturity: CORE
status: 草案
phase: P1
last_reviewed: 2026-08-15
traceability_scope: [XLF-01-005, XLF-01-011, XLF-02-009, XLF-04-007, XLF-05-003, XLF-05-008, XLF-05-009, XLF-06-010, XLF-10-013, XLF-12-013, XLF-12-015]
---
# PAL 平台后端与目标能力实施规范

> 本文把[PAL 契约](./pal.md)展开为 Windows、Linux、macOS/BSD 的后端任务。编译器只通过 `PalTargetRequest` 与 PAL 交互；私有 `TargetSpec` 及代码生成规则见[Backend 规范](../compiler/codegen.md)。本文不把扩展平台或性能目标写成已支持事实，所有平台测试证据均为 `planned`。

## 1. 目标、支持层级与非目标

P1/P4 的**目标范围**是 Windows、Linux、macOS 上的 x86_64/ARM64 原生用户态程序；这不是当前已支持声明。只有平台满足下表发布证据后，平台矩阵才能把目标状态晋级为对应 Tier。能力不是二元“支持/不支持”，而按 Tier 管理：

| Tier | 含义 | 发布要求 |
|---|---|---|
| Tier 1 | 构建、测试、安装和故障修复承诺 | 真机 CI、ABI/运行时/回滚门禁 |
| Tier 2 | 可构建并运行，支持周期较弱 | 定期真机/模拟器测试、已知限制 |
| Experimental | Feature Gate，无兼容承诺 | 原型、能力表、退出条件 |
| Research | labs 隔离 | 不进入 CORE 依赖图 |

WASM/WASI、Android/iOS、RISC-V、eBPF、裸机和小程序不是本文的稳定后端；它们复用公开 capability/handle/error 模型，但必须有独立 RFC、工具链和平台矩阵。

非目标：统一所有 OS 的特有行为、直接把 syscall 注入普通标准库、在交叉编译时运行目标探测程序、为无权限实时/NUMA 能力伪造成功、把 host SDK 路径隐式写入可复现制品。

## 2. PAL 分层与依赖方向

```text
XRT/stdlib portable API
       ↓
PAL semantic adapters (path, clock, thread, process, fs, io, signal)
       ↓
Backend capability table + opaque handle table
       ↓
Windows API | Linux libc/syscall | Darwin libc/Mach/kqueue
```

`unsafe` 限制在最底层 FFI/syscall wrapper；semantic adapter 不暴露裸 handle。每个 wrapper 先把输入转换为明确长度、编码和权限，再调用 OS；返回立即捕获原始错误码，随后映射为稳定 `PalError{kind,platform_code,retryable,operation}`。

## 3. 能力描述与探测

### 3.1 静态与运行时能力分离

`PalCapabilities` 分两部分：

- build capabilities：由签名 sysroot/SDK/toolchain manifest 提供，参与目标 fingerprint。
- runtime capabilities：进程启动后探测 kernel/API/权限，不能反向改变已生成代码的安全语义。

交叉编译只读取目标工具链 manifest，禁止用构建主机 page size、CPU feature 或 OS version 填目标表。runtime probe 失败返回 Unknown/Denied；调用方按保守路径处理。

### 3.2 探测算法

1. 验证 `PalTargetRequest` triple、arch、os 与 sysroot fingerprint。
2. 读取受信工具链能力清单，校验签名/版本。
3. 本机运行时按 allowlist 探测 API 版本、page size、clock、I/O backend、signal、affinity/NUMA。
4. 对每项产生 `Supported(version,limits)`、`Unsupported(reason)`、`Denied(permission)` 或 `Unknown(probe_error)`。
5. canonical 排序并计算 capability fingerprint；缓存键含 OS/kernel/SDK/driver/probe version。

能力缓存只做性能优化，调用关键 OS API 仍处理 `ENOSYS/ERROR_NOT_SUPPORTED/EPERM` 等运行时变化。

## 4. 通用后端接口

| 域 | portable 操作 | 必须保持的语义 |
|---|---|---|
| 内存 | page size、map/protect/unmap、aligned alloc | size/align 溢出检查、W^X、幂等释放 |
| 时钟 | monotonic/wall、sleep/timer | monotonic 不倒退；wall 可调整 |
| 线程 | spawn/join/name/priority/affinity | join handle 一次消费；权限失败可见 |
| 文件 | open/read/write/stat/mmap/rename | 路径边界、短读写、原子替换能力 |
| I/O | backend create/submit/cancel/poll | 一次完成、generation、buffer lease |
| 进程 | spawn/wait/kill/env/stdio | 显式继承列表、进程树清理 |
| 信号/控制 | termination notification | handler/trampoline async-safe |
| TLS/环境 | thread-local、env snapshot | 无隐式秘密回显、生命周期明确 |

通用 adapter 必须能注入 fault backend，以测试磁盘满、权限、EINTR、时钟错误、句柄耗尽和 API 缺失。

## 5. 路径、编码与文件系统语义

内部 Path 不是无条件 UTF-8 字符串：Unix 保存原始字节（禁止 NUL），Windows 保存合法 UTF-16/WTF-16 表示并在展示时转义不可表示值。跨平台 manifest 使用规范化逻辑路径，但实际打开文件必须保留平台语义。

共同规则：

1. workspace 操作以授权目录句柄为根逐段打开；最终对象打开后查询实际路径/文件身份并复核仍在根内，随后所有读写复用该句柄，不能把打开前的 canonicalize/resolve 结果当授权，防止 symlink/reparse point TOCTOU。
2. 不依赖大小写敏感性；冲突检测按目标文件系统能力执行。
3. 原子发布使用同卷临时文件、flush（Profile 要求时）和 atomic replace；若平台不支持必须报告 capability，不能模拟为已原子。
4. rename、delete、open-file replacement 的 Windows/Unix 差异由 adapter 暴露为明确错误/重试策略。
5. long path、UNC、device path、reserved name、symlink/reparse point 都有负向用例。

## 6. Linux 后端

### 6.1 基线

- 动态/静态链接与最低 glibc/musl 范围由 TargetSpec/发布矩阵决定。
- 文件/I/O：`openat` 风格相对目录句柄优先，非阻塞 fd，epoll 基线；io_uring 经 kernel/opcode/permission 探测后启用。
- Timer/Signal：`clock_gettime(CLOCK_MONOTONIC)`、timerfd 候选、signalfd 或 self-pipe 控制线程；不得在 signal handler 做分配/锁。
- Process：`posix_spawn` 或受控 fork+exec；多线程 runtime 中裸 fork 后只能执行 async-signal-safe 路径，优先 posix_spawn。
- zero-copy：sendfile/splice 是 capability，文件/socket 类型不支持时 buffered fallback。

### 6.2 io_uring 门禁

启用前验证 kernel 版本不是充分条件，还要 probe required opcodes、注册能力、seccomp/容器限制。每个 submission 使用 op table index+generation 编码 user_data。SQ/CQ ring size、registered buffer/file 数受 quota。任何 probe/提交异常都可将该 runtime instance 降级 epoll，但已提交 op 先安全排空。

### 6.3 affinity/NUMA/realtime

`sched_setaffinity`、NUMA topology 和 `SCHED_FIFO` 需要权限/容器支持。PAL 只执行显式请求；Denied 返回平台 code。不得自动绑定 L3 或提高实时优先级。`XLF-12-015` 保持实验能力且不承诺硬实时。

## 7. Windows 后端

### 7.1 基线

- 字符 API 使用宽字符版本；路径规范化处理 drive、UNC、`\\?\` 和 reparse point。
- I/O：IOCP 为异步主路径；每个 OVERLAPPED 由稳定 op slot 管理，completion key 不持有可悬空裸指针。
- 时钟：`QueryPerformanceCounter` 作为 monotonic 候选，转换处理频率和溢出；wall clock 使用系统时间 API。
- Thread：`CreateThread`/runtime wrapper、SetThreadDescription；processor group 对多于 64 CPU 的 affinity 单独处理。
- Process：`CreateProcessW`，命令行转义采用确定规则，显式 handle inheritance allowlist，Job Object 管理子进程树。
- 控制事件：Console control handler 只发信号到控制线程；复杂 shutdown 不在 callback 内执行。

### 7.2 IOCP 取消与关闭

`CancelIoEx` 成功仅表示取消请求，不代表 completion 不会到达。buffer/OVERLAPPED lease 保留到 completion packet。关闭 handle 前禁止新提交，取消/排空 outstanding op，再 CloseHandle 并提高 generation。同步完成与 completion packet 双重通知的 API 必须按各 API 文档分类并用一次完成槽去重。

### 7.3 制品与调试

PDB、DLL search path、manifest、签名和安装/卸载属于发布矩阵。runtime 加载 DLL 必须使用受限搜索路径，禁止当前目录劫持。Coredump 对应 Windows Error Reporting/minidump 适配；敏感内存是否纳入 dump 需明确策略。

## 8. macOS/BSD 后端

### 8.1 基线

- I/O readiness 使用 kqueue，EV_CLEAR/EV_ONESHOT 行为由 adapter 固定；文件异步能力不足时使用有界 blocking pool。
- monotonic 使用 mach continuous/absolute time 或受支持 POSIX clock，选择写入 capability。
- Process 优先 posix_spawn；signal 使用 self-pipe/kqueue signal filter，handler 保持最小。
- 路径考虑 Unicode normalization 差异但不擅自改名；文件身份以实际字节/系统 API 为准。
- affinity/NUMA 能力有限时返回 Unsupported，不提供虚假等价接口。

### 8.2 签名与公证边界

runtime/framework/dylib 的 rpath、hardened runtime、entitlement、codesign 和 notarization 是制品发布步骤。PAL 不自动请求 entitlement；缺少权限返回 Denied。插件/JIT 若涉及可执行内存必须遵守 W^X 和 hardened runtime，独立安全评审。

## 9. 进程、环境与句柄继承

跨平台 `ProcessSpec` 概念字段：`program,args,cwd,env_policy,stdio,inherit_handles,limits,deadline,cancel`。执行顺序：

1. 验证 program/cwd 在授权范围或签名工具链中。
2. 从空/最小环境开始合并声明变量；秘密值只通过引用/受控 channel，不写日志。
3. 构建显式 stdio 和 handle/fd allowlist；默认全部 close-on-exec/no-inherit。
4. 预留 process/pipe quota，创建进程组或 Job Object。
5. spawn 成功后登记 wait handle；取消先 graceful signal，再 deadline 后强制结束整个树。
6. 收集截断且脱敏的 stdout/stderr、exit code 和资源摘要。

Unix `fork` 不是 portable API。`XLF-05-003` 的用户价值以安全 `spawn/exec` 保留；fork 仅作为受限底层实现细节。

## 10. Signal、Coredump 与崩溃路径

信号/异常入口只能执行：保存最小原子状态、写入预分配 pipe/event、恢复默认处理或返回。禁止分配、锁、格式化日志、调用用户 callback。控制线程读取事件后执行 shutdown。

Coredump/minidump 元数据可包含 compiler/runtime version、target/profile、feature fingerprint 和匿名化 build ID；不得默认包含环境秘密、令牌或完整用户内存。生成、上传和保留需 opt-in 与运维策略。panic/abort 的细节以[panic 规范](./panic.md)为准。

## 11. I/O 能力与 fallback 矩阵

| 高层能力 | 首选 | 后备 | 禁止的伪装 |
|---|---|---|---|
| async socket | io_uring/IOCP/epoll/kqueue | blocking pool | 把线程阻塞标为 kernel async |
| async regular file | io_uring/IOCP | blocking pool | 在 scheduler worker 直接阻塞 |
| zero-copy file→socket | sendfile/splice/TransmitFile | bounded buffer copy | 未测量即宣称零拷贝 |
| Direct I/O | 平台 flag + alignment | buffered I/O | 静默改变 durability |
| mmap prefetch | madvise/平台 hint | no-op/read hint | 保证驻留/固定延迟 |
| high-res timer | 平台 monotonic | 较低精度 timer | 用 wall clock 模拟 monotonic |

fallback 选择记录在 runtime capability report 和观测事件中，但不把机器特有结果写入可复现编译 hash。

## 12. 分阶段任务

### TASK-P1-COMP-004 / PAL 支撑切片 A：公共语义与 fake backend

- 输出：错误映射、opaque handle、capability model、fault-injection backend。
- 验收：上层不引用 OS 类型；Supported/Unsupported/Denied/Failed 可区分。
- 回滚：保持 fake/synchronous backend 和公开错误模型，禁用尚未完成的真实平台 capability；不得绕过 handle/路径验证。

### TASK-P1-COMP-004 / PAL 支撑切片 B：目标 Tier 1 最小进程/文件/时钟/线程

- Windows/Linux/macOS 各完成 Hello World、文件、monotonic、spawn/wait。
- 验收：同一 contract suite、真实 OS 错误保留、资源无泄漏。
- 回滚：禁用单个平台发布，不影响其他 Tier。

### TASK-P2-RT-001 / PAL 支撑切片 C：异步 I/O 后端

- 依赖 async RFC 和调度器一次完成协议。
- 顺序：epoll/kqueue/IOCP 基线，再评估 io_uring。
- 回滚：按能力切 blocking fallback。

### TASK-P2-RT-001 / PAL 支撑切片 D：process tree、signal、dump、zero-copy

- 每项独立 capability gate。
- 验收：权限、取消、平台退化和敏感数据策略。
- 回滚：关闭特定 capability，使用 portable copy/control path。

### TASK-P5-EXT-001 / PAL 支撑切片 E：扩展目标

- WASI、移动、eBPF、裸机分别建立新后端，不向 Tier 1 私有实现反向依赖。
- 验收：独立目标矩阵、签名、回滚和 EOL。

## 13. 规划测试矩阵

| 测试 ID | 平台/场景 | 证据 | 状态 |
|---|---|---|---|
| `TEST-RUNTIME-PAL-001` | 三 OS 能力、缺 API/权限、交叉目标、host-target 混淆 | capability/contract golden | planned |
| `TEST-RUNTIME-PAL-002` | 目录句柄路径、symlink/reparse、close/reuse、进程/信号 | cross-platform negative fixtures | planned |
| `TEST-RUNTIME-PAL-003` | I/O backend/fallback、zero-copy、dump 脱敏、故障注入 | backend/security report | planned |

最低 OS/SDK/kernel 版本由[平台矩阵](../operations/platform-matrix.md)统一维护，本文不复制易漂移数字。真机、VM、容器和交叉编译测试必须标明，不能以模拟器结果冒充 Tier 1 真机证据。

## 14. 来源、验收与回滚

来源：`XLF-01-005/011`（跨平台与交叉目标）、`XLF-02-009`（XRT）、`XLF-04-007`（io_uring/IOCP）、`XLF-05-003/008/009`（进程、异步和零拷贝 I/O）、`XLF-06-010`（Build Matrix/PAL）、`XLF-10-013`（signal/coredump）、`XLF-12-013/015`（affinity/实时）。

平台晋级必须同时具备 capability 表、contract 测试、安装/升级/回滚、故障注入和安全审查；当前均为 `planned`。任一 backend 回归只关闭对应 capability/Tier，不改变 portable API 的正确性和错误分类。
