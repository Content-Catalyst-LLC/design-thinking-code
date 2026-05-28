# Data Dictionary

## `contextual_inquiry_evidence_units_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `unit_id` | integer | Unique evidence unit identifier. |
| `participant_group` | string | Stakeholder or participant group represented by the evidence unit. |
| `method` | string | Research method used to collect the evidence. |
| `primary_theme` | string | Main theme assigned during synthesis. |
| `secondary_theme` | string | Secondary or related theme. |
| `evidence_strength` | numeric | Score from 1 to 10 representing strength or richness of evidence. |
| `interpretive_risk` | numeric | Score from 1 to 10 representing uncertainty or risk of overinterpretation. |
| `environmental_constraint` | numeric | Score from 1 to 10 representing the importance of environmental conditions. |
| `artifact_dependency` | numeric | Score from 1 to 10 representing reliance on artifacts, tools, records, forms, notes, or systems. |
| `workflow_stage` | string | Stage of the workflow or journey where the evidence appears. |
| `privacy_sensitivity` | numeric | Score from 0 to 1 representing privacy sensitivity. |
| `power_asymmetry` | numeric | Score from 0 to 1 representing participant/institution power asymmetry. |

## `synthesis_scenario_weights.csv`

| Column | Type | Description |
|---|---:|---|
| `scenario` | string | Name of synthesis-priority scenario. |
| `evidence_strength` | numeric | Weight applied to evidence strength. |
| `stakeholder_coverage` | numeric | Weight applied to stakeholder coverage. |
| `method_triangulation` | numeric | Weight applied to method triangulation. |
| `interpretive_risk` | numeric | Weight applied as a penalty for interpretive risk. |

## `coder_theme_assignments_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `unit_id` | integer | Evidence unit identifier. |
| `coder_a` | string | Theme assigned by coder A. |
| `coder_b` | string | Theme assigned by coder B. |
| `coder_c` | string | Theme assigned by coder C. |

## `stakeholder_sampling_frame_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `stakeholder_group` | string | Stakeholder group in the sampling frame. |
| `included_sessions` | integer | Number of intended or included sessions. |
| `priority_level` | string | Sampling priority level. |
| `access_risk` | numeric | Score from 0 to 1 representing risk of exclusion or difficulty reaching group. |
| `power_asymmetry` | numeric | Score from 0 to 1 representing power asymmetry. |
| `notes` | string | Sampling notes. |
