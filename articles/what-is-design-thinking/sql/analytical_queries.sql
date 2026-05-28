-- Analytical queries for design thinking pathway evaluation.
-- Run after schema.sql:
--   sqlite3 outputs/design_thinking.db < sql/analytical_queries.sql

DELETE FROM pathway_scores;

INSERT INTO pathway_scores (
    pathway_id,
    scenario_id,
    design_value
)
SELECT
    p.pathway_id,
    s.scenario_id,
    s.human_relevance_weight * p.human_relevance +
    s.feasibility_weight * p.feasibility +
    s.learning_value_weight * p.learning_value -
    s.residual_risk_weight * p.residual_risk AS design_value
FROM design_pathways p
CROSS JOIN scenario_weights s;

DROP VIEW IF EXISTS ranked_pathway_scores;

CREATE VIEW ranked_pathway_scores AS
SELECT
    sw.scenario_name,
    dp.pathway_name,
    ps.design_value,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY ps.design_value DESC
    ) AS scenario_rank,
    dp.human_relevance,
    dp.feasibility,
    dp.learning_value,
    dp.residual_risk,
    dp.stakeholder_confidence,
    dp.evidence_quality,
    dp.implementation_complexity
FROM pathway_scores ps
JOIN design_pathways dp
    ON ps.pathway_id = dp.pathway_id
JOIN scenario_weights sw
    ON ps.scenario_id = sw.scenario_id;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    pathway_name,
    ROUND(design_value, 3) AS design_value
FROM ranked_pathway_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    pathway_name,
    COUNT(*) AS times_ranked_first
FROM ranked_pathway_scores
WHERE scenario_rank = 1
GROUP BY pathway_name
ORDER BY times_ranked_first DESC, pathway_name;

SELECT
    pathway_name,
    ROUND(AVG(design_value), 3) AS average_design_value,
    ROUND(MIN(design_value), 3) AS minimum_design_value,
    ROUND(MAX(design_value), 3) AS maximum_design_value
FROM ranked_pathway_scores
GROUP BY pathway_name
ORDER BY average_design_value DESC;
