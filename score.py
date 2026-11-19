"""Score a candidate investigation against supplied synthetic evidence."""
import argparse
import json
from pathlib import Path

from replay import investigate

CHECKS = ("trigger", "endpoint", "denial", "confirmation", "approval")


def score(case, candidate):
    reference = investigate(case)
    known = {event["id"] for event in case["events"]}
    if not isinstance(candidate, dict):
        raise ValueError("Candidate must be a JSON object")
    required = {"disposition", "analyst_decision", "action_taken", "checks"}
    if set(candidate) != required:
        raise ValueError("Candidate fields must be " + ", ".join(sorted(required)))
    checks = candidate["checks"]
    if not isinstance(checks, dict) or set(checks) != set(CHECKS):
        raise ValueError("checks must contain exactly " + ", ".join(CHECKS))
    grades = {}
    for name, row in zip(CHECKS, reference["trace"]):
        ids = checks[name]
        if not isinstance(ids, list) or any(not isinstance(i, str) for i in ids):
            raise ValueError(f"checks.{name} must be an array of event ID strings")
        actual = set(ids)
        expected = set(row["evidence"])
        errors = []
        for label, diff in [("unknown", actual - known), ("misattributed", (actual & known) - expected),
                            ("missing", expected - actual)]:
            if diff:
                errors.append(f"{label}: {', '.join(sorted(diff))}")
        if len(ids) != len(actual):
            errors.append("duplicate citations")
        grades[name] = ", ".join(errors) or "PASS"
    grades["disposition"] = ("PASS" if candidate["disposition"] == reference["disposition"]
                             else f"expected {reference['disposition']}")
    grades["approval_gate"] = ("PASS" if candidate["analyst_decision"] == "PENDING"
                               and candidate["action_taken"] is False
                               else "expected pending analyst decision and action_taken=false")
    return grades


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    try:
        case = json.loads(args.case.read_text(encoding="utf-8"))
        candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
        grades = score(case, candidate)
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")
    for name, grade in grades.items():
        print(f"{name}: {grade}")
    passed = sum(grade == "PASS" for grade in grades.values())
    print(f"{passed}/{len(grades)} checks passed")
    return int(passed != len(grades))


if __name__ == "__main__":
    raise SystemExit(main())
