# Specification — kaggle-science-exam

This file specifies the reconstructed tools. It was added after those tools
existed (the modules landed before this document). It is not a pre-registration written before the analysis.

## Question

Can the offline CLIs be rerun on the committed logs, with every stated count
recomputed by `make check`, without claiming a Kaggle result?

## Pinned result

PINNED: pytest_passed=71 pytest_failed=0 cli_modules=18 smoke_cli_ok=18 memory_logs=1 summary=0/0/0/1 health=D health_score=0 maturity_items=0 committed_reports=0 eval=20/20 selftest_failed=1 streak_stages=0 streak_longest=1 streak_current=1 streak_first=2026-07-20 streak_last=2026-07-20

`summary` is n_stages/n_total_mentions/n_orphans/n_active_days. On the committed
memory directory that tuple is the headline. The fail-closed empty-directory
test asserts n_stages=0, health="D".

## Boundary

1. Stages D1–D40, the original submission.zip, and the pre-loss history are not
   in this repository and are not reconstructed here.
2. No leaderboard score, submission rank, or medal is claimed.
3. The committed log is a reconstruction note. `build_summary` counts stage ids
   on `##` heading lines only.
4. `report/` is generated CLI output and is not committed.

## Gate

`make check` must exit 0. That runs `python3 -m pytest tests -q`,
`tests/smoke_test.py`, and `eval/run_cases.py`, including a selftest that must
fail exactly one case.
