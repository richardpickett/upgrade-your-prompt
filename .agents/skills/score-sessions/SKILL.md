---
name: score-sessions
description: Former name of the analysis stage. Follow analyze-sessions.
disable-model-invocation: true
---

# Score sessions

This name is the analysis stage. Follow `.agents/skills/analyze-sessions/SKILL.md`.

## Gate (default-closed)

| Criterion | Blocking? | Pass when |
| --- | --- | --- |
| One procedure | yes | No file is written from this skill. The analyze-sessions gate is the one that passes. |

## Procedure

Open `analyze-sessions` and run that gate and procedure.

## Done signals

- The analyze-sessions done signals hold.
