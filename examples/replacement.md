# Investigation workbook · DEMO-2

Synthetic training evidence.

Detection **ID-07** · sign-in anchor **E204**

Assessment **explained**

## Evidence checks

| Check | Result | Evidence IDs |
|---|---|---|
| Reset then matching factor enrollment then sign-in within 30 minutes | Observed | E202, E203, E204 |
| Endpoint remote access linked to the same session | Observed | E205 |
| Verified callback denies the session | Unsubstantiated | — |
| Verified callback confirms the session | Observed | E206 |
| Previously approved change covers the factor and session | Observed | E201 |

## Event record

| ID | UTC time | Source | Observation |
|---|---|---|---|
| E201 | 2026-02-02T09:01:00Z | change_control | actor=user-elm, approved=True, factor=F2, kind=change, session=S2 |
| E202 | 2026-02-02T09:05:00Z | helpdesk | actor=user-elm, kind=reset |
| E203 | 2026-02-02T09:08:00Z | identity | actor=user-elm, factor=F2, kind=enrollment |
| E204 | 2026-02-02T09:10:00Z | identity | actor=user-elm, factor=F2, kind=signin, session=S2 |
| E205 | 2026-02-02T09:12:00Z | endpoint | actor=user-elm, kind=remote_access, session=S2 |
| E206 | 2026-02-02T09:20:00Z | callback | actor=user-elm, kind=confirmation, session=S2, verified=True |

## Analyst handoff

Submit the documented change for analyst review and closure.

**Analyst decision: PENDING.** No action has been taken.
