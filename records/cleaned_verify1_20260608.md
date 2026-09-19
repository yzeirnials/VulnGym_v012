# VulnGym Verify=1 Cleaned Dataset Record

> Historical record of the first, 274-entry cleanup. Its counts, source paths,
> and execution context are preserved; they are not the current six-batch
> scope. See [current dataset identity](../data/dataset.json) and
> [statistics](dataset_statistics.json).

Date: 2026-06-08

## Scope

This record documents the experiment-fork cleanup of VulnGym under:

```text
/home/ubuntu/BenchmarkForks/worktrees/VulnGym-cleaned
```

The cleanup keeps only `data/entries.jsonl` rows where `verify == 1`.
`data/reports.jsonl` is re-aggregated to match the retained entries.

## Version

```text
branch: cleaned-20260608
baseline_commit_before_cleaning: 6fcfe4033fe252ac2ed3f69458eff20b9de76872
upstream: Tencent/VulnGym
generated_at_utc: 2026-06-08T09:25:17+00:00
```

## Counts

| Metric | Before | After |
|---|---:|---:|
| reports | 184 | 137 |
| entries | 408 | 274 |
| verified entries | 274 | 274 |
| reports with at least one verified entry | 137 | 137 |
| reports removed | 0 | 47 |
| entries removed | 0 | 134 |
| originally partial verified reports re-aggregated | 29 | 0 |

## Rules

- Keep every entry with `verify == 1`.
- Remove every entry with `verify != 1`.
- Keep a report if at least one of its entries is retained.
- Remove a report if none of its entries is retained.
- For partially verified reports, recompute `entry_ids` and `num_entries` from
  the retained verified entries only.
- Do not change `repo_url`, `commit`, `source_link`, `vuln_ids`, `project`, or
  `vuln_title` except through the report re-aggregation described above.

## Retained Reports

| report_id | project | retained_entries | original_entries | removed_unverified_entries | retained_entry_ids |
| --- | --- | --- | --- | --- | --- |
| GHSA-25GX-X37C-7PPH | openclaw | 1 | 2 | 1 | entry-00222 |
| GHSA-265W-RF2W-CJH4 | paperclipai/paperclip | 1 | 1 | 0 | entry-00437 |
| GHSA-2CH6-X3G4-7759 | openclaw | 2 | 2 | 0 | entry-00251, entry-00252 |
| GHSA-2CQ5-MF3V-MX44 | openclaw | 1 | 1 | 0 | entry-00505 |
| GHSA-2P9H-RQJW-GM92 | n8n | 3 | 3 | 0 | entry-00189, entry-00190, entry-00191 |
| GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise | 5 | 12 | 7 | entry-00469, entry-00471, entry-00474, entry-00475, entry-00481 |
| GHSA-33RQ-M5X2-FVGF | OpenClaw | 1 | 1 | 0 | entry-00142 |
| GHSA-345P-7CG4-V4C7 | typescript-sdk | 2 | 2 | 0 | entry-00114, entry-00115 |
| GHSA-3C6H-G97W-FG78 | openclaw | 1 | 1 | 0 | entry-00232 |
| GHSA-3CW3-5VXW-G2H3 | openclaw | 1 | 1 | 0 | entry-00393 |
| GHSA-3M3Q-X3GJ-F79X | openclaw | 1 | 3 | 2 | entry-00136 |
| GHSA-3W6X-GV34-MQPF | openclaw | 3 | 3 | 0 | entry-00368, entry-00369, entry-00370 |
| GHSA-3XX2-MQJM-HG9X | paperclipai/paperclip | 6 | 6 | 0 | entry-00483, entry-00484, entry-00485, entry-00486, entry-00487, entry-00488 |
| GHSA-474H-PRJG-MMW3 | openclaw | 2 | 2 | 0 | entry-00227, entry-00228 |
| GHSA-48M6-CH88-55MJ | FlowiseAI/Flowise | 2 | 2 | 0 | entry-00465, entry-00466 |
| GHSA-4JPW-HJ22-2XMC | openclaw | 1 | 1 | 0 | entry-00291 |
| GHSA-4M3H-WP5W-5HQH | apache/airflow | 1 | 1 | 0 | entry-00313 |
| GHSA-4W7M-58CG-CMFF | openclaw | 2 | 2 | 0 | entry-00292, entry-00293 |
| GHSA-4X5P-F36R-MXXR | mlflow | 2 | 2 | 0 | entry-00101, entry-00102 |
| GHSA-525J-HQQ2-66R4 | openclaw | 2 | 2 | 0 | entry-00498, entry-00499 |
| GHSA-58JC-RCG5-95F3 | n8n | 3 | 3 | 0 | entry-00084, entry-00085, entry-00086 |
| GHSA-5F53-522J-J454 | FlowiseAI/Flowise | 4 | 4 | 0 | entry-00264, entry-00265, entry-00266, entry-00267 |
| GHSA-5H2M-4Q8J-PQPJ | fastmcp | 1 | 2 | 1 | entry-00311 |
| GHSA-5H2W-QMFP-GGP6 | openclaw | 2 | 2 | 0 | entry-00398, entry-00399 |
| GHSA-5R8F-96GM-5J6G | openclaw | 1 | 1 | 0 | entry-00400 |
| GHSA-5V6X-RFC3-7QFR | openclaw | 1 | 2 | 1 | entry-00208 |
| GHSA-5WJ5-87VQ-39XM | openclaw | 1 | 1 | 0 | entry-00424 |
| GHSA-63F5-HHC7-CX6P | openclaw | 1 | 1 | 0 | entry-00312 |
| GHSA-64QX-VPXX-MVQF | openclaw | 2 | 3 | 1 | entry-00123, entry-00124 |
| GHSA-65H8-27JH-Q8WV | openclaw | 1 | 2 | 1 | entry-00365 |
| GHSA-69FQ-XP46-6X23 | aquasecurity/trivy | 3 | 3 | 0 | entry-00332, entry-00333, entry-00334 |
| GHSA-6F7G-V4PP-R667 | FlowiseAI/Flowise | 2 | 2 | 0 | entry-00477, entry-00478 |
| GHSA-6QV9-48XG-FC7F | langchain-core | 3 | 3 | 0 | entry-00066, entry-00067, entry-00068 |
| GHSA-6XG4-82HV-CP6F | openclaw | 2 | 2 | 0 | entry-00450, entry-00451 |
| GHSA-736R-JWJ6-4W23 | openclaw | 2 | 2 | 0 | entry-00496, entry-00497 |
| GHSA-7429-HXCV-268M | open-webui | 1 | 1 | 0 | entry-00401 |
| GHSA-75HX-XJ24-MQRW | n8n-mcp | 2 | 3 | 1 | entry-00506, entry-00507 |
| GHSA-7FF8-XJH3-MGH6 | openclaw | 4 | 4 | 0 | entry-00245, entry-00246, entry-00247, entry-00248 |
| GHSA-7GRX-3XCX-2XV5 | langflow | 1 | 1 | 0 | entry-00324 |
| GHSA-7JP6-R74R-995Q | openclaw | 1 | 1 | 0 | entry-00500 |
| GHSA-7PPG-37FH-VCR6 | milvus | 4 | 4 | 0 | entry-00117, entry-00118, entry-00119, entry-00120 |
| GHSA-7QHF-V65M-G5F3 | mlflow | 4 | 4 | 0 | entry-00413, entry-00414, entry-00415, entry-00416 |
| GHSA-7XMQ-G46G-F8PV | openclaw | 2 | 4 | 2 | entry-00194, entry-00196 |
| GHSA-82QX-6VJ7-P8M2 | openclaw | 3 | 3 | 0 | entry-00493, entry-00494, entry-00495 |
| GHSA-8C4J-F57C-35CF | langflow | 3 | 3 | 0 | entry-00372, entry-00373, entry-00374 |
| GHSA-8X34-9Q3V-H7G8 | apache/airflow | 3 | 3 | 0 | entry-00314, entry-00315, entry-00316 |
| GHSA-9379-MWVR-7WXX | NVIDIA NeMo | 5 | 8 | 3 | entry-00151, entry-00154, entry-00155, entry-00156, entry-00157 |
| GHSA-94PW-C6M8-P9P9 | openclaw | 2 | 2 | 0 | entry-00387, entry-00388 |
| GHSA-98HH-7GHG-X6RQ | openclaw | 2 | 2 | 0 | entry-00396, entry-00397 |
| GHSA-9F72-QCPW-2HXC | openclaw/openclaw | 1 | 1 | 0 | entry-00215 |
| GHSA-9G95-QF3F-GGRW | n8n | 3 | 3 | 0 | entry-00107, entry-00108, entry-00109 |
| GHSA-9P38-94JF-HGJJ | openclaw | 1 | 1 | 0 | entry-00233 |
| GHSA-9P93-7J67-5PC2 | openclaw | 1 | 1 | 0 | entry-00375 |
| GHSA-C5CP-VX83-JHQX | langflow | 2 | 3 | 1 | entry-00071, entry-00072 |
| GHSA-CCJ6-79J6-CQ5Q | WeKnora | 4 | 4 | 0 | entry-00271, entry-00272, entry-00273, entry-00274 |
| GHSA-CWC3-P92J-G7QM | Flowise | 2 | 2 | 0 | entry-00269, entry-00270 |
| GHSA-F275-5H5C-5WG5 | openclaw | 1 | 2 | 1 | entry-00385 |
| GHSA-F6MR-38G8-39RG | ollama | 2 | 6 | 4 | entry-00076, entry-00078 |
| GHSA-F7WW-2725-QVW2 | openclaw | 2 | 2 | 0 | entry-00210, entry-00211 |
| GHSA-FJH6-8679-9PCH | FlowiseAI/Flowise | 1 | 1 | 0 | entry-00065 |
| GHSA-FQW4-MPH7-2VR8 | openclaw | 2 | 2 | 0 | entry-00379, entry-00380 |
| GHSA-FVCW-9W9R-PXC7 | Flowise | 1 | 2 | 1 | entry-00278 |
| GHSA-FXCW-H3QJ-8M8P | n8n | 1 | 2 | 1 | entry-00357 |
| GHSA-G2J9-7RJ2-GM6C | langflow | 1 | 2 | 1 | entry-00321 |
| GHSA-G374-MGGX-P6XC | openclaw | 1 | 1 | 0 | entry-00458 |
| GHSA-G5CG-8X5W-7JPM | openclaw | 1 | 1 | 0 | entry-00406 |
| GHSA-G75X-8QQM-2VXP | openclaw | 1 | 1 | 0 | entry-00240 |
| GHSA-GG9V-MGCP-V6M7 | openclaw | 1 | 1 | 0 | entry-00459 |
| GHSA-GJM7-HW8F-73RQ | openclaw | 2 | 2 | 0 | entry-00411, entry-00412 |
| GHSA-GP3Q-WPQ4-5C5H | openclaw | 3 | 3 | 0 | entry-00283, entry-00284, entry-00285 |
| GHSA-GV46-4XFQ-JV58 | openclaw | 1 | 1 | 0 | entry-00207 |
| GHSA-H6GW-8F77-MMMP | WeKnora | 1 | 1 | 0 | entry-00276 |
| GHSA-H9G4-589H-68XV | openclaw | 10 | 10 | 0 | entry-00158, entry-00159, entry-00160, entry-00161, entry-00162, entry-00163, entry-00164, entry-00165, entry-00166, entry-00167 |
| GHSA-H9XM-J4QG-FVPG | openclaw | 2 | 2 | 0 | entry-00229, entry-00230 |
| GHSA-HF68-49FM-59CQ | OpenClaw Gateway | 1 | 1 | 0 | entry-00371 |
| GHSA-HV53-3329-VMRM | n8n | 1 | 2 | 1 | entry-00113 |
| GHSA-HV93-R4J3-Q65F | openclaw | 2 | 2 | 0 | entry-00125, entry-00126 |
| GHSA-J8G8-J7FC-43V6 | FlowiseAI/Flowise | 2 | 2 | 0 | entry-00262, entry-00263 |
| GHSA-JJ82-76V6-933R | openclaw | 2 | 2 | 0 | entry-00249, entry-00250 |
| GHSA-JJHC-V7C2-5HH6 | litellm | 1 | 1 | 0 | entry-00419 |
| GHSA-JJPJ-P2WH-QF23 | n8n | 2 | 2 | 0 | entry-00174, entry-00175 |
| GHSA-JM6W-M3J8-898G | nltk | 1 | 1 | 0 | entry-00319 |
| GHSA-JQPF-VJ28-9V7R | openclaw | 1 | 1 | 0 | entry-00318 |
| GHSA-JR6X-2Q95-FH2G | openclaw | 3 | 4 | 1 | entry-00200, entry-00201, entry-00202 |
| GHSA-JV6R-27WW-4GW4 | openclaw | 3 | 3 | 0 | entry-00216, entry-00217, entry-00218 |
| GHSA-M3MH-3MPG-37HW | openclaw | 2 | 2 | 0 | entry-00381, entry-00382 |
| GHSA-M4JW-WGMF-889X | NVIDIA/NeMo | 7 | 11 | 4 | entry-00339, entry-00342, entry-00343, entry-00344, entry-00345, entry-00346, entry-00347 |
| GHSA-MHJQ-8C7M-3F7P | milvus-io/milvus | 1 | 1 | 0 | entry-00058 |
| GHSA-MJ4P-RC52-M843 | openclaw | 2 | 2 | 0 | entry-00301, entry-00302 |
| GHSA-MP5H-M6QJ-6292 | openclaw | 2 | 4 | 2 | entry-00131, entry-00132 |
| GHSA-MQ4R-H2GH-QV7X | FlowiseAI/Flowise | 1 | 1 | 0 | entry-00268 |
| GHSA-MQPW-46FH-299H | openclaw/openclaw | 1 | 1 | 0 | entry-00147 |
| GHSA-MR32-VWC2-5J6H | openclaw | 2 | 2 | 0 | entry-00127, entry-00128 |
| GHSA-MXRG-77HM-89HV | n8n | 3 | 3 | 0 | entry-00359, entry-00360, entry-00361 |
| GHSA-P4X4-2R7F-WJXG | openclaw | 4 | 4 | 0 | entry-00402, entry-00403, entry-00404, entry-00405 |
| GHSA-PCHC-86F6-8758 | openclaw | 1 | 1 | 0 | entry-00134 |
| GHSA-PFV5-RPCW-X34X | openclaw | 2 | 2 | 0 | entry-00322, entry-00323 |
| GHSA-Q2HG-643C-GW8H | Apache Airflow | 1 | 1 | 0 | entry-00464 |
| GHSA-Q2QC-744P-66R2 | openclaw | 1 | 1 | 0 | entry-00513 |
| GHSA-Q56X-G2FJ-4RJ6 | onnx | 2 | 2 | 0 | entry-00462, entry-00463 |
| GHSA-QC36-X95H-7J53 | openclaw | 1 | 1 | 0 | entry-00296 |
| GHSA-QM2M-28PF-HGJW | openclaw | 1 | 1 | 0 | entry-00378 |
| GHSA-QPQ4-PW7F-PP8W | n8n | 2 | 2 | 0 | entry-00110, entry-00111 |
| GHSA-QWMF-95R9-GX9X | openclaw | 4 | 4 | 0 | entry-00328, entry-00329, entry-00330, entry-00331 |
| GHSA-R277-3XC5-C79V | AutoGPT | 2 | 2 | 0 | entry-00097, entry-00098 |
| GHSA-R54R-WMMQ-MH84 | openclaw | 1 | 1 | 0 | entry-00226 |
| GHSA-R65X-2HQR-J5HF | openclaw | 1 | 2 | 1 | entry-00214 |
| GHSA-R7VR-GR74-94P8 | openclaw | 4 | 4 | 0 | entry-00297, entry-00298, entry-00299, entry-00300 |
| GHSA-RG7C-G689-FR3X | google/adk-python | 3 | 6 | 3 | entry-00431, entry-00432, entry-00435 |
| GHSA-RQ6G-PX6M-C248 | openclaw | 1 | 1 | 0 | entry-00148 |
| GHSA-RQPP-RJJ8-7WV8 | openclaw | 2 | 2 | 0 | entry-00308, entry-00309 |
| GHSA-RV39-79C4-7459 | openclaw | 1 | 1 | 0 | entry-00121 |
| GHSA-RW39-5899-8MXP | openclaw | 1 | 1 | 0 | entry-00295 |
| GHSA-V3QC-WRWX-J3PW | openclaw | 2 | 2 | 0 | entry-00407, entry-00408 |
| GHSA-V4PR-FM98-W9PG | n8n | 1 | 1 | 0 | entry-00087 |
| GHSA-V773-R54F-Q32W | openclaw | 1 | 1 | 0 | entry-00149 |
| GHSA-V7V2-M736-CF3C | NVIDIA NeMo Framework | 3 | 3 | 0 | entry-00335, entry-00336, entry-00337 |
| GHSA-V865-P3GQ-HW6M | openclaw | 1 | 2 | 1 | entry-00225 |
| GHSA-V98V-FF95-F3CP | n8n | 2 | 2 | 0 | entry-00082, entry-00083 |
| GHSA-VJQW-W5JR-G9W5 | openclaw | 1 | 2 | 1 | entry-00510 |
| GHSA-VPCF-GVG4-6QWR | n8n | 6 | 6 | 0 | entry-00177, entry-00178, entry-00179, entry-00180, entry-00181, entry-00182 |
| GHSA-VPJ2-69HF-RPPW | OpenClaw | 1 | 2 | 1 | entry-00188 |
| GHSA-VR7G-88FQ-VHQ3 | paperclipai/paperclip | 1 | 1 | 0 | entry-00446 |
| GHSA-VV7Q-7JX5-F767 | fastmcp | 1 | 4 | 3 | entry-00395 |
| GHSA-VVJH-F6P9-5VCF | openclaw | 2 | 2 | 0 | entry-00256, entry-00257 |
| GHSA-W235-X559-36MG | openclaw | 1 | 3 | 2 | entry-00168 |
| GHSA-W7XJ-8FX7-WFCH | open-webui | 1 | 1 | 0 | entry-00057 |
| GHSA-WCXR-59V9-RXR8 | openclaw | 4 | 4 | 0 | entry-00304, entry-00305, entry-00306, entry-00307 |
| GHSA-WQ58-2PVG-5H4F | openclaw | 2 | 2 | 0 | entry-00362, entry-00363 |
| GHSA-WR92-6W3G-2HWC | openclaw | 1 | 1 | 0 | entry-00327 |
| GHSA-WVHQ-WP8G-C7VQ | Flowise | 1 | 4 | 3 | entry-00261 |
| GHSA-X82F-27X3-Q89C | openclaw | 1 | 2 | 1 | entry-00193 |
| GHSA-XC7W-V5X6-CC87 | openclaw | 1 | 1 | 0 | entry-00129 |
| GHSA-XF99-J42Q-5W5P | openclaw | 1 | 1 | 0 | entry-00294 |
| GHSA-XH72-V6V9-MWHC | openclaw | 4 | 4 | 0 | entry-00501, entry-00502, entry-00503, entry-00504 |
| GHSA-XP9R-PRPG-373R | openclaw | 2 | 2 | 0 | entry-00383, entry-00384 |
| GHSA-XW77-45GV-P728 | openclaw | 4 | 4 | 0 | entry-00286, entry-00287, entry-00288, entry-00289 |

## Removed Reports

| report_id | project | removed_entries | removed_entry_ids |
| --- | --- | --- | --- |
| GHSA-2F4C-VRJQ-RCGV | WeKnora | 1 | entry-00275 |
| GHSA-3PRP-9GF7-4RXX | FlowiseAI/Flowise | 3 | entry-00489, entry-00490, entry-00491 |
| GHSA-47WQ-CJ9Q-WPMP | paperclip | 3 | entry-00447, entry-00448, entry-00449 |
| GHSA-4HG8-92X6-H2F3 | openclaw | 1 | entry-00145 |
| GHSA-4JPM-CGX2-8H37 | flowise | 1 | entry-00429 |
| GHSA-4RJ2-GPMH-QQ5X | openclaw | 2 | entry-00143, entry-00144 |
| GHSA-58QR-RCGV-642V | n8n | 2 | entry-00349, entry-00350 |
| GHSA-5FW2-MWHH-9947 | FlowiseAI/Flowise | 1 | entry-00492 |
| GHSA-5XRP-6693-JJX9 | n8n | 2 | entry-00099, entry-00100 |
| GHSA-6CQR-8CFR-67F8 | n8n | 2 | entry-00511, entry-00512 |
| GHSA-75G8-RV7V-32F7 | n8n | 2 | entry-00172, entry-00173 |
| GHSA-78H3-63C4-5FQC | Tencent/WeKnora | 2 | entry-00080, entry-00081 |
| GHSA-825Q-W924-XHGX | n8n | 1 | entry-00103 |
| GHSA-98C2-4CR3-4JC3 | n8n | 1 | entry-00358 |
| GHSA-9HJH-FR4F-GXC4 | openclaw | 1 | entry-00377 |
| GHSA-9P3R-HH9G-5CMG | openclaw | 1 | entry-00410 |
| GHSA-C545-X2RH-82FC | n8n | 1 | entry-00355 |
| GHSA-C6XV-RCVW-V685 | open-webui | 1 | entry-00062 |
| GHSA-F6HC-C5JR-878P | Flowise (FlowiseAI/Flowise) | 1 | entry-00436 |
| GHSA-G55J-C2V4-PJCG | openclaw | 1 | entry-00116 |
| GHSA-GFVG-QV54-R4PC | n8n | 3 | entry-00104, entry-00105, entry-00106 |
| GHSA-GQ3W-7JJ3-X7GR | mlflow | 1 | entry-00171 |
| GHSA-H3F9-MJWJ-W476 | openclaw | 1 | entry-00146 |
| GHSA-H5HG-H7RR-GPF3 | openclaw | 2 | entry-00417, entry-00418 |
| GHSA-J4P8-H8MH-RH8Q | n8n | 2 | entry-00090, entry-00091 |
| GHSA-JJP7-G2JW-WH3J | open-webui | 1 | entry-00376 |
| GHSA-MMGG-M5J7-F83H | n8n | 1 | entry-00176 |
| GHSA-MWXV-35WR-4VVJ | openclaw | 3 | entry-00219, entry-00220, entry-00221 |
| GHSA-PH9W-R52H-28P7 | langflow-ai/langflow | 2 | entry-00325, entry-00326 |
| GHSA-PJ5X-38RW-6FPH | openclaw | 1 | entry-00231 |
| GHSA-Q399-23R3-HFX4 | openclaw | 1 | entry-00198 |
| GHSA-QCC4-P59M-P54M | openclaw | 1 | entry-00290 |
| GHSA-QJ22-XQJR-V83V | openclaw | 1 | entry-00212 |
| GHSA-R5H9-VJQC-HQ3R | @openclaw/nextcloud-talk | 2 | entry-00140, entry-00141 |
| GHSA-RF6X-R45M-XV3W | Langflow | 1 | entry-00317 |
| GHSA-RVHJ-8CHJ-8V3C | MLflow | 2 | entry-00389, entry-00390 |
| GHSA-V5W9-PRXF-W882 | Flowise (FlowiseAI/Flowise) | 2 | entry-00063, entry-00064 |
| GHSA-VMHQ-CQM9-6P7Q | openclaw | 1 | entry-00303 |
| GHSA-W7J5-J98M-W679 | openclaw | 4 | entry-00241, entry-00242, entry-00243, entry-00244 |
| GHSA-WXX7-MCGF-J869 | n8n | 2 | entry-00183, entry-00184 |
| GHSA-X2FF-J5C2-GGPR | openclaw | 3 | entry-00253, entry-00254, entry-00255 |
| GHSA-X2MW-7J39-93XQ | n8n | 2 | entry-00185, entry-00186 |
| GHSA-X39M-3393-3QP4 | FlowiseAI/Flowise | 1 | entry-00061 |
| GHSA-XFQJ-R5QW-8G4J | paperclip | 6 | entry-00438, entry-00439, entry-00440, entry-00441, entry-00442, entry-00443 |
| GHSA-XHMJ-RG95-44HV | Flowise | 2 | entry-00467, entry-00468 |
| GHSA-XJ9W-5R6Q-X6V4 | openclaw | 1 | entry-00409 |
| GHSA-XVH5-5QG4-X9QP | n8n | 2 | entry-00351, entry-00352 |

## Partially Verified Reports Re-Aggregated

| report_id | project | retained_entry_ids | removed_entry_ids |
| --- | --- | --- | --- |
| GHSA-25GX-X37C-7PPH | openclaw | entry-00222 | entry-00223 |
| GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise | entry-00469, entry-00471, entry-00474, entry-00475, entry-00481 | entry-00470, entry-00472, entry-00473, entry-00476, entry-00479, entry-00480, entry-00482 |
| GHSA-3M3Q-X3GJ-F79X | openclaw | entry-00136 | entry-00135, entry-00137 |
| GHSA-5H2M-4Q8J-PQPJ | fastmcp | entry-00311 | entry-00310 |
| GHSA-5V6X-RFC3-7QFR | openclaw | entry-00208 | entry-00209 |
| GHSA-64QX-VPXX-MVQF | openclaw | entry-00123, entry-00124 | entry-00122 |
| GHSA-65H8-27JH-Q8WV | openclaw | entry-00365 | entry-00364 |
| GHSA-75HX-XJ24-MQRW | n8n-mcp | entry-00506, entry-00507 | entry-00508 |
| GHSA-7XMQ-G46G-F8PV | openclaw | entry-00194, entry-00196 | entry-00195, entry-00197 |
| GHSA-9379-MWVR-7WXX | NVIDIA NeMo | entry-00151, entry-00154, entry-00155, entry-00156, entry-00157 | entry-00150, entry-00152, entry-00153 |
| GHSA-C5CP-VX83-JHQX | langflow | entry-00071, entry-00072 | entry-00073 |
| GHSA-F275-5H5C-5WG5 | openclaw | entry-00385 | entry-00386 |
| GHSA-F6MR-38G8-39RG | ollama | entry-00076, entry-00078 | entry-00074, entry-00075, entry-00077, entry-00079 |
| GHSA-FVCW-9W9R-PXC7 | Flowise | entry-00278 | entry-00277 |
| GHSA-FXCW-H3QJ-8M8P | n8n | entry-00357 | entry-00356 |
| GHSA-G2J9-7RJ2-GM6C | langflow | entry-00321 | entry-00320 |
| GHSA-HV53-3329-VMRM | n8n | entry-00113 | entry-00112 |
| GHSA-JR6X-2Q95-FH2G | openclaw | entry-00200, entry-00201, entry-00202 | entry-00199 |
| GHSA-M4JW-WGMF-889X | NVIDIA/NeMo | entry-00339, entry-00342, entry-00343, entry-00344, entry-00345, entry-00346, entry-00347 | entry-00338, entry-00340, entry-00341, entry-00348 |
| GHSA-MP5H-M6QJ-6292 | openclaw | entry-00131, entry-00132 | entry-00130, entry-00133 |
| GHSA-R65X-2HQR-J5HF | openclaw | entry-00214 | entry-00213 |
| GHSA-RG7C-G689-FR3X | google/adk-python | entry-00431, entry-00432, entry-00435 | entry-00430, entry-00433, entry-00434 |
| GHSA-V865-P3GQ-HW6M | openclaw | entry-00225 | entry-00224 |
| GHSA-VJQW-W5JR-G9W5 | openclaw | entry-00510 | entry-00509 |
| GHSA-VPJ2-69HF-RPPW | OpenClaw | entry-00188 | entry-00187 |
| GHSA-VV7Q-7JX5-F767 | fastmcp | entry-00395 | entry-00391, entry-00392, entry-00394 |
| GHSA-W235-X559-36MG | openclaw | entry-00168 | entry-00169, entry-00170 |
| GHSA-WVHQ-WP8G-C7VQ | Flowise | entry-00261 | entry-00258, entry-00259, entry-00260 |
| GHSA-X82F-27X3-Q89C | openclaw | entry-00193 | entry-00192 |

## Retained Entries

| entry_id | report_id | project |
| --- | --- | --- |
| entry-00057 | GHSA-W7XJ-8FX7-WFCH | open-webui |
| entry-00058 | GHSA-MHJQ-8C7M-3F7P | milvus-io/milvus |
| entry-00065 | GHSA-FJH6-8679-9PCH | FlowiseAI/Flowise |
| entry-00066 | GHSA-6QV9-48XG-FC7F | langchain-core |
| entry-00067 | GHSA-6QV9-48XG-FC7F | langchain-core |
| entry-00068 | GHSA-6QV9-48XG-FC7F | langchain-core |
| entry-00071 | GHSA-C5CP-VX83-JHQX | langflow |
| entry-00072 | GHSA-C5CP-VX83-JHQX | langflow |
| entry-00076 | GHSA-F6MR-38G8-39RG | ollama |
| entry-00078 | GHSA-F6MR-38G8-39RG | ollama |
| entry-00082 | GHSA-V98V-FF95-F3CP | n8n |
| entry-00083 | GHSA-V98V-FF95-F3CP | n8n |
| entry-00084 | GHSA-58JC-RCG5-95F3 | n8n |
| entry-00085 | GHSA-58JC-RCG5-95F3 | n8n |
| entry-00086 | GHSA-58JC-RCG5-95F3 | n8n |
| entry-00087 | GHSA-V4PR-FM98-W9PG | n8n |
| entry-00097 | GHSA-R277-3XC5-C79V | AutoGPT |
| entry-00098 | GHSA-R277-3XC5-C79V | AutoGPT |
| entry-00101 | GHSA-4X5P-F36R-MXXR | mlflow |
| entry-00102 | GHSA-4X5P-F36R-MXXR | mlflow |
| entry-00107 | GHSA-9G95-QF3F-GGRW | n8n |
| entry-00108 | GHSA-9G95-QF3F-GGRW | n8n |
| entry-00109 | GHSA-9G95-QF3F-GGRW | n8n |
| entry-00110 | GHSA-QPQ4-PW7F-PP8W | n8n |
| entry-00111 | GHSA-QPQ4-PW7F-PP8W | n8n |
| entry-00113 | GHSA-HV53-3329-VMRM | n8n |
| entry-00114 | GHSA-345P-7CG4-V4C7 | typescript-sdk |
| entry-00115 | GHSA-345P-7CG4-V4C7 | typescript-sdk |
| entry-00117 | GHSA-7PPG-37FH-VCR6 | milvus |
| entry-00118 | GHSA-7PPG-37FH-VCR6 | milvus |
| entry-00119 | GHSA-7PPG-37FH-VCR6 | milvus |
| entry-00120 | GHSA-7PPG-37FH-VCR6 | milvus |
| entry-00121 | GHSA-RV39-79C4-7459 | openclaw |
| entry-00123 | GHSA-64QX-VPXX-MVQF | openclaw |
| entry-00124 | GHSA-64QX-VPXX-MVQF | openclaw |
| entry-00125 | GHSA-HV93-R4J3-Q65F | openclaw |
| entry-00126 | GHSA-HV93-R4J3-Q65F | openclaw |
| entry-00127 | GHSA-MR32-VWC2-5J6H | openclaw |
| entry-00128 | GHSA-MR32-VWC2-5J6H | openclaw |
| entry-00129 | GHSA-XC7W-V5X6-CC87 | openclaw |
| entry-00131 | GHSA-MP5H-M6QJ-6292 | openclaw |
| entry-00132 | GHSA-MP5H-M6QJ-6292 | openclaw |
| entry-00134 | GHSA-PCHC-86F6-8758 | openclaw |
| entry-00136 | GHSA-3M3Q-X3GJ-F79X | openclaw |
| entry-00142 | GHSA-33RQ-M5X2-FVGF | OpenClaw |
| entry-00147 | GHSA-MQPW-46FH-299H | openclaw/openclaw |
| entry-00148 | GHSA-RQ6G-PX6M-C248 | openclaw |
| entry-00149 | GHSA-V773-R54F-Q32W | openclaw |
| entry-00151 | GHSA-9379-MWVR-7WXX | NVIDIA NeMo |
| entry-00154 | GHSA-9379-MWVR-7WXX | NVIDIA NeMo |
| entry-00155 | GHSA-9379-MWVR-7WXX | NVIDIA NeMo |
| entry-00156 | GHSA-9379-MWVR-7WXX | NVIDIA NeMo |
| entry-00157 | GHSA-9379-MWVR-7WXX | NVIDIA NeMo |
| entry-00158 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00159 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00160 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00161 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00162 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00163 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00164 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00165 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00166 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00167 | GHSA-H9G4-589H-68XV | openclaw |
| entry-00168 | GHSA-W235-X559-36MG | openclaw |
| entry-00174 | GHSA-JJPJ-P2WH-QF23 | n8n |
| entry-00175 | GHSA-JJPJ-P2WH-QF23 | n8n |
| entry-00177 | GHSA-VPCF-GVG4-6QWR | n8n |
| entry-00178 | GHSA-VPCF-GVG4-6QWR | n8n |
| entry-00179 | GHSA-VPCF-GVG4-6QWR | n8n |
| entry-00180 | GHSA-VPCF-GVG4-6QWR | n8n |
| entry-00181 | GHSA-VPCF-GVG4-6QWR | n8n |
| entry-00182 | GHSA-VPCF-GVG4-6QWR | n8n |
| entry-00188 | GHSA-VPJ2-69HF-RPPW | OpenClaw |
| entry-00189 | GHSA-2P9H-RQJW-GM92 | n8n |
| entry-00190 | GHSA-2P9H-RQJW-GM92 | n8n |
| entry-00191 | GHSA-2P9H-RQJW-GM92 | n8n |
| entry-00193 | GHSA-X82F-27X3-Q89C | openclaw |
| entry-00194 | GHSA-7XMQ-G46G-F8PV | openclaw |
| entry-00196 | GHSA-7XMQ-G46G-F8PV | openclaw |
| entry-00200 | GHSA-JR6X-2Q95-FH2G | openclaw |
| entry-00201 | GHSA-JR6X-2Q95-FH2G | openclaw |
| entry-00202 | GHSA-JR6X-2Q95-FH2G | openclaw |
| entry-00207 | GHSA-GV46-4XFQ-JV58 | openclaw |
| entry-00208 | GHSA-5V6X-RFC3-7QFR | openclaw |
| entry-00210 | GHSA-F7WW-2725-QVW2 | openclaw |
| entry-00211 | GHSA-F7WW-2725-QVW2 | openclaw |
| entry-00214 | GHSA-R65X-2HQR-J5HF | openclaw |
| entry-00215 | GHSA-9F72-QCPW-2HXC | openclaw/openclaw |
| entry-00216 | GHSA-JV6R-27WW-4GW4 | openclaw |
| entry-00217 | GHSA-JV6R-27WW-4GW4 | openclaw |
| entry-00218 | GHSA-JV6R-27WW-4GW4 | openclaw |
| entry-00222 | GHSA-25GX-X37C-7PPH | openclaw |
| entry-00225 | GHSA-V865-P3GQ-HW6M | openclaw |
| entry-00226 | GHSA-R54R-WMMQ-MH84 | openclaw |
| entry-00227 | GHSA-474H-PRJG-MMW3 | openclaw |
| entry-00228 | GHSA-474H-PRJG-MMW3 | openclaw |
| entry-00229 | GHSA-H9XM-J4QG-FVPG | openclaw |
| entry-00230 | GHSA-H9XM-J4QG-FVPG | openclaw |
| entry-00232 | GHSA-3C6H-G97W-FG78 | openclaw |
| entry-00233 | GHSA-9P38-94JF-HGJJ | openclaw |
| entry-00240 | GHSA-G75X-8QQM-2VXP | openclaw |
| entry-00245 | GHSA-7FF8-XJH3-MGH6 | openclaw |
| entry-00246 | GHSA-7FF8-XJH3-MGH6 | openclaw |
| entry-00247 | GHSA-7FF8-XJH3-MGH6 | openclaw |
| entry-00248 | GHSA-7FF8-XJH3-MGH6 | openclaw |
| entry-00249 | GHSA-JJ82-76V6-933R | openclaw |
| entry-00250 | GHSA-JJ82-76V6-933R | openclaw |
| entry-00251 | GHSA-2CH6-X3G4-7759 | openclaw |
| entry-00252 | GHSA-2CH6-X3G4-7759 | openclaw |
| entry-00256 | GHSA-VVJH-F6P9-5VCF | openclaw |
| entry-00257 | GHSA-VVJH-F6P9-5VCF | openclaw |
| entry-00261 | GHSA-WVHQ-WP8G-C7VQ | Flowise |
| entry-00262 | GHSA-J8G8-J7FC-43V6 | FlowiseAI/Flowise |
| entry-00263 | GHSA-J8G8-J7FC-43V6 | FlowiseAI/Flowise |
| entry-00264 | GHSA-5F53-522J-J454 | FlowiseAI/Flowise |
| entry-00265 | GHSA-5F53-522J-J454 | FlowiseAI/Flowise |
| entry-00266 | GHSA-5F53-522J-J454 | FlowiseAI/Flowise |
| entry-00267 | GHSA-5F53-522J-J454 | FlowiseAI/Flowise |
| entry-00268 | GHSA-MQ4R-H2GH-QV7X | FlowiseAI/Flowise |
| entry-00269 | GHSA-CWC3-P92J-G7QM | Flowise |
| entry-00270 | GHSA-CWC3-P92J-G7QM | Flowise |
| entry-00271 | GHSA-CCJ6-79J6-CQ5Q | WeKnora |
| entry-00272 | GHSA-CCJ6-79J6-CQ5Q | WeKnora |
| entry-00273 | GHSA-CCJ6-79J6-CQ5Q | WeKnora |
| entry-00274 | GHSA-CCJ6-79J6-CQ5Q | WeKnora |
| entry-00276 | GHSA-H6GW-8F77-MMMP | WeKnora |
| entry-00278 | GHSA-FVCW-9W9R-PXC7 | Flowise |
| entry-00283 | GHSA-GP3Q-WPQ4-5C5H | openclaw |
| entry-00284 | GHSA-GP3Q-WPQ4-5C5H | openclaw |
| entry-00285 | GHSA-GP3Q-WPQ4-5C5H | openclaw |
| entry-00286 | GHSA-XW77-45GV-P728 | openclaw |
| entry-00287 | GHSA-XW77-45GV-P728 | openclaw |
| entry-00288 | GHSA-XW77-45GV-P728 | openclaw |
| entry-00289 | GHSA-XW77-45GV-P728 | openclaw |
| entry-00291 | GHSA-4JPW-HJ22-2XMC | openclaw |
| entry-00292 | GHSA-4W7M-58CG-CMFF | openclaw |
| entry-00293 | GHSA-4W7M-58CG-CMFF | openclaw |
| entry-00294 | GHSA-XF99-J42Q-5W5P | openclaw |
| entry-00295 | GHSA-RW39-5899-8MXP | openclaw |
| entry-00296 | GHSA-QC36-X95H-7J53 | openclaw |
| entry-00297 | GHSA-R7VR-GR74-94P8 | openclaw |
| entry-00298 | GHSA-R7VR-GR74-94P8 | openclaw |
| entry-00299 | GHSA-R7VR-GR74-94P8 | openclaw |
| entry-00300 | GHSA-R7VR-GR74-94P8 | openclaw |
| entry-00301 | GHSA-MJ4P-RC52-M843 | openclaw |
| entry-00302 | GHSA-MJ4P-RC52-M843 | openclaw |
| entry-00304 | GHSA-WCXR-59V9-RXR8 | openclaw |
| entry-00305 | GHSA-WCXR-59V9-RXR8 | openclaw |
| entry-00306 | GHSA-WCXR-59V9-RXR8 | openclaw |
| entry-00307 | GHSA-WCXR-59V9-RXR8 | openclaw |
| entry-00308 | GHSA-RQPP-RJJ8-7WV8 | openclaw |
| entry-00309 | GHSA-RQPP-RJJ8-7WV8 | openclaw |
| entry-00311 | GHSA-5H2M-4Q8J-PQPJ | fastmcp |
| entry-00312 | GHSA-63F5-HHC7-CX6P | openclaw |
| entry-00313 | GHSA-4M3H-WP5W-5HQH | apache/airflow |
| entry-00314 | GHSA-8X34-9Q3V-H7G8 | apache/airflow |
| entry-00315 | GHSA-8X34-9Q3V-H7G8 | apache/airflow |
| entry-00316 | GHSA-8X34-9Q3V-H7G8 | apache/airflow |
| entry-00318 | GHSA-JQPF-VJ28-9V7R | openclaw |
| entry-00319 | GHSA-JM6W-M3J8-898G | nltk |
| entry-00321 | GHSA-G2J9-7RJ2-GM6C | langflow |
| entry-00322 | GHSA-PFV5-RPCW-X34X | openclaw |
| entry-00323 | GHSA-PFV5-RPCW-X34X | openclaw |
| entry-00324 | GHSA-7GRX-3XCX-2XV5 | langflow |
| entry-00327 | GHSA-WR92-6W3G-2HWC | openclaw |
| entry-00328 | GHSA-QWMF-95R9-GX9X | openclaw |
| entry-00329 | GHSA-QWMF-95R9-GX9X | openclaw |
| entry-00330 | GHSA-QWMF-95R9-GX9X | openclaw |
| entry-00331 | GHSA-QWMF-95R9-GX9X | openclaw |
| entry-00332 | GHSA-69FQ-XP46-6X23 | aquasecurity/trivy |
| entry-00333 | GHSA-69FQ-XP46-6X23 | aquasecurity/trivy |
| entry-00334 | GHSA-69FQ-XP46-6X23 | aquasecurity/trivy |
| entry-00335 | GHSA-V7V2-M736-CF3C | NVIDIA NeMo Framework |
| entry-00336 | GHSA-V7V2-M736-CF3C | NVIDIA NeMo Framework |
| entry-00337 | GHSA-V7V2-M736-CF3C | NVIDIA NeMo Framework |
| entry-00339 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo |
| entry-00342 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo |
| entry-00343 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo |
| entry-00344 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo |
| entry-00345 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo |
| entry-00346 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo |
| entry-00347 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo |
| entry-00357 | GHSA-FXCW-H3QJ-8M8P | n8n |
| entry-00359 | GHSA-MXRG-77HM-89HV | n8n |
| entry-00360 | GHSA-MXRG-77HM-89HV | n8n |
| entry-00361 | GHSA-MXRG-77HM-89HV | n8n |
| entry-00362 | GHSA-WQ58-2PVG-5H4F | openclaw |
| entry-00363 | GHSA-WQ58-2PVG-5H4F | openclaw |
| entry-00365 | GHSA-65H8-27JH-Q8WV | openclaw |
| entry-00368 | GHSA-3W6X-GV34-MQPF | openclaw |
| entry-00369 | GHSA-3W6X-GV34-MQPF | openclaw |
| entry-00370 | GHSA-3W6X-GV34-MQPF | openclaw |
| entry-00371 | GHSA-HF68-49FM-59CQ | OpenClaw Gateway |
| entry-00372 | GHSA-8C4J-F57C-35CF | langflow |
| entry-00373 | GHSA-8C4J-F57C-35CF | langflow |
| entry-00374 | GHSA-8C4J-F57C-35CF | langflow |
| entry-00375 | GHSA-9P93-7J67-5PC2 | openclaw |
| entry-00378 | GHSA-QM2M-28PF-HGJW | openclaw |
| entry-00379 | GHSA-FQW4-MPH7-2VR8 | openclaw |
| entry-00380 | GHSA-FQW4-MPH7-2VR8 | openclaw |
| entry-00381 | GHSA-M3MH-3MPG-37HW | openclaw |
| entry-00382 | GHSA-M3MH-3MPG-37HW | openclaw |
| entry-00383 | GHSA-XP9R-PRPG-373R | openclaw |
| entry-00384 | GHSA-XP9R-PRPG-373R | openclaw |
| entry-00385 | GHSA-F275-5H5C-5WG5 | openclaw |
| entry-00387 | GHSA-94PW-C6M8-P9P9 | openclaw |
| entry-00388 | GHSA-94PW-C6M8-P9P9 | openclaw |
| entry-00393 | GHSA-3CW3-5VXW-G2H3 | openclaw |
| entry-00395 | GHSA-VV7Q-7JX5-F767 | fastmcp |
| entry-00396 | GHSA-98HH-7GHG-X6RQ | openclaw |
| entry-00397 | GHSA-98HH-7GHG-X6RQ | openclaw |
| entry-00398 | GHSA-5H2W-QMFP-GGP6 | openclaw |
| entry-00399 | GHSA-5H2W-QMFP-GGP6 | openclaw |
| entry-00400 | GHSA-5R8F-96GM-5J6G | openclaw |
| entry-00401 | GHSA-7429-HXCV-268M | open-webui |
| entry-00402 | GHSA-P4X4-2R7F-WJXG | openclaw |
| entry-00403 | GHSA-P4X4-2R7F-WJXG | openclaw |
| entry-00404 | GHSA-P4X4-2R7F-WJXG | openclaw |
| entry-00405 | GHSA-P4X4-2R7F-WJXG | openclaw |
| entry-00406 | GHSA-G5CG-8X5W-7JPM | openclaw |
| entry-00407 | GHSA-V3QC-WRWX-J3PW | openclaw |
| entry-00408 | GHSA-V3QC-WRWX-J3PW | openclaw |
| entry-00411 | GHSA-GJM7-HW8F-73RQ | openclaw |
| entry-00412 | GHSA-GJM7-HW8F-73RQ | openclaw |
| entry-00413 | GHSA-7QHF-V65M-G5F3 | mlflow |
| entry-00414 | GHSA-7QHF-V65M-G5F3 | mlflow |
| entry-00415 | GHSA-7QHF-V65M-G5F3 | mlflow |
| entry-00416 | GHSA-7QHF-V65M-G5F3 | mlflow |
| entry-00419 | GHSA-JJHC-V7C2-5HH6 | litellm |
| entry-00424 | GHSA-5WJ5-87VQ-39XM | openclaw |
| entry-00431 | GHSA-RG7C-G689-FR3X | google/adk-python |
| entry-00432 | GHSA-RG7C-G689-FR3X | google/adk-python |
| entry-00435 | GHSA-RG7C-G689-FR3X | google/adk-python |
| entry-00437 | GHSA-265W-RF2W-CJH4 | paperclipai/paperclip |
| entry-00446 | GHSA-VR7G-88FQ-VHQ3 | paperclipai/paperclip |
| entry-00450 | GHSA-6XG4-82HV-CP6F | openclaw |
| entry-00451 | GHSA-6XG4-82HV-CP6F | openclaw |
| entry-00458 | GHSA-G374-MGGX-P6XC | openclaw |
| entry-00459 | GHSA-GG9V-MGCP-V6M7 | openclaw |
| entry-00462 | GHSA-Q56X-G2FJ-4RJ6 | onnx |
| entry-00463 | GHSA-Q56X-G2FJ-4RJ6 | onnx |
| entry-00464 | GHSA-Q2HG-643C-GW8H | Apache Airflow |
| entry-00465 | GHSA-48M6-CH88-55MJ | FlowiseAI/Flowise |
| entry-00466 | GHSA-48M6-CH88-55MJ | FlowiseAI/Flowise |
| entry-00469 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise |
| entry-00471 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise |
| entry-00474 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise |
| entry-00475 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise |
| entry-00477 | GHSA-6F7G-V4PP-R667 | FlowiseAI/Flowise |
| entry-00478 | GHSA-6F7G-V4PP-R667 | FlowiseAI/Flowise |
| entry-00481 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise |
| entry-00483 | GHSA-3XX2-MQJM-HG9X | paperclipai/paperclip |
| entry-00484 | GHSA-3XX2-MQJM-HG9X | paperclipai/paperclip |
| entry-00485 | GHSA-3XX2-MQJM-HG9X | paperclipai/paperclip |
| entry-00486 | GHSA-3XX2-MQJM-HG9X | paperclipai/paperclip |
| entry-00487 | GHSA-3XX2-MQJM-HG9X | paperclipai/paperclip |
| entry-00488 | GHSA-3XX2-MQJM-HG9X | paperclipai/paperclip |
| entry-00493 | GHSA-82QX-6VJ7-P8M2 | openclaw |
| entry-00494 | GHSA-82QX-6VJ7-P8M2 | openclaw |
| entry-00495 | GHSA-82QX-6VJ7-P8M2 | openclaw |
| entry-00496 | GHSA-736R-JWJ6-4W23 | openclaw |
| entry-00497 | GHSA-736R-JWJ6-4W23 | openclaw |
| entry-00498 | GHSA-525J-HQQ2-66R4 | openclaw |
| entry-00499 | GHSA-525J-HQQ2-66R4 | openclaw |
| entry-00500 | GHSA-7JP6-R74R-995Q | openclaw |
| entry-00501 | GHSA-XH72-V6V9-MWHC | openclaw |
| entry-00502 | GHSA-XH72-V6V9-MWHC | openclaw |
| entry-00503 | GHSA-XH72-V6V9-MWHC | openclaw |
| entry-00504 | GHSA-XH72-V6V9-MWHC | openclaw |
| entry-00505 | GHSA-2CQ5-MF3V-MX44 | openclaw |
| entry-00506 | GHSA-75HX-XJ24-MQRW | n8n-mcp |
| entry-00507 | GHSA-75HX-XJ24-MQRW | n8n-mcp |
| entry-00510 | GHSA-VJQW-W5JR-G9W5 | openclaw |
| entry-00513 | GHSA-Q2QC-744P-66R2 | openclaw |

## Removed Entries

| entry_id | report_id | project | verify |
| --- | --- | --- | --- |
| entry-00061 | GHSA-X39M-3393-3QP4 | FlowiseAI/Flowise | 0 |
| entry-00062 | GHSA-C6XV-RCVW-V685 | open-webui | 0 |
| entry-00063 | GHSA-V5W9-PRXF-W882 | Flowise (FlowiseAI/Flowise) | 0 |
| entry-00064 | GHSA-V5W9-PRXF-W882 | Flowise (FlowiseAI/Flowise) | 0 |
| entry-00073 | GHSA-C5CP-VX83-JHQX | langflow | 0 |
| entry-00074 | GHSA-F6MR-38G8-39RG | ollama | 0 |
| entry-00075 | GHSA-F6MR-38G8-39RG | ollama | 0 |
| entry-00077 | GHSA-F6MR-38G8-39RG | ollama | 0 |
| entry-00079 | GHSA-F6MR-38G8-39RG | ollama | 0 |
| entry-00080 | GHSA-78H3-63C4-5FQC | Tencent/WeKnora | 0 |
| entry-00081 | GHSA-78H3-63C4-5FQC | Tencent/WeKnora | 0 |
| entry-00090 | GHSA-J4P8-H8MH-RH8Q | n8n | 0 |
| entry-00091 | GHSA-J4P8-H8MH-RH8Q | n8n | 0 |
| entry-00099 | GHSA-5XRP-6693-JJX9 | n8n | 0 |
| entry-00100 | GHSA-5XRP-6693-JJX9 | n8n | 0 |
| entry-00103 | GHSA-825Q-W924-XHGX | n8n | 0 |
| entry-00104 | GHSA-GFVG-QV54-R4PC | n8n | 0 |
| entry-00105 | GHSA-GFVG-QV54-R4PC | n8n | 0 |
| entry-00106 | GHSA-GFVG-QV54-R4PC | n8n | 0 |
| entry-00112 | GHSA-HV53-3329-VMRM | n8n | 0 |
| entry-00116 | GHSA-G55J-C2V4-PJCG | openclaw | 0 |
| entry-00122 | GHSA-64QX-VPXX-MVQF | openclaw | 0 |
| entry-00130 | GHSA-MP5H-M6QJ-6292 | openclaw | 0 |
| entry-00133 | GHSA-MP5H-M6QJ-6292 | openclaw | 0 |
| entry-00135 | GHSA-3M3Q-X3GJ-F79X | openclaw | 0 |
| entry-00137 | GHSA-3M3Q-X3GJ-F79X | openclaw | 0 |
| entry-00140 | GHSA-R5H9-VJQC-HQ3R | @openclaw/nextcloud-talk | 0 |
| entry-00141 | GHSA-R5H9-VJQC-HQ3R | @openclaw/nextcloud-talk | 0 |
| entry-00143 | GHSA-4RJ2-GPMH-QQ5X | openclaw | 0 |
| entry-00144 | GHSA-4RJ2-GPMH-QQ5X | openclaw | 0 |
| entry-00145 | GHSA-4HG8-92X6-H2F3 | openclaw | 0 |
| entry-00146 | GHSA-H3F9-MJWJ-W476 | openclaw | 0 |
| entry-00150 | GHSA-9379-MWVR-7WXX | NVIDIA NeMo | 0 |
| entry-00152 | GHSA-9379-MWVR-7WXX | NVIDIA NeMo | 0 |
| entry-00153 | GHSA-9379-MWVR-7WXX | NVIDIA NeMo | 0 |
| entry-00169 | GHSA-W235-X559-36MG | openclaw | 0 |
| entry-00170 | GHSA-W235-X559-36MG | openclaw | 0 |
| entry-00171 | GHSA-GQ3W-7JJ3-X7GR | mlflow | 0 |
| entry-00172 | GHSA-75G8-RV7V-32F7 | n8n | 0 |
| entry-00173 | GHSA-75G8-RV7V-32F7 | n8n | 0 |
| entry-00176 | GHSA-MMGG-M5J7-F83H | n8n | 0 |
| entry-00183 | GHSA-WXX7-MCGF-J869 | n8n | 0 |
| entry-00184 | GHSA-WXX7-MCGF-J869 | n8n | 0 |
| entry-00185 | GHSA-X2MW-7J39-93XQ | n8n | 0 |
| entry-00186 | GHSA-X2MW-7J39-93XQ | n8n | 0 |
| entry-00187 | GHSA-VPJ2-69HF-RPPW | OpenClaw | 0 |
| entry-00192 | GHSA-X82F-27X3-Q89C | openclaw | 0 |
| entry-00195 | GHSA-7XMQ-G46G-F8PV | openclaw | 0 |
| entry-00197 | GHSA-7XMQ-G46G-F8PV | openclaw | 0 |
| entry-00198 | GHSA-Q399-23R3-HFX4 | openclaw | 0 |
| entry-00199 | GHSA-JR6X-2Q95-FH2G | openclaw | 0 |
| entry-00209 | GHSA-5V6X-RFC3-7QFR | openclaw | 0 |
| entry-00212 | GHSA-QJ22-XQJR-V83V | openclaw | 0 |
| entry-00213 | GHSA-R65X-2HQR-J5HF | openclaw | 0 |
| entry-00219 | GHSA-MWXV-35WR-4VVJ | openclaw | 0 |
| entry-00220 | GHSA-MWXV-35WR-4VVJ | openclaw | 0 |
| entry-00221 | GHSA-MWXV-35WR-4VVJ | openclaw | 0 |
| entry-00223 | GHSA-25GX-X37C-7PPH | openclaw | 0 |
| entry-00224 | GHSA-V865-P3GQ-HW6M | openclaw | 0 |
| entry-00231 | GHSA-PJ5X-38RW-6FPH | openclaw | 0 |
| entry-00241 | GHSA-W7J5-J98M-W679 | openclaw | 0 |
| entry-00242 | GHSA-W7J5-J98M-W679 | openclaw | 0 |
| entry-00243 | GHSA-W7J5-J98M-W679 | openclaw | 0 |
| entry-00244 | GHSA-W7J5-J98M-W679 | openclaw | 0 |
| entry-00253 | GHSA-X2FF-J5C2-GGPR | openclaw | 0 |
| entry-00254 | GHSA-X2FF-J5C2-GGPR | openclaw | 0 |
| entry-00255 | GHSA-X2FF-J5C2-GGPR | openclaw | 0 |
| entry-00258 | GHSA-WVHQ-WP8G-C7VQ | Flowise | 0 |
| entry-00259 | GHSA-WVHQ-WP8G-C7VQ | Flowise | 0 |
| entry-00260 | GHSA-WVHQ-WP8G-C7VQ | Flowise | 0 |
| entry-00275 | GHSA-2F4C-VRJQ-RCGV | WeKnora | 0 |
| entry-00277 | GHSA-FVCW-9W9R-PXC7 | Flowise | 0 |
| entry-00290 | GHSA-QCC4-P59M-P54M | openclaw | 0 |
| entry-00303 | GHSA-VMHQ-CQM9-6P7Q | openclaw | 0 |
| entry-00310 | GHSA-5H2M-4Q8J-PQPJ | fastmcp | 0 |
| entry-00317 | GHSA-RF6X-R45M-XV3W | Langflow | 0 |
| entry-00320 | GHSA-G2J9-7RJ2-GM6C | langflow | 0 |
| entry-00325 | GHSA-PH9W-R52H-28P7 | langflow-ai/langflow | 0 |
| entry-00326 | GHSA-PH9W-R52H-28P7 | langflow-ai/langflow | 0 |
| entry-00338 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo | 0 |
| entry-00340 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo | 0 |
| entry-00341 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo | 0 |
| entry-00348 | GHSA-M4JW-WGMF-889X | NVIDIA/NeMo | 0 |
| entry-00349 | GHSA-58QR-RCGV-642V | n8n | 0 |
| entry-00350 | GHSA-58QR-RCGV-642V | n8n | 0 |
| entry-00351 | GHSA-XVH5-5QG4-X9QP | n8n | 0 |
| entry-00352 | GHSA-XVH5-5QG4-X9QP | n8n | 0 |
| entry-00355 | GHSA-C545-X2RH-82FC | n8n | 0 |
| entry-00356 | GHSA-FXCW-H3QJ-8M8P | n8n | 0 |
| entry-00358 | GHSA-98C2-4CR3-4JC3 | n8n | 0 |
| entry-00364 | GHSA-65H8-27JH-Q8WV | openclaw | 0 |
| entry-00376 | GHSA-JJP7-G2JW-WH3J | open-webui | 0 |
| entry-00377 | GHSA-9HJH-FR4F-GXC4 | openclaw | 0 |
| entry-00386 | GHSA-F275-5H5C-5WG5 | openclaw | 0 |
| entry-00389 | GHSA-RVHJ-8CHJ-8V3C | MLflow | 0 |
| entry-00390 | GHSA-RVHJ-8CHJ-8V3C | MLflow | 0 |
| entry-00391 | GHSA-VV7Q-7JX5-F767 | fastmcp | 0 |
| entry-00392 | GHSA-VV7Q-7JX5-F767 | fastmcp | 0 |
| entry-00394 | GHSA-VV7Q-7JX5-F767 | fastmcp | 0 |
| entry-00409 | GHSA-XJ9W-5R6Q-X6V4 | openclaw | 0 |
| entry-00410 | GHSA-9P3R-HH9G-5CMG | openclaw | 0 |
| entry-00417 | GHSA-H5HG-H7RR-GPF3 | openclaw | 0 |
| entry-00418 | GHSA-H5HG-H7RR-GPF3 | openclaw | 0 |
| entry-00429 | GHSA-4JPM-CGX2-8H37 | flowise | 0 |
| entry-00430 | GHSA-RG7C-G689-FR3X | google/adk-python | 0 |
| entry-00433 | GHSA-RG7C-G689-FR3X | google/adk-python | 0 |
| entry-00434 | GHSA-RG7C-G689-FR3X | google/adk-python | 0 |
| entry-00436 | GHSA-F6HC-C5JR-878P | Flowise (FlowiseAI/Flowise) | 0 |
| entry-00438 | GHSA-XFQJ-R5QW-8G4J | paperclip | 0 |
| entry-00439 | GHSA-XFQJ-R5QW-8G4J | paperclip | 0 |
| entry-00440 | GHSA-XFQJ-R5QW-8G4J | paperclip | 0 |
| entry-00441 | GHSA-XFQJ-R5QW-8G4J | paperclip | 0 |
| entry-00442 | GHSA-XFQJ-R5QW-8G4J | paperclip | 0 |
| entry-00443 | GHSA-XFQJ-R5QW-8G4J | paperclip | 0 |
| entry-00447 | GHSA-47WQ-CJ9Q-WPMP | paperclip | 0 |
| entry-00448 | GHSA-47WQ-CJ9Q-WPMP | paperclip | 0 |
| entry-00449 | GHSA-47WQ-CJ9Q-WPMP | paperclip | 0 |
| entry-00467 | GHSA-XHMJ-RG95-44HV | Flowise | 0 |
| entry-00468 | GHSA-XHMJ-RG95-44HV | Flowise | 0 |
| entry-00470 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise | 0 |
| entry-00472 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise | 0 |
| entry-00473 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise | 0 |
| entry-00476 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise | 0 |
| entry-00479 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise | 0 |
| entry-00480 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise | 0 |
| entry-00482 | GHSA-2X8M-83VC-6WV4 | FlowiseAI/Flowise | 0 |
| entry-00489 | GHSA-3PRP-9GF7-4RXX | FlowiseAI/Flowise | 0 |
| entry-00490 | GHSA-3PRP-9GF7-4RXX | FlowiseAI/Flowise | 0 |
| entry-00491 | GHSA-3PRP-9GF7-4RXX | FlowiseAI/Flowise | 0 |
| entry-00492 | GHSA-5FW2-MWHH-9947 | FlowiseAI/Flowise | 0 |
| entry-00508 | GHSA-75HX-XJ24-MQRW | n8n-mcp | 0 |
| entry-00509 | GHSA-VJQW-W5JR-G9W5 | openclaw | 0 |
| entry-00511 | GHSA-6CQR-8CFR-67F8 | n8n | 0 |
| entry-00512 | GHSA-6CQR-8CFR-67F8 | n8n | 0 |

## Machine-Readable Summary

```text
records/cleaned_verify1_20260608_summary.json
```
