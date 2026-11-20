# ADR 0006: Explicit skills; compiler is a reference

Status: Proposed
Date: 2026-11-16

## Context

The skills run inside whatever agent the user has. Models differ. The user named the Natural Language Compiler as a high bar, not a required library.

## Decision

Each skill step must be explicit enough that another agent cannot invent the missing rule. The compiler's practice (knowledge, decision records, standing instructions) informs the rubric. This repo does not depend on the compiler, its CLI, or its hub identity gate.

## Consequences

The Planit identity check is waived here. It is hub-only and is not shipped to adopters.
