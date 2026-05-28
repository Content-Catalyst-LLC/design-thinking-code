-- Analytical queries for design thinking for sustainability.
-- Run after schema.sql:
--   sqlite3 outputs/sustainability_design.db < sql/schema.sql
--   sqlite3 outputs/sustainability_design.db < sql/analytical_queries.sql

DELETE FROM sustainability_scores;

INSERT INTO sustainability_scores (
    concept_id,
    scenario_id,
    sustainability_value,
    evidence_adjusted_value,
    evidence_strength,
    transition_readiness,
    ecological_integrity_index,
    justice_burden_index,
    learning_priority,
    portfolio_resilience
)
SELECT
    c.concept_id,
    w.scenario_id,
    w.usability_weight * c.usability +
    w.feasibility_weight * c.feasibility +
    w.ecological_benefit_weight * c.ecological_benefit +
    w.circularity_weight * c.circularity +
    w.equity_weight * c.equity +
    w.durability_weight * c.durability -
    w.risk_weight * c.risk AS sustainability_value,
    (
        w.usability_weight * c.usability +
        w.feasibility_weight * c.feasibility +
        w.ecological_benefit_weight * c.ecological_benefit +
        w.circularity_weight * c.circularity +
        w.equity_weight * c.equity +
        w.durability_weight * c.durability -
        w.risk_weight * c.risk
    ) * (
        0.75 + 0.25 * (
            0.35 * c.evidence_quality +
            0.30 * c.stakeholder_coverage +
            0.35 * c.lifecycle_boundary_quality
        )
    ) AS evidence_adjusted_value,
    0.35 * c.evidence_quality +
    0.30 * c.stakeholder_coverage +
    0.35 * c.lifecycle_boundary_quality AS evidence_strength,
    0.24 * c.usability +
    0.22 * c.feasibility +
    0.18 * c.stakeholder_coverage * 10.0 +
    0.18 * c.durability +
    0.18 * (
        0.35 * c.evidence_quality +
        0.30 * c.stakeholder_coverage +
        0.35 * c.lifecycle_boundary_quality
    ) * 10.0 -
    0.12 * c.implementation_complexity AS transition_readiness,
    0.40 * c.ecological_benefit +
    0.25 * c.circularity +
    0.20 * c.lifecycle_boundary_quality * 10.0 +
    0.15 * c.durability -
    0.12 * c.risk AS ecological_integrity_index,
    0.40 * c.equity +
    0.25 * c.stakeholder_coverage * 10.0 +
    0.20 * c.usability -
    0.15 * c.burden_shift_risk AS justice_burden_index,
    0.22 * c.risk +
    0.18 * c.implementation_complexity +
    0.17 * c.burden_shift_risk +
    0.16 * (1.0 - c.evidence_quality) * 10.0 +
    0.14 * (1.0 - c.stakeholder_coverage) * 10.0 +
    0.13 * (1.0 - c.lifecycle_boundary_quality) * 10.0 AS learning_priority,
    0.30 * c.durability +
    0.25 * (
        0.24 * c.usability +
        0.22 * c.feasibility +
        0.18 * c.stakeholder_coverage * 10.0 +
        0.18 * c.durability +
        0.18 * (
            0.35 * c.evidence_quality +
            0.30 * c.stakeholder_coverage +
            0.35 * c.lifecycle_boundary_quality
        ) * 10.0 -
        0.12 * c.implementation_complexity
    ) +
    0.25 * (
        0.40 * c.ecological_benefit +
        0.25 * c.circularity +
        0.20 * c.lifecycle_boundary_quality * 10.0 +
        0.15 * c.durability -
        0.12 * c.risk
    ) +
    0.20 * (
        0.40 * c.equity +
        0.25 * c.stakeholder_coverage * 10.0 +
        0.20 * c.usability -
        0.15 * c.burden_shift_risk
    ) -
    0.12 * c.risk AS portfolio_resilience
FROM sustainability_concepts c
CROSS JOIN sustainability_scenario_weights w;

DROP VIEW IF EXISTS ranked_sustainability_scores;

CREATE VIEW ranked_sustainability_scores AS
SELECT
    sw.scenario_name,
    c.concept_name,
    c.concept_type,
    c.transition_domain,
    s.sustainability_value,
    s.evidence_adjusted_value,
    s.evidence_strength,
    s.transition_readiness,
    s.ecological_integrity_index,
    s.justice_burden_index,
    s.learning_priority,
    s.portfolio_resilience,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY s.sustainability_value DESC
    ) AS scenario_rank
FROM sustainability_scores s
JOIN sustainability_concepts c
    ON s.concept_id = c.concept_id
JOIN sustainability_scenario_weights sw
    ON s.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS sustainability_risk_priority;

CREATE VIEW sustainability_risk_priority AS
SELECT
    concept_name,
    risk_category,
    risk_description,
    severity,
    likelihood,
    detectability,
    severity * likelihood * detectability AS risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM sustainability_risk_register;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    concept_name,
    concept_type,
    transition_domain,
    ROUND(sustainability_value, 3) AS sustainability_value,
    ROUND(evidence_adjusted_value, 3) AS evidence_adjusted_value,
    ROUND(ecological_integrity_index, 3) AS ecological_integrity_index,
    ROUND(justice_burden_index, 3) AS justice_burden_index
FROM ranked_sustainability_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    concept_name,
    COUNT(*) AS times_ranked_first
FROM ranked_sustainability_scores
WHERE scenario_rank = 1
GROUP BY concept_name
ORDER BY times_ranked_first DESC, concept_name;

SELECT
    concept_name,
    ROUND(AVG(sustainability_value), 3) AS average_sustainability_value,
    ROUND(AVG(evidence_adjusted_value), 3) AS average_evidence_adjusted_value,
    ROUND(AVG(transition_readiness), 3) AS average_transition_readiness,
    ROUND(AVG(ecological_integrity_index), 3) AS average_ecological_integrity_index,
    ROUND(AVG(justice_burden_index), 3) AS average_justice_burden_index,
    ROUND(AVG(learning_priority), 3) AS average_learning_priority
FROM ranked_sustainability_scores
GROUP BY concept_name
ORDER BY average_sustainability_value DESC;

SELECT
    concept_name,
    risk_category,
    risk_description,
    risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM sustainability_risk_priority
ORDER BY risk_priority_number DESC;
