---
name: extract-sessions
description: Export working-set sessions from Cursor, Copilot, Codex, oMP, and Pi into one JSONL shape. Does not analyze.
disable-model-invocation: true
---

# Extract sessions

Read each harness's own store and write `session-logs/<agent>--<session_id>.jsonl`. The working directory does not matter. This skill does not analyze.

Binds: ADR 0001, ADR 0007, ADR 0009, ADR 0010.

## Gate (default-closed)

| Criterion | Blocking? | Pass when |
| --- | --- | --- |
| Working set only | yes | `python3 tools/run_pipeline.py export` writes a log only for a row whose state was `new`. |
| One shape | yes | Line 1 is `record=session`. Later lines are `record=turn`. `agent` is `cursor`, `copilot`, `codex`, `omp`, or `pi`. |
| File bodies omitted | yes | An edit, write, or replace stores `change_path` and `change_operation`. `old_string`, `new_string`, `contents`, and `stream_content` are absent. |
| Replies kept | yes | Human text and model text that the harness stored are on turn lines. |
| Empty stays empty | yes | A missing memo field is null or `""`, and its name is in `missing_fields`. |
| Failure stays visible | yes | A session that cannot be read becomes `failed` and remains in the status file. |
| No analysis | yes | This skill writes nothing under `session-critiques/`, `session-evidence/`, or `session-observations/`. |

Fail any blocking row: do not mark that session `exported`.

## Procedure

1. Run `python3 tools/run_pipeline.py export`.
2. Stores, independent of the git repo that happens to be open:
   - Cursor chats: `~/.cursor/chats/<hash>/<id>/store.db`
   - Cursor agent transcripts: `~/.cursor/projects/**/agent-transcripts/**/*.jsonl`
   - Copilot: `~/.config/Code/User/**` chat JSON and JSONL append logs
   - Codex: `$CODEX_HOME/sessions` or `~/.codex/sessions/rollout-*.jsonl`
   - Pi and oMP: one parser. Roots `~/.pi/agent/sessions` and `~/.omp/agent/sessions`, plus `PI_CODING_AGENT_DIR` and `PI_CODING_AGENT_SESSION_DIR`
3. System prompts and reasoning text are not stored. A shell command and its result are stored. A file read stores the path and not the file body.

## Done signals

- Each exported row has state `exported` and a JSONL file.
- `python3 tools/test_pipeline.py` exits 0.
