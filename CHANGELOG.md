# Changelog

All notable changes to this repository are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Add `make check`, which reruns pytest, the CLI smoke, and the eval cases, and
  fails if the pinned counts in the README drift. No package version is declared.
- Withdraw wall-clock durations from the pinned result. A previous README
  reported `71 passed in 0.34s`; that duration is not stable across machines.
- State the committed-log result: heading-line stage mentions are 0, so the
  summary health grade on that note is D. D1–D40 and `submission.zip` stay lost.
- Correct the streak docstring: `today` is ignored. Correct PREREG.md: it was
  written after the tools existed. Point security and support links at
  `aidless/kaggle-science-exam`. Default `--memory_dir` is `.workbuddy/memory`.
- Governance baseline: LICENSE, security policy, code of conduct, contributor and
  support guides, issue and pull-request templates, CODEOWNERS, dependabot, and
  `.editorconfig` added. No research content changed.
