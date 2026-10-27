# 01 词法、文法与属性

> 类型：Spec｜唯一负责：源码编码、Token、关键字、字面量、运算符优先级、完整 EBNF、属性注册表、格式化规范。特性的阶段归属见 [roadmap §4](../../docs/roadmap.md)。

## 1. 结论

- 共 32 个硬关键字（在旧版 31 个基础上新增 `static`），另有 8 个保留字。
- 控制结构头部必须加括号；没有自动分号插入。
- 块类表达式（`if/match/loop/unsafe/{}`）作为语句时不需要 `;`。
- 优先级：比较运算低于位运算（与 C 不同，与 Rust 相同）。比较运算不可结合，比较链直接报错。
- 属性只能使用 §7 注册表中的名称，未登记的报 `X-E1020`。

## 2. 源码 [RULE-LEX-UTF8]

1. 源文件必须是 UTF-8，扩展名为 `.x`。非法字节序列报 `X-E1001`，不得替换后继续编译。
2. 接受 LF 和 CRLF。Span 统一用原始字节偏移记录，行列号按 Unicode 标量值计算。
3. 允许 UTF-8 BOM，词法分析时忽略。
4. 空白（空格、`\t`、换行）不产生语义。

## 3. Token

### 3.1 标识符 [RULE-LEX-IDENT]

`IDENT = [A-Za-z_][A-Za-z0-9_]*`，且不得是硬关键字或保留字。单独一个 `_` 是通配模式，不是标识符。含非 ASCII 字符报 `X-E1007`；Unicode 标识符留待 1.0 后的 RFC。

命名约定：
- 类型、Trait、枚举变体用 `UpperCamel`；
- 函数、变量、模块文件用 `snake_case`；
- 常量与 static 用 `SCREAMING_SNAKE`。
违反约定只产生 lint，不报错。

### 3.2 关键字 [RULE-LEX-RESERVED]

硬关键字（32 个）：

```text
const enum extern fn impl pub static struct trait type unsafe use
let move mut var
break continue else for if in loop match return while
as where
true false self Self
```

保留字（8 个，不得用作标识符）：

```text
async await defer dyn macro throw try yield
```

处理规则：
- 保留字出现在 Item、语句或表达式开头时，报 `X-E9002`（1.0 已排除的特性），并提示替代写法：`defer` 提示使用 RAII Guard，`async` 提示使用 `std::thread`。
- 保留字出现在其他位置时报 `X-E1015`。

上下文词（不是关键字）：
- `package` 只在 `pub(package)` 中有特殊含义；
- 原始类型名（`i32`、`bool` 等）属于“原始类型作用域”，不得被重新定义（报 `X-E2004`），见 [02](02-types-traits.md) §2。

### 3.3 注释 [RULE-LEX-COMMENT]

| 形式 | 含义 |
|---|---|
| `// ...` | 行注释 |
| `/* ... */` | 块注释，不可嵌套；未闭合报 `X-E1002` |
| `/// ...` | 文档注释，附着到下一个 Item、字段或变体 |
| `//! ...` | 模块文档注释，只能出现在文件开头 |

注释是 trivia，保留在 CST 中（见 [ADR-0005](../../docs/decisions/ADR-0005-query-compiler-and-lossless-cst.md)）。

### 3.4 字面量 [RULE-LEX-NUMBER] [RULE-LEX-STRING] [RULE-LEX-ESCAPE] [RULE-LEX-CHARLIT]

| 种类 | 形式 | 类型 |
|---|---|---|
| 整数 | `123`、`1_000`、`0xFF`、`0o17`、`0b1010`，可带后缀：`255u8`、`255_u8` | 有后缀时取后缀类型；无后缀时按上下文推断，无约束则为 `i32` |
| 浮点 | `1.5`、`1e10`、`2.5e-3`，可带后缀 `f32`/`f64` | 无约束时为 `f64` |
| 布尔 | `true`、`false` | `bool` |
| 字符 | `'a'`、`'\n'`、`'\u{1F600}'` | `char`（Unicode 标量值） |
| 字符串 | `"text"`，可跨行 | `&str` |
| 原始字符串 | `r"C:\path"`、`r#"含 "引号""#`（`#` 最多 255 个） | `&str` |
| 字节串 | `b"bytes"`（只允许 ASCII 与 `\x..` 转义） | `&[u8]` |
| 插值字符串 | `f"x = {x}, y = {point.y:?}"`；`{{`、`}}` 表示字面花括号 | `String`（见 [03](03-expressions-patterns.md) §7） |

更多规则：
- 转义序列只有：`\n \r \t \\ \0 \' \" \x7F`（≤ 0x7F）`\u{...}`（1–6 位十六进制，且必须是合法标量值）。其他转义报 `X-E1004`。
- 整数后缀只能是 `i8 i16 i32 i64 i128 isize u8 u16 u32 u64 u128 usize`，浮点后缀只能是 `f32 f64`。其他后缀或格式错误报 `X-E1005`。
- 浮点字面量的 `.` 后必须紧跟数字，所以 `1.max(2)` 是一次方法调用。
- **元组下标规则**：紧跟在 `.` 之后的数字序列只产生 `INTEGER` Token。因此 `t.0.1` 词法分析为 `t . 0 . 1`。
- 字面量越出目标类型范围报 `X-E3009`（类型检查阶段）。

### 3.5 分隔符与运算符

```text
( ) [ ] { } , ; : :: . .. @ -> => ?
+ - * / % ! ~ & | ^ << >> && ||
== != < <= > >=
= += -= *= /= %= &= |= ^= <<= >>=
```

1.0 不提供：`++/--`、`?:`、`??`、`?.`、`**`、`|>`、范围运算符、用户自定义运算符。

## 4. 运算符优先级（唯一来源）

| 级（高→低） | 运算符 | 结合性 |
|---|---|---|
| 1 | 调用 `f()`、方法 `.m()`、字段 `.f`、元组 `.0`、索引 `[i]`、`?` | 左 |
| 2 | 一元 `!`（仅 bool）、`-`、`~`（按位取反）、`*`（解引用）、`&`、`&mut` | 右 |
| 3 | `as` | 左 |
| 4 | `*` `/` `%` | 左 |
| 5 | `+` `-` | 左 |
| 6 | `<<` `>>` | 左 |
| 7 | `&` | 左 |
| 8 | `^` | 左 |
| 9 | `\|` | 左 |
| 10 | `==` `!=` `<` `<=` `>` `>=` | **不可结合**：`a < b < c` 报 `X-E1010`，`a == b == c` 报 `X-E1011` |
| 11 | `&&` | 左，短路 |
| 12 | `\|\|` | 左，短路 |
| 13 | 赋值与复合赋值 | 只能作语句，不产生值；用在表达式中报 `X-E1016`。求值顺序见 [03](03-expressions-patterns.md) §3 |

[RULE-SYN-CMPCHAIN] [RULE-SYN-EQCHAIN] [RULE-SYN-ASSIGNSTMT]

## 5. 文法（EBNF，唯一来源）[RULE-SYN-EXPECT] [RULE-SYN-PAREN]

记号：`{ x }` 表示 0 次或多次，`[ x ]` 表示可选，`|` 表示选择。终结符 `IDENT INTEGER FLOAT CHAR STRING RAW_STRING BYTE_STRING FSTRING` 由 §3 定义。

```ebnf
program        = { use_decl | item } ;
visibility     = "pub", [ "(", "package", ")" ] ;
use_decl       = { attribute }, [ visibility ], "use", path, [ "as", IDENT ], ";" ;
item           = { attribute }, [ visibility ], item_body ;
item_body      = function | struct_decl | enum_decl | trait_decl | impl_decl
               | type_alias | const_item | static_item | extern_block ;

attribute      = "@", IDENT, [ "(", [ attr_args ], ")" ] ;
attr_args      = attr_arg, { ",", attr_arg }, [ "," ] ;
attr_arg       = literal | IDENT, "=", literal | IDENT, [ "(", [ attr_args ], ")" ] ;

function       = [ "unsafe" ], [ abi ], "fn", IDENT, [ generic_params ],
                 "(", [ parameters ], ")", [ "->", type ], [ where_clause ],
                 ( block | ";" ) ;
abi            = "extern", STRING ;
parameters     = parameter, { ",", parameter }, [ "," ] ;
parameter      = { attribute }, ( "self", ":", type | pattern, ":", type ) ;
generic_params = "<", generic_param, { ",", generic_param }, [ "," ], ">" ;
generic_param  = IDENT, [ ":", bounds ] ;
bounds         = bound, { "+", bound } ;
bound          = type_path, [ generic_args | "(", [ type_list ], ")", [ "->", type ] ] ;
where_clause   = "where", where_pred, { ",", where_pred }, [ "," ] ;
where_pred     = type, ":", bounds ;

struct_decl    = "struct", IDENT, [ generic_params ], [ where_clause ],
                 "{", [ field, { ",", field }, [ "," ] ], "}" ;
field          = { attribute }, [ visibility ], IDENT, ":", type ;
enum_decl      = "enum", IDENT, [ generic_params ], [ where_clause ],
                 "{", [ variant, { ",", variant }, [ "," ] ], "}" ;
variant        = { attribute }, IDENT,
                 [ "(", [ type_list, [ "," ] ], ")"
                 | "{", [ field, { ",", field }, [ "," ] ], "}" ] ;
trait_decl     = [ "unsafe" ], "trait", IDENT, [ generic_params ], [ ":", bounds ],
                 [ where_clause ], "{", { trait_item }, "}" ;
trait_item     = { attribute }, ( function | "type", IDENT, [ ":", bounds ], ";" ) ;
impl_decl      = [ "unsafe" ], "impl", [ generic_params ], type, [ "for", type ],
                 [ where_clause ], "{", { impl_item }, "}" ;
impl_item      = { attribute }, [ visibility ], ( function | "type", IDENT, "=", type, ";" ) ;
type_alias     = "type", IDENT, [ generic_params ], "=", type, ";" ;
const_item     = "const", IDENT, ":", type, "=", expression, ";" ;
static_item    = "static", IDENT, ":", type, "=", expression, ";" ;
extern_block   = "extern", STRING, "{", { extern_fn }, "}" ;
extern_fn      = { attribute }, [ visibility ], "unsafe", "fn", IDENT,
                 "(", [ parameters ], ")", [ "->", type ], ";" ;

block          = "{", { statement }, [ expression ], "}" ;
statement      = ";"
               | binding
               | while_stmt | for_stmt
               | block_like, [ ";" ]
               | expression, [ assign_op, expression ], ";" ;
block_like     = if_expr | match_expr | loop_expr | unsafe_block | block ;
binding        = ( "let" | "var" ), pattern, [ ":", type ], "=", expression, ";" ;
assign_op      = "=" | "+=" | "-=" | "*=" | "/=" | "%=" | "&=" | "|=" | "^=" | "<<=" | ">>=" ;
while_stmt     = "while", "(", expression, ")", block ;
for_stmt       = "for", "(", pattern, "in", expression, ")", block ;

expression     = block_like | closure | jump_expr | logic_or ;
jump_expr      = "return", [ expression ] | "break", [ expression ] | "continue" ;
if_expr        = "if", "(", expression, ")", block, [ "else", ( block | if_expr ) ] ;
match_expr     = "match", "(", expression, ")", "{",
                 [ match_arm, { ",", match_arm }, [ "," ] ], "}" ;
match_arm      = pattern, "=>", expression ;
loop_expr      = "loop", block ;
unsafe_block   = "unsafe", block ;
closure        = [ "move" ], "fn", "(", [ closure_param, { ",", closure_param }, [ "," ] ], ")",
                 [ "->", type ], ( block | "=>", expression ) ;
closure_param  = pattern, [ ":", type ] ;

logic_or       = logic_and, { "||", logic_and } ;
logic_and      = comparison, { "&&", comparison } ;
comparison     = bit_or, [ comp_op, bit_or ] ;
comp_op        = "==" | "!=" | "<" | "<=" | ">" | ">=" ;
bit_or         = bit_xor, { "|", bit_xor } ;
bit_xor        = bit_and, { "^", bit_and } ;
bit_and        = shift, { "&", shift } ;
shift          = additive, { ( "<<" | ">>" ), additive } ;
additive       = multiplicative, { ( "+" | "-" ), multiplicative } ;
multiplicative = cast, { ( "*" | "/" | "%" ), cast } ;
cast           = unary, { "as", type } ;
unary          = ( "!" | "-" | "~" | "*" | "&", [ "mut" ] ), unary | postfix ;
postfix        = primary, { call | member | tuple_member | index | "?" } ;
call           = "(", [ arguments ], ")" ;
member         = ".", IDENT, [ "::", generic_args ] ;
tuple_member   = ".", INTEGER ;
index          = "[", expression, "]" ;
primary        = literal | path_expr | tuple_expr | array_expr | struct_expr
               | "(", expression, ")" ;
path_expr      = path_seg, { "::", path_seg } ;
path_seg       = IDENT | "self" | "Self" | generic_args ;
tuple_expr     = "(", ")" | "(", expression, ",", [ arguments ], ")" ;
array_expr     = "[", [ arguments ], "]" | "[", expression, ";", expression, "]" ;
struct_expr    = type_path, [ "::", generic_args ], "{",
                 [ field_init, { ",", field_init }, [ "," ] ], "}" ;
field_init     = IDENT, [ ":", expression ] ;
arguments      = expression, { ",", expression }, [ "," ] ;
literal        = "true" | "false" | INTEGER | FLOAT | CHAR | STRING
               | RAW_STRING | BYTE_STRING | FSTRING ;

pattern        = "_" | literal | "-", INTEGER | name_pattern | tuple_pattern
               | struct_pattern | reference_pattern ;
name_pattern   = path, [ "(", [ pattern_list ], ")" ] ;
tuple_pattern  = "(", ")" | "(", pattern, ",", [ pattern_list ], ")" ;
struct_pattern = path, "{", [ struct_pattern_fields ], "}" ;
struct_pattern_fields = field_pattern, { ",", field_pattern }, [ ",", ".." ], [ "," ]
                      | "..", [ "," ] ;
field_pattern  = IDENT, [ ":", pattern ] ;
reference_pattern = "&", [ "mut" ], pattern ;
pattern_list   = pattern, { ",", pattern }, [ "," ] ;

type           = path_type | tuple_type | array_type | slice_type
               | reference_type | pointer_type | function_type ;
path_type      = type_path, [ generic_args ] ;
generic_args   = "<", type_list, [ "," ], ">" ;
tuple_type     = "(", ")" | "(", type, ",", [ type_list, [ "," ] ], ")" ;
array_type     = "[", type, ";", expression, "]" ;
slice_type     = "[", type, "]" ;
reference_type = "&", [ "mut" ], type ;
pointer_type   = "*", ( "const" | "mut" ), type ;
function_type  = [ "unsafe" ], [ abi ], "fn", "(", [ type_list ], ")", "->", type ;
path           = IDENT, { "::", IDENT } ;
type_path      = ( IDENT | "Self" ), { "::", IDENT } ;
type_list      = type, { ",", type } ;
```

### 5.1 文法附加规则

1. **块类语句**：语句位置以 `if/match/loop/unsafe/{` 开头时，一律按 `block_like` 解析。它不是块的最后一项时，类型必须是 `()`，否则报 `X-E3004`，并提示加 `;` 显式丢弃。它是块的最后一项且没有 `;` 时，作为块的尾表达式。
2. **函数体**：`function` 以 `;` 结尾（不带函数体）的形式只允许出现在 `trait_decl` 中（表示必需方法）。其他位置报 `X-E1013`。
3. **`self` 参数**：必须是第一个参数，类型只能是 `Self`、`&Self`、`&mut Self`（见 [06](06-modules.md) §8）。
4. **结构体字面量**：由于控制头部带括号，`if (p == Point { x: 1, y: 2 }) { ... }` 不存在歧义。
5. **`abi`**：1.0 只接受 `"C"`。其他 ABI 字符串报 `X-E9001`（P5 起扩展）。
6. **`extern_fn`**：必须写 `unsafe`。可变参数 C 函数在 1.0 不支持。
7. **跳转表达式**：`return`、`break`、`continue` 是类型为 `never` 的表达式，因此可以出现在 `match` 分支中（`None => break,`）。它们后面紧跟的 Token 能开始一个表达式时，该表达式就是携带值。
8. **控制头部括号**：`if/while/for/match` 的头部缺少括号报 `X-E1014`。

## 6. 编译期内建函数

以下名称由编译器在类型检查阶段特殊处理，按普通路径导入，属于 `core::intrinsics_public` 门面：

| 函数 | 阶段 | 语义 |
|---|---|---|
| `include_str("相对路径")` | P2 | 编译期读入 UTF-8 文件，得到 `&str`；路径相对当前源文件；文件进入构建键 |
| `include_bytes("相对路径")` | P2 | 同上，得到 `&[u8]` |
| `size_of<T>()`、`align_of<T>()` | P1 | `core::mem`，结果为 `usize` |

## 7. 属性注册表（唯一来源）[RULE-ATTR-REG] [RULE-ATTR-ARGS]

| 属性 | 允许位置 | 参数 | 阶段 | 语义 |
|---|---|---|---|---|
| `@repr(C)` / `@repr(u8)`…`@repr(i64)` / `@repr(transparent)` | struct、enum | 一个布局名 | P1 | 指定布局，见 [07](07-unsafe-ffi.md) §5 |
| `@repr(align(N))` | struct | 2 的幂 | P3 | 最小对齐 |
| `@export("symbol")` | `extern "C" fn` 定义 | 符号名 | P1 | 以给定符号名导出，不做名称修饰 |
| `@link(name = "m", kind = "dylib")` | extern 块 | name、kind（`dylib`/`static`） | P2 | 链接外部库 |
| `@test` / `@test(ignore)` | 无参数、返回 `()` 或 `Result<(), E>` 的函数 | 可选 `ignore` | P1 | 测试用例，仅在 `x test` 中编译 |
| `@derive(...)` | struct、enum | `Copy Clone Eq Ord Hash Debug Default` 的子集 | P2 | 编译器生成实现，见 [02](02-types-traits.md) §7 |
| `@cfg(...)` | Item、impl 项、字段、变体、use | 谓词，见 §7.1 | P2 | 条件编译 |
| `@deprecated(since = "…", note = "…")` | Item | 两个字符串，均可选 | P2 | 使用处产生 `X-W0005` |
| `@must_use` / `@must_use("原因")` | 函数、类型 | 可选字符串 | P1 | 忽略返回值时产生 `X-W0006`；`Result` 默认带此属性 |
| `@non_exhaustive` | 公开 struct、enum | 无 | P2 | 包外匹配必须带 `..` 或 `_` |
| `@inline` / `@inline(never)` | 函数 | 可选 `never` | P1 | 优化提示，不改变语义 |
| `@cold` | 函数 | 无 | P2 | 冷路径提示 |
| `@tailcall` | 函数 | 无 | P2 | 保证自尾调用不增长栈，否则报 `X-E3020` |
| `@allow(lint)` / `@warn(lint)` / `@deny(lint)` | 任意 Item | lint 名 | P1 | lint 等级控制 |
| `@doc(hidden)` | Item | `hidden` | P3 | 从文档中隐藏 |
| `@panic_handler` | `no_std` 包中唯一的函数 | 无 | P4 | 自定义 panic 处理 |
| `@intrinsic` | `core`/`alloc`/`std` 中无函数体的函数声明 | 无 | P0 | 绑定到编译器的 intrinsic（清单见 [compiler](../../docs/design/compiler.md) §7）；在其他包中使用报 `X-E1020` |
| `@interrupt("名称")` | `extern "C" fn` | 向量名 | P5 | 裸机中断入口 |

规则：
- 同一属性重复出现，或参数非法，报 `X-E1021`。
- 位置非法或名称未登记，报 `X-E1020`。
- 新增属性必须经 RFC 修改本表。

### 7.1 `@cfg` 谓词

```text
cfg_pred = target_os = "linux"|"windows"|"macos"|"ios"|"android"|"none"
         | target_arch = "x86_64"|"aarch64"|"riscv64"|"wasm32"|…
         | target_family = "unix"|"windows"|"wasm"
         | feature = "<名称>"
         | debug_assertions | test
         | all(cfg_pred, …) | any(cfg_pred, …) | not(cfg_pred)
```

未知键报 `X-E1021`。`feature` 必须在 `x.toml [features]` 中声明（见 [包规范](../packages/manifest-lock-build.md) §3）。

## 8. 格式化规范（`x fmt`）

1. `x fmt` 只有一种风格，不提供配置项（行宽固定 100，缩进 4 个空格）。
2. 格式化必须保留所有注释，且满足：`parse(format(s))` 与 `parse(s)` 的 AST 等价；`format(format(s)) == format(s)`。
3. 多行列表加尾逗号；`pub ( package )` 规范化为 `pub(package)`；`use` 按路径字典序排序（不改变语义）。

## 9. 规则与诊断

| Rule ID | 诊断 |
|---|---|
| RULE-LEX-UTF8 | X-E1001 |
| RULE-LEX-COMMENT | X-E1002 |
| RULE-LEX-STRING | X-E1003 |
| RULE-LEX-ESCAPE | X-E1004 |
| RULE-LEX-NUMBER | X-E1005 |
| RULE-LEX-CHAR | X-E1006 |
| RULE-LEX-IDENT | X-E1007 |
| RULE-LEX-CHARLIT | X-E1008 |
| RULE-SYN-CMPCHAIN | X-E1010 |
| RULE-SYN-EQCHAIN | X-E1011 |
| RULE-SYN-EXPECT | X-E1013 |
| RULE-SYN-PAREN | X-E1014 |
| RULE-LEX-RESERVED | X-E1015 |
| RULE-SYN-ASSIGNSTMT | X-E1016 |
| RULE-ATTR-REG | X-E1020 |
| RULE-ATTR-ARGS | X-E1021 |
| LINT-DEPRECATED | X-W0005 |

所有诊断码定义见[诊断登记册](../diagnostics/registry.md)。
