#!/usr/bin/env python3
"""Convert VulnGym conversion-table rows into evaluator-ready JSONL files.

The conversion table is a provenance-preserving intermediate format for
normalizing raw tool findings before running VulnGym's recall evaluators. This
script writes three evaluator inputs:

  - pair_findings.jsonl
  - entry_point_findings.jsonl
  - critical_operation_findings.jsonl

Pair-level output is intentionally conservative: explicit candidate_pairs are
honored, otherwise a row is auto-paired only when it has exactly one usable
entry-point candidate and exactly one usable critical-operation candidate.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from evaluate import normalize_line_span


CONVERSION_METHODS = {
    "direct",
    "source-resolved",
    "semantic-assisted",
    "not-converted",
}

ROW_STATUSES = {
    "converted",
    "partially-converted",
    "not-converted",
}

PAIR_OUTPUT = "pair_findings.jsonl"
ENTRY_POINT_OUTPUT = "entry_point_findings.jsonl"
CRITICAL_OPERATION_OUTPUT = "critical_operation_findings.jsonl"
SKIPPED_OUTPUT = "conversion_skipped.jsonl"
MANIFEST_OUTPUT = "conversion_manifest.json"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from None
            if not isinstance(row, dict):
                raise SystemExit(f"{path}:{line_no}: each JSONL row must be an object")
            row["_conversion_table_line"] = line_no
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def endpoint_from_candidate(candidate: dict[str, Any]) -> dict[str, Any] | None:
    if candidate.get("conversion_method") == "not-converted":
        return None
    endpoint = candidate.get("endpoint")
    if not isinstance(endpoint, dict):
        return None
    file_name = endpoint.get("file")
    if not isinstance(file_name, str) or not file_name.strip():
        return None
    line_value = endpoint.get("line")
    if normalize_line_span(line_value) is None:
        return None
    out: dict[str, Any] = {"file": file_name, "line": line_value}
    if endpoint.get("code") is not None:
        out["code"] = endpoint.get("code")
    return out


def get_candidates(row: dict[str, Any], field: str) -> list[dict[str, Any]]:
    value = row.get(field, [])
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def usable_candidates(
    row: dict[str, Any],
    field: str,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    usable: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for candidate in get_candidates(row, field):
        endpoint = endpoint_from_candidate(candidate)
        if endpoint is not None:
            usable.append((candidate, endpoint))
    return usable


def validate_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("conversion_row_id", "finding_id", "repo_url", "commit"):
        if not isinstance(row.get(field), str) or not row.get(field, "").strip():
            errors.append(f"missing_or_invalid_{field}")
    status = row.get("conversion_status")
    if status not in ROW_STATUSES:
        errors.append("invalid_conversion_status")
    for field in ("candidate_entry_points", "candidate_critical_operations"):
        value = row.get(field, [])
        if value is not None and not isinstance(value, list):
            errors.append(f"invalid_{field}")
            continue
        for candidate in value or []:
            if not isinstance(candidate, dict):
                errors.append(f"invalid_{field}_candidate")
                continue
            method = candidate.get("conversion_method")
            if method not in CONVERSION_METHODS:
                errors.append(f"invalid_{field}_conversion_method")
            candidate_id = candidate.get("candidate_id")
            if not isinstance(candidate_id, str) or not candidate_id.strip():
                errors.append(f"missing_{field}_candidate_id")
    pairs = row.get("candidate_pairs", [])
    if pairs is not None and not isinstance(pairs, list):
        errors.append("invalid_candidate_pairs")
    return errors


def method_summary(prefix: str, candidate: dict[str, Any]) -> str:
    return f"{prefix}:{candidate.get('conversion_method', 'unknown')}"


def common_fields(row: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "repo_url": row.get("repo_url"),
        "commit": row.get("commit"),
        "conversion_row_id": row.get("conversion_row_id"),
        "source_finding_id": row.get("finding_id"),
        "tool": row.get("tool"),
        "model": row.get("model"),
        "run_id": row.get("run_id"),
        "conversion_status": row.get("conversion_status"),
        "source_artifact": row.get("source_artifact"),
        "source_categories": row.get("source_categories", []),
        "vuln_category_l1_values": row.get("vuln_category_l1_values", []),
        "vuln_category_l2_values": row.get("vuln_category_l2_values", []),
        "rationale": row.get("rationale"),
    }
    return {key: value for key, value in fields.items() if value is not None}


def single_anchor_record(
    row: dict[str, Any],
    anchor_kind: str,
    candidate: dict[str, Any],
    endpoint: dict[str, Any],
) -> dict[str, Any]:
    candidate_id = candidate.get("candidate_id")
    out = common_fields(row)
    out.update(
        {
            "finding_id": (
                f"{row.get('finding_id')}::{anchor_kind}::{candidate_id}"
            ),
            "conversion_candidate_id": candidate_id,
            "conversion_method_summary": method_summary(anchor_kind, candidate),
            anchor_kind: endpoint,
        }
    )
    if candidate.get("rationale") is not None:
        out["candidate_rationale"] = candidate.get("rationale")
    if candidate.get("confidence") is not None:
        out["candidate_confidence"] = candidate.get("confidence")
    return out


def pair_record(
    row: dict[str, Any],
    pair_id: str,
    ep_candidate: dict[str, Any],
    ep_endpoint: dict[str, Any],
    co_candidate: dict[str, Any],
    co_endpoint: dict[str, Any],
    pair_rationale: str | None = None,
) -> dict[str, Any]:
    out = common_fields(row)
    out.update(
        {
            "finding_id": f"{row.get('finding_id')}::pair::{pair_id}",
            "conversion_pair_id": pair_id,
            "entry_point_candidate_id": ep_candidate.get("candidate_id"),
            "critical_operation_candidate_id": co_candidate.get("candidate_id"),
            "conversion_method_summary": ";".join(
                [
                    method_summary("entry_point", ep_candidate),
                    method_summary("critical_operation", co_candidate),
                ]
            ),
            "entry_point": ep_endpoint,
            "critical_operation": co_endpoint,
        }
    )
    trace = row.get("candidate_trace")
    if isinstance(trace, list):
        out["trace"] = trace
    if pair_rationale:
        out["pair_rationale"] = pair_rationale
    return out


def skip_record(row: dict[str, Any], reason: str, **details: Any) -> dict[str, Any]:
    out = {
        "conversion_row_id": row.get("conversion_row_id"),
        "finding_id": row.get("finding_id"),
        "line": row.get("_conversion_table_line"),
        "reason": reason,
    }
    out.update(details)
    return out


def convert_rows(
    rows: list[dict[str, Any]],
    *,
    strict: bool,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    pair_rows: list[dict[str, Any]] = []
    entry_point_rows: list[dict[str, Any]] = []
    critical_operation_rows: list[dict[str, Any]] = []
    skipped_rows: list[dict[str, Any]] = []

    for row in rows:
        errors = validate_row(row)
        if errors:
            skipped_rows.append(skip_record(row, "invalid_row", errors=sorted(set(errors))))
            if strict:
                continue
            continue

        usable_eps = usable_candidates(row, "candidate_entry_points")
        usable_cos = usable_candidates(row, "candidate_critical_operations")

        for candidate, endpoint in usable_eps:
            entry_point_rows.append(
                single_anchor_record(row, "entry_point", candidate, endpoint)
            )
        for candidate, endpoint in usable_cos:
            critical_operation_rows.append(
                single_anchor_record(row, "critical_operation", candidate, endpoint)
            )

        ep_by_id = {
            candidate.get("candidate_id"): (candidate, endpoint)
            for candidate, endpoint in usable_eps
        }
        co_by_id = {
            candidate.get("candidate_id"): (candidate, endpoint)
            for candidate, endpoint in usable_cos
        }

        pairs = row.get("candidate_pairs", [])
        if isinstance(pairs, list) and pairs:
            for index, pair in enumerate(pairs, 1):
                if not isinstance(pair, dict):
                    skipped_rows.append(skip_record(row, "invalid_candidate_pair"))
                    continue
                ep_id = pair.get("entry_point_candidate_id")
                co_id = pair.get("critical_operation_candidate_id")
                if ep_id not in ep_by_id or co_id not in co_by_id:
                    skipped_rows.append(
                        skip_record(
                            row,
                            "candidate_pair_references_unusable_endpoint",
                            entry_point_candidate_id=ep_id,
                            critical_operation_candidate_id=co_id,
                        )
                    )
                    continue
                ep_candidate, ep_endpoint = ep_by_id[ep_id]
                co_candidate, co_endpoint = co_by_id[co_id]
                pair_id = pair.get("pair_id") or f"pair-{index}"
                pair_rows.append(
                    pair_record(
                        row,
                        pair_id,
                        ep_candidate,
                        ep_endpoint,
                        co_candidate,
                        co_endpoint,
                        pair.get("rationale"),
                    )
                )
        elif len(usable_eps) == 1 and len(usable_cos) == 1:
            ep_candidate, ep_endpoint = usable_eps[0]
            co_candidate, co_endpoint = usable_cos[0]
            pair_rows.append(
                pair_record(
                    row,
                    "auto-1",
                    ep_candidate,
                    ep_endpoint,
                    co_candidate,
                    co_endpoint,
                    "Auto-paired because the conversion row has exactly one usable entry_point candidate and one usable critical_operation candidate.",
                )
            )
        else:
            skipped_rows.append(
                skip_record(
                    row,
                    "ambiguous_or_incomplete_pairing",
                    usable_entry_point_candidates=len(usable_eps),
                    usable_critical_operation_candidates=len(usable_cos),
                    policy="No Cartesian product is generated without explicit candidate_pairs.",
                )
            )

    return pair_rows, entry_point_rows, critical_operation_rows, skipped_rows


def build_manifest(
    args: argparse.Namespace,
    rows: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
    entry_point_rows: list[dict[str, Any]],
    critical_operation_rows: list[dict[str, Any]],
    skipped_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    method_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    for row in rows:
        status_counts[str(row.get("conversion_status", "missing"))] += 1
        for field in ("candidate_entry_points", "candidate_critical_operations"):
            for candidate in get_candidates(row, field):
                method_counts[str(candidate.get("conversion_method", "missing"))] += 1

    return {
        "source_conversion_table": str(args.conversion_table),
        "out_dir": str(args.out_dir),
        "policy": {
            "pairing": "explicit_candidate_pairs_or_single_ep_single_co",
            "no_cartesian_product_without_explicit_pairs": True,
            "not_converted_candidates_exported": False,
        },
        "counts": {
            "conversion_rows": len(rows),
            "pair_findings": len(pair_rows),
            "entry_point_findings": len(entry_point_rows),
            "critical_operation_findings": len(critical_operation_rows),
            "skipped_records": len(skipped_rows),
            "conversion_status": dict(sorted(status_counts.items())),
            "conversion_methods": dict(sorted(method_counts.items())),
            "skipped_reasons": dict(
                sorted(Counter(row["reason"] for row in skipped_rows).items())
            ),
        },
        "outputs": {
            "pair_findings": PAIR_OUTPUT,
            "entry_point_findings": ENTRY_POINT_OUTPUT,
            "critical_operation_findings": CRITICAL_OPERATION_OUTPUT,
            "skipped": SKIPPED_OUTPUT,
            "manifest": MANIFEST_OUTPUT,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert VulnGym conversion-table JSONL into evaluator inputs.",
    )
    parser.add_argument("conversion_table", type=Path, help="Conversion table JSONL.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory where evaluator input JSONL files will be written.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Keep invalid rows out of outputs; invalid rows are always recorded in conversion_skipped.jsonl.",
    )
    args = parser.parse_args(argv)

    rows = load_jsonl(args.conversion_table)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    pair_rows, entry_point_rows, critical_operation_rows, skipped_rows = convert_rows(
        rows,
        strict=args.strict,
    )

    write_jsonl(args.out_dir / PAIR_OUTPUT, pair_rows)
    write_jsonl(args.out_dir / ENTRY_POINT_OUTPUT, entry_point_rows)
    write_jsonl(args.out_dir / CRITICAL_OPERATION_OUTPUT, critical_operation_rows)
    write_jsonl(args.out_dir / SKIPPED_OUTPUT, skipped_rows)

    manifest = build_manifest(
        args,
        rows,
        pair_rows,
        entry_point_rows,
        critical_operation_rows,
        skipped_rows,
    )
    (args.out_dir / MANIFEST_OUTPUT).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("VulnGym conversion export")
    print("=========================")
    print(f"source rows: {len(rows)}")
    print(f"pair findings: {len(pair_rows)} -> {args.out_dir / PAIR_OUTPUT}")
    print(
        f"entry_point findings: {len(entry_point_rows)} -> "
        f"{args.out_dir / ENTRY_POINT_OUTPUT}"
    )
    print(
        f"critical_operation findings: {len(critical_operation_rows)} -> "
        f"{args.out_dir / CRITICAL_OPERATION_OUTPUT}"
    )
    print(f"skipped records: {len(skipped_rows)} -> {args.out_dir / SKIPPED_OUTPUT}")
    print(f"manifest: {args.out_dir / MANIFEST_OUTPUT}")

    if skipped_rows:
        print()
        print("skipped reasons:")
        for reason, count in sorted(Counter(row["reason"] for row in skipped_rows).items()):
            print(f"  {reason}: {count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
