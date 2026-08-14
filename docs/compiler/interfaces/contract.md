---
doc_id: DOC-COMPILER-INTERFACES-CONTRACT
authority: implementation
owner: role/documentation
backup_owner: role/architecture
version: "1.0"
maturity: EXTENDED
status: 草案
phase: P2
last_reviewed: 2026-08-15
traceability_scope: [XLF, XLC, XLE]
---
# 编译器接口契约

> 状态：草案｜Owner：Compiler API Maintainer｜追溯：XLF-001~164、XLC-CORE-*

## CompileRequest / CompileResult

    CompileRequest {
      schema_version, workspace_root, inputs, target, profile, features,
      emit, limits, cancel, previous
    }
    CompileResult { diagnostics, artifacts, stats }

路径必须在工作区授权根内；输出采用临时目录写入，manifest 原子提交，失败不得暴露半成品。

## 工件与版本

Token、AST、HIR、MIR、LLVM 均为内部工件。每个序列化工件包含 schema_version、producer_version、source_fingerprint 和 target_fingerprint。未知主版本拒绝读取；消费者读取前必须运行 verifier。

## 诊断与错误

Diagnostic 包含 code（X-E####）、severity、message、primary_span、secondary_spans、notes、fixes、origin、retryable。1000 段为词法、2000 语法、3000 名称/类型、4000 借用、5000 IR、6000 后端、7000 工具链。机器 JSON 字段只追加；内部错误带 request id，不回显秘密。

## 取消、并发与资源

CancelToken 可由调用方、超时或资源监管器触发；文件读取、查询等待、Pass 循环和外部进程边界都要检查。取消返回 X-E7001，且不得提交缓存。共享查询表使用并发安全快照，禁止持锁调用插件。默认限制：源码 64 MiB、单文件 16 MiB、递归深度 256、IR 节点 10M、编译时间 10 min；只能经审计降低或提高。

## TargetSpec / Backend

TargetSpec 提供 triple、数据布局、ABI、sysroot、链接器和能力集合。Backend 只接受已验证 MIR 与 TargetSpec，返回对象、调试信息和诊断；不能读取主机环境绕过 TargetSpec。新增后端必须通过能力探测、差分测试和独立 RFC。

## 负向测试、验收与回滚

未知 schema、截断工件、错误 fingerprint、重复取消、宏超时、越权读写、输出过大、优化差异和缓存损坏都必须稳定失败且不修改缓存。验收证据包括 schema fixture、协议测试、fuzz、并发压力和跨平台制品；回归时关闭 feature gate，保留旧解析器一个发布周期并提供迁移工具。
