"""Tests for D49: stage trend."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_trend import build_trend, _week_of, _linear_projection
from datetime import date


def test_week_of() -> None:
    # 2026-07-18 (Sat) is in W29
    # 2026-07-20 (Mon) starts W30
    assert _week_of(date(2026, 7, 18)) == "2026-W29"
    assert _week_of(date(2026, 7, 20)) == "2026-W30"


def test_linear_projection_flat() -> None:
    proj = _linear_projection([("W1", 5), ("W2", 5), ("W3", 5)])
    assert proj == 5


def test_linear_projection_growing() -> None:
    proj = _linear_projection([("W1", 1), ("W2", 2), ("W3", 3)])
    assert proj == 4


def test_build_trend_empty(tmp_path: Path) -> None:
    r = build_trend(tmp_path)
    assert r.n_weeks == 0


def test_build_trend_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text("## D1\n", encoding="utf-8")
    # 2026-07-22 is in W30 (crosses week boundary)
    (md / "2026-07-22.md").write_text("## D2\n", encoding="utf-8")
    r = build_trend(md)
    assert r.n_weeks == 2
