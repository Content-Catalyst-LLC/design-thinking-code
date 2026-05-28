# Data Dictionary

## `organizational_innovation_concepts_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `concept` | string | Candidate organizational innovation concept. |
| `concept_type` | string | Concept category such as service design, digital service, AI-assisted workflow, employee experience, operating model, knowledge system, service recovery, decision support, inclusive design, or governance model. |
| `organizational_domain` | string | Organizational area such as operations, customer support, service operations, people operations, cross-functional work, organizational learning, customer experience, management systems, or innovation management. |
| `desirability` | numeric | Score from 1 to 10 representing stakeholder value and desirability. |
| `feasibility` | numeric | Score from 1 to 10 representing practical feasibility. |
| `viability` | numeric | Score from 1 to 10 representing strategic and institutional viability. |
| `equity` | numeric | Score from 1 to 10 representing ethical adequacy, accessibility, inclusion, and burden distribution. |
| `learning_value` | numeric | Score from 1 to 10 representing prototype learning potential. |
| `implementation_readiness` | numeric | Score from 1 to 10 representing readiness for adoption and operationalization. |
| `risk` | numeric | Score from 1 to 10 representing implementation and unintended-consequence risk. |
| `evidence_quality` | numeric | Score from 0 to 1 representing quality of available evidence. |
| `stakeholder_coverage` | numeric | Score from 0 to 1 representing coverage of relevant stakeholders. |
| `technical_complexity` | numeric | Score from 1 to 10 representing technical complexity. |
| `organizational_complexity` | numeric | Score from 1 to 10 representing governance, adoption, and coordination complexity. |
| `ethical_risk` | numeric | Score from 1 to 10 representing possible ethical or equity risk. |

## `prototype_learning_rounds_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `concept` | string | Innovation concept name. |
| `round` | integer | Prototype or pilot round. |
| `adoption_likelihood` | numeric | Estimated likelihood of adoption. |
| `user_friction` | numeric | User friction score. Lower is better. |
| `trust_score` | numeric | Stakeholder trust score. |
| `operational_burden` | numeric | Operational burden score. Lower is better. |
| `equity_score` | numeric | Equity performance score. |
| `task_success_rate` | numeric | Prototype task success rate. |
| `cycle_time` | numeric | Process cycle time. Lower is better. |
| `employee_confidence` | numeric | Employee confidence in the innovation. |
