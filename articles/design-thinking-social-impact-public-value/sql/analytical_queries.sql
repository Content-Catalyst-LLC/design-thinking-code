-- Analytical queries for social-impact public-value analysis.
-- Run after schema.sql:
--   sqlite3 outputs/public_value_impact.db < sql/schema.sql
--   sqlite3 outputs/public_value_impact.db < sql/analytical_queries.sql

DROP VIEW IF EXISTS social_impact_scores;

CREATE VIEW social_impact_scores AS
SELECT
    intervention_name,
    intervention_type,
    0.13 * access +
    0.15 * equity +
    0.12 * dignity +
    0.12 * legitimacy +
    0.13 * accountability +
    0.11 * outcome_strength +
    0.08 * sustainability +
    0.07 * learning_capacity +
    0.05 * community_defined_value +
    0.04 * repair_capacity AS public_value_score,
    0.24 * implementation_risk +
    0.22 * burden_risk +
    0.16 * (10.0 - governance_strength) +
    0.12 * (10.0 - sustainability) +
    0.10 * (10.0 - learning_capacity) +
    0.08 * (10.0 - repair_capacity) +
    0.08 * (10.0 - stewardship_capacity) AS stewardship_need,
    access,
    equity,
    dignity,
    legitimacy,
    accountability,
    governance_strength,
    implementation_risk,
    burden_risk,
    participation_quality
FROM social_impact_interventions;

DROP VIEW IF EXISTS stakeholder_burden_scores;

CREATE VIEW stakeholder_burden_scores AS
SELECT
    stakeholder_group,
    stakeholder_type,
    0.20 * baseline_time_burden +
    0.22 * baseline_cognitive_burden +
    0.20 * baseline_emotional_burden +
    0.20 * baseline_documentation_burden +
    0.18 * baseline_uncertainty_burden AS baseline_burden,
    0.20 * post_time_burden +
    0.22 * post_cognitive_burden +
    0.20 * post_emotional_burden +
    0.20 * post_documentation_burden +
    0.18 * post_uncertainty_burden AS post_burden,
    10.0 - (0.40 * voice + 0.36 * influence + 0.24 * repair_access) AS power_gap,
    accessibility_need
FROM stakeholder_burden_public_value;

.headers on
.mode column

SELECT
    intervention_name,
    intervention_type,
    ROUND(public_value_score, 3) AS public_value_score,
    ROUND(
      0.30 * public_value_score +
      0.17 * feasibility +
      0.16 * governance_strength +
      0.12 * learning_capacity +
      0.10 * participation_quality +
      0.08 * stewardship_capacity +
      0.07 * repair_capacity -
      0.07 * implementation_risk -
      0.07 * burden_risk,
      3
    ) AS impact_readiness,
    ROUND(stewardship_need, 3) AS stewardship_need
FROM social_impact_scores
JOIN social_impact_interventions USING (intervention_name)
ORDER BY public_value_score DESC;

SELECT
    stakeholder_group,
    stakeholder_type,
    ROUND(baseline_burden, 3) AS baseline_burden,
    ROUND(post_burden, 3) AS post_burden,
    ROUND(baseline_burden - post_burden, 3) AS burden_reduction,
    ROUND(power_gap, 3) AS power_gap,
    ROUND(accessibility_need * baseline_burden, 3) AS accessibility_burden
FROM stakeholder_burden_scores
ORDER BY baseline_burden + power_gap DESC;
