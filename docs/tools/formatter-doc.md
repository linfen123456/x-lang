---
doc_id: DOC-TOOLS-FORMATTER-DOC
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.1"
maturity: EXTENDED
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-02-005, XLF-03-010, XLF-11-005, XLF-11-013]
---
# `xfmt`、`xdoc` 与 `repl`

> 状态：草案｜Owner：`role/tooling-team`

## xfmt

`xfmt` 输入 `FormatRequest{files:Vec<PathBuf>,edition:Edition,config:FmtConfig,check:bool,stdin_name:String?,cancel:CancelToken}`，输出 `FormatResult{changed:Vec<PathBuf>,patches:Vec<Patch>,diagnostics,format_version}`。前置是路径授权和 parser schema 支持；后置是 parse-print-parse 等价、格式幂等、注释/空白语义保持。`--check` 不写源，默认写回前先生成临时文件并原子替换；语法或配置错误返回 1，权限/磁盘/环境失败返回 3，取消或 deadline 超时返回 4，工具内部不变量失败返回 5。

配置字段为 `line_width:u16`、`indent_width:u8`、`trailing_comma:enum`、`newline:enum`；未知配置拒绝。单文件 16 MiB、目录 10k 文件、单命令 2 min 是 `candidate_default`，遵循 [工具链 Budget 治理](./README.md#安全profile-与完成定义)；取消时不覆盖未提交文件。负向测试包括错误恢复节点、Unicode、CRLF、宏/属性、注释附着、symlink 与并发格式化。

## xdoc 与 doc-test

`xdoc` 从已验证 AST/HIR 和公开 API 元数据生成 `DocIndex{items,modules,links,examples,source_version}`；示例字段为 `code:String`、`mode:CompilePass|CompileFail|Run`、`expected_diagnostics:Vec<String>`、`timeout_ms:u64`、`sandbox:SandboxProfile`。示例必须在隔离 sandbox 中编译，失败退出码 2；文档生成不执行任意网络或生产副作用。

## repl

`x repl` 使用 `ReplSession{edition,profile,history_limit,scope:SandboxScope}`；每个输入块独立 parse/query，但共享的绑定只能显式 commit。Ctrl-C 取消当前 query，EOF 关闭任务/句柄；单行 1 MiB、历史 10k、内存 256 MiB 均为 Profile 的 `candidate_default`。REPL 不加载未签名插件、默认无网络。schema/格式器回滚通过固定 `format_version`、旧 formatter binary 和旧 doc index 恢复。
