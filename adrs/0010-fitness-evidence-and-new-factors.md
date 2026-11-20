# ADR 0010 — Fitness evidence and new factors

- Status: Accepted
- Date: 2026-11-18
- Revision: 1
- Deciders: practice maintainer

## Context

The session is judged for fitness toward effectiveness and efficiency. Effectiveness is reaching the real outcome, including leaving a record that later prompts can use. Efficiency is the absence of a cycle that did not serve that work. ADR 0008 already lists the measurement factors and makes the rung the headline. Those factors were not labeled with a result, and the decision did not say what happens to a prompt shape that matches none of them.

## Decision

The factors already written in `docs/fitness-indicators.md` stay in force. Each factor is labeled `effectiveness` or `efficiency` in that index. ADR 0008 still decides the rung, the pass rate, and the strength. This decision does not move those lines.

A prompt, a series of prompts, or the whole session may be the evidence for a factor. The evidence counts only when it is definitive. Evidence that is not definitive is not a pass and is not a fail.

The goal is the outcome the work is for. A mechanic such as pasting text into a document is not the goal. In the documentation case, the outcome is documentation that was thought through, vetted, confirmed valid, and confirmed to fit. If the outcome cannot be named from the session, or the session does not show that the work finished, the work is not finished.

A factor is applied when its evidence is definitive. Anything else is recorded as an observation: a prompt shape, a goal type, or a technique. An observation does not become a factor and does not move the rung.

A new factor exists only when the practice maintainer and the judgment agent confirm it. The product operator sends shapes, extracts, and reports. The practice maintainer and the judgment agent use that analysis to improve the judgment. The product operator does not add a factor. Classifications are not a closed list.

The person's prompting is the subject. Agent replies, tool results, and a change record are evidence. A fact the log never stored does not lower a result.

## Consequences

`docs/fitness-indicators.md` carries the result label. Adding, removing, or relabeling a factor is an edit to that index plus a confirmation by the practice maintainer and the judgment agent. An observation recorded on a session is not that confirmation.

ADR 0008 governs the rung for the factors already written. Where a prompt, a series, and a session can each carry definitive evidence, this decision governs. Where a shape has no factor yet, this decision governs.

This is a minor change: labels and a rule for new factors. The rung lines are unchanged.

## Rejected

- A closed list of prompt classifications invented before the corpus is read.
- Treating an unvetted paste as the goal.
- Scoring evidence that is not definitive.
- Letting the product operator, or an analysis skill, add a factor without confirmation by the practice maintainer and the judgment agent.
