---
doc_id: DOC-STDLIB-CORE-API
title: X-Lang core 与 alloc 核心 API 签名规范
authority: normative
owner: role/standard-library
backup_owner: role/compiler-team
version: "0.2.0"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
applies_to: [x-core, x-alloc, no-std, core-conformance]
traceability_scope: [XLF, XLC, XLE]
supersedes: [DOC-STDLIB-CORE-API-LEGACY]
---

# X-Lang core 与 alloc 核心 API 签名规范

本文给出不依赖操作系统的核心 API 初稿。签名是候选公共接口；标为待决的错误/布局选择须经过 API RFC 后稳定。core 可在 no_std/no_alloc 目标使用，alloc 需要全局 allocator。

## RULE-STD-010：Option 与 Result

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** Option<T> 只表示值缺失，Result<T,E> 表示可恢复失败；二者不可隐式互转。核心提供：

~~~x
enum Option<T> { Some(T), None }
impl<T> Option<T> {
  fn is_some(&self) -> bool
  fn as_ref<'a>(&'a self) -> Option<&'a T>
  fn map<U>(self, f: fn(T)->U) -> Option<U>
  fn and_then<U>(self, f: fn(T)->Option<U>) -> Option<U>
  fn unwrap_or(self, default: T) -> T
}
enum Result<T,E> { Ok(T), Err(E) }
impl<T,E> Result<T,E> {
  fn map<U>(self, f: fn(T)->U) -> Result<U,E>
  fn map_err<F>(self, f: fn(E)->F) -> Result<T,F>
  fn and_then<U>(self, f: fn(T)->Result<U,E>) -> Result<U,E>
  fn unwrap_or(self, default: T) -> T
}
~~~

**解释。** map 不改变失败/缺失，and_then 组合失败操作；unwrap_or 必须显式默认。unwrap/expect 可在 std 作为 panic API，但不得用于普通输入。

**正例。** first(xs).map(|x| x+1).unwrap_or(0)。

**反例。** 用 -1 表示缺失或把 Err 静默转 Ok，报告 X-E6010。

**边界。** T/E 的 Send/Sync 按字段推导；Option<&T> 不延长 lifetime；Result Drop 只析构构造的 variant。

**诊断/测试/追溯。** X-E6010；TEST-STD-CORE-001..004；来源 XLF-09-001、XLF-09-002、XLF-10-001、XLC-CORE-005；RFC-STD-API-01（P2）。

## RULE-STD-011：Vec、Slice 与迭代器

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** Vec<T> 拥有连续初始化元素和 capacity；核心签名：

~~~x
struct Vec<T> { /* representation is private */ }
impl<T> Vec<T> {
  fn new() -> Vec<T>
  fn try_with_capacity(n: usize) -> Result<Vec<T>, AllocError>
  fn len(&self) -> usize
  fn capacity(&self) -> usize
  fn get<'a>(&'a self, i: usize) -> Option<&'a T>
  fn get_mut<'a>(&'a mut self, i: usize) -> Option<&'a mut T>
  fn push(&mut self, value: T) -> Result<(), AllocError>
  fn pop(&mut self) -> Option<T>
  fn iter<'a>(&'a self) -> Iter<'a,T>
}
struct Slice<T> { /* fat reference */ }
trait Iterator { type Item; fn next(&mut self) -> Option<Self::Item>; }
~~~

**解释。** push 摊销 O(1)，扩容 O(n) 且可能分配；get O(1)，iter next 摊销 O(1)。实现可采用增长因子，但不得暴露 capacity 以外布局。

**正例。** v.get(i) 处理越界并保留引用 lifetime；迭代器用 while let Some。

**反例。** 保存 push 前引用并在可能扩容后使用，报告 X-E6011 invalidated collection borrow。

**边界。** push 失败时 Vec 和已有元素保持原状态；OOM policy 由 allocator profile 决定。Vec 非 Sync；T: Send 时可 move 跨线程。

**诊断/测试/追溯。** X-E6011；TEST-STD-VEC-001..006；来源 XLF-09-001、XLF-12-003、XLC-CORE-010；RFC-STD-VEC-01（P2）。

## RULE-STD-012：String、Bytes 与 Unicode

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** String 始终保存合法 UTF-8；Bytes 保存任意 u8。核心签名：

~~~x
struct String { /* UTF-8 invariant */ }
impl String {
  fn new() -> String
  fn from_utf8(bytes: Vec<u8>) -> Result<String, Utf8Error>
  fn as_str<'a>(&'a self) -> &'a str
  fn try_push_str(&mut self, s: &str) -> Result<(), AllocError>
  fn len_bytes(&self) -> usize
}
fn utf8_validate(bytes: &[u8]) -> Result<(), Utf8Error>
~~~

**解释。** len_bytes 是字节长度，不是 grapheme 数；按 scalar/grapheme 索引需 text API。切片不得落在 code point 中间。

**正例。** String::from_utf8(raw)?；使用 chars() 迭代 Unicode scalar。

**反例。** 任意 Bytes 直接转 String 或按 byte 截断 emoji，报告 X-E6012。

**边界。** Unicode 版本、NFC/NFKC、大小写和 grapheme 由 x-text/ICU 官方包决定；String 不承诺语言排序。

**诊断/测试/追溯。** X-E6012；TEST-STD-TEXT-001..006；来源 XLF-09-002、XLE-DATA-004、XLC-CORE-010；RFC-STD-TEXT-01（P3）。

## RULE-STD-013：Box、Rc、Arc 与 Weak

- maturity: EXTENDED
- status: 草案
- phase: P3

**规范性条文。** Box<T> 的独占所有权属于 CORE alloc；Rc<T>/Weak<T> 与 Arc<T>/Weak<T> 属 EXTENDED/P3。Rc 仅单线程；Arc 用原子计数并可跨线程但 T 必须 Send+Sync。Weak::upgrade 返回 Option，不能返回悬垂值。循环结构必须用 Weak 断开。共享指针在 RFC-STD-PTR-01 通过前不进入稳定 Prelude，也不作为核心语言实现的前置依赖。

**解释。** 引用计数不是 GC；循环 Rc 泄漏是资源语义而非 use-after-free。Arc 不保证实时无锁。

**正例。** let child=Arc::new(Node::new()); let weak=Arc::downgrade(&child); weak.upgrade()。

**反例。** Rc 在 spawn 中捕获报告 X-E6013；直接解引用 Weak 报 X-E6014。

**边界。** count 溢出、allocator 失败、析构递归和 FFI 句柄需 runtime 约束；内存序属于 RULE-CONC-002。

**诊断/测试/追溯。** X-E6013、X-E6014；TEST-STD-PTR-001..005；来源 XLF-10-005、XLF-05-001、XLC-CORE-014；RFC-STD-PTR-01（P3）。

**所有权闭合。** `Box<T>` 是唯一 owner，drop 释放其 allocator 记录的对象；`Rc<T>` 维护非原子 strong/weak 计数，只能在单线程使用；`Arc::clone` 只增加 strong count 并返回同一对象的共享 owner，最后一个 strong owner 执行 T 的 Drop，最后一个 weak count 释放控制块；`Weak::upgrade` 在 strong count 为零时返回 None。`Arc<T>` 跨线程要求 T: Send + Sync，Weak 只延长控制块而不保持 T 存活。迭代器必须携带与来源 borrow 相同或更短的 lifetime，集合变更导致失效时 API 必须拒绝或明确返回 owned snapshot。

## RULE-STD-014：核心错误和 panic

- maturity: CORE
- status: 草案
- phase: P2

**规范性条文。** core 错误类型必须是可匹配 enum/结构，不含环境文本作为稳定 key。AllocError、Utf8Error、BoundsError 和 InvariantError 至少提供 kind、source/context（可选）和 Debug 展示。panic/abort 只用于违反前置条件、不可恢复不变量或 profile 明确 OOM。

**解释。** 库不应把用户输入错误转成 panic；backtrace 可选、默认脱敏和可关闭。

**正例。** Vec::try_with_capacity 返回 AllocError；slice.get 返回 None。

**反例。** 文件解析未知字段直接 panic，报告 X-W6015。

**边界。** no_std 可没有格式化/backtrace；错误仍有稳定 discriminant。跨 FFI 必须转 code/handle。

**诊断/测试/追溯。** X-W6015；TEST-STD-ERROR-001..004；来源 XLF-10-001、XLF-12-012、XLC-CORE-010；RFC-ERROR-01（P1）。

## 6. API 契约样例和平台矩阵

| API | 时间/空间复杂度 | 分配/线程安全 | 错误/取消 | 平台 |
|---|---|---|---|---|
| Vec::get | O(1)/O(1) | 不分配；共享只读 | None，不取消 | 全部 |
| Vec::push | 摊销 O(1)/O(1) | 满容量可能分配；Vec 非 Sync | AllocError，不部分插入 | 全部 |
| String::from_utf8 | O(n)/O(n) | 复用或取得 Bytes；Send 条件 | Utf8Error | 全部 |
| Arc::clone | O(1)/O(1) | 原子计数；T: Send+Sync | 计数溢出策略待决 | 全部 |
| Iterator::next | 摊销 O(1)/O(1) | 按迭代器 | None/终止 | 全部 |

core/alloc 在 Windows、Linux、macOS、WASM/WASI 的类型语义一致；allocator、异常终止、最大地址空间由 target/profile 公开。core 不提供隐式 GC、网络、文件、线程或 OS 句柄。

## 7. 待决 RFC、回滚和测试

| RFC | 候选 | 门禁 | 最迟 |
|---|---|---|---|
| RFC-STD-VEC-01 | capacity 增长实现自由/可观察 | API diff、引用失效测试 | P2 |
| RFC-STD-TEXT-01 | Unicode 版本与 grapheme | Unicode conformance、迁移 | P3 |
| RFC-STD-PTR-01 | Cell/RefCell 内部可变性 | 动态借用、Send/Sync | P3 |
| RFC-STD-API-01 | error machine kind/文案 | 稳定 JSON、跨版本 | P2 |

tests/stdlib/core 必须包含属性、fuzz、OOM 注入、UTF-8 边界、计数并发和 doc-test。失败应回滚旧签名/实现或 feature gate；禁止删除失败测试。
