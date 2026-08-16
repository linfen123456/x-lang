---
doc_id: DOC-TOOLS-PACKAGE-MANAGER
authority: implementation
owner: role/tooling-team
backup_owner: role/architecture
version: "1.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-16
traceability_scope: [XLF-02-013, XLF-02-014, XLF-03-011, XLF-10-012, XLF-10-014, XLF-11-001, XLF-11-004]
---
# XPM、`x.toml`/`x.lock` 与依赖求解

> 状态：草案｜Owner：`role/tooling-team`

## 配置结构

`x.toml` 使用 canonical TOML：`package{name:String,version:SemVer,edition:Edition,authors:Vec<String>,entry:PathBuf}`、`targets:Map<TargetSpecId,TargetConfig>`、`dependencies:Map<Name,DependencySpec>`、`dev_dependencies`、`features:Map<String,Vec<FeatureRef>>`、`registries:Vec<RegistryRef>`、`profile:Map<ProfileId,ProfileSpec>`。`entry` 必须是 workspace-relative 源路径，存在、属于 package 且只能有一个 executable entry；library package 必须省略 entry。字段未知/重复、包名不合法、路径越界或 edition 不支持返回 `XPM_E_CONFIG`；不在网络失败时偷偷采用默认依赖。

`DependencySpec` 字段为 `source:Registry|Git|Path`、`version_req:SemVerReq`、`checksum:Hash32?`、`features:BTreeSet<String>`、`optional:bool`、`default_features:bool`。Git revision 必须固定 commit，path 必须在 workspace 或显式 vendor 根内；registry 包需 digest、签名和许可证元数据。

## 锁文件和求解器

`x.lock` 字段为 `schema_version:SemVer`、`root:PackageId`、`packages`、`target_sets`、`toolchain_fingerprint`。来源信任字段不能混用：Registry 项记录 registry/revision/checksum/signature-policy/revocation snapshot；Git 项记录 canonical repository、immutable commit、tree digest 和签名验证状态；Path 项记录 workspace/vendor 相对路径、content digest 与 `local=true`，不得伪造远端签名。canonical 排序为 name/source/version，换行和编码固定；锁文件缺其来源必需字段、重复 package、循环不可解析或工具链 fingerprint 不兼容都拒绝。

求解器输入 `RootManifest + RegistrySnapshot + TargetSpec + FeatureSet + toolchain_fingerprint`，输出唯一 `Resolution{packages,edges,explanation,lock_digest}`。算法必须确定性：版本/源/feature/tie-break 固定；候选列表在求解开始前冻结为有限集合，耗尽即生成 NoSolution incompatibility，已尝试 `(package,version,decision-context)` 不重复。每次决策消耗候选、每次冲突学习新 canonical incompatibility 并向更低层回跳，从而终止；预算耗尽返回 `XPM_E_SOLVER_LIMIT`，与语义无解 `XPM_E_CONFLICT` 区分。`--locked` 禁止更新，`--offline` 只允许本地索引/cache，`x update` 生成预览 diff 后才写锁。Profile 采用共享 `ProfileSpec`，优先级为 `CLI > x.toml profile > TargetSpec defaults > toolchain defaults`，环境变量仅进入 declared inputs。

`RegistrySnapshot.fetched_at` 只用于缓存过期与审计展示，不进入 snapshot digest、求解、lock 或 build fingerprint。build fingerprint 只含 manifest/lock/source/toolchain/target/profile/Edition/Feature/declared-env 等语义输入；LSP runtime snapshot ID、下载时间和本地缓存路径不得进入。

下载、校验、解包和构建分阶段隔离，分别有 URL/文件大小/CPU/并发上限。哈希或签名不匹配、撤回包、供应链审计失败不得使用缓存；坏缓存被 quarantine，不直接删除证据。registry 10 并发、包 512 MiB、解包 2 GiB、网络 60 s 是 `candidate_default`，遵循 [工具链 Budget 治理](./README.md#安全profile-与完成定义)，由 Profile 提供且不是 registry 容量承诺。

## 负向测试、版本与回滚

覆盖重复依赖、路径逃逸、entry 不存在/越界、同名不同源、锁冲突、循环 feature、撤回/哈希不匹配、离线缺缓存、registry 5xx、解包路径穿越、签名过期和磁盘满。规划测试 `TEST-TOOLS-XPM-001`、`TEST-TOOLS-XPM-002`、`TEST-TOOLS-XPM-003` 状态均为 `planned`，分别验证 deterministic lock、坏缓存隔离和 schema migration。schema minor 追加字段，major 通过 `x lock migrate` 迁移；求解回归时恢复旧 lock、旧 registry snapshot 或 vendor 源码构建。
