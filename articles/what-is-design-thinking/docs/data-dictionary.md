# Data Dictionary

## `data/raw/design_pathways_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `pathway` | string | Name of the design pathway or intervention option. |
| `human_relevance` | numeric | Score from 1 to 10 representing stakeholder relevance, usability, accessibility, and fit with lived experience. |
| `feasibility` | numeric | Score from 1 to 10 representing technical, operational, organizational, legal, financial, and implementation feasibility. |
| `learning_value` | numeric | Score from 1 to 10 representing how much the pathway can teach the team through prototyping, testing, or early implementation. |
| `residual_risk` | numeric | Score from 1 to 10 representing unresolved risk. Higher risk lowers the design value score. |
| `stakeholder_confidence` | numeric | Optional score from 0 to 1 representing confidence in stakeholder evidence. |
| `evidence_quality` | numeric | Optional score from 0 to 1 representing confidence in the quality of supporting evidence. |
| `implementation_complexity` | numeric | Optional score from 1 to 10 representing complexity of implementation. |

## `data/raw/scenario_weights.csv`

| Column | Type | Description |
|---|---:|---|
| `scenario` | string | Name of the strategic priority scenario. |
| `human_relevance` | numeric | Weight applied to human relevance. |
| `feasibility` | numeric | Weight applied to feasibility. |
| `learning_value` | numeric | Weight applied to learning value. |
| `residual_risk` | numeric | Weight applied as a penalty for residual risk. |

Scenario weights must sum to 1.0.
