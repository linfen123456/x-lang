# P0 纵向切片实现设计

> 状态：Proposed｜日期：2026-08-18  
> 关闭：G1、G6、G7、`GAP-COMP-01/02`、工程大纲 P0-T04～T10  
> 规范依据：RFC-0005（语法子集）、RFC-0006/0007/0008（语义子集）、RFC-0003/0004（最小包图）  
> 架构依据：[ADR-0002](../decisions/ADR-0002-staged-modular-monolith.md)、[ADR-0003](../decisions/ADR-0003-p0-language-profile-and-labs-freeze.md)、[ADR-0004](../decisions/ADR-0004-rust-llvm-host-baseline.md)  
> 物理蓝图：[完整项目目录架构 §1.3](../X-Lang完整项目目录架构与模块说明.md)

## 1. 目标与非目标

### 1.1 目标

在单一主机 Tier 候选上交付：

```text
.x 源码 → Lexer → Parser → (最小 Resolve/Type) → HIR/MIR 简化 → LLVM → 可执行文件
```

并提供：`x check` / `x build` / `x run`（最小）、符合性 runner 冒烟、一份可复现 CI。

### 1.2 非目标（P0 禁止进入实现）

- 完整借用检查器 / 生命周期推断 / Trait 求解器；
- 完整 XPM Resolver、Registry、签名、Foreign Adapter；
- LSP、增量查询磁盘缓存、自举；
- `defer`、async、宏、comptime、GC、UI、ML、Agent；
- 多 crate 拆分超过 ADR-0002 的 5 成员预算。

## 2. Workspace 与模块边界

### 2.1 成员（恰好 5）

| 成员 | 职责 | 禁止依赖 |
|---|---|---|
| `compiler` | 纵向编译链 + 内部 LLVM adapter | 不得依赖 `cli` |
| `runtime` | 入口、panic=abort 默认、最小 alloc 挂钩 | 不得依赖 `compiler` |
| `library-core` | `Option`/`Result`/标量包装的最小声明 | 不得依赖 `compiler`/`cli` |
| `cli` | `x` 命令路由 | 可依赖 `compiler` driver API |
| `conformance` | 语料发现、执行、Rule ID 报告 | 通过 CLI/driver，不读私有 AST |

`dev/xtask` 可选存在，**不**加入 Workspace `default-members`。

### 2.2 `compiler` 内部模块（单 crate）

```text
source → syntax → semantic → ir → codegen → driver
```

| 模块 | 公开给 crate 内 | 对外（`compiler::` 门面） |
|---|---|---|
| `source` | `SourceId`、`Span`、`SourceMap`、`Diagnostic` | 诊断 JSON schema 稳定草稿 |
| `syntax` | `Token`、`Ast*`、`parse` | AST dump（调试） |
| `semantic` | Resolve/Type 最小表 | 否（P0 不稳定） |
| `ir` | HIR/MIR 简化节点、verifier | MIR text dump |
| `codegen` | `Backend` trait + `LlvmBackend` | 否；LLVM 类型不泄漏 |
| `driver` | `Compilation`、工件清单 | **唯一**稳定门面 |

依赖方向单向；CI 用简单 `mod`/`use` 扫描或 `cargo deny`/自定义检查防止逆向依赖。

## 3. P0 语言子集（可编码清单）

只实现下列表面能力；其余 RFC-0005 结构解析为「识别并诊断未实现」或直接拒绝。

| 类别 | 包含 | 排除 |
|---|---|---|
| 文件 | M1–M3 单包、≤2 源文件、`main`；最终 P0 必须三包 Path Workspace | 完整模块树、`pub(package)` 全语义 |
| 绑定 | `let`/`var`、标量、`bool` | 泛型、闭包、静态 |
| 类型 | `i32`/`i64`/`bool`/`()`、名义 `struct` 无方法 | trait、枚举复杂载荷（可先支持无数据 enum 或延后） |
| 控制流 | `if`/`while`/`return`、强制 `()` 头 | `match` 完整（P0 可只支持 `if`；`match` 列 P1） |
| 函数 | `fn`、显式参数/返回类型 | 重载、默认参数 |
| 错误 | `Result` 类型名识别；`?` 可 P0 延后到 P1 | panic unwind、自定义 Drop |
| 所有权 | 移动直觉（非 Copy 赋值后旧绑定不可用）的**语法级/类型级近似** | 完整 NLL、字段级 borrow |
| 包 | M1–M3 可单 `x.toml` 或固定布局；最终 P0 必须三包 Path 图进入 Action DAG 并经 LLVM 链接（P0-T10） | Registry/Git |

**P0 Hello World 契约：**

```x
fn main() -> () {
    print_i32(1);
}
```

`print_i32` 可作为 runtime/intrinsic 或外部 C stub；不要求完整 stdio 库。

## 4. 纵向里程碑

| 里程碑 | 交付 | 验证命令（目标） | 失败回退 |
|---|---|---|---|
| M0 | Rust/LLVM 探针：手写 LLVM IR → 可执行 | `xtask llvm-probe` | 换绑定或锁定 LLVM 大版本（ADR-0004） |
| M1 | Lexer + Parser + AST dump | `x dump-ast hello.x` | 缩小语法子集 |
| M2 | 最小类型检查（标量+函数） | `x check hello.x` | 拒绝未实现语法，不崩溃 |
| M3 | AST→简化 MIR→LLVM→链接 | `x build hello.x && ./hello` | 保留 MIR interpreter 旁路（可选） |
| M4 | CLI + 三包 Path 图 + 符合性阻断门禁 + CI | `x test conformance --stage p0 --gate p0` | 失败则不宣称 P0 完成、不进入 P1 |

对应工程任务：M0↔T04/T07 探针，M1↔T05，M3↔T06，M4↔T01/T02/T03/T09/T10 与最终符合性检查点。

## 5. Driver 门面（实现接口草图）

```text
Compilation::parse(inputs) -> AstBundle | Diagnostics
Compilation::check(ast) -> TypedBundle | Diagnostics
Compilation::lower(typed) -> MirModule | Diagnostics
Compilation::codegen(mir, target) -> ObjectArtifacts | Diagnostics
Compilation::link(objects, runtime) -> Executable | Diagnostics
```

要求：

- 所有失败走 `Diagnostic { code, rule_id, span, message, fixit? }`；
- 禁止 `unwrap` 泄漏到 CLI；
- 工件目录结构固定：`target/x/<profile>/{deps,build,out}`（P0 可简化为单目录）。

## 6. 最小包图（P0-T10）

P0 不实现完整 PubGrub。最小契约：

1. 发现 Path 成员 `x.toml`（name、version、deps.path）；
2. 按 PackageId 拓扑排序；依赖环须先在 RFC-0003 登记具体诊断码及 Rule ID；`X-E2xxx`/`X-E2900` 不得作为未批准的临时代码发布；
3. 产出版本化 `ResolvedGraph` JSON（字段稳定，算法可换）；
4. XBuild 最小 Action：`compile(member) → objects`、`link(bin)`；
5. 随机目录枚举顺序下，ResolvedGraph 字节一致；节点按规范 PackageId（含 SourceId 和精确版本/提交）排序，不仅按可能重名的 package name。

完整锁文件/Registry 留在 P3（RFC-0003）。

## 7. ABI 探针（GAP-COMP-01）

| 项 | P0 要求 |
|---|---|
| Target | 单一主机 triple（由 CI 矩阵首行决定） |
| 布局 | `i32`/`i64`/`bool`/`struct { i32, i32 }` 与 C 对照 |
| Harness | `extern "C"` 双向调用各 1 个标量 + 1 个结构体 |
| 承诺 | **不**形成 Stable ABI；仅探针证据 |

## 8. 运行时最小集

| 能力 | P0 |
|---|---|
| 入口 | `xt_start` → `main` |
| panic | 仅 `panic=abort` |
| alloc | 可链接系统分配或 LLVM 默认；不暴露 GC |
| Drop | 无用户 Drop；标量/结构体无析构器副作用测试 |

## 9. 验收清单（P0 检查点）

- [ ] M0–M4 命令在文档记录的 OS/Arch 上可复现；
- [ ] 至少 1 个 compile-pass、3 个 compile-fail（含未实现语法）、1 个 run-pass；最终 P0 CI 中 `--stage p0 --gate p0` 阻断失败或未解释跳过；
- [ ] 三包 Path Workspace 经版本化 ResolvedGraph → Action DAG → LLVM 链接运行；随机化输入枚举顺序结果一致；
- [ ] LLVM 类型不出现在 `compiler` 门面公开类型中；
- [ ] Workspace 成员 ≤5；无空 crate；
- [ ] 不实现总纲已排除的 P0 特性（如 defer/async/宏）；ADR-0003 的新增剖面条件仅在 Accepted 后作为门禁依据；
- [ ] 追溯：M0–M3 实验语料可标注 `P0-UNSTABLE-*` 临时 ID；最终 P0 阻断语料均映射经评审的 Rule ID 与确定诊断码，临时 ID 不得算作覆盖；

## 10. 开放问题（必须带 Owner 阶段）

| 问题 | 责任角色 | 默认/失败回退 | 最迟决策 |
|---|---|---|
| P0 是否包含 `match` | Language Owner | 否，P1 | P1-T01 前 |
| `print_*` intrinsic vs C printf | Runtime Owner | intrinsic；失败则保留显式 C stub | M3 前 |
| Windows 链接器 | Backend Owner | 平台默认 + LLVM；失败则先选单一已验证主机 | M0 |
| 双文件模块如何解析 | Language Owner | 包根 `mod` 隐式文件路径子集；未批准则 P0 仅单文件并更新门禁 | M2 |
