---
doc_id: DOC-SPECS-MODULES-PACKAGES-EDITIONS
title: X-Lang 模块、包、清单、Feature 与 Edition 规范
authority: normative
owner: role/language-council
backup_owner: role/toolchain-team
version: "0.1"
maturity: CORE
status: 草案
phase: P2
last_reviewed: 2026-08-15
applies_to: [resolver, x-build, xpm, x-toml, package-graph]
traceability_scope: [XLF, XLC]
supersedes: []
---

# X-Lang 模块、包、清单、Feature 与 Edition 规范

## 1. 目的和职责边界

本文把原始 `2.txt` 的标准项目结构、`x.toml`、依赖与构建命令，以及 `11.txt` 的版本治理要求，细化为 Resolver、构建系统和包管理器可共同实现的规则。它展开 RULE-LANG-006、014、020，但不重复词法/表达式规则。

语言层负责模块命名、可见性和路径含义；构建层负责发现源入口、选择目标/Profile/Feature；XPM 负责依赖版本、来源、锁定与下载；Edition 只控制经过批准的源码解释差异。构建脚本沙箱、注册表发布和供应链签名分别由工具链/安全专题规定，不在本文发明格式。

## 2. 术语和规范项目形态

- **包（package）**：一个 `x.toml` 描述、具有名称与版本的发布/构建单位。
- **目标（target）**：包产生的一个二进制、库、测试或其他制品。
- **crate/编译单元**：一次前端语义分析和代码生成的根；最终术语名仍待 RFC，本文统一称“编译单元”。
- **模块（module）**：编译单元内的命名与可见性作用域。
- **工作区（workspace）**：共享锁定和构建配置的一组包，不等于一个包。
- **Feature**：显式选择的可选能力/依赖集合，不得偷偷探测环境改变公共 API。
- **Edition**：按包选择的源码语言解释版本，不等于编译器版本。

原始材料给出的推荐形态：

```text
my-project/
├── x.toml
├── src/
│   ├── main.x
│   ├── lib.x
│   └── modules/
├── tests/
├── benchmarks/
└── target/
```

P0 要求 `x.toml` 包含三个 `[package]` 字段和允许为空的 `[dependencies]` 表，并有一个选定入口。`tests/`、`benchmarks/`、`.xfmt` 按能力创建；`target/` 是生成物。`src/modules/` 是组织建议，不具有绕过 `mod` 声明的隐式魔法。

## RULE-MOD-001：包根、入口与源文件发现

- maturity: CORE
- status: 草案
- phase: P1

**规范性条文。** 构建从显式给定或向上发现的 `x.toml` 确定包根。默认二进制入口为 `src/main.x`，默认库入口为 `src/lib.x`；两者同时存在时构成同一包的两个目标，而非合并为一个模块。额外目标必须由清单显式声明，具体表名由 RFC-MODULE-01 冻结。实现不得递归编译 `src/` 下所有 `.x` 文件；只有从目标根通过 `mod` 可达的模块进入编译单元。

**发现步骤。** (1) 规范化清单绝对路径；(2) 解析清单并选择目标；(3) 验证入口在包根允许范围内；(4) 读取根源文件；(5) 遍历 `mod` 声明解析子模块；(6) 对规范化文件身份去重；(7) 检测同一文件被两个模块身份包含。

**正例。** `src/main.x` 声明 `mod config;` 后才加载约定位置的 config 源文件。

**反例。** 仅把 `secret.x` 放进 `src/` 不应自动执行或链接；`../other-package/src/lib.x` 不能作为未声明本地模块越界加载。

**边界。** symlink/junction、路径大小写、UNC 路径和 Unicode 正规化必须由 SourceManager 规范化并防止逃逸；同一路径不同拼写不得生成两个模块实例。单文件与目录模块的确切候选顺序待 RFC，歧义时必须报错，不能因文件系统枚举顺序选择。

**诊断。** X-E2701 找不到模块并列出尝试位置；X-E2704 模块路径歧义；X-E2705 包根逃逸/重复身份。

**编译器影响。** SourceManager 产生规范文件 ID；模块图成为名称解析和增量依赖输入；新增未被引用文件不应使包语义缓存失效。

**planned 测试/追溯。** TEST-MOD-DISCOVER-001..012，覆盖缺失、歧义、大小写、symlink、越界、双目标和未引用文件；来源 XLF-02-002、XLF-02-013、XLC-CORE-018；RFC-MODULE-01。

## RULE-MOD-002：模块路径、use 与名称空间

- maturity: CORE
- status: 草案
- phase: P1

**规范性条文。** `mod name` 创建模块成员；`use path [as alias];` 只把已有名称引入当前作用域，不复制定义、不改变原可见性。绝对路径、包根、自身和父模块的拼写尚待 RFC；在冻结前实现必须至少支持无歧义的包内规范路径。导入循环本身可以存在，前提是声明收集与名称解析能达到确定固定点；值初始化循环按 RULE-MOD-004 处理。

**解析步骤。**

1. 为每个模块预先收集直接声明和子模块名，形成不含 use 的初始表。
2. 将每条 use 解析成 `(起点, 路径段, 目标命名空间, alias)`。
3. 迭代解析只依赖已知声明的导入；记录阻塞原因。
4. 一轮无进展后，把剩余项按“缺失、不可见、循环/歧义”分类诊断。
5. 同一命名空间中两个显式名称冲突必须报错；禁止依赖导入顺序覆盖。

**正例。** `use math::Vector as Vec2;` 在本模块建立 `Vec2` 名称，原 `math::Vector` 不变。

**反例。** 两个 use 都引入 `Config` 且无 alias，不得选择后者；通过私有中间模块路径访问私有定义必须失败。

**边界。** 类型、值、模块、宏是否分名称空间由 RFC 决定；当前解析器必须用显式 Namespace 枚举，不能把所有名称塞进一个字符串表后形成偶然行为。glob import 未进入最小 EBNF，不是 CORE 既定能力。

**诊断。** X-E2702 不可见；X-E2710 重复/歧义导入；X-E2711 未解析路径，需标出最长成功前缀；X-E2712 导入固定点失败。

**编译器影响。** Resolver 分“声明收集”和“导入解析”查询；HIR 路径必须替换为稳定 DefId，后端不得再次解析文本路径。

**planned 测试/追溯。** TEST-MOD-RESOLVE-001..016：alias、冲突、跨层、私有、循环、固定点和增量变更；来源 XLF-01-002、XLF-02-012、XLC-CORE-018；RFC-MODULE-01。

## RULE-MOD-003：可见性与 API 表面

- maturity: CORE
- status: 草案
- phase: P1

**规范性条文。** 未写 `pub` 的顶层项和字段默认仅在其定义模块及 RFC 明确的后代范围可见；`pub` 使名称可从允许的外部路径访问，但一个项的有效可见性不得超过路径上任一父模块。受限 `pub(...)` 尚待 RFC。公开签名不得泄露调用者无法命名的私有类型。

**检查步骤。** 计算模块树上的声明可见域；解析使用点相对定义点的可达性；对每个公开 API 递归检查参数、返回、字段、Trait bound 和关联类型的有效可见性。

**正例。** 公共函数返回公共结构体；私有辅助函数使用私有类型。

**反例。** `pub fn load() -> PrivateConfig` 必须拒绝或至少在尚未发布阶段作为硬错误，不得产生无法调用的 API。

**边界。** 测试、文档测试、同包多目标不能默认绕过私有规则；编译器内部测试后门必须是显式 cfg/测试 API。重新导出需要明确 use 可见性语法，未冻结前不假定 `pub use` 已可用。

**诊断。** X-E1202 私有访问；X-E2715 私有类型泄漏；X-W2716 无效 pub（公开但父模块不可达）。

**编译器影响。** 元数据只导出有效公共项和必要布局信息；API diff 以规范化公共表面比较，不能只扫 `pub` token。

**planned 测试/追溯。** TEST-MOD-VIS-001..012；来源 XLF-01-010、XLF-02-012、XLF-11-001、XLC-CORE-018；RFC-MODULE-01、RFC-API-EVOLUTION-01。

## RULE-MOD-004：声明循环、初始化与副作用

- maturity: CORE
- status: 待决策
- phase: P2

**规范性条文。** 类型和函数声明可形成递归引用，只要类型布局与 Trait 求解终止。模块加载不得依赖文件遍历顺序执行任意顶层语句；最小语法没有任意顶层可执行语句。`const` 必须由确定性常量求值处理；需要运行时初始化的 `static` 及初始化函数在 RFC 前不得作为 CORE 稳定能力。

**决策步骤。** 对声明依赖图标记边种类：signature、layout、const-eval、runtime-init。signature 环可接受；layout 环必须含间接层；const-eval 环拒绝；runtime-init 环在能力引入前拒绝，未来必须有显式顺序/惰性状态机。

**正例。** 两个函数互相调用可在声明收集后解析；链表节点通过 Box 指向自身类型。

**反例。** `const A = B; const B = A;` 必须报告循环；两个结构体按值互含导致无限布局必须拒绝。

**边界。** FFI 动态库初始化、线程局部存储和插件注册不是普通模块初始化；构建脚本也不能注入隐式执行顺序。

**诊断。** X-E2720 常量初始化循环并输出最短环；X-E2203 无限布局；X-E2721 未批准的运行时全局初始化。

**编译器影响。** 依赖图边必须带原因和 Span；拓扑排序只用于允许的有向无环子图；MIR 不得按源码文件顺序生成隐藏 init。

**planned 测试/追溯。** TEST-MOD-CYCLE-001..010；来源 XLF-01-002、XLF-01-008、XLF-02-013、XLE-DATA-008；RFC-MODULE-INIT-01。

## RULE-PKG-001：`x.toml` 最小清单与严格解析

- maturity: CORE
- status: 草案
- phase: P1

**规范性条文。** 清单使用 TOML。最小清单必须包含 `[package].name`、`version`、`edition` 以及 `[dependencies]` 表；没有外部依赖时该表允许为空。包名必须满足注册表/文件系统共同的规范化规则；版本必须是 SemVer；Edition 必须属于编译器支持集合。未知字段默认应报告带路径的警告或错误，Stable 发布不得静默忽略影响构建语义的未知字段。

```toml
[package]
name = "my-project"
version = "0.1.0"
edition = "2026"

[dependencies]
serde = "1.0"
http = { version = "0.2", features = ["client"] }

[profile.release]
opt-level = 3
lto = true
```

上例后半来自原始 `2.txt`，是目标形状而非已冻结完整 Schema。原始 `[target].android/ios/wasm` 与 `[build].pre-build/post-build` 必须分别进入目标规范和沙箱构建脚本 RFC；不得因为出现在示例中就允许任意 shell 命令。

**解析步骤。** UTF-8/TOML 解析 → 字段类型检查 → 名称/版本/Edition 规范化 → 目标与 Feature 交叉引用 → Profile 合并 → 依赖声明交给 XPM → 生成去敏的 Canonical Manifest 指纹。路径字段相对包根解析并进行逃逸检查。

**正例。** 包含三个 `[package]` 字段和空 `[dependencies]` 表的最小清单可选择默认目标入口。

**反例。** 重复 TOML 键、非法 SemVer、未知 Edition、依赖既无版本也无批准来源均拒绝；预构建命令不能在无沙箱规范时执行。

**边界。** 环境变量展开、平台条件、私有 registry 凭据不得进入可复现指纹的秘密明文；清单错误不能回退为猜测默认值继续发布。

**诊断。** X-E2830 清单语法/字段错误，显示完整键路径；X-E2831 不支持的 Edition；X-E2832 路径逃逸；X-E2833 不安全构建配置。

**编译器影响。** Parser 与编译器不直接读取散乱环境变量，统一接收构建系统验证后的 CompileRequest；清单规范化结果进入缓存键和制品清单。

**planned 测试/追溯。** TEST-PKG-MANIFEST-001..018：最小、重复、类型、SemVer、Edition、路径、未知字段、秘密脱敏和确定指纹；来源 XLF-02-013、XLF-10-012、XLF-11-004、XLC-CORE-019；RFC-MANIFEST-01、RFC-BUILD-SCRIPT-01。

## RULE-PKG-002：依赖图、版本与锁定

- maturity: CORE/EXTENDED
- status: 待决策
- phase: P2

**规范性条文。** 依赖解析必须产生确定的包图，节点身份至少包含规范包名、精确版本和来源；同名同版本不同来源不是同一节点。库包构建允许根据清单约束求解，应用/工作区的可复现构建必须使用锁定结果。依赖环在包级拒绝。解析不得访问未声明来源，也不得因网络返回顺序改变结果。

**求解要求。** 输入规范化清单、registry 索引快照、锁文件和启用 Feature；输出精确包图、选择原因与冲突解释。具体求解算法由 XPM 规范确定，但必须：(1) 可终止并有预算；(2) 优先复用满足约束的锁定；(3) 冲突输出最小或可理解的约束链；(4) 离线模式只用已验证缓存；(5) 哈希/签名失败不回退未验证制品。

**正例。** 两个依赖约束有公共版本时产生一个有解释的选择并写锁定。

**反例。** 同一索引输入重复求解得到不同版本；哈希不符后下载“相近版本”；包 A/B 强依赖成环。

**边界。** 多版本共存策略、git/path 依赖、yanked 版本、registry 撤回、平台依赖和预发布版本需 XPM RFC；本文不擅自复制 Cargo/npm 行为。

**诊断。** X-E2840 无解依赖并列出约束来源；X-E2841 包环；X-E2842 来源/完整性冲突；X-R2843 求解预算耗尽。

**编译器影响。** 每个依赖以编译元数据/制品输入传入；包解析变化必须失效相关查询；SourceMap 和诊断使用用户依赖名同时保留规范身份。

**planned 测试/追溯。** TEST-PKG-RESOLVE-001..020；来源 XLF-01-013、XLF-02-013、XLF-11-001、XLF-11-004、XLC-CORE-019..020；RFC-XPM-RESOLVE-01、RFC-LOCKFILE-01。

## RULE-PKG-003：Feature 统一、隔离与公共 API

- maturity: EXTENDED
- status: 待决策
- phase: P3

**规范性条文。** Feature 名由包定义，启用必须是显式构建输入并进入包图、查询和制品指纹。Feature 不能读取运行时环境后隐式翻转。依赖 Feature 的合并模型、默认 Feature 和禁用语义待 RFC；在确定前不得承诺“全局只加不减”或“每条依赖边独立”模型。

**安全边界。** Feature 不得绕过 `unsafe`、权限、签名或实验能力门禁；EXPERIMENTAL/RESEARCH 能力必须默认关闭并在产物元数据中可见。Feature 组合改变公共 API 时，文档、SemVer 和兼容测试必须覆盖该组合。

**正例。** 显式 `features = ["client"]` 进入依赖实例指纹和 `x doc` API 展示。

**反例。** 仅因本机检测到 CUDA 就改变同一锁定包的公共类型；名为 `safe` 的 Feature 实际关闭边界检查。

**边界。** 原始 `build.x` 检测 CUDA 的设想必须改为沙箱声明输入与显式输出建议，不能制造不可复现的隐式 Feature。

**诊断。** X-E2850 未知 Feature；X-E2851 非法循环/冲突（模型决定后）；X-W2852 公共 API 未覆盖组合；X-E2853 实验能力无 gate。

**编译器影响。** `cfg` 在语义删除前必须保留 Span 和配置原因；未选择代码是否解析/类型检查由 RFC 冻结，避免工具与编译器看见不同语法树。

**planned 测试/追溯。** TEST-PKG-FEATURE-001..016：确定性、组合、API diff、实验隔离、缓存失效和平台差分；来源 XLF-02-013、XLF-10-012、XLF-11-001、XLE-DATA-009；RFC-FEATURE-01。

## RULE-EDITION-001：Edition 选择、兼容与迁移

- maturity: CORE治理
- status: 草案
- phase: P2

**规范性条文。** Edition 由每个包在清单中显式选择；当前清单版本缺失 Edition 必须拒绝，未来若 RFC 引入默认值需升级清单规则并提供迁移。编译器可同时支持多个 Edition，同一依赖图中的包可使用不同 Edition。Edition 只影响该包源码解析/早期语义，不改变跨包 ABI、元数据含义和已解析依赖的 Edition。

**变更条件。** 只有无法通过普通兼容演进完成、且有自动迁移或明确诊断的语言变化可进入新 Edition。新增 Edition 必须定义：差异表、迁移命令目标、保留字影响、跨 Edition 调用测试、支持周期和回退边界。Edition 不得作为绕过 SemVer 修改标准库 API 的渠道。

**正例。** 包 A 使用 2026，依赖 B 使用未来 Edition；B 的导出元数据按稳定协议被 A 消费。

**反例。** 根包 Edition 静默覆盖依赖；同一源文件根据依赖方 Edition 用不同方式编译；新 Edition 改变整数 ABI 却不升级 ABI/元数据版本。

**边界。** 宏生成代码、文档测试、build.x 的 Edition 继承需独立明确；当前不存在已批准的下一 Edition，文档不得虚构年份和特性。

**诊断。** X-E2831 未支持 Edition；X-W2860 省略/临近终止支持；X-E2861 跨 Edition 元数据不兼容。Fix-it/迁移只生成可审查 diff，不自动提交。

**编译器影响。** Edition 是 Lexer/Parser/Resolver 查询键；HIR 之后应消除 Edition 分支，必要差异显式降低；制品清单记录源 Edition 与 ABI 元数据版本。

**planned 测试/追溯。** TEST-EDITION-001..014：混合图、关键字、迁移幂等、宏/文档测试、缓存键、ABI 差分；来源 XLF-02-013、XLF-11-001～003、XLC-CORE-018..020；RFC-EDITION-01。

## 3. 跨组件流程与验收

```text
x.toml
  → 严格清单解析
  → 依赖/Feature/Edition 解析
  → 目标与模块发现
  → 声明收集和 use 固定点
  → 可见性/API 检查
  → Typed HIR
  → 锁定、制品清单与可复现证据
```

完成标准：清单、包图、模块图在相同输入下字节级确定；路径逃逸和来源冲突有安全测试；循环诊断给出最短或可理解环；每条 RULE 有 pass/fail/boundary；Windows/Linux/macOS 文件系统差异有真机测试；混合 Edition 不改变依赖语义；所有计划证据均标记 planned，未执行前不得晋级“已验证”。

待决 RFC 清单：RFC-MODULE-01、RFC-MODULE-INIT-01、RFC-MANIFEST-01、RFC-XPM-RESOLVE-01、RFC-LOCKFILE-01、RFC-FEATURE-01、RFC-EDITION-01、RFC-BUILD-SCRIPT-01。来源总览：XLF-01-013、XLF-02-012～014、XLF-10-012、XLF-11-001～004、XLC-CORE-018～020。
