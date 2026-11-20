# ADR 0003: Select sessions by id

Status: Superseded
Date: 2026-11-16

Superseded by ADR 0009. The text below is the decision it replaced.

## Context

The user must name which complete session logs to pull. Bulk selectors were deferred.

## Decision

`/extract-sessions` with no id lists the 20 newest sessions, newest first, each with id, time, and a one-line label, and extracts nothing. `/extract-sessions <id> <id>...` extracts only those ids. Date ranges and other bulk selectors are out of this version. One bad id does not drop the others.

## Consequences

The list is printed in the reply. It is not a critique file.
