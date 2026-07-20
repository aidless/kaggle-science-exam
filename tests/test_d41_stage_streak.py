"""Tests for D41: stage streak."""
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_streak import build_streak, _consecutive_run


def test_consecutive_run_empty() -> None:
    assert _consecutive_run([]) == 0


def test_consecutive_run_single() -> None:
    assert _consecutive_run([date(2026, 7, 18)]) == 1


def test_consecutive_run_three() -> None:
    assert _consecutive_run(
        [date(2026, 7, 18), date(2026, 7, 19), date(2026, 7, 20)]
    ) == 3


def test_consecutive_run_with_gap() -> None:
    assert _consecutive_run(
        [date(2026, 7, 18), date(2026, 7, 19),
         date(2026, 7, 22), date(2026, 7, 23)]
    ) == 2


def test_build_streak_empty(tmp_path: Path) -> None:
    r = build_streak(tmp_path)
    assert r.n_active_days == 0


def test_build_streak_three_consecutive(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    for i in range(3):
        (md / f"2026-07-{18 + i:02d}.md").write_text("## D1\n",
                                                         encoding="utf-8")
    r = build_streak(md, today=date(2026, 7, 20))
    assert r.n_active_days == 3
    assert r.longest_streak == 3
    assert r.current_streak == 3
