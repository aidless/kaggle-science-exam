"""Tests for D51: stage clusters."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_clusters import (
    build_clusters, count_internal_edges, greedy_cluster
)


def test_greedy_cluster_empty() -> None:
    assert greedy_cluster({}, set()) == []


def test_greedy_cluster_basic() -> None:
    pairs = {frozenset({"A", "B"}): 2, frozenset({"B", "C"}): 1}
    clusters = greedy_cluster(pairs, {"A", "B", "C"})
    # AB has higher count -> forms first; B-C adds C to same cluster
    assert len(clusters) == 1
    assert clusters[0] == {"A", "B", "C"}


def test_count_internal_edges() -> None:
    pairs = {frozenset({"A", "B"}): 1, frozenset({"B", "C"}): 2}
    assert count_internal_edges({"A", "B", "C"}, pairs) == 3


def test_build_clusters_empty(tmp_path: Path) -> None:
    clusters, stats, n_files, n_pairs, n_total, density, n_singletons = (
        build_clusters(tmp_path))
    assert clusters == []


def test_build_clusters_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text(
        "## D1\n## D2\n", encoding="utf-8")
    (md / "2026-07-19.md").write_text(
        "## D1\n## D2\n", encoding="utf-8")
    clusters, stats, n_files, n_pairs, n_total, density, n_singletons = (
        build_clusters(md))
    assert n_files == 2
    assert len(clusters) >= 1
