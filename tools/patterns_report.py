#!/usr/bin/env python3
"""Patterns report. Reads analyses only. Does not open extracts or harness stores."""

from __future__ import annotations

import json
from pathlib import Path

from rung import headline


def build(root: Path) -> str:
    evidence_dir = root / "session-evidence"
    critiques = root / "session-critiques"
    observations = root / "session-observations"
    lines = ["# Patterns report", ""]
    files = sorted(evidence_dir.glob("*.jsonl")) if evidence_dir.is_dir() else []
    if not files:
        lines.append("No analyses yet.")
        lines.append("")
        return "\n".join(lines)
    for path in files:
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        score = headline(rows)
        critique = critiques / f"{path.stem}.md"
        lines.append(f"## {path.stem}")
        lines.append("")
        lines.append(f"Headline rung: {score['headline']}")
        if critique.is_file():
            lines.append("")
            lines.append(critique.read_text(encoding="utf-8").strip())
        obs = observations / f"{path.stem}.jsonl"
        if obs.is_file():
            lines.append("")
            lines.append("Observations:")
            for line in obs.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    item = json.loads(line)
                    lines.append(f"- {item.get('kind')}: {item.get('text')}")
        lines.append("")
    return "\n".join(lines)


def write(root: Path) -> Path:
    dest = root / "patterns-report.md"
    dest.write_text(build(root), encoding="utf-8")
    return dest
