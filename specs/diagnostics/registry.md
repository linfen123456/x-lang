# 诊断码登记册（生成物）

> 状态：Accepted｜版本：2.1.0｜负责人：Compiler Lead｜最后更新：2026-10-22
> 类型：Register｜**由 `tools/doccheck.py` 从 [registry.yaml](registry.yaml) 生成，请勿手改。** 码段：0xxx 驱动｜1xxx 词法/语法/属性｜2xxx 名称/模块/模式｜3xxx 类型/Trait/求值｜4xxx 所有权/借用｜5xxx 错误/终止｜6xxx unsafe/FFI｜7xxx 并发｜8xxx 包/构建｜9xxx 阶段门禁｜X-W 为 lint。码一经分配永不复用。

共 111 个码。

| 码 | 含义 | 阶段 | 规则 | 规范 |
|---|---|---|---|---|
| `X-E0001` | 内部编译器错误（ICE），附复现包路径 | P0 | RULE-DRV-ICE | [compiler.md](../../docs/design/compiler.md) |
| `X-E0002` | 无法读取源文件或目录 | P0 | RULE-DRV-IO | [compiler.md](../../docs/design/compiler.md) |
| `X-E0003` | 命令行参数无效 | P0 | RULE-DRV-CLI | [compiler.md](../../docs/design/compiler.md) |
| `X-E0004` | 链接失败（附链接器原始输出） | P0 | RULE-DRV-LINK | [compiler.md](../../docs/design/compiler.md) |
| `X-E0005` | 目标三元组不受支持或 LLVM 目标初始化失败 | P0 | RULE-DRV-TARGET | [platforms.md](../../docs/platforms.md) |
| `X-E1001` | 源码不是合法 UTF-8 | P0 | RULE-LEX-UTF8 | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1002` | 块注释未闭合 | P0 | RULE-LEX-COMMENT | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1003` | 字符串字面量未闭合 | P0 | RULE-LEX-STRING | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1004` | 非法转义序列 | P0 | RULE-LEX-ESCAPE | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1005` | 数字字面量格式或后缀非法 | P0 | RULE-LEX-NUMBER | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1006` | 非法字符 | P0 | RULE-LEX-CHAR | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1007` | 标识符含非 ASCII 字符 | P0 | RULE-LEX-IDENT | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1008` | 字符字面量非法（空、多字符或未闭合） | P0 | RULE-LEX-CHARLIT | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1010` | 比较运算链（a < b < c） | P0 | RULE-SYN-CMPCHAIN | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1011` | 相等运算链（a == b == c） | P0 | RULE-SYN-EQCHAIN | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1012` | 结构模式中 .. 非尾部或重复 | P1 | RULE-PAT-REST | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E1013` | 语法错误：期望的 Token 缺失 | P0 | RULE-SYN-EXPECT | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1014` | if/while/match/for 头部缺少括号 | P0 | RULE-SYN-PAREN | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1015` | 保留字用作标识符 | P0 | RULE-LEX-RESERVED | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1016` | 赋值用作表达式 | P0 | RULE-SYN-ASSIGNSTMT | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1020` | 属性未登记或附着位置非法 | P0 | RULE-ATTR-REG | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1021` | 属性参数非法或重复 | P1 | RULE-ATTR-ARGS | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-E1030` | 生命周期标注不属于 1.0 | P1 | RULE-OWN-NOLIFETIME | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E2001` | 文件路径规范化后冲突 | P1 | RULE-MOD-PATH | [06-modules.md](../language/06-modules.md) |
| `X-E2002` | 路径第一段不是当前包或直接依赖 | P1 | RULE-MOD-ROOT | [06-modules.md](../language/06-modules.md) |
| `X-E2003` | 导入未直接声明的依赖 | P1 | RULE-MOD-DIRECT | [06-modules.md](../language/06-modules.md) |
| `X-E2004` | Item 名称空间重名 | P0 | RULE-MOD-NS | [06-modules.md](../language/06-modules.md) |
| `X-E2005` | 导入/别名冲突 | P1 | RULE-MOD-ALIAS | [06-modules.md](../language/06-modules.md) |
| `X-E2006` | pub use 重导出环 | P1 | RULE-MOD-REEXPORT | [06-modules.md](../language/06-modules.md) |
| `X-E2007` | 可见性不足或绕过 Facade | P1 | RULE-MOD-VIS | [06-modules.md](../language/06-modules.md) |
| `X-E2008` | 方法调用存在多个候选 | P1 | RULE-METHOD-AMBIG | [06-modules.md](../language/06-modules.md) |
| `X-E2009` | 字段与固有方法同名 | P1 | RULE-METHOD-FIELD | [06-modules.md](../language/06-modules.md) |
| `X-E2010` | 名称未解析 | P0 | RULE-MOD-UNRESOLVED | [06-modules.md](../language/06-modules.md) |
| `X-E2011` | 模块或 static 初始化存在环 | P2 | RULE-MOD-INITCYCLE | [06-modules.md](../language/06-modules.md) |
| `X-E2101` | 使用裸结构模式 { x, y } | P1 | RULE-PAT-NOMINAL | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2102` | 模式字段不存在 | P1 | RULE-PAT-FIELD | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2103` | 模式字段重复 | P1 | RULE-PAT-DUP | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2104` | 未列全字段且无 .. | P1 | RULE-PAT-EXHAUSTFIELDS | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2105` | .. 重复或不在最后（语义层） | P1 | RULE-PAT-REST | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2106` | 模式访问不可见字段 | P1 | RULE-PAT-VIS | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2107` | 不可失败位置使用可失败模式 | P1 | RULE-PAT-IRREFUTABLE | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2108` | 解构后非法使用部分移动值 | P1 | RULE-PAT-PARTIAL | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2109` | 路径解析到不能用于模式的 Item | P1 | RULE-PAT-KIND | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2110` | 引用模式与输入权限冲突 | P1 | RULE-PAT-REF | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E2111` | match 未穷尽（附缺失模式示例） | P1 | RULE-PAT-EXHAUSTIVE | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E3001` | 公开边界缺少显式类型 | P0 | RULE-TYPE-BOUNDARY | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3002` | 非白名单 as 转换 | P0 | RULE-EVAL-CAST | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E3003` | 类型无法推断或存在多个候选 | P1 | RULE-TYPE-INFER | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3004` | 类型不匹配 | P0 | RULE-TYPE-MISMATCH | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3005` | 实参个数与形参不符 | P0 | RULE-TYPE-ARITY | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3006` | 调用的值不是函数 | P0 | RULE-TYPE-CALLABLE | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3007` | 字段不存在 | P0 | RULE-TYPE-FIELD | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3008` | 赋值目标不是可写 Place | P0 | RULE-EVAL-PLACE | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E3009` | 字面量超出目标类型范围 | P0 | RULE-TYPE-LITRANGE | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3010` | 运算符不适用于该类型 | P0 | RULE-EVAL-OPERATOR | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E3011` | Trait 约束不满足（含 Hash/Eq/Fn 系列） | P1 | RULE-TRAIT-BOUND | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3012` | 比较运算要求 Ord 实现 | P1 | RULE-TRAIT-ORD | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3013` | impl 缺少 Trait 必需项 | P1 | RULE-TRAIT-MISSING | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3014` | 违反孤儿规则 | P1 | RULE-TRAIT-ORPHAN | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3015` | impl 重叠 | P1 | RULE-TRAIT-OVERLAP | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3016` | 关联类型缺失或不匹配 | P1 | RULE-TRAIT-ASSOC | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3017` | 泛型实参个数不符 | P1 | RULE-TYPE-GENERICARITY | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3018` | @derive 目标的字段未实现所需 Trait | P2 | RULE-TRAIT-DERIVE | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3019` | 递归类型大小无限（需 Box） | P1 | RULE-TYPE-RECURSIVE | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3020` | @tailcall 函数存在无法保证的自尾调用 | P2 | RULE-EVAL-TAILCALL | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E3021` | 常量求值失败或超出预算 | P2 | RULE-EVAL-CONST | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E3022` | static 类型非 Sync 或初始化器非常量 | P2 | RULE-TYPE-STATIC | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E3023` | 单态化实例数超出预算 | P2 | RULE-TYPE-MONOBUDGET | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E4001` | 移动后使用 | P0 | RULE-OWN-USEMOVED | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E4002` | 重复移动 | P1 | RULE-OWN-DOUBLEMOVE | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E4003` | 借用冲突 | P1 | RULE-OWN-CONFLICT | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E4004` | 借用逃逸出来源 | P1 | RULE-OWN-ESCAPE | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E4005` | 实现 Drop 的类型被部分移动 | P1 | RULE-DROP-PARTIAL | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E4006` | 从借用中移出值 | P1 | RULE-OWN-MOVEOUT | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E4007` | 经共享借用修改 | P1 | RULE-OWN-SHAREDMUT | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E4008` | 对 let 绑定重新赋值 | P0 | RULE-OWN-LETASSIGN | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E4009` | 闭包捕获与外部使用冲突 | P2 | RULE-OWN-CAPTURE | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-E4010` | 返回借用无法确定唯一来源 | P1 | RULE-OWN-ELISION | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-E4011` | Copy 类型含非 Copy 字段或同时实现 Drop | P1 | RULE-TRAIT-COPY | [02-types-traits.md](../language/02-types-traits.md) |
| `X-E5001` | ? 的错误类型与返回类型不一致 | P1 | RULE-ERR-SAMEE | [05-errors-panics.md](../language/05-errors-panics.md) |
| `X-E5002` | Result/Option 传播上下文混用 | P1 | RULE-ERR-MIX | [05-errors-panics.md](../language/05-errors-panics.md) |
| `X-E5003` | unwind 可能跨越外部 ABI（预留：1.0 后 unwind RFC） | P5 | RULE-TERM-FFIUNWIND | [05-errors-panics.md](../language/05-errors-panics.md) |
| `X-E5004` | main 返回类型非法 | P1 | RULE-TERM-MAIN | [05-errors-panics.md](../language/05-errors-panics.md) |
| `X-E5005` | ? 用于非 Result/Option 值 | P1 | RULE-ERR-QTYPE | [05-errors-panics.md](../language/05-errors-panics.md) |
| `X-E6001` | unsafe 操作位于 unsafe 块之外 | P1 | RULE-UNSAFE-CONTEXT | [07-unsafe-ffi.md](../language/07-unsafe-ffi.md) |
| `X-E6002` | extern 签名含非 FFI 安全类型 | P1 | RULE-FFI-TYPE | [07-unsafe-ffi.md](../language/07-unsafe-ffi.md) |
| `X-E6003` | @export 用于非 extern "C" 函数或符号重复 | P1 | RULE-FFI-EXPORT | [07-unsafe-ffi.md](../language/07-unsafe-ffi.md) |
| `X-E6004` | @repr 用法非法 | P1 | RULE-FFI-REPR | [07-unsafe-ffi.md](../language/07-unsafe-ffi.md) |
| `X-E6005` | 手动实现 Send/Sync 缺少 unsafe impl | P2 | RULE-CONC-UNSAFEIMPL | [08-concurrency.md](../language/08-concurrency.md) |
| `X-E7001` | 跨线程传递非 Send 值 | P2 | RULE-CONC-SEND | [08-concurrency.md](../language/08-concurrency.md) |
| `X-E7002` | thread::spawn 闭包捕获借用 | P2 | RULE-CONC-DETACHED | [08-concurrency.md](../language/08-concurrency.md) |
| `X-E7003` | 跨线程共享非 Sync 类型 | P2 | RULE-CONC-SYNC | [08-concurrency.md](../language/08-concurrency.md) |
| `X-E8001` | x.toml 解析失败 | P1 | RULE-PKG-PARSE | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E8002` | x.toml 含未知字段 | P1 | RULE-PKG-UNKNOWN | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E8003` | 包名非法 | P1 | RULE-PKG-NAME | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E8004` | 包名映射到相同导入根 | P1 | RULE-PKG-IMPORTROOT | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E8005` | 包依赖成环 | P1 | RULE-PKG-CYCLE | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E8006` | Path 依赖越出 Workspace 根 | P1 | RULE-PKG-PATHESCAPE | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E8007` | --locked 下 x.lock 需要更新 | P1 | RULE-PKG-LOCKED | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E8008` | Feature 未知或跨解析域 | P2 | RULE-PKG-FEATURE | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E8009` | 版本约束冲突（附最小冲突链） | P2 | RULE-PKG-CONFLICT | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E8010` | 内容摘要或签名校验失败 | P2 | RULE-PKG-DIGEST | [manifest-lock-build.md](../packages/manifest-lock-build.md) |
| `X-E9001` | 当前阶段尚未实现的语法或特性 | P0 | RULE-STAGE-UNIMPL | [roadmap.md](../../docs/roadmap.md) |
| `X-E9002` | 1.0 已排除的特性（defer/async/宏等） | P0 | RULE-STAGE-EXCLUDED | [ADR-0003-scope-1.0-and-wedge.md](../../docs/decisions/ADR-0003-scope-1.0-and-wedge.md) |
| `X-W0001` | 未使用的变量 | P1 | LINT-UNUSED-VAR | [04-ownership-borrowing.md](../language/04-ownership-borrowing.md) |
| `X-W0002` | 未使用的导入 | P1 | LINT-UNUSED-IMPORT | [06-modules.md](../language/06-modules.md) |
| `X-W0003` | 不可达代码 | P1 | LINT-UNREACHABLE | [03-expressions-patterns.md](../language/03-expressions-patterns.md) |
| `X-W0004` | 不必要的 unsafe 块 | P1 | LINT-UNUSED-UNSAFE | [07-unsafe-ffi.md](../language/07-unsafe-ffi.md) |
| `X-W0005` | 使用了 @deprecated 项 | P2 | LINT-DEPRECATED | [01-lexical-syntax.md](../language/01-lexical-syntax.md) |
| `X-W0006` | 忽略了 @must_use 值（含 Result） | P1 | LINT-MUST-USE | [05-errors-panics.md](../language/05-errors-panics.md) |
| `X-W0007` | 显式导入遮蔽 Prelude 名称 | P1 | LINT-PRELUDE-SHADOW | [06-modules.md](../language/06-modules.md) |
