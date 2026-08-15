---
doc_id: DOC-STYLE-CONTRACT
title: x-style 样式、布局与可访问性规范
authority: normative
owner: role/web-platform
backup_owner: role/design-system
version: "0.2.0"
maturity: EXTENDED
status: 草案
phase: P4
last_reviewed: 2026-08-15
applies_to: [x-style-dsl, style-ir, css-backend, skia-backend, native-ui, ssr]
traceability_scope: [XLF, XLC, XLE, SECURITY]
supersedes: [DOC-STYLE-CONTRACT-LEGACY]
---

# x-style 样式、布局与可访问性规范

## 1. 责任边界

x-style 是独立 DSL/官方生态，不改变 X-Lang 核心求值、所有权、线程或错误语义。它可编译为 CSS/DOM、Skia、原生控件或静态 SSR 输出；不同后端必须通过 style IR 和 capability matrix 声明差异。x-style 不允许任意网络、文件、反射或业务状态副作用。

## 2. 源语言语法与规则

x-style 源文件使用 UTF-8，扩展名为 `.xs`。注释、字符串与数值字面量沿用 X-Lang 的基础词法，但 x-style 是独立解析器，不允许嵌入任意 X 表达式。最小语法如下；属性集合和类型由版本化属性表约束，而不是由后端临时接受。

~~~ebnf
style_file      = { namespace_decl | variable_decl | rule | media_rule | keyframes } ;
namespace_decl  = "namespace" IDENT ";" ;
variable_decl   = "var" "--" IDENT ":" style_value ";" ;
rule            = selector_list "{" { declaration | nested_rule } "}" ;
nested_rule     = "&" selector_tail "{" { declaration } "}" ;
selector_list   = selector { "," selector } ;
selector        = compound { combinator compound } ;
compound        = [ type_selector ] { class_selector | id_selector | attr_selector | pseudo_class } ;
type_selector   = IDENT | "*" ;
class_selector  = "." IDENT ;
id_selector     = "#" IDENT ;
attr_selector   = "[" IDENT [ attr_op style_atom ] "]" ;
attr_op         = "=" | "~=" | "|=" | "^=" | "$=" | "*=" ;
pseudo_class    = ":" IDENT [ "(" selector_list ")" ] ;
combinator      = ">" | "+" | "~" | WHITESPACE ;
selector_tail   = { combinator compound | class_selector | attr_selector | pseudo_class } ;
declaration     = IDENT ":" style_value [ "!important" ] ";" ;
style_value     = style_atom { style_atom } | function_call ;
style_atom      = NUMBER [ UNIT ] | COLOR | STRING | IDENT | "--" IDENT ;
function_call   = IDENT "(" [ style_value { "," style_value } ] ")" ;
media_rule      = "@when" condition "{" { rule } "}" ;
condition       = IDENT comparison style_atom { ( "and" | "or" ) IDENT comparison style_atom } ;
comparison      = ":" | "=" | "<" | "<=" | ">" | ">=" ;
keyframes       = "@keyframes" IDENT "{" { ( NUMBER "%" | "from" | "to" ) "{" { declaration } "}" } "}" ;
~~~

解析器必须为 selector、declaration、property、value 与规则块保留 source span。未知 token、未闭合 block 和非法 selector 是解析错误；属性不存在、值类型错误、变量循环和 capability 不足是验证/lowering 错误，两类诊断不得混为同一代码。

合法源码示例：

~~~css
namespace Button;
var --space: 8px;

.root {
  display: flex;
  gap: calc(var(--space) * 2);
  color: var(--foreground, #000);
  overflow: clip;
}

.root:focus-visible { outline: 2px solid #246bfe; }
@when viewport-width <= 480px { .root { flex-direction: column; } }
~~~

从源到 Style IR 的 lowering 顺序固定为：解析并保存 span、绑定 namespace、展开变量依赖、计算 selector specificity、类型检查属性值、构造 cascade 顺序、验证布局/动画/a11y、安全过滤 URL，最后按 target capability 选择后端或显式 fallback。任何阶段失败都不得产生可发布的部分样式。

### RULE-STYLE-001：选择器、命名空间与作用域

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** 每条规则必须有 selector、declaration block 和来源 span。组件默认使用显式命名空间或隔离策略；全局 selector 必须显式 opt-in。选择器匹配按树结构、伪类状态和作用域确定，不能读取未授权业务数据。无效 selector 必须诊断而不是部分应用。

**解释。** Shadow DOM、CSS Modules 和 x-style namespace 都是隔离实现，规范要求等价的 selector scope，而非要求同一技术。

**正例。** component Button 内的 .label 只匹配该组件 namespace。

**反例。** 未声明 global 的 selector 修改任意第三方组件，报告 X-E9001 scope escape。

**边界。** Shadow DOM 与原生/Canvas 后端的穿透规则需 capability 声明；不支持伪元素时可静态降级并产生 warning。

**诊断/测试/追溯。** X-E9001；TEST-STYLE-SELECTOR-001..005；来源 XLF-06-001、XLC-STYLE-001..003；RFC-STYLE-SCOPE-01（P4）。

### RULE-STYLE-002：级联、优先级和继承

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** 计算样式必须按来源层、重要性、scope、specificity、声明顺序和继承顺序确定；实现必须能输出每个属性的 winning declaration 和被覆盖原因。未定义属性值使用属性初始值或明确 fallback，不能随机依赖 backend 默认。

**解释。** style IR 应保留来源和优先级以支持 devtools/Agent 解释。继承只对列入属性表的属性生效。

**正例。** 主题变量缺失时使用 var(--color, #000) 并记录 fallback。

**反例。** 两条同级规则在不同后端选出不同颜色，报告 X-E9002 cascade divergence。

**边界。** CSS compatibility quirks 不自动复制；若 CSS backend 需要 legacy mode，必须在 target/profile 标记。

**诊断/测试/追溯。** X-E9002；TEST-STYLE-CASCADE-001..006；来源 XLF-06-003、XLC-STYLE-004..006；RFC-STYLE-CASCADE-01（P4）。

### RULE-STYLE-003：值、单位、变量和主题

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** 长度、角度、时间、颜色、字体、百分比和自定义变量必须在 style IR 中携带单位/类型；变量解析形成有向无环依赖，循环或缺失且无 fallback 必须诊断。颜色和数值转换不得隐式丢精度。

**解释。** 变量是样式数据，不是 X mutable state；主题切换只能通过显式属性或 provider 更新。

**正例。** --space: 8px; padding: calc(var(--space) * 2)。

**反例。** 使用未定义 --brand 且无 fallback，报告 X-E9003 unresolved style variable。

**边界。** 相对单位依 viewport/font/parent；无 viewport 的 SSR 必须使用约定初值并标记 deferred layout。

**诊断/测试/追溯。** X-E9003；TEST-STYLE-VALUE-001..006；来源 XLF-06-003、XLE-DATA-004、XLC-STYLE-007..008；RFC-STYLE-VALUE-01（P4）。

### RULE-STYLE-004：布局、溢出与响应式

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** Flex/Grid/box layout 必须明确可用空间、最小/最大约束、gap、对齐、换行、溢出和测量顺序。响应式断点按显式 viewport/container 条件选择；布局无法满足约束时必须按 overflow policy（clip/scroll/wrap/error）处理，而不是截断未知内容。

**解释。** 布局 IR 可以在编译期静态化部分约束，但动态字体、窗口和内容仍需运行时测量。

**正例。** Grid 指定 minmax、overflow=scroll，并在小屏断点把列改为 1。

**反例。** 固定 1000px 宽度无 overflow policy 造成内容不可达，报告 X-W9004 unbounded overflow。

**边界。** 不同字体栅格化和 native widget metrics 可产生像素差；黄金测试应比较容差和语义框，不宣称跨平台像素完全一致。

**诊断/测试/追溯。** X-W9004；TEST-STYLE-LAYOUT-001..008；来源 XLF-06-001、XLF-06-003、XLC-STYLE-009..011；RFC-STYLE-LAYOUT-01（P4）。

### RULE-STYLE-005：动画、取消和减少动效

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** 动画必须有 duration、timing、可取消状态和终值策略；组件卸载或用户触发 cancel 时必须停止调度并释放 observer。prefers-reduced-motion 命中时必须使用静态或低动效回退，不能只隐藏视觉而保留无界计算。

**解释。** 动画是可取消任务，不能阻止页面关闭。服务端只生成静态初值。

**正例。** transition.cancel() 后 promise 返回 Cancelled，组件不再持有 node。

**反例。** reduced-motion 下仍循环 requestAnimationFrame，报告 X-E9005 motion accessibility violation。

**边界。** 后端不支持合成动画时可用离散状态切换；时间源/刷新率是平台实现定义。

**诊断/测试/追溯。** X-E9005；TEST-STYLE-MOTION-001..005；来源 XLF-06-003、XLC-STYLE-012；RFC-STYLE-MOTION-01（P5）。

### RULE-STYLE-006：可访问性和语义降级

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** 交互组件必须声明 role/name/description、键盘或触控操作、focus 顺序、状态和错误反馈。颜色不能是唯一信息通道；对比度、可见 focus、文本缩放和 reduced-motion 必须可审查。Canvas/Skia/native 后端必须提供可访问性树或明确 unsupported 诊断。

**解释。** WCAG 合规既包含自动检查也需要人工审查；语言不能保证所有内容满足法规。

**正例。** IconButton 提供 label、keyboard activation、disabled state 和 focus ring。

**反例。** 只用颜色区分错误且没有 aria/语义状态，报告 X-E9010 missing accessible name。

**边界。** 平台原生控件能力不同；降级为非交互静态文本时必须保留错误提示和替代操作。

**诊断/测试/追溯。** X-E9010；TEST-STYLE-A11Y-001..008；来源 XLF-06-001、XLC-STYLE-013..015、XLE-AI-011；RFC-STYLE-A11Y-01（P5）。

### RULE-STYLE-007：SSR、隔离和安全

- maturity: EXTENDED
- status: 草案
- phase: P4

**规范性条文。** 样式生成不得执行任意代码、发起未声明网络请求或读取秘密。SSR 输出必须包含版本化 style IR/hash；客户端 hydration 检查 class/style 顺序和 nonce/CSP 兼容。动态 style 值必须 escape，禁止用户输入构造 selector 或 url 而未校验。

**解释。** style DSL 与模板注入有相同安全边界；CSP 由 Web 宿主配置，x-style 只能生成兼容制品。

**正例。** URL 属性通过 allowlist 和 safe URL constructor；SSR 输出带 style_version。

**反例。** 把用户字符串直接拼进 selector 或 style url，报告 X-E9011 style injection。

**边界。** CSS url、font、SVG、filter 和 WebView 协议须逐项列能力；不支持 CSP nonce 的后端应拒绝 inline fallback。

**诊断/测试/追溯。** X-E9011；TEST-STYLE-SEC-001..007；来源 XLF-06-003、XLF-11-006、XLC-STYLE-014、XLE-AI-004；RFC-STYLE-SEC-01（P4）。

## 3. Style IR 与平台矩阵

Style IR 的最小逻辑记录包含：版本、namespace/scope、selector 原文与 specificity、source span、有序声明、typed value、继承与 fallback、布局约束、动画取消策略、无障碍语义和 capability 降级原因。它是编译器内部契约，不要求作者手写 YAML/JSON；作者只编写 `.xs` 源码，调试器可以把 IR 以文本树形式输出。

```text
StyleRule Button::.label @ ui.xs:12..48
  selector specificity(0,1,0)
  color: Var(--fg, fallback=#000) -> Color
  layout: Flex(overflow=clip)
  animation: Static(reduced-motion)
  lowering: css-dom; fallbacks=[]
```

validation 必须检查 schema/version、selector scope、typed value、变量 DAG、specificity/cascade 顺序、布局约束、a11y 必填项和安全 URL。lowering contract 必须保留 `source_span`、winning declaration、fallback 原因和 capability；不支持的声明只能按显式 fallback 降级，否则返回 Unsupported 并阻止发布。

| 后端 | 支持 | 降级 | 必测 |
|---|---|---|---|
| CSS/DOM | selector/cascade/flex/grid/animation | legacy browser adapter | WPT、E2E、CSP |
| SSR | static style IR、critical CSS | deferred layout marker | hydration golden |
| Skia/Canvas | style IR 计算与绘制 | 无 DOM semantics 时 a11y tree/警告 | screenshot + a11y |
| Native | subset controls/layout | unsupported property diagnostic | 真机/模拟器 |
| WASM UI | host renderer adapter | serial layout | browser matrix |

每个平台必须记录 Tier、最低版本、字体/locale、GPU capability、色彩空间、a11y bridge、style hash 和 EOL。截图黄金只约束同一后端/环境的容差；跨后端用布局框、文本语义、交互和无障碍断言。

## 4. 测试、性能、回滚

tests/style 包含 selector/cascade/value/layout/motion/security/a11y 单测、CSS/WPT 对照、截图差分、响应式矩阵、SSR/hydration、恶意输入和人工 WCAG 复核。性能报告匹配规则时间、布局时间、重排次数、首屏/交互 P50/P95/P99、内存和生成 CSS 大小。

style IR 版本变更必须提供迁移器和旧渲染器；若降级结果违反安全或可访问性门禁，回滚整包而非静默丢样式。生产 HMR 不属于稳定承诺。

## 5. 待决 RFC

| RFC | 候选 | 门禁 | 最迟 |
|---|---|---|---|
| RFC-STYLE-SCOPE-01 | namespace/Shadow/isolation | selector golden、组件冲突 | P4 |
| RFC-STYLE-CASCADE-01 | CSS subset/legacy modes | WPT、多后端差分 | P4 |
| RFC-STYLE-VALUE-01 | typed values 与主题 | 单位、循环、SSR | P4 |
| RFC-STYLE-LAYOUT-01 | Flex/Grid IR | 容差、overflow、真机 | P4 |
| RFC-STYLE-MOTION-01 | cancel/reduced-motion | a11y、资源释放 | P5 |
| RFC-STYLE-A11Y-01 | 语义树与 WCAG 工具 | 自动+人工审计 | P5 |
| RFC-STYLE-SEC-01 | style CSP/URL policy | 注入、CSP、WebView | P4 |

原始材料中的“跨平台像素一致”、GPU 光栅化和 UI 编译期固定坐标只作为候选目标；没有同后端基准、a11y 和降级证据，不得上升为保证。
