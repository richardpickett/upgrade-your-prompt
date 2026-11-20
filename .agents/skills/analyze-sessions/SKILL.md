---
name: analyze-sessions
description: Judge one exported session for fitness. Reads the extract only. Does not add factors.
disable-model-invocation: true
---

# Analyze sessions

Judge the person's prompting. Advice only. Do not change the repo, standing instructions, or harness logs.

Binds: ADR 0001, ADR 0002, ADR 0005, ADR 0008, ADR 0009, ADR 0010. Factors: `docs/fitness-indicators.md`.

## Gate (default-closed)

| Criterion | Blocking? | Pass when |
| --- | --- | --- |
| Extract only | yes | The only session input opened is `session-logs/<agent>--<id>.jsonl`. No harness path is opened. |
| Known factors | yes | Every evidence line uses an id from `docs/fitness-indicators.md`. |
| Quote in the extract | yes | `python3 tools/run_pipeline.py accept --agent <agent> --id <id>` exits 0. |
| Definitive only | yes | A factor line exists only when the quote settles that factor. Otherwise the shape is an observation, not a factor. |
| No new factor | yes | An observation file contains no new indicator id. |
| Finished or not | yes | The critique names the outcome, or says the work was not finished because the outcome cannot be named or the finish is not shown. |
| Rung only | yes | The headline is the integer from ADR 0008. No weight and no area score. |

Fail any blocking row: leave the status at `exported`. Do not mark `analyzed`.

## Procedure

1. Read the extract and the factor index. Read `docs/fitness/<id>.md` for a factor you are about to apply.
2. Identify the outcome. A series that ends in "record the conclusions" has the goal of the recorded conclusions, not an unvetted paste.
3. A prompt, a series, or the whole session may carry a factor when the evidence is definitive. A series is prompts coordinating on one piece of work. One prompt is a series of one.
4. Write `session-evidence/<agent>--<id>.jsonl`. Each line is `indicator_id`, `rung`, `result` (`good` or `bad`), `turn_id`, `quote`. `good` is a practice row. `bad` is a failure row.
5. Write `session-observations/<agent>--<id>.jsonl` for prompt shapes, goal types, and techniques that match no factor. These do not move the rung.
6. Write `session-critiques/<agent>--<id>.md`. Summary first, then the named outcome, then quotes. The audience is the author.
7. Run `python3 tools/run_pipeline.py accept --agent <agent> --id <id>`.
8. Do not reanalyze a row that is already `analyzed` on this engine unless the operator asked.

## Done signals

- Status for that session is `analyzed`.
- The evidence file's quotes occur in the extract.
