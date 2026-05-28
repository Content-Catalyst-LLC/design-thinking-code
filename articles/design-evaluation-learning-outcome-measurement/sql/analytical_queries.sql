-- Analytical queries for design evaluation, learning, and outcome measurement.
-- Run after schema.sql:
--   sqlite3 outputs/design_evaluation.db < sql/schema.sql
--   sqlite3 outputs/design_evaluation.db < sql/analytical_queries.sql

DELETE FROM evaluation_scores;

INSERT INTO evaluation_scores (
    intervention_id,
    scenario_id,
    evaluation_value,
    evidence_adjusted_value,
    evidence_strength,
    learning_priority,
    accountability_index,
    learning_value
)
SELECT
    p.intervention_id,
    s.scenario_id,
    s.outcome_improvement_weight * p.outcome_improvement +
    s.burden_reduction_weight * p.burden_reduction +
    s.equity_performance_weight * p.equity_performance +
    s.trust_improvement_weight * p.trust_improvement +
    s.durability_weight * p.durability -
    s.penalty_weight * (0.50 * p.operational_cost + 0.50 * p.residual_risk) AS evaluation_value,
    (
        s.outcome_improvement_weight * p.outcome_improvement +
        s.burden_reduction_weight * p.burden_reduction +
        s.equity_performance_weight * p.equity_performance +
        s.trust_improvement_weight * p.trust_improvement +
        s.durability_weight * p.durability -
        s.penalty_weight * (0.50 * p.operational_cost + 0.50 * p.residual_risk)
    ) * (
        0.75 + 0.25 * MAX(
            0.0,
            MIN(
                1.0,
                0.40 * p.evidence_quality +
                0.35 * p.stakeholder_coverage +
                0.25 * p.method_triangulation -
                0.20 * p.uncertainty
            )
        )
    ) AS evidence_adjusted_value,
    MAX(
        0.0,
        MIN(
            1.0,
            0.40 * p.evidence_quality +
            0.35 * p.stakeholder_coverage +
            0.25 * p.method_triangulation -
            0.20 * p.uncertainty
        )
    ) AS evidence_strength,
    0.25 * p.residual_risk +
    0.20 * (1.0 - p.evidence_quality) * 10.0 +
    0.18 * (1.0 - p.stakeholder_coverage) * 10.0 +
    0.16 * p.operational_cost +
    0.13 * (1.0 - p.method_triangulation) * 10.0 +
    0.08 * p.uncertainty * 10.0 AS learning_priority,
    0.25 * p.equity_performance +
    0.20 * p.trust_improvement +
    0.20 * (
        MAX(
            0.0,
            MIN(
                1.0,
                0.40 * p.evidence_quality +
                0.35 * p.stakeholder_coverage +
                0.25 * p.method_triangulation -
                0.20 * p.uncertainty
            )
        )
    ) * 10.0 +
    0.20 * p.burden_reduction +
    0.15 * p.durability -
    0.10 * (0.50 * p.operational_cost + 0.50 * p.residual_risk) AS accountability_index,
    0.35 * (p.current_quality - p.baseline_quality) +
    0.30 * (
        MAX(
            0.0,
            MIN(
                1.0,
                0.40 * p.evidence_quality +
                0.35 * p.stakeholder_coverage +
                0.25 * p.method_triangulation -
                0.20 * p.uncertainty
            )
        )
    ) * 10.0 +
    0.20 * (
        s.outcome_improvement_weight * p.outcome_improvement +
        s.burden_reduction_weight * p.burden_reduction +
        s.equity_performance_weight * p.equity_performance +
        s.trust_improvement_weight * p.trust_improvement +
        s.durability_weight * p.durability -
        s.penalty_weight * (0.50 * p.operational_cost + 0.50 * p.residual_risk)
    ) -
    0.15 * (
        0.25 * p.residual_risk +
        0.20 * (1.0 - p.evidence_quality) * 10.0 +
        0.18 * (1.0 - p.stakeholder_coverage) * 10.0 +
        0.16 * p.operational_cost +
        0.13 * (1.0 - p.method_triangulation) * 10.0 +
        0.08 * p.uncertainty * 10.0
    ) AS learning_value
FROM evaluation_portfolio p
CROSS JOIN evaluation_scenario_weights s;

DROP VIEW IF EXISTS ranked_evaluation_scores;

CREATE VIEW ranked_evaluation_scores AS
SELECT
    sw.scenario_name,
    p.intervention_name,
    p.intervention_type,
    p.evaluation_stage,
    es.evaluation_value,
    es.evidence_adjusted_value,
    es.evidence_strength,
    es.learning_priority,
    es.accountability_index,
    es.learning_value,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY es.evaluation_value DESC
    ) AS scenario_rank
FROM evaluation_scores es
JOIN evaluation_portfolio p
    ON es.intervention_id = p.intervention_id
JOIN evaluation_scenario_weights sw
    ON es.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS evaluation_risk_priority;

CREATE VIEW evaluation_risk_priority AS
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
FROM evaluation_risk_register;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    intervention_name,
    intervention_type,
    evaluation_stage,
    ROUND(evaluation_value, 3) AS evaluation_value,
    ROUND(evidence_adjusted_value, 3) AS evidence_adjusted_value,
    ROUND(evidence_strength, 3) AS evidence_strength,
    ROUND(learning_priority, 3) AS learning_priority
FROM ranked_evaluation_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    intervention_name,
    COUNT(*) AS times_ranked_first
FROM ranked_evaluation_scores
WHERE scenario_rank = 1
GROUP BY intervention_name
ORDER BY times_ranked_first DESC, intervention_name;

SELECT
    intervention_name,
    ROUND(AVG(evaluation_value), 3) AS average_evaluation_value,
    ROUND(AVG(evidence_adjusted_value), 3) AS average_evidence_adjusted_value,
    ROUND(AVG(evidence_strength), 3) AS average_evidence_strength,
    ROUND(AVG(learning_priority), 3) AS average_learning_priority,
    ROUND(AVG(accountability_index), 3) AS average_accountability_index
FROM ranked_evaluation_scores
GROUP BY intervention_name
ORDER BY average_evaluation_value DESC;

SELECT
    intervention_name,
    risk_category,
    risk_description,
    risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM evaluation_risk_priority
ORDER BY risk_priority_number DESC;
