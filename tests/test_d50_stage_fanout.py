"""Tests for D50: stage fanout."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_fanout import (
    build_fanout, build_pair_counts, collect_file_stages, jaccard
)


def test_collect_file_stages_empty(tmp_path: Path) -> None:
    assert collect_file_stages(tmp_path) == []


def test_build_pair_counts_basic() -> None:
    file_stages = [["D1", "D2"], ["D1", "D2"]]
    pairs = build_pair_counts(file_stages)
    assert pairs[frozenset({"D1", "D2"})] == 2


def test_jaccard_basic() -> None:
    pairs = {frozenset({"A", "B"}): 1, frozenset({"A", "C"}): 2,
              frozenset({"B", "C"}): 2}
    # jaccard(A, B) = 1 / (1 + 2 + 2 - 1) = 1/5 = 0.2
    j = jaccard("A", "B", pairs)
    assert abs(j - 0.2) < 1e-9


def test_build_fanout_empty(tmp_path: Path) -> None:
    r = build_fanout(tmp_path)
    assert r.n_files == 0


def test_build_fanout_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text(
        "## D1\n## D2\n", encoding="utf-8")
    (md / "2026-07-19.md").write_text(
        "## D1\n## D3\n", encoding="utf-8")
    r = build_fanout(md)
    assert r.n_files == 2
    assert r.n_pairs >= 1
