#!/usr/bin/env python3
"""Working set. One status row per session the operator put in scope.

States: new, exported, analyzed, failed.
A narrower scope that drops an analyzed session does nothing until the
operator says to remove those analyses or to keep them.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from session_log import ENGINE

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "working-set" / "status.json"
UUID = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
HARNESSES = ("cursor", "copilot", "codex", "omp", "pi")


def load(path: Path = STATUS) -> dict:
    if not path.is_file():
        return {"sessions": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("sessions"), list):
        raise ValueError("status file is not a session list")
    return data


def save(data: dict, path: Path = STATUS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def parse_scope(text: str, now: datetime | None = None) -> dict | None:
    """Map the phrases the operator already named. Unknown prose returns None."""
    now = now or datetime.now(timezone.utc)
    raw = text.strip().lower()
    remove = None
    if "remove analys" in raw:
        remove = True
    elif "keep analys" in raw:
        remove = False
    agents = [name for name in HARNESSES if re.search(rf"\b{name}\b", raw)]
    ids = UUID.findall(text)
    since = None
    if "last month" in raw:
        since = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    mentions_all = raw == "all" or raw.startswith("all ") or raw.startswith("all of")
    if since is None and not mentions_all and not agents and not ids:
        return None
    return {
        "since": since,
        "agents": agents,
        "ids": ids,
        "remove_analyses": remove,
        "all": mentions_all or (since is not None and not agents and not ids),
    }


def selected(inventory: list[dict], spec: dict) -> list[dict]:
    rows = []
    wanted_ids = set(spec.get("ids") or [])
    wanted_agents = set(spec.get("agents") or [])
    since = spec.get("since")
    for item in inventory:
        if wanted_ids and item["session_id"] not in wanted_ids:
            continue
        if wanted_agents and item["agent"] not in wanted_agents:
            continue
        if since and (not item.get("at") or item["at"] < since):
            continue
        rows.append(item)
    return rows


def apply_scope(inventory: list[dict], spec: dict, status: dict) -> tuple[dict, str, list[dict]]:
    """Return status, token, and analyzed rows to delete.

    Token is applied or ask-remove. ask-remove leaves status unchanged.
    remove_analyses false drops the rows and leaves the analysis files.
    remove_analyses true drops the rows and returns them for deletion.
    """
    keep = {(row["agent"], row["session_id"]): row for row in selected(inventory, spec)}
    current = {(row["agent"], row["session_id"]): row for row in status["sessions"]}
    dropped = [row for key, row in current.items() if key not in keep and row.get("state") == "analyzed"]
    if dropped and spec.get("remove_analyses") is None:
        return status, "ask-remove", []
    next_rows = []
    for key, item in keep.items():
        old = current.get(key)
        if old:
            next_rows.append(old)
        else:
            next_rows.append(
                {
                    "session_id": item["session_id"],
                    "agent": item["agent"],
                    "state": "new",
                    "at": item.get("at"),
                    "workspace": item.get("workspace"),
                    "failure": "",
                    "analysis_engine": "",
                }
            )
    updated = {"sessions": next_rows}
    delete = dropped if spec.get("remove_analyses") else []
    return updated, "applied", delete


def key_of(row: dict) -> tuple[str, str]:
    return row["agent"], row["session_id"]


def mark(status: dict, agent: str, session_id: str, state: str, failure: str = "") -> None:
    for row in status["sessions"]:
        if row["agent"] == agent and row["session_id"] == session_id:
            row["state"] = state
            row["failure"] = failure
            if state == "analyzed":
                row["analysis_engine"] = ENGINE
            return
    raise KeyError(f"{agent} {session_id}")
