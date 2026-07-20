"""Tests for D52: stage backlog."""
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_backlog import (
    build_backlog, _normalize_did, _scan_project_stages, _scan_readme_stages
)


def test_normalize_did() -> None:
    assert _normalize_did("D1") == "D01"
    assert _normalize_did("D10") == "D10"


def test_scan_project_stages_empty(tmp_path: Path) -> None:
    assert _scan_project_stages(tmp_path) == set()


def test_scan_project_stages_basic(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("## D1\n", encoding="utf-8")
    assert "D01" in _scan_project_stages(tmp_path)


def test_build_backlog_basic(tmp_path: Path) -> None:
    md = tmp_path / "memory"
    md.mkdir()
    (md / "2026-07-18.md").write_text("## D1\n## D2\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("## D1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("**D1**\n", encoding="utf-8")
    backlog, bonus = build_backlog(
        memory_dir=md, readme_path=tmp_path / "README.md",
        project_root=tmp_path, today=date(2026, 7, 19),
    )
    # D2 in memory but not in code/readme -> backlog
    ids = [b.id for b in backlog]
    assert "D02" in ids
