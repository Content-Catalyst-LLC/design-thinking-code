# Data Dictionary

## `evaluation_portfolio_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `intervention` | string | Design intervention being evaluated. |
| `intervention_type` | string | Intervention category such as service system, workflow, content prototype, partnership model, or governance system. |
| `evaluation_stage` | string | Evaluation stage such as early evaluation, pilot, phased rollout, or post-launch. |
| `outcome_improvement` | numeric | Score from 1 to 10 representing improvement in the intended outcome. |
| `burden_reduction` | numeric | Score from 1 to 10 representing reduction in user, staff, or intermediary burden. |
| `equity_performance` | numeric | Score from 1 to 10 representing equity-sensitive performance. |
| `trust_improvement` | numeric | Score from 1 to 10 representing trust, confidence, legitimacy, or perceived fairness. |
| `durability` | numeric | Score from 1 to 10 representing durability over time. |
| `operational_cost` | numeric | Score from 1 to 10 representing implementation or operational cost burden. |
| `residual_risk` | numeric | Score from 1 to 10 representing remaining risk or uncertainty. |
| `evidence_quality` | numeric | Score from 0 to 1 representing evidence quality. |
| `stakeholder_coverage` | numeric | Score from 0 to 1 representing stakeholder coverage. |
| `method_triangulation` | numeric | Score from 0 to 1 representing triangulation across evidence sources. |
| `uncertainty` | numeric | Score from 0 to 1 representing residual uncertainty. |
| `baseline_quality` | numeric | Baseline condition score from 1 to 10. |
| `current_quality` | numeric | Current condition score from 1 to 10. |

## `outcome_timeseries_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `intervention` | string | Intervention name. |
| `period` | integer | Evaluation period. |
| `outcome_score` | numeric | Outcome score in the period. |
| `burden_score` | numeric | Burden score in the period. Lower is better. |
| `equity_gap` | numeric | Difference or gap across relevant groups. Lower is better. |
| `trust_score` | numeric | Trust or legitimacy score. |
| `reliability_score` | numeric | Reliability proportion. |
| `staff_burden` | numeric | Staff burden score. Lower is better. |
| `support_ticket_rate` | numeric | Support tickets per normalized usage unit. |
| `complaint_rate` | numeric | Complaints per normalized usage unit. |
| `users_reached` | integer | Users reached by the period. |
