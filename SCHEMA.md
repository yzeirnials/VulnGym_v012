# SCHEMA.md — VulnGym six-batch data format

The dataset retains the v0.1.2 annotation format and ships four primary
ground-truth tables plus two supporting JSONL files under `data/`. Every line is
a single self-contained JSON object (no trailing comma, `\n`-terminated,
UTF-8). Field order in each row is stable (sorted alphabetically) so
`diff` is useful across releases.

- `data/reports.jsonl` — 61 rows, one per retained report-level advisory record.
- `data/entries.jsonl` — 156 rows, one per retained human-verified pair-level entry.
- `data/entry_points.jsonl` — 136 rows, one per deduplicated reachable entry-point anchor.
- `data/critical_operations.jsonl` — 137 rows, one per deduplicated critical-operation anchor.
- `data/entries_desc.jsonl` — 156 rows, the same entries with preserved explanatory `desc` annotations.
- `data/batch_manifest.jsonl` — 55 rows, one per retained `(repo_url, commit)` snapshot.
- `data/dataset.json` — one JSON object containing identity, source commits, scope, counts, and file bindings.

Join key: `entries.report_id == reports.report_id`.

This subset contains only `openclaw-01` and `mixed-01` through `mixed-05`
from the previously cleaned, 274-entry source. All entries have `verify == 1`.
Reports without retained entries are removed; `entry_ids` and `num_entries`
refer only to retained members. Original annotations and IDs remain unchanged.
Entry and anchor numbering may have gaps after selection.

## Supporting files and dataset scope

`entries_desc.jsonl` uses the same entry IDs and annotation content as
`entries.jsonl`, with an optional explanatory `desc` string added to endpoint
and trace objects. Removing these `desc` fields reproduces the corresponding
primary entry. These explanations are ground-truth annotations and are not
additional entries, findings, or independently validated vulnerabilities.

Each `batch_manifest.jsonl` row has `batch_id`, `repo_url`, `commit`, and
`entry_ids`. Every retained entry belongs to exactly one manifest row, and
each snapshot belongs to one batch. The manifest defines membership rather
than inferring it from project names or entry-number ranges.

`dataset.json` records `dataset_id`, `schema_version`, `source_repository`,
`source_dataset_commit`, `descriptions_source_commit`, `selection_manifest`,
`selected_batch_ids`, `selection_policy`, `counts`, `files_sha256`, and
`generator`. The source dataset commit is
`90002144d4a8b3654fb1bf68052889b9c2de44aa`; the descriptions source commit is
`4c4ac5659329008d9ea44ac5ec7855eae6909c2e`. File hashes bind the six JSONL
inputs; the metadata file does not hash itself.

The current complete scope is 6 batches, 55 snapshots, and 23 repositories.
`python3 scripts/subset_dataset.py --validate` checks membership, retained
source references, and dataset bindings. A generated single-batch subset has
its own metadata and counts rather than inheriting these full-scope totals.

---


## Endpoint-level rows

`data/entry_points.jsonl` and `data/critical_operations.jsonl` are derived
views over `data/entries.jsonl`.

Both files use one JSON object per deduplicated anchor. Each row contains:

| field | type | description |
|---|---|---|
| `anchor_id` | `string` | Original stable id, e.g. `entry-point-00001`; selection preserves IDs and permits gaps. |
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

Anchors are deduplicated separately by role using
`(repo_url, commit, file, str(line))`; code text does not enter this key.
After selection, `source_entry_ids`, `source_report_ids`, and all aggregate
metadata contain only retained associations. Counts of source entries must
not be confused with counts of distinct anchors.

## Derived statistics and evaluator scope

`records/dataset_statistics.json` and its CSV tables summarize the retained
data. GHSA/CVE counts union `vuln_ids`, `report_id`, and `source_link` with
case-insensitive identifier matching and uppercase deduplication. Anchor
identifier sets are derived from associated retained entries and reports.
The complete dataset has 61 reports, 62 distinct GHSA IDs, and 48 distinct
CVE IDs; a report can carry multiple identifiers or no CVE. These are not
independent-vulnerability counts and do not alter the annotation fields.

Language, source size, and category summaries follow the methodology embedded
in the statistics JSON and `scripts/source_size_policy.json`. Original
bilingual category labels are preserved.

The evaluator CLIs add a `ground_truth` object to JSON reports with the actual
file `path`, raw `rows`, distinct `repositories`, distinct `snapshots`, and
`denominator_policy`. Existing `config`, `totals`, `recall`, and match-detail
fields retain their semantics. All usable GT rows in the selected file
contribute to the denominator; findings do not restrict scope. Pair evaluation
uses `--entries`; single-anchor evaluation uses `--ground-truth`. Default
paths resolve against this checkout, independently of the working directory.

---


## Tool-output conversion table

Raw tool outputs should be normalized into a conversion table before they are
passed to the evaluators. This intermediate table records both successful and
failed mappings from tool-specific findings into VulnGym's evaluator terms.
The machine-readable schema is:

```text
examples/conversion_table.schema.json
```

The example table is:

```text
examples/example_conversion_table.jsonl
```

One conversion-table row corresponds to one original tool finding.

| field | type | required | description |
|---|---|---|---|
| `conversion_row_id` | `string` | yes | Stable id for the conversion-table row. |
| `finding_id` | `string` | yes | Original tool finding id. |
| `tool` | `string` | no | Tool name. |
| `model` | `string` | no | Model name or backend label used by the tool. |
| `run_id` | `string` | no | Experiment run id. |
| `repo_url` | `string` | yes | Repository URL to carry into evaluator input. |
| `commit` | `string` | yes | Vulnerable commit SHA to carry into evaluator input. |
| `source_artifact` | `object` | yes | Pointer to the raw finding evidence, e.g. `{path, locator, format, sha256}`. Do not store secrets. |
| `candidate_entry_points` | `object[]` | yes | Candidate reachable-entry locations derived from the finding. |
| `candidate_critical_operations` | `object[]` | yes | Candidate core-defect locations derived from the finding. |
| `candidate_pairs` | `object[]` | no | Explicit pair bindings between entry-point and critical-operation candidate ids. |
| `candidate_trace` | `object[]` | no | Optional trace evidence retained for review; current evaluators ignore it. |
| `conversion_status` | `string` | yes | `converted`, `partially-converted`, or `not-converted`. |
| `rationale` | `string` | yes | Short explanation of the conversion decision. |
| `source_categories` | `string[]` | no | Tool-native category labels. |
| `vuln_category_l1_values` / `vuln_category_l2_values` | `string[]` | no | Category labels carried forward for later analysis. |
| `confidence` | `number|string|null` | no | Optional tool or reviewer confidence. |
| `review_notes` | `string|null` | no | Optional reviewer notes. |

Each candidate endpoint has:

| field | type | required | description |
|---|---|---|---|
| `candidate_id` | `string` | yes | Stable id within the row, e.g. `ep-1` or `co-1`. |
| `endpoint` | `object|null` | no | `{file, line, code?}` when a usable location exists; `null` for retained failed attempts. |
| `conversion_method` | `string` | yes | `direct`, `source-resolved`, `semantic-assisted`, or `not-converted`. |
| `rationale` | `string` | no | Candidate-specific conversion explanation. |
| `confidence` | `number|string|null` | no | Optional candidate-level confidence. |

Conversion methods:

- `direct` — the tool already reports a usable repository-relative file and
  line span for the endpoint.
- `source-resolved` — the tool reports a symbol, snippet, URL, stack frame, or
  other source clue that is resolved against the vulnerable commit.
- `semantic-assisted` — a reviewer or model maps descriptive language to a
  concrete endpoint by understanding the vulnerability semantics.
- `not-converted` — no evaluator-usable endpoint was recovered.

Export conversion-table rows with:

```bash
python3 examples/conversion_table_to_eval_inputs.py examples/example_conversion_table.jsonl --out-dir /tmp/vulngym_eval_inputs
```

The exporter writes:

```text
pair_findings.jsonl
entry_point_findings.jsonl
critical_operation_findings.jsonl
conversion_manifest.json
conversion_skipped.jsonl
```

Pair-level output is intentionally conservative. Explicit `candidate_pairs` are
honored. If a row has no `candidate_pairs`, it is auto-paired only when it has
exactly one usable `entry_point` candidate and exactly one usable
`critical_operation` candidate. Multi-candidate rows without explicit pairs are
not expanded into a Cartesian product; they are recorded in
`conversion_skipped.jsonl`.

---

## `entries.jsonl` row

| field | type | required | description |
|---|---|---|---|
| `entry_id` | `string` | ✅ | Stable per-entry id. Format: `entry-{id:05d}`, e.g. `entry-00057`. |
| `report_id` | `string` | ✅ | GHSA id (upper-case) derived from `source_link`, e.g. `GHSA-W7XJ-8FX7-WFCH`. |
| `source_link` | `string` | ✅ | Canonical advisory URL, `https://github.com/advisories/GHSA-…`. |
| `vuln_ids` | `string[]` | ✅ | All known identifiers for this advisory. `CVE-*` first, then `GHSA-*`, upper-cased, deduped. May be empty. |
| `origin` | `string` | ✅ | Constant `"GitHub Advisory Database (reviewed)"` in this release. |
| `project` | `string` | ✅ | Short project name (e.g. `open-webui`). |
| `repo_url` | `string` | ✅ | Source repository, starts with `https://github.com/`. |
| `commit` | `string` | ✅ | Vulnerable commit SHA — 40 lowercase hex chars. Consumers should `git checkout` this commit before analysis. |
| `vuln_title` | `string` | ✅ | Per-entry title. Annotators sometimes append ` - <filename>` to disambiguate entries of the same advisory; the report-level `vuln_title` has this suffix stripped. |
| `vuln_category_l1` | `string` | ✅ | Coarse category. **Bilingual** — e.g. `XSS`, `权限绕过`, `代码注入`. |
| `vuln_category_l2` | `string` | ✅ | Sub-category. Bilingual. |
| `entry_point` | `object` | ✅ | Reachable entry point — `{file, line, code}`. See below. |
| `critical_operation` | `object` | ✅ | Critical operation (core defect location) — `{file, line, code}`. See below. |
| `trace` | `object[]` | ✅ | Ordered taint-flow steps. Each item is `{file, line, code}`. May be empty. |
| `verify` | `int` | ✅ | Human-audit flag. `1` = the entry has been reviewed and confirmed by a human annotator (high-confidence ground truth); `0` = automatically annotated, not yet human-confirmed. Added in v0.1.1. |

### `entry_point` / `critical_operation` / `trace[*]` object

| field | type | description |
|---|---|---|
| `file` | `string` | Repository-relative path at the vulnerable commit. |
| `line` | `int` \| `string` | Line location, **1-based**. Either a single positive integer (e.g. `97`) or a range string `"start-end"` where `start` and `end` are integers with `1 ≤ start ≤ end` (e.g. `"348-352"`). Always `≥ 1` — the value `0` is **not** permitted. Single-line upstream string values are coerced to `int`; range values stay strings. |
| `code` | `string` | Verbatim code snippet. May span multiple lines via `\n` and may contain 中文 inline comments when the annotator added them. |

`line` has two valid forms:

- **single line** — an `int` `≥ 1`, e.g. `"line": 97`.
- **line range** — a `string` `"start-end"` with `1 ≤ start ≤ end`, e.g.
  `"line": "348-352"` (a single-line span may also be written this way, e.g.
  `"line": "97-97"`).

A consumer can normalize either form to a `(start, end)` pair: an `int` `n`
maps to `(n, n)`; a string `"a-b"` splits on `-` to `(int(a), int(b))`.

### Example

```json
{
  "entry_id": "entry-00057",
  "report_id": "GHSA-W7XJ-8FX7-WFCH",
  "source_link": "https://github.com/advisories/GHSA-w7xj-8fx7-wfch",
  "vuln_ids": ["CVE-2025-64495", "GHSA-W7XJ-8FX7-WFCH"],
  "origin": "GitHub Advisory Database (reviewed)",
  "project": "open-webui",
  "repo_url": "https://github.com/open-webui/open-webui",
  "commit": "9942de8011d4b5a141ac507c974c061c0cdad59a",
  "vuln_title": "Open WebUI Stored DOM XSS via Prompt Insertion Rich Text Feature",
  "vuln_category_l1": "XSS",
  "vuln_category_l2": "Stored XSS",
  "entry_point": {
    "file": "src/lib/components/chat/MessageInput/CommandSuggestionList.svelte",
    "line": 97,
    "code": "insertTextHandler(data.content);"
  },
  "critical_operation": {
    "file": "src/lib/components/common/RichTextInput.svelte",
    "line": 348,
    "code": "tempDiv.innerHTML = htmlContent;"
  },
  "trace": [
    {"file": "…", "line": "42-45", "code": "…"}
  ],
  "verify": 1
}
```

---

## `reports.jsonl` row

Aggregates one or more entries that share a `source_link`. At original
upstream export, the repeated
fields (`project`, `repo_url`, `commit`, `vuln_title`, `source_link`,
`origin`, `vuln_ids`) are the canonical value for the advisory, computed as
follows:

- `vuln_title` — stripped of any trailing `" - <filename.ext>"` disambiguator
  added per entry.
- scalar fields — majority value across entries (ties broken by smallest
  `entry_id`). In practice every advisory in v0.1.0 is internally
  consistent; the export script would log a warning if it were not.
- `vuln_ids` — union of the per-entry lists, re-normalized.

The six-batch selection preserves these original report metadata fields and
recomputes only `entry_ids` and `num_entries` for retained members.

| field | type | description |
|---|---|---|
| `report_id` | `string` | Same GHSA id as the entries it aggregates. |
| `source_link` | `string` | Advisory URL. |
| `vuln_ids` | `string[]` | Union across entries, normalized. |
| `origin` | `string` | `"GitHub Advisory Database (reviewed)"`. |
| `project` | `string` | |
| `repo_url` | `string` | |
| `commit` | `string` | |
| `vuln_title` | `string` | With `- filename` suffix stripped. |
| `num_entries` | `int` | Length of `entry_ids`. |
| `entry_ids` | `string[]` | All `entry_id`s that belong to this report, sorted ascending. |

### Example

```json
{
  "report_id": "GHSA-W7XJ-8FX7-WFCH",
  "source_link": "https://github.com/advisories/GHSA-w7xj-8fx7-wfch",
  "vuln_ids": ["CVE-2025-64495", "GHSA-W7XJ-8FX7-WFCH"],
  "origin": "GitHub Advisory Database (reviewed)",
  "project": "open-webui",
  "repo_url": "https://github.com/open-webui/open-webui",
  "commit": "9942de8011d4b5a141ac507c974c061c0cdad59a",
  "vuln_title": "Open WebUI Stored DOM XSS via Prompt Insertion Rich Text Feature",
  "num_entries": 1,
  "entry_ids": ["entry-00057"]
}
```

---

## Invariants (enforced pre-release)

Every release must satisfy these before tagging:

1. Row counts match `data/dataset.json` and the current README scope;
   historical changelog sections keep their original counts.
2. Every `entry.report_id` appears in `reports.jsonl` and vice versa.
3. `report.entry_ids` equals the sorted set of `entry_id`s grouped by
   `report_id` in `entries.jsonl`.
4. `origin` is the constant `"GitHub Advisory Database (reviewed)"` on every
   row.
5. `commit` is 40 lowercase hex chars; `repo_url` starts with
   `https://github.com/`.
6. `source_link` contains `github.com/advisories/` and its embedded GHSA id
   equals `report_id`.
7. In the primary `entries.jsonl`, `entry_point`, `critical_operation`, and
   every `trace[i]` have exactly the keys `{file, line, code}`. The supporting
   `entries_desc.jsonl` permits an additional `desc` string. `line` is either a **positive integer** (`≥ 1`) or a
   **range string** `"a-b"` where `a` and `b` are integers with `1 ≤ a ≤ b`.
   The value `0` is **not** permitted.
8. No row contains any of the internal fields we intentionally omit
   (`description`, `human_remark`, `pipeline_id`, `annotated_by`,
   `is_active`, `created_at`, `generality`,
   `detection_type`, `ground_truth`, `taint_source`, `taint_sink`,
   `vuln_category_l3`).
9. Every retained entry has `verify == 1`. The underlying upstream field
   retains its integer `0` / `1` semantics.
10. Manifest entry IDs equal the retained entry-ID set without duplicate
    assignments; report and anchor source references remain inside that set.
11. Both anchor tables cover every retained entry, preserve source anchor
    IDs and locations, and contain no duplicate role/location keys.
12. `entries_desc.jsonl` has exactly the same entry IDs and underlying
    annotation content as `entries.jsonl` after removing `desc` fields.

---

## Forward compatibility

- New **optional** top-level fields may be added in minor versions; existing
  fields will not be removed or re-typed without a major version bump.
- `verify` was introduced in v0.1.1 as an integer flag (`0` / `1`); it may be
  generalized to a richer status code (e.g. multiple audit levels) in a
  future minor version while keeping backward-compatible truthy semantics
  for `1`.
- `line` (in `entry_point` / `critical_operation` / `trace[*]`) was widened
  from a plain non-negative `int` to `int | "start-end"` (positive
  integer **or** range string), and the `0`-means-unknown sentinel was
  retired — `line` is now always `≥ 1`. Consumers should accept both the `int`
  and the range-string form.
- An English translation of `vuln_category_l1/l2` is a likely future
  addition as `vuln_category_l1_en` / `_l2_en`.
- The JSONL ordering (entries by `entry_id` asc, reports by `report_id`
  asc) is part of the contract — consumers can depend on it.
