# 测试策略

> 类型：Testing｜唯一负责：测试层次、语料格式、差分与 fuzz、gate manifest、易学实验方法。性能阈值见 [performance](performance.md)。

## 1. 结论

1. 规范中的每条 `RULE-*` 都必须至少有 1 个正例和 1 个反例语料（反例对应的诊断码必须在[登记册](../specs/diagnostics/registry.md)中）。规则没有语料，就不能升为 Implemented。
2. MIR 解释器、LLVM `-O0`、LLVM `-O2` 三方差分，是语义正确性的主门禁。
3. 每个阶段的 gate 由 `gates/<phase>.toml` 定义；CI 只认 gate 的结果。

## 2. 测试层次

| 层次 | 位置 | 工具 | 何时运行 |
|---|---|---|---|
| 单元测试 | 各 crate 的 `#[cfg(test)]` | `cargo test` | 每个 PR |
| 快照测试（CST/AST/HIR/MIR/诊断） | `tests/snapshots/` | `insta` 类快照库；`cargo xtask bless` 更新 | 每个 PR |
| 符合性语料 | `tests/conformance/<phase>/{compile-pass,compile-fail,run-pass,run-fail}/` | `x-conformance` | 每个 PR |
| UI 测试（CLI 输出、退出码） | `tests/ui/` | `x-conformance --ui` | 每个 PR |
| X 语言测试（`@test`，std/生态） | `library/*/tests/`、包内 | `x test`：每个用例在独立子进程中运行（abort 模型） | 每个 PR |
| doc-test | std 文档中的代码块 | `x test --doc`（P2） | 每个 PR |
| 差分测试 | 复用 run-pass 语料 | `x test conformance --oracle` | 每个 PR（P1 起） |
| fuzz | `fuzz/` | `cargo fuzz` + 语法生成器 | 每夜 |
| 并发测试 | `tests/stress/` | TSan、模型检查 | 每夜（P2 起） |
| 基准 | `bench/` | `x test --bench` | 每夜 |

## 3. 符合性语料格式

```x
// tests/conformance/p1/compile-fail/borrow-conflict.x
// RULE: RULE-OWN-CONFLICT
// STAGE: p1
// FLAGS: --edition preview
fn main() {
    var v: Vec<i32> = Vec::new();
    let r = v.get(0);
    v.push(1);       //~ ERROR X-E4003
    print(f"{r:?}");
}
```

| 头部 / 注解 | 含义 |
|---|---|
| `// RULE: <ID>[, <ID>]` | 覆盖的规则，必须出现在 specs 中 |
| `// STAGE: p0…p4` | 最早适用的阶段 |
| `// FLAGS:` | 额外的编译参数 |
| `//~ ERROR X-Exxxx` / `//~ WARN X-Wxxxx` | 期望在本行出现的诊断；`//~^` 表示上一行 |
| `// RUN-STDOUT:` 后接块 / 同名 `.stdout` 文件 | run-pass 期望输出 |
| `// EXIT: <n>` / `// EXIT: abort` | run-fail 期望的退出类别 |

规则：
1. compile-fail 语料必须**恰好**产生标注的诊断，多一个或少一个都算失败。
2. 语料文件一旦合入就不得删除；行为变更时，修改期望并在 PR 中说明对应的规范变更。
3. Gate manifest 示例：

```toml
# gates/p1.toml
stage = "p1"
include = ["tests/conformance/p0/**", "tests/conformance/p1/**"]
required_rules = ["RULE-MOD-*", "RULE-PAT-*", "RULE-OWN-USEMOVED", "RULE-OWN-CONFLICT"]
oracle = true
waivers = []        # 每项都需要 Issue 链接与到期阶段
```

## 4. 快照与 UI 测试

- 快照内容带 `schema_version`。更新快照必须在 PR 中单独提交，并由 Reviewer 审阅 diff。
- 诊断快照同时覆盖人类可读格式与 JSON v1 格式。
- UI 测试覆盖每个 CLI 命令的成功路径、用法错误（退出码 2）和 I/O 错误（退出码 1）。

## 5. MIR 解释器差分测试

1. 对每个 run-pass 语料比较三方：解释器、`-O0`、`-O2`。比较项包括 stdout、stderr 的规范化形式、退出类别、Drop 轨迹（由打印式 Drop 观察）。
2. 不一致时，CI 产出最小化报告（自动缩减语料）。在修复之前，该语料标记为 `waiver`，并强制关联一个 Issue。
3. 随机程序差分（P2 起）：由类型正确的程序生成器（类似 Csmith 的思路）每夜生成 10k 个程序，进行三方比较。
4. 双主机一致性：P0 起，所有符合性语料都必须在 Linux 与 Windows 上同时通过；runner 把 abort 统一归类，不比较平台各自的原始退出码。

## 6. 并发测试（P2 起）

1. std 中的同步原语与通道使用**模型检查**：在受控调度器下（类似 loom 的思路）穷举 2–3 个线程的交错，验证没有数据竞争、死锁或丢消息。
2. 所有 `tests/stress/` 都在 TSan 构建下运行，要求零报告。
3. 内存安全：`x-runtime` 与 std 的分配路径在 ASan 构建下运行压力测试，要求零报告。
4. 原子操作的内存序语义使用 litmus 测试（MP、SB、LB 等）在 x86_64 与 aarch64 上分别验证。

## 7. Fuzz

| 目标 | 阶段 | 判定 |
|---|---|---|
| Lexer/Parser（字节级） | P0 | 不崩溃；CST 往返无损 |
| 类型检查（语法感知生成） | P1 | 不出现 ICE（`X-E0001`） |
| `x.toml`/`x.lock` 解析 | P1 | 不崩溃；解析-序列化-解析的结果一致 |
| 依赖解析（PubGrub） | P2 | 与小图穷举 Oracle 的结果一致 |
| `x fmt` | P1 | 幂等；不改变 CST 的 token 序列（trivia 除外） |
| 随机程序差分 | P2 | 见 §5 |

崩溃自动去重并建 Issue。每个发布版本都不得有未分诊的崩溃。

## 8. 基准

方法与阈值见 [performance](performance.md)。基准结果不阻断 PR，只在每夜运行与发布时作为门禁。

## 9. 易学实验（G-SIMPLE）

1. 参与者：20 名未参与 X 设计的开发者，有 C、Rust、Go、Python 等任一语言的经验。
2. 任务：在 2 小时内用 X 完成参考 CLI 任务（P2 用 `xwc` 的变体；1.0 用 `xgrep` 的变体），只提供 X 文档。
3. 指标：完成率、首次编译成功前的诊断次数、最常见的诊断码 Top 10、主观难度（1–5 分）。
4. 门槛：P2 试点完成率 ≥ 60%；1.0 完成率 ≥ 80%（[vision](vision.md) G-SIMPLE）。
5. 结果用于诊断文案与 ADR-0007 的复审；某个决策的失败率超过 30% 时，触发该决策的复审。
