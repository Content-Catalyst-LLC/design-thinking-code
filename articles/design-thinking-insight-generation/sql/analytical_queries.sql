-- Analytical queries for insight-generation evaluation.
-- Run after schema.sql:
--   sqlite3 outputs/insight_generation.db < sql/analytical_queries.sql

DELETE FROM insight_scores;

INSERT INTO insight_scores (
    insight_id,
    scenario_id,
    insight_value,
    interpretive_risk_index,
    confidence_adjusted_value
)
SELECT
    i.insight_id,
    s.scenario_id,
    s.pattern_support_weight * i.pattern_support +
    s.explanatory_depth_weight * i.explanatory_depth +
    s.opportunity_value_weight * i.opportunity_value -
    s.interpretive_risk_weight * i.interpretive_risk AS insight_value,
    0.30 * i.sampling_risk +
    0.25 * i.confirmation_bias_risk +
    0.25 * i.evidence_thinness_risk +
    0.20 * i.solution_capture_risk AS interpretive_risk_index,
    (
        s.pattern_support_weight * i.pattern_support +
        s.explanatory_depth_weight * i.explanatory_depth +
        s.opportunity_value_weight * i.opportunity_value -
        s.interpretive_risk_weight * i.interpretive_risk
    ) * (0.75 + 0.25 * (0.5 * i.evidence_quality + 0.5 * i.stakeholder_diversity)) AS confidence_adjusted_value
FROM candidate_insights i
CROSS JOIN scenario_weights s;

DROP VIEW IF EXISTS ranked_insight_scores;

CREATE VIEW ranked_insight_scores AS
SELECT
    sw.scenario_name,
    ci.insight_text,
    isc.insight_value,
    isc.interpretive_risk_index,
    isc.confidence_adjusted_value,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY isc.insight_value DESC
    ) AS scenario_rank,
    ci.pattern_support,
    ci.explanatory_depth,
    ci.opportunity_value,
    ci.interpretive_risk,
    ci.evidence_quality,
    ci.stakeholder_diversity,
    ci.prototype_testability,
    ci.implementation_relevance
FROM insight_scores isc
JOIN candidate_insights ci
    ON isc.insight_id = ci.insight_id
JOIN scenario_weights sw
    ON isc.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS insight_interpretation_review_priority;

CREATE VIEW insight_interpretation_review_priority AS
SELECT
    insight_text,
    pattern_support,
    explanatory_depth,
    opportunity_value,
    0.30 * sampling_risk +
    0.25 * confirmation_bias_risk +
    0.25 * evidence_thinness_risk +
    0.20 * solution_capture_risk AS interpretive_risk_index,
    0.35 * (
        0.30 * sampling_risk +
        0.25 * confirmation_bias_risk +
        0.25 * evidence_thinness_risk +
        0.20 * solution_capture_risk
    ) +
    0.25 * (10.0 - pattern_support) +
    0.20 * (10.0 - explanatory_depth) +
    0.20 * (10.0 - opportunity_value) AS interpretation_review_priority
FROM candidate_insights;

DROP VIEW IF EXISTS evidence_validation_priority;

CREATE VIEW evidence_validation_priority AS
SELECT
    insight_text,
    evidence_source_count,
    stakeholder_groups,
    method_count,
    contradictory_cases,
    validation_priority,
    0.30 * validation_priority +
    0.20 * MIN(contradictory_cases / 5.0, 1.0) +
    0.20 * (1.0 - MIN(evidence_source_count / 25.0, 1.0)) +
    0.15 * (1.0 - MIN(stakeholder_groups / 6.0, 1.0)) +
    0.15 * (1.0 - MIN(method_count / 5.0, 1.0)) AS computed_validation_priority,
    notes
FROM insight_evidence_sources;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    insight_text,
    ROUND(insight_value, 3) AS insight_value,
    ROUND(interpretive_risk_index, 3) AS interpretive_risk_index,
    ROUND(confidence_adjusted_value, 3) AS confidence_adjusted_value
FROM ranked_insight_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    insight_text,
    COUNT(*) AS times_ranked_first
FROM ranked_insight_scores
WHERE scenario_rank = 1
GROUP BY insight_text
ORDER BY times_ranked_first DESC, insight_text;

SELECT
    insight_text,
    ROUND(AVG(insight_value), 3) AS average_insight_value,
    ROUND(MIN(insight_value), 3) AS minimum_insight_value,
    ROUND(MAX(insight_value), 3) AS maximum_insight_value,
    ROUND(AVG(interpretive_risk_index), 3) AS average_interpretive_risk_index
FROM ranked_insight_scores
GROUP BY insight_text
ORDER BY average_insight_value DESC;

SELECT
    insight_text,
    ROUND(interpretation_review_priority, 3) AS interpretation_review_priority,
    ROUND(interpretive_risk_index, 3) AS interpretive_risk_index
FROM insight_interpretation_review_priority
ORDER BY interpretation_review_priority DESC;

SELECT
    insight_text,
    ROUND(computed_validation_priority, 3) AS computed_validation_priority,
    notes
FROM evidence_validation_priority
ORDER BY computed_validation_priority DESC;
