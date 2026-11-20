# Normalized session log plan

Status: shape and directories chosen. Fixtures are in `fixtures/session-logs/`. Do not write an extractor or a scorer from this file.

Binds: ADR 0007, ADR 0009, ADR 0010. The file name is `<agent>--<session_id>.jsonl`. Agents are `cursor`, `copilot`, `codex`, `omp`, and `pi`. A file change is path plus operation. File bodies are not stored.

The user chose JSONL on 2026-11-16. One JSON object per session is withdrawn.

## Gate

Default-closed. No extractor starts until every blocking row is true on the decision record this plan produces.

| Criterion | Blocking? | Pass when |
| --- | --- | --- |
| One stored shape | yes | One JSONL shape is named. Cursor, omp, and Copilot extracts all use it. |
| Scorer boundary | yes | The scorer reads only that stored shape. It does not open Cursor `store.db`, omp jsonl, or Copilot `chatSessions`. |
| Empty fields | yes | Every field in the memo's step-7 list can be absent. Absence is stored as empty, not guessed. |
| Lossy warning | yes | When a field an area score needs is empty, the session line carries `missing_fields` and the report must say the score may be off. |
| No rubric | yes | This plan does not adopt sections, bands, or quote rules. ADR 0005 still defers those. |
| No build | yes | This plan contains no extractor procedure and no skill text. |

## What this plan decides

ADR 0007 left the file format open. The stored shape is JSONL. This plan does not pull sessions.

The scorer's only input is the stored JSONL for the ids it was given. Raw harness files stay on the extractor side of ADR 0004.

## Shape

One UTF-8 JSONL file per session id. Filename is the session id plus `.jsonl`. The critique markdown uses the same session id in its filename.

Line 1 is the session record. Each later line is one turn. No trailing comma. Empty `turns` means the file is the session line only.

Session line:

| Field | Type when present | Empty when missing |
| --- | --- | --- |
| record | `session` | Never empty. |
| session_id | string | Never empty. Extractor fails that id instead of writing a file. |
| agent | `cursor`, `omp`, or `copilot` | Never empty. Known from the path the extractor read. |
| started_at | ISO-8601 string | `null` |
| updated_at | ISO-8601 string | `null` |
| workspace | string | `null` |
| missing_fields | array of field names | `[]` when nothing an area score needs was dropped |

Turn line:

| Field | Type when present | Empty when missing |
| --- | --- | --- |
| record | `turn` | Never empty. |
| session_id | string | Same id as line 1. A mismatch fails the file. |
| turn_id | string | `null` |
| parent_turn_id | string | `null` |
| role | `human` or `model` | `null`, and `Role` is added to `missing_fields` |
| at | ISO-8601 string | `null` |
| text | string | `""`, and `Human text` is added to `missing_fields` when no human turn has text |
| tool_name | string | `null` |
| tool_arguments | string | `null` |
| tool_result | string | `null` |

`model` id is omitted from the MVP record. The memo says it is not scored.

`missing_fields` uses the memo's names, not new ones: `Turn id`, `Parent turn id`, `Role`, `Timestamp per turn`, `Human text`, `Model text`, `Tool name and arguments`, `Tool result text`. A Cursor blob that was not decoded adds `Tool result text`. A Copilot file whose `requests` array is empty adds `Human text` and `Model text` and has no turn lines.

Putting `missing_fields` on line 1 keeps one file per id. A second sidecar is not used.

## Why JSONL

| Option | Result |
| --- | --- |
| JSONL, one file per id, session line then turn lines | Chosen. The critique stem matches the log. The scorer reads line 1 for the warning and the following lines for quotes. A missing turn is an absent line, not a guessed object. |
| One JSON object per session | Withdrawn. The user rejected it. |
| JSONL of turns only | Rejected. The session-level `missing_fields` list would need a second file. |
| One JSONL stream for every session | Rejected. One id must map to one filename stem. |
| Leave the harness file in place | Rejected. The scorer would read `store.db`, omp jsonl, and Copilot json. ADR 0004 forbids that. |

## Decision record

Done on 2026-11-16. These rows are the format pass. They are not an extractor.

| # | Produced | Where |
| --- | --- | --- |
| 1 | Three fixture logs, no copied prompt prose | `fixtures/session-logs/cursor-fixture-001.jsonl`, `omp-fixture-001.jsonl`, `copilot-fixture-001.jsonl` |
| 2 | Directories | Extracted logs: `session-logs/<session-id>.jsonl`. Critiques: `session-critiques/<session-id>.md`. Fixtures stay under `fixtures/session-logs/` and are not extracts. |
| 3 | Scorer read | The scorer reads only `session-logs/<session-id>.jsonl`. Cursor `store.db`, omp session jsonl, and Copilot `chatSessions` are out of bounds. |
| 4 | Warning | When `missing_fields` is non-empty, the report's first lines include: the score may be off because the harness log did not contain the missing fields. |

## Not in this plan

No skill, no extractor command, no adoption of the twelve-section candidate, no score bands.
