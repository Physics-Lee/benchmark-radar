import json
import re
from pathlib import Path

from benchmark_radar.hf_dataset import export_hf_dataset, generate_dataset_card
from benchmark_radar.query import QueryPaths


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
    import pytest

    output_dir = tmp_path / "hf_dataset"
    index_file = tmp_path / "index.json"
    shards_dir = tmp_path / "shards"
    shards_dir.mkdir(parents=True, exist_ok=True)
    index_file.write_text(
        json.dumps({"benchmarks": [{"slug": "missing-bench", "key": "test:bench"}]}),
        encoding="utf-8",
    )

    custom_paths = QueryPaths(index=index_file, shards=shards_dir)
    with pytest.raises(FileNotFoundError, match="Detail shard missing"):
        export_hf_dataset(output_dir=output_dir, paths=custom_paths)


def test_export_hf_dataset_rejects_key_mismatch(tmp_path: Path):
    import pytest

    output_dir = tmp_path / "hf_dataset"
    index_file = tmp_path / "index.json"
    shards_dir = tmp_path / "shards"
    shards_dir.mkdir(parents=True, exist_ok=True)
    index_file.write_text(
        json.dumps({"benchmarks": [{"slug": "bench-1", "key": "expected:key"}]}),
        encoding="utf-8",
    )
    shard_file = shards_dir / "bench-1.json"
    shard_file.write_text(
        json.dumps({"record": {"key": "mismatched:key"}}),
        encoding="utf-8",
    )

    custom_paths = QueryPaths(index=index_file, shards=shards_dir)
    with pytest.raises(ValueError, match="key mismatch"):
        export_hf_dataset(output_dir=output_dir, paths=custom_paths)
