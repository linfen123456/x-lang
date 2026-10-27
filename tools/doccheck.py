#!/usr/bin/env python3
"""X-Lang 文档体系自检（仅依赖 Python 标准库）。

用法：
  python3 tools/doccheck.py            # 生成 registry.md 并执行全部检查
  python3 tools/doccheck.py --check    # 只检查；生成物过期也视为失败（CI 使用）
  python3 tools/doccheck.py --old-matrix <旧追溯矩阵.md>   # 额外核对原始需求 100% 覆盖
退出码：0 = 全部通过；1 = 存在失败。
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASES = {"M0", "P0", "P1", "P2", "P3", "P4", "P5", "R"}
PHASE_ORDER = ["M0", "P0", "P1", "P2", "P3", "P4", "P5", "R"]
TRACKS = {"core", "toolchain", "eco", "labs"}
DISPOSITIONS = {"adopt", "adapt", "replace", "research"}
REQ_YAML = "docs/requirements/registry.yaml"
REQ_MD = "docs/requirements/registry.md"
DIAG_YAML = "specs/diagnostics/registry.yaml"
DIAG_MD = "specs/diagnostics/registry.md"
# 允许出现“已废止术语”的文件（迁移说明、变更日志本身就要提及旧名）
HISTORY_FILES = {"docs/migration.md", "docs/changelog.md"}

errors = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


# ---------------------------------------------------------------- 受限 YAML
def parse_flat_yaml(path):
    """解析“扁平记录列表”子集：`- key: value` 开始一条记录，`  key: value` 续行；# 注释。"""
    records, cur = [], None
    with open(path, encoding="utf-8") as f:
        for no, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = re.match(r"^(- |  )([a-z_]+): (.*)$", line)
            if not m:
                err(f"{path}:{no}", f"无法解析的 YAML 行：{line!r}")
                continue
            lead, key, val = m.groups()
            val = val.strip()
            if val.startswith('"'):
                if not (val.endswith('"') and len(val) >= 2):
                    err(f"{path}:{no}", "引号未闭合")
                val = val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
            if lead == "- ":
                cur = {"_line": no}
                records.append(cur)
            elif cur is None:
                err(f"{path}:{no}", "续行出现在记录之前")
                continue
            if key in cur:
                err(f"{path}:{no}", f"字段重复：{key}")
            cur[key] = val
    return records


# ---------------------------------------------------------------- 生成
def md_escape(s):
    return s.replace("|", "\\|").replace("\n", " ")


def gen_requirements(recs):
    out = [
        "# 原始需求登记册（生成物）",
        "",
        "> 类型：Register｜**由 `tools/doccheck.py` 从 [registry.yaml](registry.yaml) 生成，请勿手改。** 字段含义见 [vision](../vision.md) §5–6；阶段定义见 [roadmap](../roadmap.md)。",
        "",
        "## 1. 统计",
        "",
    ]
    def count(field, keys):
        return " ｜ ".join(f"{k} {sum(1 for r in recs if r.get(field) == k)}" for k in keys)
    out += [
        f"- 总数：{len(recs)}",
        f"- 轨道：{count('track', ['core', 'toolchain', 'eco', 'labs'])}",
        f"- 处置：{count('disposition', ['adopt', 'adapt', 'replace', 'research'])}",
        f"- 首次交付阶段：{count('phase', PHASE_ORDER)}",
        "",
        "## 2. 不可行或不进核心条目（replace / research）及理由",
        "",
        "| ID | 原始诉求 | 处置 | 替代落点 | 理由 / 说明 |",
        "|---|---|---|---|---|",
    ]
    for r in recs:
        if r.get("disposition") in ("replace", "research"):
            out.append(f"| {r['id']} | {md_escape(r['title'])} | {r['disposition']} | {md_escape(r['landing'])} | {md_escape(r['note'])} |")
    out += ["", "## 3. 全量表", "",
            "| ID | 标题 | 来源 | 轨道 | 阶段 | 完成 | 处置 | 落点 | 说明 |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        out.append("| " + " | ".join(md_escape(r.get(k, "")) for k in
                   ["id", "title", "source", "track", "phase", "done", "disposition", "landing", "note"]) + " |")
    return "\n".join(out) + "\n"


def gen_diagnostics(recs):
    out = [
        "# 诊断码登记册（生成物）",
        "",
        "> 类型：Register｜**由 `tools/doccheck.py` 从 [registry.yaml](registry.yaml) 生成，请勿手改。** 码段：0xxx 驱动｜1xxx 词法/语法/属性｜2xxx 名称/模块/模式｜3xxx 类型/Trait/求值｜4xxx 所有权/借用｜5xxx 错误/终止｜6xxx unsafe/FFI｜7xxx 并发｜8xxx 包/构建｜9xxx 阶段门禁｜X-W 为 lint。码一经分配永不复用。",
        "",
        f"共 {len(recs)} 个码。",
        "",
        "| 码 | 含义 | 阶段 | 规则 | 规范 |",
        "|---|---|---|---|---|",
    ]
    for r in recs:
        rel = os.path.relpath(os.path.join(ROOT, r["spec"]), os.path.join(ROOT, "specs/diagnostics")).replace(os.sep, "/")
        out.append(f"| `{r['code']}` | {md_escape(r['title'])} | {r['phase']} | {r['rule']} | [{os.path.basename(r['spec'])}]({rel}) |")
    return "\n".join(out) + "\n"


def write_or_check(rel, content, check_only):
    path = os.path.join(ROOT, rel)
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old == content:
        return
    if check_only:
        err(rel, "生成物已过期，请运行 python3 tools/doccheck.py")
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


# ---------------------------------------------------------------- 检查
def md_files():
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [name for name in dirs if name not in {".git", "archive"}]
        for f in fs:
            if f.endswith(".md"):
                yield os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")


def check_requirements(recs, old_matrix):
    seen = set()
    for r in recs:
        where = f"{REQ_YAML}:{r['_line']}"
        for k in ["id", "title", "source", "track", "phase", "done", "disposition", "landing", "note"]:
            if not r.get(k):
                err(where, f"缺少字段 {k}")
        rid = r.get("id", "")
        if not re.fullmatch(r"XLF-\d{2}-\d{3}", rid):
            err(where, f"ID 格式非法：{rid}")
        if rid in seen:
            err(where, f"ID 重复：{rid}")
        seen.add(rid)
        if r.get("track") not in TRACKS:
            err(where, f"track 非法：{r.get('track')}")
        for k in ("phase", "done"):
            if r.get(k) not in PHASES:
                err(where, f"{k} 非法：{r.get(k)}")
        if r.get("phase") in PHASES and r.get("done") in PHASES and \
                PHASE_ORDER.index(r["done"]) < PHASE_ORDER.index(r["phase"]):
            err(where, "done 早于 phase")
        if r.get("disposition") not in DISPOSITIONS:
            err(where, f"disposition 非法：{r.get('disposition')}")
        if r.get("disposition") in ("replace", "research") and r.get("note", "—") in ("", "—"):
            err(where, f"{rid} 为 {r.get('disposition')}，必须在 note 中写明理由")
        if r.get("disposition") == "research" and r.get("track") != "labs":
            err(where, f"{rid} 为 research，track 必须是 labs")
        if not re.fullmatch(r"\d{1,2}\.txt([、+]\d{1,2}\.txt)*|新增：.+", r.get("source", "")):
            err(where, f"source 格式非法：{r.get('source')}")
    if old_matrix:
        text = open(old_matrix, encoding="utf-8").read()
        old_ids = set(re.findall(r"XLF-\d{2}-\d{3}", text))
        missing = sorted(old_ids - seen)
        if missing:
            err(REQ_YAML, f"原始需求缺少归宿：{', '.join(missing)}")
        return len(old_ids), len(old_ids & seen)
    return None, None


def check_diagnostics(recs):
    seen = set()
    for r in recs:
        where = f"{DIAG_YAML}:{r['_line']}"
        code = r.get("code", "")
        if not re.fullmatch(r"X-[EW]\d{4}", code):
            err(where, f"码格式非法：{code}")
        if code in seen:
            err(where, f"码重复：{code}")
        seen.add(code)
        if r.get("phase") not in PHASES:
            err(where, f"phase 非法：{r.get('phase')}")
        spec = r.get("spec", "")
        sp = os.path.join(ROOT, spec)
        if not os.path.isfile(sp):
            err(where, f"spec 文件不存在：{spec}")
            continue
        rule = r.get("rule", "")
        if not re.fullmatch(r"(RULE|LINT)-[A-Z0-9]+(-[A-Z0-9]+)*", rule):
            err(where, f"rule 格式非法：{rule}")
        if rule not in open(sp, encoding="utf-8").read():
            err(where, f"规则 {rule} 未出现在 {spec}")
    return seen


LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
FORBIDDEN = [
    (re.compile(r"(?:[:<,&(]|->)\s*(?:mut\s+)?(I8|I16|I32|I64|I128|U8|U16|U32|U64|U128|ISize|USize|F32|F64|Bool|Unit|Str|Char|Never)\b"), "大写原始类型名（应使用小写，见 ADR-0007 D1）"),
    (re.compile(r"\bmap_err\b"), "`map_err`（唯一名称为 `map_error`）"),
    (re.compile(r"\bexport_function\b"), "`export_function`（已删除，使用 @export）"),
    (re.compile(r"\b(?:G[0-6]|R[0-5]|D0|P6|P7)\b"), "已废止或未定义的阶段名（仅允许 M0、P0–P5、R）"),
    (re.compile(r"右侧先求值"), "旧求值顺序表述"),
    (re.compile(r"待用户决定|待指定|【待决】|开放问题"), "未关闭的开放问题（ADR-0008 要求清零；确需未来数据的写成“决策时点”）"),
]
OBSOLETE_OK = re.compile(r"废止|作废|旧")
SECREF_RE = re.compile(r"\]\(([^)\s]+\.md)\)\s*§(\d+(?:\.\d+)?)")
_sections = {}


def has_section(path, sec):
    if path not in _sections:
        heads = set()
        for l in open(path, encoding="utf-8"):
            m = re.match(r"^#{2,4} (\d+(?:\.\d+)?)[.\s]", l)
            if m:
                heads.add(m.group(1))
        _sections[path] = heads
    return sec in _sections[path]


def check_markdown(diag_codes):
    files = sorted(md_files())
    n_links = 0
    used_codes = set()
    for rel in files:
        path = os.path.join(ROOT, rel)
        lines = open(path, encoding="utf-8").read().split("\n")
        # 头部
        if not lines or not lines[0].startswith("# "):
            err(rel, "第一行必须是一级标题")
        in_code = False
        for no, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_code = not in_code
            # 链接
            if not in_code:
                for target in LINK_RE.findall(line):
                    if re.match(r"^[a-z]+://|^mailto:", target):
                        continue
                    n_links += 1
                    file_part = target.split("#", 1)[0]
                    if not file_part:
                        continue
                    tp = os.path.normpath(os.path.join(os.path.dirname(path), file_part))
                    if not os.path.exists(tp):
                        err(f"{rel}:{no}", f"失效链接：{target}")
                    elif not tp.startswith(ROOT):
                        err(f"{rel}:{no}", f"链接越出文档根：{target}")
                # 章节引用：[x](file.md) §N 或 §N.M 必须指向存在的标题
                for target, sec in SECREF_RE.findall(line):
                    tp = os.path.normpath(os.path.join(os.path.dirname(path), target.split("#", 1)[0]))
                    if os.path.isfile(tp) and not has_section(tp, sec):
                        err(f"{rel}:{no}", f"章节引用不存在：{target} §{sec}")
            # 诊断码
            for c in re.findall(r"X-[EW]\d{4}", line):
                used_codes.add(c)
                if c not in diag_codes:
                    err(f"{rel}:{no}", f"未登记的诊断码：{c}")
            # 术语
            if rel in HISTORY_FILES:
                continue
            for rx, why in FORBIDDEN:
                if rx.search(line) and not OBSOLETE_OK.search(line):
                    err(f"{rel}:{no}", f"禁用术语 {why}：{line.strip()[:80]}")
    return len(files), n_links, used_codes


def check_rule_refs():
    """文档中引用的每个 RULE-* 都必须在 specs/ 或设计文档中以 [RULE-…] 或规则表行的形式定义。"""
    defined, refs = set(), {}
    for rel in md_files():
        text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        for rid in re.findall(r"\[(RULE-[A-Z0-9\-]+)\]", text):
            defined.add(rid)
        for rid in re.findall(r"^\|\s*(RULE-[A-Z0-9\-]+)\s*\|", text, re.M):
            defined.add(rid)
        for rid in re.findall(r"RULE-[A-Z0-9]+(?:-[A-Z0-9]+)*(?:-\*)?", text):
            refs.setdefault(rid, rel)
    for rid, rel in sorted(refs.items()):
        if rid.endswith("-*"):  # 通配引用，如 RULE-MOD-*：至少要有一条已定义规则匹配
            prefix = rid[:-1]
            if not any(d.startswith(prefix) for d in defined):
                err(rel, f"通配规则 {rid} 没有任何已定义规则匹配")
            continue
        if rid not in defined:
            err(rel, f"规则 {rid} 被引用但未定义")
    return len(defined)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--old-matrix")
    a = ap.parse_args()

    req = parse_flat_yaml(os.path.join(ROOT, REQ_YAML))
    diag = parse_flat_yaml(os.path.join(ROOT, DIAG_YAML))
    old_total, old_cov = check_requirements(req, a.old_matrix)
    codes = check_diagnostics(diag)
    write_or_check(REQ_MD, gen_requirements(req), a.check)
    write_or_check(DIAG_MD, gen_diagnostics(diag), a.check)
    n_files, n_links, used = check_markdown(codes)
    n_rules = check_rule_refs()

    print(f"文件 {n_files} 个｜内部链接 {n_links} 条｜需求 {len(req)} 条｜诊断码 {len(codes)} 个（文档中引用 {len(used)} 个）｜已定义规则 {n_rules} 条")
    if old_total is not None:
        print(f"原始需求覆盖：{old_cov}/{old_total}（{100.0 * old_cov / max(old_total, 1):.1f}%）")
    unused = sorted(codes - used)
    if unused:
        print(f"提示：{len(unused)} 个诊断码只在登记册中出现：{', '.join(unused[:20])}{' …' if len(unused) > 20 else ''}")
    if errors:
        print(f"\n失败 {len(errors)} 项：")
        for e in errors:
            print("  - " + e)
        return 1
    print("全部检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
