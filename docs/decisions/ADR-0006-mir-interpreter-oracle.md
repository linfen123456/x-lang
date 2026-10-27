# ADR-0006 MIR 解释器作为语义 Oracle

> 状态：Accepted｜版本：2.1.0｜负责人：Compiler Lead｜最后更新：2026-10-22
> 类型：ADR｜新增（v2）

## 决策

1. `x-compiler::interp` 是 **P1 的必需组件**，承担以下职责：
   - 符合性测试的参考执行器（Oracle）；
   - `const`/`static` 初始化与 `const fn` 的求值引擎；
   - P2 起检测 UB（[07](../../specs/language/07-unsafe-ffi.md) §3）；
   - P3 起作为 `x repl` 的后端。
2. 解释器直接执行优化前的 MIR，使用抽象内存模型：分配块、来源标签、初始化位图。外部调用只允许白名单中的 intrinsic，如打印和分配。
3. **差分门禁**：所有 run-pass 语料的结果（stdout、退出类别、Drop 轨迹）在解释器、LLVM `-O0`、LLVM `-O2` 三者间必须一致。
4. 解释器不是第二套语义：它与代码生成共享同一份 MIR。如果发现分歧，修正方向以规范为准。

## 后果

- 常量求值与运行时行为天然一致。
- 只要语料不调用解释器不支持的 FFI，CI 就可以在没有 LLVM 的环境里跑大部分语义测试。
