# VulnGym Endpoint-Level Ground Truth Record

Date: 2026-07-09

## Scope

This record documents endpoint-level ground-truth files derived from the
verified pair-level dataset in:

```text
C:/Users/chenyz/Documents/VulnGym-exp/work/VulnGym-cleaned
```

## Version

```text
branch: cleaned-20260709
source_commit_before_generation: dbd38e8475dd7af85aa34c3a6778098c27f70013
generated_at_utc: 2026-07-09T06:29:50+00:00
```

## Generated Files

```text
data/entry_points.jsonl
data/critical_operations.jsonl
examples/evaluate_entry_points.py
examples/evaluate_critical_operations.py
```

## Counts

| Metric | Count |
|---|---:|
| source pair-level entries | 393 |
| source reports | 178 |
| unique entry-point anchors | 350 |
| entry-point duplicate anchor groups | 34 |
| entry-point extra source entries collapsed | 43 |
| unique critical-operation anchors | 356 |
| critical-operation duplicate anchor groups | 30 |
| critical-operation extra source entries collapsed | 37 |

## Rules

- Derive anchors only from `data/entries.jsonl`.
- Require source entries to have `verify == 1`.
- Deduplicate anchors by `(repo_url, commit, file, line)` for the chosen
  endpoint field.
- Preserve code snippets observed at the deduplicated location in
  `source_endpoint_codes`.
- Preserve traceability through `source_entry_ids` and `source_report_ids`.
- Do not use `trace` in endpoint-level evaluator matching.

## Entry-Point Duplicate Examples

| anchor_id | source_entry_ids | source_report_ids |
| --- | --- | --- |
| entry-point-00004 | entry-00465, entry-00466 | GHSA-48M6-CH88-55MJ |
| entry-point-00026 | entry-00468, entry-00469 | GHSA-2X8M-83VC-6WV4, GHSA-XHMJ-RG95-44HV |
| entry-point-00030 | entry-00476, entry-00479 | GHSA-2X8M-83VC-6WV4 |
| entry-point-00033 | entry-00471, entry-00481 | GHSA-2X8M-83VC-6WV4 |
| entry-point-00077 | entry-00314, entry-00315 | GHSA-8X34-9Q3V-H7G8 |
| entry-point-00167 | entry-00349, entry-00350 | GHSA-58QR-RCGV-642V |
| entry-point-00181 | entry-00362, entry-00363 | GHSA-WQ58-2PVG-5H4F |
| entry-point-00185 | entry-00305, entry-00307 | GHSA-WCXR-59V9-RXR8 |
| entry-point-00196 | entry-00245, entry-00246, entry-00247, entry-00248 | GHSA-7FF8-XJH3-MGH6 |
| entry-point-00198 | entry-00251, entry-00252 | GHSA-2CH6-X3G4-7759 |
| entry-point-00208 | entry-00158, entry-00163 | GHSA-H9G4-589H-68XV |
| entry-point-00209 | entry-00161, entry-00166 | GHSA-H9G4-589H-68XV |
| entry-point-00210 | entry-00162, entry-00167 | GHSA-H9G4-589H-68XV |
| entry-point-00211 | entry-00159, entry-00164 | GHSA-H9G4-589H-68XV |
| entry-point-00212 | entry-00160, entry-00165 | GHSA-H9G4-589H-68XV |
| entry-point-00213 | entry-00292, entry-00293 | GHSA-4W7M-58CG-CMFF |
| entry-point-00229 | entry-00383, entry-00384 | GHSA-XP9R-PRPG-373R |
| entry-point-00234 | entry-00407, entry-00408 | GHSA-V3QC-WRWX-J3PW |
| entry-point-00237 | entry-00398, entry-00399 | GHSA-5H2W-QMFP-GGP6 |
| entry-point-00240 | entry-00387, entry-00388 | GHSA-94PW-C6M8-P9P9 |

## Critical-Operation Duplicate Examples

| anchor_id | source_entry_ids | source_report_ids |
| --- | --- | --- |
| critical-operation-00026 | entry-00471, entry-00474, entry-00481 | GHSA-2X8M-83VC-6WV4 |
| critical-operation-00041 | entry-00429, entry-00477 | GHSA-4JPM-CGX2-8H37, GHSA-6F7G-V4PP-R667 |
| critical-operation-00092 | entry-00430, entry-00432 | GHSA-RG7C-G689-FR3X |
| critical-operation-00101 | entry-00372, entry-00373 | GHSA-8C4J-F57C-35CF |
| critical-operation-00182 | entry-00362, entry-00363 | GHSA-WQ58-2PVG-5H4F |
| critical-operation-00186 | entry-00305, entry-00307 | GHSA-WCXR-59V9-RXR8 |
| critical-operation-00190 | entry-00379, entry-00380 | GHSA-FQW4-MPH7-2VR8 |
| critical-operation-00196 | entry-00245, entry-00246, entry-00247, entry-00248 | GHSA-7FF8-XJH3-MGH6 |
| critical-operation-00198 | entry-00251, entry-00252 | GHSA-2CH6-X3G4-7759 |
| critical-operation-00208 | entry-00158, entry-00163 | GHSA-H9G4-589H-68XV |
| critical-operation-00209 | entry-00161, entry-00166 | GHSA-H9G4-589H-68XV |
| critical-operation-00210 | entry-00162, entry-00167 | GHSA-H9G4-589H-68XV |
| critical-operation-00211 | entry-00159, entry-00164 | GHSA-H9G4-589H-68XV |
| critical-operation-00212 | entry-00160, entry-00165 | GHSA-H9G4-589H-68XV |
| critical-operation-00263 | entry-00328, entry-00330, entry-00331 | GHSA-QWMF-95R9-GX9X |
| critical-operation-00272 | entry-00402, entry-00403, entry-00404, entry-00405 | GHSA-P4X4-2R7F-WJXG |
| critical-operation-00274 | entry-00450, entry-00451 | GHSA-6XG4-82HV-CP6F |
| critical-operation-00276 | entry-00129, entry-00134 | GHSA-PCHC-86F6-8758, GHSA-XC7W-V5X6-CC87 |
| critical-operation-00290 | entry-00294, entry-00296 | GHSA-QC36-X95H-7J53, GHSA-XF99-J42Q-5W5P |
| critical-operation-00303 | entry-00201, entry-00202 | GHSA-JR6X-2Q95-FH2G |

## Machine-Readable Summary

```text
records/endpoint_ground_truth_20260709_summary.json
```
