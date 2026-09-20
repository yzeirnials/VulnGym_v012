#!/usr/bin/env python3
"""Build or validate a closed batch subset without changing its source checkout."""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REF = "90002144d4a8b3654fb1bf68052889b9c2de44aa"
DESCRIPTIONS_REF = "4c4ac5659329008d9ea44ac5ec7855eae6909c2e"
DEFAULT_BATCHES = ("openclaw-01", "mixed-01", "mixed-02", "mixed-03", "mixed-04", "mixed-05")
TABLES = ("entries", "reports", "entry_points", "critical_operations", "entries_desc")
ENDPOINTS = {"entry_points": "entry_point", "critical_operations": "critical_operation"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_jsonl(raw: bytes) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    require(all(isinstance(row, dict) for row in rows), "JSONL rows must be objects")
    return rows


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return parse_jsonl(path.read_bytes())


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                    for row in rows)).encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_bytes(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def resolve_ref(root: Path, ref: str) -> str:
    return git_bytes(root, "rev-parse", "--verify", ref + "^{commit}").decode().strip()


def stable_unique(values: list[Any]) -> list[Any]:
    values_by_key = {json.dumps(v, ensure_ascii=False, sort_keys=True): v for v in values}
    return [values_by_key[k] for k in sorted(values_by_key)]


def endpoint_key(row: dict, field: str) -> tuple[str, str, str, str]:
    endpoint = row[field]
    return row["repo_url"], row["commit"], endpoint["file"], str(endpoint["line"])


def strip_descriptions(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: strip_descriptions(v) for k, v in value.items() if k != "desc"}
    if isinstance(value, list):
        return [strip_descriptions(v) for v in value]
    return value


def unique_rows(rows: list[dict], key: str) -> dict[str, dict]:
    result = {row[key]: row for row in rows}
    require(len(result) == len(rows), f"duplicate {key}")
    require(all(isinstance(k, str) and k for k in result), f"invalid {key}")
    return result


def anchor_metadata(row: dict, entries: list[dict], field: str) -> dict:
    result = deepcopy(row)
    result["source_entry_ids"] = sorted(e["entry_id"] for e in entries)
    result["source_report_ids"] = sorted({e["report_id"] for e in entries})
    for output, source in (("projects", "project"), ("source_links", "source_link"),
                           ("vuln_titles", "vuln_title"), ("vuln_category_l1", "vuln_category_l1"),
                           ("vuln_category_l2", "vuln_category_l2")):
        result[output] = stable_unique([e[source] for e in entries])
    result["vuln_ids"] = stable_unique([v for e in entries for v in e.get("vuln_ids", [])])
    result["source_endpoint_codes"] = stable_unique([e[field]["code"] for e in entries if e[field].get("code")])
    return result


def select_tables(tables: dict[str, list[dict]], ids: set[str]) -> dict[str, list[dict]]:
    entries = [deepcopy(e) for e in tables["entries"] if e["entry_id"] in ids]
    by_id = {e["entry_id"]: e for e in entries}
    require(set(by_id) == ids, "selection contains unknown entry IDs")
    reports_to_ids: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        reports_to_ids[entry["report_id"]].append(entry["entry_id"])
    reports = []
    for report in tables["reports"]:
        if report["report_id"] in reports_to_ids:
            row = deepcopy(report)
            row["entry_ids"] = sorted(reports_to_ids[row["report_id"]])
            row["num_entries"] = len(row["entry_ids"])
            reports.append(row)
    selected = {"entries": entries, "reports": reports}
    for table, field in ENDPOINTS.items():
        selected[table] = [anchor_metadata(a, [by_id[e] for e in a["source_entry_ids"] if e in ids], field)
                           for a in tables[table] if set(a["source_entry_ids"]) & ids]
    selected["entries_desc"] = [deepcopy(e) for e in tables["entries_desc"] if e["entry_id"] in ids]
    return selected


def validate_tables(tables: dict[str, list[dict]]) -> None:
    entries = unique_rows(tables["entries"], "entry_id")
    require(bool(entries), "dataset must have entries")
    for entry in entries.values():
        require(type(entry.get("verify")) is int and entry["verify"] == 1, "entry is not verified")
        require(bool(entry.get("repo_url")) and bool(re.fullmatch(r"[0-9a-fA-F]{40}", entry.get("commit", ""))),
                "entry has invalid repo/commit")
        for field in ENDPOINTS.values():
            endpoint = entry[field]
            file = endpoint["file"]
            require(isinstance(file, str) and file and not file.startswith(("/", "\\"))
                    and ":" not in file and ".." not in file.replace("\\", "/").split("/"), "unsafe endpoint path")
            line = endpoint["line"]
            match = re.fullmatch(r"([1-9][0-9]*)(?:-([1-9][0-9]*))?", str(line))
            require(type(line) in (int, str) and bool(match), "invalid endpoint line")
            require(not match[2] or int(match[2]) >= int(match[1]), "reversed endpoint span")
    reports = unique_rows(tables["reports"], "report_id")
    require(set(reports) == {e["report_id"] for e in entries.values()}, "report references are not closed")
    for rid, report in reports.items():
        source = [e for e in entries.values() if e["report_id"] == rid]
        require(report["entry_ids"] == sorted(e["entry_id"] for e in source)
                and report["num_entries"] == len(source), "report membership/count mismatch")
        require(all((e["repo_url"], e["commit"]) == (report["repo_url"], report["commit"]) for e in source),
                "report repo/commit mismatch")
    descriptions = unique_rows(tables["entries_desc"], "entry_id")
    require(set(descriptions) == set(entries), "description membership mismatch")
    require(all(strip_descriptions(descriptions[eid]) == e for eid, e in entries.items()),
            "descriptions alter original entry fields")
    for table, field in ENDPOINTS.items():
        anchors = tables[table]
        unique_rows(anchors, "anchor_id")
        groups: dict[tuple, list[dict]] = defaultdict(list)
        for entry in entries.values():
            groups[endpoint_key(entry, field)].append(entry)
        keys = [endpoint_key(a, field) for a in anchors]
        require(len(keys) == len(set(keys)) and set(keys) == set(groups), "anchor locations/coverage mismatch")
        for anchor in anchors:
            require(anchor["anchor_kind"] == field and anchor.get("verify") == 1, "invalid anchor kind/verify")
            require(anchor == anchor_metadata(anchor, groups[endpoint_key(anchor, field)], field),
                    "anchor source metadata mismatch")
            require(anchor[field] in [e[field] for e in groups[endpoint_key(anchor, field)]],
                    "anchor endpoint differs from its source entries")


def validate_manifest(manifest: list[dict], entries: list[dict], *, complete: bool = True) -> None:
    by_id = unique_rows(entries, "entry_id")
    snapshots = set()
    assigned = set()
    for row in manifest:
        require(isinstance(row.get("batch_id"), str) and row["batch_id"], "invalid batch ID")
        key = row["repo_url"], row["commit"]
        require(key not in snapshots, "duplicate or split manifest snapshot")
        snapshots.add(key)
        require(isinstance(row["entry_ids"], list) and row["entry_ids"], "empty manifest snapshot")
        for eid in row["entry_ids"]:
            require(eid in by_id and eid not in assigned, "unknown or duplicate manifest entry")
            require((by_id[eid]["repo_url"], by_id[eid]["commit"]) == key, "manifest repo/commit mismatch")
            assigned.add(eid)
    if complete:
        require(assigned == set(by_id), "manifest does not cover all entries")


def counts(tables: dict[str, list[dict]], manifest: list[dict]) -> dict[str, int]:
    return {**{name: len(tables[name]) for name in TABLES}, "snapshots": len(manifest),
            "repositories": len({r["repo_url"] for r in manifest}),
            "batches": len({r["batch_id"] for r in manifest})}


def dataset_files(tables: dict[str, list[dict]], manifest: list[dict], metadata: dict) -> dict[str, bytes]:
    validate_tables(tables)
    validate_manifest(manifest, tables["entries"])
    files = {f"data/{name}.jsonl": jsonl_bytes(tables[name]) for name in TABLES}
    files["data/batch_manifest.jsonl"] = jsonl_bytes(manifest)
    metadata = deepcopy(metadata)
    metadata["counts"] = counts(tables, manifest)
    metadata["files_sha256"] = {name: sha256(raw) for name, raw in files.items()}
    files["data/dataset.json"] = json_bytes(metadata)
    return files


def publish_new(output_dir: Path, files: dict[str, bytes]) -> None:
    require(not output_dir.exists(), "output directory already exists; use a new directory")
    output_dir.mkdir(parents=True)
    for relative, content in files.items():
        destination = output_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)


def validate_dataset(root: Path) -> dict:
    tables = {name: load_jsonl(root / "data" / f"{name}.jsonl") for name in TABLES}
    manifest = load_jsonl(root / "data/batch_manifest.jsonl")
    metadata = json.loads((root / "data/dataset.json").read_text(encoding="utf-8"))
    validate_tables(tables)
    validate_manifest(manifest, tables["entries"])
    require(metadata["counts"] == counts(tables, manifest), "declared counts mismatch")
    batches = metadata["selected_batch_ids"]
    require(len(batches) == len(set(batches)) and set(batches) == {r["batch_id"] for r in manifest},
            "declared batch membership mismatch")
    required_files = {f"data/{n}.jsonl" for n in TABLES} | {"data/batch_manifest.jsonl"}
    require(set(metadata["files_sha256"]) == required_files, "dataset hash inventory mismatch")
    for relative, expected in metadata["files_sha256"].items():
        require(sha256((root / relative).read_bytes()) == expected, f"checksum mismatch: {relative}")
    return {"status": "passed", "dataset_id": metadata["dataset_id"], "counts": metadata["counts"]}


def build_subset(source_root: Path, source_ref: str, manifest_path: Path, output_dir: Path,
                 batch_ids: list[str] | None = None, descriptions_ref: str = DESCRIPTIONS_REF) -> dict:
    require(not output_dir.exists(), "output directory already exists; use a new directory")
    require(output_dir.resolve() != source_root.resolve(), "source and output roots must differ")
    selected_batches = list(DEFAULT_BATCHES if batch_ids is None else batch_ids)
    require(bool(selected_batches) and len(selected_batches) == len(set(selected_batches)), "batch IDs must be unique")
    source_commit = resolve_ref(source_root, source_ref)
    descriptions_commit = resolve_ref(source_root, descriptions_ref)
    tables = {name: parse_jsonl(git_bytes(source_root, "show", f"{source_commit}:data/{name}.jsonl"))
              for name in TABLES if name != "entries_desc"}
    tables["entries_desc"] = parse_jsonl(git_bytes(source_root, "show", f"{descriptions_commit}:data/entries_desc.jsonl"))
    validate_tables(tables)
    manifest = load_jsonl(manifest_path)
    validate_manifest(manifest, tables["entries"], complete=False)
    require(set(selected_batches) <= {r["batch_id"] for r in manifest}, "unknown batch ID")
    selected_manifest = [r for r in manifest if r["batch_id"] in selected_batches]
    ids = {eid for row in selected_manifest for eid in row["entry_ids"]}
    selected = select_tables(tables, ids)
    metadata = {
        "schema_version": 1, "dataset_id": "vulngym-six-batches" if set(selected_batches) == set(DEFAULT_BATCHES)
        else "vulngym-batch-subset", "selected_batch_ids": selected_batches,
        "source_repository": "https://github.com/yzeirnials/VulnGym_v012",
        "source_dataset_commit": source_commit, "descriptions_source_commit": descriptions_commit,
        "selection_manifest": "data/batch_manifest.jsonl", "generator": "scripts/subset_dataset.py",
        "selection_policy": "Exact entry IDs from the selected repo/commit batch rows; preserve source IDs and locations.",
    }
    publish_new(output_dir, dataset_files(selected, selected_manifest, metadata))
    return validate_dataset(output_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="Read-only validation of all tables, identities, and declared counts.")
    parser.add_argument("--dataset-root", type=Path, default=ROOT)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--source-ref", default=SOURCE_REF)
    parser.add_argument("--descriptions-ref", default=DESCRIPTIONS_REF)
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/batch_manifest.jsonl")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--batch-id", action="append", help="Repeat to select batches; default is all six published batches.")
    args = parser.parse_args(argv)
    try:
        if args.validate:
            require(args.output_dir is None, "--validate cannot write an output directory")
            result = validate_dataset(args.dataset_root)
        else:
            require(args.output_dir is not None, "--output-dir is required for generation")
            result = build_subset(args.source_root, args.source_ref, args.manifest, args.output_dir,
                                  args.batch_id, args.descriptions_ref)
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"dataset validation/generation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
