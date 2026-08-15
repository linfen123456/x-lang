---
doc_id: DOC-SPECS-MEMORY-CONCURRENCY
title: X-Lang 所有权、内存与并发规范
authority: normative
owner: role/runtime-team
backup_owner: role/compiler-team
version: "0.2.0"
maturity: CORE
status: 草案
phase: P0
last_reviewed: 2026-08-15
applies_to: [borrow-checker, mir, xrt, core-sync, async-runtime]
traceability_scope: [XLF, XLC]
supersedes: [DOC-SPECS-MEMORY-CONCURRENCY-LEGACY]
---

# X-Lang 所有权、内存与并发规范

## 1. 模型和保守边界

默认模式无 tracing GC；每个值有唯一 owner，作用域结束执行 Drop。所有权系统只保证其模型覆盖的悬垂、双重释放和数据竞争风险，不保证算法正确、资源永不耗尽或 unsafe/FFI 代码安全。GC、GPU 统一地址空间、持久内存、通用硬实时和编译器自动插锁均为独立 RFC。

术语：owner 是负责销毁值的绑定或字段；move path 是可单独转移的字段路径；shared borrow 是可并存但只读的 &T；mutable borrow 是独占读写的 &mut T；lifetime 是引用有效的静态区间；Send 表示可转移到另一个执行单元；Sync 表示可通过共享引用安全访问；happens-before 是内存模型中的偏序。

## 2. 所有权、借用和 Drop

### RULE-MEM-001：所有权与移动

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 每个非 Copy 值在任一时刻只有一个 owner。按值传参、赋给新 place 或 move 闭包捕获时发生 move，源 move path 立即失效；读取失效 path 必须在编译期拒绝。Copy 只有在所有字段可复制且没有拥有资源析构语义时才能实现。

**解释。** move 是静态状态改变，不等于运行时 memcpy；优化器可消除拷贝，但不能恢复源可用性。字段级 move 后未移动字段仍可用。

**正例。** let a=String::from("x"); let b=a; print(b)。

**反例。** let a=String::from("x"); let b=a; print(a) 报 X-E4001 use of moved value。

**边界。** 部分移动、模式绑定和 replace 的初始化由 MIR 验证；unsafe 不能恢复已失效 owner。

**诊断/测试/追溯。** X-E4001；TEST-MEM-MOVE-001（pass）、002（fail）、003（field boundary）；来源 XLF-01-006、XLF-05-001、XLC-CORE-010；RFC：无（核心安全基线）。

### RULE-MEM-002：借用排他性

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 同一生命周期区间可有任意多个 &T 或一个 &mut T，但不得同时有重叠的共享与可变借用。创建借用不转移 owner；借用使用结束后 owner 才能执行独占操作。违反必须编译期拒绝。

**解释。** 这是多读单写规则。实现可用 NLL 或更保守词法生命周期，但不得放宽安全结果；RefCell 等只能在自己的动态契约内检查。

**正例。** let r1=&v; let r2=&v; print(r1.len()+r2.len())。

**反例。** let r=&v; let w=&mut v; print(r) 报 X-E4002 conflicting borrows。

**边界。** 不相交字段可由 RFC 允许并行借用；索引无法证明不相交时按整体 place 处理。禁止自动插锁掩盖冲突。

**诊断/测试/追溯。** X-E4002；TEST-MEM-BORROW-001..004；来源 XLF-05-001、XLC-CORE-010..013；RFC-MEM-BORROW-01（字段级/NLL，P1）。

### RULE-MEM-003：生命周期与返回引用

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 引用 lifetime 不得长于被借 place。返回引用必须来自输入引用或静态存储，不能来自局部 owner。省略只适用于规范列出的参数/返回模式，歧义必须显式标注。

**解释。** lifetime 是静态约束，不是运行时计数器。返回 owner 应 move 或使用拥有的智能指针。

**正例。** fn first<'a>(x:&'a [u8])->Option<&'a u8>{ x.get(0) }。

**反例。** fn bad()->&str { let s=String::from("x"); &s } 报 X-E4003 dangling reference。

**边界。** async 状态机、生成器、scoped task 和 FFI callback 需要额外约束；堆分配不会自动延长引用。

**诊断/测试/追溯。** X-E4003、X-E4004；TEST-MEM-LIFE-001..004；来源 XLF-01-006、XLF-03-001、XLF-05-006；RFC-MEM-LIFE-01（NLL/HRTB，P2）。

### RULE-MEM-004：Drop 顺序与部分初始化

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 已初始化 owner 必须恰好 Drop 一次。局部变量按声明逆序 Drop；结构体字段按声明逆序 Drop；部分初始化对象只 Drop 已初始化字段。显式 drop 后不得使用。正常返回、Result 和 unwind 执行可达清理；abort 可不保证全局清理。

**解释。** 确定 Drop 顺序是资源安全和锁释放基础。defer 若采纳，只能增加明确 LIFO 清理，不得双重释放。

**正例。** let a=Guard("a"); let b=Guard("b"); 退出时 b 后 a。

**反例。** 伪造初始化状态使析构两次报 X-E4005 invalid drop state。

**边界。** panic hook、取消、future drop 和 FFI 句柄各自需测试；析构不得假设后续字段存在。

**诊断/测试/追溯。** X-E4005；TEST-MEM-DROP-001..005；来源 XLF-05-001、XLF-10-001；RFC-ERROR-01（defer/abort，P1）。

## 3. 内存模型与 unsafe

### RULE-MEM-005：初始化、布局和 pointer provenance

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 读取未初始化值、越界、解除无效/未对齐指针、整数任意转可解引用指针、访问已结束 lifetime 的对象均禁止。安全代码不能观察普通类型 padding/字段偏移。只有 repr(C)/明确布局属性形成稳定 FFI 布局；raw pointer、volatile、MMIO、自定义分配器必须在 unsafe 中并满足前置条件。

**解释。** 该条文建立保守 provenance 边界，避免把 LLVM UB 直接暴露给用户。unsafe 是调用者证明义务，不是关闭全部检查的开关。

**正例。** unsafe 中使用 read_unaligned，且 API 前置条件证明指针指向已初始化对象。

**反例。** 0x1 as *mut u32 后解引用违反契约，报告 X-E4101。

**边界。** 具体布局、空指针 niche、packed 引用、地址空间和 PMEM/GPU 一致性待 RFC-ABI-01；sanitizer 不是规范保证。

**诊断/测试/追溯。** X-E4101、X-R4102；TEST-MEM-UB-001..006；来源 XLF-05-003、XLF-06-006、XLC-CORE-010..013；RFC-ABI-01（P2，MIR interpreter/跨后端/布局探针）。

### RULE-MEM-006：分配失败、容量和资源

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 分配、增长、映射和句柄获取可能失败，API 必须用 Result、OOM hook 或文档化 abort 报告；不能以空指针构造安全值。容量计算必须检查溢出；集合扩容后旧引用是否失效必须在 API 契约中说明。

**解释。** “零分配”只能是特定路径的测量结果。Arena、HugePage、mmap 和共享内存必须声明 owner、释放、线程和平台能力。

**正例。** let buf=Vec::try_with_capacity(n)?。

**反例。** Vec::with_capacity(usize::MAX) 不能回绕，报告 X-E4104 或 X-R4103。

**边界。** OOM handler、实时线程分配禁令和 allocator hook 递归限制由 runtime profile/RFC 决定；无能力时返回 Unsupported。

**诊断/测试/追溯。** X-E4104、X-R4103；TEST-MEM-ALLOC-001..004；来源 XLF-05-002、XLF-05-004；RFC-RUNTIME-ALLOC-01（P2）。

## 4. 线程、原子和结构化并发

### RULE-CONC-001：Send/Sync 与线程所有权

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** spawn 闭包捕获值必须 Send；通过共享引用跨线程访问的类型必须 Sync。编译器在 spawn 点检查捕获、返回值和 join 句柄；作用域线程结束前必须 join 或显式 detach，detach 的资源和错误传播需记录。默认不安全跨线程的类型不实现 Send/Sync。

**解释。** Send/Sync 是能力标记，不是自动加锁。共享状态必须显式使用 Mutex/RwLock/Atomic/Arc。

**正例。** let data=Vec::new(); thread::spawn(move || use_data(data))。

**反例。** Rc<T> 跨线程产生 X-E4201；借用局部变量过期产生 X-E4202。

**边界。** OS 线程数、调度、公平性、栈和亲和性是 runtime/平台属性；不承诺纳秒切换或硬实时。

**诊断/测试/追溯。** X-E4201..4202；TEST-CONC-THREAD-001..005；来源 XLF-05-001、XLF-12-014、XLC-CORE-014；RFC-CONC-STRUCTURED-01（P2）。

### RULE-CONC-002：原子与内存顺序

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 原子 API 必须显式指定或使用文档化默认顺序；至少支持 Relaxed、Acquire、Release、AcqRel、SeqCst。实现按抽象 happens-before 语义工作，不直接暴露 CPU 指令。`atomic::fence(order)` 只接受 Acquire、Release、AcqRel 或 SeqCst；Release fence 必须由其前序普通写和后序原子写共同发布，Acquire fence 只有在其前序原子读观察到发布序列时才取得同步，单独 fence 不创造跨线程通信。顺序错误可导致逻辑错误但不能形成语言层数据竞争；原子对象必须满足对齐和 lifetime。

**解释。** PAUSE、YIELD、LDREX/STREX 和 LOCK CMPXCHG 是实现映射。无锁结构由库作者提供证明和 litmus 测试。

**正例。** ready.store(true, Release); while !ready.load(Acquire) { spin(); }。

**反例。** 两线程普通变量并发读写报告 X-E4203 data race，禁止自动加锁。

**边界。** volatile 不提供同步；compare_exchange 必须分别声明成功和失败顺序，失败顺序不得为 Release/AcqRel；进程共享、GPU 原子和 C/C++ 原子互操作待 ABI RFC。

**诊断/测试/追溯。** X-E4203、X-E4204；TEST-CONC-ATOMIC-001..006；来源 XLF-11-007、XLF-12-014、XLC-CORE-014；RFC-MEMMODEL-01（P2，litmus/模型检查）。

### RULE-CONC-003：锁、Channel 与数据竞争

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 锁保护数据只能在对应 guard 内访问，guard Drop 释放锁。Channel 必须定义有界/无界、关闭、send/recv 错误和消息所有权；有界满时阻塞、返回 Full 或等待取消，不能无限增长。数据竞争在所有合规实现中禁止。

**解释。** CSP/Actor 是库层；背压不能由语言自动假定，适配器必须定义速率和取消传播。

**正例。** let _g=mutex.lock()?; shared.update(); let ch=channel::bounded::<Msg>(64)。

**反例。** 保存裸借用超过 guard 报 X-E4205；恶意无界输入可报告 X-R4206 capacity exceeded。

**边界。** 死锁/活锁/饥饿不能全部静态判定；库应提供 timeout/cancel。自动插锁和持久 ring buffer 属扩展。

**诊断/测试/追溯。** X-E4205、X-R4206；TEST-CONC-SYNC-001..006；来源 XLF-01-009、XLF-05-006、XLF-12-014；RFC-CONC-CHANNEL-01（P2）。

## 5. async、取消和并发失败

### RULE-CONC-004：Future、await 与取消

- maturity: EXTENDED
- status: 草案
- phase: P3

**规范性条文。** async/await 在 P2 为扩展候选；未通过 RFC 前不能自动改变普通函数。接受后 Future 显式表示未完成计算，await 只在 executor 上挂起，不能阻塞 executor 工作线程；Future 被 drop/取消时执行已初始化字段 Drop，并记录底层 I/O 是取消、完成还是不可取消。

**解释。** 取消是协作式，不保证立即停止。网络、文件和 GPU 操作可能只能标记取消或等待安全边界，调用者须处理 Cancelled 与部分结果。

**正例。** let response = client.get(url).with_timeout(t).await?。

**反例。** 单线程 executor 中阻塞 read 报 X-W4301；取消后写 future 状态报 X-E4302。

**边界。** Pin、生成器、async trait、select 和 executor 公平性由 RFC-ASYNC-01 决定；M:N 不是语言保证。

**诊断/测试/追溯。** X-W4301、X-E4302；TEST-CONC-ASYNC-001..006；来源 XLF-05-006、XLF-10-004、XLC-CORE-014..015；RFC-ASYNC-01（P3）。

### RULE-CONC-005：并发失败与清理

- maturity: EXTENDED
- status: 草案
- phase: P3

**规范性条文。** 子任务失败、panic、取消和超时必须按父任务 policy 传播或显式忽略；忽略产生 lint。任务终止不得泄漏 owner、锁、句柄或 waker。取消期间不得执行不可重入回调，除非 API 明确允许。

**解释。** 结构化并发要求可观察任务树，而不是固定调度器。runtime 可选实现但结果须等价。

**正例。** scope 中保存 join handle 并显式 join?。

**反例。** 丢弃带未处理错误的 handle 报 X-W4303；取消后使用关闭 socket 报 X-E4304。

**边界。** 进程 abort 不保证兄弟任务清理；SIGKILL、电源失败不属于可恢复保证；持久消息需幂等。

**诊断/测试/追溯。** X-W4303、X-E4304；TEST-CONC-FAIL-001..004；来源 XLF-05-001、XLF-12-012；RFC-CONC-STRUCTURED-01（P2）。

### RULE-CONC-006：happens-before、数据竞争与 Channel 状态

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 同步操作建立抽象 happens-before 边：Release→Acquire 仅在同一原子对象读到对应发布值时同步；SeqCst 还服从单一全局顺序；Relaxed 只保证该原子对象的修改顺序，不发布普通内存。无 happens-before 的冲突普通访问（至少一方写入）是数据竞争并属于禁止行为。bounded channel 满时 send 返回 Full、阻塞或响应取消；unbounded channel 仍必须受资源预算约束。close 后新 send 返回 Closed，已入队消息可被 recv 完成，队列耗尽后 recv 返回 Closed；取消返回 Cancelled，且不得丢失已明确 transfer 的 owner。

**解释。** 这些是语言级最小语义，CPU 指令、锁实现和公平性仍可不同。channel 的关闭是终态，不等同于取消；sender/receiver 的最后一个 owner 释放可触发隐式关闭，但必须在 API 中说明。

**正例。** producer 先写普通数据再对同一 `ready` 原子执行 Release store；consumer 对 `ready` 的 Acquire load 读到该发布值后才读取普通数据。Channel 的 `send` 成功与对应 `recv` 成功另行建立消息所有权的同步边，不要求额外原子 load。

**反例。** 用 Relaxed flag 发布普通指针，或 close 后继续假设 send 成功，报告 X-E4210/X-E4211。

**边界。** 跨进程、GPU、volatile 和 C/C++ 原子互操作需要 ABI 适配；模型检查和 litmus 是实现门禁，不是运行时补救。

**诊断/测试/追溯。** X-E4210、X-E4211；TEST-CONC-MODEL-001..010；来源 XLF-11-007、XLF-12-014、XLC-CORE-014；RFC-MEMMODEL-01、RFC-CONC-CHANNEL-01（P2）。

## 6. 待决 RFC 和测试矩阵

| RFC | 选择候选 | 门禁 | 最迟阶段 |
|---|---|---|---|
| RFC-MEM-BORROW-01 | 词法 lifetime/NLL/字段借用 | 别名模型、诊断、MIR soundness | P1/P2 |
| RFC-MEM-LIFE-01 | 显式 lifetime 与 HRTB 子集 | 返回引用、async/线程边界 | P2 |
| RFC-ABI-01 | C 布局+保守 provenance | ABI goldens、sanitizer、跨后端 | P2 |
| RFC-RUNTIME-ALLOC-01 | fallible alloc/OOM hook/abort | OOM、句柄耗尽、资源预算 | P2 |
| RFC-CONC-STRUCTURED-01 | scoped join/explicit detach | panic 聚合、孤儿任务、泄漏 | P2 |
| RFC-MEMMODEL-01 | C11-like/stronger abstract model | litmus、模型检查、C FFI | P2 |
| RFC-CONC-CHANNEL-01 | bounded default/explicit unbounded | 关闭、背压、取消 | P2 |
| RFC-ASYNC-01 | executor-independent Future | cancellation、blocking、I/O matrix | P3 |

每个 RULE-MEM/RULE-CONC 至少需要 pass、fail、boundary 三类测试，并在 tests/conformance、tests/memory、tests/concurrency 保留最小复现。实验实现可使用 feature gate，但不得改变默认借用、Drop 或 happens-before。
