---
name: run
description: Advance every outstanding session in the working set. Export, analyze, then rebuild the patterns report.
disable-model-invocation: true
---

# Run

One invocation moves outstanding work. It does not reanalyze a finished session unless the operator asks and the analysis engine changed.

Binds: ADR 0002, ADR 0009, ADR 0010.

## Gate (default-closed)

| Criterion | Blocking? | Pass when |
| --- | --- | --- |
| Scope first | yes | If the operator named a scope, `scope-sessions` passes before export. |
| Export new only | yes | `extract-sessions` passes. Rows already `exported` or `analyzed` are not exported again. |
| Analyze exported only | yes | `analyze-sessions` runs for each `pending` row and for no `analyzed` row. |
| Failed stays listed | yes | A `failed` row is still in `working-set/status.json` after the run. |
| Report when analyses exist | yes | `patterns-report` passes after the accepts. |
| Advice only | yes | No standing instruction, harness log, or product source file is edited by this run. |

Fail any blocking row: stop that stage. Leave later stages unrun.

## Procedure

1. Scope sentence present: run `.agents/skills/scope-sessions/SKILL.md`. On `ask-remove`, stop.
2. Run `.agents/skills/extract-sessions/SKILL.md`.
3. Run `python3 tools/run_pipeline.py pending`. For each printed line, run `.agents/skills/analyze-sessions/SKILL.md`.
4. Run `.agents/skills/patterns-report/SKILL.md`.

## Done signals

- No row remains `new`.
- Every `exported` row from this invocation is `analyzed` or still `exported` with a stated gate failure.
- `patterns-report.md` is newer than the evidence files it includes, or there were no analyses.
