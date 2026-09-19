#!/usr/bin/env python3
"""Check or rebuild endpoint views while retaining existing anchor identities.

The default is read-only. --output-dir writes both endpoint tables to a new
folder and never changes documentation or historical cleaning records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from subset_dataset import (ENDPOINTS, ROOT, anchor_metadata, endpoint_key,
                            jsonl_bytes, load_jsonl, publish_new, require,
                            stable_unique, unique_rows)


def build_anchor_rows(entries: list[dict], *, field: str, anchor_prefix: str,
                      existing: list[dict] | None = None) -> list[dict]:
    unique_rows(entries, "entry_id")
    require(all(type(e.get("verify")) is int and e["verify"] == 1 for e in entries),
            "entries must be filtered to verify == 1 first")
    old_rows = existing or []
    unique_rows(old_rows, "anchor_id")
    old_by_key = {endpoint_key(a, field): a for a in old_rows}
    require(len(old_by_key) == len(old_rows), "duplicate existing endpoint identity")
    groups: dict[tuple, list[dict]] = {}
    for entry in entries:
        groups.setdefault(endpoint_key(entry, field), []).append(entry)
    result = []
    for key, source in sorted(groups.items()):
        source.sort(key=lambda e: e["entry_id"])
        if key in old_by_key:
            row = old_by_key[key]
        else:
            # New locations use a content-derived ID; filtering cannot renumber IDs.
            digest = hashlib.sha256(json.dumps(key, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()[:20]
            row = {"anchor_id": f"{anchor_prefix}-{digest}", "anchor_kind": field,
                   "repo_url": key[0], "commit": key[1], field: source[0][field], "verify": 1}
        result.append(anchor_metadata(row, source, field))
    unique_rows(result, "anchor_id")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="Read-only check (the default).")
    parser.add_argument("--output-dir", type=Path, help="New folder for regenerated endpoint JSONL files.")
    args = parser.parse_args(argv)
    try:
        require(not (args.check and args.output_dir), "--check cannot write outputs")
        data = args.dataset_root / "data"
        entries = load_jsonl(data / "entries.jsonl")
        generated = {}
        for table, field in ENDPOINTS.items():
            path = data / f"{table}.jsonl"
            existing = load_jsonl(path) if path.exists() else []
            rows = build_anchor_rows(entries, field=field, anchor_prefix=field.replace("_", "-"), existing=existing)
            if args.output_dir is None:
                require(rows == existing, f"{table} differs from its derived view; use --output-dir to inspect a rebuild")
            generated[table] = rows
        if args.output_dir:
            publish_new(args.output_dir, {f"{name}.jsonl": jsonl_bytes(rows) for name, rows in generated.items()})
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"endpoint check/build failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "passed", "mode": "write" if args.output_dir else "check",
                      "counts": {name: len(rows) for name, rows in generated.items()}}, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
