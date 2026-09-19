"""Regression checks for membership, source identity, and safe maintenance."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import subset_dataset as subset
from build_endpoint_ground_truth import build_anchor_rows


class DatasetSubsetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = {name: subset.load_jsonl(ROOT / "data" / f"{name}.jsonl") for name in subset.TABLES}
        cls.manifest = subset.load_jsonl(ROOT / "data/batch_manifest.jsonl")
        cls.metadata = json.loads((ROOT / "data/dataset.json").read_text(encoding="utf-8"))

    def test_published_membership_and_denominators(self):
        result = subset.validate_dataset(ROOT)
        self.assertEqual(result["counts"], {
            "entries": 156, "entries_desc": 156, "reports": 61,
            "entry_points": 136, "critical_operations": 137,
            "snapshots": 55, "repositories": 23, "batches": 6,
        })
        self.assertEqual(set(self.metadata["selected_batch_ids"]), set(subset.DEFAULT_BATCHES))
        self.assertEqual(self.metadata["source_dataset_commit"], subset.SOURCE_REF)
        self.assertEqual(self.metadata["descriptions_source_commit"], subset.DESCRIPTIONS_REF)

    def test_reproduction_from_git_preserves_source_and_exact_bytes(self):
        before = {name: (ROOT / "data" / f"{name}.jsonl").read_bytes() for name in subset.TABLES}
        head = subset.resolve_ref(ROOT, "HEAD")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "reproduced"
            subset.build_subset(ROOT, subset.SOURCE_REF, ROOT / "data/batch_manifest.jsonl", output)
            for relative in self.metadata["files_sha256"]:
                self.assertEqual((ROOT / relative).read_bytes(), (output / relative).read_bytes(), relative)
            self.assertEqual((ROOT / "data/dataset.json").read_bytes(), (output / "data/dataset.json").read_bytes())
            with self.assertRaisesRegex(ValueError, "already exists"):
                subset.build_subset(ROOT, subset.SOURCE_REF, ROOT / "data/batch_manifest.jsonl", output)
        self.assertEqual(head, subset.resolve_ref(ROOT, "HEAD"))
        for name, content in before.items():
            self.assertEqual(content, (ROOT / "data" / f"{name}.jsonl").read_bytes())

    def test_every_batch_has_expected_counts_and_closed_references(self):
        expected = {
            "openclaw-01": (32, 7, 18, 19, 6), "mixed-01": (27, 11, 27, 27, 10),
            "mixed-02": (21, 10, 19, 19, 7), "mixed-03": (30, 10, 27, 26, 9),
            "mixed-04": (34, 14, 33, 34, 14), "mixed-05": (12, 9, 12, 12, 9),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for batch, counts in expected.items():
                with self.subTest(batch=batch):
                    output = Path(tmp) / batch
                    result = subset.build_subset(ROOT, subset.SOURCE_REF, ROOT / "data/batch_manifest.jsonl", output, [batch])
                    self.assertEqual(tuple(result["counts"][k] for k in
                                           ("entries", "reports", "entry_points", "critical_operations", "snapshots")), counts)
                    selected_ids = {e["entry_id"] for e in subset.load_jsonl(output / "data/entries.jsonl")}
                    for table in subset.ENDPOINTS:
                        self.assertTrue(all(set(a["source_entry_ids"]) <= selected_ids for a in
                                            subset.load_jsonl(output / "data" / f"{table}.jsonl")))

    def test_rejects_ambiguous_or_incorrect_manifest(self):
        repeated = deepcopy(self.manifest)
        repeated[0]["entry_ids"].append(repeated[0]["entry_ids"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            subset.validate_manifest(repeated, self.tables["entries"])
        mismatched = deepcopy(self.manifest)
        mismatched[0]["commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "repo/commit"):
            subset.validate_manifest(mismatched, self.tables["entries"])
        with self.assertRaisesRegex(ValueError, "cover all"):
            subset.validate_manifest(self.manifest[1:], self.tables["entries"])
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "unknown batch"):
                subset.build_subset(ROOT, subset.SOURCE_REF, ROOT / "data/batch_manifest.jsonl",
                                    Path(tmp) / "bad", ["openclaw-05"])
            self.assertFalse((Path(tmp) / "bad").exists())

    def test_rejects_description_or_anchor_corruption(self):
        tables = deepcopy(self.tables)
        tables["entries_desc"][0]["entry_point"]["line"] += 1
        with self.assertRaisesRegex(ValueError, "descriptions alter"):
            subset.validate_tables(tables)
        tables = deepcopy(self.tables)
        tables["entry_points"][0]["source_entry_ids"].append("entry-excluded")
        with self.assertRaisesRegex(ValueError, "metadata mismatch"):
            subset.validate_tables(tables)
        tables = deepcopy(self.tables)
        tables["reports"][0]["num_entries"] += 1
        with self.assertRaisesRegex(ValueError, "membership/count mismatch"):
            subset.validate_tables(tables)

    def test_filtering_preserves_anchor_ids_and_rebuild_is_idempotent(self):
        ids = {eid for row in self.manifest if row["batch_id"] == "openclaw-01" for eid in row["entry_ids"]}
        selected = subset.select_tables(self.tables, ids)
        for table, field in subset.ENDPOINTS.items():
            rows = build_anchor_rows(selected["entries"], field=field,
                                     anchor_prefix=field.replace("_", "-"), existing=self.tables[table])
            self.assertEqual(rows, selected[table])
            self.assertEqual(build_anchor_rows(selected["entries"], field=field,
                                              anchor_prefix=field.replace("_", "-"), existing=rows), rows)

    def test_partial_report_and_anchor_selection_closes_all_source_metadata(self):
        anchor = next(a for a in self.tables["entry_points"] if len(a["source_entry_ids"]) > 1)
        eid = anchor["source_entry_ids"][0]
        selected = subset.select_tables(self.tables, {eid})
        subset.validate_tables(selected)
        self.assertEqual(len(selected["reports"]), 1)
        self.assertEqual(selected["reports"][0]["entry_ids"], [eid])
        self.assertEqual(selected["reports"][0]["num_entries"], 1)
        self.assertEqual(selected["entry_points"][0]["anchor_id"], anchor["anchor_id"])
        for table in subset.ENDPOINTS:
            self.assertEqual(selected[table][0]["source_entry_ids"], [eid])
            self.assertEqual(selected[table][0]["source_report_ids"], [selected["reports"][0]["report_id"]])

    def test_new_anchor_identity_is_stable_when_earlier_entries_are_removed(self):
        entries = self.tables["entries"][:5]
        first = build_anchor_rows(entries, field="entry_point", anchor_prefix="entry-point")
        second = build_anchor_rows(entries[1:], field="entry_point", anchor_prefix="entry-point")
        by_key = {subset.endpoint_key(a, "entry_point"): a["anchor_id"] for a in first}
        for row in second:
            self.assertEqual(row["anchor_id"], by_key[subset.endpoint_key(row, "entry_point")])

    def test_maintenance_defaults_do_not_modify_data_docs_or_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dataset"
            subset.publish_new(root, subset.dataset_files(self.tables, self.manifest, self.metadata))
            (root / "records").mkdir()
            for name in ("README.md", "README_zh.md", "SCHEMA.md", "CHANGELOG.md", "records/history.json"):
                (root / name).write_text("immutable sentinel\n", encoding="utf-8")
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            for script in ("build_endpoint_ground_truth.py", "clean_verify1_dataset.py"):
                proc = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--dataset-root", str(root)],
                                      capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(before, {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()})
            output = Path(tmp) / "cleaned"
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/clean_verify1_dataset.py"),
                                   "--dataset-root", str(root), "--output-dir", str(output)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            for relative in self.metadata["files_sha256"]:
                self.assertEqual((root / relative).read_bytes(), (output / relative).read_bytes())

    def test_standalone_validator_rejects_changed_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dataset"
            subset.publish_new(root, subset.dataset_files(self.tables, self.manifest, self.metadata))
            with (root / "data/entries.jsonl").open("ab") as stream:
                stream.write(b"\n")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                subset.validate_dataset(root)


if __name__ == "__main__":
    unittest.main()
