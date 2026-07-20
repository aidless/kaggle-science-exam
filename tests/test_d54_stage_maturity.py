"""Tests for D54: stage maturity."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_maturity import build_maturity, _normalize_did


def test_normalize_did() -> None:
    assert _normalize_did("D1") == "D01"
    assert _normalize_did("D10") == "D10"


def test_build_maturity_empty(tmp_path: Path) -> None:
    assert build_maturity(memory_dir=tmp_path / "no_mem",
                            project_root=tmp_path) == []


def test_build_maturity_full(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text("## D1\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("## D1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("**D1**\n", encoding="utf-8")
    items = build_maturity(memory_dir=md, project_root=tmp_path)
    assert len(items) == 1
    assert items[0].score == 3
