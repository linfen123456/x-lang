# RFC-0010：JSON 数据模型、Codec 与规范化输出

> 状态：Proposed
> 日期：2026-08-18
> 目标阶段：P2/P3 官方 `x-codec` 包
> 依赖：RFC-0007、RFC-0008、RFC-0009
> 相关需求：`XLF-09-002`、`XLF-12-010`
> 正式产物：接受后生成 `specs/library/json.md`。

## 1. 摘要

JSON 是官方 Codec，不是核心语法，也不是普通同质 `Map<String, V>` 的别名。本提案分别定义动态数据模型、拥有型/借用型/流式解码、资源限制和 Canonical Output。

## 2. 动态数据模型

```x
pub enum JsonValue {
    Null,
    Bool(Bool),
    Number(JsonNumber),
    String(String),
    Array(Vec<JsonValue>),
    Object(OrderedMap<String, JsonValue>),
}
```

递归容器通过 `Vec`/`OrderedMap` 的拥有型分配间接表示，类型本身具有有限布局。Object 使用 `OrderedMap` 保留输入顺序以改善诊断和 round-trip 体验，但该顺序不构成规范化输出。

`JsonNumber` 保存合法 JSON 数字的精确十进制语义与规范化所需信息，不接受 NaN、Infinity 或前导零等非法形式。`to_i64/to_u64/to_f64` 均为受检查转换；超范围、非整数或精度损失不得静默发生。

## 3. 解码接口

```x
pub fn decode<T>(input: &Str, limits: DecodeLimits) -> Result<T, JsonError>;
pub fn decode_borrowed<T>(input: &Str, limits: DecodeLimits) -> Result<T, JsonError>;
pub fn stream(reader: &mut Reader, limits: DecodeLimits) -> JsonStream;
```

- `decode` 产生拥有型结果，输入在返回后可释放；
- `decode_borrowed` 允许结果中的 `&Str`/`&[U8]` 指向输入，其推导生命周期不得长于输入；
- `stream` 以事件或逐项解码提供有界内存处理，调用者必须消费或显式跳过当前值；
- 三条路径使用同一词法、数字、重复键和错误位置规则；
- 静态 `T` 解码由显式 Codec Trait/登记生成物提供，不依赖运行时反射。

## 4. Object 与重复键

默认策略是 `RejectDuplicate`，错误同时指出首次与重复键 Span。兼容旧系统时可以显式选择 `KeepFirst` 或 `KeepLast`，该策略必须出现在调用配置、日志和测试中；安全敏感配置与 Canonical Output 强制拒绝重复键。

键比较基于解码后的 Unicode Scalar Sequence；不同转义写法解码为同一键时视为重复。解析器不执行 Unicode Normalization，避免静默改变数据。

## 5. 资源限制

`DecodeLimits` 至少包含：

```text
maximum input bytes
maximum nesting depth
maximum string bytes
maximum number characters
maximum array items
maximum object members
maximum total allocated bytes
```

默认值必须有限且适合不可信网络输入；“无限制”只能由显式受审计配置启用。超限返回结构化 `JsonError::LimitExceeded`，不能 panic、无限递归或继续分配。

## 6. 编码与 Canonical Output

```x
pub fn encode<T>(value: &T) -> Result<String, JsonError>;
pub fn encode_to<T>(writer: &mut Writer, value: &T) -> Result<Unit, JsonError>;
pub fn encode_canonical<T>(value: &T) -> Result<Bytes, JsonError>;
```

- 普通 `encode` 保留 Object 的逻辑顺序，但不承诺字节适合签名；
- `encode_canonical` 使用版本化、RFC 8785 兼容的 Canonical Profile：拒绝重复键，按该 Profile 的键序、字符串转义和数字格式输出 UTF-8；
- 不能无损满足 Canonical Number Profile 的 `JsonNumber` 返回 `NonCanonicalNumber`，不得舍入后签名；
- 不改变 Unicode Normalization，不输出无意义空白，所有实现对相同值产生相同字节；
- Canonical Output 重新排序 Object，绝不读取 HashMap 或插入顺序作为签名顺序。

具体外部标准版本、勘误锚点和兼容语料必须在 RFC 接受前锁定；升级 Canonical Profile 需要新版本和迁移规则，不能静默改变签名字节。

## 7. 字面量与生成

1.0 不提供 JSON Literal。未来若研究，使用与 Map 不同的 `json { ... }` 上下文，并要求每个插值显式满足 JSON Codec；不得复用 `%{}` 或依靠期望类型在 Map/JSON 间切换。

结构体 Codec 的自动生成属于后续受限 Derive/Generator RFC，必须声明输入、输出、工具版本、SourceMap 和资源预算。1.0 可以手写或由外部登记生成工具提供 Codec Trait 实现。

## 8. 诊断、安全与验收

- 错误包含稳定 Kind、字节 Span、JSON Pointer 路径和资源限制名称；不回显大段秘密输入；
- compile-pass/fail：拥有型与借用型结果、借用逃逸和 Codec Trait 缺失；
- AST/HIR Snapshot：`decode/decode_borrowed/stream/encode_canonical` 均保持普通路径与调用表达式，仅带类型参数的 API 记录泛型实参，不产生 JSON Literal 专用 AST；HIR 记录 Codec Trait 选择和输入生命周期来源；
- 诊断 Snapshot：Codec Trait 缺失使用 `X-E3010`，Borrowed 结果逃逸复用 `X-E4004`，并固定类型、输入来源和建议的拥有型替代；
- 解析语料：重复键、深度炸弹、超长字符串、巨大数字、非法 UTF-8/转义和截断输入；
- Streaming：分块边界穷举、部分读取、取消和 Reader 错误；
- Canonical Golden：键序、数字、Unicode、转义和跨平台确定字节；
- Fuzz/差分：三条解码路径结果一致，外部实现差异必须分类；
- 边界反例：重复键、深度炸弹、巨大数字、非规范 Unicode/转义、Borrowed 逃逸和 Canonical Bytes 差异必须分别命中确定策略；
- 性能只记录环境、数据、吞吐、分配和尾延迟，不作无证据倍数声明。
