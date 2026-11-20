# ADR 0007: Normalized session log is JSONL

Status: Proposed
Date: 2026-11-16

## Context

Scoring is more consistent when every stored session has the same shape. Cursor, omp, and Copilot do not all provide a session in a form that can be scored directly. The user chose JSONL over one JSON object per session.

## Decision

The stored session log is one UTF-8 `.jsonl` file per session id at `session-logs/<session-id>.jsonl`. The critique is `session-critiques/<session-id>.md`.

Line 1 is a session record (`record` = `session`) and includes `missing_fields`. Each following line is one turn (`record` = `turn`). No turn lines means the harness stored no turns. Field rules are in `docs/plans/normalized-session-log.md`.

Extractors write that file. The scorer reads only that file. It does not open Cursor `store.db`, omp session jsonl, or Copilot `chatSessions`.

When a harness cannot fill a field without guessing, the field stays empty (`null`, `""`, or no turn line) and the name is listed in `missing_fields`. The report states that the score may be off. The scorer must not invent the missing structure.

## Consequences

A JSON object file per session is not the contract. A turns-only JSONL with no session line is not the contract. Replacing this ADR is required before a different container.
