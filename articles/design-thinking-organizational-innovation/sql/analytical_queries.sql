-- Analytical queries for design thinking and organizational innovation.
-- Run after schema.sql:
--   sqlite3 outputs/organizational_innovation.db < sql/schema.sql
--   sqlite3 outputs/organizational_innovation.db < sql/analytical_queries.sql

DELETE FROM innovation_scores;

INSERT INTO innovation_scores (
    concept_id,
    scenario_id,
    design_value,
    evidence_adjusted_value,
    evidence_strength,
    implementation_resilience,
    ethical_innovation_index,
    organizational_learning_index,
    learning_priority,
    portfolio_strength
)
SELECT
    c.concept_id,
    w.scenario_id,
    w.desirability_weight * c.desirability +
    w.feasibility_weight * c.feasibility +
    w.viability_weight * c.viability +
    w.equity_weight * c.equity +
    w.learning_value_weight * c.learning_value +
    w.implementation_readiness_weight * c.implementation_readiness -
    w.risk_weight * c.risk AS design_value,
    (
        w.desirability_weight * c.desirability +
        w.feasibility_weight * c.feasibility +
        w.viability_weight * c.viability +
        w.equity_weight * c.equity +
        w.learning_value_weight * c.learning_value +
        w.implementation_readiness_weight * c.implementation_readiness -
        w.risk_weight * c.risk
    ) * (
        0.75 + 0.25 * (
            0.55 * c.evidence_quality +
            0.45 * c.stakeholder_coverage
        )
    ) AS evidence_adjusted_value,
    0.55 * c.evidence_quality +
    0.45 * c.stakeholder_coverage AS evidence_strength,
    0.26 * c.implementation_readiness +
    0.22 * c.feasibility +
    0.18 * c.viability +
    0.16 * (
        0.55 * c.evidence_quality +
        0.45 * c.stakeholder_coverage
    ) * 10.0 -
    0.09 * c.technical_complexity -
    0.09 * c.organizational_complexity AS implementation_resilience,
    0.34 * c.equity +
    0.22 * c.stakeholder_coverage * 10.0 +
    0.18 * c.desirability +
    0.16 * c.learning_value -
    0.10 * c.ethical_risk AS ethical_innovation_index,
    0.30 * c.learning_value +
    0.22 * (
        0.55 * c.evidence_quality +
        0.45 * c.stakeholder_coverage
    ) * 10.0 +
    0.18 * c.stakeholder_coverage * 10.0 +
    0.16 * c.implementation_readiness -
    0.07 * c.risk -
    0.07 * c.organizational_complexity AS organizational_learning_index,
    0.22 * c.risk +
    0.18 * c.technical_complexity +
    0.18 * c.organizational_complexity +
    0.16 * c.ethical_risk +
    0.14 * (1.0 - c.evidence_quality) * 10.0 +
    0.12 * (1.0 - c.stakeholder_coverage) * 10.0 AS learning_priority,
    0.30 * (
        w.desirability_weight * c.desirability +
        w.feasibility_weight * c.feasibility +
        w.viability_weight * c.viability +
        w.equity_weight * c.equity +
        w.learning_value_weight * c.learning_value +
        w.implementation_readiness_weight * c.implementation_readiness -
        w.risk_weight * c.risk
    ) +
    0.24 * (
        0.26 * c.implementation_readiness +
        0.22 * c.feasibility +
        0.18 * c.viability +
        0.16 * (
            0.55 * c.evidence_quality +
            0.45 * c.stakeholder_coverage
        ) * 10.0 -
        0.09 * c.technical_complexity -
        0.09 * c.organizational_complexity
    ) +
    0.24 * (
        0.34 * c.equity +
        0.22 * c.stakeholder_coverage * 10.0 +
        0.18 * c.desirability +
        0.16 * c.learning_value -
        0.10 * c.ethical_risk
    ) +
    0.22 * (
        0.30 * c.learning_value +
        0.22 * (
            0.55 * c.evidence_quality +
            0.45 * c.stakeholder_coverage
        ) * 10.0 +
        0.18 * c.stakeholder_coverage * 10.0 +
        0.16 * c.implementation_readiness -
        0.07 * c.risk -
        0.07 * c.organizational_complexity
    ) -
    0.12 * c.risk AS portfolio_strength
FROM innovation_concepts c
CROSS JOIN innovation_scenario_weights w;

DROP VIEW IF EXISTS ranked_innovation_scores;

CREATE VIEW ranked_innovation_scores AS
SELECT
    sw.scenario_name,
    c.concept_name,
    c.concept_type,
    c.organizational_domain,
    s.design_value,
    s.evidence_adjusted_value,
    s.evidence_strength,
    s.implementation_resilience,
    s.ethical_innovation_index,
    s.organizational_learning_index,
    s.learning_priority,
    s.portfolio_strength,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY s.design_value DESC
    ) AS scenario_rank
FROM innovation_scores s
JOIN innovation_concepts c
    ON s.concept_id = c.concept_id
JOIN innovation_scenario_weights sw
    ON s.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS innovation_risk_priority;

CREATE VIEW innovation_risk_priority AS
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
FROM innovation_risk_register;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    concept_name,
    concept_type,
    organizational_domain,
    ROUND(design_value, 3) AS design_value,
    ROUND(evidence_adjusted_value, 3) AS evidence_adjusted_value,
    ROUND(ethical_innovation_index, 3) AS ethical_innovation_index,
    ROUND(implementation_resilience, 3) AS implementation_resilience
FROM ranked_innovation_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    concept_name,
    COUNT(*) AS times_ranked_first
FROM ranked_innovation_scores
WHERE scenario_rank = 1
GROUP BY concept_name
ORDER BY times_ranked_first DESC, concept_name;

SELECT
    concept_name,
    ROUND(AVG(design_value), 3) AS average_design_value,
    ROUND(AVG(evidence_adjusted_value), 3) AS average_evidence_adjusted_value,
    ROUND(AVG(implementation_resilience), 3) AS average_implementation_resilience,
    ROUND(AVG(ethical_innovation_index), 3) AS average_ethical_innovation_index,
    ROUND(AVG(organizational_learning_index), 3) AS average_organizational_learning_index,
    ROUND(AVG(learning_priority), 3) AS average_learning_priority
FROM ranked_innovation_scores
GROUP BY concept_name
ORDER BY average_design_value DESC;

SELECT
    concept_name,
    risk_category,
    risk_description,
    risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM innovation_risk_priority
ORDER BY risk_priority_number DESC;
