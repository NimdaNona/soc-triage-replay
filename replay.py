"""Offline, deterministic investigation of a single synthetic sign-in alert."""
import argparse
import json
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

RULE = "ID-07"
WINDOW = timedelta(minutes=30)
SOURCES = {"reset": "helpdesk", "enrollment": "identity", "signin": "identity",
           "remote_access": "endpoint", "denial": "callback", "confirmation": "callback",
           "change": "change_control"}
ACTIONS = {"corroborated": "Escalate for analyst review of session containment.",
           "explained": "Submit the documented change for analyst review and closure.",
           "insufficient": "Hold open. Resolve missing or contradictory evidence."}


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.utcoffset() is None:
        raise ValueError("Timezone required")
    return result


def investigate(case):
    alert = case["alert"]
    events = case["events"]
    index = {e["id"]: e for e in events}
    if len(index) != len(events):
        raise ValueError("Duplicate evidence ID")
    if alert["rule"] != RULE:
        raise ValueError("Unsupported detection")
    if any(e["kind"] not in SOURCES or e["source"] != SOURCES[e["kind"]] for e in events):
        raise ValueError("Unexpected source for event kind")
    anchor = index.get(alert["event"])
    if not anchor or anchor["kind"] != "signin":
        raise ValueError("Alert needs a sign-in anchor")
    for field in ("actor", "session", "factor"):
        value = anchor.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Sign-in anchor needs a nonblank {field}")
    at = timestamp(anchor["time"])
    trace = []

    def check(label, matches):
        ids = sorted({e["id"] for e in matches})
        trace.append({"check": label, "matched": bool(ids), "evidence": ids})
        return bool(ids)

    related = [e for e in events if e["actor"] == anchor["actor"]]
    def prior(kind):
        return [e for e in related if e["kind"] == kind
                and at - WINDOW <= timestamp(e["time"]) <= at]
    pairs = [(r, n) for r in prior("reset") for n in prior("enrollment")
             if timestamp(r["time"]) < timestamp(n["time"]) < at
             and n.get("factor") == anchor["factor"]]
    fired = check("Reset then matching factor enrollment then sign-in within 30 minutes",
                  [anchor, *(e for pair in pairs for e in pair)] if pairs else [])
    following = [e for e in related if at <= timestamp(e["time"]) <= at + WINDOW
                 and e.get("session") == anchor["session"]]
    remote = check("Endpoint remote access linked to the same session",
                   [e for e in following if e["kind"] == "remote_access"])
    denied = check("Verified callback denies the session",
                   [e for e in following if e["kind"] == "denial" and e.get("verified") is True])
    confirmed = check("Verified callback confirms the session",
                      [e for e in following if e["kind"] == "confirmation" and e.get("verified") is True])
    approved = check("Previously approved change covers the factor and session",
                     [e for e in prior("change") if e.get("approved") is True
                      and e.get("session") == anchor["session"] and e.get("factor") == anchor["factor"]
                      and any(timestamp(e["time"]) < timestamp(r["time"]) for r, _ in pairs)])
    verdict = "insufficient"
    if fired and remote and denied and not (confirmed or approved):
        verdict = "corroborated"
    if fired and remote and confirmed and approved and not denied:
        verdict = "explained"
    return {"alert": alert["id"], "rule": RULE, "anchor": anchor["id"], "trigger_reproduced": fired,
            "disposition": verdict, "trace": trace, "recommendation": ACTIONS[verdict],
            "analyst_decision": "PENDING"}


def cell(value):
    # Entity-encode punctuation before Markdown parsing. A value stays in one cell
    # even when it contains markup, an HTML tag, a table pipe, or a newline.
    return "".join(f"&#{ord(c)};" if (c in string.punctuation and c != "-") or not c.isprintable() else c
                   for c in str(value))


def workbook(case, result):
    lines = [f"# Investigation workbook · {cell(result['alert'])}", "", "Synthetic training evidence.", "",
             f"Detection **{RULE}** · sign-in anchor **{cell(result['anchor'])}**",
             f"\nAssessment **{result['disposition']}**", "", "## Evidence checks", "",
             "| Check | Result | Evidence IDs |", "|---|---|---|"]
    for row in result["trace"]:
        lines.append(f"| {row['check']} | {'Observed' if row['matched'] else 'Unsubstantiated'} | "
                     + (", ".join(map(cell, row["evidence"])) or "—") + " |")
    lines.extend(["", "## Event record", "", "| ID | UTC time | Source | Observation |",
                  "|---|---|---|---|"])
    for e in sorted(case["events"], key=lambda event: timestamp(event["time"])):
        observation = ", ".join(f"{cell(k)}={cell(v)}" for k, v in sorted(e.items())
                                if k not in {"id", "source", "time"})
        utc = timestamp(e["time"]).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        lines.append(f"| {cell(e['id'])} | {utc} | {cell(e['source'])} | {observation} |")
    lines.extend(["", "## Analyst handoff", "", result["recommendation"], "",
                  "**Analyst decision: PENDING.** No action has been taken.", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", nargs="?", type=Path,
                        default=Path(__file__).parent / "cases" / "reset.json")
    parser.add_argument("--json", action="store_true", help="print the machine-readable trace")
    args = parser.parse_args()
    data = json.loads(args.case.read_text(encoding="utf-8"))
    result = investigate(data)
    print(json.dumps(result, indent=2) if args.json else workbook(data, result), end="\n" if args.json else "")
