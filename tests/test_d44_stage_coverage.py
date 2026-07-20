"""Tests for D44: stage coverage."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.analysis.stage_coverage import build_coverage


def test_build_coverage_empty(tmp_path: Path) -> None:
    r = build_coverage(tmp_path)
    assert r.n_stages == 0


def test_build_coverage_full(tmp_path: Path) -> None:
    (tmp_path / "src" / "analysis").mkdir(parents=True)
    (tmp_path / "src" / "analysis" / "a.py").write_text(
        "## D1\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text(
        "## D1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("**D1**\n", encoding="utf-8")
    (tmp_path / ".workbuddy" / "memory").mkdir(parents=True)
    (tmp_path / ".workbuddy" / "memory" / "2026-07-18.md").write_text(
        "## D1\n", encoding="utf-8")
    r = build_coverage(tmp_path)
    assert "D01" in r.details["project_stages"]
    assert "D01" in r.details["test_stages"]
    assert "D01" in r.details["documented"]
