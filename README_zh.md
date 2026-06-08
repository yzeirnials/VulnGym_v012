<p align="center">
  <img src="./img/wukong_logo.png" alt="VulnGym" height="60">
</p>

<h4 align="center">
    <p>
        <a href="#">中文</a> |
        <a href="./README.md">English</a>
    </p>
</h4>

<p align="center">
  <a href="https://github.com/Tencent/VulnGym/stargazers"><img alt="GitHub Stars" src="https://img.shields.io/github/stars/Tencent/VulnGym?color=gold"></a>
  <a href="https://github.com/Tencent/VulnGym/network/members"><img alt="GitHub Forks" src="https://img.shields.io/github/forks/Tencent/VulnGym?color=gold"></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-CC--BY--4.0-blue.svg"></a>
</p>

<p align="center">
  <b>面向白盒漏洞检测 Agent 的真实工程级漏洞评测基准</b>
</p>

<p align="center">
  <a href="https://github.com/Tencent/VulnGym"><img src="https://img.shields.io/badge/⭐-给 VulnGym 点个 Star-yellow?style=flat&logo=github" alt="Give VulnGym a Star"></a>
  <a href="https://huggingface.co/datasets/tencent/VulnGym"><img src="https://img.shields.io/badge/🤗%20HuggingFace-数据集-yellow?style=flat" alt="HuggingFace Dataset"></a>
</p>

**VulnGym** 是面向白盒漏洞检测 Agent 的项目级评测基准，支持在**真实工程上下文**中评估 Agent 的漏洞识别能力，并提供**可验证的漏洞触发路径与业务语义证据链**。

**三个核心设计理念：**
- **🏗️ 真实项目级评测单元** — 每个样本绑定到含漏洞的特定版本代码仓库，评测 Agent 在真实多文件、多模块工程中的漏洞发现与定位能力
- **🧠 全面的漏洞类型覆盖** — 评测体系同时涵盖需要跨模块代码语义理解的业务逻辑漏洞（如权限绕过、认证缺失等）与传统安全漏洞（如注入、路径穿越等），旨在全面评估 Agent 对不同类型漏洞的发现能力
- **✅ 可验证的漏洞路径** — 每个样本提供人工审核的**漏洞入口（entry point）**、**敏感代码操作（critical operation）** 和**跨模块推理链路（trace）**，实现可复现、可解释的确定性评测

---

## 📢 最新动态
- **2026-06-08** — 🧹 cleaned fork：仅保留 `verify = 1` 的人工审计入口，数据集规模调整为 **137 reports / 274 entries**；部分 verified 的 advisory 已按保留 entry 重新计算 `entry_ids` 和 `num_entries`。
- **2026-05-31** — 🔧 v0.1.2 数据更新：人工审计通过数量大幅提升，已审计 entry 从 **113 条增至 274 / 408 条 (67.2%)**，覆盖 advisory 从 **61 条增至 137 / 184 条 (74.5%)**。此外，对 80 条 entry 的 `entry_point` / `critical_operation` / `trace` 标注进行了精度优化。
- **2026-05-17** — 🔧 v0.1.1 数据更新：为每条 entry 新增 `verify` 字段以标记人工审计状态；目前已有 **113 / 408 条 entry**（覆盖 **61 / 184 条 advisory**）通过人工审计。同时对部分 `entry_point` / `critical_operation` / `trace` 字段值做了优化。
- **2026-05-15** — 🎉 VulnGym v0.1.0 版本正式开源！



## 目录

- [🔍 为什么需要 VulnGym](#-为什么需要-vulngym)
- [✨ 数据集概览](#-数据集概览)
- [📈 基线评测结果](#-基线评测结果)
- [📦 目录结构](#-目录结构)
- [🚀 快速开始](#-快速开始)
- [📊 评测你的工具](#-评测你的工具)
- [📖 引用](#-引用)
- [🤝 贡献指南](#-贡献指南)
- [🙏 致谢](#-致谢)
- [📄 许可协议](#-许可协议)

---

## 🔍 为什么需要 VulnGym

现有漏洞评测集在评估 AI Agent 的真实漏洞挖掘能力时，存在以下局限：

| 局限 | 表现 |
|---|---|
| **评测粒度不足** | 多以函数或 diff 片段为评测单元，难以反映 Agent 在完整工程项目中定位漏洞的能力 |
| **漏洞类型单一** | 偏重 SQL 注入、缓冲区溢出等模式化 CWE 漏洞，较少涉及需要深度上下文推理的类别 |
| **Ground Truth 粗粒度** | 多为二分类标签（有漏洞 / 无漏洞）或 patch diff，无法精确验证 Agent 是否定位到了正确的入口和缺陷点 |


## ✨ 数据集概览

当前为 VulnGym 的 **v0.1.2 版本**。数据以两个 JSONL 文件提供于 `data/` 目录下：

- `reports.jsonl` — 以 GitHub Advisory 为粒度的聚合记录
- `entries.jsonl` — 以外部可达入口（entry point）为粒度的标注记录

每条记录包含 `repo_url` 和 `commit`，可据此拉取对应漏洞版本的完整源码树。

### 数据规模

| 指标 | 数值 |
|---|---|
| Advisory 数（reports） | **137** |
| 可达入口数（entries） | **274** |
| 涉及项目数 | 30 |
| 涉及仓库数 | 23 |
| 人工审计通过的入口（`verify = 1`） | **274 / 274 (100.0%)** |
| 人工审计通过的 advisory（至少一条入口已审计） | **137 / 137 (100.0%)** |

### 人工审计状态

自 v0.1.1 起，`entries.jsonl` 中每条记录均包含 `verify` 字段（`int`，取值 `0` 或 `1`）。

当前 cleaned fork 已经将 `data/entries.jsonl` 过滤为仅包含 `verify == 1` 的人工审计入口；
`data/reports.jsonl` 也已重新聚合，使 `entry_ids` 和 `num_entries` 仅指向保留的 verified entries。
上游 v0.1.2 中 `verify == 0` 的入口不包含在本分支的数据文件中，删除和保留明细记录在
`records/cleaned_verify1_20260608.md` 与 `records/cleaned_verify1_20260608_summary.json`。

过滤前，上游 v0.1.2 包含 **184 reports / 408 entries**，
其中 **274** 条 entry、**137** 条 report 至少包含一条 verified entry。
过滤后，本分支保留 **137 reports / 274 entries**。
其中 **29** 条原本部分 verified 的 report 已删除未验证 entry 并重算聚合字段。

### 漏洞类型分布

每条数据包含两级分类字段：`vuln_category_l1`（粗粒度类型）和
`vuln_category_l2`（细粒度子类型）。在当前 cleaned subset 中，**105 / 137 (76.6%)** 的漏洞为业务逻辑类，其余 **32 / 137 (23.4%)** 覆盖传统漏洞类型。完整数据模型与字段定义详见 [`SCHEMA.md`](SCHEMA.md)。

> 注：一个漏洞（Advisory）可能对应多个入口（Entry）——下表按 **漏洞数** 统计，而非入口数。

**业务逻辑类 (105 / 137, 76.6%) — `vuln_category_l2` 分布：**

| 二级分类 | 漏洞数 | 占比 |
| --- | --- | --- |
| BL-AUTHZ-BROKEN | 23 | 21.9% |
| BL-AUTHZ-MISSING | 18 | 17.1% |
| BL-AGENT-CAPABILITY | 17 | 16.2% |
| BL-PRIV-ESC | 12 | 11.4% |
| BL-AUTH-BYPASS | 8 | 7.6% |
| BL-ORIGIN-INTEGRITY | 7 | 6.7% |
| BL-WORKFLOW-VIOLATION | 6 | 5.7% |
| BL-INSECURE-DEFAULT | 5 | 4.8% |
| BL-RACE-LOGIC | 4 | 3.8% |
| BL-MASS-ASSIGNMENT | 2 | 1.9% |
| BL-TRUST-BOUNDARY | 2 | 1.9% |
| BL-MULTI-TENANT | 1 | 1.0% |

<br>

**传统漏洞类 (32 / 137, 23.4%) — 主要 `vuln_category_l1` 分布：**

| 类别 | 漏洞数 | 占比 |
| --- | --- | --- |
| 路径穿越/文件操作 | 8 | 25.0% |
| XSS | 4 | 12.5% |
| 代码注入 | 4 | 12.5% |
| 命令注入 | 3 | 9.4% |
| SSRF | 3 | 9.4% |
| 反序列化 | 2 | 6.2% |
| 模板注入 | 1 | 3.1% |
| 权限绕过 | 1 | 3.1% |
| 注入类 | 1 | 3.1% |
| 沙箱逃逸 | 1 | 3.1% |
| 认证绕过 | 1 | 3.1% |
| 供应链 | 1 | 3.1% |
| 注入与反序列化 | 1 | 3.1% |
| 原型链污染 | 1 | 3.1% |

> 后续版本将持续扩展更多漏洞类别与项目覆盖

### 单点粒度 Ground Truth

除 pair-level `data/entries.jsonl` 外，本 cleaned fork 还从同一批 verified entries
派生了两个单点粒度 ground-truth 文件：

- `data/entry_points.jsonl` — 去重后的可达入口 anchor
- `data/critical_operations.jsonl` — 去重后的核心缺陷操作 anchor

这两个文件中的每个 anchor 都保留 `source_entry_ids` 和 `source_report_ids`，
用于回溯到原始 pair-level entries。当前规模为 **236** 个 entry-point anchors
和 **241** 个 critical-operation anchors。

## 📈 基线评测结果

> 🚧 **即将发布** — 我们正在对主流工具和 AI Agent 进行系统评测，结果将随技术报告一并公布。


## 📦 目录结构

```
VulnGym/
├── README.md                    # 英文版
├── README_zh.md                 # 当前文件
├── SCHEMA.md                    # 字段参考与校验不变量
├── CHANGELOG.md
├── CITATION.cff
├── LICENSE                      # CC-BY-4.0
├── data/
│   ├── reports.jsonl             # 137 行 —— 每行一条保留的 GitHub Advisory
│   ├── entries.jsonl             # 274 行 —— pair-level verified entries
│   ├── entry_points.jsonl        # 236 行 —— 去重后的入口 anchor
│   └── critical_operations.jsonl # 241 行 —— 去重后的核心操作 anchor
└── examples/
    ├── load_dataset.py
    ├── example_result.jsonl
    ├── evaluate.py                      # pair-level 召回评测
    ├── evaluate_entry_points.py         # entry_point anchor 召回评测
    └── evaluate_critical_operations.py  # critical_operation anchor 召回评测
```

---

## 🚀 快速开始

```bash
git clone https://github.com/Tencent/VulnGym.git
cd VulnGym
python3 examples/load_dataset.py
```

或者直接在 Python 中加载：

```python
import json
with open("data/entries.jsonl", encoding="utf-8") as f:
    entries = [json.loads(line) for line in f if line.strip()]

xss = [e for e in entries if e["vuln_category_l1"] == "XSS"]
print(len(xss), "条 XSS entries")
print(xss[0]["entry_point"], "→", xss[0]["critical_operation"])

# 仅取人工审计通过的高置信子集
verified = [e for e in entries if e["verify"] == 1]
print(len(verified), "条人工审计通过的 entries")
```

Pandas：

```python
import pandas as pd
reports = pd.read_json("data/reports.jsonl", lines=True)
entries = pd.read_json("data/entries.jsonl", lines=True)
```

HuggingFace `datasets`：

VulnGym 也已发布至 HuggingFace Hub：[tencent/VulnGym](https://huggingface.co/datasets/tencent/VulnGym)。

```python
from datasets import load_dataset

# 直接从 HuggingFace Hub 加载
ds = load_dataset("tencent/VulnGym")

# 或者从本地 JSONL 文件加载
ds = load_dataset("json", data_files={
    "reports": "data/reports.jsonl",
    "entries": "data/entries.jsonl",
})
```


## 📊 评测你的工具

将工具检出结果写入一个 JSONL 文件（每行一条 finding）。当前 cleaned fork
提供三个 recall-only evaluator：

```bash
# 严格 pair-level 路径重建：entry_point + critical_operation
python3 examples/evaluate.py path/to/your_findings.jsonl -v

# 仅评估可达入口定位
python3 examples/evaluate_entry_points.py path/to/your_findings.jsonl -v

# 仅评估核心缺陷位置定位
python3 examples/evaluate_critical_operations.py path/to/your_findings.jsonl -v
```

pair-level 评估要求每条 finding 至少包含 `repo_url`、`commit`、`entry_point`
（外部可达入口）和 `critical_operation`（核心缺陷位置）。entry-point-only 评估只要求
`entry_point`；critical-operation-only 评估只要求 `critical_operation`。`trace`
（跨模块推理链路）可选，三个 matcher 都不使用 `trace`。完整格式参考
`examples/example_result.jsonl`。

pair-level 脚本报告：

- **Advisory-level recall**（主指标）— `covered_advisories /
  usable_advisories`。如果某个 advisory 至少有一条 entry 被匹配，则视为覆盖。
- **Entry-level recall**（辅助指标）— `matched_entries / usable_entries`。

两个单点粒度脚本报告：

- **Anchor-level recall**（主指标）— 命中的 `entry_point` 或 `critical_operation`
  anchors / usable anchors。
- **Report-level recall**（补充指标）— 通过 matched anchors 覆盖到的 reports。
- **Source-entry coverage**（补充指标）— 通过 matched anchors 覆盖到的原始
  pair-level entries。

**默认匹配策略**

| 维度 | 默认值 |
|---|---|
| 路径匹配 | 归一化后严格相等 |
| 行号容差 | `int` 或 `"start-end"` span；默认容差 `+/-5` |
| 方向 | pair-level 严格匹配 entry_point 对 entry_point、critical_operation 对 critical_operation；单点评估只匹配对应 anchor |
| 不可用 ground truth line | 同时从分子分母中剔除 |

所有策略均有文档说明，并可通过 CLI 参数调整（`--line-tolerance` 等）。

> **注意：** 当前评测器**只计算召回率 / 覆盖率**，无法惩罚过度上报，
> 因此其数值应理解为覆盖率指标，而非完整的 precision-aware benchmark。


## 📖 引用

> 📚 **配套论文正在撰写中**。论文公开发布前，请使用以下数据集 BibTeX 条目引用 VulnGym；论文发布后我们会更新此处。

```bibtex
@misc{vulngym2026,
  title        = {VulnGym: A Real-World, Project-Level Vulnerability Benchmark
                  for White-Box Vulnerability-Hunting Agents},
  author       = {{Tencent Wukong Code Security Team and contributors}},
  year         = {2026},
  version      = {0.1.2},
  howpublished = {\url{https://github.com/Tencent/VulnGym}},
  note         = {Dataset. A companion paper is in preparation; please check
                  the repository for the latest citation.}
}
```

论文公开后，以下条目将被补全并作为推荐引用：

```bibtex
@inproceedings{vulngym2026paper,
  title     = {TBA — A companion paper for VulnGym is in preparation.},
  author    = {{To be announced}},
  year      = {TBA},
  note      = {Placeholder; will be replaced once the paper is publicly available.}
}
```

机器可读版本详见 `CITATION.cff`。

---

## 🤝 贡献指南

VulnGym 致力于成为**开放、可复现、持续演进**的社区评测基准，
欢迎学术界与产业界共同参与：

- 🧠 **数据贡献** — 新增 advisory、为已有 advisory 补充外部可达入口、
  修正 `entry_point` / `critical_operation` / `trace`
- 🔧 **评测器改进** — precision / F1、按类别拆分、
  统计显著性（bootstrap CI）、新增匹配策略等
- 📊 **评测结果提交** — 欢迎通过 PR 提交你的工具评测结果，纳入基线对比
- 💬 **讨论与反馈** — 欢迎通过
  [Issues](https://github.com/Tencent/VulnGym/issues) 或
  [Discussions](https://github.com/Tencent/VulnGym/discussions) 交流

提交数据变更前请先阅读 `SCHEMA.md`，其中列出的所有不变量都会在发布前被强校验。

---

## 🙏 致谢

VulnGym 由**腾讯悟空安全团队**联合以下学术单位共同建设（排名不分先后，顺序待定）：

- 香港中文大学 ARISE Lab
- 复旦大学系统软件与安全实验室
- 香港大学 JC STEM Lab of Intelligent Cybersecurity
- 北京大学 Narwhal-Lab
- 中国科学院信息工程研究所网络威胁分析研究室

感谢各方对 VulnGym 的卓越贡献！

---

## 📄 许可协议

数据集以 **CC-BY-4.0** 协议开源，详见 [`LICENSE`](LICENSE)，
允许商业与学术使用，惟需署名。`entry_point` / `critical_operation` / `trace` 字段中引用的
代码片段、路径与 commit 哈希归其上游项目所有，遵循各自原始开源协议，
再利用前请查阅对应上游仓库。
