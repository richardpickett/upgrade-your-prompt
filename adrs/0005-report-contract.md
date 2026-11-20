# ADR 0005: Report shape

- Status: Accepted
- Date: 2026-11-16
- Revision: 2
- Deciders: practice maintainer

Previous bytes: `history/0005-report-contract-R1.md`.

## Context

The report shape was accepted on 2026-11-16. The scoring formula that was accepted with it is withdrawn by ADR 0008.

## Decision

These stay in force:

- The critique is a thorough written markdown report with examples.
- Each evaluated area has an integer score from 1 to 100, plus a composite from 1 to 100.
- The summary, including the composite, is at the top.
- The summary filename matches the stored session log.
- Audience is the session author or a later reader.
- The harness list and the stage split are ADR 0009. Extract, analysis, and the patterns report stay separate.
- Natural Language Compiler practice is a reference, not a dependency.
- Task success, safety, and cost are notes. They are not part of the composite.
- Trace, lint, and a two-pass jury are checks. They do not add composite points.
- The headline score is the fitness rung in ADR 0008. Area scores, the twelve-section list, and the mean-plus-lowest formula are withdrawn.
- A quote used as evidence must occur in the stored session text.

## Consequences

The headline is the rung in ADR 0008. This ADR no longer defines a composite. The report shape above remains. ADR 0010 governs when a factor counts and how a new factor is added.
