"""Tests for D58: stage calendar."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_calendar import collect_calendar, _WEEKDAY_NAMES


def test_weekday_names() -> None:
    assert _WEEKDAY_NAMES == ["Mon", "Tue", "Wed", "Thu", "Fri",
                                "Sat", "Sun"]


def test_collect_calendar_empty(tmp_path: Path) -> None:
    r = collect_calendar(tmp_path)
    assert r.n_active_days == 0


def test_collect_calendar_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-19.md").write_text(
        "## D1\n## D2\n## D3\n", encoding="utf-8")
    r = collect_calendar(md)
    assert r.n_active_days == 1
    assert r.n_total_mentions == 3
    # 2026-07-19 is Sunday
    assert r.per_weekday["Sun"] == 3
