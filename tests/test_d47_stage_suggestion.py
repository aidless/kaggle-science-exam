"""Tests for D47: stage suggestion."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_suggestion import collect_suggestions


def test_collect_suggestions_empty(tmp_path: Path) -> None:
    assert collect_suggestions(tmp_path) == []


def test_collect_suggestions_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text(
        "## D1\n## D2\n## D3\n", encoding="utf-8")
    suggestions = collect_suggestions(md)
    assert len(suggestions) >= 1
    # Always suggests a "next" stage
    types = {s["type"] for s in suggestions}
    assert "next" in types
