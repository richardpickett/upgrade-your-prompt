# ADR 0009 — Working set and three stages

- Status: Accepted
- Date: 2026-11-18
- Revision: 1
- Deciders: practice maintainer

## Context

Sessions from several coding harnesses have to be brought into this checkout before they can be analyzed. The operator names the scope in ordinary language, including every session or a time window. A later run has to advance whatever is still outstanding without redoing a finished analysis. ADR 0003 limited selection to named ids. ADR 0004 limited the harnesses to three and the skills to two. ADR 0005 repeats that harness list and that two-skill split.

## Decision

The harnesses are Cursor, Copilot, Codex, oMP, and Pi. Pi and oMP share one session format and are read from their own roots.

Work is three stages. Extract writes the session copy and does not analyze. Analysis reads that copy and does not open the harness store. The patterns report reads the analyses and does not open the extracts.

The operator's instruction is the scope. A scope skill interprets that instruction, including all sessions, a time window, named sessions, and named harnesses.

A status file lists every session in the working set and its state: new, exported, analyzed, or failed. A failed row stays visible.

`/run` with no new scope instruction exports rows marked new, analyzes rows marked exported, leaves a finished analysis in place, and rebuilds the patterns report when any session analysis is newer than that report.

A finished analysis is redone only when its engine has changed and the operator asks. When the operator narrows the scope and does not say whether analyses that fell out of scope are removed, the skill asks and deletes nothing. Removal happens only when the operator chooses it.

The skills advise. They do not change this repo, standing instructions, or the harness logs.

## Consequences

ADR 0003 and ADR 0004 are superseded. The harness list and the two-skill limit in ADR 0005 are superseded by this decision. The rest of ADR 0005 stays.

The product operator is the role that names scope and receives the report. That role does not confirm new measurement factors. New factors are ADR 0010.

This is a minor change: new policy and a wider harness set. It does not remove the rung.

## Rejected

- Exporting every session on disk when the operator has not named a scope.
- Deleting an analysis because a later scope is smaller, without an explicit remove choice.
- One skill that extracts, scores, and discovers harness files in the same step.
