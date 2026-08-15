---
doc_id: DOC-GUIDE-OWNERSHIP-ERRORS-CONCURRENCY
title: X-Lang 所有权、错误与并发教程
authority: implementation
owner: role/docs-team
backup_owner: role/runtime-team
version: "0.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
applies_to: [learner, borrow-checker, runtime]
traceability_scope: [XLF]
supersedes: []
---

# X-Lang 所有权、错误与并发教程

## 1. 为什么把三者放在一起

原始材料要求以所有权、借用和生命周期在编译期避免悬垂引用与数据竞争，以 RAII 处理资源，并以协程/CSP/Channel 提供并发。错误返回、panic、任务取消都会改变控制流，因此必须共同说明资源在成功、失败和并发退出时如何释放。

> 当前状态：所有权 + RAII 是 CORE 方向；作用域线程为 CORE/EXTENDED 分阶段能力；Channel、Future、`async/await` 为 EXTENDED 且待 RFC。示例是规范目标，不表示运行时已实现。可选 GC 属于隔离实验，不改变本教程默认无 GC 模型。

先决条件：[核心语言教程](./core-language-tutorial.md)。规则依据：[内存与并发规范](../specs/memory-concurrency.md)。

## 2. 从移动理解所有权

每个非 Copy 值有一个有效所有者。赋值、按值传参或按值返回可以移动它：

```x
fn consume(data: Bytes) -> usize {
    data.len()
}

fn main() {
    let packet = Bytes::from([1, 2, 3]);
    let size = consume(packet);
    println(packet.len()); // 错误：packet 已移动
}
```

编译器应指出移动发生在 `consume(packet)`，使用发生在下一行。它不能偷偷深拷贝以让程序通过。若调用者仍需访问，应借用：

```x
fn measure(data: &Bytes) -> usize {
    data.len()
}

fn main() {
    let packet = Bytes::from([1, 2, 3]);
    let size = measure(&packet);
    println(packet.len()); // 合法
}
```

是否 Copy 由类型规则决定，不能从“值看起来很小”猜测。部分移动、字段级 Place 和 Drop 类型限制见 RULE-MEM-001/004。

## 3. 借用排他性

同一访问期间允许多个只读借用，或一个可变借用，但不能两者重叠：

```x
fn main() {
    let mut values = Vec::new();
    values.push(1);

    let first = &values[0];
    values.push(2);          // 错误：可能重分配，且 first 仍存活
    println(first);
}
```

安全改写是缩短借用：

```x
fn append_after_copy(values: &mut Vec<i32>) {
    let first_value = values[0];
    values.push(2);
    println(first_value);
}
```

如果元素不是 Copy，可用显式作用域结束借用，或重新设计 API。借用检查器不应靠运行时自动插锁解决单线程别名冲突。

### 3.1 生命周期约束而非手工释放

```x
fn bad_ref() -> &i32 {
    let local = 42;
    &local // 错误：返回引用超过 local 生命周期
}
```

生命周期描述引用有效范围，不是“延长对象生命”的指令。合法的返回引用必须来自调用者提供的输入或具有足够长生命周期的存储：

```x
fn first<'a>(values: &'a [i32]) -> &'a i32 {
    &values[0]
}
```

生命周期省略和非词法生命周期仍待 RFC 完整冻结；教学重点是输出引用不能比来源活得更久。

## 4. RAII、Drop 与失败路径

资源封装对象在作用域退出时执行 Drop。正常返回、`Result` 提前返回和允许展开的 panic 都必须沿已初始化对象的逆序清理；abort 不保证全局清理。

```x
fn write_report(path: &Path) -> Result<(), IoError> {
    let file = File::create(path)?;
    let buffer = Buffer::new();
    file.write_all(buffer.bytes())?;
    Ok(())
} // buffer 后创建，先 Drop；随后 file
```

不能依靠 Drop 完成必须对外确认的操作，例如事务提交或持久写入；这些应显式返回 `Result`。Drop 中再次 panic 会触发运行时的二次失败策略。

原始 `10.txt` 提出的 `defer` 已追踪为 XLF-10-002，但与 RAII、return、panic 的精确交互仍为 EXPERIMENTAL。当前稳定教程优先使用资源类型，不把 `defer` 当既定 CORE。

## 5. 可恢复错误与不可恢复失败

### 5.1 给错误增加上下文

```x
fn read_user(path: &Path) -> Result<User, UserLoadError> {
    let text = file::read_to_string(path)
        .map_err(|source| UserLoadError::Read { path: path, source: source })?;
    parse_user(text)
        .map_err(|source| UserLoadError::Parse { path: path, source: source })
}
```

错误链来自 XLF-10-001。默认是否捕获 Backtrace、何时分配内存和如何脱敏仍由标准库/运行时规范决定；程序不应为了日志而泄露密钥或用户数据。

### 5.2 panic 策略矩阵

| 路径 | 已初始化局部 Drop | 调用者可恢复 | 适用 |
|---|---|---|---|
| `Err` 返回 | 是 | 是 | 业务/环境失败 |
| panic + unwind | 是，直到捕获边界 | 仅批准边界 | 违反不变量、测试 |
| panic + abort | 不保证全局清理 | 否 | 体积/安全策略要求 |
| `no_exceptions` Profile | 由 RFC 定义，不能出现隐藏 unwind | 通过 Result | 受限平台/ABI |

`x.toml` 中 panic Profile 来自 XLF-10-003/XLF-12-014。禁止让同一公共 ABI 在不声明的情况下因 Profile 切换而改变展开行为。

## 6. 在线程间移动所有权

作用域线程的目标形态：

```x
fn analyze_records() -> Result<(), LoadError> {
    let records = load_records()?;

    thread::scope(|scope| {
        let (left, right) = records.split_at(100);
        scope.spawn(move || analyze(left));
        scope.spawn(move || analyze(right));
    });
    Ok(())
}
```

作用域结束前必须 join 子线程，因此借用不能逃逸。跨线程移动的类型必须满足 Send 类能力，共享引用还要求 Sync 类能力。以下应失败：

```x
fn invalid_share() {
    let local = Rc::new(State::new());
    thread::spawn(move || use_state(local)); // Rc 不是跨线程共享容器
}
```

可选替代是经评审后使用 `Arc` 加同步原语；`Arc` 不会自动让内部可变数据无竞争。

## 7. Channel 与结构化并发

原始材料偏好 CSP/Channel 以减少共享内存锁竞争，但这不意味着 Channel 自动消除死锁或无限排队。目标 API 示例：

```x
fn exchange() -> Result<(), ChannelError> {
    let pair: (Sender<Message>, Receiver<Message>) = channel::bounded(64);
    let (sender, receiver) = pair;

    thread::scope(|scope| {
        scope.spawn(move || {
            sender.send(Message::Stop)?;
            Ok(())
        });

        match receiver.recv()? {
            Message::Stop => {},
            Message::Data(value) => process(value)?,
        }
        Ok(())
    })
}
```

必须定义：容量是否为零、队列满时阻塞/异步等待、发送端全部关闭后的接收结果、接收端关闭后的发送结果、公平性、取消与消息析构。完整状态机在 RULE-CONC-003/006 的 RFC 中冻结。

边界练习：删除接收方，发送不得永久静默阻塞；删除所有发送方，接收必须得到关闭结果；任务失败时队列中消息仍须按所有权规则析构。

## 8. async/await 与取消是扩展能力

目标形态：

```x
async fn fetch(url: &Url, cancel: &CancelToken) -> Result<Bytes, NetError> {
    let response = http::get(url, cancel).await?;
    response.body(cancel).await
}
```

Future 在 `.await` 间保存状态。取消不是任意位置强杀线程：调用方发出请求，Future 在定义的取消点观察它；被 Drop 的 Future 必须释放自身资源，但远端操作是否已完成需由 I/O 契约说明。

反例：持有非异步锁跨 `.await`，既可能阻塞执行器又可能死锁，应由 lint 或类型规则诊断。异步函数、Stream/Generator 和背压分别追溯 XLF-01-009、XLF-10-009，均不阻塞 P0/P1 同步主线。

## 9. 综合案例：有界工作队列

设计要求：最多 32 个待处理作业；任何 worker 失败都通知父作用域；关闭输入后排空或明确取消；不丢失资源所有权。

```x
fn run_jobs(jobs: Vec<Job>) -> Result<Vec<Output>, JobError> {
    let pair: (Sender<Job>, Receiver<Job>) = channel::bounded(32);
    let (tx, rx) = pair;

    thread::scope(|scope| {
        let worker = scope.spawn(move || {
            let mut outputs = Vec::new();
            loop {
                match rx.recv()? {
                    Some(job) => outputs.push(process(job)?),
                    None => { break; },
                }
            }
            Ok(outputs)
        });

        for job in jobs {
            tx.send(job)?;
        }
        drop(tx); // 显式关闭最后一个发送端
        worker.join()?
    })
}
```

这是接口目标，不是已实现 API；代码刻意使用当前 EBNF 已定义的 `loop + match`，而未使用尚待模式 RFC 确认的 `while let`。示例的价值是揭示所有权路径和关闭协议，而非暗示运行时已经完成。

## 10. 常见错误、练习和检查点

常见错误：移动后使用；返回局部引用；同时保留可变与不可变借用；用 Drop 隐藏可失败提交；跨线程移动非 Send 值；认为 `Arc` 等于无锁；无界 Channel 没有资源预算；把取消等同强制终止；在 abort 模式承诺全部清理。

练习：

1. 修复“借用 Vec 元素后 push”的反例，并说明为何安全。
2. 为文件解析函数设计 `Result` 错误枚举，保留路径与源错误但不记录文件内容。
3. 画出 bounded Channel 的 Open、SenderClosed、ReceiverClosed、Drained 状态及每个操作结果。
4. 把共享计数器分别设计为消息聚合和 `Arc<Atomic>`；比较所需内存顺序，不直接宣称谁更快。
5. 为异步下载写取消测试：取消前、I/O 等待中、完成同时取消、Future Drop 四个边界。

检查点：能准确判断值的所有者和借用范围；能说明 Result/unwind/abort 的清理差异；能区分线程安全静态规则与运行时同步；能识别 Channel/async 尚待 RFC 的具体决策。

## 11. 来源与测试映射

- 原始来源：`1.txt` 的所有权、无 GC、协程/CSP；`2.txt` 的 RAII/可选 GC 设想；`5.txt` 的 spawn、Send、M:N、共享内存和分配器；`10.txt` 的错误链、defer、panic 策略、Stream 与弱引用；`11.txt` 的低级并发原语。
- 追溯：XLF-01-006、XLF-01-007、XLF-01-009、XLF-02-010、XLF-05-001、XLF-05-002、XLF-10-001～003、XLF-10-009～011、XLF-11-012、XLF-12-014。
- planned：TEST-MEM-MOVE/BORROW/LIFE/DROP、TEST-CONC-THREAD/SYNC/MODEL/ASYNC/FAIL 系列；目前是未来符合性目标，不是已执行证据。
