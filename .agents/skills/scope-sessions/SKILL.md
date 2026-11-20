---
name: scope-sessions
description: Put harness sessions into the working set from the operator's scope sentence. Does not extract or analyze.
disable-model-invocation: true
---

# Scope sessions

The operator names which sessions are in the working set. This skill writes `working-set/status.json` and nothing else.

Binds: ADR 0009.

## Gate (default-closed)

| Criterion | Blocking? | Pass when |
| --- | --- | --- |
| Known phrase or a mapped flag | yes | `python3 tools/run_pipeline.py scope --text "..."` exits 0, or the sentence was mapped onto `all`, a harness name, an id, or `last month` and that command then exits 0. |
| Narrower scope asks | yes | Exit code 3 prints `ask-remove`. No analysis file is deleted. The status file is unchanged. |
| Remove only when chosen | yes | Analysis files are deleted only after `--remove-analyses`. `--keep-analyses` drops the rows and leaves the files. |

Fail any blocking row: stop. Do not export.

## Procedure

1. Run `python3 tools/run_pipeline.py scope --text "<the operator sentence>"`.
2. Exit 0: the status file lists the selected sessions. New rows are `new`.
3. Exit 2 (`scope-unparsed`): map the sentence onto one phrase the parser accepts (`all`, `all from the last month`, a harness name, a session id). Do not invent a harness. If it still will not map, ask one question and stop.
4. Exit 3 (`ask-remove`): ask whether to remove the analyses that fell out of scope. Stop. Delete nothing.

## Done signals

- `working-set/status.json` exists and every row has `state` `new`, `exported`, `analyzed`, or `failed`.
- A time window did not include a session that has no timestamp.
