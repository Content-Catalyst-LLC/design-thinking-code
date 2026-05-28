-- Analytical queries for prototype portfolio evaluation.
-- Run after schema.sql:
--   sqlite3 outputs/prototype_portfolio.db < sql/analytical_queries.sql

DELETE FROM prototype_scores;

INSERT INTO prototype_scores (
    prototype_id,
    scenario_id,
    prototype_value,
    composite_risk,
    confidence_adjusted_value,
    prototype_review_priority,
    advance_readiness
)
SELECT
    p.prototype_id,
    s.scenario_id,
    s.learning_gain_weight * p.learning_gain +
    s.feasibility_signal_weight * p.feasibility_signal +
    s.user_response_weight * p.user_response +
    s.equity_value_weight * p.equity_value +
    s.implementation_relevance_weight * p.implementation_relevance -
    s.composite_risk_weight * (
        0.30 * p.ethical_risk +
        0.30 * p.operational_risk +
        0.20 * p.technical_risk +
        0.20 * p.scaling_risk
    ) AS prototype_value,
    0.30 * p.ethical_risk +
    0.30 * p.operational_risk +
    0.20 * p.technical_risk +
    0.20 * p.scaling_risk AS composite_risk,
    (
        s.learning_gain_weight * p.learning_gain +
        s.feasibility_signal_weight * p.feasibility_signal +
        s.user_response_weight * p.user_response +
        s.equity_value_weight * p.equity_value +
        s.implementation_relevance_weight * p.implementation_relevance -
        s.composite_risk_weight * (
            0.30 * p.ethical_risk +
            0.30 * p.operational_risk +
            0.20 * p.technical_risk +
            0.20 * p.scaling_risk
        )
    ) * (0.75 + 0.25 * p.evidence_quality) AS confidence_adjusted_value,
    0.35 * (
        0.30 * p.ethical_risk +
        0.30 * p.operational_risk +
        0.20 * p.technical_risk +
        0.20 * p.scaling_risk
    ) +
    0.20 * (10.0 - p.evidence_quality * 10.0) +
    0.20 * p.ethical_risk +
    0.15 * p.scaling_risk +
    0.10 * (10.0 - p.feasibility_signal) AS prototype_review_priority,
    0.30 * (
        (
            s.learning_gain_weight * p.learning_gain +
            s.feasibility_signal_weight * p.feasibility_signal +
            s.user_response_weight * p.user_response +
            s.equity_value_weight * p.equity_value +
            s.implementation_relevance_weight * p.implementation_relevance -
            s.composite_risk_weight * (
                0.30 * p.ethical_risk +
                0.30 * p.operational_risk +
                0.20 * p.technical_risk +
                0.20 * p.scaling_risk
            )
        ) * (0.75 + 0.25 * p.evidence_quality)
    ) +
    0.25 * p.feasibility_signal +
    0.20 * p.implementation_relevance +
    0.15 * p.stakeholder_coverage * 10.0 -
    0.10 * (
        0.30 * p.ethical_risk +
        0.30 * p.operational_risk +
        0.20 * p.technical_risk +
        0.20 * p.scaling_risk
    ) AS advance_readiness
FROM prototypes p
CROSS JOIN prototype_scenario_weights s;

DROP VIEW IF EXISTS ranked_prototype_scores;

CREATE VIEW ranked_prototype_scores AS
SELECT
    sw.scenario_name,
    p.prototype_name,
    p.prototype_type,
    p.fidelity_level,
    ps.prototype_value,
    ps.composite_risk,
    ps.confidence_adjusted_value,
    ps.prototype_review_priority,
    ps.advance_readiness,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY ps.prototype_value DESC
    ) AS scenario_rank
FROM prototype_scores ps
JOIN prototypes p
    ON ps.prototype_id = p.prototype_id
JOIN prototype_scenario_weights sw
    ON ps.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS risk_priority;

CREATE VIEW risk_priority AS
SELECT
    prototype_name,
    risk_category,
    risk_description,
    severity,
    likelihood,
    detectability,
    severity * likelihood * detectability AS risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM prototype_risk_register;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    prototype_name,
    prototype_type,
    fidelity_level,
    ROUND(prototype_value, 3) AS prototype_value,
    ROUND(composite_risk, 3) AS composite_risk,
    ROUND(advance_readiness, 3) AS advance_readiness
FROM ranked_prototype_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    prototype_name,
    COUNT(*) AS times_ranked_first
FROM ranked_prototype_scores
WHERE scenario_rank = 1
GROUP BY prototype_name
ORDER BY times_ranked_first DESC, prototype_name;

SELECT
    prototype_name,
    ROUND(AVG(prototype_value), 3) AS average_prototype_value,
    ROUND(MIN(prototype_value), 3) AS minimum_prototype_value,
    ROUND(MAX(prototype_value), 3) AS maximum_prototype_value,
    ROUND(AVG(composite_risk), 3) AS average_composite_risk,
    ROUND(AVG(prototype_review_priority), 3) AS average_review_priority
FROM ranked_prototype_scores
GROUP BY prototype_name
ORDER BY average_prototype_value DESC;

SELECT
    prototype_name,
    risk_category,
    risk_description,
    risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM risk_priority
ORDER BY risk_priority_number DESC;
