# Data Dictionary

## `codesign_activities_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `activity` | string | Participatory design activity. |
| `activity_type` | string | Activity category such as problem framing, journey mapping, field research, prototype workshop, synthesis review, AI governance, implementation governance, or feedback loop. |
| `design_stage` | string | Stage of the design process. |
| `representation` | numeric | 1-10 score for participant representation. |
| `accessibility` | numeric | 1-10 score for accessibility of the participation process. |
| `participant_influence` | numeric | 1-10 score for participant influence over design decisions. |
| `trust_quality` | numeric | 1-10 score for trust, safety, and credibility. |
| `evidence_quality` | numeric | 1-10 score for quality of participatory evidence. |
| `implementation_accountability` | numeric | 1-10 score for implementation follow-through and ownership. |
| `decision_impact` | numeric | 1-10 score for how much participation changes decisions. |
| `ethical_risk` | numeric | 1-10 score for ethical, tokenism, extraction, or legitimacy risk. |
| `affectedness_weight` | numeric | 0-1 weight for how affected the participating group is. |
| `compensation_quality` | numeric | 1-10 score for fair compensation or support. |
| `feedback_loop_quality` | numeric | 1-10 score for reporting back and accountability. |
| `tokenism_risk` | numeric | 1-10 score for symbolic participation risk. |

## `participant_groups_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `group` | string | Participant or affected group. |
| `stakeholder_type` | string | Type of stakeholder group. |
| `affectedness` | numeric | 0-1 estimate of how strongly the group is affected. |
| `presence` | numeric | 0-1 estimate of whether the group is meaningfully present. |
| `framing_influence` | numeric | 0-1 influence over problem framing. |
| `synthesis_influence` | numeric | 0-1 influence over synthesis. |
| `concept_influence` | numeric | 0-1 influence over concepts. |
| `testing_influence` | numeric | 0-1 influence over testing. |
| `implementation_influence` | numeric | 0-1 influence over implementation. |
| `governance_influence` | numeric | 0-1 influence over governance. |
| `access_support` | numeric | 0-1 access support score. |
| `trust_score` | numeric | 0-1 trust and safety score. |
| `compensation_support` | numeric | 0-1 compensation support score. |
| `language_access` | numeric | 0-1 language access score. |
| `disability_access` | numeric | 0-1 disability access score. |
