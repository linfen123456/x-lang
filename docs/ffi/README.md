---
doc_id: DOC-FFI-INTEROP
title: X-Lang 外部函数与语言互操作规范
authority: normative
owner: role/interoperability
backup_owner: role/security-team
version: "0.2"
maturity: EXTENDED
status: 草案
phase: P3
last_reviewed: 2026-08-16
applies_to: [extern-c, x-bindgen, c-shim, python, jni, js-wasm, plugins]
traceability_scope: [XLF, XLC, XLE, SECURITY]
supersedes: [DOC-FFI-INTEROP-LEGACY]
---

# X-Lang 外部函数与语言互操作规范

## 1. 范围与安全原则

本规范先定义可审计的 C ABI 子集，再定义 C++ shim、CPython、JNI 和 JavaScript/WASM 的边界。X 类型不能因为名字相似就直接暴露给外部语言；除非布局、生命周期、线程和错误契约均被证明，否则必须使用 opaque handle 或受长度约束的 buffer。任意 C++ 模板 ABI、跨 GC 普遍零拷贝、自动异常翻译和自动生产插件加载均不在稳定承诺中。

每个 FFI 函数必须回答：谁分配、谁释放、释放函数/allocator、是否可为空、长度和所有权、线程/回调、错误表示、取消、版本和安全前置条件。

## 2. C ABI 核心规则

**C 数据模型基线。** 固定宽度整数使用 `int8_t`…`uint64_t`；计数和字节长度使用 `size_t` 并在转换前检查上限。每个指针显式标记 nullable/non-null，`ptr + len` 必须满足 `ptr == NULL ⇔ len == 0`（除非 manifest 另有声明），并验证对齐、溢出和可读/可写权限。结构体必须包含 `size` 或 `abi_version` 字段以支持扩展；字段顺序、alignment、padding 和 endianness 记录在 manifest，禁止依赖宿主 `long`/enum 大小。

### RULE-FFI-001：显式 ABI、布局与调用约定

- maturity: EXTENDED
- status: 草案
- phase: P3

**规范性条文。** 只有显式 extern C 且 repr(C) 的函数/类型进入稳定 C ABI。整数宽度、端序、对齐、padding、指针可空性、数组长度和结构版本必须在头文件及机器 manifest 中声明。extern C 函数不得让 X panic/unwind 穿越边界；调用者必须接收 XError/code 或 Result shim。

**解释。** 默认 X 布局可由编译器改变；C ABI 是受限、版本化的兼容岛。stdcall、vectorcall、系统调用约定需在目标矩阵中单独声明。

**正例。** extern "C" fn x_buffer_free(ptr:*mut u8,len:usize,allocator:u32)->XStatus。

**反例。** 直接导出 X String 或普通 struct，报告 X-E7001 unstable FFI layout。

**边界。** packed、union、bitfield、long double 和 C++ bool 的布局需平台 probe；不匹配必须拒绝生成头文件。

**诊断/测试/追溯。** X-E7001；TEST-FFI-C-001..006；来源 XLF-02-011、XLF-11-008、XLC-FFI-001、XLC-FFI-002、XLC-FFI-003、XLC-FFI-012；RFC-FFI-C-01（C ABI 子集，P3）。

### RULE-FFI-002：资源生命周期与 allocator

- maturity: EXTENDED
- status: 草案
- phase: P3

**规范性条文。** 跨边界返回的拥有资源必须配套创建方提供的 release/free 函数，或由 opaque handle 的 destroy 函数销毁。指针与长度必须成对验证，释放函数必须可识别 allocator_id；同一资源不得被两种 allocator 释放。borrowed buffer 必须标注有效调用区间，异步调用不得保存短生命周期指针。

**解释。** 句柄模式优先于裸指针。零拷贝只有在 owner、只读/可写、缓存和 lifetime 可证明时才启用。

**正例。** x_bytes_new 返回 {ptr,len,owner}，由 x_bytes_free(owner) 释放。

**反例。** X 分配的 String 交给 Python free，报告 X-E7002 allocator mismatch。

**边界。** 进程崩溃可能遗留 OS 资源；API 应提供幂等 destroy 或文档化一次性 close。共享内存/DMABUF 需安全标签。

**诊断/测试/追溯。** X-E7002；TEST-FFI-LIFE-001..005；来源 XLF-02-011、XLF-10-015、XLC-FFI-005、XLC-FFI-012；RFC-FFI-OWN-01（P3）。

### RULE-FFI-003：错误、panic、取消和回调

- maturity: EXTENDED
- status: 草案
- phase: P3

**规范性条文。** FFI 函数必须将错误映射为稳定整数/enum+可选 message handle；不得跨边界抛出异常、panic 或 longjmp。回调必须声明调用线程、重入、取消、user_data 生命周期和异常返回；异步操作必须提供 cancel/status 或声明不可取消。

**解释。** 外部异常对象的堆栈和线程局部状态不可自动安全转换。错误 message 只作诊断，不作控制逻辑。

**正例。** XResult { status: XStatus, value: XHandle, error: XErrorHandle }。

**反例。** C callback 中 panic 继续 unwinding，报告 X-E7003 foreign exception。

**边界。** 信号处理器只能调用 async-signal-safe shim；JNI/JS 回调可能只能排队到宿主线程。

**诊断/测试/追溯。** X-E7003；TEST-FFI-ERR-001..005；来源 XLF-10-003、XLF-10-015、XLF-12-014、XLC-FFI-004、XLC-FFI-008、XLC-FFI-009、XLC-FFI-010、XLC-FFI-012；RFC-FFI-ERR-01（P3）。

**回调状态机。** 异步 callback 必须可观测地经过 `Created → Registered → Invoked* → CancelRequested → Completed|Cancelled|Destroyed`。`destroy` 必须与 callback 注册同一 owner 域；并发 destroy 要么等待 in-flight callback 完成，要么原子地标记取消并保证 callback 不再访问 user_data，禁止 use-after-free。重复 cancel/destroy 必须幂等并返回已完成状态。

## 3. 语言适配契约

### C++ shim

稳定做法是生成 C-compatible shim，再由 C++ 维护 RAII/模板类型。必须锁定编译器、标准库、编译选项和 ABI；不可直接承诺 std::vector、异常或 name mangling 跨版本稳定。若 libclang 生成 wrapper，必须保存头文件 hash 和生成器版本。

### Python/CPython

适配器必须声明 Python 版本、GIL、PyObject 引用计数、Buffer protocol、异常转换和线程附着。借用 Python buffer 时 X view 不得超过 exporter；释放必须在 GIL/宿主约束内完成。numpy/tensor 零拷贝只有 stride、dtype、alignment、device 和 lifetime 全匹配时启用，否则复制并标记成本。

### Java/JNI

JNI 层必须声明 local/global/weak reference、线程 attach/detach、类加载器、异常清除和 DirectByteBuffer lifetime。native 线程不得保存短暂 JNIEnv；Java exception 必须在 JNI 返回前转换或显式 pending。GC 不得移动仍被 X 保存的裸地址，优先使用 handle/direct buffer。

### JavaScript/WASM

WASM 模块必须声明 imports/exports、线性内存、memory growth、alignment、Promise/Task、Event Loop、AbortSignal 和 SourceMap。JS string/object 不直接当 X String；转换必须验证 UTF-8/大小。异步回调只能在规定 microtask/task 队列回到宿主。

## 4. 适配矩阵与测试

| 目标 | 稳定边界 | 典型失败 | 线程/取消 | 版本门禁 |
|---|---|---|---|---|
| C | repr(C)+extern C+handle | status/allocator mismatch | 调用者声明；cancel API | libc/target ABI probe |
| C++ | C shim | STL/exception/mangling | shim owner | compiler+stdlib tuple |
| Python | PyObject/Buffer | Python exception/GIL | GIL/asyncio bridge | CPython minor + numpy |
| Java | JNI handle/direct buffer | pending exception/classloader | attach/detach | JDK/Android API |
| JS/WASM | export/import/linear memory | Promise/Abort/CORS | browser event loop | browser Tier/WPT |

测试必须包含双向调用、短生命周期、重复释放、线程并发、异常、取消、ABI mismatch、大小端/对齐、内存增长、宿主关闭和恶意长度。生成绑定为只读制品，CI 必须重生成并零差异。

## 5. 安全、性能和降级

绑定生成器默认无网络、最小文件权限和固定输入；不可信头文件、Python 包或 npm 包不得执行任意构建代码。所有长度先做上限检查，字符串和路径按宿主安全策略处理。跨界基准报告复制次数、分配、P50/P95/P99、内存峰值和版本；“零拷贝”只能作为具体测量结论。

当 ABI、布局、版本或能力不匹配时，默认拒绝加载并报告 X-E7004；若契约允许，回退到 C shim/复制/同步调用，且记录 degraded 状态。不得静默把不安全指针转换成可用对象。

## 6. 待决 RFC 与追溯

| RFC | 候选 | 门禁 | 最迟 |
|---|---|---|---|
| RFC-FFI-C-01 | C ABI 最小稳定集 | ABI golden、头文件、Sanitizer | P3 |
| RFC-FFI-OWN-01 | handle/borrowed buffer 所有权图 | 泄漏、double-free、异步回调 | P3 |
| RFC-FFI-ERR-01 | status+error handle / Result shim | 异常、panic、取消 | P3 |
| RFC-FFI-PY-01 | Buffer 与 GIL 边界 | CPython/numpy 版本和泄漏 | P4 |
| RFC-FFI-JNI-01 | direct buffer 与线程附着 | JDK/Android 真机、GC | P4 |
| RFC-FFI-JS-01 | WASM Promise/Abort/SourceMap | 浏览器 WPT、内存增长 | P4 |

规则来源为 XLF-02-011、XLF-10-003、XLF-10-014、XLF-10-015、XLF-11-008、XLF-11-009、XLF-12-014 和对标大纲中的 XLC-FFI 系列；工程落点为 tools/x-bindgen、sdk、tests/interoperability。失败时回滚绑定版本或切换 shim，不改变核心语言类型。
