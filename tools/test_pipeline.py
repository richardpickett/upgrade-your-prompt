#!/usr/bin/env python3
"""Pipeline tests. No home-directory stores."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_evidence import check  # noqa: E402
from harness_extract import (  # noqa: E402
    extract_codex,
    extract_copilot,
    extract_cursor_db,
    extract_cursor_transcript,
    extract_pi,
)
from patterns_report import build  # noqa: E402
from rung import headline, wilson_lower  # noqa: E402
from session_log import tool_record  # noqa: E402
from working_set import apply_scope, parse_scope  # noqa: E402


class ToolRecordTest(unittest.TestCase):
    def test_edit_keeps_path_and_drops_body(self) -> None:
        record = tool_record(
            "edit",
            {"path": "src/a.py", "stream_content": "secret body"},
            "wrote the file",
        )
        self.assertEqual(record["change_path"], "src/a.py")
        self.assertEqual(record["change_operation"], "edit")
        self.assertNotIn("secret body", record["tool_arguments"])
        self.assertIsNone(record["tool_result"])

    def test_shell_keeps_command_and_result(self) -> None:
        record = tool_record("bash", {"command": "pytest"}, "1 passed")
        self.assertIn("pytest", record["tool_arguments"])
        self.assertEqual(record["tool_result"], "1 passed")
        self.assertIsNone(record["change_operation"])


class ExtractTest(unittest.TestCase):
    def test_pi_and_omp_share_parser(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.jsonl"
            path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "session",
                                "version": 3,
                                "id": "s1",
                                "timestamp": "2026-11-01T00:00:00Z",
                                "cwd": "/work",
                            }
                        ),
                        json.dumps(
                            {
                                "type": "message",
                                "id": "t1",
                                "message": {
                                    "role": "user",
                                    "content": [{"type": "text", "text": "Name the end state."}],
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "message",
                                "id": "t2",
                                "message": {
                                    "role": "assistant",
                                    "content": [
                                        {"type": "thinking", "thinking": "hidden"},
                                        {
                                            "type": "toolCall",
                                            "id": "c1",
                                            "name": "edit",
                                            "arguments": {"path": "a.py", "stream_content": "BODY"},
                                        },
                                    ],
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            header, turns = extract_pi(path, "omp")
            self.assertEqual(header["agent"], "omp")
            self.assertEqual(turns[0]["text"], "Name the end state.")
            self.assertNotIn("BODY", json.dumps(turns))
            self.assertNotIn("hidden", json.dumps(turns))
            self.assertEqual(turns[1]["change_path"], "a.py")

    def test_codex_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rollout.jsonl"
            path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {"id": "c1", "timestamp": "2026-11-01T00:00:00Z", "cwd": "/work"},
                            }
                        ),
                        json.dumps(
                            {
                                "type": "response_item",
                                "payload": {
                                    "type": "message",
                                    "role": "user",
                                    "content": [{"type": "input_text", "text": "Ship the report."}],
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            header, turns = extract_codex(path)
            self.assertEqual(header["agent"], "codex")
            self.assertEqual(turns[0]["role"], "human")
            self.assertEqual(turns[0]["text"], "Ship the report.")

    def test_copilot_requests_and_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plain = Path(tmp) / "chat.json"
            plain.write_text(
                json.dumps(
                    {
                        "sessionId": "p1",
                        "creationDate": 1762000000000,
                        "requests": [
                            {
                                "message": {"text": "Write the decision down."},
                                "response": [{"value": "Recorded."}],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            header, turns = extract_copilot(plain)
            self.assertEqual([item["text"] for item in turns], ["Write the decision down.", "Recorded."])
            log = Path(tmp) / "chat.jsonl"
            log.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "kind": 0,
                                "v": {"sessionId": "p2", "requests": []},
                            }
                        ),
                        json.dumps(
                            {
                                "kind": 2,
                                "k": ["requests"],
                                "v": [{"message": {"text": "Added later."}, "response": [{"value": "Yes."}]}],
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            header, turns = extract_copilot(log)
            self.assertEqual(header["session_id"], "p2")
            self.assertEqual(turns[0]["text"], "Added later.")

    def test_cursor_transcript_strips_replace_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "abc.jsonl"
            path.write_text(
                json.dumps(
                    {
                        "role": "assistant",
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "name": "StrReplace",
                                    "input": {"path": "a.py", "old_string": "OLD", "new_string": "NEW"},
                                }
                            ]
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            _header, turns = extract_cursor_transcript(path)
            blob = json.dumps(turns)
            self.assertNotIn("OLD", blob)
            self.assertNotIn("NEW", blob)
            self.assertEqual(turns[0]["change_operation"], "edit")

    def test_cursor_db(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "store.db"
            con = sqlite3.connect(db)
            con.execute("CREATE TABLE blobs (id TEXT, data BLOB)")
            con.execute(
                "INSERT INTO blobs VALUES (?, ?)",
                ("1", json.dumps({"role": "user", "content": [{"type": "text", "text": "Hello"}]}).encode()),
            )
            con.commit()
            con.close()
            header, turns = extract_cursor_db(db, "sid", {"cwd": "/work"})
            self.assertEqual(header["workspace"], "/work")
            self.assertEqual(turns[0]["text"], "Hello")


class ScopeTest(unittest.TestCase):
    def test_last_month_and_narrow_ask(self) -> None:
        now = datetime(2026, 11, 19, tzinfo=timezone.utc)
        spec = parse_scope("all from the last month", now)
        self.assertIsNotNone(spec)
        inventory = [
            {"session_id": "old", "agent": "omp", "at": "2026-09-01T00:00:00Z"},
            {"session_id": "new", "agent": "cursor", "at": "2026-11-10T00:00:00Z"},
        ]
        status, token, _delete = apply_scope(inventory, spec, {"sessions": []})
        self.assertEqual(token, "applied")
        self.assertEqual([row["session_id"] for row in status["sessions"]], ["new"])
        status["sessions"][0]["state"] = "analyzed"
        narrower = parse_scope("omp", now)
        again, token, _delete = apply_scope(inventory, narrower, status)
        self.assertEqual(token, "ask-remove")
        self.assertEqual(again["sessions"][0]["state"], "analyzed")
        narrower["remove_analyses"] = False
        kept, token, delete = apply_scope(inventory, narrower, status)
        self.assertEqual(token, "applied")
        self.assertEqual([row["session_id"] for row in kept["sessions"]], ["old"])
        self.assertEqual(delete, [])


class RungTest(unittest.TestCase):
    def test_sixteen_clears_and_one_does_not(self) -> None:
        many = headline([{"rung": 1, "result": "good"} for _ in range(16)])
        self.assertEqual(many["headline"], 1)
        self.assertGreaterEqual(wilson_lower(16, 16), 0.5)
        one = headline([{"rung": 1, "result": "good"}])
        self.assertEqual(one["headline"], 0)
        self.assertLess(wilson_lower(1, 1), 0.5)

    def test_gap_stops_the_block(self) -> None:
        score = headline(
            [{"rung": 1, "result": "good"} for _ in range(16)]
            + [{"rung": 3, "result": "good"} for _ in range(16)]
        )
        self.assertEqual(score["headline"], 1)


class EvidenceTest(unittest.TestCase):
    def test_quote_must_be_in_the_extract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            extract = root / "s.jsonl"
            extract.write_text(
                json.dumps({"record": "turn", "text": "Name the finished condition."}) + "\n",
                encoding="utf-8",
            )
            evidence = root / "e.jsonl"
            evidence.write_text(
                json.dumps(
                    {"indicator_id": "P01", "rung": 1, "result": "good", "quote": "not in the log"}
                )
                + "\n",
                encoding="utf-8",
            )
            problems = check(extract, evidence)
            self.assertTrue(any("quote" in item for item in problems))

    def test_report_reads_analysis_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "session-evidence").mkdir()
            (root / "session-evidence" / "cursor--s.jsonl").write_text(
                "\n".join(
                    json.dumps({"indicator_id": "P01", "rung": 1, "result": "good"}) for _ in range(16)
                )
                + "\n",
                encoding="utf-8",
            )
            text = build(root)
            self.assertIn("Headline rung: 1", text)
            self.assertFalse((root / "session-logs").exists())


if __name__ == "__main__":
    unittest.main()
