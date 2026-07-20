"""Tests for D57: stage distribution."""
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_distribution import (
    build_distribution, collect_mentions, _gini
)


def test_gini_empty() -> None:
    assert _gini([]) == 0.0


def test_gini_all_equal() -> None:
    assert abs(_gini([3, 3, 3]) - 0.0) < 1e-9


def test_gini_dominant() -> None:
    g = _gini([1, 1, 1, 100])
    assert g > 0.5


def test_collect_mentions_empty(tmp_path: Path) -> None:
    assert collect_mentions(tmp_path) == Counter()


def test_collect_mentions_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text(
        "## D1\n## D1\n## D2\n", encoding="utf-8")
    m = collect_mentions(md)
    assert m["D1"] == 2
    assert m["D2"] == 1


def test_build_distribution_empty() -> None:
    r = build_distribution(Counter())
    assert r.n_stages == 0


def test_build_distribution_buckets() -> None:
    r = build_distribution(Counter({"A": 1, "B": 2, "C": 5, "D": 6}))
    assert r.buckets["1"] == 1
    assert r.buckets["2"] == 1
    assert r.buckets["5+"] == 2
