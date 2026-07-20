"""
End-to-end smoke test for the Kaggle Science Exam analysis tools.

Runs each `src/analysis/*.py` CLI against a synthetic memory dir
and asserts the outputs exist and contain expected content.

This is a simplified reconstruction covering D41-D58 stages. Each
test corresponds to a smoke "stage" in the project pipeline.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_subprocess(cmd: list, cwd: Path = None) -> tuple:
    """Run subprocess and return (returncode, stdout, stderr)."""
    r = subprocess.run(cmd, capture_output=True, text=True,
                         cwd=str(cwd) if cwd else str(ROOT))
    return r.returncode, r.stdout, r.stderr


def synth_memory() -> Path:
    """Create a synthetic memory dir with 7 days of activity."""
    p = Path(tempfile.mkdtemp()) / "memory"
    p.mkdir(parents=True)
    # Day 1: D1, D2
    (p / "2026-07-18.md").write_text(
        "## D1\n## D2\n## D3\n", encoding="utf-8")
    # Day 2: D1, D4
    (p / "2026-07-19.md").write_text(
        "## D1\n## D4\n", encoding="utf-8")
    # Day 3: D2, D5
    (p / "2026-07-20.md").write_text(
        "## D2\n## D5\n", encoding="utf-8")
    # Day 4: D1, D6
    (p / "2026-07-21.md").write_text(
        "## D1\n## D6\n", encoding="utf-8")
    # Day 5: D1
    (p / "2026-07-22.md").write_text("## D1\n", encoding="utf-8")
    return p


def step_unit(n: int, total: int, test_name: str) -> None:
    print(f"\n[{n}/{total}] {test_name}")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/{test_name}", "-v", "-q"],
        capture_output=True, text=True, cwd=str(ROOT))
    print(r.stdout[-500:] if r.stdout else "")
    if r.returncode != 0:
        print("STDERR:", r.stderr[-500:])
    assert r.returncode == 0, f"{test_name} failed"


def main() -> int:
    sh_p = Path(tempfile.mkdtemp())
    sh_md = synth_memory()
    total = 18  # D41-D58 = 18 stages
    # ----- D41: stage streak -----
    step_unit(1, total, "test_d41_stage_streak.py")
    # ----- D42: stage leaderboard -----
    step_unit(2, total, "test_d42_stage_leaderboard.py")
    # ----- D43: stage grep -----
    step_unit(3, total, "test_d43_stage_grep.py")
    # ----- D44: stage coverage -----
    step_unit(4, total, "test_d44_stage_coverage.py")
    # ----- D45: stage timeline -----
    step_unit(5, total, "test_d45_stage_timeline.py")
    # ----- D46: stage cadence -----
    step_unit(6, total, "test_d46_stage_cadence.py")
    # ----- D47: stage suggestion -----
    step_unit(7, total, "test_d47_stage_suggestion.py")
    # ----- D48: stage summary -----
    step_unit(8, total, "test_d48_stage_summary.py")
    # ----- D49: stage trend -----
    step_unit(9, total, "test_d49_stage_trend.py")
    # ----- D50: stage fanout -----
    step_unit(10, total, "test_d50_stage_fanout.py")
    # ----- D51: stage clusters -----
    step_unit(11, total, "test_d51_stage_clusters.py")
    # ----- D52: stage backlog -----
    step_unit(12, total, "test_d52_stage_backlog.py")
    # ----- D53: stage coupling -----
    step_unit(13, total, "test_d53_stage_coupling.py")
    # ----- D54: stage maturity -----
    step_unit(14, total, "test_d54_stage_maturity.py")
    # ----- D55: stage velocity -----
    step_unit(15, total, "test_d55_stage_velocity.py")
    # ----- D56: stage density curve -----
    step_unit(16, total, "test_d56_stage_density_curve.py")
    # ----- D57: stage distribution -----
    step_unit(17, total, "test_d57_stage_distribution.py")
    # ----- D58: stage calendar -----
    step_unit(18, total, "test_d58_stage_calendar.py")

    # ----- D41 CLI: stage_streak -----
    print(f"\n[{total}/{total}] stage_streak CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_streak",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "streak.md"),
        "--out_json", str(sh_p / "streak.json"),
    ])
    assert rc == 0, f"stage_streak CLI failed: {stderr}"

    # ----- D42 CLI: stage_leaderboard -----
    print(f"\n[{total}/{total}] stage_leaderboard CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_leaderboard",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "lb.md"),
        "--out_json", str(sh_p / "lb.json"),
    ])
    assert rc == 0, f"stage_leaderboard CLI failed: {stderr}"

    # ----- D43 CLI: stage_grep -----
    print(f"\n[{total}/{total}] stage_grep CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_grep",
        "--project_root", str(ROOT),
        "--out", str(sh_p / "grep.md"),
        "--out_json", str(sh_p / "grep.json"),
    ])
    assert rc == 0, f"stage_grep CLI failed: {stderr}"

    # ----- D44 CLI: stage_coverage -----
    print(f"\n[{total}/{total}] stage_coverage CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_coverage",
        "--project_root", str(ROOT),
        "--out", str(sh_p / "cov.md"),
        "--out_json", str(sh_p / "cov.json"),
    ])
    assert rc == 0, f"stage_coverage CLI failed: {stderr}"

    # ----- D45 CLI: stage_timeline -----
    print(f"\n[{total}/{total}] stage_timeline CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_timeline",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "tl.md"),
        "--out_json", str(sh_p / "tl.json"),
    ])
    assert rc == 0, f"stage_timeline CLI failed: {stderr}"
    text = (sh_p / "tl.md").read_text(encoding="utf-8")
    assert "Stage Timeline" in text
    j = json.loads((sh_p / "tl.json").read_text(encoding="utf-8"))
    assert j["report"]["n_stages"] >= 6

    # ----- D46 CLI: stage_cadence -----
    print(f"\n[{total}/{total}] stage_cadence CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_cadence",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "cd.md"),
        "--out_json", str(sh_p / "cd.json"),
    ])
    assert rc == 0, f"stage_cadence CLI failed: {stderr}"

    # ----- D47 CLI: stage_suggestion -----
    print(f"\n[{total}/{total}] stage_suggestion CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_suggestion",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "sg.md"),
        "--out_json", str(sh_p / "sg.json"),
    ])
    assert rc == 0, f"stage_suggestion CLI failed: {stderr}"

    # ----- D48 CLI: stage_summary -----
    print(f"\n[{total}/{total}] stage_summary CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_summary",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "sm.md"),
        "--out_json", str(sh_p / "sm.json"),
    ])
    assert rc == 0, f"stage_summary CLI failed: {stderr}"

    # ----- D49 CLI: stage_trend -----
    print(f"\n[{total}/{total}] stage_trend CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_trend",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "tr.md"),
        "--out_json", str(sh_p / "tr.json"),
    ])
    assert rc == 0, f"stage_trend CLI failed: {stderr}"

    # ----- D50 CLI: stage_fanout -----
    print(f"\n[{total}/{total}] stage_fanout CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_fanout",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "fo.md"),
        "--out_json", str(sh_p / "fo.json"),
    ])
    assert rc == 0, f"stage_fanout CLI failed: {stderr}"

    # ----- D51 CLI: stage_clusters -----
    print(f"\n[{total}/{total}] stage_clusters CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_clusters",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "cl.md"),
        "--out_json", str(sh_p / "cl.json"),
    ])
    assert rc == 0, f"stage_clusters CLI failed: {stderr}"

    # ----- D52 CLI: stage_backlog -----
    print(f"\n[{total}/{total}] stage_backlog CLI")
    bl_p = sh_p / "bl_proj"
    bl_p.mkdir()
    (bl_p / "src").mkdir()
    (bl_p / "src" / "x.py").write_text("## D1\n", encoding="utf-8")
    (bl_p / "README.md").write_text("**D1**\n", encoding="utf-8")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_backlog",
        "--memory_dir", str(sh_md),
        "--readme", str(bl_p / "README.md"),
        "--project_root", str(bl_p),
        "--out", str(sh_p / "bl.md"),
        "--out_json", str(sh_p / "bl.json"),
    ])
    assert rc == 0, f"stage_backlog CLI failed: {stderr}"

    # ----- D53 CLI: stage_coupling -----
    print(f"\n[{total}/{total}] stage_coupling CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_coupling",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "cp.md"),
        "--out_json", str(sh_p / "cp.json"),
    ])
    assert rc == 0, f"stage_coupling CLI failed: {stderr}"

    # ----- D54 CLI: stage_maturity -----
    print(f"\n[{total}/{total}] stage_maturity CLI")
    mt_p = sh_p / "mt_proj"
    mt_p.mkdir()
    (mt_p / "src").mkdir()
    (mt_p / "src" / "x.py").write_text("## D1\n", encoding="utf-8")
    (mt_p / "README.md").write_text("**D1**\n", encoding="utf-8")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_maturity",
        "--memory_dir", str(sh_md),
        "--readme", str(mt_p / "README.md"),
        "--project_root", str(mt_p),
        "--out", str(sh_p / "mt.md"),
        "--out_json", str(sh_p / "mt.json"),
    ])
    assert rc == 0, f"stage_maturity CLI failed: {stderr}"

    # ----- D55 CLI: stage_velocity -----
    print(f"\n[{total}/{total}] stage_velocity CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_velocity",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "vl.md"),
        "--out_json", str(sh_p / "vl.json"),
    ])
    assert rc == 0, f"stage_velocity CLI failed: {stderr}"

    # ----- D56 CLI: stage_density_curve -----
    print(f"\n[{total}/{total}] stage_density_curve CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_density_curve",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "dc.md"),
        "--out_json", str(sh_p / "dc.json"),
    ])
    assert rc == 0, f"stage_density_curve CLI failed: {stderr}"

    # ----- D57 CLI: stage_distribution -----
    print(f"\n[{total}/{total}] stage_distribution CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_distribution",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "ds.md"),
        "--out_json", str(sh_p / "ds.json"),
    ])
    assert rc == 0, f"stage_distribution CLI failed: {stderr}"

    # ----- D58 CLI: stage_calendar -----
    print(f"\n[{total}/{total}] stage_calendar CLI")
    rc, _, stderr = run_subprocess([
        sys.executable, "-m", "src.analysis.stage_calendar",
        "--memory_dir", str(sh_md),
        "--out", str(sh_p / "cl2.md"),
        "--out_json", str(sh_p / "cl2.json"),
    ])
    assert rc == 0, f"stage_calendar CLI failed: {stderr}"

    print("\n" + "=" * 64)
    print("ALL SMOKE TESTS PASSED (D41 - D58)")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
