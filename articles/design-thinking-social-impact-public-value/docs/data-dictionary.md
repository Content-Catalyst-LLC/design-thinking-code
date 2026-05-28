# Data Dictionary

## `social_impact_interventions_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `intervention` | string | Social impact intervention or design option. |
| `intervention_type` | string | Intervention category. |
| `access` | numeric | 1-10 expected access contribution. |
| `equity` | numeric | 1-10 equity contribution. |
| `dignity` | numeric | 1-10 dignity/respect contribution. |
| `legitimacy` | numeric | 1-10 public legitimacy contribution. |
| `accountability` | numeric | 1-10 accountability and answerability contribution. |
| `outcome_strength` | numeric | 1-10 expected outcome strength. |
| `sustainability` | numeric | 1-10 sustainability and maintainability. |
| `learning_capacity` | numeric | 1-10 ability to support public learning. |
| `feasibility` | numeric | 1-10 implementation feasibility. |
| `governance_strength` | numeric | 1-10 governance readiness. |
| `implementation_risk` | numeric | 1-10 implementation risk. |
| `burden_risk` | numeric | 1-10 risk of burden shifting or harm. |
| `participation_quality` | numeric | 1-10 participation quality. |
| `community_defined_value` | numeric | 1-10 alignment with community-defined value. |
| `repair_capacity` | numeric | 1-10 ability to repair errors or harms. |
| `stewardship_capacity` | numeric | 1-10 long-term stewardship capacity. |

## `stakeholder_burden_public_value_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `stakeholder_group` | string | Stakeholder or affected group. |
| `stakeholder_type` | string | Stakeholder category. |
| `baseline_*_burden` | numeric | Baseline burden measures before intervention. |
| `post_*_burden` | numeric | Expected or measured burden after intervention. |
| `affectedness` | numeric | 0-1 degree to which group is affected. |
| `voice` | numeric | 1-10 group voice in the process. |
| `influence` | numeric | 1-10 influence over decisions. |
| `repair_access` | numeric | 1-10 access to correction or repair. |
| `trust_gap` | numeric | 1-10 trust gap. |
| `accessibility_need` | numeric | 0-1 accessibility need. |
