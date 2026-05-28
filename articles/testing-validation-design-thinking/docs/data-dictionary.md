# Data Dictionary

## `validation_concepts_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `concept` | string | Tested design concept or prototype name. |
| `prototype_type` | string | Prototype category such as digital flow, form redesign, service pathway, or content prototype. |
| `fidelity_level` | string | Low, mid, or high fidelity. |
| `desirability` | numeric | Score from 1 to 10 representing stakeholder value, usefulness, or meaning. |
| `feasibility` | numeric | Score from 1 to 10 representing technical and operational feasibility. |
| `viability` | numeric | Score from 1 to 10 representing sustainability, governance, policy, cost, or maintenance fit. |
| `responsibility` | numeric | Score from 1 to 10 representing safety, ethics, privacy, equity, and accountability. |
| `friction` | numeric | Score from 1 to 10 representing observed friction or user burden. |
| `residual_risk` | numeric | Score from 1 to 10 representing unresolved risk or uncertainty. |
| `evidence_quality` | numeric | Score from 0 to 1 representing confidence in evidence quality. |
| `stakeholder_coverage` | numeric | Score from 0 to 1 representing coverage of relevant stakeholder groups. |
| `method_triangulation` | numeric | Score from 0 to 1 representing the strength of method triangulation. |
| `equity_signal` | numeric | Score from 1 to 10 representing equity evidence. |
| `accessibility_signal` | numeric | Score from 1 to 10 representing accessibility evidence. |
| `operational_signal` | numeric | Score from 1 to 10 representing operational evidence. |

## `validation_scenario_weights.csv`

| Column | Type | Description |
|---|---:|---|
| `scenario` | string | Name of validation-priority scenario. |
| `desirability` | numeric | Weight applied to desirability. |
| `feasibility` | numeric | Weight applied to feasibility. |
| `viability` | numeric | Weight applied to viability. |
| `responsibility` | numeric | Weight applied to responsibility. |
| `risk_penalty` | numeric | Weight applied as penalty for combined risk. |

## `testing_rounds_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `concept` | string | Tested concept. |
| `round` | integer | Testing round. |
| `adoption_likelihood` | numeric | Likelihood that participants would adopt or continue using the concept. |
| `comprehension` | numeric | Comprehension score. |
| `trust` | numeric | Trust score. |
| `observed_friction` | numeric | Observed friction score. |
| `task_success_rate` | numeric | Task completion proportion. |
| `error_rate` | numeric | Error proportion. |
| `mean_time_minutes` | numeric | Mean task completion time. |
| `critical_issue_count` | integer | Number of critical issues observed. |
| `participant_count` | integer | Number of participants in the testing round. |
