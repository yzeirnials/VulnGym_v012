#!/usr/bin/env python3
"""Reproduce the retained dataset's counts and source-based size statistics.

Only Python's standard library is required. Source sizes must be measured at
the exact manifest commits before this script runs; no network is accessed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
ID_PATTERN = re.compile(r"\b(?:GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}|CVE-\d{4}-\d{4,})\b", re.I)
DATA_FILES = ("entries", "reports", "entry_points", "critical_operations", "batch_manifest")
README_START = "<!-- DATASET_STATISTICS:START -->"
README_END = "<!-- DATASET_STATISTICS:END -->"
L1_ENGLISH_DISPLAY = {
    "业务逻辑": "Business logic",
    "代码注入": "Code injection",
    "XSS": "Cross-site scripting (XSS)",
    "反序列化漏洞": "Deserialization vulnerability",
    "反序列化": "Deserialization",
    "命令注入": "Command injection",
    "供应链攻击": "Supply chain attack",
    "模板注入": "Template injection",
    "SSRF": "Server-side request forgery (SSRF)",
    "原型链污染": "Prototype pollution",
    "注入与反序列化": "Injection and deserialization",
    "沙箱逃逸": "Sandbox escape",
    "文件操作安全": "File operation security",
    "权限绕过": "Authorization bypass",
    "路径遍历 / 任意文件读取": "Path traversal / arbitrary file read",
    "路径穿越": "Path traversal",
    "注入类": "Injection",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def unique_index(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    result = {}
    for row in rows:
        key = row[field]
        if key in result:
            raise ValueError(f"Duplicate {field}: {key}")
        result[key] = row
    return result


def identifiers(*rows: dict[str, Any]) -> dict[str, list[str]]:
    """Count explicit identifier fields, never IDs mentioned only in prose/code."""
    found = set()
    for row in rows:
        for field in ("vuln_ids", "report_id", "source_link", "source_report_ids", "source_links"):
            values = row.get(field, [])
            if isinstance(values, str):
                values = [values]
            for value in values or []:
                found.update(match.group().upper() for match in ID_PATTERN.finditer(value))
    return {kind: sorted(value for value in found if value.startswith(kind.upper() + "-"))
            for kind in ("ghsa", "cve")}


def union_ids(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {kind: sorted({value for row in rows for value in row[kind]}) for kind in ("ghsa", "cve")}


def percentile(values: list[int], fraction: float) -> float:
    """Linear interpolation at (n - 1) * fraction, including both endpoints."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot summarize an empty source-size population")
    position = (len(ordered) - 1) * fraction
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def size_summary(values: list[int]) -> dict[str, int | float]:
    return {"count": len(values), "min": min(values), "p25": percentile(values, .25),
            "median": statistics.median(values), "mean": statistics.mean(values),
            "p75": percentile(values, .75), "max": max(values)}


def snapshot_key(row: dict[str, Any]) -> tuple[str, str]:
    return row["repo_url"], row["commit"]


def check_nonnegative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a nonnegative integer")
    return value


def build_statistics(data: dict[str, list[dict[str, Any]]], source_sizes: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    entries = unique_index(data["entries"], "entry_id")
    reports = unique_index(data["reports"], "report_id")
    manifest = data["batch_manifest"]
    manifest_by_snapshot = {}
    entry_batches = {}
    for row in manifest:
        key = snapshot_key(row)
        if key in manifest_by_snapshot:
            raise ValueError(f"Duplicate manifest snapshot: {key}")
        manifest_by_snapshot[key] = row
        if not row["entry_ids"]:
            raise ValueError(f"Empty manifest snapshot: {key}")
        for entry_id in row["entry_ids"]:
            if entry_id in entry_batches:
                raise ValueError(f"Entry occurs more than once in manifest: {entry_id}")
            if entry_id not in entries or snapshot_key(entries[entry_id]) != key:
                raise ValueError(f"Manifest entry identity mismatch: {entry_id}")
            entry_batches[entry_id] = row["batch_id"]
    if set(entry_batches) != set(entries):
        raise ValueError("Manifest does not cover the exact retained entry set")
    expected_report_entries = defaultdict(set)
    for entry_id, entry in entries.items():
        expected_report_entries[entry["report_id"]].add(entry_id)
    if set(expected_report_entries) != set(reports):
        raise ValueError("Reports do not cover the exact retained report set")
    for report_id, report in reports.items():
        retained = report["entry_ids"]
        if (set(retained) != expected_report_entries[report_id] or len(retained) != len(set(retained))
                or report["num_entries"] != len(retained)):
            raise ValueError(f"Report membership/count mismatch: {report_id}")
        if any(snapshot_key(entries[entry_id]) != snapshot_key(report) for entry_id in retained):
            raise ValueError(f"Report/source snapshot mismatch: {report_id}")

    entry_ids = {entry_id: identifiers(entry, reports[entry["report_id"]]) for entry_id, entry in entries.items()}
    associations = []
    by_granularity = {}
    for granularity in ("entries", "entry_points", "critical_operations"):
        rows = []
        covered_entries = set()
        unique_index(data[granularity], "entry_id" if granularity == "entries" else "anchor_id")
        for record in data[granularity]:
            source_entry_ids = ([record["entry_id"]] if granularity == "entries" else record["source_entry_ids"])
            if not source_entry_ids or len(source_entry_ids) != len(set(source_entry_ids)):
                raise ValueError(f"Invalid source entry list in {granularity}")
            if not set(source_entry_ids) <= set(entries):
                raise ValueError(f"Unknown source entry in {granularity}")
            if any(snapshot_key(entries[entry_id]) != snapshot_key(record) for entry_id in source_entry_ids):
                raise ValueError(f"Anchor/source snapshot mismatch in {granularity}")
            covered_entries.update(source_entry_ids)
            row = {"granularity": granularity,
                   "record_id": record["entry_id"] if granularity == "entries" else record["anchor_id"],
                   "repo_url": record["repo_url"], "commit": record["commit"],
                   "batch_ids": sorted({entry_batches[entry_id] for entry_id in source_entry_ids}),
                   "source_entry_ids": sorted(source_entry_ids),
                   **union_ids([entry_ids[entry_id] for entry_id in source_entry_ids])}
            rows.append(row)
        if covered_entries != set(entries):
            raise ValueError(f"{granularity} does not cover every retained entry")
        by_granularity[granularity] = rows
        associations.extend(rows)

    all_ids = union_ids(list(entry_ids.values()))
    counts = {"entries": len(entries), "reports": len(reports),
              "entry_points": len(data["entry_points"]), "critical_operations": len(data["critical_operations"]),
              "snapshots": len(manifest_by_snapshot), "repositories": len({key[0] for key in manifest_by_snapshot}),
              "ghsa": len(all_ids["ghsa"]), "cve": len(all_ids["cve"])}
    granularity_rows = []
    for granularity, rows in by_granularity.items():
        ids = union_ids(rows)
        granularity_rows.append({"granularity": granularity, "records": len(rows),
                                 "ghsa": len(ids["ghsa"]), "cve": len(ids["cve"])})
    batch_rows = []
    for batch_id in sorted(set(entry_batches.values())):
        selected = [entry for entry in entries.values() if entry_batches[entry["entry_id"]] == batch_id]
        ids = union_ids([entry_ids[entry["entry_id"]] for entry in selected])
        batch_rows.append({"batch_id": batch_id, "entries": len(selected),
                           "reports": len({entry["report_id"] for entry in selected}),
                           "entry_points": sum(batch_id in row["batch_ids"] for row in by_granularity["entry_points"]),
                           "critical_operations": sum(batch_id in row["batch_ids"] for row in by_granularity["critical_operations"]),
                           "snapshots": len({snapshot_key(entry) for entry in selected}),
                           "repositories": len({entry["repo_url"] for entry in selected}),
                           "ghsa": len(ids["ghsa"]), "cve": len(ids["cve"])})

    category_rows = []
    for batch_id in ["ALL"] + sorted(set(entry_batches.values())):
        selected = [entry for entry in entries.values() if batch_id == "ALL" or entry_batches[entry["entry_id"]] == batch_id]
        for level in ("l1", "l2"):
            field = "vuln_category_" + level
            for entry in selected:
                if not isinstance(entry.get(field), str) or not entry[field]:
                    raise ValueError(f"Missing/non-string category on {entry['entry_id']}: {field}")
            entry_counts = Counter(entry[field] for entry in selected)
            report_counts = Counter(category for report_id, category in {(entry["report_id"], entry[field]) for entry in selected})
            for unit, distribution in (("entry", entry_counts), ("report", report_counts)):
                denominator = len(selected) if unit == "entry" else len({entry["report_id"] for entry in selected})
                category_rows.extend({"batch_id": batch_id, "level": level, "unit": unit, "category": category,
                                      "count": count, "denominator": denominator, "percentage": 100 * count / denominator}
                                     for category, count in sorted(distribution.items(), key=lambda item: (-item[1], item[0])))

    measured = {}
    for snapshot in source_sizes["snapshots"]:
        key = snapshot_key(snapshot)
        if key in measured:
            raise ValueError(f"Duplicate measured source snapshot: {key}")
        measured[key] = snapshot
    if set(measured) != set(manifest_by_snapshot):
        raise ValueError("Source sizes must cover exactly the retained manifest snapshots")
    snapshot_rows = []
    language_counts = defaultdict(lambda: {"sloc": 0, "source_files": 0, "source_bytes": 0,
                                          "snapshot_count": 0, "primary_snapshot_count": 0, "primary_entry_count": 0})
    for key, snapshot in sorted(measured.items()):
        for field in ("sloc", "source_files", "source_bytes"):
            check_nonnegative_int(snapshot[field], field)
        languages = snapshot["languages"]
        if not languages or not snapshot["sloc"]:
            raise ValueError(f"Source snapshot has no counted code: {key}")
        for language, values in languages.items():
            for field in ("code", "files", "bytes", "blank", "comment"):
                check_nonnegative_int(values[field], f"{language}.{field}")
        for total_field, language_field in (("sloc", "code"), ("source_files", "files"), ("source_bytes", "bytes")):
            if snapshot[total_field] != sum(value[language_field] for value in languages.values()):
                raise ValueError(f"Source language totals do not match {total_field}: {key}")
        primary = min(languages, key=lambda language: (-languages[language]["code"], language))
        member = manifest_by_snapshot[key]
        row = {"batch_id": member["batch_id"], "repo_url": key[0], "commit": key[1],
               "entries": len(member["entry_ids"]), "primary_language": primary,
               "sloc": snapshot["sloc"], "source_files": snapshot["source_files"], "source_bytes": snapshot["source_bytes"]}
        snapshot_rows.append(row)
        for language, values in languages.items():
            target = language_counts[language]
            target["sloc"] += values["code"]
            target["source_files"] += values["files"]
            target["source_bytes"] += values["bytes"]
            target["snapshot_count"] += int(values["code"] > 0)
            if language == primary:
                target["primary_snapshot_count"] += 1
                target["primary_entry_count"] += len(member["entry_ids"])
    snapshot_sloc_sum = sum(row["sloc"] for row in snapshot_rows)
    language_rows = [{"language": language, **values, "sloc_percentage": 100 * values["sloc"] / snapshot_sloc_sum,
                      "primary_entry_percentage": 100 * values["primary_entry_count"] / len(entries)}
                     for language, values in sorted(language_counts.items(), key=lambda item: (-item[1]["sloc"], item[0]))]
    repository_rows = []
    for repo_url in sorted({row["repo_url"] for row in snapshot_rows}):
        rows = [row for row in snapshot_rows if row["repo_url"] == repo_url]
        values = [row["sloc"] for row in rows]
        repository_rows.append({"repo_url": repo_url, "snapshots": len(rows), "entries": sum(row["entries"] for row in rows),
                                "primary_languages": sorted({row["primary_language"] for row in rows}),
                                **{f"sloc_{key}": value for key, value in size_summary(values).items() if key != "count"}})
    summary = {
        "schema_version": 1,
        "counts": counts,
        "batches": batch_rows,
        "granularities": granularity_rows,
        "identifiers": all_ids,
        "categories": category_rows,
        "languages": language_rows,
        "project_size": {"unit": "physical source lines of code (excluding comments and blank lines)",
                         "population": "unique (repo_url, commit) snapshots",
                         "sloc": size_summary([row["sloc"] for row in snapshot_rows]),
                         "snapshot_sloc_sum": snapshot_sloc_sum},
        "repositories": repository_rows,
        "methodology": {
            "identifier_fields": ["vuln_ids", "report_id", "source_link"],
            "identifier_normalization": "Case-insensitive matching; uppercase unique GHSA/CVE identifier sets; no IDs inferred from titles or code.",
            "anchor_identifiers": "Union of identifiers on associated retained entries and their reports.",
            "identifier_limitations": "Identifier counts are not independent vulnerability counts; one report may reference multiple GHSA IDs, and CVE and GHSA can identify the same advisory.",
            "categories": "Original L1/L2 labels are preserved. Entry counts count rows; report counts count distinct (report_id, category) memberships. Percentages use the scope's entry count or distinct report count, so report percentages can sum above 100 if a report has multiple labels.",
            "language": "Measured code SLOC per language at each pinned snapshot; primary language has most code SLOC, with alphabetical language-name tie breaking.",
            "language_entry_counts": "Each entry inherits its snapshot's primary language; this is not the language of its vulnerable anchor.",
            "language_snapshot_coverage": "A language covers a snapshot only when its code SLOC is positive; multilingual coverage counts need not sum to the snapshot count.",
            "percentiles": "Linear interpolation at (n - 1) * p (inclusive endpoints).",
            "project_identity": "Exact repo_url; repeated commits are distinct snapshots of the same repository.",
            "size_limitations": "snapshot_sloc_sum and language SLOC sum count multiple revisions of a project; neither is deduplicated project source volume.",
            "source_measurement": {"cloc_version": source_sizes.get("cloc_version"), "policy": source_sizes.get("policy", {})},
        },
    }
    tables = {"batch_statistics": batch_rows, "granularity_statistics": granularity_rows,
              "identifier_associations": sorted(associations, key=lambda row: (row["granularity"], row["record_id"])),
              "category_statistics": category_rows, "language_statistics": language_rows,
              "snapshot_statistics": snapshot_rows, "repository_statistics": repository_rows}
    return summary, tables


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False, separators=(",", ":")) if isinstance(value, (list, dict)) else value
                             for key, value in row.items()})


def markdown_cell(value: Any) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def format_number(value: int | float) -> str:
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"


def render_overview(summary: dict[str, Any], zh: bool = False) -> str:
    """Render measured tables without changing or merging annotation labels."""
    counts = summary["counts"]
    total_sloc = summary["project_size"]["snapshot_sloc_sum"]
    lines = ["所有计入统计的语言如下；覆盖快照数允许重叠。" if zh else
             "All counted languages are shown below; snapshot coverage can overlap.", "",
             "| 语言 | SLOC | SLOC 占比 | 覆盖快照 | 主语言 Entries |" if zh else
             "| Language | SLOC | SLOC share | Snapshot coverage | Primary-language entries |",
             "|---|---:|---:|---:|---:|"]
    for row in summary["languages"]:
        lines.append(f"| {markdown_cell(row['language'])} | {format_number(row['sloc'])} | "
                     f"{row['sloc_percentage']:.2f}% | {row['snapshot_count']} | {row['primary_entry_count']} |")
    total_label = "合计" if zh else "Total"
    lines.extend([f"| **{total_label}** | **{format_number(total_sloc)}** | **100.00%** | — | **{counts['entries']}** |", ""])
    size = summary["project_size"]["sloc"]
    lines.extend([f"**{counts['snapshots']} 个固定快照的项目规模（SLOC）**" if zh else
                  f"**Project size across {counts['snapshots']} pinned snapshots (SLOC)**", "",
                  "| 最小值 | P25 | 中位数 | 均值 | P75 | 最大值 |" if zh else
                  "| Minimum | P25 | Median | Mean | P75 | Maximum |",
                  "|---:|---:|---:|---:|---:|---:|",
                  "| " + " | ".join(format_number(size[key]) for key in ("min", "p25", "median", "mean", "p75", "max")) + " |", "",
                  f"**原始 L1 漏洞类别**：Entry 占比以 {counts['entries']} 条 entry 为分母，Report 占比以 {counts['reports']} 条 report 为分母。" if zh else
                  f"**Original L1 vulnerability categories**: entry shares use {counts['entries']} entries; report shares use {counts['reports']} reports.", "",
                  "| 原始 L1 类别 | Entries | Entry 占比 | Reports | Report 占比 |" if zh else
                  "| Original L1 label | English display | Entries | Entry share | Reports | Report share |",
                  "|---|---:|---:|---:|---:|" if zh else "|---|---|---:|---:|---:|---:|"])
    entry_rows = [row for row in summary["categories"] if row["batch_id"] == "ALL" and row["level"] == "l1" and row["unit"] == "entry"]
    report_rows = {row["category"]: row for row in summary["categories"]
                   if row["batch_id"] == "ALL" and row["level"] == "l1" and row["unit"] == "report"}
    for row in entry_rows:
        category = row["category"]
        columns = [markdown_cell(category)]
        if not zh:
            columns.append(markdown_cell(L1_ENGLISH_DISPLAY.get(category, "—")))
        report = report_rows[category]
        columns.extend([str(row["count"]), f"{row['percentage']:.2f}%",
                        str(report["count"]), f"{report['percentage']:.2f}%"])
        lines.append("| " + " | ".join(columns) + " |")
    lines.extend(["", "原始标签分别计数，不合并同义标签。完整 L1/L2、各批次 entry/report 分布见 "
                  "[漏洞类别统计](records/category_statistics.csv)。更多结果见 "
                  "[统计汇总](records/dataset_statistics.json)、[语言统计](records/language_statistics.csv)、"
                  "[快照规模明细](records/snapshot_statistics.csv) 和 [仓库规模明细](records/repository_statistics.csv)。" if zh else
                  "Original labels remain separate; English names are display translations only. "
                  "Complete L1/L2 and per-batch entry/report distributions are in "
                  "[category statistics](records/category_statistics.csv). Further results are in "
                  "[dataset statistics](records/dataset_statistics.json), [language statistics](records/language_statistics.csv), "
                  "[snapshot sizes](records/snapshot_statistics.csv), and [repository sizes](records/repository_statistics.csv)."])
    return "\n".join(lines)


def replace_overview(original: str, rendered: str) -> str:
    """Replace exactly one marker pair, preserving all bytes outside its body."""
    matches = [list(re.finditer(r"(?m)^" + re.escape(marker) + r"\r?$", original))
               for marker in (README_START, README_END)]
    if any(len(found) != 1 for found in matches) or any(original.count(marker) != 1 for marker in (README_START, README_END)):
        raise ValueError("README must contain exactly one standalone statistics START and END marker")
    start, end = matches[0][0], matches[1][0]
    if start.end() >= end.start():
        raise ValueError("README statistics START marker must precede END marker")
    return original[:start.end()] + "\n\n" + rendered.rstrip("\n") + "\n\n" + original[end.start():]


def prepare_readme_updates(repo_root: Path, summary: dict[str, Any]) -> dict[Path, str]:
    """Validate both documents before any CLI output or README is written."""
    return {repo_root / filename: replace_overview((repo_root / filename).read_bytes().decode("utf-8"), render_overview(summary, zh))
            for filename, zh in (("README.md", False), ("README_zh.md", True))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data")
    parser.add_argument("--source-sizes", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "records")
    parser.add_argument("--update-readmes", action="store_true", help="Also replace the marked statistics blocks in README.md and README_zh.md")
    args = parser.parse_args()
    data = {name: load_jsonl(args.data_dir / f"{name}.jsonl") for name in DATA_FILES}
    source_sizes = json.loads(args.source_sizes.read_text(encoding="utf-8"))
    summary, tables = build_statistics(data, source_sizes)
    readme_updates = prepare_readme_updates(REPO_ROOT, summary) if args.update_readmes else {}
    inputs = {f"data/{name}.jsonl": args.data_dir / f"{name}.jsonl" for name in DATA_FILES}
    if (args.data_dir / "dataset.json").exists():
        inputs["data/dataset.json"] = args.data_dir / "dataset.json"
    inputs["source_sizes"] = args.source_sizes
    summary["provenance"] = {"inputs_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sorted(inputs.items())}}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "dataset_statistics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    for name, rows in tables.items():
        write_csv(args.output_dir / f"{name}.csv", rows)
    for path, content in readme_updates.items():
        path.write_text(content, encoding="utf-8", newline="\n")
    print(json.dumps(summary["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
