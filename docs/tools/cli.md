---
doc_id: DOC-TOOLS-CLI
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF-02-013, XLF-02-014, XLF-03-005, XLF-10-012, XLF-11-003, XLF-11-013, XLF-12-018]
---
# `x` CLI 逐命令契约

> 状态：草案｜Owner：`role/tooling-team`

## 通用参数与返回

全局参数：`--format text|json`、`--manifest-path PathBuf`、`--profile ProfileId`、`--target TargetSpecId`、`--offline`、`--locked`、`--jobs u16`、`--timeout Duration`、`--color auto|always|never`、`--verbose`。cwd、路径和环境必须经过 workspace guard；命令不覆盖脏工作区中的用户文件。

| 命令 | 输入/输出 | 成功后置 | 常见失败 |
|---|---|---|---|
| `x init [path]` | 模板/edition→项目文件 | 原子创建 `x.toml/src/` | 1 路径存在/无权 |
| `x check [--all-targets]` | 源+lock→诊断 | 不生成可发布制品 | 1 配置；2 语义失败 |
| `x build [--emit]` | 源+TargetSpec→manifest | 原子写 `target/` | 2 编译；3 工具链 |
| `x run [-- args]` | build artifact→进程状态 | 子进程完成并清理 | 2 程序失败；3 环境 |
| `x test [filter]` | TestPlan→TestReport | 保存 pass/fail/日志 | 2 断言失败；4 取消 |
| `x fmt [--check]` | 源→patch/写回 | 幂等格式；check 不写盘 | 1 语法/权限 |
| `x doc [--open]` | API+示例→HTML/JSON | doc-test 通过才发布 | 2 示例失败 |
| `x repl [--edition]` | 行/块输入→值/诊断 | 会话退出清理资源 | 1 输入；4 Ctrl-C |
| `x clean [--cache]` | 明确输出范围→删除 | 只删 target/cache 白名单 | 1 路径越权 |
| `x publish` | manifest+签名→registry | 服务器确认 digest | 3 签名/网络 |
| `x doctor` | 环境→DoctorReport | 列出版本/权限/能力 | 3 缺失环境 |
| `x env` | profile/服务→脱敏配置 | 只写配置引用 | 3 凭据/权限 |

所有命令支持 `--help`、取消 token、超时和结构化诊断。`x run` 的子进程继承最小环境；`x repl` 默认不加载任意插件和网络；`x clean` 必须展示待删除清单并拒绝 workspace 根或未解析路径。

`x init` 是创建项目的规范命令；`x new` 是完全等价的兼容别名，帮助、JSON 结果和审计记录必须保留用户实际输入，同时将内部操作规范化为 `init`。发布 Profile 的规范写法是 `x build --profile release`；`x build --release` 是等价短别名。若 `--release` 与非 release 的 `--profile` 同时出现，CLI 必须报告参数冲突，不得按参数顺序覆盖。

## JSON 与资源边界

JSON `CommandResult` 字段统一为 `schema_version:"1.0"`、`command:String`、`status:success|user_error|build_failed|environment_failed|cancelled|internal_error`、`exit_code:u8`、`request_id:String`（16-byte u128 的 canonical 32-hex 表示）、`diagnostics:Vec<Diagnostic>`、`artifacts:Vec<ArtifactRef>`、`duration_ms:u64`、`resource:{peak_memory_bytes:u64,network_bytes:u64,children:u16}`。该结构与 `docs/compiler/interfaces/contract.md`、`docs/tools/contracts/contract.md` 相同；单 JSON 1 GiB、诊断 10k、子进程 64。超过声明的输出/资源预算属于环境或配额失败，返回 3 并保留截断标记；只有工具自身不变量被破坏才返回 5。

## 负向测试、兼容与回滚

测试坏 UTF-8/配置、未知命令、重复 flag、锁竞争、非 TTY、stdin EOF、路径逃逸、网络断开、签名不匹配、Ctrl-C、磁盘满和子进程树残留。协议主版本变化使用 `--json-schema` 协商，旧客户端继续读上一 minor；回归时切换上一 CLI/lockfile，禁用实验子命令，不删除源或用户缓存。
