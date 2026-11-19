# ADR 0004: Three agents, two skills

Status: Superseded
Date: 2026-11-16

Superseded by ADR 0009. The text below is the decision it replaced.

## Context

Session logs differ by product. Scoring must not discover or pull logs.

## Decision

The first version supports Cursor, omp, and Copilot. One extract skill detects the agent and delegates to one extractor for that agent. A separate scoring skill scores only the ids it is given, and only logs already extracted. Scoring with no ids stops and asks for ids.

## Consequences

Adding an agent means adding an extractor. The scorer does not gain a fourth discovery path.
