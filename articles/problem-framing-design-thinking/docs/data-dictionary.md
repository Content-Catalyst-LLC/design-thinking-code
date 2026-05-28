# Data Dictionary

## `data/raw/problem_frames_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `frame` | string | Candidate problem frame. |
| `explanatory_adequacy` | numeric | Score from 1 to 10 representing how well the frame explains available evidence. |
| `stakeholder_coverage` | numeric | Score from 1 to 10 representing how well the frame includes relevant stakeholders and system dimensions. |
| `opportunity_value` | numeric | Score from 1 to 10 representing whether the frame opens useful downstream design opportunities. |
| `framing_risk` | numeric | Score from 1 to 10 representing overall risk. Higher risk lowers frame value. |
| `narrowness_risk` | numeric | Score from 1 to 10 representing risk that the frame is too narrow. |
| `stakeholder_exclusion_risk` | numeric | Score from 1 to 10 representing risk that the frame excludes affected stakeholders. |
| `causality_risk` | numeric | Score from 1 to 10 representing risk of misattributing causes. |
| `political_distortion_risk` | numeric | Score from 1 to 10 representing risk that the frame is politically or institutionally convenient rather than analytically strong. |
| `evidence_quality` | numeric | Optional score from 0 to 1 representing confidence in supporting evidence. |
| `frame_confidence` | numeric | Optional score from 0 to 1 representing confidence in the frame. |
| `implementation_scope` | numeric | Optional score from 1 to 10 representing scope or complexity implied by the frame. |

## `data/raw/problem_framing_scenario_weights.csv`

| Column | Type | Description |
|---|---:|---|
| `scenario` | string | Name of the strategic priority scenario. |
| `explanatory_adequacy` | numeric | Weight applied to explanatory adequacy. |
| `stakeholder_coverage` | numeric | Weight applied to stakeholder/system coverage. |
| `opportunity_value` | numeric | Weight applied to opportunity value. |
| `framing_risk` | numeric | Weight applied as a penalty for framing risk. |

Scenario weights must sum to 1.0.

## `data/raw/counterframes_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `dominant_frame` | string | Frame currently being considered or treated as dominant. |
| `counterframe` | string | Alternative frame that should be tested. |
| `reason_to_test` | string | Why the counterframe matters. |
| `missing_evidence_risk` | numeric | Score from 0 to 1 representing risk that the dominant frame lacks sufficient evidence. |
| `power_convenience_risk` | numeric | Score from 0 to 1 representing risk that the dominant frame is convenient for powerful actors. |
