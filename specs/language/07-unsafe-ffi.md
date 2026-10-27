# 07 unsafe、原始指针、未定义行为与 FFI

> 类型：Spec｜唯一负责：unsafe 上下文与操作、UB 清单、原始指针、布局 `@repr`、C FFI（导入/导出/链接/回调）。

## 1. 结论

1. Safe 代码不会产生 UB。UB 只可能出现在 `unsafe` 块或 `unsafe fn` 中。写 unsafe 代码的人负责维持 §3 的不变量。
2. 1.0 的 FFI **只支持 C ABI**。C++、Python、JVM、Node 互操作都建立在 C ABI 之上，由生态工具（`x-bindgen` 等）提供。
3. panic 不得跨越 FFI 边界，边界处直接 abort。

## 2. unsafe 上下文与操作 [RULE-UNSAFE-CONTEXT]

下面 5 种操作**只能**出现在 `unsafe { }` 块或 `unsafe fn` 体内，否则报 `X-E6001`：
1. 解引用原始指针 `*p`；
2. 调用 `unsafe fn`，包括所有 extern 函数；
3. 实现 `unsafe trait`（`unsafe impl Send for T {}`）；
4. 调用 `core::ptr` 和 `core::mem` 中标为 unsafe 的函数，如 `ptr::read`、`mem::transmute`；
5. 访问 `@repr(C)` 联合体式布局（1.0 没有 `union`，通过 `core::mem` API 进行）。

不必要的 `unsafe` 块产生 `X-W0004`。每个 `unsafe` 块**应**带一条 `// SAFETY:` 注释，说明为何满足不变量；lint 在 P2 检查这一点。

## 3. 未定义行为清单（1.0）

以下情况是 UB。MIR 解释器在 P2 起能检测其中带 ✔ 标记的项：

| # | UB | 解释器可检测 |
|---|---|---|
| 1 | 解引用空指针、悬垂指针或未对齐指针 | ✔ |
| 2 | 越界读写（超出分配） | ✔ |
| 3 | 读取未初始化内存（作为非 `MaybeUninit` 类型） | ✔ |
| 4 | 违反别名规则：存在 `&mut T` 时经其他路径访问同一内存；或经 `&T` 写入（`Cell` 等除外） | ✔（保守模型） |
| 5 | 数据竞争（定义见 [08](08-concurrency.md) §6） | 部分（TSan） |
| 6 | 产生非法值：`bool` 不是 0/1、`char` 不是标量值、枚举判别值非法、`&T` 为空 | ✔ |
| 7 | 用错误的 ABI 或签名调用函数 | 否 |
| 8 | 外部代码的展开（如 C++ 异常、`longjmp`）穿越 X 栈帧 | 否 |
| 9 | 指针运算越出所属分配（超出末尾后一个位置） | ✔ |

指针来源（provenance）：
- 每个指针都携带它所属分配的来源信息。
- 整数转指针必须经过 `core::ptr::with_addr(base, addr)`（继承 `base` 的来源），或 `core::ptr::from_exposed_addr(addr)`（unsafe，只能找回此前已暴露的来源）。
- 完整的形式化模型在 P2 末随 UB 检测器一起冻结。

## 4. 原始指针

- 写作 `*const T`、`*mut T`，可以为空，不受借用检查约束。
- 由引用得到：`&x as *const T`。空指针：`core::ptr::null()`、`null_mut()`。
- 指针运算：`p.add(n)`、`p.offset(n)`，均为 unsafe，以元素为单位。
- 原始指针既不是 `Send` 也不是 `Sync`。

## 5. 布局 `@repr` [RULE-FFI-REPR]

| 属性 | 适用于 | 语义 |
|---|---|---|
| `@repr(C)` | struct | 字段按声明顺序排列，按目标 C ABI 规则填充和对齐 |
| `@repr(C)` | 无载荷 enum | 与 C `int` 同宽 |
| `@repr(u8)` 等 | 无载荷 enum | 判别值使用指定整数类型 |
| `@repr(transparent)` | 只有一个非零大小字段的 struct | 与该字段布局相同 |

在其他位置使用 `@repr` 报 `X-E6004`。

## 6. 调用 C（导入）[RULE-FFI-TYPE]

```x
@link(name = "m")
extern "C" {
    unsafe fn cos(x: f64) -> f64;
}

pub fn cosine(x: f64) -> f64 { unsafe { cos(x) } }
```

FFI 安全类型如下。其他类型出现在 extern 签名中报 `X-E6002`：

| X 类型 | C 类型 |
|---|---|
| `i8…i64`、`u8…u64` | `int8_t…uint64_t` |
| `isize`、`usize` | `intptr_t`、`size_t` |
| `f32`、`f64` | `float`、`double` |
| `bool` | `_Bool` |
| `()`（仅作返回类型） | `void` |
| `*const T`、`*mut T`（`T` 为 FFI 安全类型或 `()`） | 指针 |
| `@repr(C)` struct/enum | struct/enum |
| `extern "C" fn(...) -> R` | 函数指针 |
| `Option<extern "C" fn(...)>`、`Option<&T>` | 可空指针 |

C 字符串使用 `std::ffi::CStr` 和 `CString`（P2）。

## 7. 被 C 调用（导出）[RULE-FFI-EXPORT]

```x
@export("x_add")
pub extern "C" fn add(a: i32, b: i32) -> i32 { a + b }
```

- `extern "C"` 决定调用约定，`@export("sym")` 决定导出的符号名。导出函数两者都必须写，这是唯一的写法。
- `@export` 用在非 `extern "C"` 函数上，或符号名重复，报 `X-E6003`。
- 导出函数内部发生 panic 时，直接 abort。

## 8. 链接

- `@link(name, kind)` 写在 extern 块上。另外，`x.toml [target.<triple>.link]` 可以按目标追加库搜索路径（见[包规范](../packages/manifest-lock-build.md) §3）。
- 默认链接方式：Linux/macOS 用系统 C 编译器驱动（`cc`）链接；Windows 用 `link.exe` 或 `lld-link`。P3 评估是否随工具链附带 lld。

## 9. 规则与诊断

| Rule ID | 诊断 |
|---|---|
| RULE-UNSAFE-CONTEXT | X-E6001 |
| RULE-FFI-TYPE | X-E6002 |
| RULE-FFI-EXPORT | X-E6003 |
| RULE-FFI-REPR | X-E6004 |
| LINT-UNUSED-UNSAFE | X-W0004 |
