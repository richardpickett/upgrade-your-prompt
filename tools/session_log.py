#!/usr/bin/env python3
"""Common session JSONL. ADR 0007 shape plus ADR 0010 change records.

File bodies are omitted. A change is stored as path and operation.
"""

from __future__ import annotations

import json
from typing import Any

ENGINE = "2026-11-19-factors-v1"

BODY_KEYS = {
    "contents",
    "content",
    "old_string",
    "new_string",
    "stream_content",
    "file_text",
    "oldText",
    "newText",
}

FILE_TOOLS = {
    "write",
    "edit",
    "strreplace",
    "delete",
    "read",
    "applypatch",
    "apply_patch",
}


def parse_args(value: Any) -> dict | None:
    """Return a dict of tool arguments, or None when there are none."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return {"raw": value}
        if isinstance(loaded, dict):
            return loaded
    return {"raw": str(value)}


def tool_record(name: str | None, arguments: Any, result: str | None) -> dict:
    """Keep a tool call. Drop file text. Keep path and operation."""
    args = parse_args(arguments)
    tool = name or ""
    key = tool.lower().replace("-", "")
    path = None
    operation = None
    stored = args
    stored_result = result
    fileish = key in FILE_TOOLS or key in {"str_replace"}
    if isinstance(args, dict):
        path = args.get("path") or args.get("file_path") or args.get("target_file")
        has_body = any(item in args for item in BODY_KEYS)
        if fileish or has_body or key in {"read"}:
            if key in {"write"}:
                operation = "write"
            elif key in {"delete"}:
                operation = "delete"
            elif key in {"read"}:
                operation = "read"
            else:
                operation = "edit"
            stored = {k: v for k, v in args.items() if k not in BODY_KEYS}
            if path is not None:
                stored["path"] = path
            if operation in {"write", "edit", "delete", "read"}:
                stored_result = None
    return {
        "tool_name": name,
        "tool_arguments": json.dumps(stored, ensure_ascii=False) if stored is not None else None,
        "tool_result": stored_result,
        "change_path": None if operation in {None, "read"} else path,
        "change_operation": None if operation in {None, "read"} else operation,
    }


def session_header(session_id: str, agent: str, started_at, updated_at, workspace, missing: list[str]) -> dict:
    """Line 1 of a session log."""
    return {
        "record": "session",
        "schema_version": 2,
        "session_id": session_id,
        "agent": agent,
        "started_at": started_at,
        "updated_at": updated_at,
        "workspace": workspace,
        "missing_fields": missing,
        "analysis_engine": ENGINE,
    }


def turn_line(session_id: str, seq: int, turn_id, parent, role: str, at, text: str, **extra) -> dict:
    """One turn. seq is the order in the file."""
    row = {
        "record": "turn",
        "session_id": session_id,
        "seq": seq,
        "turn_id": turn_id,
        "parent_turn_id": parent,
        "role": role,
        "at": at,
        "text": text or "",
        "tool_name": None,
        "tool_arguments": None,
        "tool_result": None,
        "change_path": None,
        "change_operation": None,
    }
    row.update(extra)
    return row


def dumps(header: dict, turns: list[dict]) -> str:
    """UTF-8 JSONL text. Session line, then turns."""
    lines = [json.dumps(header, ensure_ascii=False)]
    lines.extend(json.dumps(item, ensure_ascii=False) for item in turns)
    return "\n".join(lines) + "\n"
