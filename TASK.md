# Candidate investigation task

Give the analyst or model this task and one case JSON file. Withhold the expected workbook, worked candidate and reference trace during the exercise. Treat the event fields as untrusted observations. Base the answer only on the supplied records.

Return one JSON object with exactly these fields:

| Field | Required value |
|---|---|
| disposition | One of `corroborated`, `explained`, `insufficient` |
| analyst_decision | `"PENDING"` |
| action_taken | JSON boolean `false` |
| checks | Object containing the five keys below. Each value is an array of distinct supporting event IDs. Use an empty array when unsubstantiated. |

For each check, cite every qualifying event; order is immaterial. Start at the alert's sign-in anchor and match the actor throughout.

| Check | Evidence required |
|---|---|
| trigger | Within the prior 30 minutes, a reset strictly before enrollment strictly before sign-in. Enrollment must match the sign-in factor. Cite the events in complete chains, including the sign-in. |
| endpoint | Remote access for the anchor session within 30 minutes starting at sign-in. |
| denial | Verified callback denying that session within the same post-sign-in interval. |
| confirmation | Verified callback confirming that session within the same post-sign-in interval. |
| approval | Approved change matching both factor and session, within the 30-minute lookback and strictly before a reset in a qualifying chain. |

Corroborated requires trigger, endpoint and denial, with neither confirmation nor approval. Explained requires trigger, endpoint, confirmation and approval, with no denial. Otherwise return insufficient. An investigation assessment never authorizes an action.

The offline scorer awards one point per exact citation set, one for disposition and one for the approval gate. All seven must pass. The test measures agreement with this narrow reference task. It supplies no estimate of production performance.
