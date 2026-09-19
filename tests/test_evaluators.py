"""Compatibility checks for the six-batch recall evaluators and exporter."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))

import conversion_table_to_eval_inputs as converter
import evaluate as pair
import evaluate_entry_points as ep
import evaluate_critical_operations as co


REPO = "https://github.com/example/project"
COMMIT = "a" * 40


def fixture_entries() -> list[dict]:
    return [
        {
            "entry_id": "entry-1", "report_id": "report-1",
            "repo_url": REPO, "commit": COMMIT,
            "entry_point": {"file": "src/handler.py", "line": 10},
            "critical_operation": {"file": "src/storage.py", "line": 90},
        },
        {
            "entry_id": "entry-2", "report_id": "report-2",
            "repo_url": REPO, "commit": COMMIT,
            "entry_point": {"file": "src/handler.py", "line": 10},
            "critical_operation": {"file": "src/storage.py", "line": 120},
        },
    ]


def fixture_anchors() -> tuple[list[dict], list[dict]]:
    entries = fixture_entries()
    entry_points = [{
        "anchor_id": "entry-point-00007", "anchor_kind": "entry_point",
        "repo_url": REPO, "commit": COMMIT,
        "entry_point": deepcopy(entries[0]["entry_point"]),
        "source_entry_ids": ["entry-1", "entry-2"],
        "source_report_ids": ["report-1", "report-2"],
    }]
    critical_operations = [{
        "anchor_id": f"critical-operation-{index:05d}",
        "anchor_kind": "critical_operation", "repo_url": REPO, "commit": COMMIT,
        "critical_operation": deepcopy(entry["critical_operation"]),
        "source_entry_ids": [entry["entry_id"]],
        "source_report_ids": [entry["report_id"]],
    } for index, entry in enumerate(entries, 12)]
    return entry_points, critical_operations


class EvaluatorCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.entries = fixture_entries()
        self.entry_points, self.critical_operations = fixture_anchors()
        self.cases = [
            ("pair", pair.evaluate, self.entries),
            ("entry_point", ep.evaluate_anchors, self.entry_points),
            ("critical_operation", co.evaluate_anchors, self.critical_operations),
        ]

    def test_empty_findings_keep_full_denominators(self) -> None:
        for name, evaluate, ground_truth in self.cases:
            with self.subTest(name=name):
                result = evaluate(ground_truth, [], 5)
                for metric in result["recall"].values():
                    self.assertGreater(metric["denominator"], 0)
                    self.assertEqual(metric["numerator"], 0)
                    self.assertEqual(metric["value"], 0.0)

    def test_ground_truth_self_match_and_duplicate_invariance(self) -> None:
        for name, evaluate, ground_truth in self.cases:
            with self.subTest(name=name):
                result = evaluate(ground_truth, ground_truth, 5)
                doubled = evaluate(ground_truth, ground_truth * 2, 5)
                self.assertEqual(result["recall"], doubled["recall"])
                for metric in result["recall"].values():
                    self.assertEqual(metric["value"], 1.0)

    def test_same_location_in_different_commit_or_repository_does_not_match(self) -> None:
        for field, other in [("commit", "b" * 40), ("repo_url", REPO + "-other")]:
            for name, evaluate, ground_truth in self.cases:
                with self.subTest(name=name, field=field):
                    findings = deepcopy(ground_truth)
                    for finding in findings:
                        finding[field] = other
                    result = evaluate(ground_truth, findings, 5)
                    self.assertTrue(all(m["numerator"] == 0 for m in result["recall"].values()))

    def test_roles_remain_directional(self) -> None:
        findings = deepcopy(self.entries)
        for finding in findings:
            finding["entry_point"], finding["critical_operation"] = (
                finding["critical_operation"], finding["entry_point"],
            )
        for name, evaluate, ground_truth in self.cases:
            with self.subTest(name=name):
                result = evaluate(ground_truth, findings, 5)
                self.assertTrue(all(m["numerator"] == 0 for m in result["recall"].values()))

    def test_duplicate_anchor_sources_count_as_two_entries_not_two_anchors(self) -> None:
        result = ep.evaluate_anchors(self.entry_points, [self.entries[0]], 5)
        self.assertEqual(result["recall"]["anchor_level"]["numerator"], 1)
        self.assertEqual(result["recall"]["source_entry_coverage"]["numerator"], 2)
        self.assertEqual(result["recall"]["report_level"]["numerator"], 2)

    def test_unusable_lines_are_excluded_from_denominators(self) -> None:
        for name, evaluate, ground_truth in self.cases:
            with self.subTest(name=name):
                invalid = deepcopy(ground_truth[0])
                if name == "pair":
                    invalid.update(entry_id="unusable-entry", report_id="unusable-report")
                    invalid["entry_point"]["line"] = 0
                else:
                    invalid["anchor_id"] = "unusable-anchor"
                    invalid["source_entry_ids"] = ["unusable-entry"]
                    invalid["source_report_ids"] = ["unusable-report"]
                    invalid[name]["line"] = 0
                expected = evaluate(ground_truth, [], 5)
                actual = evaluate(ground_truth + [invalid], [], 5)
                self.assertEqual(actual["recall"], expected["recall"])

    def test_normalized_paths_line_ranges_and_tolerance_are_preserved(self) -> None:
        finding = deepcopy(self.entries[0])
        finding["entry_point"] = {"file": "./src\\handler.py", "line": "14-15"}
        finding["critical_operation"] = {"file": "src//storage.py", "line": 95}
        self.assertEqual(pair.evaluate(self.entries, [finding], 5)["recall"]["entry_level"]["numerator"], 1)
        self.assertEqual(pair.evaluate(self.entries, [finding], 4)["recall"]["entry_level"]["numerator"], 0)


class EvaluatorCliTests(unittest.TestCase):
    CLIS = [
        ("evaluate.py", "--entries", "entries.jsonl"),
        ("evaluate_entry_points.py", "--ground-truth", "entry_points.jsonl"),
        ("evaluate_critical_operations.py", "--ground-truth", "critical_operations.jsonl"),
    ]

    def run_cli(self, script: str, findings: Path, cwd: Path, *args: str) -> dict:
        output = cwd / "result.json"
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "examples" / script), str(findings),
             *args, "--json-out", str(output)],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ground-truth file:", result.stdout)
        return json.loads(output.read_text(encoding="utf-8"))

    def test_default_cli_scores_this_checkout_from_another_working_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vulngym evaluator ") as temp:
            cwd = Path(temp)
            for script, _, filename in self.CLIS:
                with self.subTest(script=script):
                    source = ROOT / "data" / filename
                    rows = pair.load_jsonl(source)
                    result = self.run_cli(script, source, cwd)
                    self.assertEqual(result["ground_truth"]["path"], str(source.resolve()))
                    self.assertEqual(result["ground_truth"]["rows"], len(rows))
                    self.assertTrue(all(m["value"] == 1.0 for m in result["recall"].values()))

    def test_custom_ground_truth_replaces_scope_and_findings_do_not_narrow_it(self) -> None:
        fixtures = [fixture_entries(), *fixture_anchors()]
        with tempfile.TemporaryDirectory(prefix="vulngym evaluator ") as temp:
            cwd = Path(temp)
            findings = cwd / "empty.jsonl"
            findings.write_text("", encoding="utf-8")
            for (script, flag, _), rows in zip(self.CLIS, fixtures):
                with self.subTest(script=script):
                    source = cwd / "custom.jsonl"
                    source.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
                    result = self.run_cli(script, findings, cwd, flag, source.name)
                    self.assertEqual(result["ground_truth"]["path"], str(source.resolve()))
                    self.assertEqual(result["ground_truth"]["rows"], len(rows))
                    self.assertEqual(result["ground_truth"]["repositories"], 1)
                    self.assertEqual(result["ground_truth"]["snapshots"], 1)
                    self.assertTrue(all(m["denominator"] > 0 and m["numerator"] == 0
                                        for m in result["recall"].values()))

    def test_jsonl_loader_rejects_non_object_with_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "invalid.jsonl"
            source.write_text("\n[]\n", encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, r":2: each JSONL row must be an object"):
                pair.load_jsonl(source)


class ConverterCompatibilityTests(unittest.TestCase):
    def test_multiple_candidates_require_explicit_pair(self) -> None:
        candidate = lambda kind, index: {
            "candidate_id": f"{kind}-{index}", "conversion_method": "direct",
            "endpoint": {"file": f"src/{kind}.py", "line": index * 10},
        }
        row = {
            "conversion_row_id": "conversion-1", "finding_id": "finding-1",
            "repo_url": REPO, "commit": COMMIT, "conversion_status": "converted",
            "candidate_entry_points": [candidate("ep", 1), candidate("ep", 2)],
            "candidate_critical_operations": [candidate("co", 1), candidate("co", 2)],
        }
        pairs, eps, cos, skipped = converter.convert_rows([row], strict=True)
        self.assertEqual((len(pairs), len(eps), len(cos)), (0, 2, 2))
        self.assertEqual(skipped[0]["reason"], "ambiguous_or_incomplete_pairing")
        row["candidate_pairs"] = [{
            "pair_id": "pair-1", "entry_point_candidate_id": "ep-1",
            "critical_operation_candidate_id": "co-2",
        }]
        pairs, eps, cos, skipped = converter.convert_rows([row], strict=True)
        self.assertEqual((len(pairs), len(eps), len(cos), len(skipped)), (1, 2, 2, 0))
        self.assertEqual(pairs[0]["entry_point"]["line"], 10)
        self.assertEqual(pairs[0]["critical_operation"]["line"], 20)


if __name__ == "__main__":
    unittest.main()
