# Data Dictionary

## `strategic_options_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `option` | string | Strategic option under review. |
| `option_type` | string | Portfolio category or strategic bet type. |
| `strategic_hypothesis` | string | Main hypothesis behind the option. |
| `desirability` | numeric | 1-10 evidence of human or stakeholder desirability. |
| `feasibility` | numeric | 1-10 technical/operational feasibility. |
| `viability` | numeric | 1-10 economic, resource, or institutional viability. |
| `strategic_alignment` | numeric | 1-10 alignment with strategic direction. |
| `ethical_quality` | numeric | 1-10 ethical quality, dignity, fairness, and accountability. |
| `learning_value` | numeric | 1-10 value of the option for strategic learning. |
| `implementation_effort` | numeric | 1-10 effort or cost of implementation. |
| `strategic_risk` | numeric | 1-10 strategic risk. |
| `capability_gap` | numeric | 1-10 gap between required and current capability. |
| `evidence_strength` | numeric | 0-1 evidence strength. |
| `time_to_learn` | numeric | 1-10 time or delay before meaningful evidence is available. |
| `public_value` | numeric | 1-10 expected public, civic, social, or institutional value. |

## `strategic_assumptions_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `option` | string | Associated strategic option. |
| `assumption` | string | Critical assumption. |
| `assumption_type` | string | Assumption category. |
| `importance` | numeric | 0-1 importance of assumption. |
| `confidence` | numeric | 0-1 current confidence. |
| `test_cost` | numeric | 0-1 cost or difficulty of testing. |
| `time_to_test` | numeric | Relative time to test. |
| `ethical_sensitivity` | numeric | 0-1 ethical or public-value sensitivity. |
| `decision_threshold` | numeric | Confidence threshold needed before scale. |
| `current_evidence` | string | Evidence currently supporting the assumption. |
