import json
import unittest
from pathlib import Path

from replay import investigate, workbook

ROOT = Path(__file__).resolve().parents[1]


def load(name="reset"):
    return json.loads((ROOT / "cases" / (name + ".json")).read_text(encoding="utf-8"))


class ReplayTests(unittest.TestCase):
    def test_fixture_evaluation_and_published_workbooks(self):
        for name, expected in [("reset", "corroborated"), ("replacement", "explained"),
                               ("handoff", "insufficient")]:
            with self.subTest(case=name):
                case = load(name)
                result = investigate(case)
                self.assertEqual(result["disposition"], expected)
                self.assertTrue(result["trigger_reproduced"])
                self.assertEqual(result["analyst_decision"], "PENDING")
                self.assertEqual(workbook(case, result), (ROOT / "examples" / (name + ".md")).read_text(encoding="utf-8"))
                ids = {e["id"] for e in case["events"]}
                for check in result["trace"]:
                    self.assertTrue(ids.issuperset(check["evidence"]))
                    self.assertEqual(check["matched"], bool(check["evidence"]))

    def test_evidence_order_and_labels_are_irrelevant(self):
        case = load()
        case["expected"] = "explained"
        case["alert"]["id"] = "DEMO-2"
        case["events"].reverse()
        self.assertEqual(investigate(case)["disposition"], "corroborated")

    def test_remove_any_required_signal(self):
        for kind in ("reset", "enrollment", "remote_access", "denial"):
            with self.subTest(kind=kind):
                case = load()
                case["events"] = [e for e in case["events"] if e["kind"] != kind]
                self.assertEqual(investigate(case)["disposition"], "insufficient")

    def test_mismatched_session_actor_factor_or_late_endpoint(self):
        for kind, key, value in [("remote_access", "session", "other"),
                                 ("denial", "actor", "other"), ("denial", "verified", False),
                                 ("enrollment", "factor", "other"),
                                 ("remote_access", "time", "2026-02-01T09:40:01Z")]:
            with self.subTest(key=key):
                case = load()
                next(e for e in case["events"] if e["kind"] == kind)[key] = value
                self.assertEqual(investigate(case)["disposition"], "insufficient")

    def test_contradiction_overrides_complete_chain(self):
        case = load()
        case["events"].append(dict(case["events"][-1], id="EX", kind="confirmation"))
        self.assertEqual(investigate(case)["disposition"], "insufficient")

    def test_post_hoc_approval_cannot_explain(self):
        case = load("replacement")
        case["events"][0]["time"] = "2026-02-02T09:06:00Z"
        self.assertEqual(investigate(case)["disposition"], "insufficient")

    def test_duplicate_ids_rejected(self):
        case = load()
        case["events"].append(case["events"][0])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            investigate(case)
