---
doc_id: SPEC-FFI
title: X-Lang 外部函数与语言互操作契约
status: draft
maturity: EXTENDED
owner: interoperability
trace: [XLF-01-013, XLF-10-014, XLF-11-009, XLC-FFI-001..012]
---

# X-Lang FFI 与互操作契约

## 目标与非目标

先稳定 C ABI，再为 C++、Python、Java/JNI、JavaScript/WASM 提供有边界的绑定。目标是可审计的资源、错误、线程和版本契约；不承诺任意 C++ 模板 ABI、任意对象自动零拷贝或跨 GC 普遍互转。

## 公共契约

`extern "C"` 接口必须声明布局、对齐、调用约定、所有权、释放函数、错误码和线程要求。跨边界对象默认句柄或受长度约束的 buffer；异常/panic 不得越过边界，调用者必须显式转换为 `Result`/错误码。

| 目标 | 必须定义 | 测试 |
|---|---|---|
| C | ABI、头文件、布局、allocator | `tests/interoperability/c` |
| C++ | C Shim、名称修饰限制、STL 边界 | `.../cpp-shim` |
| Python | GIL、引用计数、Buffer、异常 | `.../python` |
| Java | JNI 引用、线程附着、类加载 | `.../jni` |
| JS/WASM | Promise、Event Loop、线性内存、SourceMap | `.../js-wasm` |

## 正反例与边界

正例：`x_buffer_free(ptr, len, allocator_id)` 由创建方提供释放入口。反例：把 X-Lang `String` 地址直接暴露给 Python/JS 并假设生命周期一致。边界包括 ABI 版本不匹配、线程退出、异常、编码和大端/小端布局；不满足契约必须拒绝加载并给出诊断。

## 安全与性能

绑定生成器默认只读、无网络；构建脚本和插件需沙箱。零拷贝仅在布局、生命周期和线程模型可证明时启用，否则回退复制并记录成本。基准比较复制次数、跨界调用延迟和内存峰值。

## 回滚与追溯

绑定按语言和 ABI 版本独立发布；失败时回退 C Shim/句柄模式，不修改核心类型。规则和测试映射 `XLC-FFI-*`、`XLF-01-013`、`XLF-10-014`，物理项目见 `tools/x-bindgen`、`sdk/` 与 `tests/interoperability/`。
