#!/usr/bin/env python3
"""Build endpoint-level VulnGym ground-truth files from pair entries."""
from __future__ import annotations

import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RECORDS = ROOT / "records"

ENTRY_POINTS = DATA / "entry_points.jsonl"
CRITICAL_OPERATIONS = DATA / "critical_operations.jsonl"
SUMMARY_JSON = RECORDS / "endpoint_ground_truth_20260608_summary.json"
SUMMARY_MD = RECORDS / "endpoint_ground_truth_20260608.md"


def git(args: list[str]) -> str:
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


def stable_unique(values: list[Any]) -> list[Any]:
    seen: set[str] = set()
    out: list[Any] = []
    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return sorted(out, key=lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True))


def endpoint_key(entry: dict[str, Any], field: str) -> tuple[str, str, str, str]:
    endpoint = entry[field]
    return (
        entry["repo_url"],
        entry["commit"],
        endpoint["file"],
        str(endpoint["line"]),
    )


def build_anchor_rows(
    entries: list[dict[str, Any]],
    *,
    field: str,
    anchor_prefix: str,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        grouped[endpoint_key(entry, field)].append(entry)

    rows: list[dict[str, Any]] = []
    for idx, (key, source_entries) in enumerate(sorted(grouped.items()), 1):
        repo_url, commit, _, _ = key
        source_entries = sorted(source_entries, key=lambda e: e["entry_id"])
        endpoint = dict(source_entries[0][field])
        anchor_id = f"{anchor_prefix}-{idx:05d}"
        row: dict[str, Any] = {
            "anchor_id": anchor_id,
            "anchor_kind": field,
            "repo_url": repo_url,
            "commit": commit,
            field: endpoint,
            "source_entry_ids": sorted(e["entry_id"] for e in source_entries),
            "source_report_ids": sorted({e["report_id"] for e in source_entries}),
            "projects": stable_unique([e["project"] for e in source_entries]),
            "source_links": stable_unique([e["source_link"] for e in source_entries]),
            "vuln_ids": stable_unique([vid for e in source_entries for vid in e.get("vuln_ids", [])]),
            "vuln_titles": stable_unique([e["vuln_title"] for e in source_entries]),
            "vuln_category_l1": stable_unique([e["vuln_category_l1"] for e in source_entries]),
            "vuln_category_l2": stable_unique([e["vuln_category_l2"] for e in source_entries]),
            "source_endpoint_codes": stable_unique(
                [e[field].get("code", "") for e in source_entries if e[field].get("code", "")]
            ),
            "verify": 1,
        }
        rows.append(row)
    return rows


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(out)


def duplicate_summary(rows: list[dict[str, Any]]) -> tuple[int, int, list[list[str]]]:
    duplicate_rows = [row for row in rows if len(row["source_entry_ids"]) > 1]
    extra_source_entries = sum(len(row["source_entry_ids"]) - 1 for row in duplicate_rows)
    examples = [
        [
            row["anchor_id"],
            ", ".join(row["source_entry_ids"]),
            ", ".join(row["source_report_ids"]),
        ]
        for row in duplicate_rows[:20]
    ]
    return len(duplicate_rows), extra_source_entries, examples


def update_readme(path: Path, *, zh: bool) -> None:
    text = path.read_text(encoding="utf-8")
    if zh:
        text = text.replace(
            "│   ├── reports.jsonl            # 184 行 —— 每行一条 GitHub Advisory\n"
            "│   └── entries.jsonl            # 408 行 —— 每行一个入口点，含人工审计标记 verify\n"
            "└── examples/\n"
            "    ├── load_dataset.py          # stdlib / pandas / HuggingFace datasets 加载器\n"
            "    ├── example_result.jsonl     # 工具提交结果的示例\n"
            "    └── evaluate.py              # 覆盖率 / 召回率 评测脚本\n",
            "│   ├── reports.jsonl             # 137 行 —— 每行一条保留的 GitHub Advisory\n"
            "│   ├── entries.jsonl             # 274 行 —— pair-level verified entries\n"
            "│   ├── entry_points.jsonl        # 236 行 —— 去重后的入口 anchor\n"
            "│   └── critical_operations.jsonl # 241 行 —— 去重后的核心操作 anchor\n"
            "└── examples/\n"
            "    ├── load_dataset.py\n"
            "    ├── example_result.jsonl\n"
            "    ├── evaluate.py                      # pair-level 召回评测\n"
            "    ├── evaluate_entry_points.py         # entry_point anchor 召回评测\n"
            "    └── evaluate_critical_operations.py  # critical_operation anchor 召回评测\n",
        )
        insert = """### 单点粒度 Ground Truth

除 pair-level `data/entries.jsonl` 外，本 cleaned fork 还从同一批 verified entries
派生了两个单点粒度 ground-truth 文件：

- `data/entry_points.jsonl` — 去重后的可达入口 anchor
- `data/critical_operations.jsonl` — 去重后的核心缺陷操作 anchor

这两个文件中的每个 anchor 都保留 `source_entry_ids` 和 `source_report_ids`，
用于回溯到原始 pair-level entries。当前规模为 **236** 个 entry-point anchors
和 **241** 个 critical-operation anchors。

"""
        if "### 单点粒度 Ground Truth" not in text:
            text = text.replace("## 📈 基线评测结果\n", insert + "## 📈 基线评测结果\n")
        old = """Write your tool's findings to a JSONL file (one finding per line) and run:

```bash
python3 examples/evaluate.py path/to/your_findings.jsonl -v
```

Each finding must carry at least `repo_url`, `commit`, `entry_point`
(reachable entry point), and `critical_operation` (core defect location).
`trace` (cross-module reasoning chain) is optional and ignored by the
matcher. See `examples/example_result.jsonl` for a working sample.

The script reports two metrics:

- **Advisory-level recall** (primary) — `covered_advisories /
  usable_advisories`. An advisory is covered if **at least one** of its
  entries is matched.
- **Entry-level recall** (secondary) — `matched_entries / usable_entries`.
"""
        new = """Write your tool's findings to a JSONL file (one finding per line). The
cleaned fork provides three recall-only evaluator entry points:

```bash
# Strict pair-level path reconstruction: entry_point + critical_operation
python3 examples/evaluate.py path/to/your_findings.jsonl -v

# Reachable-entry localization only
python3 examples/evaluate_entry_points.py path/to/your_findings.jsonl -v

# Core defect-location localization only
python3 examples/evaluate_critical_operations.py path/to/your_findings.jsonl -v
```

For pair-level evaluation, each finding must carry at least `repo_url`,
`commit`, `entry_point` (reachable entry point), and `critical_operation`
(core defect location). For entry-point-only evaluation, `entry_point` is
required. For critical-operation-only evaluation, `critical_operation` is
required. `trace` (cross-module reasoning chain) is optional and ignored by all
three matchers. See `examples/example_result.jsonl` for a working sample.

The pair-level script reports:

- **Advisory-level recall** (primary) — `covered_advisories /
  usable_advisories`. An advisory is covered if **at least one** of its
  entries is matched.
- **Entry-level recall** (secondary) — `matched_entries / usable_entries`.

The single-anchor scripts report:

- **Anchor-level recall** (primary) — matched `entry_point` or
  `critical_operation` anchors over usable anchors.
- **Report-level recall** (supplemental) — reports covered through matched
  anchors.
- **Source-entry coverage** (supplemental) — original pair-level entries covered
  through matched anchors.
"""
        if old in text:
            text = text.replace(old, new)
        old_zh = """将工具检出结果写入一个 JSONL 文件（每行一条 finding），然后运行：

```bash
python3 examples/evaluate.py path/to/your_findings.jsonl -v
```

每条 finding 至少需要包含 `repo_url`、`commit`、`entry_point`（外部可达入口）和
`critical_operation`（核心缺陷位置）。`trace`（跨模块推理链路）可选，当前评测器不参与匹配。
完整格式参考 `examples/example_result.jsonl`。

评测脚本报告两个指标：

- **Advisory-level recall**（主指标）— `covered_advisories /
  usable_advisories`。如果某个 advisory 至少有一条 entry 被匹配，则视为覆盖。
- **Entry-level recall**（辅助指标）— `matched_entries / usable_entries`。
"""
        new_zh = """将工具检出结果写入一个 JSONL 文件（每行一条 finding）。当前 cleaned fork
提供三个 recall-only evaluator：

```bash
# 严格 pair-level 路径重建：entry_point + critical_operation
python3 examples/evaluate.py path/to/your_findings.jsonl -v

# 仅评估可达入口定位
python3 examples/evaluate_entry_points.py path/to/your_findings.jsonl -v

# 仅评估核心缺陷位置定位
python3 examples/evaluate_critical_operations.py path/to/your_findings.jsonl -v
```

pair-level 评估要求每条 finding 至少包含 `repo_url`、`commit`、`entry_point`
（外部可达入口）和 `critical_operation`（核心缺陷位置）。entry-point-only 评估只要求
`entry_point`；critical-operation-only 评估只要求 `critical_operation`。`trace`
（跨模块推理链路）可选，三个 matcher 都不使用 `trace`。完整格式参考
`examples/example_result.jsonl`。

pair-level 脚本报告：

- **Advisory-level recall**（主指标）— `covered_advisories /
  usable_advisories`。如果某个 advisory 至少有一条 entry 被匹配，则视为覆盖。
- **Entry-level recall**（辅助指标）— `matched_entries / usable_entries`。

两个单点粒度脚本报告：

- **Anchor-level recall**（主指标）— 命中的 `entry_point` 或 `critical_operation`
  anchors / usable anchors。
- **Report-level recall**（补充指标）— 通过 matched anchors 覆盖到的 reports。
- **Source-entry coverage**（补充指标）— 通过 matched anchors 覆盖到的原始
  pair-level entries。
"""
        if old_zh in text:
            text = text.replace(old_zh, new_zh)
        eval_start = text.find("## 📊 评测你的工具")
        policy_start = text.find("**默认匹配策略**", eval_start)
        if eval_start != -1 and policy_start != -1:
            eval_intro = "## 📊 评测你的工具\n\n" + new_zh + "\n"
            if "examples/evaluate_entry_points.py" not in text[eval_start:policy_start]:
                text = text[:eval_start] + eval_intro + text[policy_start:]
        text = text.replace(
            "| 行号容差 | entry_point 与 critical_operation 均满足 `|Δline| ≤ 5` |\n"
            "| 方向 | 严格（entry_point 对 entry_point，critical_operation 对 critical_operation） |\n"
            "| ground truth 中 `line == 0` | 同时从分子分母中剔除 |",
            "| 行号容差 | `int` 或 `\"start-end\"` span；默认容差 `+/-5` |\n"
            "| 方向 | pair-level 严格匹配 entry_point 对 entry_point、critical_operation 对 critical_operation；单点评估只匹配对应 anchor |\n"
            "| 不可用 ground truth line | 同时从分子分母中剔除 |",
        )
    else:
        text = text.replace(
            "│   ├── reports.jsonl            # 184 rows — one GitHub Advisory per row\n"
            "│   └── entries.jsonl            # 408 rows — one entry point per row, with human-audit flag (verify)\n"
            "└── examples/\n"
            "    ├── load_dataset.py          # stdlib / pandas / HuggingFace datasets loader\n"
            "    ├── example_result.jsonl     # illustrative tool-findings submission\n"
            "    └── evaluate.py              # coverage / recall evaluator\n",
            "│   ├── reports.jsonl             # 137 rows — one retained GitHub Advisory per row\n"
            "│   ├── entries.jsonl             # 274 rows — pair-level verified entries\n"
            "│   ├── entry_points.jsonl        # 236 rows — deduplicated reachable-entry anchors\n"
            "│   └── critical_operations.jsonl # 241 rows — deduplicated critical-operation anchors\n"
            "└── examples/\n"
            "    ├── load_dataset.py\n"
            "    ├── example_result.jsonl\n"
            "    ├── evaluate.py                      # pair-level recall evaluator\n"
            "    ├── evaluate_entry_points.py         # entry_point anchor recall evaluator\n"
            "    └── evaluate_critical_operations.py  # critical_operation anchor recall evaluator\n",
        )
        insert = """### Endpoint-Level Ground Truth

In addition to pair-level `data/entries.jsonl`, this cleaned fork derives two
single-anchor ground-truth files from the same verified entries:

- `data/entry_points.jsonl` — deduplicated reachable-entry anchors
- `data/critical_operations.jsonl` — deduplicated core defect-operation anchors

Every anchor keeps `source_entry_ids` and `source_report_ids` so it can be
traced back to the original pair-level entries. The current cleaned subset
contains **236** entry-point anchors and **241** critical-operation anchors.

"""
        if "### Endpoint-Level Ground Truth" not in text:
            text = text.replace("## 📈 Baseline evaluation results\n", insert + "## 📈 Baseline evaluation results\n")
        old = """Write your tool's findings to a JSONL file (one finding per line) and run:

```bash
python3 examples/evaluate.py path/to/your_findings.jsonl -v
```

Each finding must carry at least `repo_url`, `commit`, `entry_point`
(reachable entry point), and `critical_operation` (core defect location).
`trace` (cross-module reasoning chain) is optional and ignored by the
matcher. See `examples/example_result.jsonl` for a working sample.

The script reports two metrics:

- **Advisory-level recall** (primary) — `covered_advisories /
  usable_advisories`. An advisory is covered if **at least one** of its
  entries is matched.
- **Entry-level recall** (secondary) — `matched_entries / usable_entries`.
"""
        new = """Write your tool's findings to a JSONL file (one finding per line). The
cleaned fork provides three recall-only evaluator entry points:

```bash
# Strict pair-level path reconstruction: entry_point + critical_operation
python3 examples/evaluate.py path/to/your_findings.jsonl -v

# Reachable-entry localization only
python3 examples/evaluate_entry_points.py path/to/your_findings.jsonl -v

# Core defect-location localization only
python3 examples/evaluate_critical_operations.py path/to/your_findings.jsonl -v
```

For pair-level evaluation, each finding must carry at least `repo_url`,
`commit`, `entry_point` (reachable entry point), and `critical_operation`
(core defect location). For entry-point-only evaluation, `entry_point` is
required. For critical-operation-only evaluation, `critical_operation` is
required. `trace` (cross-module reasoning chain) is optional and ignored by all
three matchers. See `examples/example_result.jsonl` for a working sample.

The pair-level script reports:

- **Advisory-level recall** (primary) — `covered_advisories /
  usable_advisories`. An advisory is covered if **at least one** of its
  entries is matched.
- **Entry-level recall** (secondary) — `matched_entries / usable_entries`.

The single-anchor scripts report:

- **Anchor-level recall** (primary) — matched `entry_point` or
  `critical_operation` anchors over usable anchors.
- **Report-level recall** (supplemental) — reports covered through matched
  anchors.
- **Source-entry coverage** (supplemental) — original pair-level entries covered
  through matched anchors.
"""
        if old in text:
            text = text.replace(old, new)
        text = text.replace(
            "| Line tolerance | `\\|Δline\\| ≤ 5` on entry_point **and** critical_operation |\n"
            "| Direction | strict (entry_point-to-entry_point, critical_operation-to-critical_operation) |\n"
            "| `line == 0` in ground truth | excluded from numerator and denominator |",
            "| Line tolerance | `int` or `\"start-end\"` span; default tolerance `+/-5` |\n"
            "| Direction | pair-level is strict entry_point-to-entry_point and critical_operation-to-critical_operation; single-anchor evaluators match only their corresponding anchor |\n"
            "| Unusable ground-truth line | excluded from numerator and denominator |",
        )
    path.write_text(text, encoding="utf-8", newline="\n")


def update_schema(path: Path, entry_point_count: int, critical_operation_count: int) -> None:
    text = path.read_text(encoding="utf-8")
    bullets = (
        f"- `data/entry_points.jsonl` — {entry_point_count} rows, one per deduplicated "
        "human-verified reachable entry-point anchor.\n"
        f"- `data/critical_operations.jsonl` — {critical_operation_count} rows, one per "
        "deduplicated human-verified critical-operation anchor.\n"
    )
    if "`data/entry_points.jsonl`" not in text:
        text = text.replace(
            "- `data/entries.jsonl` — 274 rows, one per retained human-verified reachable entry point.\n",
            "- `data/entries.jsonl` — 274 rows, one per retained human-verified pair-level entry.\n" + bullets,
        )
    else:
        text = re.sub(
            r"- `data/entry_points\.jsonl` — \d+ rows, one per deduplicated human-verified reachable entry-point anchor\.",
            f"- `data/entry_points.jsonl` — {entry_point_count} rows, one per deduplicated human-verified reachable entry-point anchor.",
            text,
        )
        text = re.sub(
            r"- `data/critical_operations\.jsonl` — \d+ rows, one per deduplicated human-verified critical-operation anchor\.",
            f"- `data/critical_operations.jsonl` — {critical_operation_count} rows, one per deduplicated human-verified critical-operation anchor.",
            text,
        )
    if "## Endpoint-level rows" not in text:
        endpoint_schema = """
## Endpoint-level rows

`data/entry_points.jsonl` and `data/critical_operations.jsonl` are derived
views over `data/entries.jsonl`.

Both files use one JSON object per deduplicated anchor. Each row contains:

| field | type | description |
|---|---|---|
| `anchor_id` | `string` | Stable id within the file, e.g. `entry-point-00001`. |
| `anchor_kind` | `string` | Either `entry_point` or `critical_operation`. |
| `repo_url` | `string` | Same repository key used by pair-level evaluation. |
| `commit` | `string` | Vulnerable commit SHA. |
| `entry_point` / `critical_operation` | `object` | The anchor object `{file, line, code}`. Only the field named by `anchor_kind` is present. |
| `source_entry_ids` | `string[]` | Pair-level `entry_id` rows that produced this anchor. |
| `source_report_ids` | `string[]` | Advisory/report ids reachable from `source_entry_ids`. |
| `projects` | `string[]` | Source project labels for the anchor. |
| `source_links` | `string[]` | Advisory URLs associated with the anchor. |
| `vuln_ids` | `string[]` | Union of vulnerability ids associated with source entries. |
| `vuln_titles` | `string[]` | Source vulnerability titles. |
| `vuln_category_l1` / `vuln_category_l2` | `string[]` | Source category labels. |
| `source_endpoint_codes` | `string[]` | Source code snippets observed at this anchor location. |
| `verify` | `int` | Always `1` in this cleaned fork because source entries are filtered to `verify == 1`. |

The endpoint files are for localization-only evaluation. They do not encode the
full pair relation between reachable entry point and critical operation; use
`data/entries.jsonl` and `examples/evaluate.py` for strict pair-level path
reconstruction.

---
"""
        text = text.replace("## `entries.jsonl` row\n", endpoint_schema + "\n## `entries.jsonl` row\n")
    elif "`source_endpoint_codes`" not in text:
        text = text.replace(
            "| `vuln_category_l1` / `vuln_category_l2` | `string[]` | Source category labels. |\n",
            "| `vuln_category_l1` / `vuln_category_l2` | `string[]` | Source category labels. |\n"
            "| `source_endpoint_codes` | `string[]` | Source code snippets observed at this anchor location. |\n",
        )
    path.write_text(text, encoding="utf-8", newline="\n")


def update_changelog(path: Path, entry_point_count: int, critical_operation_count: int) -> None:
    text = path.read_text(encoding="utf-8")
    if "Endpoint-level ground-truth views" in text:
        text = re.sub(
            r"`data/entry_points\.jsonl` \(\d+ anchors\) and `data/critical_operations\.jsonl` \(\d+ anchors\)",
            f"`data/entry_points.jsonl` ({entry_point_count} anchors) and `data/critical_operations.jsonl` ({critical_operation_count} anchors)",
            text,
        )
        path.write_text(text, encoding="utf-8", newline="\n")
        return
    needle = "### Records\n- `records/cleaned_verify1_20260608.md`\n- `records/cleaned_verify1_20260608_summary.json`\n"
    replacement = needle + (
        "\n### Added\n"
        f"- Endpoint-level ground-truth views: `data/entry_points.jsonl` "
        f"({entry_point_count} anchors) and `data/critical_operations.jsonl` "
        f"({critical_operation_count} anchors).\n"
        "- Endpoint-level recall evaluators: `examples/evaluate_entry_points.py` "
        "and `examples/evaluate_critical_operations.py`.\n"
        "- Endpoint generation records under `records/endpoint_ground_truth_20260608.*`.\n"
    )
    text = text.replace(needle, replacement)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    RECORDS.mkdir(exist_ok=True)
    entries = load_jsonl(DATA / "entries.jsonl")
    if any(e.get("verify") != 1 for e in entries):
        raise SystemExit("data/entries.jsonl must be filtered to verify == 1 first")

    entry_points = build_anchor_rows(entries, field="entry_point", anchor_prefix="entry-point")
    critical_operations = build_anchor_rows(
        entries, field="critical_operation", anchor_prefix="critical-operation"
    )

    write_jsonl(ENTRY_POINTS, entry_points)
    write_jsonl(CRITICAL_OPERATIONS, critical_operations)

    ep_dups, ep_extra, ep_examples = duplicate_summary(entry_points)
    co_dups, co_extra, co_examples = duplicate_summary(critical_operations)
    stats = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "branch": git(["branch", "--show-current"]),
        "source_commit": git(["rev-parse", "HEAD"]),
        "source_entries": len(entries),
        "source_reports": len({rid for e in entries for rid in [e["report_id"]]}),
        "entry_point_anchors": len(entry_points),
        "entry_point_duplicate_anchor_groups": ep_dups,
        "entry_point_extra_source_entries_collapsed": ep_extra,
        "critical_operation_anchors": len(critical_operations),
        "critical_operation_duplicate_anchor_groups": co_dups,
        "critical_operation_extra_source_entries_collapsed": co_extra,
    }

    summary = {
        "stats": stats,
        "entry_point_duplicate_examples": ep_examples,
        "critical_operation_duplicate_examples": co_examples,
    }
    SUMMARY_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    SUMMARY_MD.write_text(
        f"""# VulnGym Endpoint-Level Ground Truth Record

Date: 2026-06-08

## Scope

This record documents endpoint-level ground-truth files derived from the
verified pair-level dataset in:

```text
/home/ubuntu/BenchmarkForks/worktrees/VulnGym-cleaned
```

## Version

```text
branch: {stats['branch']}
source_commit_before_generation: {stats['source_commit']}
generated_at_utc: {stats['generated_at_utc']}
```

## Generated Files

```text
data/entry_points.jsonl
data/critical_operations.jsonl
examples/evaluate_entry_points.py
examples/evaluate_critical_operations.py
```

## Counts

| Metric | Count |
|---|---:|
| source pair-level entries | {stats['source_entries']} |
| source reports | {stats['source_reports']} |
| unique entry-point anchors | {stats['entry_point_anchors']} |
| entry-point duplicate anchor groups | {stats['entry_point_duplicate_anchor_groups']} |
| entry-point extra source entries collapsed | {stats['entry_point_extra_source_entries_collapsed']} |
| unique critical-operation anchors | {stats['critical_operation_anchors']} |
| critical-operation duplicate anchor groups | {stats['critical_operation_duplicate_anchor_groups']} |
| critical-operation extra source entries collapsed | {stats['critical_operation_extra_source_entries_collapsed']} |

## Rules

- Derive anchors only from `data/entries.jsonl`.
- Require source entries to have `verify == 1`.
- Deduplicate anchors by `(repo_url, commit, file, line)` for the chosen
  endpoint field.
- Preserve code snippets observed at the deduplicated location in
  `source_endpoint_codes`.
- Preserve traceability through `source_entry_ids` and `source_report_ids`.
- Do not use `trace` in endpoint-level evaluator matching.

## Entry-Point Duplicate Examples

{md_table(['anchor_id', 'source_entry_ids', 'source_report_ids'], ep_examples)}

## Critical-Operation Duplicate Examples

{md_table(['anchor_id', 'source_entry_ids', 'source_report_ids'], co_examples)}

## Machine-Readable Summary

```text
records/endpoint_ground_truth_20260608_summary.json
```
""",
        encoding="utf-8",
        newline="\n",
    )

    update_readme(ROOT / "README.md", zh=False)
    update_readme(ROOT / "README_zh.md", zh=True)
    update_schema(ROOT / "SCHEMA.md", len(entry_points), len(critical_operations))
    update_changelog(ROOT / "CHANGELOG.md", len(entry_points), len(critical_operations))

    print(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
