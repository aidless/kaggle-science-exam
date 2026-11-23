.PHONY: check eval
.DEFAULT_GOAL := check

# Offline gate. Recomputes every pinned README figure and exits non-zero on drift.
check:
	python3 scripts/check_claims.py

# Pytest only. The recipe line is the string eval case KS-20 matches.
eval:
	python3 -m pytest tests -q
