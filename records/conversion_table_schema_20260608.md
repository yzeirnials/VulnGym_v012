# VulnGym Conversion Table Schema — 2026-06-08

> Historical implementation record; source paths and dated context below
> are preserved. The conversion contract still applies. Current dataset
> scope and usage are documented in [README](../README.md) and
> [SCHEMA](../SCHEMA.md).

This record documents the v2 dataset-setting change for the cleaned VulnGym
fork at `/home/ubuntu/BenchmarkForks/worktrees/VulnGym-cleaned`.

## Purpose

Raw tool outputs are intentionally not treated as evaluator inputs directly.
They first pass through a provenance-preserving conversion table. The table
records how each original finding was mapped into VulnGym's `entry_point` and
`critical_operation` terminology, including partial and failed conversions.

## Files Added

```text
examples/conversion_table.schema.json
examples/conversion_table_to_eval_inputs.py
examples/example_conversion_table.jsonl
```

## Core Policy

- One conversion-table row corresponds to one original tool finding.
- Candidate endpoints preserve their own `conversion_method` because the
  `entry_point` and `critical_operation` sides of the same finding may be
  converted by different methods.
- Supported methods are `direct`, `source-resolved`, `semantic-assisted`, and
  `not-converted`.
- The exporter writes three evaluator input files:
  `pair_findings.jsonl`, `entry_point_findings.jsonl`, and
  `critical_operation_findings.jsonl`.
- Pair-level export is conservative. It honors explicit `candidate_pairs`; if
  no pairs are supplied, a row is auto-paired only when it has exactly one
  usable entry-point candidate and exactly one usable critical-operation
  candidate. It does not generate a Cartesian product for multi-candidate rows.
- Skipped or invalid conversions are preserved in `conversion_skipped.jsonl`
  rather than silently dropped.

## Relationship To Evaluators

The conversion table is not ground truth and does not change the evaluator
matching policy. It is an audit layer before running:

```text
examples/evaluate.py
examples/evaluate_entry_points.py
examples/evaluate_critical_operations.py
```
