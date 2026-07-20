"""Tests for D43: stage grep."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_grep import build_grep, scan_directory


def test_scan_directory_empty(tmp_path: Path) -> None:
    assert scan_directory(tmp_path) == []


def test_scan_directory_basic(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("## D1\n## D2\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("## D1\n", encoding="utf-8")
    out = scan_directory(tmp_path)
    assert len(out) == 2


def test_build_grep_basic(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text(
        "## D1\n## D2\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "t.py").write_text("## D1\n", encoding="utf-8")
    r = build_grep(tmp_path)
    assert r.n_files >= 2
    assert r.n_distinct_stages >= 2
    assert "D01" in r.per_stage
