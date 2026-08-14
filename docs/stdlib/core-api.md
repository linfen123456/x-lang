---
doc_id: STDLIB-CORE-API
title: X-Lang Core/Alloc 核心 API 契约
status: draft
maturity: CORE
owner: standard-library
depends_on: [SPEC-LANG-CORE, SPEC-MEM-CONC]
trace: [XLF-01-006, XLF-09-001, XLF-09-002, XLF-10-001, XLC-CORE-005]
---

# Core/Alloc 核心 API 契约

## 目标与非目标

提供无 OS 依赖的 `Option`、`Result`、集合、字符串、迭代器、智能指针和基础错误类型；不在 Core 引入网络、线程调度、GUI、隐式 GC 或平台句柄。

## API 规则

- `Option<T>` 表示可能缺失，`Result<T,E>` 表示可恢复失败；两者转换必须显式。
- `Vec<T>`、`String` 和 `Box<T>` 的所有权、容量、失效和释放规则与内存规范一致。
- 公开 API 的错误类型必须可匹配，错误信息文本不是稳定标识。
- `Arc/Weak` 仅提供引用计数语义，不保证无锁实时性；循环引用由调用者通过 `Weak` 处理。

```x
fn first(xs: Slice<Int>) -> Option<Int> { xs.get(0) }
fn load(path: Path) -> Result<Bytes, IoError> { fs.read(path) }
```

反例：用空字符串或 `-1` 伪装缺失值；在 `Drop` 中再次释放已转移的指针。

## 边界、性能与安全

整数容量溢出、UTF-8 无效序列、分配失败和迭代器失效必须有明确错误或 panic 策略。基准记录分配、复制、容量增长和迭代吞吐；不提供“零成本”绝对保证。`unsafe` 构造函数必须列出对齐、生命周期和初始化前置条件。

## 测试、回滚与追溯

`tests/stdlib/core` 覆盖属性、模糊、OOM 注入、Unicode、并发计数和 doc-test；API 变更需 ABI/API diff。稳定 API 只能通过新 Edition 或主版本废弃，回滚保留旧实现和迁移说明。
