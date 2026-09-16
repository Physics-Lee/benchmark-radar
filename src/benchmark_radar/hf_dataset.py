"""Export Benchmark Radar datasets in standard formats for Hugging Face Hub.

Produces four subsets (configs) aligning with the Benchmark Radar paper:
1. `catalog` (default): Normalized metadata for all 1,284+ benchmarks.
2. `scores`: 12,900+ benchmark evaluation score observations across models.
3. `radar_artifacts`: 8,500+ emerging benchmarks, papers, and repositories tracked by radar.
4. `radar_observations`: 14,800+ daily dynamic discovery events and attention metrics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .query import QueryPaths

DEFAULT_EXPORT_DIR = Path("site/data/hf_dataset")


@dataclass
class DatasetExportResult:
    export_dir: Path
    catalog_count: int
    scores_count: int
    artifacts_count: int
    observations_count: int
    manifest: dict[str, Any]


def generate_dataset_card(
    *,
    catalog_count: int,
    scores_count: int,
    artifacts_count: int,
    observations_count: int,
) -> str:
    """Generate Hugging Face Dataset Card README.md with YAML frontmatter."""
    card = f"""---
license: apache-2.0
task_categories:
  - text-generation
  - question-answering
  - tabular-classification
language:
  - en
  - zh
tags:
  - benchmark
  - evaluation
  - llm
  - leaderboard
  - ai-evaluation
  - benchmark-radar
size_categories:
  - 10K<n<100K
configs:
  - config_name: default
    data_files: "data/catalog.jsonl"
  - config_name: catalog
    data_files: "data/catalog.jsonl"
  - config_name: scores
    data_files: "data/scores.jsonl"
  - config_name: radar_artifacts
    data_files: "data/radar_artifacts.jsonl"
  - config_name: radar_observations
    data_files: "data/radar_observations.jsonl"
---

# Benchmark Radar Dataset

<p align="center">
  <a href="https://huggingface.co/papers/2609.11115"><img alt="Paper" src="https://img.shields.io/badge/Paper-arXiv%3A2609.11115-B31B1B.svg"></a>
  <a href="https://benchmark-radar.org"><img alt="Website" src="https://img.shields.io/badge/Website-benchmark--radar.org-blue.svg"></a>
  <a href="https://github.com/ktwu01/benchmark-radar"><img alt="GitHub" src="https://img.shields.io/badge/GitHub-Benchmark%20Radar-black.svg"></a>
  <a href="https://huggingface.co/datasets/ktwu01/benchmark-radar"><img alt="HF Dataset" src="https://img.shields.io/badge/Hugging%20Face-Datasets-yellow.svg"></a>
</p>

## Overview

**Benchmark Radar** is a living registry, search engine, and discovery pipeline
for AI evaluation benchmarks. This dataset mirrors the full-corpus findings of the
Benchmark Radar technical report (*"Benchmark Radar: Daily Discovery and
Full-Corpus Search Across the AI Evaluation Landscape"*, arXiv:2609.11115).

As described in the paper's *Two Input Paths* framework, Benchmark Radar
combines two complementary systems:
1. **Catalog & Scores**: A curated, normalized cross-registry archive of
   **{catalog_count:,}** benchmark suites and **{scores_count:,}** reported
   model score observations across LLM Stats, OpenCompass Hub,
   Artificial Analysis, and premier model technical reports.
2. **Radar Discoveries**: A 24/7 automated intelligence pipeline tracking emerging
   papers, code repositories, datasets, and community attention across 37+ sources,
   capturing **{artifacts_count:,}** research artifacts and **{observations_count:,}**
   daily observations.

---

## Dataset Structure & Usage

The dataset is partitioned into 4 configs (subsets), easily loaded via
Hugging Face `datasets`:

```python
from datasets import load_dataset

# 1. Load benchmark catalog (default)
catalog = load_dataset("ktwu01/benchmark-radar", "catalog")

# 2. Load model evaluation scores
scores = load_dataset("ktwu01/benchmark-radar", "scores")

# 3. Load emerging radar artifacts (papers, repositories, datasets)
artifacts = load_dataset("ktwu01/benchmark-radar", "radar_artifacts")

# 4. Load daily discovery observations (attention, downloads, events)
observations = load_dataset("ktwu01/benchmark-radar", "radar_observations")
```

### 1. `catalog` (Default Config)
Contains {catalog_count:,} normalized benchmark records.
- `benchmark_id`: Canonical unique identifier (e.g. `llm-stats:mmlu-pro`, `opencompass:1580`)
- `slug`: URL-safe unique identifier
- `name`: Benchmark display name
- `source`: Source provider (`llm_stats`, `opencompass_hub`, `artificial_analysis`, `model_reports`)
- `source_url`: URL to original source entry
- `description`: Plaintext description and task summary
- `categories`: Assigned category tags (e.g. `Reasoning`, `Code`, `Multimodal`)
- `languages`: Languages evaluated (e.g. `en`, `zh`)
- `modality`: Evaluated modality (`text`, `multimodal`, `code`, etc.)
- `publisher`: Creator organization or research lab
- `released_at`: Official release date (YYYY-MM-DD proxy)
- `openness`: Data and code openness tier
- `paper_url`: Associated paper URL (arXiv or DOI)
- `repo_url`: Associated code repository URL (GitHub)
- `dataset_url`: Direct dataset download or Hub URL
- `document_count`: Number of verified source documents citing this benchmark
- `model_count`: Number of distinct models evaluated
- `score_count`: Number of numeric scores recorded
- `highest_score`: Maximum observed score across all evaluated models
- `score_unit`: Score metric / unit (e.g. `%`, `accuracy`, `Elo`)

### 2. `scores`
Contains {scores_count:,} reported evaluation score observations across 870+ frontier models.
- `obs_id`: Unique observation identifier
- `key`: Benchmark key
- `model_id`: Model slug
- `model_name`: Model display name
- `organization`: Model creator/lab (e.g. `DeepSeek`, `OpenAI`, `Anthropic`, `Google`, `Meta`)
- `value`: Numeric reported score
- `raw_value`: Original score string from source
- `value_kind`: Value data type (`number`, `percentage`, etc.)
- `reported_date`: Model announcement or report publication date
- `date_precision`: Precision level of reported date
- `reported_by`: Source reporting modality (`self_reported`, `evaluated`)
- `source`: Score ingestion source
- `source_url`: URL of source leaderboard or technical report
- `document_id`: Source document citation ID

### 3. `radar_artifacts`
Contains {artifacts_count:,} academic artifacts surfaced by daily radar.
- `id`: Artifact identifier (e.g. `artifact:arxiv:2203.17257`)
- `type`: Entity type (`artifact`)
- `label`: Title or repository name
- `url`: Primary external URL
- `categories`: Extracted capability categories
- `sources`: Discovery sources that observed this artifact
- `first_seen_at`: First discovery date (YYYY-MM-DD)
- `last_seen_at`: Latest discovery date (YYYY-MM-DD)
- `observation_count`: Total appearances across snapshots
- `latest_score`: Attention and composite radar score
- `metrics`: Dictionary of observed signals (e.g. stars, citations, downloads)

### 4. `radar_observations`
Contains {observations_count:,} discrete daily discovery events.
- `id`: Observation identifier
- `entity_id`: Referenced artifact ID
- `snapshot_date`: Radar snapshot date (YYYY-MM-DD)
- `source`: Discovery source platform
- `source_id`: Upstream source identifier
- `url`: Surfaced event URL
- `discovered_at`: Timestamp of discovery
- `published_at`: Original creation / publication timestamp
- `total_score`: Radar composite relevance score
- `event_kind`: Event category (`new`, `updated`)
- `organizations`: Identified affiliated organizations
- `metrics`: Point-in-time metrics (stars, likes, downloads)

---

## Data Provenance and Principles

- **Full-Corpus Coverage**: All {catalog_count:,} benchmarks across all sources are preserved.
  Unscored benchmarks are retained with verified paper, code, and dataset links.
- **Strict Evidence Citation**: Every score links directly to its source document
  or technical report.
- **Daily Automated Sync**: Radar discoveries are refreshed daily at 05:00 UTC via GitHub Actions.

## Citation

```bibtex
@article{{benchmark_radar_2026,
  title={{Benchmark Radar: Daily Discovery and Full-Corpus Search
          Across the AI Evaluation Landscape}},
  author={{Wu, Koutian and Contributors}},
  journal={{arXiv preprint arXiv:2609.11115}},
  year={{2026}}
}}
```
"""
    return card.strip() + "\n"


def export_hf_dataset(
    output_dir: Path = DEFAULT_EXPORT_DIR,
    paths: QueryPaths | None = None,
) -> DatasetExportResult:
    """Export the benchmark catalog, scores, and radar snapshots to JSONL format.

    Files written:
    - `output_dir/README.md` (Dataset card with YAML metadata)
    - `output_dir/data/catalog.jsonl`
    - `output_dir/data/scores.jsonl`
    - `output_dir/data/radar_artifacts.jsonl`
    - `output_dir/data/radar_observations.jsonl`
    - `output_dir/manifest.json`
    """
    resolved_paths = paths or QueryPaths()
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load catalog index
    if not resolved_paths.index.exists():
        raise FileNotFoundError(
            f"Catalog index missing at {resolved_paths.index}; "
            "run `benchmark-radar normalize-catalog` first."
        )
    index_data = json.loads(resolved_paths.index.read_text(encoding="utf-8"))
    benchmarks = index_data.get("benchmarks", [])

    # 2. Extract catalog & scores
    catalog_rows = []
    score_rows = []

    for b in benchmarks:
        slug = b.get("slug", "")
        shard_path = resolved_paths.shards / f"{slug}.json"
        artifacts = []
        if shard_path.exists():
            shard = json.loads(shard_path.read_text(encoding="utf-8"))
            artifacts = shard.get("record", {}).get("artifacts", [])
            for _src, src_data in shard.get("scores_by_source", {}).items():
                for r in src_data.get("rows", []):
                    score_rows.append(r)

        paper_url = next(
            (a["url"] for a in artifacts if a.get("kind") == "paper"),
            None,
        )
        repo_url = next(
            (a["url"] for a in artifacts if a.get("kind") == "repo"),
            None,
        )
        dataset_url = next(
            (a["url"] for a in artifacts if a.get("kind") == "dataset"),
            None,
        )

        catalog_rows.append(
            {
                "benchmark_id": b.get("key"),
                "slug": b.get("slug"),
                "name": b.get("name"),
                "source": b.get("source"),
                "source_url": b.get("source_url"),
                "description": b.get("description"),
                "categories": b.get("categories", []),
                "languages": b.get("languages", []),
                "modality": b.get("modality"),
                "publisher": b.get("publisher"),
                "released_at": b.get("released"),
                "openness": b.get("openness"),
                "paper_url": paper_url,
                "repo_url": repo_url,
                "dataset_url": dataset_url,
                "document_count": (b.get("evidence_summary") or {}).get("document_count", 0),
                "model_count": (b.get("evidence_summary") or {}).get("model_count"),
                "score_count": b.get("score_count", 0),
                "highest_score": (b.get("score_summary") or {}).get("observed_max"),
                "score_unit": b.get("unit"),
            }
        )

    # 3. Extract radar artifacts & observations from radar.json
    radar_path = Path("site/data/radar.json")
    artifact_rows = []
    observation_rows = []
    if radar_path.exists():
        radar_data = json.loads(radar_path.read_text(encoding="utf-8"))
        corpus = radar_data.get("corpus", {})
        artifact_rows = [e for e in corpus.get("entities", []) if e.get("type") == "artifact"]
        observation_rows = corpus.get("observations", [])

    # 4. Write JSONL files
    catalog_file = data_dir / "catalog.jsonl"
    with catalog_file.open("w", encoding="utf-8") as f:
        for row in catalog_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    scores_file = data_dir / "scores.jsonl"
    with scores_file.open("w", encoding="utf-8") as f:
        for row in score_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    artifacts_file = data_dir / "radar_artifacts.jsonl"
    with artifacts_file.open("w", encoding="utf-8") as f:
        for row in artifact_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    observations_file = data_dir / "radar_observations.jsonl"
    with observations_file.open("w", encoding="utf-8") as f:
        for row in observation_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # 5. Write Dataset Card README.md
    readme_content = generate_dataset_card(
        catalog_count=len(catalog_rows),
        scores_count=len(score_rows),
        artifacts_count=len(artifact_rows),
        observations_count=len(observation_rows),
    )
    (output_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 6. Write Manifest
    manifest = {
        "version": "1.0.0",
        "paper_id": "2609.11115",
        "counts": {
            "catalog": len(catalog_rows),
            "scores": len(score_rows),
            "radar_artifacts": len(artifact_rows),
            "radar_observations": len(observation_rows),
        },
        "files": {
            "catalog": "data/catalog.jsonl",
            "scores": "data/scores.jsonl",
            "radar_artifacts": "data/radar_artifacts.jsonl",
            "radar_observations": "data/radar_observations.jsonl",
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return DatasetExportResult(
        export_dir=output_dir,
        catalog_count=len(catalog_rows),
        scores_count=len(score_rows),
        artifacts_count=len(artifact_rows),
        observations_count=len(observation_rows),
        manifest=manifest,
    )
