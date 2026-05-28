-- Analytical queries for implementation and scaling.
-- Run after schema.sql:
--   sqlite3 outputs/implementation_scaling.db < sql/schema.sql
--   sqlite3 outputs/implementation_scaling.db < sql/analytical_queries.sql

DELETE FROM implementation_scores;

INSERT INTO implementation_scores (
    intervention_id,
    scenario_id,
    implementation_value,
    evidence_adjusted_value,
    scaled_quality_estimate,
    composite_risk,
    implementation_review_priority,
    scale_readiness
)
SELECT
    p.intervention_id,
    s.scenario_id,
    s.adoption_readiness_weight * p.adoption_readiness +
    s.operational_fit_weight * p.operational_fit +
    s.durability_weight * p.durability +
    s.governance_readiness_weight * p.governance_readiness +
    s.equity_readiness_weight * p.equity_readiness +
    s.financial_sustainability_weight * p.financial_sustainability -
    s.composite_risk_weight * (
        0.25 * p.operational_risk +
        0.22 * p.governance_risk +
        0.18 * p.technical_risk +
        0.22 * p.equity_risk +
        0.13 * p.financial_risk
    ) AS implementation_value,
    (
        s.adoption_readiness_weight * p.adoption_readiness +
        s.operational_fit_weight * p.operational_fit +
        s.durability_weight * p.durability +
        s.governance_readiness_weight * p.governance_readiness +
        s.equity_readiness_weight * p.equity_readiness +
        s.financial_sustainability_weight * p.financial_sustainability -
        s.composite_risk_weight * (
            0.25 * p.operational_risk +
            0.22 * p.governance_risk +
            0.18 * p.technical_risk +
            0.22 * p.equity_risk +
            0.13 * p.financial_risk
        )
    ) * (0.75 + 0.15 * p.evidence_quality + 0.10 * p.stakeholder_coverage) AS evidence_adjusted_value,
    (
        s.adoption_readiness_weight * p.adoption_readiness +
        s.operational_fit_weight * p.operational_fit +
        s.durability_weight * p.durability +
        s.governance_readiness_weight * p.governance_readiness +
        s.equity_readiness_weight * p.equity_readiness +
        s.financial_sustainability_weight * p.financial_sustainability -
        s.composite_risk_weight * (
            0.25 * p.operational_risk +
            0.22 * p.governance_risk +
            0.18 * p.technical_risk +
            0.22 * p.equity_risk +
            0.13 * p.financial_risk
        )
    ) - p.scale_sensitivity * p.context_complexity AS scaled_quality_estimate,
    0.25 * p.operational_risk +
    0.22 * p.governance_risk +
    0.18 * p.technical_risk +
    0.22 * p.equity_risk +
    0.13 * p.financial_risk AS composite_risk,
    0.28 * (
        0.25 * p.operational_risk +
        0.22 * p.governance_risk +
        0.18 * p.technical_risk +
        0.22 * p.equity_risk +
        0.13 * p.financial_risk
    ) +
    0.18 * (10.0 - p.governance_readiness) +
    0.18 * (10.0 - p.equity_readiness) +
    0.14 * (10.0 - p.financial_sustainability) +
    0.12 * p.context_complexity +
    0.10 * (1.0 - p.evidence_quality) * 10.0 AS implementation_review_priority,
    0.25 * p.adoption_readiness +
    0.20 * p.operational_fit +
    0.20 * p.durability +
    0.15 * p.governance_readiness +
    0.15 * p.equity_readiness -
    0.05 * (
        0.25 * p.operational_risk +
        0.22 * p.governance_risk +
        0.18 * p.technical_risk +
        0.22 * p.equity_risk +
        0.13 * p.financial_risk
    ) -
    0.10 * p.scale_sensitivity * p.context_complexity AS scale_readiness
FROM implementation_portfolio p
CROSS JOIN implementation_scenario_weights s;

DROP VIEW IF EXISTS ranked_implementation_scores;

CREATE VIEW ranked_implementation_scores AS
SELECT
    sw.scenario_name,
    p.intervention_name,
    p.intervention_type,
    p.implementation_stage,
    s.implementation_value,
    s.evidence_adjusted_value,
    s.scaled_quality_estimate,
    s.composite_risk,
    s.implementation_review_priority,
    s.scale_readiness,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY s.implementation_value DESC
    ) AS scenario_rank
FROM implementation_scores s
JOIN implementation_portfolio p
    ON s.intervention_id = p.intervention_id
JOIN implementation_scenario_weights sw
    ON s.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS implementation_risk_priority;

CREATE VIEW implementation_risk_priority AS
SELECT
    intervention_name,
    risk_category,
    risk_description,
    severity,
    likelihood,
    detectability,
    severity * likelihood * detectability AS risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM implementation_risk_register;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    intervention_name,
    intervention_type,
    implementation_stage,
    ROUND(implementation_value, 3) AS implementation_value,
    ROUND(scaled_quality_estimate, 3) AS scaled_quality_estimate,
    ROUND(scale_readiness, 3) AS scale_readiness
FROM ranked_implementation_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    intervention_name,
    COUNT(*) AS times_ranked_first
FROM ranked_implementation_scores
WHERE scenario_rank = 1
GROUP BY intervention_name
ORDER BY times_ranked_first DESC, intervention_name;

SELECT
    intervention_name,
    ROUND(AVG(implementation_value), 3) AS average_implementation_value,
    ROUND(AVG(scaled_quality_estimate), 3) AS average_scaled_quality,
    ROUND(AVG(composite_risk), 3) AS average_composite_risk,
    ROUND(AVG(implementation_review_priority), 3) AS average_review_priority,
    ROUND(AVG(scale_readiness), 3) AS average_scale_readiness
FROM ranked_implementation_scores
GROUP BY intervention_name
ORDER BY average_implementation_value DESC;

SELECT
    intervention_name,
    risk_category,
    risk_description,
    risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM implementation_risk_priority
ORDER BY risk_priority_number DESC;
