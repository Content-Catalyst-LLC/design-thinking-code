# Data Dictionary

## `prototype_portfolio_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `prototype` | string | Candidate prototype name. |
| `prototype_type` | string | Prototype category such as service blueprint, digital mockup, pilot, or simulation. |
| `fidelity_level` | string | Low, mid, or high fidelity. |
| `learning_gain` | numeric | Score from 1 to 10 representing expected learning value. |
| `feasibility_signal` | numeric | Score from 1 to 10 representing feasibility evidence. |
| `user_response` | numeric | Score from 1 to 10 representing stakeholder response value. |
| `equity_value` | numeric | Score from 1 to 10 representing access, burden, and inclusion value. |
| `implementation_relevance` | numeric | Score from 1 to 10 representing relevance to implementation decisions. |
| `ethical_risk` | numeric | Score from 1 to 10 representing ethical risk. |
| `operational_risk` | numeric | Score from 1 to 10 representing operational risk. |
| `technical_risk` | numeric | Score from 1 to 10 representing technical risk. |
| `scaling_risk` | numeric | Score from 1 to 10 representing scaling risk. |
| `evidence_quality` | numeric | Score from 0 to 1 representing confidence in available evidence. |
| `prototype_testability` | numeric | Score from 0 to 1 representing how easy the prototype is to test. |
| `stakeholder_coverage` | numeric | Score from 0 to 1 representing coverage of relevant stakeholder groups. |

## `prototype_scenario_weights.csv`

| Column | Type | Description |
|---|---:|---|
| `scenario` | string | Name of prototyping-priority scenario. |
| `learning_gain` | numeric | Weight applied to learning gain. |
| `feasibility_signal` | numeric | Weight applied to feasibility signal. |
| `user_response` | numeric | Weight applied to user response. |
| `equity_value` | numeric | Weight applied to equity value. |
| `implementation_relevance` | numeric | Weight applied to implementation relevance. |
| `composite_risk` | numeric | Weight applied as penalty for composite risk. |

## `prototype_test_rounds_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `prototype` | string | Prototype tested. |
| `round` | integer | Iteration round. |
| `usability` | numeric | Usability score. |
| `comprehension` | numeric | Comprehension score. |
| `trust` | numeric | Trust score. |
| `unresolved_friction` | numeric | Remaining friction score. |
| `task_success_rate` | numeric | Task completion proportion. |
| `mean_time_minutes` | numeric | Mean completion time. |
| `critical_issue_count` | integer | Number of critical issues observed. |
| `participant_count` | integer | Number of participants in the round. |
