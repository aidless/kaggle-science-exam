# Kaggle Science Exam — reconstructed stage-log tools (D41–D58)

[![CI](https://github.com/aidless/kaggle-science-exam/actions/workflows/checks.yml/badge.svg)](https://github.com/aidless/kaggle-science-exam/actions/workflows/checks.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

This repository is 18 offline Python CLIs that read daily `.workbuddy/memory/YYYY-MM-DD.md` notes and report how stage ids show up in those notes.
Stages D1–D40, the original `submission.zip`, and the history from before the 2026-07-20 workspace loss are not in this tree and are not reconstructed here.
This is not a Kaggle competition result: there is no score, rank, or medal.

**Headline (recomputed by `make check`).** On the committed logs (n=1, `.workbuddy/memory/2026-07-20.md`), stage ids on lines that start with `##` number 0, so `build_summary` returns n_stages=0, n_total_mentions=0, n_orphans=0, n_active_days=1, health D, health_score 0. `build_streak` on that same directory returns n_total_stages_first_seen=0, longest_streak=1, current_streak=1, first_active_date=2026-07-20, last_active_date=2026-07-20. Limits: the file is a reconstruction note, not a competition diary; an active day is any dated filename, including one with no stage headings, and `today` is ignored; maturity items 0; smoke uses a synthetic log; committed_reports=0. Separately, 71 pytest tests passing and 18/18 CLI smoke stages pass (`ALL SMOKE TESTS PASSED (D41 - D58)`). Eval is 20/20 cases passed, and the selftest is 19/20. `make check` fails if this run exceeds 15 minutes.

The committed note states `D1-D40 未重建` and that `submission.zip` was not restored (`.workbuddy/memory/2026-07-20.md`).

<!-- claims:start -->
pytest_passed: 71
pytest_failed: 0
cli_modules: 18
smoke_cli_ok: 18
memory_logs: 1
summary_n_stages: 0
summary_n_total_mentions: 0
summary_n_orphans: 0
summary_n_active_days: 1
summary_health: D
summary_health_score: 0
maturity_items: 0
committed_reports: 0
eval_passed: 20
eval_total: 20
eval_selftest_failed: 1
streak_stages_first_seen: 0
streak_longest: 1
streak_current: 1
streak_first_active_date: 2026-07-20
streak_last_active_date: 2026-07-20
check_budget_minutes: 15
<!-- claims:end -->

PINNED: pytest_passed=71 pytest_failed=0 cli_modules=18 smoke_cli_ok=18 memory_logs=1 summary=0/0/0/1 health=D health_score=0 maturity_items=0 committed_reports=0 eval=20/20 selftest_failed=1 streak_stages=0 streak_longest=1 streak_current=1 streak_first=2026-07-20 streak_last=2026-07-20

`summary` is n_stages/n_total_mentions/n_orphans/n_active_days. No package version is declared (there is no `pyproject.toml`, `setup.py`, `setup.cfg`, or `__version__`). Wall-clock durations are not claims. Failure modes: [FAILURE_MODES.md](FAILURE_MODES.md).

## Install and check

Dependencies are the Python standard library plus `pytest>=8.0` from `requirements.txt`. No API key and no Kaggle credential is used.

CI Python is 3.10 and 3.12 in `checks.yml`, 3.12 in `ci.yml`, and 3.11 in `pr-checks.yml`.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make check
```

`make check` reruns `python3 -m pytest tests -q`, `tests/smoke_test.py`, and `eval/run_cases.py` (including the one-case selftest), then diffs the claims block and the `PINNED` line. `make eval` is pytest only.

From the repository root the default `--memory_dir` is `.workbuddy/memory`.

## Modules

| Stage | Module | What it does |
|-------|--------|--------------|
| D41 | `src/analysis/stage_streak.py` | Consecutive-day streaks of dated notes |
| D42 | `src/analysis/stage_leaderboard.py` | Most-mentioned stages on heading lines, plus one-shot/repeat |
| D43 | `src/analysis/stage_grep.py` | Stage-id scan of `src/`, `tests/`, and `report/` |
| D44 | `src/analysis/stage_coverage.py` | Per-stage coverage across project sources |
| D45 | `src/analysis/stage_timeline.py` | First-seen dates and gap analysis |
| D46 | `src/analysis/stage_cadence.py` | Per-day cadence and an A–F grade |
| D47 | `src/analysis/stage_suggestion.py` | Next-stage suggestions from the log |
| D48 | `src/analysis/stage_summary.py` | Health summary graded A–D |
| D49 | `src/analysis/stage_trend.py` | Week-over-week trend and a projection |
| D50 | `src/analysis/stage_fanout.py` | Co-occurrence pairs and density |
| D51 | `src/analysis/stage_clusters.py` | Greedy community detection |
| D52 | `src/analysis/stage_backlog.py` | Mentioned-but-not-implemented backlog |
| D53 | `src/analysis/stage_coupling.py` | Cross-cluster coupling and modularity |
| D54 | `src/analysis/stage_maturity.py` | Three-channel score (memory, code, readme) |
| D55 | `src/analysis/stage_velocity.py` | Epochs and active ratio per stage |
| D56 | `src/analysis/stage_density_curve.py` | Front-loaded / back-loaded flag |
| D57 | `src/analysis/stage_distribution.py` | Mention histogram and Gini |
| D58 | `src/analysis/stage_calendar.py` | Per-month, per-weekday, and per-day counts |

```bash
python -m src.analysis.stage_summary \
    --memory_dir .workbuddy/memory \
    --out report/stage_summary.md \
    --out_json report/stage_summary.json
```

`report/` is gitignored. Nothing under it is a recovered competition artifact.

## What this run shows, and what it does not

`tests/test_d48_stage_summary.py::test_build_summary_empty` asserts that an empty directory returns n_stages=0 and health D. A missing directory takes the same grade. That is a property of the parser, not a grade of a competition and not a grade of this repository.

Smoke builds a temporary log. A green smoke run does not mean the committed note contains stage headings.

This does not show that the modules describe the original Kaggle work. Stages D1–D40 are absent. No leaderboard score, submission rank, or medal is claimed.

## Layout

```
src/analysis/stage_*.py    # D41–D58 CLIs
tests/                     # one test file per CLI, plus tests/smoke_test.py
eval/cases.jsonl           # executable checks; eval/run_cases.py runs them
.workbuddy/memory/         # the one committed note
scripts/check_claims.py    # the make check implementation
```
