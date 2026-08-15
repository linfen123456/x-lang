---
doc_id: DOC-GUIDE-GETTING-STARTED
title: X-Lang 入门：工具链、项目与第一个程序
authority: implementation
owner: role/docs-team
backup_owner: role/language-council
version: "0.1"
maturity: CORE
status: 草案
phase: P0
last_reviewed: 2026-08-15
applies_to: [learner, x-cli, x-build, x-project]
traceability_scope: [XLF]
supersedes: []
---

# X-Lang 入门：工具链、项目与第一个程序

## 1. 本教程的边界

本章把读者从空目录带到一个可检查、构建、运行和测试的最小 X-Lang 项目。它落实原始材料提出的标准项目结构、一体化命令和 Hello World 端到端目标（XLF-02-012～014），但不声称工具链已经发布。

> **当前实现状态：规划中。** 本仓库目前交付的是语言与工程文档，不包含可执行的 `x` 编译器。下列命令、输出和代码是 P0/P1 的规范目标，用于约束未来实现和验收；现在执行可能得到“命令不存在”。

读完后，读者应能：

- 区分包（package）、模块（module）和源文件；
- 解释 `x.toml`、`src/main.x`、`tests/` 与 `target/` 的职责；
- 按预期使用 `x init/check/build/run/test/fmt/doc`；
- 识别“解析失败、类型失败、链接失败、运行失败”四类问题；
- 不把尚待 RFC 的异步、GC、宏或高级平台能力当成入门前提。

先决条件仅为命令行、文本编辑器和基本函数概念。未来正式工具链的安装包、签名和最低系统版本由平台发布文档决定；本章不提供虚构下载地址。

## 2. 工具链组成与可用性检查

原始材料将构建、运行、测试、格式化、文档和包管理统一到 `x` 命令。未来安装完成后，首先运行：

```console
$ x --version
x 0.x.y (development)

$ x help
Usage: x <COMMAND> [OPTIONS]
Commands: init, check, build, run, test, fmt, doc
```

预期行为：`--version` 返回编译器与工具链版本；`help` 离线可用。任何命令成功返回退出码 0，用户输入或编译失败返回非 0；精确退出码以 [CLI 规范](../tools/cli.md) 为准。

如果系统报告找不到 `x`，说明工具链未安装或不在 `PATH`，不是 X 源码错误。当前仓库没有可供安装的二进制，应继续把示例作为规范阅读，而不是下载来历不明的程序。

## 3. 创建最小项目

### 3.1 目标命令

```console
$ x init hello_x
Created binary package `hello_x`
$ cd hello_x
```

生成结果应等价于：

```text
hello_x/
├── x.toml
├── src/
│   └── main.x
├── tests/
└── .gitignore
```

`target/` 是构建产生的可删除制品目录，不应由模板预填业务文件；`x.lock` 何时生成由包管理规范决定。原始材料曾列出 `benchmarks/`、`.xfmt` 和 `src/modules/`，它们是按需目录，不是 Hello World 的强制噪声。

### 3.2 最小清单

`x.toml` 的 P0 最小目标为：

```toml
[package]
name = "hello_x"
version = "0.1.0"
edition = "2026"

[dependencies]
```

字段约束见 [模块、包与 Edition 规范](../specs/modules-packages-editions.md)。最小清单必须出现 `[dependencies]`，没有依赖时保留为空表；作者、目标平台和 Profile 在需要时再添加。

### 3.3 第一个源文件

`src/main.x`：

```x
fn main() {
    println("Hello, X-Lang!");
}
```

这里 `main` 是二进制包入口；`println` 是 Prelude/标准输出 API 的规范目标，其最终签名仍需标准库 RFC 固化。若早期 P0 原型暂未提供格式化打印，实现可用等价的最小输出内建完成端到端验证，但不得把临时内建写成稳定语言语法。

## 4. 检查、构建与运行

建议开发循环：

```console
$ x fmt --check
$ x check
Checking hello_x 0.1.0
Finished check

$ x run
Hello, X-Lang!
```

各步骤的职责：

| 命令 | 必须做什么 | 不应暗示什么 |
|---|---|---|
| `x fmt --check` | 判断源文件是否符合稳定格式 | 不修改文件 |
| `x check` | 词法、解析、名称解析、类型和所有权检查 | 不要求生成最终可执行文件 |
| `x build` | 生成当前 Profile 的制品 | 不启动程序 |
| `x run` | 必要时构建，然后运行选定二进制 | 不吞掉程序退出码 |
| `x test` | 发现、编译并运行测试 | 不自动接受失败快照 |
| `x doc` | 生成本地文档 | 不上传源码或遥测 |

发布构建目标命令为 `x build --profile release`；兼容别名 `x build --release` 必须等价展开，二者同时出现且冲突时应拒绝。性能数字必须在目标平台上测量，本教程不承诺“比某语言快”或固定编译时间。

## 5. 第一次修改：输入、函数与 Result

为避免依赖尚未冻结的命令行解析库，先把名字定义为常量：

```x
fn greet(name: &str) -> String {
    "Hello, " + name
}

fn main() {
    let message = greet("X-Lang");
    println(message);
}
```

关键点：`let` 默认不可变；函数参数和返回类型显式；函数末尾无分号的表达式是返回值。字符串拼接的所有权与具体 API 最终以标准库文本规范为准，因此编译器原型若尚未实现 `String + &str`，示例应替换成已批准的格式化 API，而不是悄悄改变类型规则。

涉及失败的入口应显式返回 `Result`：

```x
fn run() -> Result<(), AppError> {
    load_config()?;
    Ok(())
}

fn main() {
    match run() {
        Ok(()) => {},
        Err(error) => {
            eprintln(error);
            panic("application failed");
        },
    }
}
```

`?` 只传播兼容错误；它不是异常。生产入口的退出码 API 尚待标准库/运行时规范，因此这里用 `panic` 展示失败路径，不作为企业服务的最终错误策略。

## 6. 添加一个测试

原始材料要求 `x test` 与 `tests/` 目录，但测试属性的最终语法仍待测试 RFC。以下是目标形态：

```x
#[test]
fn greeting_contains_name() {
    let result = greet("Ada");
    assert(result == "Hello, Ada");
}
```

```console
$ x test
running 1 test
test greeting_contains_name ... ok
test result: ok. 1 passed; 0 failed
```

实现验收不能只比对这段展示文本；应验证测试发现、非零失败退出码、诊断 Span 和重复运行的一致性。

## 7. 常见错误与排查顺序

### 7.1 缺少分号

```x
fn main() {
    let answer = 42
    println(answer);
}
```

当前 EBNF 要求 `let` 语句以分号结束。Parser 应在下一行前报告缺少 `;`，并给出 Fix-it；不能把它误报为 `println` 未定义。

### 7.2 修改不可变绑定

```x
fn main() {
    let count = 0;
    count = count + 1;
}
```

应提示把声明改为 `let mut count = 0;`。`mut` 是显式可变性，不应由编译器自动插入。

### 7.3 把未实现特性当成安装问题

当文档标为 EXTENDED、EXPERIMENTAL 或“待 RFC”时，即使语法被 Lexer 保留，当前编译器也可以明确报告 feature-disabled。不要通过随机 Feature 名绕过，也不要把实验代码写入 CORE 教程。

### 7.4 包名、模块名与路径混淆

包名来自 `x.toml`；模块名来自 `mod`；文件路径只是默认模块发现的一项输入。详细规则见 [模块、包与 Edition 规范](../specs/modules-packages-editions.md)。

## 8. 练习与检查点

1. 将消息文本提取为 `fn greet(name: &str) -> String`，解释参数为何是借用。
2. 声明 `let mut count = 0;`，在循环中递增到 3；再移除 `mut`，写出预期诊断。
3. 新建一个库包布局草图，把可复用函数放进 `src/lib.x`，说明二进制入口如何导入它；不要自行发明模块查找规则。
4. 写一个返回 `Result` 的函数，通过 `match` 分别处理成功和失败。

完成检查：你应能说清 `x check` 与 `x build` 的差异；知道当前命令尚未实现；能从错误位置判断词法、解析、类型或所有权阶段；能指出哪些结论来自正式规范而非教程示例。

## 9. 来源与下一步

- 原始来源：`1.txt` 的一体化工具链与渐进学习；`2.txt` 的语法示例、项目结构、`x.toml` 和命令标准。
- 追溯：XLF-01-010、XLF-01-013、XLF-02-012、XLF-02-013、XLF-02-014、XLF-11-013。
- 继续学习：[核心语言教程](./core-language-tutorial.md) → [所有权、错误与并发教程](./ownership-errors-concurrency.md)。
- 规范依据：[核心语言规范](../specs/language-core.md)、[符合性规范](../specs/conformance.md)、[工具链 CLI](../tools/cli.md)。
