---
doc_id: DOC-STDLIB-TEXT-TIME-SECURITY-DATA
authority: normative
owner: role/standard-library
backup_owner: role/security-team
version: "0.1"
maturity: EXTENDED
status: 草案
phase: P3
last_reviewed: 2026-08-15
traceability_scope: [XLF, XLC, XLE, SECURITY]
---
# X-Lang 文本、时间、安全、序列化与数据标准库实施规范

> 文档性质：候选规范（Normative Draft）
> 成熟度：文本基础 `CORE`，时间与序列化 `EXTENDED`，认证/数据库/列式数据 `EXTENDED`，PQC 与编译期 SQL `EXPERIMENTAL`
> 权威入口：[标准库索引](./README.md)｜[核心 API](./core-api.md)｜[测试策略](../testing/test-strategy.md)

## 1. 目标与非目标

本文把 Unicode 文本、日期时间、随机数、密码学、配置、序列化、Schema 演进、数据库、Arrow/Parquet 与流式 ETL 整理为可实现的库契约。重点是数据边界明确、错误可恢复、版本可迁移、资源有上限，而不是把每种格式和框架塞进语言核心。

本文不自创 Unicode、时区、密码和列式存储标准；不宣称某算法“绝对安全”；不把 ORM、JWT、数据库驱动、PQC、Tensor 或媒体编解码放入 Prelude。具体第三方实现要经过许可证、漏洞和互操作审查。

## 2. 包分层

| 包 | 成熟度/阶段 | 责任 |
|---|---|---|
| `core::char`、`alloc::string`、`alloc::bytes` | CORE/P2 | Unicode Scalar、UTF-8 String、原始字节 |
| `std::text`、`std::time`、`std::random` | EXTENDED/P3 | 文本算法、时钟、时区入口、随机源 |
| `x-codec-*` | EXTENDED/P3 | JSON/YAML/TOML/CSV/MessagePack/Protobuf 适配 |
| `x-crypto`、`x-auth` | EXTENDED/P3-P4 | 成熟 Provider、TLS 所需原语、JWT/RBAC/Session |
| `x-db` | EXTENDED/P3-P4 | 驱动接口、连接池、事务、迁移、离线 Schema |
| `x-data-columnar`、`x-data-loader` | EXTENDED/P4 | Arrow、Parquet、批量与流式数据 |
| `x-crypto-pqc`、编译期 SQL | EXPERIMENTAL/P4+ | 标准跟踪、独立审计、离线检查 |

## 3. Unicode、字符串与文本处理

### 3.1 不变量与索引

`String` 和 `str` 始终是合法 UTF-8；`Bytes` 不承诺文本含义。`char` 表示 Unicode Scalar Value，不等于用户可见字符。字符串按字节、Scalar、Grapheme、行分别提供迭代器，API 名称必须说明使用哪一种单位。

```x
fn as_bytes(&self) -> &[u8]
fn chars(&self) -> Chars
fn graphemes(&self, data: &UnicodeData) -> Graphemes
fn slice_bytes(&self, range: Range<usize>) -> Result<&str, TextBoundaryError>
```

字符串不提供未经检查的整数下标。字节切片的首尾必须位于 UTF-8 边界；用户界面光标应使用 Grapheme，而协议长度通常使用字节。大小写转换和规范化可能改变长度，调用者不得预分配固定等长缓冲。

### 3.2 Unicode 数据版本

编译器、标准库、格式化器和正则包必须记录 Unicode 数据版本。升级数据可能改变分类、分词、规范化和标识符安全检查，需在 Edition/库版本发布说明中列出。稳定程序可锁定数据版本；不得依赖宿主 OS 未记录的区域设置得到可复现结果。

### 3.3 正则与国际化

运行时正则默认使用可证明线性时间或有明确回溯预算的实现；输入、模式、状态数和执行时间均有限制。常量模式可在 P3 编译为 DFA，但超过体积预算时回退运行时编译并诊断，不得导致制品无限膨胀。

国际化包负责 locale、消息目录、复数、性别、格式化和回退链。消息键稳定，翻译文本不是程序控制流。缺少 locale 数据时返回明确回退信息；安全日志仍使用稳定机器码。

## 4. 时间、日期、时区与调度

### 4.1 三种时间类型

```x
struct Duration { /* signed/unsigned choice pending RFC */ }
struct Instant { /* monotonic, opaque */ }
struct SystemTime { /* wall clock */ }
```

`Instant` 只用于测量间隔和 deadline，不能序列化成跨进程绝对时间；`SystemTime` 可回拨或跳变，不能驱动超时。日历时间由 `Date/LocalDateTime/ZonedDateTime` 官方包提供，并携带时区标识和规则版本。

### 4.2 时区、闰秒和歧义

本地时间转换可能得到唯一、歧义或不存在三种结果，API 不得擅自选择：

```x
enum LocalResolution<T> { Unique(T), Ambiguous(T, T), Missing(Gap) }
```

时区数据库升级需要可追溯版本。闰秒策略（保留、平滑或拒绝）由运行 Profile 明确。Cron/Timer 使用指定时区与错过策略；进程停机后是否补跑、重复时段运行一次还是两次都必须配置。Leader Election 只是分布式协调工具，不能证明任务 exactly-once，任务自身仍需幂等。

## 5. 随机数、哈希与密码学

随机 API 分为可复现伪随机 `Prng(seed)` 和系统密码随机 `SecureRandom`，二者不能隐式替换。测试固定 seed，生产密钥和 Token 必须使用 `SecureRandom`。熵不足、Provider 不可用或系统调用失败返回错误，禁止退回时间戳种子。

密码学公共 API 遵循 Provider 模式。以下签名是候选形状而非稳定 ABI；RFC 还必须记录所有权、阻塞/取消、复杂度、Provider 平台和密钥驻留位置：

```x
struct AeadKey<A: AeadAlgorithm> {
    provider: ProviderHandle,
    key_id: KeyId,
    parameters: A::Parameters,
    secret: NonExportableSecret,
}
trait AeadAlgorithm {
    type Parameters;
    const ALGORITHM_ID: AlgorithmId;
}
trait Aead<A: AeadAlgorithm> {
    fn seal(&self, key: &AeadKey<A>, nonce: Nonce<A>, aad: &[u8], plaintext: &[u8])
        -> Result<Ciphertext, CryptoError>
    fn open(&self, key: &AeadKey<A>, nonce: Nonce<A>, aad: &[u8], ciphertext: &[u8])
        -> Result<SecretBytes, CryptoError>
}
```

- 默认选择来自当前安全政策，而不是在签名中永久硬编码算法。
- Key 必须绑定 Provider、算法 ID、参数和 key ID，不能把任意等长字节用于另一算法；密文 envelope 记录协议所需的算法/参数版本，但不泄露密钥。
- 高层 `Sealer` 默认负责 nonce 生成、计数持久化和重启/并发唯一性；低层显式 nonce API 只面向协议实现者，调用者承担“同一 key 下 nonce 不重复”的证明义务并接受静态/运行时审计。
- 密钥使用不可复制或显式复制的 Secret 类型，Drop 尽力清零；日志和 Debug 不输出内容。
- Nonce 唯一性、密钥轮换、算法协商和旧密钥读取窗口属于协议契约。
- 密码比较使用常数时间操作；错误文本不泄露认证状态差异。
- PQC 仅在 NIST 标准、成熟 Provider、互操作和独立审计通过后晋级；ZKP 不属于本标准库。

## 6. 认证、授权与会话官方包

JWT、RBAC 和 Session 是官方包而非语言内置。JWT 验证必须限定算法、issuer、audience、有效期和密钥 ID，拒绝 `alg=none` 与算法混淆。访问 Token 短期有效，刷新 Token 可撤销并轮换；密钥缓存遵循最大陈旧期。

RBAC 判定输入包含主体、租户、资源、动作和上下文，默认 deny。授权决策可审计但必须脱敏。Session Cookie 默认为 Secure、HttpOnly、SameSite，并有固定/绝对过期、CSRF 防护和服务端撤销。认证失败不应通过响应时间或文本暴露用户是否存在。

最小切片只提供验证器接口与一个审计过的 Provider；OAuth/OIDC、企业目录与云 KMS 作为适配器，不在首版自研。

## 7. 序列化和配置

### 7.1 统一 Codec 契约

```x
trait Encoder<T> {
    fn encode(&mut self, value: &T, out: &mut dyn Write, ctx: &CodecContext)
        -> Result<(), EncodeError>
}
trait Decoder<T> {
    fn decode(&mut self, input: &mut dyn Read, ctx: &CodecContext)
        -> Result<T, DecodeError>
}

struct CodecLimits {
    max_bytes: usize, max_depth: usize, max_items: usize,
    max_string_bytes: usize, allow_unknown_fields: bool,
}
```

解析失败包含格式、稳定错误码、字节位置/字段路径和安全摘要。Decoder 必须限制深度、总字节、集合长度和整数范围，禁止不可信输入触发无限分配。浮点 NaN/Infinity、重复键、未知字段、BOM、注释和尾随数据的处理逐格式明确。

### 7.2 格式边界

| 格式 | 推荐用途 | 必须明确的边界 |
|---|---|---|
| JSON | Web/API | 数字精度、重复键、UTF-8、未知字段 |
| YAML | 人工配置 | Anchor/Alias 上限、类型推断、安全加载模式 |
| TOML | 项目配置 | 日期时间和整数范围、重复表 |
| CSV | 流式表格 | 方言、编码、引号、列数变化 |
| Protobuf | 版本化协议 | 字段号保留、unknown fields、oneof |
| MessagePack | 紧凑传输 | 扩展类型注册、整数宽度 |

配置优先级固定为 `default → system file → user file → project file → environment → CLI`，每个最终值可查询来源但不显示秘密。配置加载先解析、再合并、再验证，失败不产生部分生效状态。

### 7.3 Schema 演进

兼容规则至少覆盖新增可选字段、删除字段保留编号、类型扩大/缩小、枚举未知值和默认值改变。消费者应保留未知字段的协议须明确。迁移采用版本化函数并支持 N-1/N 双读；破坏性变更需要新版本或新媒体类型，不能仅修改文档。

## 8. 数据库、事务与迁移

### 8.1 驱动和连接池接口

```x
trait DbDriver {
    async fn connect(&self, config: &DbConfig, ctx: &DbContext)
        -> Result<Connection, DbError>
}

async fn transaction<T>(
    conn: &mut Connection,
    options: TxOptions,
    body: fn(&mut Transaction) -> Result<T, DbError>,
) -> Result<T, DbError>
```

连接池有最大连接、等待队列、获取 deadline、空闲/存活期限和健康探针。取消获取不泄漏租约；连接返回池前重置事务、会话变量和临时资源。密码使用 Secret 引用，不出现在 DSN 日志中。

事务错误区分连接、语法、约束、死锁、序列化冲突、取消和未知提交结果。遇到网络中断时，客户端可能无法判断提交是否成功；库不得把它简化为普通失败并自动重试。自动重试仅限明确可重试且业务幂等的闭包。

### 8.2 编译期 SQL 和离线 Schema

P3/P4 以离线 Schema 快照检查参数数量、类型与结果列，不要求 CI 连接生产数据库。快照携带数据库类型、版本、迁移 ID 和哈希；过期时诊断并要求更新。动态 SQL 仍可使用运行时 API，但不享有静态保证。本文中的 Driver/Transaction/Codec 签名均为非规范性接口草图；各 API RFC 必须补齐所有权、阻塞/取消、复杂度、资源和平台字段，遵循[标准库索引](./README.md)的统一条文。

迁移遵循 Expand → Backfill → Contract，可前滚且有恢复计划。破坏性 DDL 需要备份、锁影响评估和 N-1 应用兼容证据。

## 9. Arrow、Parquet、流式 ETL 与 DataLoader

### 9.1 列式内存边界

Arrow 适配遵循 Arrow C Data Interface，数组包含类型 Schema、长度、offset、null bitmap、buffers 和释放回调。零拷贝只在布局、对齐、端序、设备和 lifetime 兼容时成立；否则返回转换计划或显式复制。接收方获得所有权前，生产方不能释放缓冲区。

Parquet Reader 对行组、列投影、Predicate Pushdown、压缩 codec、Schema 合并和统计可信度给出选项。损坏页、校验失败、列类型冲突和超出资源上限返回带位置错误。

### 9.2 流式解码

JSON/CSV 流式 Decoder 以 `Chunk → ParsedBatch → ConsumerAck` 工作，不加载完整输入。跨 Chunk 的 UTF-8、引号、转义和数字状态保留在解析器中。错误策略可选停止、跳过记录或收集有限错误；跳过必须返回行/字节偏移和已丢数据计数。

### 9.3 DataLoader 与背压

DataLoader 由 Reader、Decode、Transform、Batch、Prefetch 五级组成，每级有有界队列。双缓冲是可选优化，不是语义。取消从消费者反向传播，已借出的 Batch 在归还前保持资源。预取窗口由内存配额约束；GPU 不可用时可回退 CPU/Host Buffer，但调用者可禁止隐式复制。

## 10. 错误、取消和资源耗尽矩阵

| 域 | 典型错误 | 取消后状态 | 资源上限 |
|---|---|---|---|
| 文本/正则 | InvalidUtf8、InvalidPattern、BudgetExceeded | 纯计算停止，无外部副作用 | 模式、DFA、输入、时间 |
| 时间/调度 | ClockUnavailable、AmbiguousLocalTime | Timer 移除或报告已触发 | Timer 数、队列、补跑次数 |
| 密码 | InvalidKey、AuthFailed、ProviderUnavailable | 不返回部分明文 | 密钥、消息、KDF 成本 |
| Codec | Syntax、Depth、Size、UnknownField | 已消费偏移可查询 | 字节、深度、集合、错误数 |
| DB | Deadlock、UnknownCommit、PoolTimeout | 查询可能已提交，按驱动说明 | 连接、排队、行、事务时长 |
| ETL | CorruptPage、SchemaMismatch、DeviceUnavailable | 已确认 Batch 保留，未确认释放 | Batch、预取、并发、设备内存 |

## 11. 安全基线

- 所有反序列化默认按不可信输入处理，不支持任意类型实例化或代码执行。
- Unicode 安全检查提供混淆字符、双向文本和规范化诊断，但不得擅自修改用户数据。
- 密钥、Token、数据库密码和个人数据通过分类标签控制日志、Trace、Core dump 与 AI 上下文。
- 正则、YAML Alias、压缩包、KDF、SQL、列式页和数据批次均需资源预算，防止计算/内存放大。
- SQL 参数使用绑定，不拼接；动态标识符通过 allowlist 构造。
- 第三方 codec、crypto、数据库和媒体依赖必须有 SBOM、CVE 策略、许可证与升级 Owner。

## 12. 平台矩阵

| 能力 | Windows/Linux/macOS | WASI/浏览器 | 移动端 | `no_std`/嵌入式 |
|---|---|---|---|---|
| UTF-8/Unicode 核心 | supported | supported | supported | 精简数据表 |
| 时区数据库 | 可随包发布 | 宿主/随包 | OS/随包 | 通常 unsupported |
| SecureRandom | OS CSPRNG | Web Crypto/WASI | 平台安全 API | 需硬件/宿主 Provider |
| Codec | supported | supported | supported | 受 alloc 与体积限制 |
| 数据库 | 驱动支持 | 通常 HTTP/代理 | 平台策略限制 | unsupported |
| Arrow/Parquet | supported | 内存/文件能力受限 | 条件支持 | 通常 unsupported |
| SIMD 解码 | 能力探测+标量回退 | WASM SIMD 可选 | NEON 可选 | 目标相关 |

不得以一个平台的 ICU、OpenSSL、数据库或 SIMD 能力推断其他平台。缺失 Provider 返回 `Unsupported`，安全能力不得使用弱算法静默降级。

## 13. 最小切片

| 阶段 | 最小交付 | 验收边界 |
|---|---|---|
| P2 | UTF-8 String/Bytes、基础 char、稳定错误模型 | 正反边界、Unicode 版本锁定 |
| P3 | Instant/SystemTime、JSON/TOML、SecureRandom、配置合并 | 三大 OS、资源上限、互操作 |
| P3/P4 | TLS 所需 crypto Provider、JWT 验证、数据库 Driver/Pool | 独立安全审计、故障注入 |
| P4 | Protobuf/MessagePack/CSV 流式、Schema 演进、离线 SQL | N-1/N 兼容与有界内存 |
| P4/P5 | Arrow/Parquet、DataLoader、PQC Provider 探针 | C Data 互操作、CPU 回退、Feature Gate |

## 14. Planned 测试目录

- `TEST-TEXT-UTF8-001`：非法 UTF-8、边界切片、组合字符、双向文本与数据版本。
- `TEST-TEXT-REGEX-001`：恶意模式、DFA 体积预算、运行时回退和线性/限时执行。
- `TEST-TIME-001`：时钟回拨不影响 deadline；DST 歧义/缺失和时区升级。
- `TEST-CRYPTO-001`：已知答案、Key/Provider/算法参数不匹配拒绝、高层 nonce 并发与重启唯一性、低层 nonce 重用诊断、错误密文和密钥不进入日志。
- `TEST-AUTH-001`：JWT 算法混淆、过期、issuer/audience、轮换与撤销。
- `TEST-CODEC-001`：深度/大小/重复键/未知字段/截断输入与流式恢复。
- `TEST-SCHEMA-001`：N-1/N 双向兼容、未知枚举、字段删除和迁移失败回滚。
- `TEST-DB-001`：池耗尽、取消、死锁重试、未知提交状态、秘密脱敏。
- `TEST-DATA-001`：Arrow lifetime、Parquet 损坏页、投影、标量回退和内存上限。
- `TEST-DATALOADER-001`：双缓冲背压、消费者停止、设备失败和 Batch 资源归还。

全部 ID 为 planned。通过定义要求真实测试卡、数据来源、seed、平台、工具链、期望/实际和证据链接，不以文档中的示例代替执行结果。

## 15. 回滚、兼容和验收

Unicode/时区/CA 数据升级可以回滚到上一签名数据包；Codec 和数据库迁移保持 N-1 Reader，写新格式前验证旧版本策略；Crypto 算法轮换允许双读单写，禁止回滚到已撤销算法。Arrow/GPU 优化关闭后应回到标量/CPU 路径且结果在规定误差内。

本专题达到“可实施”要求需同时具备：接口 RFC、Owner、Provider 选择 ADR、错误与资源契约、平台矩阵、planned 案例落成、互操作证据、安全审计和回滚演练。在此之前状态保持草案。

## 16. 原始资料追溯

| 来源 | XLF 与落实位置 |
|---|---|
| `1.txt` | XLF-01-011：跨平台标准库 |
| `7.txt`/`8.txt` | XLF-07-007：PQC 按标准与审计回归；XLF-07-013：合规污点能力的资料分类边界 |
| `9.txt` | XLF-09-002～XLF-09-003、XLF-09-007、XLF-09-009、XLF-09-011～XLF-09-014：Codec、Schema、配置、i18n、DB、调度与认证 |
| `10.txt` | XLF-10-004～XLF-10-006：Decimal/Regex/Bitfield（本文件仅负责库边界） |
| `12.txt` | XLF-12-008～XLF-12-010：Arrow/Parquet、DataLoader、流式 JSON/CSV |

AI/Tensor/GPU 的数据消费边界见 [Tensor、GPU 与 Agent 平台](../ai/tensor-gpu-agent-platform.md)；它们不得反向改变本文的 CORE 文本和序列化语义。
