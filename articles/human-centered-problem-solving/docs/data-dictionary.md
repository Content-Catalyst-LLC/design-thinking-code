# Data Dictionary

## `data/raw/human_centered_options_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `option` | string | Name of the design option or intervention. |
| `human_benefit` | numeric | Score from 1 to 10 representing improvement in lived experience, dignity, access, usefulness, or outcome. |
| `usability` | numeric | Score from 1 to 10 representing intelligibility, ease of use, accessibility, and fit with human cognition. |
| `stakeholder_fit` | numeric | Score from 1 to 10 representing fit across affected stakeholder groups. |
| `burden` | numeric | Score from 1 to 10 representing user cost or burden. Higher burden lowers the value score. |
| `learning_cost` | numeric | Score from 1 to 10 representing difficulty understanding what the system requires. |
| `compliance_cost` | numeric | Score from 1 to 10 representing effort required to comply with the process. |
| `psychological_cost` | numeric | Score from 1 to 10 representing fear, shame, stress, uncertainty, or emotional strain. |
| `access_cost` | numeric | Score from 1 to 10 representing barriers related to language, mobility, time, digital access, documentation, or support. |
| `evidence_quality` | numeric | Optional score from 0 to 1 representing confidence in the quality of supporting evidence. |
| `stakeholder_confidence` | numeric | Optional score from 0 to 1 representing confidence in stakeholder evidence. |
| `implementation_complexity` | numeric | Optional score from 1 to 10 representing complexity of implementation. |

## `data/raw/human_centered_scenario_weights.csv`

| Column | Type | Description |
|---|---:|---|
| `scenario` | string | Name of the strategic priority scenario. |
| `human_benefit` | numeric | Weight applied to human benefit. |
| `usability` | numeric | Weight applied to usability. |
| `stakeholder_fit` | numeric | Weight applied to stakeholder fit. |
| `burden` | numeric | Weight applied as a penalty for burden. |

Scenario weights must sum to 1.0.

## `data/raw/stakeholder_groups_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `stakeholder_group` | string | Name of the affected stakeholder group. |
| `visibility_to_institution` | numeric | Score from 0 to 1 representing how visible the group is to institutional decision-makers. |
| `power_to_influence_design` | numeric | Score from 0 to 1 representing the group’s ability to shape design decisions. |
| `burden_exposure` | numeric | Score from 0 to 1 representing exposure to the burden produced by the current system. |
| `access_risk` | numeric | Score from 0 to 1 representing access-related vulnerability. |
| `notes` | string | Interpretation notes. |
