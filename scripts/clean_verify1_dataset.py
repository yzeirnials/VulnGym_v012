#!/usr/bin/env python3
"""Check verified-entry filtering, or write a cleaned copy to a new directory.

The published dataset is already verified. With no --output-dir this command
only validates it. Explicit cleaning preserves IDs and rebuilds report/anchor
source references, descriptions, and the manifest together; historical records
and documentation are never rewritten.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from subset_dataset import (ROOT, TABLES, dataset_files, load_jsonl, publish_new,
                            require, select_tables, validate_dataset)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="Read-only validation (the default).")
    parser.add_argument("--output-dir", type=Path, help="New directory for a complete verified dataset copy.")
    args = parser.parse_args(argv)
    try:
        require(not (args.check and args.output_dir), "--check cannot write outputs")
        if args.output_dir is None:
            result = validate_dataset(args.dataset_root)
        else:
            require(not args.output_dir.exists(), "output directory already exists; use a new directory")
            data = args.dataset_root / "data"
            tables = {name: load_jsonl(data / f"{name}.jsonl") for name in TABLES}
            retained = {e["entry_id"] for e in tables["entries"] if type(e.get("verify")) is int and e["verify"] == 1}
            selected = select_tables(tables, retained)
            manifest = []
            for row in load_jsonl(data / "batch_manifest.jsonl"):
                entry_ids = [eid for eid in row["entry_ids"] if eid in retained]
                if entry_ids:
                    manifest.append({**row, "entry_ids": entry_ids})
            metadata = json.loads((data / "dataset.json").read_text(encoding="utf-8"))
            metadata["selected_batch_ids"] = [b for b in metadata["selected_batch_ids"]
                                               if b in {row["batch_id"] for row in manifest}]
            if len(retained) != len(tables["entries"]):
                metadata["dataset_id"] = "vulngym-verified-subset"
                metadata["generator"] = "scripts/clean_verify1_dataset.py"
                metadata["selection_policy"] = "Retain verify == 1 within the input dataset, preserving IDs and locations."
            publish_new(args.output_dir, dataset_files(selected, manifest, metadata))
            result = validate_dataset(args.output_dir)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"verified-dataset check/clean failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
