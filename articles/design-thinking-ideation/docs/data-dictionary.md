# Data Dictionary

## `data/raw/idea_portfolio_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `idea` | string | Candidate idea or design concept. |
| `idea_cluster` | string | Idea family or conceptual cluster. |
| `desirability` | numeric | Score from 1 to 10 representing stakeholder desirability. |
| `feasibility` | numeric | Score from 1 to 10 representing practical feasibility. |
| `novelty` | numeric | Score from 1 to 10 representing originality or exploratory value. |
| `equity_value` | numeric | Score from 1 to 10 representing likely equity/access value. |
| `learning_value` | numeric | Score from 1 to 10 representing prototype or experiment learning value. |
| `residual_risk` | numeric | Score from 1 to 10 representing unresolved risk. |
| `ethical_risk` | numeric | Score from 1 to 10 representing ethical, dignity, consent, privacy, or agency risk. |
| `operational_risk` | numeric | Score from 1 to 10 representing workflow, staffing, or process risk. |
| `technical_risk` | numeric | Score from 1 to 10 representing build, integration, reliability, or security risk. |
| `scaling_risk` | numeric | Score from 1 to 10 representing risk that prototype value may not scale. |
| `evidence_quality` | numeric | Optional score from 0 to 1 representing confidence in evidence. |
| `prototype_testability` | numeric | Optional score from 0 to 1 representing ease of testing. |
| `implementation_relevance` | numeric | Optional score from 1 to 10 representing relevance to implementation decisions. |

## `data/raw/ideation_scenario_weights.csv`

| Column | Type | Description |
|---|---:|---|
| `scenario` | string | Name of the ideation-priority scenario. |
| `desirability` | numeric | Weight applied to desirability. |
| `feasibility` | numeric | Weight applied to feasibility. |
| `novelty` | numeric | Weight applied to novelty. |
| `equity_value` | numeric | Weight applied to equity value. |
| `learning_value` | numeric | Weight applied to learning value. |
| `composite_risk` | numeric | Weight applied as a penalty for composite risk. |

Scenario weights must sum to 1.0.

## `data/raw/idea_cluster_map_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `idea` | string | Candidate idea. |
| `idea_cluster` | string | Idea family or conceptual cluster. |
| `cluster_distance` | numeric | Approximate distinctiveness from cluster center. |
| `stakeholder_groups` | integer | Number of stakeholder groups represented in evidence. |
| `methods_supporting` | integer | Number of research methods supporting the idea. |
| `evidence_source_count` | integer | Number of evidence sources linked to the idea. |
| `notes` | string | Interpretation notes. |
