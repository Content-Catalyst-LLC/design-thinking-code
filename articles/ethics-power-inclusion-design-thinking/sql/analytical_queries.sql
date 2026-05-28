-- Analytical queries for ethics, power, and inclusion.
-- Run after schema.sql:
--   sqlite3 outputs/ethics_power_inclusion.db < sql/schema.sql
--   sqlite3 outputs/ethics_power_inclusion.db < sql/analytical_queries.sql

DROP VIEW IF EXISTS stakeholder_scores;

CREATE VIEW stakeholder_scores AS
SELECT
    group_name,
    stakeholder_type,
    0.20 * access +
    0.20 * voice +
    0.16 * safety +
    0.14 * compensation +
    0.14 * representation +
    0.16 * accountability AS inclusion_score,
    0.18 * time_burden +
    0.22 * cognitive_burden +
    0.18 * emotional_burden +
    0.16 * documentation_burden +
    0.16 * uncertainty_burden +
    0.10 * coordination_burden AS burden_score,
    10.0 - (
        0.40 * voice +
        0.34 * accountability +
        0.16 * compensation +
        0.10 * representation
    ) AS power_gap,
    accessibility_need * (10.0 - access) AS accessibility_gap,
    0.28 * affectedness * (
        0.18 * time_burden +
        0.22 * cognitive_burden +
        0.18 * emotional_burden +
        0.16 * documentation_burden +
        0.16 * uncertainty_burden +
        0.10 * coordination_burden
    ) +
    0.24 * affectedness * (
        10.0 - (
            0.40 * voice +
            0.34 * accountability +
            0.16 * compensation +
            0.10 * representation
        )
    ) +
    0.18 * (
        10.0 - (
            0.20 * access +
            0.20 * voice +
            0.16 * safety +
            0.14 * compensation +
            0.14 * representation +
            0.16 * accountability
        )
    ) +
    0.14 * accessibility_need * (10.0 - access) +
    0.10 * (10.0 - trust_level) +
    0.06 * affectedness * emotional_burden AS ethical_attention_priority
FROM stakeholder_groups;

DROP VIEW IF EXISTS design_decision_scores;

CREATE VIEW design_decision_scores AS
SELECT
    design_decision,
    decision_type,
    harm_severity * probability * exposure * (1.0 - detectability) * (1.0 - accountability) AS ethical_risk,
    0.24 * harm_severity +
    0.16 * exposure +
    0.14 * (1.0 - detectability) +
    0.14 * (1.0 - accountability) +
    0.12 * privacy_sensitivity +
    0.10 * autonomy_risk +
    0.10 * manipulation_risk AS governance_need,
    0.32 * (
        harm_severity * probability * exposure * (1.0 - detectability) * (1.0 - accountability)
    ) +
    0.20 * harm_severity +
    0.14 * exposure +
    0.10 * (1.0 - accountability) +
    0.08 * (1.0 - detectability) +
    0.06 * (1.0 - inclusion_strength) +
    0.05 * privacy_sensitivity +
    0.03 * autonomy_risk +
    0.02 * manipulation_risk AS review_priority,
    (
        0.32 * (
            harm_severity * probability * exposure * (1.0 - detectability) * (1.0 - accountability)
        ) +
        0.20 * harm_severity +
        0.14 * exposure +
        0.10 * (1.0 - accountability) +
        0.08 * (1.0 - detectability) +
        0.06 * (1.0 - inclusion_strength) +
        0.05 * privacy_sensitivity +
        0.03 * autonomy_risk +
        0.02 * manipulation_risk
    ) - 0.12 * public_value + 0.10 * (1.0 - repairability) AS public_value_adjusted_risk
FROM ethical_design_decisions;

.headers on
.mode column

SELECT
    group_name,
    stakeholder_type,
    ROUND(inclusion_score, 3) AS inclusion_score,
    ROUND(burden_score, 3) AS burden_score,
    ROUND(power_gap, 3) AS power_gap,
    ROUND(ethical_attention_priority, 3) AS ethical_attention_priority
FROM stakeholder_scores
ORDER BY ethical_attention_priority DESC;

SELECT
    design_decision,
    decision_type,
    ROUND(ethical_risk, 4) AS ethical_risk,
    ROUND(governance_need, 4) AS governance_need,
    ROUND(public_value_adjusted_risk, 4) AS public_value_adjusted_risk
FROM design_decision_scores
ORDER BY public_value_adjusted_risk DESC;
