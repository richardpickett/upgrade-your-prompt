# ADR 0001: Score the human's prompting

Status: Proposed
Date: 2026-11-16

## Context

A session log contains the human's prompts and the harness and model behavior. The product is a critique of prompting practice.

## Decision

The critique scores the human's prompting only. Model replies, tool calls, and tool output are evidence of what the human did next. They are not a second score. A fact the log never stored is a logging limit and must not lower a section.

## Consequences

Steering scores whether the next human prompt corrected a failure. The failure itself stays off the composite. Task success is context, not the score.
