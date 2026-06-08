#!/usr/bin/env python3
"""Evaluate defect-location localization against VulnGym critical-operation anchors."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from evaluate import (
    line_spans_match,
    load_jsonl,
    normalize_commit,
    normalize_line_span,
    normalize_path,
    normalize_repo,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GROUND_TRUTH = REPO_ROOT / "data" / "critical_operations.jsonl"
DEFAULT_TOLERANCE = 5
ANCHOR_KIND = "critical_operation"
ANCHOR_LABEL = "critical-operation"


def anchor_matches_finding(finding: dict, anchor: dict, tolerance: int) -> bool:
    f_ep = finding.get(ANCHOR_KIND, {})
    a_ep = anchor.get(ANCHOR_KIND, {})
    if not f_ep or not a_ep:
        return False
    if normalize_path(f_ep.get("file", "")) != normalize_path(a_ep.get("file", "")):
        return False
    f_span = normalize_line_span(f_ep.get("line"))
    a_span = normalize_line_span(a_ep.get("line"))
    if f_span is None or a_span is None:
        return False
    return line_spans_match(f_span, a_span, tolerance)


def evaluate_anchors(
    anchors: list[dict],
    findings: list[dict],
    tolerance: int,
) -> dict[str, Any]:
    usable_anchors: list[dict] = []
    skipped_anchors: list[dict] = []
    for anchor in anchors:
        span = normalize_line_span(anchor.get(ANCHOR_KIND, {}).get("line"))
        if span is None:
            skipped_anchors.append(anchor)
        else:
            usable_anchors.append(anchor)

    by_repo_commit: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for anchor in usable_anchors:
        key = (normalize_repo(anchor["repo_url"]), normalize_commit(anchor["commit"]))
        by_repo_commit[key].append(anchor)

    all_source_entry_ids = {eid for a in usable_anchors for eid in a["source_entry_ids"]}
    all_report_ids = {rid for a in usable_anchors for rid in a["source_report_ids"]}

    matched_anchor_ids: set[str] = set()
    matched_source_entry_ids: set[str] = set()
    matched_report_ids: set[str] = set()
    finding_details: list[dict] = []

    for i, finding in enumerate(findings):
        key = (
            normalize_repo(finding.get("repo_url", "")),
            normalize_commit(finding.get("commit", "")),
        )
        matches: list[dict] = []
        if key[0] and key[1]:
            for anchor in by_repo_commit.get(key, ()):
                if anchor_matches_finding(finding, anchor, tolerance):
                    matches.append(anchor)
                    matched_anchor_ids.add(anchor["anchor_id"])
                    matched_source_entry_ids.update(anchor["source_entry_ids"])
                    matched_report_ids.update(anchor["source_report_ids"])
        finding_details.append(
            {
                "index": i,
                "finding_id": finding.get("finding_id"),
                "repo_url": finding.get("repo_url"),
                "commit": finding.get("commit"),
                ANCHOR_KIND: finding.get(ANCHOR_KIND),
                "matched_anchor_ids": sorted(a["anchor_id"] for a in matches),
                "matched_source_entry_ids": sorted(
                    {eid for a in matches for eid in a["source_entry_ids"]}
                ),
                "matched_report_ids": sorted(
                    {rid for a in matches for rid in a["source_report_ids"]}
                ),
            }
        )

    total_anchors = len(usable_anchors)
    total_source_entries = len(all_source_entry_ids)
    total_reports = len(all_report_ids)
    matched_anchors = len(matched_anchor_ids)
    matched_source_entries = len(matched_source_entry_ids)
    matched_reports = len(matched_report_ids)

    return {
        "config": {
            "anchor_kind": ANCHOR_KIND,
            "line_tolerance": tolerance,
            "match_path": "normalized_exact",
            "line_policy": "int_or_range_span",
            "unusable_ground_truth_line_policy": "skip",
        },
        "totals": {
            "ground_truth_anchors": len(anchors),
            "skipped_anchors_unusable_line": len(skipped_anchors),
            "usable_anchors": total_anchors,
            "source_entries": total_source_entries,
            "source_reports": total_reports,
            "findings": len(findings),
        },
        "recall": {
            "anchor_level": {
                "numerator": matched_anchors,
                "denominator": total_anchors,
                "value": matched_anchors / total_anchors if total_anchors else 0.0,
            },
            "report_level": {
                "numerator": matched_reports,
                "denominator": total_reports,
                "value": matched_reports / total_reports if total_reports else 0.0,
            },
            "source_entry_coverage": {
                "numerator": matched_source_entries,
                "denominator": total_source_entries,
                "value": (
                    matched_source_entries / total_source_entries
                    if total_source_entries
                    else 0.0
                ),
            },
        },
        "findings": finding_details,
    }


def print_summary(report: dict, verbose: bool) -> None:
    cfg = report["config"]
    totals = report["totals"]
    anchor = report["recall"]["anchor_level"]
    report_level = report["recall"]["report_level"]
    source_entry = report["recall"]["source_entry_coverage"]

    print(f"VulnGym {ANCHOR_LABEL} evaluation")
    print("=" * (len("VulnGym ") + len(ANCHOR_LABEL) + len(" evaluation")))
    print(
        f"policy: line_tolerance=+/-{cfg['line_tolerance']} | "
        f"path={cfg['match_path']} | line={cfg['line_policy']} | "
        f"unusable_line_policy={cfg['unusable_ground_truth_line_policy']}"
    )
    print()
    print(
        f"ground truth:  {totals['usable_anchors']} {ANCHOR_LABEL} anchors "
        f"(skipped {totals['skipped_anchors_unusable_line']} with unusable line)"
    )
    print(
        f"source scope:  {totals['source_reports']} reports / "
        f"{totals['source_entries']} pair-level entries"
    )
    print(f"findings:      {totals['findings']} reported by the tool")
    print()
    print(
        f"Anchor-level recall (primary): "
        f"{anchor['numerator']} / {anchor['denominator']} = "
        f"{anchor['value']*100:.2f}%"
    )
    print(
        f"Report-level recall (supplemental): "
        f"{report_level['numerator']} / {report_level['denominator']} = "
        f"{report_level['value']*100:.2f}%"
    )
    print(
        f"Source-entry coverage (supplemental): "
        f"{source_entry['numerator']} / {source_entry['denominator']} = "
        f"{source_entry['value']*100:.2f}%"
    )

    unmatched_findings = [f for f in report["findings"] if not f["matched_anchor_ids"]]
    if unmatched_findings:
        print()
        print(
            f"note: {len(unmatched_findings)} of {totals['findings']} findings did "
            f"not match any ground-truth {ANCHOR_LABEL} anchor under this policy."
        )

    if verbose:
        print()
        print("per-finding detail")
        print("------------------")
        for f in report["findings"]:
            hits = ",".join(f["matched_anchor_ids"]) if f["matched_anchor_ids"] else "-"
            print(f"  finding[{f['index']}] {f.get('finding_id')}: matched=[{hits}]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=f"Evaluate VulnGym {ANCHOR_LABEL} localization.",
    )
    parser.add_argument("findings", type=Path, help="Path to tool findings JSONL.")
    parser.add_argument(
        "--ground-truth",
        type=Path,
        default=DEFAULT_GROUND_TRUTH,
        help=f"Ground-truth anchors (default: {DEFAULT_GROUND_TRUTH.relative_to(REPO_ROOT)}).",
    )
    parser.add_argument(
        "--line-tolerance",
        type=int,
        default=DEFAULT_TOLERANCE,
        help="Max line delta allowed for the anchor location (default: %(default)s).",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    if args.line_tolerance < 0:
        parser.error("--line-tolerance must be >= 0")

    anchors = load_jsonl(args.ground_truth)
    findings = load_jsonl(args.findings)
    report = evaluate_anchors(anchors, findings, args.line_tolerance)
    print_summary(report, args.verbose)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nwrote JSON report -> {args.json_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
