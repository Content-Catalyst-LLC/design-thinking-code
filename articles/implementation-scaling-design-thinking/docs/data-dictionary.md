# Data Dictionary

## `implementation_portfolio_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `intervention` | string | Candidate intervention or deployment unit. |
| `intervention_type` | string | Intervention category such as workflow, playbook, protocol, tool, service, or monitoring system. |
| `implementation_stage` | string | Current deployment stage. |
| `adoption_readiness` | numeric | Score from 1 to 10 representing readiness for use and normalization. |
| `operational_fit` | numeric | Score from 1 to 10 representing workflow and operational fit. |
| `durability` | numeric | Score from 1 to 10 representing ability to persist over time. |
| `governance_readiness` | numeric | Score from 1 to 10 representing ownership, accountability, and decision-rights clarity. |
| `equity_readiness` | numeric | Score from 1 to 10 representing readiness across differential access and burden conditions. |
| `financial_sustainability` | numeric | Score from 1 to 10 representing budget, procurement, maintenance, and renewal capacity. |
| `operational_risk` | numeric | Score from 1 to 10 representing operational risk. |
| `governance_risk` | numeric | Score from 1 to 10 representing governance risk. |
| `technical_risk` | numeric | Score from 1 to 10 representing technical risk. |
| `equity_risk` | numeric | Score from 1 to 10 representing equity risk. |
| `financial_risk` | numeric | Score from 1 to 10 representing financial risk. |
| `evidence_quality` | numeric | Score from 0 to 1 representing evidence confidence. |
| `stakeholder_coverage` | numeric | Score from 0 to 1 representing stakeholder coverage. |
| `context_complexity` | numeric | Score from 1 to 10 representing contextual complexity for scale. |
| `scale_sensitivity` | numeric | Score from 0 to 1 representing sensitivity to contextual variation. |

## `rollout_stage_metrics_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `intervention` | string | Intervention being rolled out. |
| `stage` | integer | Rollout stage. |
| `adoption_rate` | numeric | Share of target users or sites adopting the intervention. |
| `staff_compliance` | numeric | Share of staff following the intended workflow. |
| `service_reliability` | numeric | Reliability rate. |
| `support_ticket_rate` | numeric | Support tickets per normalized usage unit. |
| `equity_gap` | numeric | Performance gap across relevant access or stakeholder groups. |
| `mean_resolution_time_hours` | numeric | Mean issue resolution time. |
| `user_trust` | numeric | Trust score. |
| `staff_burden` | numeric | Staff burden score. |
| `incident_count` | integer | Number of incidents in the stage. |
| `sites_live` | integer | Number of deployment sites. |
| `users_reached` | integer | Number of users reached. |
