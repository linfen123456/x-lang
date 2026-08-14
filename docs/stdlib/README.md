---
doc_id: STDLIB-INDEX
title: X-Lang 标准库 API 契约索引
status: draft
maturity: CORE+EXTENDED
owner: standard-library
trace: [XLF-01-011, XLF-09-001..016, XLF-12-008..010, XLC-SERVER-001..010]
---

# X-Lang 标准库 API 契约索引

## 目标与非目标

规定 `x-core`、`x-alloc`、`x-std` 及官方扩展包的公共 API、错误、线程安全、平台能力和稳定级别。不把 GUI、云厂商 SDK、Tensor 或全部协议栈强行塞入核心标准库；这些能力按独立包发布。

## 分层与契约

核心 API 的可执行契约见[Core/Alloc API](./core-api.md)。

| 层 | 示例 | 稳定要求 |
|---|---|---|
| CORE | `Option`、`Result`、集合基础、字符串、迭代器 | 无 OS 依赖；版本兼容和文档测试 |
| EXTENDED | fs、net、time、process、observability、serialization | 平台 Tier、错误/取消、MSRV 和能力探测 |
| EXPERIMENTAL | tensor、GUI、QUIC、高级媒体 | feature gate、独立版本和退出条件 |

### API 契约模板

每个公开函数必须说明输入不变量、返回值、错误类型、取消/阻塞行为、线程安全、资源释放、平台差异和示例。错误不得通过字符串匹配作为稳定接口。

```x
pub fn read(path: Path) -> Result<Bytes, IoError>
```

正例：调用者显式处理 `IoError`；反例：库内部 `panic` 掩盖权限或编码失败。

## 边界、性能与安全

时间、随机数、TLS、密码学和 Unicode 规则必须引用外部标准并记录版本。网络 API 默认超时、取消和大小上限；加密 API 禁止自创算法。性能目标记录吞吐、P95/P99、分配和平台，未测量不得承诺。

## 测试、发布与回滚

`tests/stdlib` 覆盖 API 契约、doc-test、跨平台 Tier、错误注入、模糊输入和 ABI。稳定 API 只能通过 Edition/主版本变更删除；扩展包可独立回滚，注册表保留签名制品和撤回记录。

## P3–P6 入口

- P3：网络/文件/时间/序列化/观测 API 稳定化与平台矩阵。
- P4：数据库、TLS、HTTP/2/3、CLI 和企业认证包。
- P5：GUI、媒体、移动、云原生和数据工程适配器。
- P6：Tensor、Autograd、GPU、嵌入式和研究型库，均不得反向依赖 `x-core` 之外的实验实现。
