# P1 工作分解：Core-CLI 0.1

> 类型：Workplan｜唯一负责：P1 的任务、顺序、DoD、样例。门禁以 [roadmap](../roadmap.md) 为准，特性范围以 roadmap §4 为准。

## 1. 结论

- 目标：用 X 写出真实的小型 CLI（参考程序 `xwc`），具备多文件、单包 + Path 依赖、泛型/Trait、受检引用、`Result/?`、最小 std、测试与格式化。
- 四条工作流可以并行：A 语言前端，B 中端与借用检查，C std/运行时，D 工具链与包。
- 规模【推断】：4–6 人，6–9 个月。开工前置条件：spec 01–07 的 P1 子集为 Accepted；ADR-0005 的查询框架探针已有结论。

## 2. 任务

### A 语言前端

| ID | 任务 | 依赖 | DoD |
|---|---|---|---|
| A01 | 多文件模块树、`use/as/pub use`、可见性（`X-E2001…2009`） | P0 | RULE-MOD-* 语料全部通过 |
| A02 | `enum`、`match`、模式全集、穷尽性检查（`X-E2101…2111`） | A01 | RULE-PAT-* 语料通过；穷尽性诊断给出缺失模式示例 |
| A03 | `impl` 固有方法、Receiver、一次自动解引用（[06](../../specs/language/06-modules.md) §9） | A01 | RULE-METHOD-* 语料通过 |
| A04 | 泛型 + Trait + 关联类型 + 孤儿/重叠规则（`X-E3011…3017`） | A03 | RULE-TRAIT-*（P1 子集）语料通过 |
| A05 | 内建 Trait：`Copy/Clone/Drop/Eq/Ord/Hash/Default/Display/Debug/Iterator/IntoIterator` | A04 | `==`/`<` 经 Eq/Ord 分派；`for` 脱糖可运行 |
| A06 | `f"..."` 插值字符串、`i128/u128/f32/f64/char` 代码生成 | A05 | 插值字符串快照通过；浮点语料与 C 参考值逐位一致 |
| A07 | `X-E1030` 生命周期语法拒绝、`X-W0001…0004/0006/0007` lint | A01 | 语料通过 |

### B 中端与借用检查

| ID | 任务 | 依赖 | DoD |
|---|---|---|---|
| B01 | 查询式 Driver（ADR-0005），覆盖 [compiler](compiler.md) §3 的查询清单 | P0 | 未改动时二次 `x check` 零重算；修改函数体只重算该函数 |
| B02 | `&`/`&mut`、区域推断、省略规则（`X-E4010`） | A04 | RULE-OWN-ELISION 语料通过 |
| B03 | 受限 NLL 借用检查（`X-E4002…4007`），不含两阶段借用 | B02 | RULE-OWN-*（P1 子集）语料通过；不存在未经检查的引用 |
| B04 | Drop 展开 + drop flag；部分移动规则 | B03 | Drop 轨迹语料（打印式 Drop）三方一致 |
| B05 | MIR 解释器（ADR-0006） | B04 | `x test conformance --oracle` 全部 run-pass 结果三方一致 |
| B06 | MIR 优化遍：常量传播、死块消除、内联 | B04 | 差分测试一致；基准不劣化 |
| B07 | `Result/Option/?` 脱糖、`main` 返回 `Result`（`X-E5001/5002/5004/5005`） | A05 | RULE-ERR-*、RULE-TERM-MAIN 语料通过 |
| B08 | `unsafe`、原始指针、`extern "C"`、`@repr(C)`、`@export`（`X-E6001…6004`） | A04 | RULE-UNSAFE-CONTEXT、RULE-FFI-* 语料通过；调用 libc `strlen` 的示例正确 |

### C 标准库与运行时

| ID | 任务 | 依赖 | DoD |
|---|---|---|---|
| C01 | `core`：原语方法、`Option/Result`、`cmp`、`iter`（P1 部分）、`slice`、`str`、`mem`、`fmt` | A05 | 每个公开 API 至少有 1 个 `@test` |
| C02 | `alloc`：`Box/Vec/String/Rc/Weak`；xrt 分配器 intrinsic | C01、B04 | 在 ASan 构建下跑 Vec/String 压力测试零报告 |
| C03 | `std`：`collections::HashMap/HashSet`（随机种子）、`io`、`fs`、`env`、`process::exit`、`time` | C02 | 三主机 CI 通过 I/O 语料 |
| C04 | macOS arm64 支持（xrt `pal/unix.rs` 的 Darwin 差异、链接、签名占位）；Windows 与 Linux 从 P0 起已经支持 | C03 | `ubuntu-24.04`、`windows-2025`、`macos-15` 三主机 CI 为绿 |

### D 工具链与包

| ID | 任务 | 依赖 | DoD |
|---|---|---|---|
| D01 | `x.toml` 解析与校验（`X-E8001…8004`） | P0 | RULE-PKG-*（P1 子集）语料通过 |
| D02 | Path 依赖与 Workspace，`x.lock` v1，`--locked`（`X-E8005…8007`） | D01 | 三包 Path Workspace 构建运行；在随机目录枚举顺序下 Lockfile 字节一致 |
| D03 | `x new/init/build/run/check/test/fmt/clean`（命令契约见[包规范](../../specs/packages/manifest-lock-build.md) §7） | D02 | 命令的 UI 测试通过 |
| D04 | `@test` 收集与运行：每个用例在独立子进程中运行（1.0 只有 panic=abort，见 ADR-0008 K3），并行执行，带超时 | A05 | 某个用例 panic 时，其余用例照常运行；失败用例给出名称、位置、消息；退出码为 1 |
| D05 | `x fmt`（基于 CST，[01](../../specs/language/01-lexical-syntax.md) §8） | P0 | 对语料仓执行 `x fmt --check` 幂等；注释零丢失 |
| D06 | fuzz：parser、类型检查（基于语法生成器）每晚 1 CPU 小时 | P0 | 崩溃自动建 Issue；没有未分诊崩溃 |

关键路径：A01→A03→A04→A05→B02→B03→B04→B05。C、D 两条线在 A05 之后汇合于 `xwc`。

## 3. 样例

### 3.1 参考 CLI `xwc`

```x
// xwc/src/count.x
pub struct Counts { pub lines: usize, pub words: usize, pub bytes: usize }

pub fn count_text(text: &str) -> Counts {
    var c = Counts { lines: 0, words: 0, bytes: text.len() };
    var in_word = false;
    for (ch in text.chars()) {
        if (ch == '\n') { c.lines = c.lines + 1; }
        if (ch == ' ' || ch == '\n' || ch == '\t' || ch == '\r') {
            in_word = false;
        } else if (!in_word) {
            in_word = true;
            c.words = c.words + 1;
        }
    }
    c
}

@test
fn counts_basic() {
    let c = count_text("a b\nc\n");
    assert_eq(c.lines, 2);
    assert_eq(c.words, 3);
    assert_eq(c.bytes, 6);
}
```

```x
// xwc/src/main.x
use std::env;
use std::fs;
use std::io::IoError;
use xwc::count::count_text;

fn main() -> Result<(), IoError> {
    var first = true;
    for (arg in env::args()) {
        if (first) { first = false; continue; }
        let text = fs::read_to_string(arg.as_str())?;
        let c = count_text(text.as_str());
        println(f"{c.lines} {c.words} {c.bytes} {arg}");
    }
    Ok(())
}
```

命令与期望：

```text
$ printf 'a b\nc\n' > t.txt && x run -- t.txt
2 3 6 t.txt
$ x run -- missing.txt; echo $?
error: 文件不存在: missing.txt (NotFound)
1
$ x test
test count::counts_basic ... ok
test result: ok. 1 passed; 0 failed
```

`IoError` 的 `Display` 格式为 `<本地化描述>: <路径> (<IoErrorKind>)`，具体文本以 std 文档为准，测试中只匹配 `NotFound`。

### 3.2 借用检查（compile-fail）

```x
fn main() {
    var v: Vec<i32> = Vec::new();
    v.push(1);
    let first = v.get(0);
    v.push(2);           //~ ERROR X-E4003
    print(f"{first:?}\n");
}
```

期望：`error[X-E4003]: 无法可变借用 `v`，因为它已被共享借用`。附加标签指出共享借用在 `v.get(0)`，并在 `first` 最后一次使用处标注借用仍然活跃。

### 3.3 `?` 错误类型不一致（compile-fail）

```x
use std::io::IoError;

fn parse_port(s: &str) -> Result<u16, IoError> {
    let n = s.parse::<u16>()?;   //~ ERROR X-E5001
    Ok(n)
}
```

期望：`error[X-E5001]: `?` 的错误类型 `ParseError` 与函数返回的错误类型 `IoError` 不一致`。附加提示：使用 `match` 显式转换；P2 起也可以用 `map_error`。

### 3.4 Drop 轨迹（run-pass，三方一致）

```x
struct Noisy { id: i32 }
impl Drop for Noisy {
    fn drop(&mut self) { println(f"drop {self.id}"); }
}
fn main() {
    let a = Noisy { id: 1 };
    let b = Noisy { id: 2 };
    println("end");
}
```

期望 stdout：`end`、`drop 2`、`drop 1`，各占一行（逆声明顺序）。解释器、`-O0`、`-O2` 三方的输出必须一致。

## 4. P1 完成定义（汇总）

1. [roadmap](../roadmap.md) 中 P1 的全部验收项为绿；
2. `gates/p1.toml` 中所有 Rule ID 都有通过的语料；
3. 诊断登记册中 phase ≤ P1 的码都已实现，并各有至少 1 条语料；
4. [performance](../performance.md) 中 P1 列的指标已开始采集（P1 不设阻断阈值，只记录基线）。
