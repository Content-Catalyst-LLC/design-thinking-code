# Data Dictionary

## `institutional_design_options_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `option` | string | Institutional design option. |
| `option_type` | string | Option category. |
| `desirability` | numeric | 1-10 stakeholder desirability. |
| `authority` | numeric | 1-10 authority to implement or approve the option. |
| `capability` | numeric | 1-10 organizational capability. |
| `funding` | numeric | 1-10 funding readiness. |
| `policy_fit` | numeric | 1-10 fit with policy or legal constraints. |
| `governance_strength` | numeric | 1-10 governance and decision-rights strength. |
| `trust_gain` | numeric | 1-10 expected trust or legitimacy gain. |
| `burden_reduction` | numeric | 1-10 burden-reduction potential. |
| `coordination_complexity` | numeric | 1-10 coordination difficulty. |
| `implementation_risk` | numeric | 1-10 implementation risk. |
| `data_readiness` | numeric | 1-10 data-system readiness. |
| `frontline_fit` | numeric | 1-10 fit with frontline work. |
| `maintenance_capacity` | numeric | 1-10 capacity to sustain the design. |
| `equity_priority` | numeric | 1-10 equity/public fairness priority. |
| `public_value` | numeric | 1-10 public or institutional mission value. |

## `stakeholder_burden_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `stakeholder_group` | string | Stakeholder or affected group. |
| `stakeholder_type` | string | Stakeholder category. |
| `time_burden` | numeric | 1-10 time burden. |
| `cognitive_burden` | numeric | 1-10 cognitive burden. |
| `emotional_burden` | numeric | 1-10 emotional burden. |
| `documentation_burden` | numeric | 1-10 documentation burden. |
| `uncertainty_burden` | numeric | 1-10 uncertainty burden. |
| `coordination_burden` | numeric | 1-10 coordination burden. |
| `accessibility_need` | numeric | 0-1 accessibility need. |
| `trust_gap` | numeric | 1-10 trust gap. |
| `affectedness` | numeric | 0-1 degree to which the group is affected. |
| `voice` | numeric | 1-10 voice in the institution. |
| `influence` | numeric | 1-10 influence over decisions. |
| `repair_access` | numeric | 1-10 access to correction, escalation, or repair. |
