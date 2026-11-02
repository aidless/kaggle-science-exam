# Kaggle Science Exam - Stage Analysis Tools

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A collection of analysis modules that read `.workbuddy/memory/YYYY-MM-DD.md`
files and produce reports on the cadence, structure, and quality of the
stage workflow used in the project. It contains **18 reconstructed CLI modules (D41–D58)** only — the original Kaggle competition work (stages D1–D40) is permanently lost (see note below).

> **Note (2026-07-20):** This README and the source tree were
> reconstructed after a workspace loss on 2026-07-20 ~16:00 (the
> original working directory was cleared by an unrelated operation). The modules
> D41-D58 are restored from the conversation history. Earlier
> stages D1-D40 are not included in this reconstruction; the
> original `submission.zip` and full history is unavailable.

## Quick start

```bash
cd kaggle-science-exam
python -m pytest tests/ -v
python tests/smoke_test.py
```

## Modules

| Stage | Module | What it does |
|-------|--------|--------------|
| D41 | `src/analysis/stage_streak.py` | Consecutive-day streaks of activity |
| D42 | `src/analysis/stage_leaderboard.py` | Most-mentioned stages + one-shot/repeat classification |
| D43 | `src/analysis/stage_grep.py` | Grep Dxx in src/, tests/, report/ |
| D44 | `src/analysis/stage_coverage.py` | Per-stage coverage across project sources |
| D45 | `src/analysis/stage_timeline.py` | First-seen dates + gap analysis |
| D46 | `src/analysis/stage_cadence.py` | Per-day cadence + grade (A-F) |
| D47 | `src/analysis/stage_suggestion.py` | Actionable next-stage suggestions |
| D48 | `src/analysis/stage_summary.py` | Project health summary (grade A-D) |
| D49 | `src/analysis/stage_trend.py` | Week-over-week trend + projection |
| D50 | `src/analysis/stage_fanout.py` | Co-occurrence pairs + density |
| D51 | `src/analysis/stage_clusters.py` | Greedy community detection |
| D52 | `src/analysis/stage_backlog.py` | Mentioned-but-not-implemented backlog |
| D53 | `src/analysis/stage_coupling.py` | Cross-cluster coupling + modularity |
| D54 | `src/analysis/stage_maturity.py` | 3-channel score 0-3 (memory+code+readme) |
| D55 | `src/analysis/stage_velocity.py` | Epochs + active ratio per stage |
| D56 | `src/analysis/stage_density_curve.py` | Front-loaded / back-loaded flag |
| D57 | `src/analysis/stage_distribution.py` | Mention histogram + Gini |
| D58 | `src/analysis/stage_calendar.py` | Per-month + per-weekday + per-day counts |

Each module is a CLI:

```bash
python -m src.analysis.stage_timeline \
    --memory_dir ../.workbuddy/memory \
    --out report/stage_timeline.md \
    --out_json report/stage_timeline.json
```

## Project structure

```
kaggle_science_exam/
+-- src/
|   +-- __init__.py
|   +-- analysis/
|       +-- __init__.py
|       +-- stage_streak.py          # D41
|       +-- stage_leaderboard.py     # D42
|       +-- stage_grep.py            # D43
|       +-- stage_coverage.py        # D44
|       +-- stage_timeline.py        # D45
|       +-- stage_cadence.py         # D46
|       +-- stage_suggestion.py      # D47
|       +-- stage_summary.py         # D48
|       +-- stage_trend.py           # D49
|       +-- stage_fanout.py          # D50
|       +-- stage_clusters.py        # D51
|       +-- stage_backlog.py         # D52
|       +-- stage_coupling.py        # D53
|       +-- stage_maturity.py        # D54
|       +-- stage_velocity.py        # D55
|       +-- stage_density_curve.py   # D56
|       +-- stage_distribution.py    # D57
|       +-- stage_calendar.py        # D58
+-- tests/
|   +-- test_d{41-58}_*.py
|   +-- smoke_test.py
+-- report/   # CLI output goes here
+-- .workbuddy/memory/  # input data
+-- README.md
```

## Status

- 18 modules (D41-D58) restored
- 71 pytest tests, all passing (verified 2026-11-01 on this tree)
- 18 smoke stages
- Reconstruction completed 2026-07-20 ~18:00

## Fail-closed guarantee

When the input is missing or malformed, the modules **do not fabricate numbers**.
`_safe_read` returns `""` for a nonexistent path (`src/analysis/stage_summary.py:29`),
and `build_summary` on an empty directory returns `n_stages=0, health="D"` (the worst
grade) instead of inventing a health score — asserted by `tests/test_d48_stage_summary.py::test_build_summary_empty`.
A missing log yields the worst grade, never a fake "pass".

## Related work (reconstruction vs original audit)

This toolset sits in a deliberate contrast to the original competition run:

| Prior work | Real basis | This repo's relationship |
|---|---|---|
| Original Kaggle stages D1–D40 | Lost (workspace cleared 2026-07-20) | **Not** reconstructed here; this repo explicitly does not audit them |
| Stage-analysis as an audit of a live run | A live project's `.workbuddy/memory/` logs | This repo measures a **reconstructed** log, not a live run |
| Generic activity-streak / cadence analysis | Standard time-series activity metrics | This repo reimplements them per-stage (D41–D58) over daily markdown logs |
| Community detection / coupling analysis | Graph partition + modularity | This repo applies greedy clustering + cross-cluster coupling to stage co-mentions |

**Core difference**: a live-run stage audit can claim to describe the real workflow; this
toolset explicitly **cannot** — the analysis is a reconstruction artifact, not an audit
of the original project (see the note above and the "What this does and does not prove"
section).

## What this does and does not prove

**Proves:** the 18 reconstructed CLI modules parse `.workbuddy/memory/*.md` daily
logs and emit the documented report structures without error; each module's core
logic (streak, cadence, coverage, clusters, backlog, coupling, maturity, velocity,
distribution, calendar, etc.) is exercised by a passing pytest case on fixture
input.

**Does not prove:** these modules describe the original Kaggle competition work.
Stages D1–D40 are permanently lost (workspace cleared 2026-07-20), so the
"stage analysis" here measures a **reconstructed log**, not the original
competition run. No leaderboard score, submission rank, or competition result is
claimed. The analysis is a reconstruction artifact, not an audit of the original
project.

## Reproducing the numbers

```bash
cd kaggle-science-exam
python -m pytest -q          # 71 passed
python tests/smoke_test.py   # ALL 18 STAGES PASSED

# one CLI, one run
python -m src.analysis.stage_timeline \
    --memory_dir .workbuddy/memory \
    --out report/stage_timeline.md \
    --out_json report/stage_timeline.json
```

All 71 tests live under `tests/` and all 18 modules under `src/analysis/`; the
input fixture is `.workbuddy/memory/2026-07-20.md`. The count above is the
actual `pytest --collect-only` total, not a target.
