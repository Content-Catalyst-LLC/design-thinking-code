# Data Dictionary

## `data/raw/candidate_insights_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `insight` | string | Candidate insight statement. |
| `pattern_support` | numeric | Score from 1 to 10 representing evidentiary pattern support. |
| `explanatory_depth` | numeric | Score from 1 to 10 representing explanatory power. |
| `opportunity_value` | numeric | Score from 1 to 10 representing design opportunity value. |
| `interpretive_risk` | numeric | Score from 1 to 10 representing overall interpretive risk. Higher risk lowers insight value. |
| `sampling_risk` | numeric | Score from 1 to 10 representing sampling or coverage risk. |
| `confirmation_bias_risk` | numeric | Score from 1 to 10 representing risk that the insight confirms prior assumptions. |
| `evidence_thinness_risk` | numeric | Score from 1 to 10 representing weak or narrow evidence. |
| `solution_capture_risk` | numeric | Score from 1 to 10 representing risk that the insight is shaped by a favored solution. |
| `evidence_quality` | numeric | Optional score from 0 to 1 representing confidence in supporting evidence. |
| `stakeholder_diversity` | numeric | Optional score from 0 to 1 representing breadth of stakeholder perspective. |
| `prototype_testability` | numeric | Optional score from 0 to 1 representing ease of testing the insight through prototype work. |
| `implementation_relevance` | numeric | Optional score from 1 to 10 representing relevance to downstream implementation decisions. |

## `data/raw/insight_scenario_weights.csv`

| Column | Type | Description |
|---|---:|---|
| `scenario` | string | Name of the synthesis-priority scenario. |
| `pattern_support` | numeric | Weight applied to pattern support. |
| `explanatory_depth` | numeric | Weight applied to explanatory depth. |
| `opportunity_value` | numeric | Weight applied to opportunity value. |
| `interpretive_risk` | numeric | Weight applied as a penalty for interpretive risk. |

Scenario weights must sum to 1.0.

## `data/raw/insight_evidence_sources_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `insight` | string | Candidate insight statement. |
| `evidence_source_count` | integer | Number of evidence sources supporting the candidate insight. |
| `stakeholder_groups` | integer | Number of stakeholder groups represented in supporting evidence. |
| `method_count` | integer | Number of research methods contributing evidence. |
| `contradictory_cases` | integer | Number of contradictory or complicating cases identified. |
| `validation_priority` | numeric | Initial validation-priority score from 0 to 1. |
| `notes` | string | Interpretation notes. |
