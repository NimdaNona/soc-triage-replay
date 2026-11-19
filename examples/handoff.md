# Investigation workbook · DEMO-3

Synthetic training evidence.

Detection **ID-07** · sign-in anchor **E303**

Assessment **insufficient**

## Evidence checks

| Check | Result | Evidence IDs |
|---|---|---|
| Reset then matching factor enrollment then sign-in within 30 minutes | Observed | E301, E302, E303 |
| Endpoint remote access linked to the same session | Unsubstantiated | — |
| Verified callback denies the session | Observed | E305 |
| Verified callback confirms the session | Observed | E306 |
| Previously approved change covers the factor and session | Unsubstantiated | — |

## Event record

| ID | UTC time | Source | Observation |
|---|---|---|---|
| E301 | 2026-02-03T09:05:00Z | helpdesk | actor=user-oak, kind=reset |
| E302 | 2026-02-03T09:08:00Z | identity | actor=user-oak, factor=F3, kind=enrollment |
| E303 | 2026-02-03T09:10:00Z | identity | actor=user-oak, factor=F3, kind=signin, session=S3 |
| E304 | 2026-02-03T09:12:00Z | endpoint | actor=user-oak, kind=remote&#95;access, session=S-other |
| E305 | 2026-02-03T09:20:00Z | callback | actor=user-oak, kind=denial, session=S3, verified=True |
| E306 | 2026-02-03T09:22:00Z | callback | actor=user-oak, kind=confirmation, session=S3, verified=True |

## Analyst handoff

Hold open. Resolve missing or contradictory evidence.

**Analyst decision: PENDING.** No action has been taken.
