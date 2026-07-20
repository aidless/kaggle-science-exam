"""Tests for D46: stage cadence."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_cadence import build_cadence, _median


def test_median() -> None:
    assert _median([1, 2, 3]) == 2.0


def test_build_cadence_empty(tmp_path: Path) -> None:
    r = build_cadence(tmp_path)
    assert r.n_active_days == 0


def test_build_cadence_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text("## D1\n## D2\n", encoding="utf-8")
    (md / "2026-07-19.md").write_text("## D1\n", encoding="utf-8")
    r = build_cadence(md)
    assert r.n_active_days == 2
    assert r.n_total_mentions == 3
    assert r.n_unique_stages == 2
