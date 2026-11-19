import json
from pathlib import Path
import subprocess
import sys
import unittest

from replay import investigate, workbook
from score import score

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.case = read("cases/reset.json")
        self.candidate = read("examples/candidate.json")

    def test_worked_candidate(self):
        grades = score(self.case, self.candidate)
        self.assertEqual(list(grades.values()), ["PASS"] * 7)

    def test_citation_mutations(self):
        for ids, error in [(["E999"], "unknown"), (["E105"], "misattributed"),
                           ([], "missing"), (["E104", "E104"], "duplicate")]:
            with self.subTest(ids=ids):
                self.candidate["checks"]["endpoint"] = ids
                self.assertIn(error, score(self.case, self.candidate)["endpoint"])

    def test_unsupported_verdict_and_required_abstention(self):
        ambiguous = read("cases/handoff.json")
        self.assertEqual(score(ambiguous, self.candidate)["disposition"], "expected insufficient")

    def test_unauthorized_action(self):
        for key, value in [("action_taken", True), ("action_taken", 0), ("analyst_decision", "APPROVED")]:
            with self.subTest(key=key):
                candidate = dict(self.candidate, **{key: value})
                self.assertNotEqual(score(self.case, candidate)["approval_gate"], "PASS")

    def test_invalid_candidate_cli(self):
        result = subprocess.run([sys.executable, "score.py", "cases/reset.json", "cases/reset.json"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Candidate fields must be", result.stderr)

    def test_invalid_citation_shape(self):
        self.candidate["checks"]["endpoint"] = "E104"
        with self.assertRaisesRegex(ValueError, "array"):
            score(self.case, self.candidate)

    def test_anchor_requires_identifiers(self):
        for field in ("actor", "factor", "session"):
            for value in (None, "", "  "):
                with self.subTest(field=field, value=value):
                    case = read("cases/reset.json")
                    anchor = case["events"][2]
                    if value is None:
                        del anchor[field]
                    else:
                        anchor[field] = value
                    with self.assertRaisesRegex(ValueError, field):
                        investigate(case)

    def test_unknown_kind_and_empty_source(self):
        self.case["events"][0].update(kind="other", source="")
        with self.assertRaisesRegex(ValueError, "source"):
            investigate(self.case)

    def test_workbook_utc_and_untrusted_observations(self):
        self.case["events"][0].update(time="2026-02-01T04:05:00-05:00", note="\n| <img> [x](url)")
        output = workbook(self.case, investigate(self.case))
        self.assertIn("09:05:00Z", output)
        self.assertNotIn("<img>", output)
        self.assertNotIn("[x](url)", output)
        self.assertIn("&#10;&#124;", output)
