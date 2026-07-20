"""Tests for D45: stage timeline."""
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_timeline import build_timeline, _normalize_did, _median


def test_normalize_did() -> None:
    assert _normalize_did("D1") == "D01"
    assert _normalize_did("D10") == "D10"
    assert _normalize_did("XX") == "XX"


def test_median() -> None:
    assert _median([1, 2, 3]) == 2.0
    assert _median([1, 2, 3, 4]) == 2.5
    assert _median([]) == 0.0


def test_build_timeline_empty(tmp_path: Path) -> None:
    r = build_timeline(tmp_path)
    assert r.n_stages == 0


def test_build_timeline_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text("## D1\n", encoding="utf-8")
    (md / "2026-07-19.md").write_text("## D2\n", encoding="utf-8")
    r = build_timeline(md)
    assert r.n_stages == 2
    assert "D01" in r.first_seen
    assert "D02" in r.first_seen
