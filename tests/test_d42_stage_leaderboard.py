"""Tests for D42: stage leaderboard."""
import json
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_leaderboard import build_leaderboard


def test_build_leaderboard_empty(tmp_path: Path) -> None:
    r = build_leaderboard(tmp_path)
    assert r.n_unique_stages == 0


def test_build_leaderboard_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text(
        "## D1\n## D1\n## D2\n", encoding="utf-8")
    (md / "2026-07-19.md").write_text("## D1\n", encoding="utf-8")
    r = build_leaderboard(md, today=date(2026, 7, 20))
    assert r.n_unique_stages == 2
    assert r.n_one_shot == 1  # D2
    assert r.n_repeat == 1  # D1
    assert r.top_20[0][0] == "D01"  # most mentioned (normalized)
