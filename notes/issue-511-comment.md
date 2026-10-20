认领这条线：做神经科学 / 脑机接口方向的，issue 里提到的 yixuan 就是我。按 9 月 4 日的结论（"专业的人愿意来搞"），我来牵头，第一个 PR 已开：**#647**。

先交代实测结论，再给三步计划和时间线。

## 结论：bench 搜不到，主因不是算法，是三层缺口

我把 53 天快照（8,367 条唯一记录）、外部目录、策展层各查了一遍：

| 层 | 规模 | 神经科学覆盖 |
|---|---|---|
| 每日发现 | ~400 条/天 | 有进来的（53 天 103 条带神经科学特征），但源头全是 AI 地盘 |
| 外部目录 | ~1,173 行 | ≈ 7 行 |
| 策展层 | 110 采用 / 87 轨道 | ≈ 0 |

- **算法没有 bug**：40 分是推荐线不是发布线，低分科学记录其实都在页面上。relevance 的设计也不必动。
- **真正缺的**：① arXiv 只订 cs.AI/CL/CV/SE，神经科学论文发在 q-bio.NC，脑电/解码类常发 eess.SP，从来不路过；② 各搜索源的关键词全是 "LLM benchmark" 这类 AI 措辞；③ 外部目录和策展层结构性没有科学类。
- **知名缺口清单**（40 天发现层均未出现，也不在目录/策展层，所以站内搜不到）：NeuroBench、BCI Competition I–IV、TUH EEG、Sleep-EDF、Human Connectome Project、ScienceAgentBench、MatBench、WeatherBench……这份清单就是 PR2 的召回种子。

## 三步计划与时间线

| 步骤 | 内容 | 状态 |
|---|---|---|
| **PR1** | `science_domains` 标签：确定性关键词规则，网站数据和本地查询共用同一函数，53 天历史全部点亮、快照零改写、不动任何分数 | ✅ #647 已开，待评审 |
| **PR2** | 换源头：arXiv 加 q-bio.NC / eess.SP，各搜索源加神经科学关键词，重点基准挂牌（MOABB、NeuroBench、BCI Competition、LibriBrain）。按仓库传统带测量：种子召回基线 + 按来源分层抽样 + 门槛（总体精度 ≥0.80、每源 ≥0.60、日增量 ≤+20%），不达标就回退 | PR1 合并后 ~1 周 |
| **PR3** | "AI for Science" tab：导航短名 + 页标题 "Neuroscience & BCI" + Preview 徽标，域筛选 + 7/30/90 天时间窗 | 与 PR2 并行准备 |

## PR1 已经抓到的（53 天实测）

103 条记录带标签，38 条进过推荐位，周流量从 5–17 条涨到 9 月的 27–28 条。亮点：**LibriBrain100**（牛津，100 小时 MEG 神经语音解码）、**BrainBench**（EEG × LLM 理解）、**CORAL**（全脑神经元重建）、临床 EEG 基础模型**负对照协议**、颅内动脉瘤 AI 检测。

词表已按领域审计收词（brain-machine interface、neuroprosthesis、speech neuroprosthesis、Utah array、sEEG、fNIRS、calcium imaging、optogenetics、Brain2Text/2Voice/2Qwerty 家族等），误报逐类追因并用测试锁死（Snowflake Cortex 撞 cortex、"acts as the brain of" 比喻、血脑屏障假说数据集等）。**欢迎继续补词**——每个词都会先过一遍全量语料实测再上锁。

<details>
<summary>English TL;DR</summary>

Claiming the neuro/BCI slice per the Sep 4 decision. Root cause of "science benchmarks not found" is **not** the scoring algorithm — it is three gaps: arXiv categories (no q-bio.NC / eess.SP), AI-only search vocabulary, and near-zero science coverage in the catalog and curated layers. Plan: **PR1** (#647, open) adds a deterministic `science_domains` tag shared by radar.json and local query surfaces — 103 records tagged across 53 days, 38 recommended, snapshots untouched, no score changes; **PR2** adds discovery sources with measured precision gates (seed recall over MOABB / NeuroBench / BCI Competition / TUH / Sleep-EDF / HCP); **PR3** ships the "AI for Science · Neuroscience & BCI (Preview)" view with domain filter and a rolling time window. Vocabulary from a domain review is already in PR1 with false-positive classes locked by tests; more terms welcome.
</details>
