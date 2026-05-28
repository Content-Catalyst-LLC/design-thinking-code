# Data Dictionary

## `system_intervention_portfolio_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `intervention` | string | Candidate design-system intervention. |
| `intervention_type` | string | Intervention category such as service redesign, policy rule, information flow, governance change, or support infrastructure. |
| `leverage_level` | string | Leverage category such as workflow, information flow, feedback loop, rule, governance, infrastructure, or paradigm. |
| `human_value` | numeric | Score from 1 to 10 representing stakeholder experience, usability, trust, access, and burden reduction. |
| `system_leverage` | numeric | Score from 1 to 10 representing likely influence on system structure or feedback. |
| `feasibility` | numeric | Score from 1 to 10 representing implementation feasibility. |
| `equity_sensitivity` | numeric | Score from 1 to 10 representing attention to differential access and burden. |
| `durability` | numeric | Score from 1 to 10 representing long-term sustainability of the intervention. |
| `risk` | numeric | Score from 1 to 10 representing implementation or unintended-consequence risk. |
| `evidence_quality` | numeric | Score from 0 to 1 representing quality of available evidence. |
| `stakeholder_coverage` | numeric | Score from 0 to 1 representing coverage of relevant stakeholder groups. |
| `context_complexity` | numeric | Score from 1 to 10 representing complexity of implementation context. |
| `delay_sensitivity` | numeric | Score from 0 to 1 representing sensitivity to delayed feedback and lagged consequences. |
| `burden_shift_risk` | numeric | Score from 1 to 10 representing risk that burden shifts elsewhere in the system. |

## `feedback_dynamics_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `intervention` | string | Intervention name. |
| `period` | integer | Feedback review period. |
| `intervention_intensity` | numeric | Relative intensity of implementation. |
| `visible_performance` | numeric | Visible system performance score. |
| `adaptation_pressure` | numeric | Pressure from system adaptation or counter-response. |
| `system_burden` | numeric | System burden score. Lower is better. |
| `equity_gap` | numeric | Differential outcome or access gap. Lower is better. |
| `trust_score` | numeric | Stakeholder trust score. |
| `queue_pressure` | numeric | Queue, backlog, or capacity pressure. Lower is better. |
| `implementation_drift` | numeric | Degree of drift from intended implementation. Lower is better. |
