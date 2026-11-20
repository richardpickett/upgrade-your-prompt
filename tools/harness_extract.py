#!/usr/bin/env python3
"""Read harness session files into the common JSONL. No analysis."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from session_log import dumps, session_header, tool_record, turn_line

AGENTS = ("cursor", "copilot", "codex", "omp", "pi")


def iso_ms(value) -> str | None:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, str) and value:
        return value
    return None


def text_from_parts(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    chunks = []
    for part in content:
        if isinstance(part, str):
            chunks.append(part)
        elif isinstance(part, dict):
            if isinstance(part.get("text"), str) and part.get("type") in {None, "text", "input_text", "output_text"}:
                chunks.append(part["text"])
            elif isinstance(part.get("value"), str):
                chunks.append(part["value"])
    return "\n".join(item for item in chunks if item)


def _with_tools(session_id: str, seq: int, turn_id, parent, role: str, at, text: str, tool: dict | None) -> dict:
    extra = tool or {}
    return turn_line(session_id, seq, turn_id, parent, role, at, text, **extra)


def extract_pi(path: Path, agent: str) -> tuple[dict, list[dict]]:
    """Pi and oMP share this file shape."""
    session = None
    raw_turns = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get("type") == "session" and session is None:
            session = obj
            continue
        if obj.get("type") != "message":
            continue
        message = obj.get("message") or {}
        role = message.get("role")
        content = message.get("content")
        at = iso_ms(message.get("timestamp")) or obj.get("timestamp")
        turn_id = obj.get("id")
        parent = obj.get("parentId")
        if role == "user":
            raw_turns.append(("human", turn_id, parent, at, text_from_parts(content), None))
        elif role == "assistant":
            body = text_from_parts(content)
            if body:
                raw_turns.append(("model", turn_id, parent, at, body, None))
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "toolCall":
                        raw_turns.append(
                            (
                                "model",
                                part.get("id") or turn_id,
                                turn_id,
                                at,
                                "",
                                tool_record(part.get("name"), part.get("arguments"), None),
                            )
                        )
        elif role == "toolResult":
            record = tool_record(message.get("toolName"), None, text_from_parts(content))
            raw_turns.append(("model", turn_id, parent, at, "", record))
    if session is None:
        raise ValueError("session line missing")
    session_id = session.get("id") or path.stem.split("_")[-1]
    missing = []
    if not any(item[0] == "human" and item[4] for item in raw_turns):
        missing.append("Human text")
    if not any(item[0] == "model" and item[4] for item in raw_turns):
        missing.append("Model text")
    header = session_header(
        session_id,
        agent,
        session.get("timestamp"),
        session.get("timestamp"),
        session.get("cwd"),
        missing,
    )
    turns = [
        _with_tools(session_id, index, turn_id, parent, role, at, text, tool)
        for index, (role, turn_id, parent, at, text, tool) in enumerate(raw_turns, start=1)
    ]
    return header, turns


def extract_codex(path: Path) -> tuple[dict, list[dict]]:
    """Codex rollout JSONL. Modern envelope and a bare-item fallback."""
    session_id = None
    started = None
    workspace = None
    raw = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        kind = obj.get("type")
        payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else obj
        if kind == "session_meta" or (session_id is None and payload.get("id") and "timestamp" in payload and kind is None):
            session_id = payload.get("id") or payload.get("session_id") or session_id
            started = payload.get("timestamp") or obj.get("timestamp") or started
            workspace = payload.get("cwd") or workspace
            continue
        if kind not in {None, "response_item"}:
            continue
        inner = payload.get("type")
        if inner == "message" or payload.get("role") in {"user", "assistant"}:
            role = "human" if payload.get("role") == "user" else "model"
            raw.append((role, None, None, obj.get("timestamp"), text_from_parts(payload.get("content")), None))
        elif inner in {"function_call", "custom_tool_call", "local_shell_call"}:
            name = payload.get("name") or "shell"
            args = payload.get("arguments") or payload.get("action")
            raw.append(("model", payload.get("call_id"), None, obj.get("timestamp"), "", tool_record(name, args, None)))
        elif inner in {"function_call_output", "tool_result"}:
            raw.append(
                (
                    "model",
                    payload.get("call_id"),
                    None,
                    obj.get("timestamp"),
                    "",
                    tool_record(payload.get("name"), None, text_from_parts(payload.get("output") or payload.get("content"))),
                )
            )
    if not session_id:
        session_id = path.stem.split("-")[-1]
    missing = []
    if not any(item[0] == "human" and item[4] for item in raw):
        missing.append("Human text")
    header = session_header(session_id, "codex", started, started, workspace, missing)
    turns = [
        _with_tools(session_id, index, turn_id, parent, role, at, text, tool)
        for index, (role, turn_id, parent, at, text, tool) in enumerate(raw, start=1)
    ]
    return header, turns


def _copilot_requests(data: dict) -> list:
    requests = data.get("requests")
    return requests if isinstance(requests, list) else []


def replay_copilot(data: dict) -> dict:
    """Apply a JSONL append log onto a snapshot. kind 0 replaces, 1 sets, 2 pushes."""
    return data


def load_copilot(path: Path) -> dict:
    if path.suffix == ".jsonl":
        state = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            kind = obj.get("kind")
            if kind == 0 and isinstance(obj.get("v"), dict):
                state = obj["v"]
            elif kind == 2 and state is not None and obj.get("k") == ["requests"] and isinstance(obj.get("v"), list):
                state.setdefault("requests", []).extend(obj["v"])
            elif kind == 1 and state is not None and isinstance(obj.get("k"), list):
                cursor = state
                keys = obj["k"]
                for key in keys[:-1]:
                    if isinstance(key, int):
                        while len(cursor) <= key:
                            cursor.append({})
                        cursor = cursor[key]
                    else:
                        cursor = cursor.setdefault(key, {})
                last = keys[-1]
                if isinstance(last, int) and isinstance(cursor, list):
                    while len(cursor) <= last:
                        cursor.append(None)
                    cursor[last] = obj.get("v")
                elif isinstance(cursor, dict):
                    cursor[last] = obj.get("v")
        if not isinstance(state, dict):
            raise ValueError("copilot snapshot missing")
        return state
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("copilot file is not an object")
    return data


def extract_copilot(path: Path) -> tuple[dict, list[dict]]:
    data = load_copilot(path)
    session_id = data.get("sessionId") or path.stem
    raw = []
    for request in _copilot_requests(data):
        if not isinstance(request, dict):
            continue
        message = request.get("message")
        human = message.get("text") if isinstance(message, dict) else text_from_parts(message)
        if not human and isinstance(message, dict):
            human = text_from_parts(message.get("parts"))
        raw.append(("human", request.get("requestId"), None, iso_ms(request.get("timestamp")), human or "", None))
        response = request.get("response")
        if isinstance(response, list):
            bits = []
            for part in response:
                if isinstance(part, str):
                    bits.append(part)
                elif isinstance(part, dict) and isinstance(part.get("value"), str):
                    bits.append(part["value"])
                elif isinstance(part, dict) and part.get("kind") == "toolInvocation":
                    raw.append(
                        (
                            "model",
                            None,
                            None,
                            iso_ms(request.get("timestamp")),
                            "",
                            tool_record(part.get("toolId") or part.get("name"), part.get("parameters") or part.get("input"), None),
                        )
                    )
            if bits:
                raw.append(("model", None, None, iso_ms(request.get("timestamp")), "\n".join(bits), None))
    missing = []
    if not any(item[0] == "human" and item[4] for item in raw):
        missing.append("Human text")
    if not any(item[0] == "model" and item[4] for item in raw):
        missing.append("Model text")
    header = session_header(
        session_id,
        "copilot",
        iso_ms(data.get("creationDate")),
        iso_ms(data.get("lastMessageDate")),
        data.get("workingDirectory"),
        missing,
    )
    turns = [
        _with_tools(session_id, index, turn_id, parent, role, at, text, tool)
        for index, (role, turn_id, parent, at, text, tool) in enumerate(raw, start=1)
    ]
    return header, turns


def _cursor_messages(obj: dict) -> list[tuple]:
    role = obj.get("role")
    content = obj.get("content")
    rows = []
    if role == "user":
        rows.append(("human", text_from_parts(content), None))
        return rows
    if role not in {"assistant", "tool"}:
        return rows
    body = text_from_parts(content)
    if body:
        rows.append(("model", body, None))
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") in {"tool-call", "tool_use"}:
                name = part.get("toolName") or part.get("name")
                args = part.get("args") or part.get("arguments") or part.get("input")
                rows.append(("model", "", tool_record(name, args, None)))
            elif part.get("type") in {"tool-result", "tool_result"}:
                name = part.get("toolName") or part.get("name")
                result = part.get("result")
                result_text = result if isinstance(result, str) else text_from_parts(result)
                rows.append(("model", "", tool_record(name, None, result_text)))
    return rows


def extract_cursor_db(path: Path, session_id: str, meta: dict | None) -> tuple[dict, list[dict]]:
    meta = meta or {}
    raw = []
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        for blob_id, data in con.execute("SELECT id, data FROM blobs ORDER BY rowid"):
            if isinstance(data, str):
                data = data.encode()
            try:
                obj = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(obj, dict) and "role" in obj:
                for role, text, tool in _cursor_messages(obj):
                    raw.append((role, blob_id, None, None, text, tool))
    finally:
        con.close()
    missing = []
    if not any(item[0] == "human" and item[4] for item in raw):
        missing.append("Human text")
    if not any(item[0] == "model" and item[4] for item in raw):
        missing.append("Model text")
    header = session_header(
        session_id,
        "cursor",
        iso_ms(meta.get("createdAtMs")),
        iso_ms(meta.get("updatedAtMs")),
        meta.get("cwd"),
        missing,
    )
    turns = [
        _with_tools(session_id, index, turn_id, parent, role, at, text, tool)
        for index, (role, turn_id, parent, at, text, tool) in enumerate(raw, start=1)
    ]
    return header, turns


def extract_cursor_transcript(path: Path) -> tuple[dict, list[dict]]:
    session_id = path.stem
    raw = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        role = obj.get("role")
        message = obj.get("message") if isinstance(obj.get("message"), dict) else {}
        content = message.get("content")
        mapped = "human" if role == "user" else "model" if role == "assistant" else None
        if mapped is None:
            continue
        body = text_from_parts(content)
        if body:
            raw.append((mapped, None, None, None, body, None))
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") in {"tool_use", "tool-call"}:
                    name = part.get("name") or part.get("toolName")
                    args = part.get("input") or part.get("args")
                    raw.append(("model", None, None, None, "", tool_record(name, args, None)))
    missing = []
    if not any(item[0] == "human" and item[4] for item in raw):
        missing.append("Human text")
    header = session_header(session_id, "cursor", None, None, None, missing)
    turns = [
        _with_tools(session_id, index, turn_id, parent, role, at, text, tool)
        for index, (role, turn_id, parent, at, text, tool) in enumerate(raw, start=1)
    ]
    return header, turns


def write_log(dest: Path, header: dict, turns: list[dict]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(dumps(header, turns), encoding="utf-8")
