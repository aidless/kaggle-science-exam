#!/usr/bin/env python3
"""Recompute the README claims and exit 1 if any of them drifted.

This script is the offline gate (`make check`). It does not call Kaggle,
does not read API keys, and does not invent counts: every pinned value is
either a subprocess result or a direct call into ``src.analysis``.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Policy threshold, not a measurement. The README claims block must cite it,
# and this run must finish inside it.
BUDGET_MINUTES = 15
SMOKE_BANNER = "ALL SMOKE TESTS PASSED (D41 - D58)"
PYTEST_CMD = "python3 -m pytest tests -q"
PINNED_FILES = (
    "README.md",
    "PAPER.md",
    "PREREG.md",
    "FAILURE_MODES.md",
)
RATIO_FILES = PINNED_FILES
DURATION_FILES = ("README.md", "PAPER.md", "PREREG.md")
CLAIM_KEYS = (
    "pytest_passed",
    "pytest_failed",
    "cli_modules",
    "smoke_cli_ok",
    "memory_logs",
    "summary_n_stages",
    "summary_n_total_mentions",
    "summary_n_orphans",
    "summary_n_active_days",
    "summary_health",
    "summary_health_score",
    "maturity_items",
    "committed_reports",
    "eval_passed",
    "eval_total",
    "eval_selftest_failed",
    "streak_stages_first_seen",
    "streak_longest",
    "streak_current",
    "streak_first_active_date",
    "streak_last_active_date",
    "check_budget_minutes",
)
DATE_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
HEADING_STAGE = re.compile(r"\bD\d+\b")
RATIO = re.compile(r"\d+(?:/\d+)+")
MODULE_ROW = re.compile(
    r"\|\s*D\d+\s*\|\s*`(src/analysis/stage_[A-Za-z0-9_]+\.py)`\s*\|"
)
NO_MEMORY_DIR_DEFAULT = {"stage_grep.py", "stage_coverage.py"}

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL: {msg}", file=sys.stderr)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=BUDGET_MINUTES * 60,
        check=False,
    )


def git_files() -> list[str]:
    proc = run(["git", "ls-files", "-z"])
    if proc.returncode != 0:
        fail(f"git ls-files failed: {proc.stderr.strip()}")
        return []
    return [p for p in proc.stdout.split("\0") if p]


def heading_mentions(memory_dir: Path) -> int:
    """README definition: stage ids on lines that start with ``##`` (not ``###``)."""
    n = 0
    for path in sorted(memory_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            if line.startswith("##") and not line.startswith("###"):
                n += len(HEADING_STAGE.findall(line))
    return n


def ast_test_count() -> int:
    n = 0
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        n += sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        )
    return n


def parse_claims(text: str) -> dict[str, str]:
    match = re.search(
        r"<!-- claims:start -->(.*)<!-- claims:end -->",
        text,
        re.DOTALL,
    )
    if not match:
        fail("README.md is missing the <!-- claims:start --> block")
        return {}
    found: dict[str, str] = {}
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        found[key.strip()] = value.strip()
    return found


def pinned_line(v: dict[str, str]) -> str:
    summary = (
        f"{v['summary_n_stages']}/{v['summary_n_total_mentions']}/"
        f"{v['summary_n_orphans']}/{v['summary_n_active_days']}"
    )
    return (
        "PINNED: "
        f"pytest_passed={v['pytest_passed']} "
        f"pytest_failed={v['pytest_failed']} "
        f"cli_modules={v['cli_modules']} "
        f"smoke_cli_ok={v['smoke_cli_ok']} "
        f"memory_logs={v['memory_logs']} "
        f"summary={summary} "
        f"health={v['summary_health']} "
        f"health_score={v['summary_health_score']} "
        f"maturity_items={v['maturity_items']} "
        f"committed_reports={v['committed_reports']} "
        f"eval={v['eval_passed']}/{v['eval_total']} "
        f"selftest_failed={v['eval_selftest_failed']} "
        f"streak_stages={v['streak_stages_first_seen']} "
        f"streak_longest={v['streak_longest']} "
        f"streak_current={v['streak_current']} "
        f"streak_first={v['streak_first_active_date']} "
        f"streak_last={v['streak_last_active_date']}"
    )


def claim_diffs(got: dict[str, str], claimed: dict[str, str]) -> list[str]:
    diffs: list[str] = []
    missing = [k for k in CLAIM_KEYS if k not in claimed]
    extra = sorted(set(claimed) - set(CLAIM_KEYS))
    if missing:
        diffs.append(f"claims block missing {missing}")
    if extra:
        diffs.append(f"claims block has unknown keys {extra}")
    for key in CLAIM_KEYS:
        if key in claimed and claimed[key] != got[key]:
            diffs.append(f"{key}: claims {claimed[key]!r} != recomputed {got[key]!r}")
    return diffs


def allowed_ratios(v: dict[str, str]) -> set[str]:
    selftest_passed = int(v["eval_total"]) - int(v["eval_selftest_failed"])
    summary = (
        f"{v['summary_n_stages']}/{v['summary_n_total_mentions']}/"
        f"{v['summary_n_orphans']}/{v['summary_n_active_days']}"
    )
    return {
        f"{v['smoke_cli_ok']}/{v['cli_modules']}",
        f"{v['eval_passed']}/{v['eval_total']}",
        f"{selftest_passed}/{v['eval_total']}",
        summary,
    }


def main() -> int:
    started = time.monotonic()
    from src.analysis.stage_maturity import build_maturity
    from src.analysis.stage_streak import build_streak
    from src.analysis.stage_summary import build_summary

    modules = sorted((ROOT / "src" / "analysis").glob("stage_*.py"))
    module_names = {p.stem for p in modules}
    memory_dir = ROOT / ".workbuddy" / "memory"
    all_md = sorted(memory_dir.glob("*.md")) if memory_dir.is_dir() else []
    dated = [p for p in all_md if DATE_NAME.match(p.name)]
    if len(all_md) != len(dated):
        fail("memory dir has markdown files that are not YYYY-MM-DD.md")

    summary = build_summary(memory_dir)
    streak = build_streak(memory_dir)
    maturity = build_maturity(memory_dir=memory_dir, project_root=ROOT)
    mentions = heading_mentions(memory_dir)
    if mentions != summary.n_total_mentions:
        fail(
            "heading-line stage count "
            f"{mentions} != build_summary.n_total_mentions {summary.n_total_mentions}"
        )
    if summary.n_active_days != len(dated):
        fail(
            f"build_summary.n_active_days {summary.n_active_days} != "
            f"dated memory files {len(dated)}"
        )
    if streak.n_active_days != len(dated):
        fail(
            f"build_streak.n_active_days {streak.n_active_days} != "
            f"dated memory files {len(dated)}"
        )

    tracked = git_files()
    report_files = [p for p in tracked if p == "report" or p.startswith("report/")]
    submissions = [p for p in tracked if Path(p).name == "submission.zip"]
    if submissions:
        fail(f"submission.zip is tracked: {submissions}")

    pytest_proc = run([sys.executable, "-m", "pytest", "tests", "-q", "--tb=line"])
    pytest_out = (pytest_proc.stdout or "") + "\n" + (pytest_proc.stderr or "")
    passed_m = re.search(r"(\d+) passed", pytest_out)
    failed_m = re.search(r"(\d+) failed", pytest_out)
    pytest_passed = int(passed_m.group(1)) if passed_m else -1
    pytest_failed = int(failed_m.group(1)) if failed_m else 0
    if pytest_proc.returncode != 0 or passed_m is None or pytest_failed != 0:
        fail(
            "pytest did not report a clean pass "
            f"(exit {pytest_proc.returncode}):\n{pytest_out[-1500:]}"
        )
    collected = ast_test_count()
    if collected != pytest_passed:
        fail(f"AST test_ functions {collected} != pytest passed {pytest_passed}")

    smoke_proc = run([sys.executable, "tests/smoke_test.py"])
    smoke_out = (smoke_proc.stdout or "") + "\n" + (smoke_proc.stderr or "")
    cli_hits = re.findall(
        r"^\[(\d+)/(\d+)\] (stage_[A-Za-z0-9_]+) CLI\s*$",
        smoke_out,
        re.MULTILINE,
    )
    cli_names = [name for _, _, name in cli_hits]
    if smoke_proc.returncode != 0 or SMOKE_BANNER not in smoke_out:
        fail(
            "smoke did not pass "
            f"(exit {smoke_proc.returncode}); banner present="
            f"{SMOKE_BANNER in smoke_out}"
        )
    if len(cli_names) != len(set(cli_names)) or set(cli_names) != module_names:
        fail(f"smoke CLI names {sorted(cli_names)} != modules {sorted(module_names)}")
    for left, right, _name in cli_hits:
        if left != right or int(right) != len(modules):
            fail(f"smoke progress [{left}/{right}] does not match {len(modules)} modules")
            break

    eval_proc = run([sys.executable, "eval/run_cases.py", "--json"])
    eval_payload: dict = {}
    try:
        eval_payload = json.loads(eval_proc.stdout)
    except json.JSONDecodeError:
        fail(f"eval JSON was not parseable:\n{eval_proc.stdout[-1500:]}")
    if eval_proc.returncode != 0 or eval_payload.get("failed") != 0:
        fail(
            "eval cases failed "
            f"(exit {eval_proc.returncode}): {eval_payload.get('failed_by_axis')}"
        )
    self_proc = run([sys.executable, "eval/run_cases.py", "--selftest", "--json"])
    self_payload: dict = {}
    try:
        self_payload = json.loads(self_proc.stdout)
    except json.JSONDecodeError:
        fail(f"selftest JSON was not parseable:\n{self_proc.stdout[-1500:]}")
    self_failed = int(self_payload.get("failed", -1))
    if self_proc.returncode != 0 or self_failed != 1:
        fail(
            "eval selftest must fail exactly 1 case and exit 0 "
            f"(exit {self_proc.returncode}, failed {self_failed})"
        )

    report_path = ROOT / "eval" / "run-report.json"
    if report_path.is_file() and eval_payload:
        saved = json.loads(report_path.read_text(encoding="utf-8"))
        fresh_rows = [
            (r["id"], r["ok"], r["detail"]) for r in eval_payload.get("results", [])
        ]
        saved_rows = [
            (r["id"], r["ok"], r["detail"]) for r in saved.get("results", [])
        ]
        if (
            saved.get("passed") != eval_payload.get("passed")
            or saved.get("total") != eval_payload.get("total")
            or saved.get("failed") != 0
            or saved.get("selftest") is not False
            or saved_rows != fresh_rows
        ):
            fail(
                "eval/run-report.json does not match this eval run; "
                "regenerate with `python3 eval/run_cases.py --save` and commit it"
            )
    elif not report_path.is_file():
        fail("eval/run-report.json is missing")

    got = {
        "pytest_passed": str(pytest_passed),
        "pytest_failed": str(pytest_failed),
        "cli_modules": str(len(modules)),
        "smoke_cli_ok": str(len(cli_names)),
        "memory_logs": str(len(dated)),
        "summary_n_stages": str(summary.n_stages),
        "summary_n_total_mentions": str(summary.n_total_mentions),
        "summary_n_orphans": str(summary.n_orphans),
        "summary_n_active_days": str(summary.n_active_days),
        "summary_health": str(summary.health),
        "summary_health_score": str(summary.health_score),
        "maturity_items": str(len(maturity)),
        "committed_reports": str(len(report_files)),
        "eval_passed": str(eval_payload.get("passed", -1)),
        "eval_total": str(eval_payload.get("total", -1)),
        "eval_selftest_failed": str(self_failed),
        "streak_stages_first_seen": str(streak.n_total_stages_first_seen),
        "streak_longest": str(streak.longest_streak),
        "streak_current": str(streak.current_streak),
        "streak_first_active_date": str(streak.first_active_date),
        "streak_last_active_date": str(streak.last_active_date),
        "check_budget_minutes": str(BUDGET_MINUTES),
    }

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    claimed = parse_claims(readme)
    for diff in claim_diffs(got, claimed):
        fail(diff)
    line = pinned_line(got)
    selftest_ratio = (
        f"{int(got['eval_total']) - int(got['eval_selftest_failed'])}/"
        f"{got['eval_total']}"
    )
    required = [
        line,
        f"{got['cli_modules']} offline Python CLIs",
        f"committed logs (n={got['memory_logs']},",
        f"number {got['summary_n_total_mentions']}",
        (
            f"n_stages={got['summary_n_stages']}, "
            f"n_total_mentions={got['summary_n_total_mentions']}, "
            f"n_orphans={got['summary_n_orphans']}, "
            f"n_active_days={got['summary_n_active_days']}, "
            f"health {got['summary_health']}, "
            f"health_score {got['summary_health_score']}"
        ),
        (
            f"n_total_stages_first_seen={got['streak_stages_first_seen']}, "
            f"longest_streak={got['streak_longest']}, "
            f"current_streak={got['streak_current']}, "
            f"first_active_date={got['streak_first_active_date']}, "
            f"last_active_date={got['streak_last_active_date']}"
        ),
        f"maturity items {got['maturity_items']}",
        f"committed_reports={got['committed_reports']}",
        f"{got['pytest_passed']} pytest tests passing",
        f"{got['smoke_cli_ok']}/{got['cli_modules']}",
        f"{got['eval_passed']}/{got['eval_total']} cases passed",
        selftest_ratio,
        f"{got['check_budget_minutes']} minutes",
        "No package version is declared",
        "pytest>=8.0",
        PYTEST_CMD,
        "D1-D40 未重建",
        SMOKE_BANNER,
        "3.10",
        "3.11",
        "3.12",
    ]
    for snippet in required:
        if snippet not in readme:
            fail(f"README.md is missing recomputed text: {snippet}")

    table_paths = set(MODULE_ROW.findall(readme))
    disk_paths = {f"src/analysis/{p.name}" for p in modules}
    if table_paths != disk_paths:
        fail(
            "README module table paths != src/analysis/stage_*.py: "
            f"only in table {sorted(table_paths - disk_paths)}, "
            f"only on disk {sorted(disk_paths - table_paths)}"
        )

    ratios = allowed_ratios(got)
    for rel in RATIO_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        pinned_lines = [
            ln.strip() for ln in text.splitlines() if ln.strip().startswith("PINNED:")
        ]
        if pinned_lines != [line]:
            fail(f"{rel} PINNED line != recomputed result")
        for token in RATIO.findall(text):
            if token not in ratios:
                fail(f"{rel} has ratio {token} which this run did not produce")
    for rel in DURATION_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if re.search(r"passed in \d", text) or re.search(r"\d+(?:\.\d+)?s\b", text):
            fail(f"{rel} pins a wall-clock duration; durations are not claims")

    note = (memory_dir / "2026-07-20.md").read_text(encoding="utf-8")
    if "D1-D40 未重建" not in note or "submission.zip" not in note:
        fail("committed memory note no longer supports the README attribution")

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").strip()
    if requirements != "pytest>=8.0":
        fail(f"requirements.txt is {requirements!r}; README pins pytest>=8.0")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    if PYTEST_CMD not in makefile:
        fail(f"Makefile is missing {PYTEST_CMD}")

    for path in modules:
        text = path.read_text(encoding="utf-8")
        if "../.workbuddy/memory" in text:
            fail(f"{path.name} still defaults to ../.workbuddy/memory")
        if path.name not in NO_MEMORY_DIR_DEFAULT:
            if 'default=Path(".workbuddy/memory")' not in text:
                fail(f"{path.name} is missing the repo-root memory_dir default")

    init_text = (ROOT / "src" / "__init__.py").read_text(encoding="utf-8")
    if "__version__" in init_text:
        fail("src/__init__.py declares __version__; README says no package version")
    for name in ("pyproject.toml", "setup.py", "setup.cfg"):
        if (ROOT / name).exists():
            fail(f"{name} exists; README says no package version is declared")

    prereg = (ROOT / "PREREG.md").read_text(encoding="utf-8")
    # The empty-directory test is a fixed fail-closed assertion. It is not the
    # corpus headline, even when the committed log currently parses to the same grade.
    empty_test = (ROOT / "tests" / "test_d48_stage_summary.py").read_text(encoding="utf-8")
    if "assert r.n_stages == 0" not in empty_test or 'assert r.health == "D"' not in empty_test:
        fail("test_build_summary_empty no longer asserts n_stages 0 and health D")
    if 'n_stages=0, health="D"' not in prereg:
        fail('PREREG.md is missing the fail-closed quote n_stages=0, health="D"')
    if "not a pre-registration written before the analysis" not in prereg:
        fail("PREREG.md still claims it was written before the analysis")

    for rel in (
        ".github/workflows/checks.yml",
        ".github/workflows/ci.yml",
        ".github/workflows/pr-checks.yml",
    ):
        if "make check" not in (ROOT / rel).read_text(encoding="utf-8"):
            fail(f"{rel} does not run make check")
    checks_yml = (ROOT / ".github/workflows/checks.yml").read_text(encoding="utf-8")
    ci_yml = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    pr_yml = (ROOT / ".github/workflows/pr-checks.yml").read_text(encoding="utf-8")
    if "'3.10'" not in checks_yml or "'3.12'" not in checks_yml:
        fail("checks.yml no longer runs Python 3.10 and 3.12")
    if 'python-version: "3.12"' not in ci_yml:
        fail('ci.yml verify job no longer pins Python 3.12')
    if 'python-version: "3.11"' not in pr_yml:
        fail('pr-checks.yml no longer pins Python 3.11')
    if "|| true" in pr_yml:
        fail("pr-checks.yml swallows failures with || true")
    if "253 passed" in ci_yml or "no requirements.txt" in ci_yml:
        fail("ci.yml still carries the stale 253-passed / missing-requirements comment")

    for rel in ("SECURITY.md", "SUPPORT.md", ".github/ISSUE_TEMPLATE/config.yml"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "github.com/kaggle-science-exam/" in text:
            fail(f"{rel} links to github.com/kaggle-science-exam without the aidless owner")
        if "github.com/aidless/kaggle-science-exam" not in text:
            fail(f"{rel} is missing the aidless/kaggle-science-exam link")

    # The comparator itself has to reject a lie. This does not rerun the suite.
    mutated = dict(got)
    mutated["pytest_passed"] = str(int(got["pytest_passed"]) + 1)
    if not claim_diffs(got, mutated):
        fail("drift comparator accepted a mutated pytest_passed")

    elapsed = time.monotonic() - started
    if elapsed > BUDGET_MINUTES * 60:
        fail(f"make check took {elapsed:.1f}s, over the {BUDGET_MINUTES} minute budget")

    print(line)
    print(f"elapsed_s={elapsed:.2f} budget_minutes={BUDGET_MINUTES}")
    if errors:
        print(f"{len(errors)} check(s) failed", file=sys.stderr)
        return 1
    print("make check: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
