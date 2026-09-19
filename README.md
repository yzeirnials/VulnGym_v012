# VulnGym — six-batch dataset

[中文](README_zh.md) · [Schema](SCHEMA.md) · [Dataset identity](data/dataset.json)

This fork of [Tencent VulnGym](https://github.com/Tencent/VulnGym) retains
**openclaw-01 and mixed-01 through mixed-05** from the human-verified v0.1.2
dataset. Each entry identifies a vulnerable repository commit, a reachable
entry point, a critical operation, and an annotated trace.

The final dataset contains **156 entries, 61 reports, 136 entry-point anchors,
and 137 critical-operation anchors**, across **55 source snapshots and
23 repositories**. All retained entries have `verify == 1`.

## Dataset and identifiers

An **entry** is an annotated entry-point/critical-operation pair. An
**entry-point anchor** or **critical-operation anchor** is a unique
`(repo_url, commit, file, line)` location for that role; several entries can
share an anchor. A **snapshot** is one `(repo_url, commit)` pair. Original
entry, report, and anchor IDs are preserved and may have gaps.

| Batch | Snapshots | Entries | Reports | Entry points | Critical operations | GHSA IDs | CVE IDs |
|---|---:|---:|---:|---:|---:|---:|---:|
| openclaw-01 | 6 | 32 | 7 | 18 | 19 | 8 | 4 |
| mixed-01 | 10 | 27 | 11 | 27 | 27 | 11 | 11 |
| mixed-02 | 7 | 21 | 10 | 19 | 19 | 10 | 7 |
| mixed-03 | 9 | 30 | 10 | 27 | 26 | 10 | 6 |
| mixed-04 | 14 | 34 | 14 | 33 | 34 | 14 | 12 |
| mixed-05 | 9 | 12 | 9 | 12 | 12 | 9 | 8 |
| **Total** | **55** | **156** | **61** | **136** | **137** | **62** | **48** |

Across entries, entry-point anchors, and critical-operation anchors, each
granularity is associated with the same **62 distinct GHSA IDs and 48 distinct
CVE IDs**. IDs are extracted from the union of `vuln_ids`, `report_id`, and
`source_link`, normalized to uppercase, and deduplicated. Anchor associations
come from their retained source entries and reports.

Identifier counts are not counts of independent vulnerabilities. Thirteen
reports have no recorded CVE. Report `GHSA-QWMF-95R9-GX9X` also lists
`GHSA-HFF7-CCV5-52F8`, explaining why 61 reports correspond to 62 GHSA IDs.
Some `vuln_ids` lists omit their report's GHSA ID or are empty; counting only
that field would undercount. See [identifier associations](records/identifier_associations.csv)
and [granularity statistics](records/granularity_statistics.csv).

## Language, vulnerability category, and project size

<!-- DATASET_STATISTICS:START -->

All counted languages are shown below; snapshot coverage can overlap.

| Language | SLOC | SLOC share | Snapshot coverage | Primary-language entries |
|---|---:|---:|---:|---:|
| TypeScript | 22,638,058 | 63.62% | 46 | 94 |
| Python | 6,782,456 | 19.06% | 43 | 45 |
| Go | 1,653,170 | 4.65% | 15 | 15 |
| Vuejs Component | 1,376,675 | 3.87% | 12 | 0 |
| JSX | 539,647 | 1.52% | 11 | 0 |
| Java | 523,177 | 1.47% | 5 | 0 |
| Swift | 485,971 | 1.37% | 7 | 0 |
| C++ | 297,655 | 0.84% | 8 | 0 |
| JavaScript | 277,907 | 0.78% | 46 | 0 |
| C/C++ Header | 164,244 | 0.46% | 5 | 0 |
| Svelte | 152,074 | 0.43% | 2 | 2 |
| SCSS | 116,516 | 0.33% | 17 | 0 |
| CSS | 113,104 | 0.32% | 50 | 0 |
| Bourne Shell | 100,491 | 0.28% | 53 | 0 |
| Kotlin | 94,487 | 0.27% | 7 | 0 |
| HTML | 67,332 | 0.19% | 49 | 0 |
| Handlebars | 58,872 | 0.17% | 17 | 0 |
| Jupyter Notebook | 56,907 | 0.16% | 11 | 0 |
| Protocol Buffers | 23,388 | 0.07% | 15 | 0 |
| SQL | 14,878 | 0.04% | 15 | 0 |
| R | 9,824 | 0.03% | 2 | 0 |
| Bourne Again Shell | 8,068 | 0.02% | 16 | 0 |
| Dart | 4,566 | 0.01% | 1 | 0 |
| Jinja Template | 3,945 | 0.01% | 4 | 0 |
| Groovy | 3,708 | 0.01% | 2 | 0 |
| Prisma Schema | 2,760 | 0.01% | 2 | 0 |
| Scala | 1,617 | 0.00% | 2 | 0 |
| Nunjucks | 1,525 | 0.00% | 1 | 0 |
| DOS Batch | 1,325 | 0.00% | 32 | 0 |
| Objective-C | 1,267 | 0.00% | 1 | 0 |
| PowerShell | 1,247 | 0.00% | 7 | 0 |
| LESS | 1,211 | 0.00% | 3 | 0 |
| Rego | 1,039 | 0.00% | 7 | 0 |
| C | 684 | 0.00% | 4 | 0 |
| GraphQL | 568 | 0.00% | 2 | 0 |
| Mako | 502 | 0.00% | 12 | 0 |
| ANTLR Grammar | 322 | 0.00% | 2 | 0 |
| Ruby | 224 | 0.00% | 2 | 0 |
| XSLT | 149 | 0.00% | 1 | 0 |
| yacc | 63 | 0.00% | 1 | 0 |
| AppleScript | 56 | 0.00% | 1 | 0 |
| Elixir Script | 27 | 0.00% | 1 | 0 |
| PHP | 11 | 0.00% | 1 | 0 |
| IDL | 8 | 0.00% | 1 | 0 |
| **Total** | **35,581,725** | **100.00%** | — | **156** |

**Project size across 55 pinned snapshots (SLOC)**

| Minimum | P25 | Median | Mean | P75 | Maximum |
|---:|---:|---:|---:|---:|---:|
| 50,846 | 194,707.50 | 404,139 | 646,940.45 | 943,666 | 2,112,892 |

**Original L1 vulnerability categories**: entry shares use 156 entries; report shares use 61 reports.

| Original L1 label | English display | Entries | Entry share | Reports | Report share |
|---|---|---:|---:|---:|---:|
| 业务逻辑 | Business logic | 95 | 60.90% | 36 | 59.02% |
| 代码注入 | Code injection | 12 | 7.69% | 4 | 6.56% |
| XSS | Cross-site scripting (XSS) | 9 | 5.77% | 4 | 6.56% |
| 反序列化漏洞 | Deserialization vulnerability | 7 | 4.49% | 1 | 1.64% |
| 反序列化 | Deserialization | 5 | 3.21% | 1 | 1.64% |
| 命令注入 | Command injection | 4 | 2.56% | 2 | 3.28% |
| SSRF | Server-side request forgery (SSRF) | 3 | 1.92% | 3 | 4.92% |
| 供应链攻击 | Supply chain attack | 3 | 1.92% | 1 | 1.64% |
| 原型链污染 | Prototype pollution | 3 | 1.92% | 1 | 1.64% |
| 模板注入 | Template injection | 3 | 1.92% | 1 | 1.64% |
| 注入与反序列化 | Injection and deserialization | 3 | 1.92% | 1 | 1.64% |
| 文件操作安全 | File operation security | 2 | 1.28% | 1 | 1.64% |
| 权限绕过 | Authorization bypass | 2 | 1.28% | 1 | 1.64% |
| 沙箱逃逸 | Sandbox escape | 2 | 1.28% | 1 | 1.64% |
| 注入类 | Injection | 1 | 0.64% | 1 | 1.64% |
| 路径穿越 | Path traversal | 1 | 0.64% | 1 | 1.64% |
| 路径遍历 / 任意文件读取 | Path traversal / arbitrary file read | 1 | 0.64% | 1 | 1.64% |

Original labels remain separate; English names are display translations only. Complete L1/L2 and per-batch entry/report distributions are in [category statistics](records/category_statistics.csv). Further results are in [dataset statistics](records/dataset_statistics.json), [language statistics](records/language_statistics.csv), [snapshot sizes](records/snapshot_statistics.csv), and [repository sizes](records/repository_statistics.csv).

<!-- DATASET_STATISTICS:END -->

Language and size are measured at each vulnerable commit. Size means physical
source lines of code (SLOC), excluding comments and blank lines. The primary
language is the language with the most SLOC in a snapshot; entry-level
language counts inherit that snapshot label. It does not necessarily identify
the language at the vulnerable anchor. Multilingual snapshot counts can overlap.

Measurements use pinned **cloc 2.10**, tracked regular files, and the explicit
[source-size policy](scripts/source_size_policy.json). Tests and examples are
included; documentation, data/configuration languages, dependencies, and
identified generated/vendor files are excluded. Generated-file detection is
heuristic. Snapshot totals count different versions of a repository separately.
Categories retain the original bilingual L1/L2 labels; report distributions
count distinct report/category memberships rather than relabeling annotations.

## Quick start

Clone the six-batch branch explicitly. For an existing local checkout, start
with the Python commands.

```bash
git clone --branch codex/six-batch-dataset https://github.com/yzeirnials/VulnGym_v012.git
cd VulnGym_v012
python3 scripts/subset_dataset.py --validate
python3 examples/load_dataset.py
```

Validation and evaluation use the Python standard library. The loader also
demonstrates optional pandas and HuggingFace `datasets` loading from these
local files. Tencent's HuggingFace dataset has a different scope.

| File | Role |
|---|---|
| `data/entries.jsonl` | 156 pair-level ground-truth entries |
| `data/reports.jsonl` | 61 reports with retained `entry_ids` and `num_entries` |
| `data/entry_points.jsonl` | 136 deduplicated entry-point anchors |
| `data/critical_operations.jsonl` | 137 deduplicated critical-operation anchors |
| `data/entries_desc.jsonl` | 156 matching entries with preserved explanatory `desc` annotations |
| `data/batch_manifest.jsonl` | 55 snapshot rows defining the six batches |
| `data/dataset.json` | Dataset identity, source commits, counts, and file bindings |

Source repositories are referenced by `repo_url` and `commit`; they are not
bundled in this dataset. Keep ground-truth annotations out of tool prompts and
configuration when measuring ground-truth-blind detection.

## Evaluate findings

Record native findings in the [conversion-table format](examples/conversion_table.schema.json),
then export and score the three roles:

```bash
python3 examples/conversion_table_to_eval_inputs.py examples/example_conversion_table.jsonl --out-dir /tmp/vulngym_eval_inputs
python3 examples/evaluate.py /tmp/vulngym_eval_inputs/pair_findings.jsonl --json-out /tmp/vulngym_pair.json
python3 examples/evaluate_entry_points.py /tmp/vulngym_eval_inputs/entry_point_findings.jsonl --json-out /tmp/vulngym_ep.json
python3 examples/evaluate_critical_operations.py /tmp/vulngym_eval_inputs/critical_operation_findings.jsonl --json-out /tmp/vulngym_co.json
```

The JSONL files under `examples/` are illustrative fixtures, not tool results.
Explicit candidate pairs are preserved; a row is automatically paired only
when it has exactly one usable candidate for each role. Multiple candidates
are never expanded into an implicit Cartesian product.

Evaluators default to this checkout's complete six-batch ground truth,
independent of the working directory. Pair evaluation accepts `--entries`;
anchor evaluation accepts `--ground-truth` to select a different GT file.
Reports include the actual GT path and scope. Findings never narrow the
denominator. For the complete dataset, all **156 pairs / 61 reports, 136 EP
anchors, and 137 CO anchors** have usable lines.

Matching uses the same repository and commit, normalized exact paths, strict
endpoint roles, and a default `--line-tolerance 5`; integer lines and line
ranges are supported. Unusable GT lines are excluded. `trace` is not matched.
These are **recall/coverage metrics**; no precision or F1 is computed. The pair
evaluator reports advisory coverage when any of an advisory's entries matches;
anchor evaluation also reports source-entry and report coverage.

## Reproduce the subset and statistics

With the Git history available, reproduce the selected data in a new directory:

```bash
python3 scripts/subset_dataset.py --output-dir ../VulnGym-six-batches-reproduced
python3 scripts/subset_dataset.py --batch-id mixed-05 --output-dir ../VulnGym-mixed-05
python3 scripts/build_endpoint_ground_truth.py --check
python3 -m unittest discover -s tests
```

`--batch-id` is repeatable. The generator reads the pinned source commits and
the retained manifest, preserves IDs and endpoint locations, and recalculates
report and anchor associations. Output directories must be new. The historical
cleaning and anchor scripts default to read-only checks and do not rewrite docs.

Rebuild statistics using the included source measurements:

```bash
python3 scripts/dataset_stats.py --source-sizes records/source_sizes.json --output-dir records --update-readmes
```

Omit `--update-readmes` to regenerate only the JSON and CSV artifacts.

To measure source code again, prepare clean Git checkouts at all 55 manifest
commits and install Perl plus the official cloc 2.10 script. Its required
SHA-256 and filtering rules are fixed in the source-size policy:

```bash
python3 scripts/measure_source_sizes.py --source-root /path/to/source-cache --cloc /path/to/cloc-2.10.pl
```

The cache uses `<host-and-repo-with-nonalphanumeric-runs-replaced-by-__>__<commit>`
directory names. Alternatively, use `--source-map /path/to/local-map.jsonl`,
whose rows contain `repo_url`, `commit`, and `cache_path`. Machine-specific maps
stay local. Measurement reads tracked source without building or executing it.

## Provenance and historical material

Tencent VulnGym v0.1.2 originally contained 408 entries / 184 reports. The
first cleaning retained 274 verified entries / 137 reports. This second
selection retains the six batches above, using source commit
`90002144d4a8b3654fb1bf68052889b9c2de44aa`; explanatory annotations come from
`4c4ac5659329008d9ea44ac5ec7855eae6909c2e`.

[CHANGELOG.md](CHANGELOG.md) and the dated `20260608` records preserve earlier
cleanup history. Their counts and any historical benchmark material refer to
their original scopes, not to six-batch evaluation results. This repository
does not claim a newly measured six-batch tool baseline. The
[earlier README](https://github.com/yzeirnials/VulnGym_v012/blob/90002144d4a8b3654fb1bf68052889b9c2de44aa/README.md)
preserves the original release overview.

## Attribution and license

The original dataset is credited to the **Tencent Wukong Code Security Team
and VulnGym contributors**. Cite the original dataset using [CITATION.cff](CITATION.cff)
and identify this fork, the six-batch selection, and the revision used in your
experiment. Dataset annotations are licensed under [CC-BY-4.0](LICENSE).
Referenced source projects retain their own licenses.
