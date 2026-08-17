# RFC-0005：核心词法、关键字与表层语法

> 状态：Proposed
> 日期：2026-08-18
> 目标版本：X-Lang 1.0 候选
> 依赖：无
> 相关缺口：`GAP-LANG-01`、`GAP-LANG-02`
> 正式产物：接受后生成 `specs/language/lexical.md` 与 `grammar.ebnf`。

## 1. 摘要

本提案是 1.0 候选词法和表层语法的唯一详细来源。大纲只保留设计摘要；Parser、Formatter、高亮器和语料必须从接受后的同一机器可读来源生成。

## 2. 源码与词法

- 源码是 UTF-8；无效字节序列报 `X-E1001`，不得替换后继续编译；
- 接受 LF 与 CRLF，语义和 Span 统一按 Unicode Scalar 与原始字节偏移记录；
- 标识符候选为 ASCII 字母或 `_` 开头，后接 ASCII 字母、数字或 `_`；Unicode 标识符延期；
- 注释为 `//`、非嵌套 `/* ... */` 和 `///` 文档注释；
- 空白不产生语义，不采用自动分号插入；
- Token 使用最长匹配；字符串和字符的转义、数字进制与后缀必须有独立失败 Token，Lexer 不猜测修复。

## 3. 关键字与符号

31 个硬关键字是：

```text
const enum extern fn impl pub struct trait type unsafe use
let move mut var
break continue else for if in loop match return while
as where
true false self Self
```

`package` 仅在 `pub(package)` 中是上下文词。`Some/None/Ok/Err` 是可导入的标准库名称，不是关键字。1.0 不保留 `async/await/comptime/effect/macro/throw/try` 等未来词。

分隔符为 `() [] {} , ; : :: . .. @ -> =>`。不提供自动分号、用户自定义运算符、范围运算符、`++/--`、`?:`、`??`、`?.`、`**` 或管道运算符。

## 4. 核心产生式

```ebnf
program       = { use_decl | item } ;
visibility    = "pub", [ "(", "package", ")" ] ;
use_decl      = [ visibility ], "use", path, [ "as", IDENT ], ";" ;
item          = { attribute }, [ visibility ], item_body ;
item_body     = function | struct_decl | enum_decl | trait_decl | impl_decl |
                type_alias | const_item | extern_block | export_function ;
attribute     = "@", BUILTIN_ATTRIBUTE, [ "(", [ arguments ], ")" ] ;

function      = [ "unsafe" ], "fn", IDENT, [ generic_params ],
                "(", [ parameters ], ")", [ "->", type ], [ where_clause ], block ;
parameters    = parameter, { ",", parameter }, [ "," ] ;
parameter     = ( pattern | "self" ), ":", type ;
generic_params = "<", type_param, { ",", type_param }, [ "," ], ">" ;
type_param    = IDENT, [ ":", trait_bounds ] ;
trait_bounds  = path, { "+", path } ;
where_clause  = "where", bound, { ",", bound }, [ "," ] ;
bound         = IDENT, ":", trait_bounds ;

struct_decl   = "struct", IDENT, [ generic_params ], "{",
                [ field, { ",", field }, [ "," ] ], "}" ;
field         = [ visibility ], IDENT, ":", type ;
enum_decl     = "enum", IDENT, [ generic_params ], "{",
                [ variant, { ",", variant }, [ "," ] ], "}" ;
variant       = IDENT, [ "(", [ type_list ], ")" | "{",
                [ field, { ",", field }, [ "," ] ], "}" ] ;
trait_decl    = "trait", IDENT, [ generic_params ], "{", { method_signature }, "}" ;
method_signature = "fn", IDENT, "(", [ parameters ], ")", [ "->", type ], ";" ;
impl_decl     = "impl", [ generic_params ], type, [ "for", type ],
                [ where_clause ], "{", { impl_item }, "}" ;
impl_item     = { attribute }, [ visibility ], function ;
type_alias    = "type", IDENT, [ generic_params ], "=", type, ";" ;
const_item    = "const", IDENT, ":", type, "=", expression, ";" ;
extern_block  = "extern", STRING, "{", { extern_function }, "}" ;
extern_function = "unsafe", "fn", IDENT, "(", [ parameters ], ")",
                  [ "->", type ], ";" ;
export_function = [ "unsafe" ], "extern", STRING, "fn", IDENT,
                  "(", [ parameters ], ")", [ "->", type ], block ;

block         = "{", { statement }, [ expression ], "}" ;
statement     = binding | return_stmt | break_stmt | continue_stmt |
                while_stmt | for_stmt | expression, [ assign_tail ], ";" ;
assign_tail   = assign_op, expression ;
assign_op     = "=" | "+=" | "-=" | "*=" | "/=" | "%=" ;
binding       = ( "let" | "var" ), pattern, [ ":", type ], "=", expression, ";" ;
return_stmt   = "return", [ expression ], ";" ;
break_stmt    = "break", [ expression ], ";" ;
continue_stmt = "continue", ";" ;
while_stmt    = "while", "(", expression, ")", block ;
for_stmt      = "for", "(", pattern, "in", expression, ")", block ;

expression    = if_expr | match_expr | loop_expr | unsafe_expr | closure | logic_or ;
if_expr       = "if", "(", expression, ")", block, [ "else", ( block | if_expr ) ] ;
match_expr    = "match", "(", expression, ")", "{",
                [ match_arm, { ",", match_arm }, [ "," ] ], "}" ;
match_arm     = pattern, "=>", expression ;
loop_expr     = "loop", block ;
unsafe_expr   = "unsafe", block ;
closure       = [ "move" ], "fn", "(", [ parameters ], ")", [ "->", type ],
                ( block | "=>", expression ) ;
logic_or      = logic_and, { "||", logic_and } ;
logic_and     = bit_or, { "&&", bit_or } ;
bit_or        = bit_xor, { "|", bit_xor } ;
bit_xor       = bit_and, { "^", bit_and } ;
bit_and       = equality, { "&", equality } ;
equality      = comparison, [ ( "==" | "!=" ), comparison ] ;
comparison    = shift, [ ( "<" | "<=" | ">" | ">=" ), shift ] ;
shift         = additive, { ( "<<" | ">>" ), additive } ;
additive      = multiplicative, { ( "+" | "-" ), multiplicative } ;
multiplicative = cast, { ( "*" | "/" | "%" ), cast } ;
cast          = unary, { "as", type } ;
unary         = ( "!" | "-" | "~" | "*" | "&", [ "mut" ] ), unary | postfix ;
postfix       = primary, { call | member | tuple_member | index | "?" } ;
call          = "(", [ arguments ], ")" ;
member        = ".", IDENT ;
tuple_member  = ".", INTEGER ;
index         = "[", expression, "]" ;
primary       = literal | value_path | tuple_expr | array_expr | struct_expr |
                block | "(", expression, ")" ;
tuple_expr    = "(", expression, ",", [ arguments ], ")" ;
array_expr    = "[", [ arguments ], "]" ;
struct_expr   = type_path, "{", [ field_init, { ",", field_init }, [ "," ] ], "}" ;
field_init    = IDENT, ":", expression ;

pattern       = "_" | literal | name_pattern | tuple_pattern |
                struct_pattern | reference_pattern ;
name_pattern  = path, [ "(", [ pattern_list ], ")" ] ;
tuple_pattern = "(", pattern, ",", [ pattern_list ], ")" ;
struct_pattern = path, "{", [ struct_pattern_fields ], "}" ;
struct_pattern_fields = field_pattern, { ",", field_pattern },
                        [ ",", ".." ], [ "," ] | "..", [ "," ] ;
field_pattern = IDENT, [ ":", pattern ] ;
reference_pattern = "&", [ "mut" ], pattern ;
pattern_list  = pattern, { ",", pattern }, [ "," ] ;

type          = path_type | tuple_type | array_type | slice_type |
                reference_type | pointer_type | function_type ;
path_type     = type_path, [ "<", type_list, [ "," ], ">" ] ;
tuple_type    = "(", ")" | "(", type, ",", [ type_list ], ")" ;
array_type    = "[", type, ";", ( INTEGER | IDENT ), "]" ;
slice_type    = "[", type, "]" ;
reference_type = "&", [ "mut" ], type ;
pointer_type  = "*", ( "const" | "mut" ), type ;
function_type = "fn", "(", [ type_list ], ")", "->", type ;
path          = IDENT, { "::", IDENT } ;
value_path    = ( IDENT | "self" ), { "::", IDENT } ;
type_path     = ( IDENT | "Self" ), { "::", IDENT } ;
type_list     = type, { ",", type } ;
arguments     = expression, { ",", expression }, [ "," ] ;
literal       = "true" | "false" | INTEGER | FLOAT | CHAR | STRING ;
```

`IDENT/INTEGER/FLOAT/CHAR/STRING/BUILTIN_ATTRIBUTE` 是第 2、3、5 节定义的词法终结符；除此之外实现不得自行补语法。`a < b < c`、`a == b == c` 在 Parser 阶段拒绝。Assignment 先解析左侧表达式，再按 RFC-0006 验证它是否为可写 Place。

## 5. 属性和可见性

- 1.0 只登记 `@repr(...)` 与 `@export(...)`；未知属性报 `X-E1020`；
- `@repr` 只允许结构体、枚举和显式布局类型；`@export` 只允许具有兼容 ABI 的函数；
- 默认 Item/字段为模块私有，`pub(package)` 为包内可见，`pub` 为包外可见；
- 任何新属性必须通过 RFC 登记适用位置、参数语法、重复规则和语义阶段。

## 6. 诊断

`X-E1xxx` 专用于词法和语法。Rule ID 使用 `RULE-LEX-*`、`RULE-SYN-*`，不得把 Rule ID 当诊断码复用。

## 7. 验收语料

- compile-pass：31 个关键字上下文、`pub(package)`、tuple `.0`、尾逗号和合法结构模式；
- compile-fail：比较链、相等链、非尾部/重复 `..`、未知属性、嵌套导入和非法 UTF-8；
- AST Snapshot：赋值左侧保留普通表达式树，属性和可见性节点唯一；
- 诊断 Snapshot：每个 `X-E1xxx` 固定主 Span、标签和可选 Fix-it；
- `parse → format → parse` AST 等价，Formatter 二次执行零差异。

## 8. 非目标

本 RFC 不定义所有权、错误传播、名称解析或宏；分别由 RFC-0006～0008、0001 和后续扩展负责。
