-- Analytical queries for testing and validation.
-- Run after schema.sql:
--   sqlite3 outputs/testing_validation.db < sql/schema.sql
--   sqlite3 outputs/testing_validation.db < sql/analytical_queries.sql

DELETE FROM validation_scores;

INSERT INTO validation_scores (
    concept_id,
    scenario_id,
    validation_value,
    combined_risk,
    confidence_adjusted_value,
    validation_review_priority,
    advance_readiness
)
SELECT
    c.concept_id,
    s.scenario_id,
    s.desirability_weight * c.desirability +
    s.feasibility_weight * c.feasibility +
    s.viability_weight * c.viability +
    s.responsibility_weight * c.responsibility -
    s.risk_penalty_weight * (0.50 * c.friction + 0.50 * c.residual_risk) AS validation_value,
    0.50 * c.friction + 0.50 * c.residual_risk AS combined_risk,
    (
        s.desirability_weight * c.desirability +
        s.feasibility_weight * c.feasibility +
        s.viability_weight * c.viability +
        s.responsibility_weight * c.responsibility -
        s.risk_penalty_weight * (0.50 * c.friction + 0.50 * c.residual_risk)
    ) * (
        0.75 +
        0.25 * (
            0.45 * c.evidence_quality +
            0.35 * c.stakeholder_coverage +
            0.20 * c.method_triangulation
        )
    ) AS confidence_adjusted_value,
    0.30 * c.residual_risk +
    0.25 * c.friction +
    0.15 * (1.0 - c.evidence_quality) * 10.0 +
    0.15 * (1.0 - c.stakeholder_coverage) * 10.0 +
    0.15 * (10.0 - c.responsibility) AS validation_review_priority,
    0.35 * (
        (
            s.desirability_weight * c.desirability +
            s.feasibility_weight * c.feasibility +
            s.viability_weight * c.viability +
            s.responsibility_weight * c.responsibility -
            s.risk_penalty_weight * (0.50 * c.friction + 0.50 * c.residual_risk)
        ) * (
            0.75 +
            0.25 * (
                0.45 * c.evidence_quality +
                0.35 * c.stakeholder_coverage +
                0.20 * c.method_triangulation
            )
        )
    ) +
    0.25 * (
        0.30 * c.feasibility +
        0.25 * c.viability +
        0.20 * c.operational_signal -
        0.10 * (0.50 * c.friction + 0.50 * c.residual_risk)
    ) +
    0.20 * (
        0.50 * c.equity_signal +
        0.35 * c.accessibility_signal +
        0.15 * c.stakeholder_coverage * 10.0
    ) +
    0.10 * c.method_triangulation * 10.0 -
    0.10 * (
        0.30 * c.residual_risk +
        0.25 * c.friction +
        0.15 * (1.0 - c.evidence_quality) * 10.0 +
        0.15 * (1.0 - c.stakeholder_coverage) * 10.0 +
        0.15 * (10.0 - c.responsibility)
    ) AS advance_readiness
FROM validation_concepts c
CROSS JOIN validation_scenario_weights s;

DROP VIEW IF EXISTS ranked_validation_scores;

CREATE VIEW ranked_validation_scores AS
SELECT
    sw.scenario_name,
    c.concept_name,
    c.prototype_type,
    c.fidelity_level,
    vs.validation_value,
    vs.combined_risk,
    vs.confidence_adjusted_value,
    vs.validation_review_priority,
    vs.advance_readiness,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY vs.validation_value DESC
    ) AS scenario_rank
FROM validation_scores vs
JOIN validation_concepts c
    ON vs.concept_id = c.concept_id
JOIN validation_scenario_weights sw
    ON vs.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS validation_risk_priority;

CREATE VIEW validation_risk_priority AS
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
FROM validation_risk_register;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    concept_name,
    prototype_type,
    fidelity_level,
    ROUND(validation_value, 3) AS validation_value,
    ROUND(combined_risk, 3) AS combined_risk,
    ROUND(advance_readiness, 3) AS advance_readiness
FROM ranked_validation_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    concept_name,
    COUNT(*) AS times_ranked_first
FROM ranked_validation_scores
WHERE scenario_rank = 1
GROUP BY concept_name
ORDER BY times_ranked_first DESC, concept_name;

SELECT
    concept_name,
    ROUND(AVG(validation_value), 3) AS average_validation_value,
    ROUND(MIN(validation_value), 3) AS minimum_validation_value,
    ROUND(MAX(validation_value), 3) AS maximum_validation_value,
    ROUND(AVG(combined_risk), 3) AS average_combined_risk,
    ROUND(AVG(validation_review_priority), 3) AS average_review_priority
FROM ranked_validation_scores
GROUP BY concept_name
ORDER BY average_validation_value DESC;

SELECT
    concept_name,
    risk_category,
    risk_description,
    risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM validation_risk_priority
ORDER BY risk_priority_number DESC;
