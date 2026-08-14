---
doc_id: SPEC-MEM-CONC
title: X-Lang 内存与并发规范
status: draft
maturity: CORE
owner: runtime-architecture
depends_on: [SPEC-LANG-CORE]
trace: [XLF-01-006, XLF-01-009, XLF-05-001, XLF-05-006, XLF-10-003, XLF-12-014, XLC-CORE-010..015]
---

# X-Lang 内存与并发规范

## 目标与非目标

冻结所有权、借用、RAII、线程安全和异步取消的核心边界。可选 GC、GPU 统一地址空间、通用硬实时和自动插锁属于独立 RFC/Labs，不改变默认语义。

## 规范条文

### XSP-MEM-001 所有权与 RAII

值默认移动；`Copy` 必须显式满足无资源复制条件。作用域退出按确定顺序执行 Drop；正常返回、错误传播和 panic 路径均必须清理已初始化资源且不得双重释放。

### XSP-MEM-002 借用

共享借用可并存；可变借用在其生命周期内必须排他。借用不能超过被借对象，违反规则必须在编译期拒绝；`unsafe` 只能通过明确边界进入。

### XSP-MEM-003 线程与数据竞争

跨线程迁移必须满足 `Send` 能力，共享必须满足 `Sync` 能力。数据竞争不是可接受的实现定义行为；锁、原子和 Channel 的同步语义必须显式可见。

### XSP-MEM-004 异步取消

取消是协作式的；Future 被丢弃时必须执行规定的 Drop，不能隐式阻塞或泄漏外部句柄。`await` 不改变所有权规则，阻塞调用必须通过显式隔离 API。

## 正例与反例

```x
let mut v = Vec<Int>();
let view = &v;       // 正例：共享借用
print(view.len());
```

```x
let a = &mut v;
let b = &v;           // 反例 X-E-BORROW-001：可变借用期间禁止共享借用
```

## 边界、安全与性能

原始指针、MMIO、对齐、FFI 和自定义分配器必须在 `unsafe` 契约中声明前置条件。实现不得以自动插锁掩盖竞争；运行时可提供 Race 检测但不能改变程序语义。基准记录分配次数、尾延迟、任务取消延迟和线程数。

## 测试与回滚

`CON-MEM-MOVE-*`、`CON-MEM-DROP-*`、`CON-CONC-LITMUS-*`、`CON-ASYNC-CANCEL-*` 覆盖 compile-fail、MIR Drop 检查、Loom/模型测试、Sanitizer、跨平台线程和 panic/FFI 边界。若新规则破坏兼容性，限定在新 Edition 或 feature gate，并保留旧 lowering。
