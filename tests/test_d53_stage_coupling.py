"""Tests for D53: stage coupling."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_coupling import (
    build_coupling, build_pair_counts, collect_file_stages, count_internal_edges
)


def test_collect_file_stages_empty(tmp_path: Path) -> None:
    assert collect_file_stages(tmp_path) == []


def test_build_pair_counts() -> None:
    file_stages = [["A", "B"], ["A", "C"]]
    pairs = build_pair_counts(file_stages)
    assert pairs[frozenset({"A", "B"})] == 1
    assert pairs[frozenset({"A", "C"})] == 1


def test_count_internal_edges() -> None:
    pairs = {frozenset({"A", "B"}): 2, frozenset({"B", "C"}): 1}
    assert count_internal_edges({"A", "B", "C"}, pairs) == 3


def test_build_coupling_empty() -> None:
    r = build_coupling({}, [])
    assert r.n_total_edges == 0
    assert r.modularity == 1.0


def test_build_coupling_one_cluster() -> None:
    pairs = {frozenset({"A", "B"}): 1, frozenset({"B", "C"}): 1}
    clusters = [{"A", "B", "C"}]
    r = build_coupling(pairs, clusters)
    assert r.n_cross_edges == 0
    assert r.modularity == 1.0
