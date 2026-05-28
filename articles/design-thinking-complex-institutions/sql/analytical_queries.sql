-- Analytical queries for institutional design-thinking analysis.
-- Run after schema.sql:
--   sqlite3 outputs/institutional_design.db < sql/schema.sql
--   sqlite3 outputs/institutional_design.db < sql/analytical_queries.sql

DROP VIEW IF EXISTS institutional_design_scores;

CREATE VIEW institutional_design_scores AS
SELECT
    option_name,
    option_type,
    0.14 * desirability +
    0.13 * authority +
    0.12 * capability +
    0.10 * funding +
    0.10 * policy_fit +
    0.11 * governance_strength +
    0.08 * trust_gain +
    0.08 * burden_reduction +
    0.06 * data_readiness +
    0.05 * frontline_fit +
    0.03 * maintenance_capacity -
    0.05 * coordination_complexity -
    0.05 * implementation_risk AS change_readiness,
    0.18 * authority +
    0.18 * capability +
    0.14 * funding +
    0.14 * governance_strength +
    0.12 * policy_fit +
    0.10 * frontline_fit +
    0.08 * maintenance_capacity +
    0.06 * data_readiness AS absorption_capacity,
    0.24 * public_value +
    0.20 * burden_reduction +
    0.18 * trust_gain +
    0.16 * equity_priority +
    0.12 * desirability +
    0.10 * policy_fit -
    0.08 * implementation_risk AS public_value_priority,
    0.28 * coordination_complexity +
    0.24 * implementation_risk +
    0.14 * (10.0 - authority) +
    0.12 * (10.0 - capability) +
    0.10 * (10.0 - funding) +
    0.07 * (10.0 - maintenance_capacity) +
    0.05 * (10.0 - data_readiness) AS sequencing_need
FROM institutional_design_options;

DROP VIEW IF EXISTS stakeholder_burden_scores;

CREATE VIEW stakeholder_burden_scores AS
SELECT
    stakeholder_group,
    stakeholder_type,
    0.18 * time_burden +
    0.20 * cognitive_burden +
    0.17 * emotional_burden +
    0.17 * documentation_burden +
    0.16 * uncertainty_burden +
    0.12 * coordination_burden AS burden_score,
    10.0 - (0.40 * voice + 0.36 * influence + 0.24 * repair_access) AS power_gap,
    accessibility_need * (
        0.18 * time_burden +
        0.20 * cognitive_burden +
        0.17 * emotional_burden +
        0.17 * documentation_burden +
        0.16 * uncertainty_burden +
        0.12 * coordination_burden
    ) AS accessibility_burden
FROM stakeholder_burden;

.headers on
.mode column

SELECT
    option_name,
    option_type,
    ROUND(change_readiness, 3) AS change_readiness,
    ROUND(absorption_capacity, 3) AS absorption_capacity,
    ROUND(public_value_priority, 3) AS public_value_priority,
    ROUND(sequencing_need, 3) AS sequencing_need,
    ROUND(
        0.30 * change_readiness +
        0.26 * public_value_priority +
        0.20 * absorption_capacity -
        0.12 * sequencing_need,
        3
    ) AS simplified_portfolio_score
FROM institutional_design_scores
ORDER BY simplified_portfolio_score DESC;

SELECT
    stakeholder_group,
    stakeholder_type,
    ROUND(burden_score, 3) AS burden_score,
    ROUND(power_gap, 3) AS power_gap,
    ROUND(accessibility_burden, 3) AS accessibility_burden
FROM stakeholder_burden_scores
ORDER BY burden_score + power_gap DESC;
