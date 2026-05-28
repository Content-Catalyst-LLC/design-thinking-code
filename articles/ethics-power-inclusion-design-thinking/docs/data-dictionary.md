# Data Dictionary

## `stakeholder_groups_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `group` | string | Stakeholder or affected group. |
| `stakeholder_type` | string | Stakeholder category. |
| `access` | numeric | 1-10 access score. |
| `voice` | numeric | 1-10 ability to influence or speak safely. |
| `safety` | numeric | 1-10 psychological, social, or procedural safety. |
| `compensation` | numeric | 1-10 compensation and reciprocity quality. |
| `representation` | numeric | 1-10 representation in research and decision evidence. |
| `accountability` | numeric | 1-10 ability to receive response, correction, or repair. |
| `time_burden` | numeric | 1-10 time burden. |
| `cognitive_burden` | numeric | 1-10 cognitive burden. |
| `emotional_burden` | numeric | 1-10 emotional burden. |
| `documentation_burden` | numeric | 1-10 documentation burden. |
| `uncertainty_burden` | numeric | 1-10 uncertainty burden. |
| `coordination_burden` | numeric | 1-10 coordination burden. |
| `affectedness` | numeric | 0-1 degree to which group is affected. |
| `trust_level` | numeric | 1-10 institutional trust level. |
| `accessibility_need` | numeric | 0-1 relative need for access accommodations. |

## `ethical_design_decisions_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `design_decision` | string | Design decision under review. |
| `decision_type` | string | Category of decision. |
| `harm_severity` | numeric | 0-1 severity of possible harm. |
| `probability` | numeric | 0-1 probability of harm. |
| `exposure` | numeric | 0-1 population exposure. |
| `detectability` | numeric | 0-1 likelihood that harm will be detected. |
| `accountability` | numeric | 0-1 accountability strength. |
| `inclusion_strength` | numeric | 0-1 inclusion strength. |
| `public_value` | numeric | 0-1 public or stakeholder value. |
| `repairability` | numeric | 0-1 ease of repair. |
| `privacy_sensitivity` | numeric | 0-1 privacy sensitivity. |
| `autonomy_risk` | numeric | 0-1 autonomy risk. |
| `manipulation_risk` | numeric | 0-1 manipulation risk. |
