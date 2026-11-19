# Investigation workbook · DEMO-1

Synthetic training evidence.

Detection **ID-07** · sign-in anchor **E103**

Assessment **corroborated**

## Evidence checks

| Check | Result | Evidence IDs |
|---|---|---|
| Reset then matching factor enrollment then sign-in within 30 minutes | Observed | E101, E102, E103 |
| Endpoint remote access linked to the same session | Observed | E104 |
| Verified callback denies the session | Observed | E105 |
| Verified callback confirms the session | Unsubstantiated | — |
| Previously approved change covers the factor and session | Unsubstantiated | — |

## Event record

| ID | UTC time | Source | Observation |
|---|---|---|---|
| E101 | 2026-02-01T09:05:00Z | helpdesk | actor=user-ash, kind=reset |
| E102 | 2026-02-01T09:08:00Z | identity | actor=user-ash, factor=F1, kind=enrollment |
| E103 | 2026-02-01T09:10:00Z | identity | actor=user-ash, factor=F1, kind=signin, session=S1 |
| E104 | 2026-02-01T09:12:00Z | endpoint | actor=user-ash, kind=remote&#95;access, session=S1 |
| E105 | 2026-02-01T09:20:00Z | callback | actor=user-ash, kind=denial, session=S1, verified=True |

## Analyst handoff

Escalate for analyst review of session containment.

**Analyst decision: PENDING.** No action has been taken.
