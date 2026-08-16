---
doc_id: DOC-GOVERNANCE-README
authority: master
owner: role/documentation
backup_owner: role/architecture
version: "2.0.0"
maturity: CORE
status: 已决策
phase: P0
last_reviewed: 2026-08-16
traceability_scope: [GOVERNANCE, XLF, XLC, XLE, REVIEW]
---
# X-Lang 文档治理与证据规范

本目录定义文档治理规则。当前阶段以经过评审的 Markdown 正文、RFC/ADR 和实际测试证据为事实来源；少量 YAML 仅是字段示例，不覆盖正文决策，也不能代替测试。任何“已完成”声明必须能够沿下列关系人工核查，进入实现阶段后再逐步自动化：

`source → spec_or_rfc → project → test → phase/status → evidence`

## 权威顺序与不可变边界

1. `docs/原始文档/1.txt` 至 `12.txt` 是不可改的历史输入。文档阶段通过 Git 差异确认这 12 个文件没有改动；建立正式发布流水线时再生成并签署来源哈希清单。
2. 8 份主大纲分别承载规范、架构、对标、追溯、复审和工程风险事实；专题文档只能解释或链接，不能悄然改写结论。
3. 历史遗留的[文档元数据约定](document-metadata-schema.yaml)、[追溯字段约定](traceability-manifest.yaml)和[项目登记示例](project-registry.yaml)只提供辅助字段参考，不是本阶段交付主体，也不覆盖 Markdown 正文。新增专题不要求创建新的 YAML/JSON；字段能以可读 Markdown 元数据块表达时优先使用正文。
4. RFC/ADR 记录冲突和变更原因；状态只能沿状态机迁移，不能直接编辑成“已稳定”。

## 统一文档契约

专题 Markdown 使用“YAML front matter 或标题后的可读 Markdown 元数据块”记录 `doc_id/authority/owner/version/maturity/status/phase/last_reviewed/traceability_scope`；两种形式语义相同，不要求为了机器格式复制正文。8 份 `docs/X-Lang*.md` 主大纲继续使用文件开头的可读元数据块。所有文档都必须记录版本、状态、日期、职责和权威引用。定义表的 XLF/XLC/XLE ID 只能出现在各自权威矩阵；复审表重复引用是边，不是新定义。

专题完成定义（DoD）包含：目标和非目标、术语、输入/输出契约、正反例、边界与失败语义、性能预算或明确“尚无基线”、安全边界、兼容/迁移、canonical 测试 ID、回滚、Owner/备份 Owner、来源和证据状态。尚无实现时证据必须写 `planned`，不得填写不存在的文件或运行结果。缺一项只能标记为 `草案` 或 `待决策`。

## 可执行检查

评审时按“标题层级与链接、术语与状态、318 项需求和 87 项复审映射、原始 12 份资料未改动”四组检查表逐项确认。当前阶段不维护专用校验程序，避免工具代码取代正文建设。

检查只能读取文档，不得自动改写或生成正文。失败时记录具体文件、行号和缺失关系，禁止以重试掩盖失败。

## 变更流程

提出者先创建 RFC/ADR 和影响范围，补齐追溯说明，再以最小增量修改专题。评审至少覆盖规范、实现、质量、安全和运维五个视角；合并前检查 Markdown 结构与链接、定义计数、追溯抽样以及 `git diff -- docs/原始文档` 为空。重大决策必须有替代方案、后果、迁移和回滚，旧 ADR 不删除。
