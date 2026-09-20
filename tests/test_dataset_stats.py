"""Statistics tests covering identifier aliases, shared anchors and source scope."""

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "dataset_stats.py"
SPEC = importlib.util.spec_from_file_location("dataset_stats", SCRIPT)
stats = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stats)


def fixture():
    location = {"repo_url": "https://github.com/example/project", "commit": "a" * 40}
    report = {"report_id": "GHSA-AAAA-BBBB-CCCC", "vuln_ids": ["CVE-2026-12345", "GHSA-DDDD-EEEE-FFFF"],
              "source_link": "https://github.com/advisories/ghsa-aaaa-bbbb-cccc",
              "entry_ids": ["e1", "e2"], "num_entries": 2, **location}
    entries = [{"entry_id": key, "report_id": report["report_id"], "vuln_ids": [],
                "vuln_category_l1": "raw label", "vuln_category_l2": "raw subtype", **location} for key in ("e1", "e2")]
    anchor = {"anchor_id": "a1", "source_entry_ids": ["e1", "e2"], **location}
    data = {"entries": entries, "reports": [report], "entry_points": [copy.deepcopy(anchor)],
            "critical_operations": [copy.deepcopy(anchor)],
            "batch_manifest": [{"batch_id": "batch-01", "entry_ids": ["e1", "e2"], **location}]}
    languages = {language: {"code": 10, "files": 1, "bytes": 100, "blank": 2, "comment": 3} for language in ("Python", "JavaScript")}
    sources = {"schema_version": 1, "cloc_version": "2.10", "policy": {},
               "snapshots": [{"sloc": 20, "source_files": 2, "source_bytes": 200, "languages": languages, **location}]}
    return data, sources


class DatasetStatisticsTests(unittest.TestCase):
    def test_missing_declared_ids_aliases_and_shared_anchors(self):
        data, sources = fixture()
        summary, tables = stats.build_statistics(data, sources)
        self.assertEqual(summary["counts"]["ghsa"], 2)
        self.assertEqual(summary["counts"]["cve"], 1)
        self.assertEqual(summary["counts"]["entries"], 2)
        self.assertEqual(summary["counts"]["entry_points"], 1)
        self.assertEqual(summary["counts"]["critical_operations"], 1)
        for row in summary["granularities"]:
            self.assertEqual((row["ghsa"], row["cve"]), (2, 1))
        anchor_row = next(row for row in tables["identifier_associations"] if row["granularity"] == "entry_points")
        self.assertEqual(anchor_row["source_entry_ids"], ["e1", "e2"])
        categories = [row for row in summary["categories"] if row["batch_id"] == "ALL" and row["level"] == "l1"]
        self.assertEqual({row["unit"]: row["count"] for row in categories}, {"entry": 2, "report": 1})
        for row in summary["categories"]:
            self.assertEqual(row["denominator"], 2 if row["unit"] == "entry" else 1)
            self.assertEqual(row["percentage"], 100)

    def test_language_tie_break_and_entry_weighting(self):
        data, sources = fixture()
        summary, tables = stats.build_statistics(data, sources)
        self.assertEqual(tables["snapshot_statistics"][0]["primary_language"], "JavaScript")
        languages = {row["language"]: row for row in summary["languages"]}
        self.assertEqual(languages["JavaScript"]["primary_entry_count"], 2)
        self.assertEqual(languages["Python"]["primary_entry_count"], 0)
        self.assertEqual(languages["Python"]["snapshot_count"], 1)
        self.assertEqual(languages["JavaScript"]["sloc_percentage"], 50)
        self.assertEqual(languages["Python"]["sloc_percentage"], 50)
        self.assertEqual(languages["JavaScript"]["primary_entry_percentage"], 100)
        self.assertEqual(languages["Python"]["primary_entry_percentage"], 0)

    def test_identifier_extraction_ignores_prose(self):
        result = stats.identifiers({"report_id": "ghsa-aaaa-bbbb-cccc", "vuln_title": "CVE-2026-99999"})
        self.assertEqual(result, {"ghsa": ["GHSA-AAAA-BBBB-CCCC"], "cve": []})

    def test_source_scope_mismatch_is_rejected(self):
        data, sources = fixture()
        sources["snapshots"][0]["commit"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "cover exactly"):
            stats.build_statistics(data, sources)

    def test_source_language_totals_are_checked(self):
        data, sources = fixture()
        sources["snapshots"][0]["sloc"] = 21
        with self.assertRaisesRegex(ValueError, "do not match sloc"):
            stats.build_statistics(data, sources)

    def test_unknown_anchor_entry_is_rejected(self):
        data, sources = fixture()
        data["entry_points"][0]["source_entry_ids"].append("excluded-entry")
        with self.assertRaisesRegex(ValueError, "Unknown source entry"):
            stats.build_statistics(data, sources)

    def test_report_snapshot_mismatch_is_rejected(self):
        for field, changed in (("repo_url", "https://github.com/other/project"), ("commit", "b" * 40)):
            with self.subTest(field=field):
                data, sources = fixture()
                data["reports"][0][field] = changed
                with self.assertRaisesRegex(ValueError, "Report/source snapshot mismatch"):
                    stats.build_statistics(data, sources)

    def test_csv_has_lf_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "statistics.csv"
            stats.write_csv(output, [{"record": "example", "ids": ["GHSA-AAAA-BBBB-CCCC"]}])
            content = output.read_bytes()
            self.assertNotIn(b"\r", content)
            self.assertEqual(content.count(b"\n"), 2)

    def test_readme_markers_preserve_surrounding_multilingual_content(self):
        before = "# 标题 / Introduction\r\n\r\n" + stats.README_START
        after = stats.README_END + "\r\n\r\nExisting 日本語 / Français content.\r\n"
        original = before + "\r\nOld tables\r\n" + after
        updated = stats.replace_overview(original, "New tables")
        self.assertEqual(updated, before + "\r\n\nNew tables\n\n" + after)
        self.assertEqual(stats.replace_overview(updated, "New tables"), updated)

    def test_missing_duplicate_and_reversed_readme_markers_are_rejected(self):
        for original in ("No markers", stats.README_START + "\nOnly start",
                         stats.README_END + "\n" + stats.README_START,
                         stats.README_START + "\n" + stats.README_START + "\n" + stats.README_END):
            with self.subTest(original=original):
                with self.assertRaises(ValueError):
                    stats.replace_overview(original, "Replacement")

    def test_readme_preflight_does_not_change_existing_documents_on_error(self):
        data, sources = fixture()
        summary, _ = stats.build_statistics(data, sources)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = (stats.README_START + "\nKeep this body\n" + stats.README_END).encode()
            (root / "README.md").write_bytes(original)
            (root / "README_zh.md").write_bytes(b"No statistics markers")
            with self.assertRaises(ValueError):
                stats.prepare_readme_updates(root, summary)
            self.assertEqual((root / "README.md").read_bytes(), original)
            self.assertEqual((root / "README_zh.md").read_bytes(), b"No statistics markers")

    def test_rendered_overview_counts_and_raw_categories(self):
        data, sources = fixture()
        data["entries"][0]["vuln_category_l1"] = "反序列化漏洞"
        data["entries"][1]["vuln_category_l1"] = "反序列化"
        summary, _ = stats.build_statistics(data, sources)
        english = stats.render_overview(summary)
        chinese = stats.render_overview(summary, zh=True)
        self.assertIn("| JavaScript | 10 | 50.00% | 1 | 2 |", english)
        self.assertIn("| Python | 10 | 50.00% | 1 | 0 |", english)
        self.assertIn("| 20 | 20 | 20 | 20 | 20 | 20 |", english)
        self.assertIn("| 反序列化漏洞 | Deserialization vulnerability | 1 | 50.00% | 1 | 100.00% |", english)
        self.assertIn("| 反序列化 | Deserialization | 1 | 50.00% | 1 | 100.00% |", english)
        self.assertIn("| 反序列化漏洞 | 1 | 50.00% | 1 | 100.00% |", chinese)
        self.assertIn("records/category_statistics.csv", english)

    def test_inclusive_percentiles(self):
        self.assertEqual(stats.percentile([10, 20, 30, 40], .25), 17.5)
        self.assertEqual(stats.percentile([10], .75), 10)
        self.assertEqual(stats.size_summary([10, 20, 30, 40])["median"], 25)

    def test_conflicting_report_labels_remain_explicit_memberships(self):
        data, sources = fixture()
        data["entries"][1]["vuln_category_l1"] = "other label"
        summary, _ = stats.build_statistics(data, sources)
        rows = [row for row in summary["categories"] if row["batch_id"] == "ALL" and row["level"] == "l1" and row["unit"] == "report"]
        self.assertEqual({row["category"]: row["count"] for row in rows}, {"raw label": 1, "other label": 1})
        self.assertEqual([row["denominator"] for row in rows], [1, 1])
        self.assertEqual([row["percentage"] for row in rows], [100, 100])

    def test_multiple_revisions_are_one_repository_with_a_size_range(self):
        data, sources = fixture()
        extra_data, extra_sources = fixture()
        for row in extra_data["entries"]:
            row["commit"] = "b" * 40
            row["entry_id"] = {"e1": "e3", "e2": "e4"}[row["entry_id"]]
            row["report_id"] = "GHSA-GGGG-HHHH-JJJJ"
        report = extra_data["reports"][0]
        report.update(commit="b" * 40, report_id="GHSA-GGGG-HHHH-JJJJ", entry_ids=["e3", "e4"])
        for granularity in ("entry_points", "critical_operations"):
            extra_data[granularity][0].update(commit="b" * 40, anchor_id="a2", source_entry_ids=["e3", "e4"])
        extra_data["batch_manifest"][0].update(commit="b" * 40, entry_ids=["e3", "e4"], batch_id="batch-02")
        measured = extra_sources["snapshots"][0]
        measured.update(commit="b" * 40, sloc=60)
        measured["languages"]["JavaScript"]["code"] = 40
        measured["languages"]["Python"]["code"] = 20
        for name in data:
            data[name].extend(extra_data[name])
        sources["snapshots"].extend(extra_sources["snapshots"])
        summary, _ = stats.build_statistics(data, sources)
        self.assertEqual(summary["counts"]["repositories"], 1)
        self.assertEqual(summary["counts"]["snapshots"], 2)
        self.assertEqual(summary["project_size"]["sloc"],
                         {"count": 2, "min": 20, "p25": 30, "median": 40, "mean": 40, "p75": 50, "max": 60})
        self.assertEqual(summary["repositories"][0]["sloc_min"], 20)
        self.assertEqual(summary["repositories"][0]["sloc_max"], 60)
        for row in summary["categories"]:
            expected_denominator = {("ALL", "entry"): 4, ("ALL", "report"): 2,
                                    ("batch-01", "entry"): 2, ("batch-01", "report"): 1,
                                    ("batch-02", "entry"): 2, ("batch-02", "report"): 1}
            self.assertEqual(row["denominator"], expected_denominator[row["batch_id"], row["unit"]])


if __name__ == "__main__":
    unittest.main()
