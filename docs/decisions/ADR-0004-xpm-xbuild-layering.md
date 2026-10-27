# ADR-0004 XPM / XBuild 分层与分期

> 状态：Accepted｜版本：2.1.0｜负责人：Tooling Lead｜最后更新：2026-10-22
> 类型：ADR｜取代：旧 ADR-0001（分期后移：最小包图从 P0 移到 P1）

## 决策

1. XPM 负责校验、解析、获取、校验摘要，输出 `x.lock` 和 ResolvedGraph。XBuild 消费锁图，生成 Action DAG 并执行。编译器只执行编译 Action。
2. 禁止反向调用：编译器不回调 Resolver，XBuild 不重新选版本，缓存不是源码的唯一来源。
3. 分期：
   - P0：单文件，不需要 XPM；
   - P1：Path/Workspace，加 `x.lock` v1 和 `graph-v1`；
   - P2：Git、版本约束、PubGrub、Feature；
   - P3：Registry、签名、远程只读缓存、SBOM；
   - P4：publish、yank、API diff；
   - P5：外部生态适配器。
4. 优先复用经过验证的算法和标准：PubGrub、SemVer、内容寻址、Sigstore 无密钥签名、SLSA Provenance、CycloneDX（ADR-0008 K9 已选定）。具体实现库在对应阶段的设计评审中选定。
5. 契约细节见[包规范](../../specs/packages/manifest-lock-build.md)。

## 备选方案

直接复用 Cargo：不选。X 的包身份、Edition、Feature 域与 Cargo 不同，而且需要与编译器查询深度集成。可以借鉴 Cargo 的设计，但不依赖它。

## 后果

- P0 不再要求三包 Workspace，避免“先造 Cargo、语言空心”。
- P1 的三包 Path Workspace 是 Lockfile 确定性的首个证据。
