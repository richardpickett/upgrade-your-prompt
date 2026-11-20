#!/usr/bin/env python3
"""Advance the working set. Export is deterministic. Analysis is not.

Usage:
  python3 tools/run_pipeline.py scope --text "all"
  python3 tools/run_pipeline.py scope --text "all from the last month" --remove-analyses
  python3 tools/run_pipeline.py export
  python3 tools/run_pipeline.py report
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_evidence import check  # noqa: E402
from harness_extract import (  # noqa: E402
    extract_codex,
    extract_copilot,
    extract_cursor_db,
    extract_cursor_transcript,
    extract_pi,
    write_log,
)
from inventory import (  # noqa: E402
    list_codex,
    list_copilot,
    list_cursor_chats,
    list_cursor_transcripts,
    list_pi,
)
from patterns_report import write as write_report  # noqa: E402
from working_set import STATUS, apply_scope, load, mark, parse_scope, save  # noqa: E402


def home_inventory() -> list[dict]:
    home = Path.home()
    rows = []
    rows.extend(list_pi(home / ".pi" / "agent" / "sessions", "pi"))
    rows.extend(list_pi(home / ".omp" / "agent" / "sessions", "omp"))
    for key in ("PI_CODING_AGENT_SESSION_DIR", "PI_CODING_AGENT_DIR"):
        value = os.environ.get(key)
        if value:
            root = Path(value)
            if key.endswith("DIR") and key != "PI_CODING_AGENT_SESSION_DIR":
                root = root / "sessions"
            rows.extend(list_pi(root, "pi"))
    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    rows.extend(list_codex(codex_home / "sessions"))
    rows.extend(list_copilot(home / ".config" / "Code" / "User"))
    rows.extend(list_cursor_chats(home / ".cursor" / "chats"))
    rows.extend(list_cursor_transcripts(home / ".cursor" / "projects"))
    seen = set()
    unique = []
    for row in rows:
        key = (row["agent"], row["session_id"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def export_one(item: dict, dest_root: Path) -> None:
    source = Path(item["source"])
    kind = item["kind"]
    if kind == "pi":
        header, turns = extract_pi(source, item["agent"])
    elif kind == "codex":
        header, turns = extract_codex(source)
    elif kind == "copilot":
        header, turns = extract_copilot(source)
    elif kind == "cursor-db":
        meta_path = source.parent / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
        header, turns = extract_cursor_db(source, item["session_id"], meta)
    elif kind == "cursor-transcript":
        header, turns = extract_cursor_transcript(source)
    else:
        raise ValueError(f"unknown kind {kind}")
    write_log(dest_root / "session-logs" / f"{item['agent']}--{item['session_id']}.jsonl", header, turns)


def cmd_scope(text: str, remove: bool | None) -> int:
    spec = parse_scope(text)
    if spec is None:
        print("scope-unparsed")
        return 2
    if remove is True:
        spec["remove_analyses"] = True
    elif remove is False:
        spec["remove_analyses"] = False
    status = load()
    updated, token, delete_rows = apply_scope(home_inventory(), spec, status)
    if token == "ask-remove":
        print("ask-remove")
        return 3
    for row in delete_rows:
        stem = f"{row['agent']}--{row['session_id']}"
        for folder in ("session-evidence", "session-critiques", "session-observations"):
            path = ROOT / folder / f"{stem}.jsonl"
            md = ROOT / folder / f"{stem}.md"
            if path.is_file():
                path.unlink()
            if md.is_file():
                md.unlink()
    save(updated)
    print(f"applied {len(updated['sessions'])}")
    return 0


def cmd_export() -> int:
    status = load()
    by_key = {(item["agent"], item["session_id"]): item for item in home_inventory()}
    failed = 0
    for row in status["sessions"]:
        if row["state"] != "new":
            continue
        item = by_key.get((row["agent"], row["session_id"]))
        if item is None:
            mark(status, row["agent"], row["session_id"], "failed", "session file not found")
            failed += 1
            continue
        try:
            export_one(item, ROOT)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            mark(status, row["agent"], row["session_id"], "failed", exc.__class__.__name__)
            failed += 1
            continue
        mark(status, row["agent"], row["session_id"], "exported")
    save(status)
    print(f"failed {failed}")
    return 0


def cmd_pending() -> int:
    status = load()
    for row in status["sessions"]:
        if row["state"] == "exported":
            print(f"{row['agent']}\t{row['session_id']}")
    return 0


def cmd_accept(agent: str, session_id: str) -> int:
    stem = f"{agent}--{session_id}"
    extract = ROOT / "session-logs" / f"{stem}.jsonl"
    evidence = ROOT / "session-evidence" / f"{stem}.jsonl"
    problems = check(extract, evidence)
    if problems:
        for item in problems:
            print(item)
        return 1
    status = load()
    mark(status, agent, session_id, "analyzed")
    save(status)
    print("analyzed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Working-set pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    scope = sub.add_parser("scope")
    scope.add_argument("--text", required=True)
    group = scope.add_mutually_exclusive_group()
    group.add_argument("--remove-analyses", action="store_true")
    group.add_argument("--keep-analyses", action="store_true")
    sub.add_parser("export")
    sub.add_parser("pending")
    accept = sub.add_parser("accept")
    accept.add_argument("--agent", required=True)
    accept.add_argument("--id", required=True)
    sub.add_parser("report")
    args = parser.parse_args()
    if args.cmd == "scope":
        remove = True if args.remove_analyses else False if args.keep_analyses else None
        return cmd_scope(args.text, remove)
    if args.cmd == "export":
        return cmd_export()
    if args.cmd == "pending":
        return cmd_pending()
    if args.cmd == "accept":
        return cmd_accept(args.agent, args.id)
    write_report(ROOT)
    print("report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
