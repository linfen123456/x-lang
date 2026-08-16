---
doc_id: DOC-SPECS-LANGUAGE-CORE
title: X-Lang 核心语言规范（词法、语法、类型与模块）
authority: normative
owner: role/language-council
backup_owner: role/compiler-team
version: "0.2"
maturity: CORE
status: 草案
phase: P0
last_reviewed: 2026-08-16
applies_to: [x-source, lexer, parser, resolver, type-checker, hir]
traceability_scope: [XLF, XLC, XLE]
supersedes: [DOC-SPECS-LANGUAGE-CORE-LEGACY]
---

# X-Lang 核心语言规范

## 1. 状态、目标与术语

这是 P0–P2 的规范初稿。核心方向是无 GC 默认模式、所有权+借用+RAII、显式转换、可移植结果语义和 Rust+LLVM 初始实现；完整 Trait 求解、高级宏、comptime、动态反射和异步语法仍须单独 RFC。

术语：程序是一个包及其依赖的编译单元；模块是名字和可见性作用域；值是具有静态类型的运行时数据；place 是可被读取或写入的位置；移动使源 place 失效；借用是在受限生命周期内通过引用访问 place；panic 是非正常控制流失败；UB 是规范禁止程序依赖的行为。

## 2. 词法

### RULE-LANG-001：源文件编码与偏移

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 实现必须将源文件按 UTF-8 字节序列读取；可选 UTF-8 BOM 必须被忽略且不得成为 token。非法 UTF-8 必须拒绝。源码位置必须同时保留字节偏移、行号和 UTF-8 标量列号；换行统一识别 LF、CRLF 和 CR，但诊断输出应保留原始行尾风格。

**解释。** 字节偏移用于工具协议和重放，标量列号用于诊断。禁止用 U+FFFD 静默替换非法输入。

**正例。** let café = 1 合法。

**反例。** 出现 0xFF 必须报告 X-E1001 invalid UTF-8。

**边界。** BOM 只允许在文件起始处；行尾转换不得改变 token 的 byte span。

**诊断/测试/追溯。** X-E1001、X-E1002；TEST-LANG-LEX-001（pass）、TEST-LANG-LEX-002（fail）、TEST-LANG-LEX-003（boundary）；来源 XLF-01-001、XLC-CORE-010；RFC：无。

### RULE-LANG-002：空白、注释与文档注释

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 空格、制表、换行和注释仅起分隔作用。行注释从 // 到行尾；块注释使用 /* ... */ 且支持嵌套深度至少 128，未闭合必须拒绝。/// 和 /** ... */ 作为附着元数据保留，但不得改变程序语义。

**解释。** 保留注释支持 xdoc 和诊断；注释不是可执行宏。

**正例。** let x/* inner /* nested */ */=1 合法。

**反例。** let x = 1 /* 报告 X-E1003 unterminated comment。

**边界。** 字符串内部的 // 不是注释；超过实现上限必须报告 X-E1004，不得栈溢出。

**诊断/测试/追溯。** X-E1003、X-E1004；TEST-LANG-LEX-004、005；来源 XLF-01-001；RFC-CORE-LEX-01（文档元数据，P1）。

### RULE-LANG-003：标识符、关键字与最长匹配

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 标识符由 Unicode XID_Start 后跟 XID_Continue 组成，允许 ASCII 下划线；大小写敏感，词法阶段不自动 Unicode 正规化。关键字为 as、async、await、break、const、continue、defer、else、enum、extern、false、fn、for、if、impl、in、let、loop、match、mod、move、mut、panic、pub、return、self、struct、trait、true、type、unsafe、use、while。关键字不得作普通标识符，Lexer 必须最长匹配。`async/await` 即使 feature 未启用也按关键字识别，由语义阶段报告 feature-disabled，避免不同 Profile 产生不同 Token 流。

**解释。** defer 先保留为候选关键字，是否进入稳定语义由 RULE-LANG-013 的 RFC 决定。

**正例。** let mut café_2 = true 合法；a==b 识别为 a、==、b。

**反例。** let = 3 报告 X-E1005 keyword as identifier。

**边界。** Unicode 混淆字符只产生安全 lint，不改变合法性；原始标识符语法待 RFC。

**诊断/测试/追溯。** X-E1005、X-E1006；TEST-LANG-LEX-006、007；来源 XLF-01-002、XLC-CORE-001；RFC-CORE-LEX-02（P1）。

### RULE-LANG-004：字面量

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 整数支持十进制、0b、0o、0x 和下划线分隔；浮点必须有小数点或指数；布尔为 true/false；字符用单引号，字符串用双引号，转义至少包括反斜杠、换行、回车、制表、空字符、引号、十六进制和 Unicode 标量。原始字符串、插值和 decimal 不是 P0 核心。字面量超出目标类型必须报错或要求显式宽类型。

**解释。** 字面量先形成无类型候选，再由上下文确定类型；HIR 必须记录最终类型。

**正例。** let n: u32 = 0xff_ff; let c: char = '\u{1F600}'。

**反例。** let n: u8 = 256 报 X-E1010；非法转义报 X-E1011。

**边界。** -128 是负号与 128 的组合；NaN/Infinity 只能通过标准库或 RFC。

**诊断/测试/追溯。** X-E1010、X-E1011；TEST-LANG-LIT-001..003；来源 XLF-10-004、XLC-CORE-010；RFC-CORE-NUM-01（P2）。

## 3. EBNF 与语法

以下 EBNF 是 P0 参考语法；ε 表示空。大写词法名由 lexer 产生，且不属于可由 parser 自由扩展的非终结符。递归下降+Pratt 或等价解析器必须产生相同 AST。

~~~ebnf
program        = { item } ;
item           = outer_attrs ( import | module | struct | enum | trait | impl | function | const_decl | type_alias ) ;
outer_attrs    = { attribute } ;
attribute      = "#[" attr_name [ "(" attr_args ")" ] "]" ;
attr_name      = IDENT { "::" IDENT } ;
attr_args      = attr_arg { "," attr_arg } [ "," ] ;
attr_arg       = IDENT [ "=" literal ] | literal ;
import         = "use" path [ "as" IDENT ] ";" ;
module         = "mod" IDENT ( ";" | "{" { item } "}" ) ;
struct         = [ "pub" ] "struct" IDENT [ generic_params ] "{" { field } "}" ;
field          = [ "pub" ] IDENT ":" type "," ;
enum           = [ "pub" ] "enum" IDENT [ generic_params ] "{" { variant } "}" ;
variant        = IDENT [ "(" type_list ")" | "{" { field } "}" ] "," ;
trait          = [ "pub" ] "trait" IDENT [ generic_params ] [ ":" bounds ] "{" { function_sig | type_item } "}" ;
impl           = "impl" [ generic_params ] impl_head "{" { function | type_item } "}" ;
impl_head      = type [ "for" type ] ;
function       = [ "pub" ] [ "async" ] [ "unsafe" ] [ extern_abi ] "fn" IDENT [ generic_params ] "(" [ params ] ")" [ "->" type ] block ;
function_sig   = [ "async" ] [ "unsafe" ] [ extern_abi ] "fn" IDENT "(" [ params ] ")" [ "->" type ] ";" ;
extern_abi     = "extern" STRING ;
const_decl     = [ "pub" ] "const" IDENT ":" type "=" expr ";" ;
type_alias     = [ "pub" ] "type" IDENT [ generic_params ] "=" type ";" ;
type_item      = "type" IDENT [ ":" bounds ] ";" ;
params         = param { "," param } [ "," ] ;
param          = receiver | [ "move" ] IDENT ":" type ;
receiver       = "self" | "mut" "self" | "&" [ LIFETIME ] [ "mut" ] "self" ;
args           = arg { "," arg } [ "," ] ;
arg            = [ IDENT "=" ] expr ;
type_list      = [ type { "," type } [ "," ] ] ;
bounds         = path { "+" path } ;
generic_params = "<" generic_param { "," generic_param } [ "," ] ">" ;
generic_param  = LIFETIME | IDENT [ ":" bounds ] ;
generic_args   = "<" type { "," type } [ "," ] ">" ;
path           = [ "::" ] IDENT { "::" IDENT } ;
type           = never | primitive | path [ generic_args ] | "(" type_list ")" | "[" type "]" | "[" type ";" expr "]" | "&" [ LIFETIME ] [ "mut" ] type | "*" ( "const" | "mut" ) type | "fn" "(" type_list ")" "->" type ;
never          = "!" ;
primitive      = "bool" | "char" | "str" | "i8" | "i16" | "i32" | "i64" | "i128" | "isize" | "u8" | "u16" | "u32" | "u64" | "u128" | "usize" | "f32" | "f64" ;
block          = "{" { statement } [ expr ] "}" ;
statement      = let_stmt | expr_stmt | return_stmt | break_stmt | continue_stmt | item ;
let_stmt       = "let" [ "mut" ] pattern [ ":" type ] [ "=" expr ] ";" ;
expr_stmt      = expr ";" ;
return_stmt    = "return" [ expr ] ";" ;
break_stmt     = "break" [ expr ] ";" ;
continue_stmt  = "continue" ";" ;
expr           = assignment ;
assignment     = pipeline [ assign_op assignment ] ;
assign_op      = "=" | "+=" | "-=" | "*=" | "/=" ;
pipeline       = logical_or { "|>" logical_or } ;
logical_or     = logical_and { "||" logical_and } ;
logical_and    = equality { "&&" equality } ;
equality       = comparison { ( "==" | "!=" ) comparison } ;
comparison     = additive { ( "<" | "<=" | ">" | ">=" ) additive } ;
additive       = multiplicative { ( "+" | "-" ) multiplicative } ;
multiplicative = cast { ( "*" | "/" | "%" ) cast } ;
cast           = unary { "as" type } ;
unary          = ( "!" | "-" | "&" | "*" ) unary | postfix ;
postfix        = primary { call | index | member | await_suffix | "?" } ;
call           = "(" [ args ] ")" ;
index          = "[" expr "]" ;
member         = "." IDENT ;
await_suffix   = "." "await" ;
primary        = literal | tuple_or_group | array_expr | struct_expr | panic_expr | path | block | unsafe_block | async_block | if_expr | match_expr | loop_expr | closure ;
tuple_or_group = "(" [ expr { "," expr } [ "," ] ] ")" ;
array_expr     = "[" [ expr { "," expr } [ "," ] ] "]" ;
struct_expr    = path "{" [ field_init { "," field_init } [ "," ] ] "}" ;
field_init     = IDENT [ ":" expr ] ;
panic_expr     = "panic" "(" expr ")" ;
unsafe_block   = "unsafe" block ;
async_block    = "async" [ "move" ] block ;
if_expr        = "if" expr block { "else" "if" expr block } [ "else" block ] ;
match_expr     = "match" expr "{" { pattern [ "if" expr ] "=>" expr "," } "}" ;
loop_expr      = "loop" block | "while" expr block | "for" pattern "in" expr block ;
closure        = [ "async" ] [ "move" ] "|" [ closure_params ] "|" ( expr | block ) ;
closure_params = closure_param { "," closure_param } [ "," ] ;
closure_param  = IDENT [ ":" type ] ;
pattern        = "_" | literal | IDENT | tuple_pattern | struct_pattern | variant_pattern ;
tuple_pattern  = "(" [ pattern { "," pattern } [ "," ] ] ")" ;
struct_pattern = path "{" [ field_pattern { "," field_pattern } [ "," ] ] "}" ;
field_pattern  = IDENT [ ":" pattern ] ;
variant_pattern= path [ "(" [ pattern { "," pattern } [ "," ] ] ")" ] ;
literal        = INT | FLOAT | CHAR | STRING | "true" | "false" ;
IDENT          = /* Unicode XID_Start/XID_Continue 或 ASCII _，见 RULE-LANG-003 */ ;
INT            = /* 整数 token，见 RULE-LANG-004 */ ;
FLOAT          = /* 浮点 token，见 RULE-LANG-004 */ ;
CHAR           = /* 字符 token，见 RULE-LANG-004 */ ;
STRING         = /* 字符串 token，见 RULE-LANG-004 */ ;
LIFETIME       = /* 单引号后接非关键字 IDENT，例如 'a；字符字面量由 Lexer 优先识别为 CHAR */ ;
~~~

### RULE-LANG-005：解析与优先级

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 调用/索引/成员最高，乘除高于加减，比较高于逻辑与，逻辑与高于逻辑或，管道低于逻辑表达式，赋值最低且右结合。赋值左侧必须是可写 place；语句分号不可省略，块尾表达式可省略分号并成为块值。

**解释。** 块值让 if、match 和闭包可组合；管道仅为语法糖，P0 只允许将左值作为首个位置参数。

**正例。** let y = x + 2 * f() 先调用/乘法再加法。

**反例。** 1 = x 报 X-E1101 assignment target；f(a b) 报 X-E1102 expected comma。

**边界。** Parser 必须在分号、右花括号或 item 起始有限恢复；错误节点不能代码生成。

**诊断/测试/追溯。** X-E1101、X-E1102；TEST-LANG-PARSE-001..004；来源 XLF-02-002、XLF-11-003、XLC-CORE-001；RFC-CORE-SYNTAX-01（P1）。

### RULE-LANG-006：声明、作用域与可见性

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** let 默认不可变，let mut 才可赋值。块、函数、模块和模式各自产生词法作用域；内层可遮蔽外层，同一作用域重复定义必须拒绝。顶层默认私有，pub 才能导出；use 不改变被导出项的所有权。

**解释。** 遮蔽创建新 DefId，不是重新赋值；未初始化绑定不可读。

**正例。** let x=1; { let x=2; print(x); } print(x)。

**反例。** 对不可变 x 赋值报 X-E1201；同层重复定义报 X-E1202。

**边界。** 模块初始化和循环依赖由包规则确定；pub(crate) 等细粒度可见性待 RFC。

**诊断/测试/追溯。** X-E1201、X-E1202、X-E1203；TEST-LANG-SCOPE-001..003；来源 XLF-02-002、XLC-CORE-018；RFC-CORE-MODULE-01（P1）。

## 4. 类型系统与推断

### RULE-LANG-007：静态类型与显式转换

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 每个表达式和 place 必须有编译期确定的类型；赋值、参数、返回和分支结果必须相容。布尔、整数、浮点、字符串、指针/引用之间禁止隐式转换；窄化、解析和可能失败转换必须显式调用 API。底类型 ! 可作为任何需要值的位置但不能构造。

**解释。** 类型安全优先于便利；不同宽度转换的溢出策略必须由 API 名称表达。

**正例。** `let n: u32 = u16_value as u32; let id: u64 = text.parse()?;`。调用结果的显式类型为泛型解析提供约束，不引入尚未定义的尖括号调用语法。

**反例。** let n: i32 = true 报 X-E2001 incompatible types。

**边界。** 无类型数字默认 i32/f64；子类型系统不进入 P0。

**诊断/测试/追溯。** X-E2001、X-E2002；TEST-LANG-TYPE-001..004；来源 XLF-02-004、XLF-10-004、XLC-CORE-010；RFC-CORE-NUM-01（P2）。

### RULE-LANG-008：类型推断、泛型与 Trait 约束

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 推断只使用局部约束、显式签名、泛型参数和已导入 Trait，不得根据运行时值推断类型。泛型参数必须在声明中出现或由上下文唯一确定；Trait bound 必须满足，歧义、递归超限和冲突实现必须拒绝。P2 一致性规则为：同一 crate 只能为本地 Trait 或本地类型提供实现，除非 RFC 放宽。

**解释。** 这是最小局部约束加名义 Trait 选择，不承诺全部 GAT/HRTB/Specialization。编译器应显示约束来源。

**正例。** fn id<T>(x:T)->T { x }；fn show<T: Printable>(x:&T){ x.print(); }。

**反例。** T 缺少方法报 X-E2101；两个实现匹配报 X-E2102。

**边界。** 单态化、动态分派和对象安全属实现/ABI；求解超限报 X-E2103，不能失控。

**诊断/测试/追溯。** X-E2101..2103；TEST-LANG-TRAIT-001..005；来源 XLF-02-008、XLC-CORE-004..009；RFC-TRAIT-01（P2，终止性/对象安全/代码体积）。

### RULE-LANG-009：数值与浮点

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 有符号整数为规定宽度二进制补码；无符号整数按模 2^N。检查 profile 检测溢出并报告 X-R3001；release 策略必须由 RFC 决定，程序不得依赖 LLVM poison/UB。浮点为 IEEE 754 binary32/binary64，NaN 比较遵循 IEEE，total order 使用显式 API。

**解释。** decimal32/64/128 是标准库/扩展候选，不是 P0 原生类型。整数、NaN、FMA 和严格/快速模式的决策门见[求值与 UB 规范](./evaluation-and-ub.md)。

**正例。** u8::wrapping_add(a,b)；f64::total_cmp(a,b)。

**反例。** u8 的 255+1 在检查 profile 报 X-R3001。

**边界。** FMA、fast-math、SIMD、舍入和端序必须由 target/profile 开启；strict 模式才提供跨后端相同结果。

**诊断/测试/追溯。** X-R3001、X-E2004；TEST-LANG-NUM-001..006；来源 XLC-CORE-011、XLC-CORE-019、XLE-DATA-006；decimal 扩展来源 XLF-10-004，但不由本条实现；RFC-NUM-01（P1 差分）。

### RULE-LANG-010：复合类型与布局

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 数组为 [T;N]；切片由指针+长度表示但 ABI 仅在 repr(C)/FFI 条文中稳定；元组、结构体、枚举访问必须类型检查。默认布局由实现选择，安全代码不能观察 padding/字段偏移；repr(C)、对齐和 packed 需显式属性与 unsafe 前置条件。

**解释。** 优化器可重排私有布局，FFI 使用显式稳定边界。

**正例。** let p:(i32,bool)=(1,true); let a:[u8;4]=[0,1,2,3]。

**反例。** 普通 struct 强转 C 结构体报 X-E2301；越界报 X-R3002。

**边界。** 零长数组、未初始化、packed 引用和 provenance 见 RFC-ABI-01。

**诊断/测试/追溯。** X-E2301、X-R3002；TEST-LANG-TYPE-006..009；来源 XLC-CORE-010..013；RFC-ABI-01（P2）。

## 5. 模式、函数和控制流

### RULE-LANG-011：模式匹配与穷尽性

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** match 必须覆盖所有可构造值或包含 _ 兜底；守卫不能替代穷尽性证明。不可达模式至少 warning，重复且无副作用模式可 error。解构绑定遵守 move/borrow 和可见性规则。

**解释。** 穷尽性是静态保证；守卫依赖运行时值不计入覆盖。

**正例。** match r { Ok(x)=>x, Err(_)=>0 } 覆盖 Result。

**反例。** match b { true=>1 } 报 X-E2401；重复模式报 X-W2402。

**边界。** 范围、slice 和自定义穷尽 Trait 属 RFC-PATTERN-01；P1 仅支持基础字面量/枚举/tuple/struct/_。

**诊断/测试/追溯。** X-E2401、X-W2402；TEST-LANG-PATTERN-001..004；来源 XLF-02-005、XLF-11-003；RFC-PATTERN-01（P2）。

### RULE-LANG-012：求值顺序与函数

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 函数实参按源代码从左到右；&&/|| 短路，普通算术不短路。函数返回表达式必须满足返回类型；块尾表达式为返回值，return 提前退出。闭包不得隐式克隆非 Copy 值。

**解释。** 明确顺序避免后端差异；尾调用优化不能改变 Drop 顺序。参数、短路、临时和 cleanup edge 的实现规则见[求值与 UB 规范](./evaluation-and-ub.md)。

**正例。** f({log("a");1},{log("b");2}) 总是先 a 后 b。

**反例。** 返回字符串到 i32 报 X-E2501；`false && panic("unreachable")` 不执行 panic。

**边界。** effect、生成器和并行求值不属于核心；FFI 调用约定见 FFI 文档。

**诊断/测试/追溯。** X-E2501、X-E2502；TEST-LANG-EVAL-001..003；来源 XLF-11-005、XLC-CORE-011、XLC-CORE-019；RFC-EVAL-01（P1）。

## 6. 错误、模块、包与 Edition

### RULE-LANG-013：Result、panic 与清理

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** Result<T,E> 表示可处理失败；问号传播只能用于 E 可转换的返回上下文。panic 表示当前任务无法继续，不得代替输入校验。panic/unwind/abort 由 profile 选择；已初始化 Drop 值必须清理，abort 可不保证全局析构。

**解释。** 错误值与异常控制流分离。defer 只是保留关键字；若接受必须定义与 Drop 的 LIFO 顺序。

**正例。** fn load()->Result<Data,IoError>{ let b=read()?; Ok(parse(b)?) }。

**反例。** 输入校验用 panic 报 X-W2602；extern C 中 unwind 报 X-E2603。

**边界。** 线程 panic 聚合、取消和 backtrace 属并发/运行时 RFC，backtrace 不能泄漏秘密。

**诊断/测试/追溯。** X-E2601、X-E2603；TEST-LANG-ERR-001..006；来源 XLF-03-001、XLF-10-001、XLF-12-012；RFC-ERROR-01（P1）。

### RULE-LANG-014：模块、包、依赖与 Edition

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 包由 x.toml 定义名称、版本、edition 和依赖表；依赖表允许为空，入口按规范默认位置发现或由扩展目标配置显式指定。依赖图必须确定且无循环初始化，锁文件固定结果和来源哈希。模块默认私有，pub 可导出。Edition 隔离解析/类型/语义变化，不改变包版本；当前清单版本未声明 edition 必须拒绝，不得按编译器版本猜测默认值。

**解释。** Edition 是迁移边界。依赖解析、feature、平台条件的完整 Schema 由 XPM 文档定义。

**正例。** x.toml 声明 name、version、edition 和允许为空的 dependencies 表；pub fn api() 可外部引用。

**反例。** 不确定依赖图报 X-E2701；越过私有边界报 X-E2702。

**边界。** registry、撤回、SBOM、签名和离线策略属发布治理；构建脚本不可静默修改已解析源码。

**诊断/测试/追溯。** X-E2701..2703；TEST-LANG-MOD-001..006；来源 XLF-02-002、XLF-11-001、XLC-CORE-018..020；RFC-MODULE-01（P2）。

### RULE-LANG-015：属性、repr 与 feature gate

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** 属性必须绑定到紧邻 item；未知属性必须报错，除非显式启用实验 feature。P0 解析 repr(C)、repr(transparent)、cfg、test 和 allow/warn/deny；repr(C) 只用于 ABI 边界，repr(transparent) 只用于单一字段。未启用的 async、宏、comptime、GPU、GC 和热重载语法必须拒绝。

**解释。** 属性是元数据，不能通过字符串改变类型或所有权。Stable 默认关闭实验功能。

**正例。** repr(C) struct CPoint { x: i32, y: i32 }。

**反例。** Stable 中使用 async feature 报 X-E2801 feature not enabled。

**边界。** 重复属性、未知 cfg target 和 packed 布局由属性校验器报告；不能静默选择。

**诊断/测试/追溯。** X-E2801、X-E2802；TEST-LANG-ATTR-001..006；来源 XLF-02-006、XLF-06-006、XLC-CORE-010；RFC-ATTR-01（P1）。

### RULE-LANG-016：显式 cast、问号、never 与 raw pointer

- maturity: EXTENDED
- status: 草案
- phase: P2

**规范性条文。** as、问号和 never 是 CORE 候选：as 只允许安全 widening 或显式 trait 转换；窄化必须使用 checked Result；问号只可用于 Option/Result 并传播 None/Err；never 类型 ! 只能由发散表达式产生。raw pointer 类型 *const T 与 *mut T、unsafe 解引用及 Ghost Memory 诊断属于 EXTENDED/P2，必须由 RFC-ABI-01 和 feature gate 启用；指针解引用、偏移、读写必须满足 provenance、alignment、initialization、bounds。

**解释。** 允许底层语法但不放宽安全默认；问号先做 residual 转换再返回。

**正例。** small as u64；fallible()?；unsafe 中读取已验证指针。

**反例。** 未检查窄化报 X-E2803；安全上下文解引用报 X-E2804。

**边界。** 指针整数往返、volatile、MMIO 和 extern memory 由 RFC-ABI-01 定义。

**诊断/测试/追溯。** X-E2803、X-E2804、X-E2805；TEST-LANG-CAST-001..008；来源 XLF-05-003、XLF-06-006、XLC-CORE-010..013；RFC-ABI-01（P2）。

### RULE-LANG-017：extern 声明和 C 调用边界

- maturity: EXTENDED
- status: 草案
- phase: P3

**规范性条文。** extern item 必须给出 ABI、签名和 unsafe 要求；首个互操作原型只验证 extern C，不在 P0/P1 承诺稳定 ABI。extern 调用默认为 unsafe，除非由审计过的 safe wrapper 封装。panic、Result 内部表示和引用 lifetime 不得隐式穿越 C 边界；repr(C) 与 ptr+len 必须显式。只有 RFC-FFI-C-01、ABI golden 和跨平台测试通过后，相关语法与实现才可从 feature gate 晋级。

**解释。** extern 是声明，不验证外部实现；符号、调用约定和平台库由 FFI manifest 约束。

**正例。** extern C 声明 ptr+len 函数，并由 wrapper 检查 null、长度和 UTF-8。

**反例。** 导出 String 或允许 unwind 穿越 extern 报 X-E2806。

**边界。** stdcall/vectorcall、动态符号和 C++ shim 属 Extended；缺失符号必须链接失败。

**诊断/测试/追溯。** X-E2806、X-E2807；TEST-LANG-FFI-001..006；来源 XLF-01-013、XLF-11-005、XLC-FFI-001..005；RFC-FFI-C-01（P3）。

### RULE-LANG-018：async 语法 feature gate

- maturity: EXTENDED
- status: 草案
- phase: P3

**规范性条文。** async fn、async block、await 和 async closure 只有在 async feature 与 runtime profile 同时启用时解析；否则报 X-E2810。启用后 async fn 返回 Future，await 只能在 async context，Future 的 Pin、取消、waker 和 Drop 遵守内存并发规范。

**解释。** 保留语法用于 P3 原型，不承诺 M:N executor 或网络取消。编译器可生成状态机，runtime 由 profile 选择。

**正例。** async profile 中 async fn fetch() -> Result<Data, Error> { client.get(url).await? }。

**反例。** Stable 普通函数中写 await，报告 X-E2810。

**边界。** no_std async 可需手工 executor；阻塞检测、select 和 async trait 由唯一决策 `RFC-ASYNC-001` 决定。

**诊断/测试/追溯。** X-E2810、X-E2811；TEST-LANG-ASYNC-001..008；来源 XLF-05-006、XLF-10-004、XLC-CORE-014..015；`RFC-ASYNC-001` 当前待决策，必须在 P2 async 实施切片启动前完成决策，能力实现与稳定化仍在 P3。

### RULE-LANG-019：panic、unwind、abort 与溢出 profile

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** panic 进入当前 task 的终止状态并携带脱敏 payload；unwind 按栈帧逆序运行已初始化 Drop，再将 panic 传播到明确的 join/线程边界。abort 在完成当前安全边界后终止进程，不承诺全局析构、其他 task 或 FFI 清理。panic 不得穿越 extern C；线程或 task 的传播必须由父级 policy 接收、聚合或显式记录。checked、release 和 wrapping 溢出 profile 必须分别规定：checked 报告 X-R3001，release 采用 manifest 声明的确定策略，wrapping 按 2^N 模运算；禁止依赖后端未定义行为。

**解释。** profile 是构建输入而非运行时猜测；unwind 清理只覆盖语言可达 owner，操作系统强制终止不在保证内。

**正例。** profile=checked 时 `u8::add(255,1)` 返回 panic 诊断；C wrapper 将 panic 转为 XStatus 后返回。

**反例。** 让 X panic 直接 unwinding 到 C caller，或在 release 中依赖 LLVM poison，报告 X-E2820。

**边界。** panic hook、backtrace、信号、OOM 和宿主 terminate 由 runtime profile 补充；不得把 hook 当作恢复机制。

**诊断/测试/追溯。** X-E2820、X-R3001；TEST-LANG-PANIC-001..008；来源 XLF-10-001、XLF-10-003、XLF-12-014、XLC-CORE-011；RFC-ERROR-01（P1）。

### RULE-LANG-020：清单、Edition 与依赖解析

- maturity: CORE
- status: 草案
- phase: P0

**规范性条文。** x.toml 最小必须包含 package.name、package.version、package.edition、[dependencies]；没有外部依赖时 `[dependencies]` 允许为空。缺失 edition 必须产生 X-E2831 并拒绝构建，禁止按编译器版本猜测。解析顺序固定为清单、锁文件、registry/source、feature/cfg，再进行模块解析；锁文件必须记录精确版本、来源和 hash。依赖图中的循环必须在解析阶段拒绝；同一 feature 解析结果必须可重现。

**解释。** Edition 选择语法和语义规则，不改变包版本；cfg 只能来自受信 manifest/target，不得由源码隐式改写依赖图。

**正例。** CI 使用提交的 lockfile 和明确 `--target/--features`，生成与本地相同的解析图。

**反例。** 两次构建从浮动 registry 取得不同版本，或循环初始化被静默排序，报告 X-E2830。

**边界。** registry 撤回、签名、SBOM 和离线缓存属于发布治理；构建脚本不得修改 lockfile 而不留下诊断。

**诊断/测试/追溯。** X-E2830、X-E2831；TEST-LANG-MOD-007..012；来源 XLF-11-001、XLC-CORE-018..020；RFC-MODULE-01（P2）。

## 7. 待决事项总表

| RFC | 候选与保守默认 | 决策门禁 | 最迟阶段 |
|---|---|---|---|
| RFC-CORE-LEX-02 | 保守 Unicode；原始标识符可选 | Unicode 安全、round-trip | P1 |
| RFC-CORE-NUM-01 | 二进制浮点；decimal 为库/扩展 | IEEE/跨后端/舍入 | P2 |
| RFC-TRAIT-01 | 局部一致性、终止求解 | 冲突、对象安全、代码体积 | P2 |
| RFC-PATTERN-01 | 基础模式稳定；范围/slice 待扩展 | 穷尽性算法和迁移 | P2 |
| RFC-EVAL-01 | 左到右、短路；effect 待研究 | MIR 语义和重排证明 | P1 |
| RFC-ERROR-01 | Result+panic，unwind/abort profile | Drop/FFI/资源证据 | P1 |
| RFC-MODULE-01 | 清单+锁文件+Edition | 确定解析、N-1/N-2 迁移 | P2 |
| RFC-ABI-01 | 非 repr 布局不稳定，C ABI 显式 | ABI goldens、provenance | P2 |
| RFC-META-01 | P0 仅接受无需执行用户代码的常量；宏/comptime 默认关闭 | 阶段顺序、确定输入、CPU/内存/递归预算、卫生与 Span、过程能力沙箱、缓存键和生成代码追溯；来源 XLF-01-008、XLF-10-012、XLC-CORE-001、XLC-CORE-002、XLC-CORE-003 | P2 |

RFC 未通过前可有 feature-gate 原型，但不得把原型示例当作 CORE 语义。
