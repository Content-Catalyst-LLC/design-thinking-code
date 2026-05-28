-- Analytical queries for ideation portfolio evaluation.
-- Run after schema.sql:
--   sqlite3 outputs/ideation_portfolio.db < sql/analytical_queries.sql

DELETE FROM idea_scores;

INSERT INTO idea_scores (
    idea_id,
    scenario_id,
    idea_value,
    composite_risk,
    prototype_priority,
    confidence_adjusted_value
)
SELECT
    i.idea_id,
    s.scenario_id,
    s.desirability_weight * i.desirability +
    s.feasibility_weight * i.feasibility +
    s.novelty_weight * i.novelty +
    s.equity_value_weight * i.equity_value +
    s.learning_value_weight * i.learning_value -
    s.composite_risk_weight * (
        0.25 * i.residual_risk +
        0.25 * i.ethical_risk +
        0.20 * i.operational_risk +
        0.15 * i.technical_risk +
        0.15 * i.scaling_risk
    ) AS idea_value,
    0.25 * i.residual_risk +
    0.25 * i.ethical_risk +
    0.20 * i.operational_risk +
    0.15 * i.technical_risk +
    0.15 * i.scaling_risk AS composite_risk,
    0.30 * i.desirability +
    0.25 * i.learning_value +
    0.20 * i.feasibility +
    0.15 * i.equity_value -
    0.10 * (
        0.25 * i.residual_risk +
        0.25 * i.ethical_risk +
        0.20 * i.operational_risk +
        0.15 * i.technical_risk +
        0.15 * i.scaling_risk
    ) AS prototype_priority,
    (
        s.desirability_weight * i.desirability +
        s.feasibility_weight * i.feasibility +
        s.novelty_weight * i.novelty +
        s.equity_value_weight * i.equity_value +
        s.learning_value_weight * i.learning_value -
        s.composite_risk_weight * (
            0.25 * i.residual_risk +
            0.25 * i.ethical_risk +
            0.20 * i.operational_risk +
            0.15 * i.technical_risk +
            0.15 * i.scaling_risk
        )
    ) * (0.75 + 0.25 * i.evidence_quality) AS confidence_adjusted_value
FROM ideas i
CROSS JOIN scenario_weights s;

DROP VIEW IF EXISTS ranked_idea_scores;

CREATE VIEW ranked_idea_scores AS
SELECT
    sw.scenario_name,
    i.idea_name,
    i.idea_cluster,
    isc.idea_value,
    isc.composite_risk,
    isc.prototype_priority,
    isc.confidence_adjusted_value,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY isc.idea_value DESC
    ) AS scenario_rank,
    i.desirability,
    i.feasibility,
    i.novelty,
    i.equity_value,
    i.learning_value,
    i.evidence_quality,
    i.prototype_testability,
    i.implementation_relevance
FROM idea_scores isc
JOIN ideas i
    ON isc.idea_id = i.idea_id
JOIN scenario_weights sw
    ON isc.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS idea_review_priority;

CREATE VIEW idea_review_priority AS
SELECT
    idea_name,
    idea_cluster,
    0.25 * residual_risk +
    0.25 * ethical_risk +
    0.20 * operational_risk +
    0.15 * technical_risk +
    0.15 * scaling_risk AS composite_risk,
    ethical_risk,
    scaling_risk,
    0.30 * (
        0.25 * residual_risk +
        0.25 * ethical_risk +
        0.20 * operational_risk +
        0.15 * technical_risk +
        0.15 * scaling_risk
    ) +
    0.20 * (10.0 - feasibility) +
    0.20 * (10.0 - evidence_quality * 10.0) +
    0.15 * ethical_risk +
    0.15 * scaling_risk AS review_priority
FROM ideas;

DROP VIEW IF EXISTS idea_cluster_breadth;

CREATE VIEW idea_cluster_breadth AS
SELECT
    idea_cluster,
    COUNT(*) AS idea_count,
    AVG(cluster_distance) AS mean_cluster_distance,
    MAX(stakeholder_groups) AS stakeholder_groups,
    MAX(methods_supporting) AS methods_supporting,
    SUM(evidence_source_count) AS evidence_source_count
FROM idea_cluster_map
GROUP BY idea_cluster;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    idea_name,
    idea_cluster,
    ROUND(idea_value, 3) AS idea_value,
    ROUND(composite_risk, 3) AS composite_risk,
    ROUND(prototype_priority, 3) AS prototype_priority
FROM ranked_idea_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    idea_name,
    COUNT(*) AS times_ranked_first
FROM ranked_idea_scores
WHERE scenario_rank = 1
GROUP BY idea_name
ORDER BY times_ranked_first DESC, idea_name;

SELECT
    idea_name,
    ROUND(AVG(idea_value), 3) AS average_idea_value,
    ROUND(MIN(idea_value), 3) AS minimum_idea_value,
    ROUND(MAX(idea_value), 3) AS maximum_idea_value,
    ROUND(AVG(composite_risk), 3) AS average_composite_risk
FROM ranked_idea_scores
GROUP BY idea_name
ORDER BY average_idea_value DESC;

SELECT
    idea_cluster,
    idea_count,
    ROUND(mean_cluster_distance, 3) AS mean_cluster_distance,
    stakeholder_groups,
    methods_supporting,
    evidence_source_count
FROM idea_cluster_breadth
ORDER BY idea_count DESC, evidence_source_count DESC;

SELECT
    idea_name,
    idea_cluster,
    ROUND(review_priority, 3) AS review_priority,
    ROUND(composite_risk, 3) AS composite_risk,
    ROUND(ethical_risk, 3) AS ethical_risk,
    ROUND(scaling_risk, 3) AS scaling_risk
FROM idea_review_priority
ORDER BY review_priority DESC;
