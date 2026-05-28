-- Analytical queries for design thinking and systems thinking.
-- Run after schema.sql:
--   sqlite3 outputs/system_design.db < sql/schema.sql
--   sqlite3 outputs/system_design.db < sql/analytical_queries.sql

DELETE FROM system_design_scores;

INSERT INTO system_design_scores (
    intervention_id,
    scenario_id,
    system_design_value,
    evidence_adjusted_value,
    context_adjusted_value,
    evidence_strength,
    learning_priority,
    deep_leverage_index,
    burden_shift_index
)
SELECT
    p.intervention_id,
    s.scenario_id,
    s.human_value_weight * p.human_value +
    s.system_leverage_weight * p.system_leverage +
    s.feasibility_weight * p.feasibility +
    s.equity_sensitivity_weight * p.equity_sensitivity +
    s.durability_weight * p.durability -
    s.risk_weight * p.risk AS system_design_value,
    (
        s.human_value_weight * p.human_value +
        s.system_leverage_weight * p.system_leverage +
        s.feasibility_weight * p.feasibility +
        s.equity_sensitivity_weight * p.equity_sensitivity +
        s.durability_weight * p.durability -
        s.risk_weight * p.risk
    ) * (0.75 + 0.25 * (0.55 * p.evidence_quality + 0.45 * p.stakeholder_coverage)) AS evidence_adjusted_value,
    (
        s.human_value_weight * p.human_value +
        s.system_leverage_weight * p.system_leverage +
        s.feasibility_weight * p.feasibility +
        s.equity_sensitivity_weight * p.equity_sensitivity +
        s.durability_weight * p.durability -
        s.risk_weight * p.risk
    ) - 0.10 * p.context_complexity - 0.08 * p.delay_sensitivity * 10.0 - 0.06 * p.burden_shift_risk AS context_adjusted_value,
    0.55 * p.evidence_quality + 0.45 * p.stakeholder_coverage AS evidence_strength,
    0.24 * p.risk +
    0.20 * (1.0 - p.evidence_quality) * 10.0 +
    0.18 * (1.0 - p.stakeholder_coverage) * 10.0 +
    0.14 * p.context_complexity +
    0.12 * p.delay_sensitivity * 10.0 +
    0.12 * p.burden_shift_risk AS learning_priority,
    0.35 * p.system_leverage +
    0.18 * p.durability +
    0.15 * p.equity_sensitivity +
    0.12 * (0.55 * p.evidence_quality + 0.45 * p.stakeholder_coverage) * 10.0 -
    0.15 * p.risk AS deep_leverage_index,
    0.45 * p.burden_shift_risk +
    0.25 * p.context_complexity +
    0.20 * p.delay_sensitivity * 10.0 -
    0.10 * p.equity_sensitivity AS burden_shift_index
FROM system_intervention_portfolio p
CROSS JOIN system_design_scenario_weights s;

DROP VIEW IF EXISTS ranked_system_design_scores;

CREATE VIEW ranked_system_design_scores AS
SELECT
    sw.scenario_name,
    p.intervention_name,
    p.intervention_type,
    p.leverage_level,
    s.system_design_value,
    s.evidence_adjusted_value,
    s.context_adjusted_value,
    s.evidence_strength,
    s.learning_priority,
    s.deep_leverage_index,
    s.burden_shift_index,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY s.system_design_value DESC
    ) AS scenario_rank
FROM system_design_scores s
JOIN system_intervention_portfolio p
    ON s.intervention_id = p.intervention_id
JOIN system_design_scenario_weights sw
    ON s.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS system_intervention_risk_priority;

CREATE VIEW system_intervention_risk_priority AS
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
FROM system_intervention_risk_register;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    intervention_name,
    intervention_type,
    leverage_level,
    ROUND(system_design_value, 3) AS system_design_value,
    ROUND(evidence_adjusted_value, 3) AS evidence_adjusted_value,
    ROUND(context_adjusted_value, 3) AS context_adjusted_value,
    ROUND(deep_leverage_index, 3) AS deep_leverage_index
FROM ranked_system_design_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    intervention_name,
    COUNT(*) AS times_ranked_first
FROM ranked_system_design_scores
WHERE scenario_rank = 1
GROUP BY intervention_name
ORDER BY times_ranked_first DESC, intervention_name;

SELECT
    intervention_name,
    ROUND(AVG(system_design_value), 3) AS average_system_design_value,
    ROUND(AVG(evidence_adjusted_value), 3) AS average_evidence_adjusted_value,
    ROUND(AVG(context_adjusted_value), 3) AS average_context_adjusted_value,
    ROUND(AVG(deep_leverage_index), 3) AS average_deep_leverage_index,
    ROUND(AVG(learning_priority), 3) AS average_learning_priority,
    ROUND(AVG(burden_shift_index), 3) AS average_burden_shift_index
FROM ranked_system_design_scores
GROUP BY intervention_name
ORDER BY average_system_design_value DESC;

SELECT
    intervention_name,
    risk_category,
    risk_description,
    risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM system_intervention_risk_priority
ORDER BY risk_priority_number DESC;
