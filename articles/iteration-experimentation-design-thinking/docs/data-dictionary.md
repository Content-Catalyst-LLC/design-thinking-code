# Data Dictionary

## `data/raw/experiments_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `experiment` | string | Candidate design experiment. |
| `learning_gain` | numeric | Score from 1 to 10 representing expected learning value. |
| `update_flexibility` | numeric | Score from 1 to 10 representing reversibility and ease of revision. |
| `expected_improvement` | numeric | Score from 1 to 10 representing plausible downstream improvement. |
| `residual_risk` | numeric | Score from 1 to 10 representing unresolved risk. Higher risk lowers experiment value. |
| `ethical_risk` | numeric | Score from 1 to 10 representing ethical or human-subject risk. |
| `operational_risk` | numeric | Score from 1 to 10 representing workflow, staff, process, or operational risk. |
| `interpretive_risk` | numeric | Score from 1 to 10 representing risk of misinterpreting ambiguous evidence. |
| `scaling_risk` | numeric | Score from 1 to 10 representing risk that a successful test may not generalize at scale. |
| `evidence_quality` | numeric | Optional score from 0 to 1 representing confidence in supporting evidence. |
| `team_confidence` | numeric | Optional score from 0 to 1 representing confidence in team assumptions. |
| `implementation_complexity` | numeric | Optional score from 1 to 10 representing complexity of execution. |

## `data/raw/experiment_scenario_weights.csv`

| Column | Type | Description |
|---|---:|---|
| `scenario` | string | Name of the strategic priority scenario. |
| `learning_gain` | numeric | Weight applied to learning gain. |
| `update_flexibility` | numeric | Weight applied to update flexibility. |
| `expected_improvement` | numeric | Weight applied to expected improvement. |
| `residual_risk` | numeric | Weight applied as a penalty for residual risk. |

Scenario weights must sum to 1.0.

## `data/raw/experiment_ethics_review_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `experiment` | string | Candidate design experiment. |
| `requires_informed_consent` | numeric | Score from 0 to 1 indicating consent sensitivity. |
| `participant_burden` | numeric | Score from 0 to 1 representing participant time, effort, stress, or access burden. |
| `privacy_sensitivity` | numeric | Score from 0 to 1 representing data or privacy sensitivity. |
| `power_asymmetry` | numeric | Score from 0 to 1 representing asymmetry between the testing institution and participants. |
| `review_priority` | numeric | Initial review-priority score from 0 to 1. |
| `notes` | string | Interpretation notes. |
