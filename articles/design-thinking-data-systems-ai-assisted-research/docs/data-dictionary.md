# Data Dictionary

## `research_signals_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `signal` | string | Research signal or finding candidate. |
| `evidence_type` | string | Source category such as interviews, analytics, service logs, prototype tests, or AI validation. |
| `source_strength` | numeric | 0-1 strength of original evidence source. |
| `relevance` | numeric | 0-1 relevance to design decision or research question. |
| `traceability` | numeric | 0-1 ability to trace the claim to source evidence. |
| `representativeness` | numeric | 0-1 degree of participant or data coverage. |
| `validation` | numeric | 0-1 validation status. |
| `missingness_risk` | numeric | 0-1 risk that important evidence or groups are missing. |
| `ai_assistance_risk` | numeric | 0-1 risk introduced by AI-assisted analysis. |
| `decision_relevance` | numeric | 0-1 relevance to design decisions. |
| `recency` | numeric | 0-1 recency of evidence. |
| `consent_alignment` | numeric | 0-1 alignment with participant consent and reuse limits. |
| `participant_coverage` | numeric | 0-1 coverage of affected participant groups. |

## `ai_assistance_log_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `artifact_id` | string | AI-assisted research artifact identifier. |
| `research_task` | string | Task performed with AI assistance. |
| `ai_tool_class` | string | AI tool category. |
| `source_grounding` | numeric | 0-1 source grounding quality. |
| `human_review` | numeric | 0-1 strength of human review. |
| `output_reliability` | numeric | 0-1 reliability of output. |
| `sensitive_data_exposure` | numeric | 0-1 exposure of sensitive data. |
| `prompt_traceability` | numeric | 0-1 prompt and instruction traceability. |
| `model_version_recorded` | numeric | 0-1 whether model/version information is recorded. |
| `hallucination_risk` | numeric | 0-1 hallucination or unsupported inference risk. |
| `minority_signal_preservation` | numeric | 0-1 preservation of edge cases and minority signals. |
