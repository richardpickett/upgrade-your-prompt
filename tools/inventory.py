#!/usr/bin/env python3
"""List sessions from harness stores. Roots are arguments so tests stay off the home directory."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from harness_extract import iso_ms


def _first_session(path: Path) -> dict:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get("type") == "session":
            return obj
        payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else obj
        if obj.get("type") == "session_meta" or payload.get("id"):
            return payload
    return {}


def list_pi(root: Path, agent: str) -> list[dict]:
    if not root.is_dir():
        return []
    rows = []
    for path in sorted(root.glob("**/*.jsonl")):
        if "blobs" in path.parts:
            continue
        header = _first_session(path)
        session_id = header.get("id") or path.stem.split("_")[-1]
        rows.append(
            {
                "session_id": session_id,
                "agent": agent,
                "at": header.get("timestamp"),
                "workspace": header.get("cwd"),
                "source": str(path),
                "kind": "pi",
            }
        )
    return rows


def list_codex(root: Path) -> list[dict]:
    if not root.is_dir():
        return []
    rows = []
    for path in sorted(root.glob("**/rollout-*.jsonl")):
        header = _first_session(path)
        rows.append(
            {
                "session_id": header.get("id") or path.stem,
                "agent": "codex",
                "at": header.get("timestamp"),
                "workspace": header.get("cwd"),
                "source": str(path),
                "kind": "codex",
            }
        )
    return rows


def copilot_store_path(path: Path) -> bool:
    """True when the file sits in an IDE Copilot Chat store.

    Stores are workspaceStorage chatSessions and GitHub.copilot-chat
    transcripts. Other JSON under the VS Code User folder is not Copilot Chat.
    """
    parts = {part.lower() for part in path.parts}
    return "chatsessions" in parts or "github.copilot-chat" in parts


def _copilot_row(path: Path) -> dict | None:
    """Return one inventory row from a Copilot Chat file, or None if unreadable."""
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        session_id = data.get("sessionId") or path.stem
        at = iso_ms(data.get("creationDate"))
        workspace = data.get("workingDirectory")
    elif path.suffix == ".jsonl":
        session_id = path.stem
        at = None
        workspace = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("kind") == 0 and isinstance(obj.get("v"), dict):
                session_id = obj["v"].get("sessionId") or session_id
                at = iso_ms(obj["v"].get("creationDate"))
                workspace = obj["v"].get("workingDirectory")
                break
        else:
            if not session_id:
                return None
    else:
        return None
    return {
        "session_id": session_id,
        "agent": "copilot",
        "at": at,
        "workspace": workspace,
        "source": str(path),
        "kind": "copilot",
    }


def list_copilot(root: Path) -> list[dict]:
    """List IDE Copilot Chat sessions under a VS Code User root."""
    if not root.is_dir():
        return []
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".jsonl"}:
            continue
        if not copilot_store_path(path):
            continue
        try:
            row = _copilot_row(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            continue
        if row is not None:
            rows.append(row)
    return rows


def list_cursor_chats(root: Path) -> list[dict]:
    if not root.is_dir():
        return []
    rows = []
    for meta_path in sorted(root.glob("*/*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        session_id = meta.get("id") or meta_path.parent.name
        db = meta_path.parent / "store.db"
        rows.append(
            {
                "session_id": session_id,
                "agent": "cursor",
                "at": iso_ms(meta.get("createdAtMs")),
                "workspace": meta.get("cwd"),
                "source": str(db if db.is_file() else meta_path),
                "kind": "cursor-db" if db.is_file() else "cursor-meta",
            }
        )
    return rows


def list_cursor_transcripts(root: Path) -> list[dict]:
    if not root.is_dir():
        return []
    rows = []
    for path in sorted(root.glob("**/agent-transcripts/**/*.jsonl")):
        rows.append(
            {
                "session_id": path.stem,
                "agent": "cursor",
                "at": None,
                "workspace": None,
                "source": str(path),
                "kind": "cursor-transcript",
            }
        )
    return rows


def has_blobs(path: Path) -> bool:
    if not path.is_file():
        return False
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        row = con.execute("SELECT 1 FROM blobs LIMIT 1").fetchone()
    except sqlite3.Error:
        return False
    finally:
        con.close()
    return row is not None
