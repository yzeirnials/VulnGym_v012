# Changelog

All notable changes to VulnGym are documented here.
Earlier release sections are retained as historical source records; their
counts and scope do not describe the current six-batch dataset.

## Six-batch subset — 2026-09-19

- Retained `openclaw-01` and `mixed-01` through `mixed-05`: **274 → 156
  entries**, **137 → 61 reports**, **236 → 136 entry-point anchors**, and
  **241 → 137 critical-operation anchors** across 55 snapshots / 23 repositories.
- Preserved original IDs, vulnerable commits, locations, and annotations;
  recomputed retained report membership and anchor source metadata.
- Filtered the existing explanatory `entries_desc.jsonl` to the same 156 entries.
- Added a standalone batch manifest, dataset identity, reproducible subset
  generation, source-size measurement policy, and language/category/size and
  GHSA/CVE statistics. Identifier associations total 62 distinct GHSA IDs and
  48 distinct CVE IDs; these are not independent-vulnerability counts.
- Updated both READMEs, schema documentation, and loader examples. Evaluators
  now report the actual GT file and scope while preserving matching behavior.
- Historical cleaning/build scripts default to read-only checks. Compatibility
  and data-integrity tests cover generation, source association, and evaluators.

Current authorities: `data/dataset.json`, `data/batch_manifest.jsonl`, and
`records/dataset_statistics.json`. This change does not add tool baseline results.

## [0.1.2-cleaned-verify1] — 2026-06-08

Experiment fork cleanup — retain only human-audited VulnGym entries for formal
benchmark runs.

### Changed
- Filtered `data/entries.jsonl` from **408 → 274**
  rows by keeping only `verify = 1`.
- Filtered `data/reports.jsonl` from **184 → 137**
  rows by removing reports with no retained verified entries.
- Recomputed `entry_ids` and `num_entries` for **29**
  originally partially verified reports.

### Records
- `records/cleaned_verify1_20260608.md`
- `records/cleaned_verify1_20260608_summary.json`

### Added
- Endpoint-level ground-truth views: `data/entry_points.jsonl` (236 anchors) and `data/critical_operations.jsonl` (241 anchors).
- Endpoint-level recall evaluators: `examples/evaluate_entry_points.py` and `examples/evaluate_critical_operations.py`.
- Endpoint generation records under `records/endpoint_ground_truth_20260608.*`.
- Conversion-table schema, example, and exporter for turning raw tool findings into the three evaluator input formats.
- Conversion schema record: `records/conversion_table_schema_20260608.md`.

## [0.1.2] — 2026-05-31

Data refresh — significant expansion of human-audited coverage and annotation refinements.

### Changed
- Human-audited entries grew from **113 → 274 / 408** (67.2 %),
  covering **137 / 184** advisories (74.5 %).
- Refined `entry_point`, `critical_operation`, and `trace` annotations
  on **80** entries for improved accuracy.

### Stats
- reports: **184** (unchanged)
- entries: **408** (unchanged)
- human-audited entries (verify = 1): **274** (was 113)
- human-audited advisories (≥ 1 verified entry): **137** (was 61)

## [0.1.1] — 2026-05-15

Data refresh — adds a human-audit flag and additional human-verified entries.

### Added
- `verify` field on every row in `data/entries.jsonl` (`int`, `0` or `1`):
  `1` marks entries that have been reviewed and confirmed by a human
  annotator (high-confidence ground truth); `0` marks automatically
  annotated entries that have not yet been human-confirmed.
- **113 / 408** entries (≈ 27.7 %) are now flagged `verify = 1`,
  covering **61 / 184** advisories (≈ 33.2 %; **50** advisories have all
  of their entries verified, **11** are partially verified).

### Changed
- Refined values of selected `entry_point`, `critical_operation`, `trace`,
  and other annotation fields in `data/entries.jsonl`. Row counts and the
  `report_id` ↔ `entry_id` join structure are unchanged.
- `SCHEMA.md` now documents `verify`; `human_confirmed` is removed from
  the "intentionally omitted internal fields" invariant since the audit
  status is exposed publicly via `verify`.

### Stats
- reports: **184** (unchanged)
- entries: **408** (unchanged)
- human-audited entries (verify = 1): **113**
- human-audited advisories (≥ 1 verified entry): **61**

## [0.1.0] — 2026-05-xx

Initial open-source release.

### Added
- `data/reports.jsonl` — 184 GitHub Advisories (report-level aggregates).
- `data/entries.jsonl` — 408 per-entry-point records with
  `entry_point` / `critical_operation` / `trace` annotations.
- `SCHEMA.md` — full field reference and invariants.
- `examples/load_dataset.py` — stdlib / pandas / HuggingFace `datasets`
  loaders.
- `examples/evaluate.py` — coverage / recall evaluator.
- `examples/example_result.jsonl` — illustrative tool-findings submission.
- CC-BY-4.0 license.

### Stats
- reports: **184**
- entries: **408**
- projects: 38
- repositories: 23
