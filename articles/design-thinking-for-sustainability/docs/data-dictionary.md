# Data Dictionary

## `sustainability_concepts_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `concept` | string | Candidate sustainability design concept. |
| `concept_type` | string | Concept category such as service model, circular system, urban infrastructure, repair platform, energy access, institutional toolkit, climate resilience, or water system. |
| `transition_domain` | string | Broad transition domain such as energy, mobility, materials, water, food, adaptation, procurement, or built environment. |
| `usability` | numeric | Score from 1 to 10 representing stakeholder usability and adoption value. |
| `feasibility` | numeric | Score from 1 to 10 representing implementation feasibility. |
| `ecological_benefit` | numeric | Score from 1 to 10 representing expected ecological benefit. |
| `circularity` | numeric | Score from 1 to 10 representing material stewardship, reuse, repair, and waste-reduction potential. |
| `equity` | numeric | Score from 1 to 10 representing equity, justice, access, and burden distribution. |
| `durability` | numeric | Score from 1 to 10 representing durability under real institutional conditions. |
| `risk` | numeric | Score from 1 to 10 representing implementation and unintended-consequence risk. |
| `evidence_quality` | numeric | Score from 0 to 1 representing quality of available evidence. |
| `stakeholder_coverage` | numeric | Score from 0 to 1 representing coverage of relevant stakeholder groups. |
| `lifecycle_boundary_quality` | numeric | Score from 0 to 1 representing clarity of lifecycle boundaries and evidence scope. |
| `burden_shift_risk` | numeric | Score from 1 to 10 representing risk that burdens shift elsewhere. |
| `implementation_complexity` | numeric | Score from 1 to 10 representing implementation complexity. |

## `transition_pathways_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `concept` | string | Concept name. |
| `period` | integer | Transition review period. |
| `adoption_rate` | numeric | Adoption rate in the period. |
| `friction_score` | numeric | Friction score. Lower is better. |
| `ecological_impact_reduction` | numeric | Estimated impact reduction proportion. |
| `equity_score` | numeric | Equity score. |
| `implementation_cost` | numeric | Implementation cost score. Lower is better. |
| `maintenance_burden` | numeric | Maintenance burden score. Lower is better. |
| `trust_score` | numeric | Stakeholder trust score. |
| `participation_quality` | numeric | Participation quality score from 0 to 1. |
