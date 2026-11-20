---
name: patterns-report
description: Rebuild the patterns report from session analyses only.
disable-model-invocation: true
---

# Patterns report

Read analyses. Do not open extracts or harness stores.

Binds: ADR 0005, ADR 0008, ADR 0009.

## Gate (default-closed)

| Criterion | Blocking? | Pass when |
| --- | --- | --- |
| Analyses only | yes | `python3 tools/run_pipeline.py report` reads `session-evidence/`, `session-critiques/`, and `session-observations/` and does not open `session-logs/` or a home-directory store. |
| Rung per session | yes | Each section states `Headline rung:` as an integer. |
| Observations included | yes | Observation lines from the analysis files are listed under that session and are not scored. |

Fail any blocking row: do not overwrite `patterns-report.md`.

## Procedure

1. Run `python3 tools/run_pipeline.py report`.
2. The file is `patterns-report.md` in the checkout.

## Done signals

- `patterns-report.md` exists.
- Its session sections match the evidence files on disk.
