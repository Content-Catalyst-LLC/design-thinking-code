-- Analytical queries for design thinking in public policy.
-- Run after schema.sql:
--   sqlite3 outputs/public_policy_design.db < sql/schema.sql
--   sqlite3 outputs/public_policy_design.db < sql/analytical_queries.sql

DELETE FROM policy_scores;

INSERT INTO policy_scores (
    pilot_id,
    scenario_id,
    policy_value,
    evidence_adjusted_value,
    evidence_strength,
    implementation_readiness,
    public_legitimacy_index,
    equity_access_index,
    learning_priority,
    policy_resilience
)
SELECT
    p.pilot_id,
    w.scenario_id,
    w.accessibility_weight * p.accessibility +
    w.feasibility_weight * p.feasibility +
    w.legitimacy_weight * p.legitimacy +
    w.equity_weight * p.equity +
    w.burden_reduction_weight * p.burden_reduction +
    w.durability_weight * p.durability -
    w.risk_weight * p.risk AS policy_value,
    (
        w.accessibility_weight * p.accessibility +
        w.feasibility_weight * p.feasibility +
        w.legitimacy_weight * p.legitimacy +
        w.equity_weight * p.equity +
        w.burden_reduction_weight * p.burden_reduction +
        w.durability_weight * p.durability -
        w.risk_weight * p.risk
    ) * (
        0.75 + 0.25 * (
            0.40 * p.evidence_quality +
            0.35 * p.stakeholder_coverage +
            0.25 * p.participation_quality
        )
    ) AS evidence_adjusted_value,
    0.40 * p.evidence_quality +
    0.35 * p.stakeholder_coverage +
    0.25 * p.participation_quality AS evidence_strength,
    0.28 * p.feasibility +
    0.22 * p.durability +
    0.18 * (
        0.40 * p.evidence_quality +
        0.35 * p.stakeholder_coverage +
        0.25 * p.participation_quality
    ) * 10.0 +
    0.16 * p.accessibility +
    0.16 * p.legitimacy -
    0.12 * p.legal_complexity -
    0.12 * p.implementation_complexity AS implementation_readiness,
    0.35 * p.legitimacy +
    0.25 * p.participation_quality * 10.0 +
    0.20 * p.stakeholder_coverage * 10.0 +
    0.20 * p.equity -
    0.10 * p.risk AS public_legitimacy_index,
    0.35 * p.equity +
    0.25 * p.accessibility +
    0.20 * p.burden_reduction +
    0.20 * p.stakeholder_coverage * 10.0 -
    0.10 * p.legal_complexity AS equity_access_index,
    0.20 * p.risk +
    0.18 * p.legal_complexity +
    0.18 * p.implementation_complexity +
    0.16 * (1.0 - p.evidence_quality) * 10.0 +
    0.14 * (1.0 - p.stakeholder_coverage) * 10.0 +
    0.14 * (1.0 - p.participation_quality) * 10.0 AS learning_priority,
    0.28 * (
        0.28 * p.feasibility +
        0.22 * p.durability +
        0.18 * (
            0.40 * p.evidence_quality +
            0.35 * p.stakeholder_coverage +
            0.25 * p.participation_quality
        ) * 10.0 +
        0.16 * p.accessibility +
        0.16 * p.legitimacy -
        0.12 * p.legal_complexity -
        0.12 * p.implementation_complexity
    ) +
    0.26 * (
        0.35 * p.legitimacy +
        0.25 * p.participation_quality * 10.0 +
        0.20 * p.stakeholder_coverage * 10.0 +
        0.20 * p.equity -
        0.10 * p.risk
    ) +
    0.24 * (
        0.35 * p.equity +
        0.25 * p.accessibility +
        0.20 * p.burden_reduction +
        0.20 * p.stakeholder_coverage * 10.0 -
        0.10 * p.legal_complexity
    ) +
    0.22 * p.durability -
    0.15 * p.risk AS policy_resilience
FROM public_policy_pilots p
CROSS JOIN public_policy_scenario_weights w;

DROP VIEW IF EXISTS ranked_policy_scores;

CREATE VIEW ranked_policy_scores AS
SELECT
    sw.scenario_name,
    p.pilot_name,
    p.policy_domain,
    p.pilot_type,
    s.policy_value,
    s.evidence_adjusted_value,
    s.evidence_strength,
    s.implementation_readiness,
    s.public_legitimacy_index,
    s.equity_access_index,
    s.learning_priority,
    s.policy_resilience,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY s.policy_value DESC
    ) AS scenario_rank
FROM policy_scores s
JOIN public_policy_pilots p
    ON s.pilot_id = p.pilot_id
JOIN public_policy_scenario_weights sw
    ON s.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS policy_risk_priority;

CREATE VIEW policy_risk_priority AS
SELECT
    pilot_name,
    risk_category,
    risk_description,
    severity,
    likelihood,
    detectability,
    severity * likelihood * detectability AS risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM public_policy_risk_register;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    pilot_name,
    policy_domain,
    pilot_type,
    ROUND(policy_value, 3) AS policy_value,
    ROUND(evidence_adjusted_value, 3) AS evidence_adjusted_value,
    ROUND(public_legitimacy_index, 3) AS public_legitimacy_index,
    ROUND(equity_access_index, 3) AS equity_access_index
FROM ranked_policy_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    pilot_name,
    COUNT(*) AS times_ranked_first
FROM ranked_policy_scores
WHERE scenario_rank = 1
GROUP BY pilot_name
ORDER BY times_ranked_first DESC, pilot_name;

SELECT
    pilot_name,
    ROUND(AVG(policy_value), 3) AS average_policy_value,
    ROUND(AVG(evidence_adjusted_value), 3) AS average_evidence_adjusted_value,
    ROUND(AVG(implementation_readiness), 3) AS average_implementation_readiness,
    ROUND(AVG(public_legitimacy_index), 3) AS average_public_legitimacy_index,
    ROUND(AVG(equity_access_index), 3) AS average_equity_access_index,
    ROUND(AVG(learning_priority), 3) AS average_learning_priority
FROM ranked_policy_scores
GROUP BY pilot_name
ORDER BY average_policy_value DESC;

SELECT
    pilot_name,
    risk_category,
    risk_description,
    risk_priority_number,
    mitigation_owner,
    mitigation_status
FROM policy_risk_priority
ORDER BY risk_priority_number DESC;
