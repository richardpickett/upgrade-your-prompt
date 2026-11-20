#!/usr/bin/env python3
"""Check that an analysis only uses known factors and quotes the extract."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "fitness-indicators.md"


def factor_ids() -> set[str]:
    found = set()
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| ([PF]\d+) \|", line)
        if match:
            found.add(match.group(1))
    return found


def extract_text(path: Path) -> str:
    chunks = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("text"):
            chunks.append(row["text"])
        if row.get("tool_arguments"):
            chunks.append(row["tool_arguments"])
        if row.get("tool_result"):
            chunks.append(row["tool_result"])
    return "\n".join(chunks)


def check(extract: Path, evidence: Path) -> list[str]:
    """Return problems. Empty means the evidence file may be marked analyzed."""
    known = factor_ids()
    source = extract_text(extract)
    problems = []
    for number, line in enumerate(evidence.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        indicator = row.get("indicator_id")
        if indicator not in known:
            problems.append(f"line {number}: unknown factor {indicator}")
        quote = row.get("quote") or ""
        if not quote or quote not in source:
            problems.append(f"line {number}: quote is not in the extract")
        if row.get("result") not in {"good", "bad"}:
            problems.append(f"line {number}: result must be good or bad")
    return problems
