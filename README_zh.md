# VulnGym 六批次数据集

[English](README.md) · [数据格式](SCHEMA.md) · [机器可读版本信息](data/dataset.json)

本仓库基于 [Tencent VulnGym](https://github.com/Tencent/VulnGym) v0.1.2
的人工验证数据，仅保留 **openclaw-01 与 mixed-01 至 mixed-05**。
每条 entry 绑定漏洞仓库的指定 commit，以及可达入口、关键操作和标注 trace。

最终数据集包含 **156 条 entry、61 条 report、136 个 entry-point anchor、
137 个 critical-operation anchor**，覆盖 **55 个源码快照、23 个仓库**。
所有保留 entry 均为 `verify == 1`。

## 数据规模与漏洞标识

**entry** 是一组入口与关键操作的配对标注。**entry-point anchor** 和
**critical-operation anchor** 分别按该角色的
`(repo_url, commit, file, line)` 去重；多条 entry 可以共享一个 anchor。
**源码快照**指一个 `(repo_url, commit)`。原始 entry、report、anchor ID
均保留，因此编号允许不连续。

| Batch | 快照 | Entries | Reports | Entry points | Critical operations | GHSA IDs | CVE IDs |
|---|---:|---:|---:|---:|---:|---:|---:|
| openclaw-01 | 6 | 32 | 7 | 18 | 19 | 8 | 4 |
| mixed-01 | 10 | 27 | 11 | 27 | 27 | 11 | 11 |
| mixed-02 | 7 | 21 | 10 | 19 | 19 | 10 | 7 |
| mixed-03 | 9 | 30 | 10 | 27 | 26 | 10 | 6 |
| mixed-04 | 14 | 34 | 14 | 33 | 34 | 14 | 12 |
| mixed-05 | 9 | 12 | 9 | 12 | 12 | 9 | 8 |
| **合计** | **55** | **156** | **61** | **136** | **137** | **62** | **48** |

entry、entry-point、critical-operation 三种粒度分别关联的去重标识数均为
**62 个 GHSA、48 个 CVE**。统计从 `vuln_ids`、`report_id`、`source_link`
三个字段取并集，统一大写后去重；anchor 的标识关联来自保留的 source entries
及其 reports。

这些标识数不能直接当作独立漏洞数。13 条 report 没有记录 CVE；
`GHSA-QWMF-95R9-GX9X` 同时列出 `GHSA-HFF7-CCV5-52F8`，因此 61 条 report
对应 62 个 GHSA。部分 `vuln_ids` 缺少本条 report 的 GHSA 或为空，只统计该字段
会漏计。完整明细见 [标识关联表](records/identifier_associations.csv) 和
[粒度统计表](records/granularity_statistics.csv)。

## 语言、漏洞类别与项目规模

<!-- DATASET_STATISTICS:START -->

所有计入统计的语言如下；覆盖快照数允许重叠。

| 语言 | SLOC | SLOC 占比 | 覆盖快照 | 主语言 Entries |
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
| **合计** | **35,581,725** | **100.00%** | — | **156** |

**55 个固定快照的项目规模（SLOC）**

| 最小值 | P25 | 中位数 | 均值 | P75 | 最大值 |
|---:|---:|---:|---:|---:|---:|
| 50,846 | 194,707.50 | 404,139 | 646,940.45 | 943,666 | 2,112,892 |

**原始 L1 漏洞类别**：Entry 占比以 156 条 entry 为分母，Report 占比以 61 条 report 为分母。

| 原始 L1 类别 | Entries | Entry 占比 | Reports | Report 占比 |
|---|---:|---:|---:|---:|
| 业务逻辑 | 95 | 60.90% | 36 | 59.02% |
| 代码注入 | 12 | 7.69% | 4 | 6.56% |
| XSS | 9 | 5.77% | 4 | 6.56% |
| 反序列化漏洞 | 7 | 4.49% | 1 | 1.64% |
| 反序列化 | 5 | 3.21% | 1 | 1.64% |
| 命令注入 | 4 | 2.56% | 2 | 3.28% |
| SSRF | 3 | 1.92% | 3 | 4.92% |
| 供应链攻击 | 3 | 1.92% | 1 | 1.64% |
| 原型链污染 | 3 | 1.92% | 1 | 1.64% |
| 模板注入 | 3 | 1.92% | 1 | 1.64% |
| 注入与反序列化 | 3 | 1.92% | 1 | 1.64% |
| 文件操作安全 | 2 | 1.28% | 1 | 1.64% |
| 权限绕过 | 2 | 1.28% | 1 | 1.64% |
| 沙箱逃逸 | 2 | 1.28% | 1 | 1.64% |
| 注入类 | 1 | 0.64% | 1 | 1.64% |
| 路径穿越 | 1 | 0.64% | 1 | 1.64% |
| 路径遍历 / 任意文件读取 | 1 | 0.64% | 1 | 1.64% |

原始标签分别计数，不合并同义标签。完整 L1/L2、各批次 entry/report 分布见 [漏洞类别统计](records/category_statistics.csv)。更多结果见 [统计汇总](records/dataset_statistics.json)、[语言统计](records/language_statistics.csv)、[快照规模明细](records/snapshot_statistics.csv) 和 [仓库规模明细](records/repository_statistics.csv)。

<!-- DATASET_STATISTICS:END -->

语言与规模在漏洞对应的 commit 上测量。规模采用剔除空行、注释行后的物理源码行数
（SLOC）。快照中 SLOC 最多的语言作为主要语言，entry 的语言分布继承所在快照的
主要语言；这不一定是漏洞 anchor 所在文件的语言。一个快照可覆盖多种语言。

测量使用固定的 **cloc 2.10**，仅读取 Git 跟踪的普通文件，并遵循
[源码统计规则](scripts/source_size_policy.json)：纳入测试与示例代码，排除文档、
数据与配置语言、依赖以及识别出的生成代码和第三方代码。生成文件识别采用启发式规则。
快照 SLOC 总和会分别计算同一仓库的不同版本。漏洞类别保留原始双语 L1/L2 标签；
report 分布按不同的 report/category 关联计数，不重写原标注。

## 快速开始

显式克隆六批次分支；已有本地 checkout 可直接运行 Python 命令。

```bash
git clone --branch codex/six-batch-dataset https://github.com/yzeirnials/VulnGym_v012.git
cd VulnGym_v012
python3 scripts/subset_dataset.py --validate
python3 examples/load_dataset.py
```

验证与评测脚本仅依赖 Python 标准库。loader 也提供可选的 pandas、HuggingFace
`datasets` 示例，读取的都是本地文件。Tencent 的 HuggingFace 数据集范围不同。

| 文件 | 用途 |
|---|---|
| `data/entries.jsonl` | 156 条 pair-level ground truth |
| `data/reports.jsonl` | 61 条 report，`entry_ids`、`num_entries` 已按保留成员重算 |
| `data/entry_points.jsonl` | 136 个去重入口 anchor |
| `data/critical_operations.jsonl` | 137 个去重关键操作 anchor |
| `data/entries_desc.jsonl` | 与 156 条 entry 一一对应，保留已有的 `desc` 解释标注 |
| `data/batch_manifest.jsonl` | 55 条快照记录，定义六批次成员 |
| `data/dataset.json` | 数据集身份、来源 commit、计数与文件绑定 |

源码仓库通过 `repo_url`、`commit` 引用，未打包进本数据集。进行 GT-blind 检测评测时，
应将 ground-truth 标注与工具提示词、配置隔离。

## 评测工具结果

先用 [conversion-table 格式](examples/conversion_table.schema.json) 记录工具原始发现，
再导出三种输入并分别评测：

```bash
python3 examples/conversion_table_to_eval_inputs.py examples/example_conversion_table.jsonl --out-dir /tmp/vulngym_eval_inputs
python3 examples/evaluate.py /tmp/vulngym_eval_inputs/pair_findings.jsonl --json-out /tmp/vulngym_pair.json
python3 examples/evaluate_entry_points.py /tmp/vulngym_eval_inputs/entry_point_findings.jsonl --json-out /tmp/vulngym_ep.json
python3 examples/evaluate_critical_operations.py /tmp/vulngym_eval_inputs/critical_operation_findings.jsonl --json-out /tmp/vulngym_co.json
```

`examples/` 下的 JSONL 是演示数据，不代表真实工具结果。转换器保留显式 candidate
pairs；只有恰好一个可用入口候选与一个可用关键操作候选时才自动配对，多候选不会
隐式展开为笛卡尔积。

默认 GT 是当前 checkout 的完整六批次数据，不受启动目录影响。pair evaluator
用 `--entries`，两个 anchor evaluator 用 `--ground-truth` 指定其他 GT 文件。
报告记录实际 GT 路径与范围，findings 的覆盖范围不会缩小分母。完整数据集的
**156 条 pair / 61 条 report、136 个 EP、137 个 CO** 均有可用行号。

匹配要求仓库与 commit 一致、规范化后路径精确相等、入口和关键操作角色方向一致；
默认 `--line-tolerance 5`，支持整数和区间行号。不可用 GT 行号从分母排除，
`trace` 不参与匹配。评测仅提供 **recall/coverage**，不计算 precision 或 F1。
pair evaluator 的 report 覆盖率只需命中该 report 的任一 entry；anchor 评测另给出来源
entry 与 report 的覆盖率。

## 复现子集与统计

在保留 Git 历史的 checkout 中，将相同数据生成到新目录：

```bash
python3 scripts/subset_dataset.py --output-dir ../VulnGym-six-batches-reproduced
python3 scripts/subset_dataset.py --batch-id mixed-05 --output-dir ../VulnGym-mixed-05
python3 scripts/build_endpoint_ground_truth.py --check
python3 -m unittest discover -s tests
```

`--batch-id` 可重复指定。生成器读取固定来源 commit 与保留 manifest，保留 ID 和
endpoint 位置，重算 report 与 anchor 来源关联；输出目录必须不存在。旧清洗与
anchor 脚本默认只读检查，不再重写 README、SCHEMA、CHANGELOG 或历史 records。

使用已提供的源码测量结果重建统计：

```bash
python3 scripts/dataset_stats.py --source-sizes records/source_sizes.json --output-dir records --update-readmes
```

省略 `--update-readmes` 时，仅重新生成 JSON 与 CSV，不修改 README。

重新测量源码时，先准备 manifest 中 55 个 commit 的干净 Git checkout，安装 Perl
及官方 cloc 2.10 脚本。允许的脚本 SHA-256 与过滤规则固定在源码统计规则中：

```bash
python3 scripts/measure_source_sizes.py --source-root /path/to/source-cache --cloc /path/to/cloc-2.10.pl
```

缓存目录命名为 `<主机与仓库路径的连续非字母数字字符替换为__>__<commit>`。
也可用 `--source-map /path/to/local-map.jsonl` 指定路径，每行含 `repo_url`、
`commit`、`cache_path`；机器专用映射留在本地。测量读取源码，不编译或执行项目。

## 来源与历史记录

Tencent VulnGym v0.1.2 最初包含 408 条 entry / 184 条 report；首次清洗保留
274 条人工验证 entry / 137 条 report。本次从
`90002144d4a8b3654fb1bf68052889b9c2de44aa` 按上述六批次再次筛选至 156 条 entry；
解释标注来源为 `4c4ac5659329008d9ea44ac5ec7855eae6909c2e`。

[CHANGELOG.md](CHANGELOG.md) 和日期为 `20260608` 的 records 保留原清洗历史。
其中旧计数与历史 benchmark 材料只适用于各自的原始范围，不是本六批次的工具评测结果。
本次仓库整理没有生成新的工具 baseline。完整原版本说明见
[历史 README](https://github.com/yzeirnials/VulnGym_v012/blob/90002144d4a8b3654fb1bf68052889b9c2de44aa/README_zh.md)。

## 署名与许可

原始数据集归功于 **Tencent Wukong Code Security Team 与 VulnGym 贡献者**。
引用原数据集时使用 [CITATION.cff](CITATION.cff)，并在实验中额外注明本 fork、
六批次选择范围与使用的具体版本。数据标注遵循 [CC-BY-4.0](LICENSE)；引用的各源码
项目仍遵循各自许可证。
