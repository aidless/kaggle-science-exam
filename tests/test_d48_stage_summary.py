"""Tests for D48: stage summary."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_summary import build_summary


def test_build_summary_empty(tmp_path: Path) -> None:
    r = build_summary(tmp_path)
    assert r.n_stages == 0
    assert r.health == "D"


def test_build_summary_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text(
        "## D1\n## D2\n## D3\n", encoding="utf-8")
    (md / "2026-07-19.md").write_text("## D1\n## D2\n", encoding="utf-8")
    r = build_summary(md)
    assert r.n_stages == 3
    assert r.n_total_mentions == 5
    assert r.n_active_days == 2
