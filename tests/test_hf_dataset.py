import json
import re
from pathlib import Path

import pytest

import benchmark_radar.hf_dataset as hf_dataset
from benchmark_radar.corpus import CorpusError
from benchmark_radar.hf_dataset import export_hf_dataset, generate_dataset_card
from benchmark_radar.query import QueryError, QueryPaths


def _write_catalog(
    root: Path,
    *,
    key: str = "test:bench",
    slug: str = "test-bench",
    shard_key: str | None = None,
) -> QueryPaths:
    index_file = root / "benchmark-index.json"
    shards_dir = root / "benchmarks"
    shards_dir.mkdir(parents=True, exist_ok=True)
    benchmark = {
        "key": key,
        "slug": slug,
        "name": "Test benchmark",
        "source": "llm_stats",
        "description": "A test benchmark.",
        "categories": [],
        "languages": [],
        "has_paper": False,
        "has_repo": False,
        "has_dataset": False,
        "has_size": False,
    }
    index_file.write_text(
        json.dumps({"schema_version": 1, "count": 1, "benchmarks": [benchmark]}),
        encoding="utf-8",
    )
    if shard_key is not None:
        (shards_dir / f"{slug}.json").write_text(
            json.dumps({"record": {"key": shard_key}}),
            encoding="utf-8",
        )
    return QueryPaths(index=index_file, shards=shards_dir)


def _allow_tiny_test_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hf_dataset, "MIN_CATALOG_RECORDS", 1)
    monkeypatch.setattr(hf_dataset, "REQUIRED_CATALOG_SOURCES", frozenset({"llm_stats"}))


def test_generate_dataset_card():
    card = generate_dataset_card(
        catalog_count=1284,
        scores_count=12929,
        artifacts_count=8577,
        observations_count=14814,
    )
    assert card.startswith("---\n")
    assert "configs:" in card
    assert "config_name: default" in card
    assert "config_name: catalog" in card
    assert "config_name: scores" in card
    assert "config_name: radar_artifacts" in card
    assert "config_name: radar_observations" in card
    assert "2609.11115" in card
    assert "1,284" in card
    assert "12,929" in card
    assert "license: other" in card
    assert "license: apache-2.0" not in card
    assert "LICENSE-CONTENT.md" in card


def test_export_hf_dataset(tmp_path: Path):
    output_dir = tmp_path / "hf_dataset"
    paths = QueryPaths()

    result = export_hf_dataset(output_dir=output_dir, paths=paths)

    # Invariants
    assert result.export_dir == output_dir
    # Full corpus principle: catalog >= 1,259
    assert result.catalog_count >= 1259
    assert result.scores_count > 10000
    assert result.artifacts_count > 5000
    assert result.observations_count > 10000

    # File existence
    data_dir = output_dir / "data"
    assert (output_dir / "README.md").is_file()
    assert (output_dir / "manifest.json").is_file()
    assert (data_dir / "catalog.jsonl").is_file()
    assert (data_dir / "scores.jsonl").is_file()
    assert (data_dir / "radar_artifacts.jsonl").is_file()
    assert (data_dir / "radar_observations.jsonl").is_file()

    # Verify JSONL lines match counts
    with (data_dir / "catalog.jsonl").open(encoding="utf-8") as f:
        catalog_lines = [json.loads(line) for line in f]
    assert len(catalog_lines) == result.catalog_count
    first_catalog = catalog_lines[0]
    assert "benchmark_id" in first_catalog
    assert "name" in first_catalog
    assert "source" in first_catalog
    assert {row["source"] for row in catalog_lines} >= hf_dataset.REQUIRED_CATALOG_SOURCES
    scored_catalog = [row for row in catalog_lines if row["score_count"] > 0]
    assert scored_catalog
    assert any(row["highest_score"] is not None for row in scored_catalog)

    with (data_dir / "scores.jsonl").open(encoding="utf-8") as f:
        score_lines = [json.loads(line) for line in f]
    assert len(score_lines) == result.scores_count
    first_score = score_lines[0]
    assert "key" in first_score
    assert "model_name" in first_score
    assert "value" in first_score

    with (data_dir / "radar_artifacts.jsonl").open(encoding="utf-8") as f:
        artifact_lines = [json.loads(line) for line in f]
    assert len(artifact_lines) == result.artifacts_count

    with (data_dir / "radar_observations.jsonl").open(encoding="utf-8") as f:
        obs_lines = [json.loads(line) for line in f]
    assert len(obs_lines) == result.observations_count

    # Verify YAML frontmatter in README.md matches configs
    readme_text = (output_dir / "README.md").read_text(encoding="utf-8")
    frontmatter_match = re.search(r"^---\n(.*?)\n---", readme_text, re.DOTALL)
    assert frontmatter_match is not None


def test_export_hf_dataset_rejects_missing_shard(tmp_path: Path):
    output_dir = tmp_path / "hf_dataset"
    custom_paths = _write_catalog(tmp_path, slug="missing-bench")
    with pytest.raises(QueryError, match="benchmark detail shard is missing"):
        export_hf_dataset(output_dir=output_dir, paths=custom_paths)


def test_export_hf_dataset_rejects_key_mismatch(tmp_path: Path):
    output_dir = tmp_path / "hf_dataset"
    custom_paths = _write_catalog(
        tmp_path,
        key="expected:key",
        slug="bench-1",
        shard_key="mismatched:key",
    )
    with pytest.raises(QueryError, match="does not match catalog key"):
        export_hf_dataset(output_dir=output_dir, paths=custom_paths)


def test_export_hf_dataset_rejects_empty_index(tmp_path: Path):
    output_dir = tmp_path / "hf_dataset"
    index_file = tmp_path / "index.json"
    shards_dir = tmp_path / "shards"
    shards_dir.mkdir(parents=True, exist_ok=True)
    index_file.write_text(
        json.dumps({"schema_version": 1, "count": 0, "benchmarks": []}),
        encoding="utf-8",
    )

    custom_paths = QueryPaths(index=index_file, shards=shards_dir)
    with pytest.raises(ValueError, match="contains no benchmarks"):
        export_hf_dataset(output_dir=output_dir, paths=custom_paths)


def test_export_hf_dataset_binds_radar_to_custom_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    output_dir = tmp_path / "hf_dataset"
    custom_dir = tmp_path / "custom_site"
    custom_paths = _write_catalog(custom_dir, key="test:b1", slug="b1", shard_key="test:b1")
    _allow_tiny_test_catalog(monkeypatch)
    # Expected radar_file at custom_dir / "radar.json", which does not exist
    with pytest.raises(FileNotFoundError, match="Radar corpus missing at .*custom_site/radar.json"):
        export_hf_dataset(output_dir=output_dir, paths=custom_paths)


def test_export_hf_dataset_rejects_malformed_radar_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    custom_dir = tmp_path / "custom_site"
    custom_paths = _write_catalog(
        custom_dir,
        key="test:b1",
        slug="b1",
        shard_key="test:b1",
    )
    (custom_dir / "radar.json").write_text(json.dumps({"corpus": {}}), encoding="utf-8")
    _allow_tiny_test_catalog(monkeypatch)

    with pytest.raises(CorpusError, match="entities must be an array of objects"):
        export_hf_dataset(output_dir=tmp_path / "hf_dataset", paths=custom_paths)


def test_export_hf_dataset_rejects_radar_count_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    custom_dir = tmp_path / "custom_site"
    custom_paths = _write_catalog(custom_dir, shard_key="test:bench")
    payload_hash = "sha256:" + "a" * 64
    corpus = {
        "schema_version": 1,
        "entity_count": 2,
        "observation_count": 1,
        "edge_count": 0,
        "entities": [
            {
                "id": "artifact:test",
                "type": "artifact",
                "url": "https://example.com/artifact",
                "parser_versions": ["test/1"],
                "raw_payload_hashes": [payload_hash],
            }
        ],
        "observations": [
            {
                "id": "observation:test",
                "entity_id": "artifact:test",
                "url": "https://example.com/observation",
                "published_at": "2026-09-15T00:00:00Z",
                "retrieved_at": "2026-09-15T00:00:00Z",
                "parser_version": "test/1",
                "raw_payload_hash": payload_hash,
            }
        ],
        "edges": [],
        "aggregates": {"entity_types": {"artifact": 1}},
    }
    (custom_dir / "radar.json").write_text(json.dumps({"corpus": corpus}), encoding="utf-8")
    _allow_tiny_test_catalog(monkeypatch)

    with pytest.raises(CorpusError, match="entity_count does not match"):
        export_hf_dataset(output_dir=tmp_path / "hf_dataset", paths=custom_paths)


def test_export_hf_dataset_rejects_truncated_catalog(tmp_path: Path):
    custom_paths = _write_catalog(tmp_path, shard_key="test:bench")

    with pytest.raises(ValueError, match="expected at least 1259"):
        export_hf_dataset(output_dir=tmp_path / "hf_dataset", paths=custom_paths)
