#!/usr/bin/env python3
"""Filter VulnGym to the human-verified entry subset.

This script is intended for the experiment fork. It keeps only entries with
verify == 1, re-aggregates reports.jsonl accordingly, and writes an audit
record of retained and removed rows.
"""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RECORDS = ROOT / "records"

SUMMARY_JSON = RECORDS / "cleaned_verify1_20260608_summary.json"
SUMMARY_MD = RECORDS / "cleaned_verify1_20260608.md"


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")


def pct(num: int, den: int) -> str:
    return f"{num / den * 100:.1f}%" if den else "0.0%"


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    s = text.index(start)
    e = text.index(end, s)
    return text[:s] + replacement.rstrip() + "\n\n" + text[e:]


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(out)


def normalize_l2(label: str) -> str:
    return label.split("(", 1)[0]


def group_traditional_l1(label: str) -> str:
    path_file = {
        "路径穿越",
        "文件操作安全",
        "路径遍历 / 任意文件读取",
        "越界文件读取",
        "路径遍历 / 越权写入",
    }
    if label in path_file:
        return "Path Traversal / File ops"
    if label == "代码注入":
        return "Code Injection"
    if label == "命令注入":
        return "Command Injection"
    if label == "认证绕过":
        return "Authentication Bypass"
    if label in {"反序列化", "反序列化漏洞"}:
        return "Deserialization"
    if label == "沙箱逃逸":
        return "Sandbox Escape"
    if label == "模板注入":
        return "Template Injection"
    if label == "供应链攻击":
        return "Supply Chain"
    if label == "权限绕过":
        return "Authorization Bypass"
    if label == "注入类":
        return "Injection"
    if label == "注入与反序列化":
        return "Injection / Deserialization"
    if label == "原型链污染":
        return "Prototype Pollution"
    return label


def group_traditional_l1_zh(label: str) -> str:
    path_file = {
        "路径穿越",
        "文件操作安全",
        "路径遍历 / 任意文件读取",
        "越界文件读取",
        "路径遍历 / 越权写入",
    }
    if label in path_file:
        return "路径穿越/文件操作"
    if label == "代码注入":
        return "代码注入"
    if label == "命令注入":
        return "命令注入"
    if label == "认证绕过":
        return "认证绕过"
    if label in {"反序列化", "反序列化漏洞"}:
        return "反序列化"
    if label == "沙箱逃逸":
        return "沙箱逃逸"
    if label == "模板注入":
        return "模板注入"
    if label == "供应链攻击":
        return "供应链"
    return label


def build_readme_distribution(
    report_category: dict[str, tuple[str, str]],
    *,
    zh: bool,
) -> str:
    total_reports = len(report_category)
    business = {rid: cat for rid, cat in report_category.items() if cat[0] == "业务逻辑"}
    traditional = {rid: cat for rid, cat in report_category.items() if cat[0] != "业务逻辑"}

    business_l2 = Counter(normalize_l2(cat[1]) for cat in business.values())
    if zh:
        traditional_l1 = Counter(group_traditional_l1_zh(cat[0]) for cat in traditional.values())
        business_heading = (
            f"**业务逻辑类 ({len(business)} / {total_reports}, {pct(len(business), total_reports)}) "
            "— `vuln_category_l2` 分布：**"
        )
        traditional_heading = (
            f"**传统漏洞类 ({len(traditional)} / {total_reports}, {pct(len(traditional), total_reports)}) "
            "— 主要 `vuln_category_l1` 分布：**"
        )
        business_headers = ["二级分类", "漏洞数", "占比"]
        traditional_headers = ["类别", "漏洞数", "占比"]
        intro = (
            "每条数据包含两级分类字段：`vuln_category_l1`（粗粒度类型）和\n"
            "`vuln_category_l2`（细粒度子类型）。在当前 cleaned subset 中，"
            f"**{len(business)} / {total_reports} ({pct(len(business), total_reports)})** "
            "的漏洞为业务逻辑类，其余 "
            f"**{len(traditional)} / {total_reports} ({pct(len(traditional), total_reports)})** "
            "覆盖传统漏洞类型。完整数据模型与字段定义详见 [`SCHEMA.md`](SCHEMA.md)。"
        )
        note = (
            "> 注：一个漏洞（Advisory）可能对应多个入口（Entry）——下表按 "
            "**漏洞数** 统计，而非入口数。"
        )
        future = "> 后续版本将持续扩展更多漏洞类别与项目覆盖"
    else:
        traditional_l1 = Counter(group_traditional_l1(cat[0]) for cat in traditional.values())
        business_heading = (
            f"**Business-logic advisories ({len(business)} / {total_reports}, "
            f"{pct(len(business), total_reports)}) — `vuln_category_l2` breakdown:**"
        )
        traditional_heading = (
            f"**Traditional vulnerability advisories ({len(traditional)} / {total_reports}, "
            f"{pct(len(traditional), total_reports)}) — top `vuln_category_l1`:**"
        )
        business_headers = ["Sub-category", "Advisories", "% of BL"]
        traditional_headers = ["Category", "Advisories", "% of Trad."]
        intro = (
            "Every entry carries a two-level classification: `vuln_category_l1`\n"
            "(coarse type) and `vuln_category_l2` (fine-grained sub-type). In this\n"
            f"cleaned subset, **{len(business)} / {total_reports} "
            f"({pct(len(business), total_reports)})** advisories are business-logic\n"
            f"vulnerabilities; the remaining **{len(traditional)} / {total_reports} "
            f"({pct(len(traditional), total_reports)})** cover traditional vulnerability\n"
            "types. Full data model and field definitions are in [`SCHEMA.md`](SCHEMA.md)."
        )
        note = (
            "> Note: one advisory may map to multiple entries — the counts below\n"
            "> are by **advisory (vulnerability)**, not by entry."
        )
        future = "> Future releases will continue expanding vulnerability categories and project coverage."

    business_rows = [
        [label, count, pct(count, len(business))]
        for label, count in business_l2.most_common()
    ]
    traditional_rows = [
        [label, count, pct(count, len(traditional))]
        for label, count in traditional_l1.most_common()
    ]

    return "\n\n".join(
        [
            "### " + ("漏洞类型分布" if zh else "Vulnerability type distribution"),
            intro,
            note,
            business_heading,
            md_table(business_headers, business_rows),
            "<br>",
            traditional_heading,
            md_table(traditional_headers, traditional_rows),
            future,
        ]
    )


def update_readme(
    path: Path,
    stats: dict[str, Any],
    report_category: dict[str, tuple[str, str]],
    *,
    zh: bool,
) -> None:
    text = path.read_text(encoding="utf-8")
    if zh:
        if "2026-06-08" not in text.split("## 📢 最新动态", 1)[1].split("## 目录", 1)[0]:
            text = text.replace(
                "## 📢 最新动态\n",
                "## 📢 最新动态\n"
                "- **2026-06-08** — 🧹 cleaned fork：仅保留 `verify = 1` 的人工审计入口，"
                f"数据集规模调整为 **{stats['reports_after']} reports / {stats['entries_after']} entries**；"
                "部分 verified 的 advisory 已按保留 entry 重新计算 `entry_ids` 和 `num_entries`。\n",
            )
        data_scale = f"""### 数据规模

| 指标 | 数值 |
|---|---|
| Advisory 数（reports） | **{stats['reports_after']}** |
| 可达入口数（entries） | **{stats['entries_after']}** |
| 涉及项目数 | {stats['projects_after']} |
| 涉及仓库数 | {stats['repos_after']} |
| 人工审计通过的入口（`verify = 1`） | **{stats['entries_after']} / {stats['entries_after']} (100.0%)** |
| 人工审计通过的 advisory（至少一条入口已审计） | **{stats['reports_after']} / {stats['reports_after']} (100.0%)** |"""
        audit_status = f"""### 人工审计状态

自 v0.1.1 起，`entries.jsonl` 中每条记录均包含 `verify` 字段（`int`，取值 `0` 或 `1`）。

当前 cleaned fork 已经将 `data/entries.jsonl` 过滤为仅包含 `verify == 1` 的人工审计入口；
`data/reports.jsonl` 也已重新聚合，使 `entry_ids` 和 `num_entries` 仅指向保留的 verified entries。
上游 v0.1.2 中 `verify == 0` 的入口不包含在本分支的数据文件中，删除和保留明细记录在
`records/cleaned_verify1_20260608.md` 与 `records/cleaned_verify1_20260608_summary.json`。

过滤前，上游 v0.1.2 包含 **{stats['reports_before']} reports / {stats['entries_before']} entries**，
其中 **{stats['verified_entries_before']}** 条 entry、**{stats['verified_reports_before']}** 条 report 至少包含一条 verified entry。
过滤后，本分支保留 **{stats['reports_after']} reports / {stats['entries_after']} entries**。
其中 **{stats['partial_reports_before']}** 条原本部分 verified 的 report 已删除未验证 entry 并重算聚合字段。"""
        text = replace_section(text, "### 数据规模", "### 人工审计状态", data_scale)
        text = replace_section(text, "### 人工审计状态", "### 漏洞类型分布", audit_status)
        text = replace_section(
            text,
            "### 漏洞类型分布",
            "## 📈 基线评测结果",
            build_readme_distribution(report_category, zh=True),
        )
    else:
        if "2026-06-08" not in text.split("## 📢 What's New", 1)[1].split("## Table of Contents", 1)[0]:
            text = text.replace(
                "## 📢 What's New\n",
                "## 📢 What's New\n"
                "- **2026-06-08** — 🧹 cleaned fork: retained only human-audited `verify = 1` entries, "
                f"reducing the dataset to **{stats['reports_after']} reports / {stats['entries_after']} entries**; "
                "partially verified advisories were re-aggregated to the retained `entry_ids` and `num_entries`.\n",
            )
        data_scale = f"""### Data scale

| Metric | Value |
|---|---|
| Advisories (reports) | **{stats['reports_after']}** |
| Reachable entry points (entries) | **{stats['entries_after']}** |
| Distinct projects | {stats['projects_after']} |
| Distinct repositories | {stats['repos_after']} |
| Human-audited entries (`verify = 1`) | **{stats['entries_after']} / {stats['entries_after']} (100.0 %)** |
| Human-audited advisories (≥ 1 verified entry) | **{stats['reports_after']} / {stats['reports_after']} (100.0 %)** |"""
        audit_status = f"""### Human audit status

Starting in v0.1.1, every row in `entries.jsonl` carries a `verify` field
(`int`, `0` or `1`).

This cleaned fork has already filtered `data/entries.jsonl` to rows with
`verify == 1`. `data/reports.jsonl` has also been re-aggregated so that
`entry_ids` and `num_entries` refer only to retained verified entries. Upstream
v0.1.2 rows with `verify == 0` are not present in this branch's data files;
retained and removed rows are recorded in `records/cleaned_verify1_20260608.md`
and `records/cleaned_verify1_20260608_summary.json`.

Before filtering, upstream v0.1.2 contained **{stats['reports_before']} reports /
{stats['entries_before']} entries**, with **{stats['verified_entries_before']}**
verified entries across **{stats['verified_reports_before']}** reports. After
filtering, this branch retains **{stats['reports_after']} reports /
{stats['entries_after']} entries**. The **{stats['partial_reports_before']}**
originally partially verified reports have had unverified entries removed and
their aggregate fields recomputed."""
        text = replace_section(text, "### Data scale", "### Human audit status", data_scale)
        text = replace_section(text, "### Human audit status", "### Vulnerability type distribution", audit_status)
        text = replace_section(
            text,
            "### Vulnerability type distribution",
            "## 📈 Baseline evaluation results",
            build_readme_distribution(report_category, zh=False),
        )
    path.write_text(text, encoding="utf-8", newline="\n")


def update_schema(path: Path, stats: dict[str, Any]) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"- `data/reports\.jsonl` — \d+ rows, one per GitHub Advisory \(report-level\)\.",
        f"- `data/reports.jsonl` — {stats['reports_after']} rows, one per retained GitHub Advisory (report-level).",
        text,
    )
    text = re.sub(
        r"- `data/entries\.jsonl` — \d+ rows, one per reachable entry point\.",
        f"- `data/entries.jsonl` — {stats['entries_after']} rows, one per retained human-verified reachable entry point.",
        text,
    )
    marker = "Join key: `entries.report_id == reports.report_id`.\n"
    note = (
        "\nCleaned fork note: this branch filters upstream v0.1.2 to entries with "
        "`verify == 1`. Reports with no retained verified entries are removed; "
        "partially verified reports are re-aggregated so `entry_ids` and "
        "`num_entries` refer only to retained entries.\n"
    )
    if "Cleaned fork note:" not in text:
        text = text.replace(marker, marker + note)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_changelog(path: Path, stats: dict[str, Any]) -> None:
    text = path.read_text(encoding="utf-8")
    if "[0.1.2-cleaned-verify1]" in text:
        path.write_text(text, encoding="utf-8", newline="\n")
        return
    entry = f"""
## [0.1.2-cleaned-verify1] — 2026-06-08

Experiment fork cleanup — retain only human-audited VulnGym entries for formal
benchmark runs.

### Changed
- Filtered `data/entries.jsonl` from **{stats['entries_before']} → {stats['entries_after']}**
  rows by keeping only `verify = 1`.
- Filtered `data/reports.jsonl` from **{stats['reports_before']} → {stats['reports_after']}**
  rows by removing reports with no retained verified entries.
- Recomputed `entry_ids` and `num_entries` for **{stats['partial_reports_before']}**
  originally partially verified reports.

### Records
- `records/cleaned_verify1_20260608.md`
- `records/cleaned_verify1_20260608_summary.json`

"""
    text = text.replace("\n## [0.1.2] — 2026-05-31", entry + "## [0.1.2] — 2026-05-31")
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    branch = run_git(["branch", "--show-current"])
    baseline_commit = run_git(["rev-parse", "HEAD"])

    reports_before = load_jsonl(DATA / "reports.jsonl")
    entries_before = load_jsonl(DATA / "entries.jsonl")

    reports_by_id = {r["report_id"]: r for r in reports_before}
    entries_by_report: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries_before:
        entries_by_report[entry["report_id"]].append(entry)

    verified_entries = [e for e in entries_before if e.get("verify") == 1]
    removed_entries = [e for e in entries_before if e.get("verify") != 1]

    verified_ids_by_report: dict[str, list[str]] = defaultdict(list)
    verified_entries_by_report: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in verified_entries:
        verified_ids_by_report[entry["report_id"]].append(entry["entry_id"])
        verified_entries_by_report[entry["report_id"]].append(entry)

    retained_report_ids = sorted(verified_ids_by_report)
    deleted_report_ids = sorted(set(reports_by_id) - set(retained_report_ids))
    partial_report_ids = sorted(
        rid
        for rid in retained_report_ids
        if len(verified_ids_by_report[rid]) != len(entries_by_report[rid])
    )

    retained_reports: list[dict[str, Any]] = []
    for report in reports_before:
        rid = report["report_id"]
        if rid not in verified_ids_by_report:
            continue
        updated = dict(report)
        updated["entry_ids"] = sorted(verified_ids_by_report[rid])
        updated["num_entries"] = len(updated["entry_ids"])
        retained_reports.append(updated)

    retained_entries = [e for e in entries_before if e.get("verify") == 1]

    projects_after = len({r["project"] for r in retained_reports})
    repos_after = len({r["repo_url"] for r in retained_reports})
    report_category: dict[str, tuple[str, str]] = {}
    for rid, rows in verified_entries_by_report.items():
        first = sorted(rows, key=lambda e: e["entry_id"])[0]
        report_category[rid] = (first["vuln_category_l1"], first["vuln_category_l2"])

    stats = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "branch": branch,
        "baseline_commit_before_cleaning": baseline_commit,
        "reports_before": len(reports_before),
        "entries_before": len(entries_before),
        "verified_entries_before": len(verified_entries),
        "verified_reports_before": len(retained_report_ids),
        "reports_after": len(retained_reports),
        "entries_after": len(retained_entries),
        "removed_reports": len(deleted_report_ids),
        "removed_entries": len(removed_entries),
        "partial_reports_before": len(partial_report_ids),
        "projects_after": projects_after,
        "repos_after": repos_after,
    }

    summary = {
        "stats": stats,
        "retained_reports": [
            {
                "report_id": rid,
                "project": reports_by_id[rid]["project"],
                "source_link": reports_by_id[rid]["source_link"],
                "entry_ids": sorted(verified_ids_by_report[rid]),
                "original_entry_ids": sorted(e["entry_id"] for e in entries_by_report[rid]),
            }
            for rid in retained_report_ids
        ],
        "deleted_reports": [
            {
                "report_id": rid,
                "project": reports_by_id[rid]["project"],
                "source_link": reports_by_id[rid]["source_link"],
                "entry_ids": sorted(e["entry_id"] for e in entries_by_report[rid]),
            }
            for rid in deleted_report_ids
        ],
        "partial_reports": [
            {
                "report_id": rid,
                "project": reports_by_id[rid]["project"],
                "retained_entry_ids": sorted(verified_ids_by_report[rid]),
                "removed_entry_ids": sorted(
                    e["entry_id"] for e in entries_by_report[rid] if e.get("verify") != 1
                ),
            }
            for rid in partial_report_ids
        ],
        "retained_entries": [
            {
                "entry_id": e["entry_id"],
                "report_id": e["report_id"],
                "project": e["project"],
                "repo_url": e["repo_url"],
                "commit": e["commit"],
                "verify": e["verify"],
            }
            for e in retained_entries
        ],
        "removed_entries": [
            {
                "entry_id": e["entry_id"],
                "report_id": e["report_id"],
                "project": e["project"],
                "repo_url": e["repo_url"],
                "commit": e["commit"],
                "verify": e.get("verify"),
            }
            for e in removed_entries
        ],
    }

    RECORDS.mkdir(exist_ok=True)
    write_jsonl(DATA / "entries.jsonl", retained_entries)
    write_jsonl(DATA / "reports.jsonl", retained_reports)
    SUMMARY_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    kept_report_rows = []
    for item in summary["retained_reports"]:
        original_count = len(item["original_entry_ids"])
        retained_count = len(item["entry_ids"])
        kept_report_rows.append(
            [
                item["report_id"],
                item["project"],
                retained_count,
                original_count,
                original_count - retained_count,
                ", ".join(item["entry_ids"]),
            ]
        )

    deleted_report_rows = [
        [
            item["report_id"],
            item["project"],
            len(item["entry_ids"]),
            ", ".join(item["entry_ids"]),
        ]
        for item in summary["deleted_reports"]
    ]
    partial_rows = [
        [
            item["report_id"],
            item["project"],
            ", ".join(item["retained_entry_ids"]),
            ", ".join(item["removed_entry_ids"]),
        ]
        for item in summary["partial_reports"]
    ]
    retained_entry_rows = [
        [item["entry_id"], item["report_id"], item["project"]]
        for item in summary["retained_entries"]
    ]
    removed_entry_rows = [
        [item["entry_id"], item["report_id"], item["project"], item["verify"]]
        for item in summary["removed_entries"]
    ]

    md = f"""# VulnGym Verify=1 Cleaned Dataset Record

Date: 2026-06-08

## Scope

This record documents the experiment-fork cleanup of VulnGym under:

```text
/home/ubuntu/BenchmarkForks/worktrees/VulnGym-cleaned
```

The cleanup keeps only `data/entries.jsonl` rows where `verify == 1`.
`data/reports.jsonl` is re-aggregated to match the retained entries.

## Version

```text
branch: {stats['branch']}
baseline_commit_before_cleaning: {stats['baseline_commit_before_cleaning']}
upstream: Tencent/VulnGym
generated_at_utc: {stats['generated_at_utc']}
```

## Counts

| Metric | Before | After |
|---|---:|---:|
| reports | {stats['reports_before']} | {stats['reports_after']} |
| entries | {stats['entries_before']} | {stats['entries_after']} |
| verified entries | {stats['verified_entries_before']} | {stats['entries_after']} |
| reports with at least one verified entry | {stats['verified_reports_before']} | {stats['reports_after']} |
| reports removed | 0 | {stats['removed_reports']} |
| entries removed | 0 | {stats['removed_entries']} |
| originally partial verified reports re-aggregated | {stats['partial_reports_before']} | 0 |

## Rules

- Keep every entry with `verify == 1`.
- Remove every entry with `verify != 1`.
- Keep a report if at least one of its entries is retained.
- Remove a report if none of its entries is retained.
- For partially verified reports, recompute `entry_ids` and `num_entries` from
  the retained verified entries only.
- Do not change `repo_url`, `commit`, `source_link`, `vuln_ids`, `project`, or
  `vuln_title` except through the report re-aggregation described above.

## Retained Reports

{md_table(['report_id', 'project', 'retained_entries', 'original_entries', 'removed_unverified_entries', 'retained_entry_ids'], kept_report_rows)}

## Removed Reports

{md_table(['report_id', 'project', 'removed_entries', 'removed_entry_ids'], deleted_report_rows)}

## Partially Verified Reports Re-Aggregated

{md_table(['report_id', 'project', 'retained_entry_ids', 'removed_entry_ids'], partial_rows)}

## Retained Entries

{md_table(['entry_id', 'report_id', 'project'], retained_entry_rows)}

## Removed Entries

{md_table(['entry_id', 'report_id', 'project', 'verify'], removed_entry_rows)}

## Machine-Readable Summary

```text
records/cleaned_verify1_20260608_summary.json
```
"""
    SUMMARY_MD.write_text(md, encoding="utf-8", newline="\n")

    update_readme(ROOT / "README.md", stats, report_category, zh=False)
    update_readme(ROOT / "README_zh.md", stats, report_category, zh=True)
    update_schema(ROOT / "SCHEMA.md", stats)
    update_changelog(ROOT / "CHANGELOG.md", stats)

    print(json.dumps(stats, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
