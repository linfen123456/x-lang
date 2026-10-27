> 已归档：见 v2 [docs/testing.md](../../../../docs/testing.md)

# 符合性与门禁实现设计

> 状态：Proposed｜日期：2026-08-18  
> 关闭：G3、工程大纲第九篇 / P0 检查点 / 波次 A 证据  
> 落点：`conformance/` crate + `tests/conformance/`

## 1. 目标

把「规范规则 → 自动语料 → PR/发布门禁」变成可执行契约，避免 Proposed RFC 与实现脱节。

## 2. 目录约定

```text
tests/conformance/
  p0/
    compile-pass/
    compile-fail/
    run-pass/
    run-fail/
  meta/
    manifest.toml          # P0 --gate p0 必需：冻结必需语料 ID、Rule ID 和豁免
```

单条语料推荐布局：

```text
tests/conformance/p0/compile-fail/e3008_assign_to_call/
  main.x
  expected.toml            # code, rule_id, span_hint?, stage
```

`expected.toml` 最小字段：

```toml
id = "CONF-P0-E3008-001"
rule_ids = ["RULE-EVAL-PLACE"]
codes = ["X-E3008"]
kind = "compile-fail"      # compile-pass|compile-fail|run-pass|run-fail
stage = "p0"               # p0|p1|p2|...
```

P0 门禁的 `meta/manifest.toml` 必须在评审后列明必需 case ID、Rule ID/诊断码及对应 RFC 版本（或提交）；Runner 比对发现集与 manifest，缺失、重名或意外豁免均失败。M0–M3 可以报告模式使用不完整 manifest，不能作为最终 P0 通过证据。豁免至少记录 Issue、Owner、原因、到期阶段和审批者；任何必需安全/语义规则不得以永久跳过关闭。

## 3. Runner 行为

`conformance` 或 `x test conformance`：

1. 加载必需的 gate manifest，发现 `**/expected.toml` 并检查必需 ID、重复 ID 和 RFC/Rule ID 映射；
2. 按 `kind` 调用 driver：`check` / `build` / `run`；
3. `compile-fail`：必须失败，且诊断集合 ⊇ `codes`（允许额外 note，禁止缺主码）；
4. `compile-pass`/`run-pass`：退出码 0；`run-pass` 可校对 stdout fixture；
5. 汇总 JSON：`{ passed, failed, skipped, by_rule_id }`；
6. `--gate p0` 遇到失败、缺少/重复必需语料、未授权跳过/豁免、缺少报告或 runner 无法启动时返回非 0，不得将其计为通过。

阶段过滤：`--stage p0` 只跑 `stage <= p0` 映射表（P0 仅 `p0`）。

## 4. Rule ID 追溯报告

每次门禁产出 `target/x/conformance-report.json`：

| 字段 | 含义 |
|---|---|
| `rule_id` | RFC 中的 RULE-* |
| `status` | covered / missing / waived |
| `tests` | 语料 id 列表 |
| `rfc` | 如 RFC-0006 |

P0 门禁要求：设计声明并经对应 RFC 登记的 P0 诊断码（见语义管线 §5 的 P0 子集）`covered == 100%`；仍为临时代码或无 Rule ID 的用例不能满足门禁。`waived` 必须有 Issue 链接与到期阶段。

## 5. P0 门禁清单（可勾选）

### 5.1 构建与探针

- [ ] LLVM 探针通过（ADR-0004）；
- [ ] Hello World `run-pass`；
- [ ] ABI 标量/结构体 harness（GAP-COMP-01）；
- [ ] Workspace 成员数 ≤ 5（GAP-COMP-02）；
- [ ] 三包 Path Workspace 经同一 ResolvedGraph → Action DAG → LLVM 链接运行；随机化目录枚举顺序后图字节一致；`-O0` 与首个启用优化级别的可观察输出/终止类别一致。

### 5.2 语言语料（最小集）

| 语料意图 | kind | 代码 |
|---|---|---|
| Hello | run-pass | — |
| 公开 fn 缺返回类型 | compile-fail | X-E3001 |
| 向调用结果赋值 | compile-fail | X-E3008 |
| 未实现语法（如 defer） | compile-fail | X-E9001 候选；最终 P0 前须在 RFC-0005 登记规则和诊断码 |
| 非 Copy use-after-move（若 P0 启用） | compile-fail | X-E4001 |

### 5.3 治理

- [ ] 报告中无「静默跳过」的 Tier 主机测试；
- [ ] 失败保留 `diagnostics.json` 与命令行；
- [ ] 总纲已排除的 P0 语法（如 `defer`）须由编译器明确拒绝并有语料；ADR-0003 仍为 Proposed，其额外剖面约束须经评审接受后才能作为独立阻断依据。

## 6. PR 门禁映射

| 检查 | 阻断 |
|---|---|
| `fmt` + `clippy`（宿主机） | 是 |
| `x test conformance --stage p0 --gate p0` | P0 最终检查点起阻断；此前 M0–M3 可仅报告，不得据此宣称 P0 通过 |
| fuzz lexer/parser 冒烟 | P0 建议；P1 阻断崩溃 |
| 完整平台矩阵 | P1+ |

P0 期间允许「仅 Linux 或仅 Windows 主机」单平台绿；但报告必须标明非 Tier1 承诺。最终 P0 还须三包端到端证据；失败或静默跳过不可标记完成。

## 7. 与 RFC Accept 的关系

- 语料通过 **不能** 单独把 RFC 标为 Accepted；
- Accept 仍需：规则完整、审查者签字、未决问题关闭（见 `rfcs/README.md`）；
- 但缺少对应语料的 RFC **不得** Stable。

## 8. 验收

- [ ] `conformance` 可在无手写路径硬编码下发现语料；
- [ ] 故意破坏 Hello World 时门禁失败；
- [ ] 报告含 Rule ID 覆盖率；
- [ ] 本文清单与 [p0-vertical-slice.md §9](p0-vertical-slice.md) 交叉引用无矛盾。
