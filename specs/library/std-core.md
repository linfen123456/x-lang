# 标准库最小契约（core / alloc / std）

> 类型：Spec｜唯一负责：标准库分层、各模块最小 API 与阶段、集合与文本契约、I/O/进程/时间契约。语言规则见 [specs/language](../language/01-lexical-syntax.md)。

## 1. 结论

1. 分层：`core`（不分配、不依赖 OS）→ `alloc`（需要分配器）→ `std`（需要 OS）。下层不得依赖上层，`no_std` 包只能使用 `core` 和 `alloc`。
2. 标准库用 X 编写，通过编译器 intrinsic 调用 xrt/PAL（intrinsic 清单见 [compiler](../../docs/design/compiler.md) §7）。
3. 下文的 API 签名用于说明契约，不是可编译源码；签名中省略了函数体。
4. 可能失败的操作返回 `Result`；属于编程错误的情况（越界、溢出）触发 panic；分配类 API 另外提供 `try_*` 版本。

## 2. `core`

| 模块 | API（阶段） |
|---|---|
| 原语方法 | 整数：`checked_*`、`wrapping_*`、`saturating_*`、`overflowing_*`、`pow`、`abs`、`min`、`max`、`to_string`（alloc）、`T::try_from`、`T::wrapping_from`、`T::MIN`、`T::MAX`（P1）；浮点：`sqrt`、`abs`、`floor`、`ceil`、`round`、`is_nan`、`total_cmp`、`to_i64_checked`、`round_to_f32`（P1）；`char`：`is_alphabetic`、`to_digit`、`len_utf8`（P1） |
| `option` / `result` | `Option<T>`：`is_some`、`unwrap_or`、`unwrap_or_panic`、`map`（P2，需要闭包）、`ok_or`、`as_ref`；`Result<T, E>`：`is_ok`、`ok`、`unwrap_or_panic`、`map`、`map_error`（P2）、`expect(msg)`（P1） |
| `cmp` | `Ordering { Less, Equal, Greater }`、`min`、`max`（P1） |
| `iter` | `Iterator`、`IntoIterator`、`range(a, b)`、`range_inclusive(a, b)`（P1）；适配器 `map`、`filter`、`enumerate`、`zip`、`take`、`skip`、`rev`；消费者 `count`、`sum`（`Sum` Trait）、`fold`、`any`、`all`、`find`、`collect`（`FromIterator`）（P2） |
| `slice` | `len`、`is_empty`、`get -> Option<&T>`、`get_mut`、`iter`、`iter_mut`、`first`、`last`、`split_at`、`split_at_mut`、`contains`、`starts_with`（P1）；`sort`（稳定排序）、`sort_unstable`、`binary_search`（P2） |
| `str` | `len`（字节数）、`is_empty`、`chars`、`bytes`、`lines`、`split(&str)`、`split_whitespace`、`trim`、`starts_with`、`ends_with`、`contains`、`find -> Option<usize>`、`parse::<T>() -> Result<T, ParseError>`、`as_bytes`（P1） |
| `mem` | `size_of`、`align_of`、`drop`、`forget`、`replace`、`swap`、`take`（P1）；`MaybeUninit`、`transmute`（unsafe，P2） |
| `ptr` | `null`、`null_mut`、`with_addr`、`read`/`write`（unsafe）、`NonNull<T>`（P1–P2） |
| `fmt` | `Display`、`Debug`、`Formatter`、`FmtError`（P1） |
| `hint` | `likely(b)`、`unlikely(b)`、`black_box`（P2）；它们不改变语义 |
| `sync::atomic` | 见 [08](../language/08-concurrency.md) §6（P2） |

## 3. `alloc`

| 类型 | 契约（阶段） |
|---|---|
| `Box<T>` | 独占堆所有权；`Box::new`、`*b`；支持 `Box<str>`、`Box<[T]>`（P1） |
| `Vec<T>` | 保证 `len <= capacity`；方法 `new`、`with_capacity`、`push`、`pop`、`len`、`get`、`insert`、`remove`、`clear`、`extend_from_slice`、`as_slice`、`try_reserve -> Result<(), AllocError>`；`v[i]` 越界即 panic（P1） |
| `String` | 内容始终是合法 UTF-8；方法 `new`、`from(&str)`、`push`、`push_str`、`len`、`as_str`、`clear`、`with_capacity`（P1） |
| `Rc<T>` / `Weak<T>` | 单线程引用计数，不是 Send/Sync（P1） |
| `Arc<T>` | 原子引用计数（P2） |
| `Cell<T>` / `RefCell<T>` | 内部可变性；`RefCell` 借用冲突时 panic（P2） |
| `BTreeMap<K, V>` / `BTreeSet<T>` | 要求 `K: Ord`；按键顺序遍历；操作为对数复杂度（P2） |
| `VecDeque<T>` | 环形缓冲区（P2） |

## 4. `std`

| 模块 | API（阶段） |
|---|---|
| prelude 打印 | `print<T: Display>(v: T)`、`println`、`eprint`、`eprintln`（P0 只接受字面量 `&str`；P1 起为泛型版本） |
| `collections` | `HashMap<K, V>`、`HashSet<T>`（要求 `K: Hash + Eq`）（P1） |
| `io` | `stdin()`、`stdout()`、`stderr()`；`Read`/`Write` Trait；`BufReader::lines`；`IoError { kind: IoErrorKind, … }`（P1） |
| `fs` | `read_to_string`、`read`、`write`、`File::open`、`File::create`、`metadata`、`create_dir_all`、`remove_file`、`read_dir`（P1）；`rename`（同一卷上保证原子）、文件锁（P3） |
| `env` | `args() -> Args`（第 0 项是程序名）、`var(name) -> Result<String, VarError>`、`current_dir`（P1） |
| `process` | `exit(code: i32) -> never`（P0 由编译器桩提供，P1 起由 std 提供）；`Command`（`arg`、`env`、`current_dir`、`status`、`output`、`spawn`）（P2） |
| `time` | `Instant`（单调时钟）、`Duration`（P1）；`SystemTime`（P2） |
| `path` | `Path`、`PathBuf`（与平台无关的规范化）（P2） |
| `thread` / `sync` | 见 [08](../language/08-concurrency.md)（P2） |
| `guard` | `on_exit(f) -> Guard`、`Guard::dismiss`（P2），用于替代 `defer` |
| `ffi` | `CStr`、`CString`、`OsStr`、`OsString`（P2） |
| `os::{linux, windows, macos}` | 平台扩展：信号、`sendfile`、亲和性、Direct I/O（P3） |
| `net` | `TcpListener`、`TcpStream`、`UdpSocket`（阻塞式）（P3）。HTTP 等协议由生态包提供 |

## 5. 集合与文本契约（原 RFC-0009）

1. **HashMap**
   - 平均 O(1)，不承诺具体算法。
   - 默认哈希种子在每个进程中随机生成，用于抵御 HashDoS。
   - **遍历顺序不作规定**，不得用于序列化、签名、快照或构建键。
   - 不提供全局替换默认 HashMap 实现的开关。
2. **BTreeMap**：按键顺序遍历；适合需要确定顺序的输出。
3. **借用**
   - `get -> Option<&V>`、`get_mut -> Option<&mut V>`、`remove -> Option<V>`，缺键时返回 `None`，不 panic。
   - 存在活跃迭代器时，不能做结构性修改（由借用检查器保证）。
4. **容量**：容量计算溢出时，在分配之前就失败。处理不可信输入的批量 API 必须接受大小上限参数。
5. **字面量**：1.0 没有 Map 字面量。
6. **文本**
   - `str` 和 `String` 始终是合法 UTF-8；`&s[a..b]` 形式的切片在 1.0 中不存在（没有范围运算符），改用 `s.slice(a, b) -> Option<&str>`（按字节，不落在字符边界时返回 `None`）。
   - 字节数据使用 `[u8]` 和 `Vec<u8>`。

## 6. I/O 与平台契约

- 所有 I/O 都返回 `Result<_, IoError>`。`IoErrorKind` 是跨平台枚举（`NotFound`、`PermissionDenied`、`AlreadyExists`、`Interrupted`、`InvalidData`、`UnexpectedEof`、`Other` 等），平台原始错误码通过 `raw_os_error()` 获取。
- `stdout` 连接终端时按行缓冲，否则按块缓冲；进程正常退出时刷新缓冲。`process::exit` 也会刷新 `stdout`。
- 路径：Windows 上与 UTF-16 之间无损往返，通过 `OsString` 实现。
- `env::args()` 遇到非 UTF-8 参数时 panic，并在消息中提示改用 `args_os()`（P2）。

## 7. 错误与 panic 对照

| 情形 | 行为 |
|---|---|
| `v[i]` 越界 | panic |
| `v.get(i)` 越界 | 返回 `None` |
| `s.parse::<i32>()` 失败 | 返回 `Err(ParseError)` |
| 分配失败 | abort；`try_reserve` 返回 `Err(AllocError)` |
| `RefCell` 借用冲突 | panic |
