"""Tests for D55: stage velocity."""
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_velocity import collect_velocity, _epochs


def test_epochs_empty() -> None:
    assert _epochs([]) == []


def test_epochs_three_consecutive() -> None:
    eps = _epochs([date(2026, 7, 18), date(2026, 7, 19),
                    date(2026, 7, 20)])
    assert len(eps) == 1
    assert len(eps[0]) == 3


def test_epochs_with_gap() -> None:
    eps = _epochs([date(2026, 7, 18), date(2026, 7, 19),
                    date(2026, 7, 22), date(2026, 7, 23)])
    assert len(eps) == 2
    assert [len(e) for e in eps] == [2, 2]


def test_collect_velocity_empty(tmp_path: Path) -> None:
    assert collect_velocity(tmp_path) == []


def test_collect_velocity_one_epoch(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    for i in range(3):
        (md / f"2026-07-{18 + i:02d}.md").write_text(
            "## D1\n", encoding="utf-8")
    entries = collect_velocity(md)
    assert entries[0].n_days == 3
    assert entries[0].n_epochs == 1
