# Data Dictionary

## `public_policy_pilots_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `pilot` | string | Candidate public-policy pilot concept. |
| `policy_domain` | string | Policy area such as social protection, public health, licensing, education, housing, disability support, climate adaptation, or economic development. |
| `pilot_type` | string | Intervention type such as service redesign, outreach service, digital service, navigation service, grant access, compliance support, automatic enrollment, or communication design. |
| `accessibility` | numeric | Score from 1 to 10 representing public legibility, usability, and access. |
| `feasibility` | numeric | Score from 1 to 10 representing implementation feasibility. |
| `legitimacy` | numeric | Score from 1 to 10 representing trust, acceptability, procedural fairness, and public justification. |
| `equity` | numeric | Score from 1 to 10 representing equity adequacy and differential burden awareness. |
| `burden_reduction` | numeric | Score from 1 to 10 representing likely administrative-burden reduction. |
| `durability` | numeric | Score from 1 to 10 representing durability under real institutional conditions. |
| `risk` | numeric | Score from 1 to 10 representing implementation and unintended-consequence risk. |
| `evidence_quality` | numeric | Score from 0 to 1 representing quality of available evidence. |
| `stakeholder_coverage` | numeric | Score from 0 to 1 representing coverage of relevant stakeholder groups. |
| `legal_complexity` | numeric | Score from 1 to 10 representing legal and procedural complexity. |
| `implementation_complexity` | numeric | Score from 1 to 10 representing operational complexity. |
| `participation_quality` | numeric | Score from 0 to 1 representing quality of affected-stakeholder participation. |

## `policy_learning_pathways_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `pilot` | string | Pilot name. |
| `period` | integer | Policy learning period. |
| `uptake_rate` | numeric | Uptake rate in the period. |
| `citizen_friction` | numeric | Citizen friction score. Lower is better. |
| `implementation_error` | numeric | Implementation error rate. Lower is better. |
| `trust_score` | numeric | Public trust score. |
| `equity_score` | numeric | Equity performance score. |
| `appeal_access` | numeric | Appeal access score from 0 to 1. |
| `staff_workload` | numeric | Staff workload score. Lower is better. |
| `case_resolution_time` | numeric | Case resolution time. Lower is better. |
