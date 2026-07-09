<p align="center">
  <img src="./img/wukong_logo.png" alt="VulnGym" height="60">
</p>

<h4 align="center">
    <p>
        <a href="./README_zh.md">中文</a> |
        <a href="#">English</a>
    </p>
</h4>

<p align="center">
  <a href="https://github.com/Tencent/VulnGym/stargazers"><img alt="GitHub Stars" src="https://img.shields.io/github/stars/Tencent/VulnGym?color=gold"></a>
  <a href="https://github.com/Tencent/VulnGym/network/members"><img alt="GitHub Forks" src="https://img.shields.io/github/forks/Tencent/VulnGym?color=gold"></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-CC--BY--4.0-blue.svg"></a>
</p>

<p align="center">
  <b>A Real-World, Project-Level Vulnerability Benchmark for White-Box Vulnerability-Hunting Agents</b>
</p>

<p align="center">
  <a href="https://github.com/Tencent/VulnGym"><img src="https://img.shields.io/badge/⭐-Give VulnGym a Star-yellow?style=flat&logo=github" alt="Give VulnGym a Star"></a>
  <a href="https://huggingface.co/datasets/tencent/VulnGym"><img src="https://img.shields.io/badge/🤗%20HuggingFace-Dataset-yellow?style=flat" alt="HuggingFace Dataset"></a>
</p>

**VulnGym** is a project-level benchmark for white-box vulnerability-hunting agents, designed to evaluate an agent's vulnerability detection capabilities within **real-world engineering contexts**, with **verifiable vulnerability trigger paths and code-semantic evidence chains**.

**Three core design principles:**
- **🏗️ Real project-level evaluation units** — every sample is bound to a specific vulnerable commit of a real repository, evaluating an agent's ability to discover and locate vulnerabilities inside real multi-file, multi-module engineering projects.
- **🧠 Comprehensive vulnerability-type coverage** — the benchmark covers both business-logic defects that demand cross-module code-semantic reasoning (e.g., authorization bypass, broken authentication) and traditional security flaws (e.g., injection, path traversal), providing a comprehensive assessment of an agent's ability to discover diverse vulnerability classes.
- **✅ Verifiable vulnerability paths** — each sample ships with a human-reviewed **reachable entry point** (`entry_point`), **critical operation** (`critical_operation`), and **cross-module reasoning chain** (`trace`), enabling reproducible, explainable, and deterministic evaluation.

---

## 📢 What's New
- **2026-07-09** — 🧹 cleaned fork: rebuilt from upstream v0.1.4 and retained only human-audited `verify = 1` entries, reducing the dataset to **178 reports / 393 entries**; partially verified advisories were re-aggregated to the retained `entry_ids` and `num_entries`.
- **2026-06-26** — 🔧 v0.1.4 data refresh: human-audited entries grew from **350 → 393 / 408 (96.3 %)**, covering **178 / 184 advisories (96.7 %)**. This release updates only human-audit status flags; row counts, schema, `desc` coverage, and vulnerability-type distribution are unchanged.
- **2026-06-18** — 🔧 v0.1.3 data refresh: human-audited entries grew from **274 → 350 / 408 (85.8 %)**, covering **163 / 184 advisories (88.6 %)**. In addition, a `desc` field was added to the `entry_point` / `critical_operation` / `trace` nodes of 400 entries, giving a natural-language explanation of each node's role in the vulnerability chain.
- **2026-05-31** — 🔧 v0.1.2 data refresh: human-audited entries grew from **113 → 274 / 408 (67.2 %)**, covering **137 / 184 advisories (74.5 %)**. Additionally, `entry_point` / `critical_operation` / `trace` annotations were refined on 80 entries for improved accuracy.
- **2026-05-17** — 🔧 v0.1.1 data refresh: added a `verify` field on every entry to mark human-audit status; **113 / 408 entries** (covering **61 / 184 advisories**) are now human-verified. Selected `entry_point` / `critical_operation` / `trace` values were also refined.
- **2026-05-15** — 🎉 VulnGym v0.1.0 officially open-sourced!



## Table of Contents

- [🔍 Why VulnGym](#-why-vulngym)
- [✨ Dataset overview](#-dataset-overview)
- [📈 Baseline evaluation results](#-baseline-evaluation-results)
- [📦 Repository layout](#-repository-layout)
- [🚀 Quick start](#-quick-start)
- [📊 Evaluating your tool](#-evaluating-your-tool)
- [📖 Citation](#-citation)
- [🤝 Contribution Guide](#-contribution-guide)
- [🙏 Acknowledgements](#-acknowledgements)
- [📄 License](#-license)

---

## 🔍 Why VulnGym

Existing vulnerability benchmarks have the following limitations when
evaluating the real-world vulnerability-hunting capabilities of AI agents:

| Limitation | Manifestation |
|---|---|
| **Insufficient evaluation granularity** | Most benchmarks use functions or diff snippets as the evaluation unit, failing to reflect an agent's ability to locate vulnerabilities within complete engineering projects |
| **Narrow vulnerability types** | Over-emphasis on pattern-matchable CWE flaws such as SQL injection and buffer overflow, with little coverage of categories requiring deep contextual reasoning |
| **Coarse-grained ground truth** | Typically binary labels (vulnerable / not vulnerable) or patch diffs, unable to precisely verify whether the agent locates the correct entry point and defect site |


## ✨ Dataset overview

This is the **v0.1.4 cleaned-verify1 release** of VulnGym. Data is provided
as four JSONL files under the `data/` directory:

- `reports.jsonl` — aggregated records at the GitHub Advisory granularity
- `entries.jsonl` - verified pair-level records at the reachable entry point granularity
- `entry_points.jsonl` - deduplicated reachable-entry anchors
- `critical_operations.jsonl` - deduplicated critical-operation anchors

Each record contains `repo_url` and `commit`, allowing you to check out the
full vulnerable source tree for the corresponding version.

### Data scale

| Metric | Value |
|---|---|
| Advisories (reports) | **178** |
| Reachable entry points (entries) | **393** |
| Deduplicated entry-point anchors | **350** |
| Deduplicated critical-operation anchors | **356** |
| Distinct projects | 38 |
| Distinct repositories | 23 |
| Human-audited entries (`verify = 1`) | **393 / 393 (100.0 %)** |
| Human-audited advisories (≥ 1 verified entry) | **178 / 178 (100.0 %)** |

### Human audit status

Starting in v0.1.1, every row in `entries.jsonl` carries a `verify` field
(`int`, `0` or `1`).

This cleaned fork has already filtered `data/entries.jsonl` to rows with
`verify == 1`. `data/reports.jsonl` has also been re-aggregated so that
`entry_ids` and `num_entries` refer only to retained verified entries. Upstream
v0.1.4 rows with `verify == 0` are not present in this branch's data files;
retained and removed rows are recorded in `records/cleaned_verify1_20260709.md`
and `records/cleaned_verify1_20260709_summary.json`.

Before filtering, upstream v0.1.4 contained **184 reports /
408 entries**, with **393**
verified entries across **178** reports. After
filtering, this branch retains **178 reports /
393 entries**. The **4**
originally partially verified reports have had unverified entries removed and
their aggregate fields recomputed.

### Vulnerability type distribution

Every entry carries a two-level classification: `vuln_category_l1`
(coarse type) and `vuln_category_l2` (fine-grained sub-type). In this
cleaned subset, **131 / 178 (73.6%)** advisories are business-logic
vulnerabilities; the remaining **47 / 178 (26.4%)** cover traditional vulnerability
types. Full data model and field definitions are in [`SCHEMA.md`](SCHEMA.md).

> Note: one advisory may map to multiple entries — the counts below
> are by **advisory (vulnerability)**, not by entry.

**Business-logic advisories (131 / 178, 73.6%) — `vuln_category_l2` breakdown:**

| Sub-category | Advisories | % of BL |
| --- | --- | --- |
| BL-AUTHZ-BROKEN | 31 | 23.7% |
| BL-AUTHZ-MISSING | 23 | 17.6% |
| BL-AGENT-CAPABILITY | 20 | 15.3% |
| BL-PRIV-ESC | 13 | 9.9% |
| BL-AUTH-BYPASS | 11 | 8.4% |
| BL-ORIGIN-INTEGRITY | 8 | 6.1% |
| BL-WORKFLOW-VIOLATION | 7 | 5.3% |
| BL-INSECURE-DEFAULT | 6 | 4.6% |
| BL-RACE-LOGIC | 4 | 3.1% |
| BL-MULTI-TENANT | 3 | 2.3% |
| BL-MASS-ASSIGNMENT | 3 | 2.3% |
| BL-TRUST-BOUNDARY | 2 | 1.5% |

<br>

**Traditional vulnerability advisories (47 / 178, 26.4%) — top `vuln_category_l1`:**

| Category | Advisories | % of Trad. |
| --- | --- | --- |
| Path Traversal / File ops | 9 | 19.1% |
| Command Injection | 8 | 17.0% |
| Code Injection | 7 | 14.9% |
| XSS | 4 | 8.5% |
| SSRF | 4 | 8.5% |
| Deserialization | 2 | 4.3% |
| Sandbox Escape | 2 | 4.3% |
| Authentication Bypass | 2 | 4.3% |
| 注入 | 1 | 2.1% |
| Template Injection | 1 | 2.1% |
| Authorization Bypass | 1 | 2.1% |
| Injection | 1 | 2.1% |
| Supply Chain | 1 | 2.1% |
| Injection / Deserialization | 1 | 2.1% |
| 信息泄露 | 1 | 2.1% |
| 注入攻击 | 1 | 2.1% |
| Prototype Pollution | 1 | 2.1% |

> Future releases will continue expanding vulnerability categories and project coverage.

## 📈 Baseline evaluation results

> 🚧 **Coming soon** — We are systematically evaluating mainstream tools and AI agents. Results will be published alongside the technical report.


## 📦 Repository layout

```
VulnGym/
├── README.md                    # English version
├── README_zh.md                 # 中文版
├── SCHEMA.md                    # field reference & validation invariants
├── CHANGELOG.md
├── CITATION.cff
├── LICENSE                      # CC-BY-4.0
├── data/
?   ??? reports.jsonl             # 178 rows - one retained GitHub Advisory per row
?   ??? entries.jsonl             # 393 rows - verified pair-level entries
?   ??? entry_points.jsonl        # 350 rows - deduplicated reachable-entry anchors
?   ??? critical_operations.jsonl # 356 rows - deduplicated critical-operation anchors
└── examples/
    ├── load_dataset.py          # stdlib / pandas / HuggingFace datasets loader
    ├── example_result.jsonl     # illustrative tool-findings submission
    ??? evaluate.py                      # pair-level recall evaluator
    ??? evaluate_entry_points.py         # entry-point anchor recall evaluator
    ??? evaluate_critical_operations.py  # critical-operation anchor recall evaluator
    ??? conversion_table_to_eval_inputs.py # conversion-table exporter
```

---

## 🚀 Quick start

```bash
git clone https://github.com/Tencent/VulnGym.git
cd VulnGym
python3 examples/load_dataset.py
```

Or load directly in Python:

```python
import json
with open("data/entries.jsonl", encoding="utf-8") as f:
    entries = [json.loads(line) for line in f if line.strip()]

xss = [e for e in entries if e["vuln_category_l1"] == "XSS"]
print(len(xss), "XSS entries")
print(xss[0]["entry_point"], "→", xss[0]["critical_operation"])

# Restrict to the human-audited high-confidence subset
verified = [e for e in entries if e["verify"] == 1]
print(len(verified), "human-audited entries")
```

Pandas:

```python
import pandas as pd
reports = pd.read_json("data/reports.jsonl", lines=True)
entries = pd.read_json("data/entries.jsonl", lines=True)
```

HuggingFace `datasets`:

VulnGym is also published on the HuggingFace Hub: [tencent/VulnGym](https://huggingface.co/datasets/tencent/VulnGym).

```python
from datasets import load_dataset

# Load directly from the HuggingFace Hub
ds = load_dataset("tencent/VulnGym")

# Or load from local JSONL files
ds = load_dataset("json", data_files={
    "reports": "data/reports.jsonl",
    "entries": "data/entries.jsonl",
})
```


## 📊 Evaluating your tool

Write your tool's findings to a JSONL file (one finding per line). This cleaned fork provides three recall-only evaluator entry points:

```bash
# Strict pair-level path reconstruction: entry_point + critical_operation
python3 examples/evaluate.py path/to/your_findings.jsonl -v

# Reachable-entry localization only
python3 examples/evaluate_entry_points.py path/to/your_findings.jsonl -v

# Core defect-location localization only
python3 examples/evaluate_critical_operations.py path/to/your_findings.jsonl -v
```

For pair-level evaluation, each finding must carry at least `repo_url`, `commit`, `entry_point`, and `critical_operation`. For entry-point-only evaluation, `entry_point` is required. For critical-operation-only evaluation, `critical_operation` is required. `trace` is optional and ignored by all three matchers. See `examples/example_result.jsonl` for a working sample.

The pair-level script reports advisory-level and entry-level recall. The single-anchor scripts report anchor-level recall, report-level recall, and source-entry coverage.

**Default matching policy**

| Aspect | Default |
|---|---|
| Path match | normalized, exact |
| Line tolerance | `\|Δline\| ≤ 5` on entry_point **and** critical_operation |
| Direction | pair-level is strict entry_point-to-entry_point and critical_operation-to-critical_operation; single-anchor evaluators match only their corresponding anchor |
| Unusable ground-truth line | excluded from numerator and denominator |

All policies are documented and configurable via CLI arguments
(`--line-tolerance`, etc.).

> **Note:** The current evaluator **only computes recall / coverage** and
> cannot penalize over-reporting. The resulting numbers should be
> interpreted as coverage metrics, not a full precision-aware benchmark.


## 📖 Citation

> 📚 **A companion paper is in preparation.** Until it is released, please cite VulnGym using the dataset entry below; we will update this section once the paper is publicly available.

```bibtex
@misc{vulngym2026,
  title        = {VulnGym: A Real-World, Project-Level Vulnerability Benchmark
                  for White-Box Vulnerability-Hunting Agents},
  author       = {{Tencent Wukong Code Security Team and contributors}},
  year         = {2026},
  version      = {0.1.4},
  howpublished = {\url{https://github.com/Tencent/VulnGym}},
  note         = {Dataset. A companion paper is in preparation; please check
                  the repository for the latest citation.}
}
```

Once the paper is public, the entry below will be filled in and should be preferred:

```bibtex
@inproceedings{vulngym2026paper,
  title     = {TBA — A companion paper for VulnGym is in preparation.},
  author    = {{To be announced}},
  year      = {TBA},
  note      = {Placeholder; will be replaced once the paper is publicly available.}
}
```

See `CITATION.cff` for the machine-readable form.

---

## 🤝 Contribution Guide

VulnGym aims to be an **open, reproducible, and continuously evolving**
community benchmark. Contributions from both academia and industry are
warmly welcomed:

- 🧠 **Dataset contributions** — new advisories, additional reachable
  entry points for existing advisories, corrections to `entry_point` /
  `critical_operation` / `trace`.
- 🔧 **Evaluator improvements** — precision / F1, per-category
  breakdowns, statistical significance (bootstrap CI), alternative
  matching policies.
- 📊 **Evaluation result submissions** — submit your tool's evaluation
  results via PR to be included in the baseline comparison.
- 💬 **Discussions & feedback** — file an
  [Issue](https://github.com/Tencent/VulnGym/issues) or start a
  [Discussion](https://github.com/Tencent/VulnGym/discussions).

Please read `SCHEMA.md` before proposing data changes — all invariants
listed there are enforced at release time.

---

## 🙏 Acknowledgements

VulnGym is jointly built by the **Tencent Wukong Security Team**
together with the following academic partners (listed in no particular
order, final order TBD):
- ARISE Lab, The Chinese University of Hong Kong
- Systems Software & Security Lab, Fudan University
- JC STEM Lab of Intelligent Cybersecurity, The University of Hong Kong
- Narwhal-Lab, Peking University
- Network Threat Analysis Lab, Institute of Information Engineering, Chinese Academy of Sciences

Many thanks to all partners for their outstanding contributions to
VulnGym.

---

## 📄 License

The dataset is released under **CC-BY-4.0** — see [`LICENSE`](LICENSE).
You may use it for commercial and academic purposes with attribution.
Source code paths and commit hashes referenced in `entry_point` /
`critical_operation` / `trace` fields belong to their respective upstream
projects under their original licenses; consult the referenced
repositories before reusing any quoted code fragment.
