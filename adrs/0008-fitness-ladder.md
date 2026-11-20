# ADR 0008: Fitness is the rung

- Status: Accepted
- Date: 2026-11-16
- Revision: 2
- Deciders: practice maintainer

Previous bytes: `history/0008-fitness-ladder-R1.md`.

## Context

ADR 0005 locked a report shape and a mean-plus-lowest composite over area scores. The area list was deferred. Later sessions replaced that instrument with an ordered ladder. Items on the ladder must be adjustable without changing the score.

## Decision

The headline score is the rung, an integer from 0 to 10. There are no item weights, and rung percents are not averaged into one session score.

Every indicator is tested against the whole session. One good instance does not mean the practice was consistent. Each observed case is recorded as good or bad.

A series of prompts may be one goal. A question that lists, edges, or completes that goal is a pass on rung 1, not a miss. The person will rarely know the whole scope in the first prompt. The pass rate is still k/n over prompts that had a case. A question aimed at the goal counts as good for P01. An activity with no outcome and no such question is bad.

A conclusion that never reaches a store is not a rung-1 miss. It is F20. The next session then has to rediscover the same domain. Asking is the practice. Repeating the discovery because nothing was written down is the failure.

The strength of a rung is the lower end of the 95% Wilson interval for that pass rate. It is the lowest rate still believable, 19 times out of 20, given this many prompts. A pass rate from two prompts can look high and still have a weak strength. The same rate from twenty prompts is stronger. Strength is not averaged across rungs.

The headline rung is the highest rung whose pass rate is at least 80% and whose strength is at least 50%, with every lower occupied rung also clearing both lines. Rung 0 means rung 1 does not. Both lines are constants in this decision. Moving either requires replacing this ADR. Neither is a weight on an indicator.

A strength line of 80% is not used. Sixteen perfect prompts are required before a 95% lower bound reaches 80%, so that line would reject sessions the pass rate already describes well. Strength of 50% means the sample is large enough that a coin-flip rate is no longer believable.

The evidence file is `session-evidence/<session-id>.jsonl`. Each line is one observed instance: indicator id, rung, good or bad, turn id, and the quote from the stored log. The critique reads this file and does not replace it.

Missing evidence does not raise the rung. A silent edit is not invented.

## Determinate sample

The evidence file is still written when the sample is too small. A rung that misses either line is shown with its pass rate, its prompt count, and its strength, and it is not the headline.

A scattered pattern cannot clear the lines. Occupied rungs that are not a contiguous block from rung 1 were not sampled in order, so a single prompt that touches a high rung does not carry it.

The critique asks for a longer session when no rung clears both lines. When sessions are listed, each line includes the human prompt count. A human prompt is one human turn. The count is not a score. A larger count is the one more likely to lift the strength.

Adding, removing, or moving an indicator is an edit to `docs/fitness-indicators.md`. The indicator's id stays stable. A move changes which rung it belongs to. It does not introduce a weight. Replacing this ADR is required before a weighted composite, an area score, or a single percent averaged across rungs.

ADR 0005 still governs the report shape: markdown, examples, summary on top, filename stem equal to the session id, advice only. The mean-plus-lowest formula and the twelve-section candidate are withdrawn.

ADR 0010 governs evidence that is not definitive, the efficiency or effectiveness label, and how a new factor is added. A prompt, a series, or the session may carry a factor when the evidence is definitive. The rung lines in this decision stay.

## Consequences

Two sessions on the same headline rung can show different pass rates and different strengths. A high pass rate on a handful of prompts stays a weak strength and does not clear the line. A bad prompt lowers the rate. It drops the rung when the rate falls under 80% or the strength falls under 50%, or when a lower rung misses either line.
