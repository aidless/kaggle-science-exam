"""Tests for D56: stage density curve."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_density_curve import collect_curves, _quartile_shares


def test_quartile_shares_empty() -> None:
    assert _quartile_shares([]) == (0.0, 0.0, 0.0)


def test_quartile_shares_one_day() -> None:
    assert _quartile_shares([3]) == (1.0, 0.0, 0.0)


def test_quartile_shares_four_equal() -> None:
    fq, m, lq = _quartile_shares([1, 1, 1, 1])
    assert abs(fq - 0.25) < 1e-9
    assert abs(m - 0.5) < 1e-9
    assert abs(lq - 0.25) < 1e-9


def test_collect_curves_empty(tmp_path: Path) -> None:
    assert collect_curves(tmp_path) == []


def test_collect_curves_one_day(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text("## D1\n", encoding="utf-8")
    curves = collect_curves(md)
    assert len(curves) == 1
    assert curves[0].first_quarter_share == 1.0
