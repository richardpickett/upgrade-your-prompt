#!/usr/bin/env python3
"""Rung math from an evidence file. ADR 0008. Judgment is not done here."""

from __future__ import annotations

import math
from collections import defaultdict


def wilson_lower(good: int, total: int, z: float = 1.96) -> float:
    """Lower bound of the 95% Wilson interval, as a fraction."""
    if total <= 0:
        return 0.0
    phat = good / total
    denom = 1 + z * z / total
    centre = phat + z * z / (2 * total)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)
    return (centre - margin) / denom


def headline(rows: list[dict]) -> dict:
    """Highest rung with rate >= 80% and strength >= 50%, contiguous from 1.

    A row is {rung: int, result: good|bad}. Empty rungs are skipped, so the
    block stops at the first occupied rung that fails, or at a gap before it.
    """
    counts: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    for row in rows:
        rung = int(row["rung"])
        bucket = counts[rung]
        bucket[1] += 1
        if row["result"] == "good":
            bucket[0] += 1
    if not counts:
        return {"headline": 0, "rungs": []}
    detail = []
    best = 0
    expected = 1
    for rung in range(1, max(counts) + 1):
        if rung not in counts:
            break
        good, total = counts[rung]
        rate = good / total
        strength = wilson_lower(good, total)
        clears = rate >= 0.8 and strength >= 0.5
        detail.append(
            {
                "rung": rung,
                "good": good,
                "total": total,
                "rate": rate,
                "strength": strength,
                "clears": clears,
            }
        )
        if rung != expected or not clears:
            break
        best = rung
        expected += 1
    return {"headline": best, "rungs": detail}
