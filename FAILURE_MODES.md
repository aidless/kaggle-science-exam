# Failure modes

PINNED: pytest_passed=71 pytest_failed=0 cli_modules=18 smoke_cli_ok=18 memory_logs=1 summary=0/0/0/1 health=D health_score=0 maturity_items=0 committed_reports=0 eval=20/20 selftest_failed=1 streak_stages=0 streak_longest=1 streak_current=1 streak_first=2026-07-20 streak_last=2026-07-20

`summary` is n_stages/n_total_mentions/n_orphans/n_active_days. Health D here is the parser's grade on the committed note. It is not a Kaggle result and it is not this repository's review grade.

## Lost inputs

Stages D1–D40, the original `submission.zip`, the pre-loss `report/` files, and the pre-loss history are not in this repository. They are not reconstructed here. The size figure written in the 2026-07-20 note is not recomputed, because the zip is not in the tree, and it is not a README claim.

The note `.workbuddy/memory/2026-07-20.md` is a reconstruction log. It records `D1-D40 未重建` and that `submission.zip` was not restored. Stage ids in that file sit in list items. The parsers count a stage only on a line that starts with `##` and does not start with `###`, so the summary's mention count is 0 while `n_active_days` is still 1. Any dated `YYYY-MM-DD.md` counts as an active day, including a note with no stage headings.

## Streak wording

`build_streak` accepts `today` and does not read it. `current_streak` is the consecutive run ending on the last dated file, not a run that has to include the calendar day of the run. A single note dated 2026-07-20 therefore reports longest_streak=1 and current_streak=1 on later calendar days. The module docstring used to say the streak ends today; that sentence was wrong and has been corrected to match the code.

## Smoke and grep

`tests/smoke_test.py` writes a temporary memory directory, reruns the unit-test files, then runs each CLI. Passing smoke does not measure the committed note. The banner `ALL SMOKE TESTS PASSED (D41 - D58)` is the script's closing line; `make check` also requires the CLI names in that output to match `src/analysis/stage_*.py`.

`build_grep` counts stage-id tokens under `src/`, `tests/`, and `report/`. That tally is an eval case about the source tree. It is not a count of competition mentions, and it is not a README headline. `report/` is not tracked.

## What is not pinned

Durations are not claims. The previous README reported `71 passed in 0.34s` (dated there 2026-11-10). This audit's pytest run printed a different duration on the same pass count. The reconstruction note records another duration from 2026-07-20. Neither duration is stable across machines, so both are withdrawn from the pinned result.

`eval/run-report.json` is a snapshot. `make check` reruns `eval/run_cases.py` and requires the snapshot's pass rows to match. The selftest used to exit 0 whenever at least one case failed, so a suite that failed every case still counted as a successful selftest. It now exits 0 only when exactly one case fails.

Doc cases KS-18, KS-19, and KS-20 are substring checks. A sentence can stay true while a neighbor lies. The claims block and the single `PINNED` line are the drift gate, and the same line has to appear in README.md, PAPER.md, PREREG.md, and this file.

## Paths, secrets, packaging

CLI `--memory_dir` used to default to `../.workbuddy/memory`, which misses the in-repo note when the command runs from the repository root. The default is now `.workbuddy/memory`. `stage_grep` and `stage_coverage` take a project root instead of a memory directory.

No package version is declared. There is no `pyproject.toml`, `setup.py`, `setup.cfg`, or `__version__`. Publishing workflows skip the build when that metadata is absent.

A search of the tree found no committed API keys, Kaggle tokens, or private keys. `make check` does not read credentials and does not call the network. The CI secret-scan job downloads gitleaks; that job is separate from the offline gate.

GitHub About text is outside this repository. Until it is updated, the GitHub blurb can lag the README. The replacement text is in the pull request that introduced this file.

## CI footguns that were fixed

`pr-checks.yml` used to append `|| true` to compileall and to pip install, and it skipped tests when pytest was missing. Those steps now fail closed and run `make check`. `ci.yml` used to say this repository had no `requirements.txt` and cited a `253 passed` figure that is not this suite. `requirements.txt` is `pytest>=8.0`, and the verify job runs `make check`.

## Specification timing

PREREG.md was added after the CLI modules. It is a specification of the reconstructed tools, not a pre-registration written before the analysis.
