-- Analytical queries for problem-framing evaluation.
-- Run after schema.sql:
--   sqlite3 outputs/problem_framing.db < sql/analytical_queries.sql

DELETE FROM frame_scores;

INSERT INTO frame_scores (
    frame_id,
    scenario_id,
    frame_value,
    framing_risk_index,
    confidence_adjusted_value
)
SELECT
    f.frame_id,
    s.scenario_id,
    s.explanatory_adequacy_weight * f.explanatory_adequacy +
    s.stakeholder_coverage_weight * f.stakeholder_coverage +
    s.opportunity_value_weight * f.opportunity_value -
    s.framing_risk_weight * f.framing_risk AS frame_value,
    0.25 * f.narrowness_risk +
    0.30 * f.stakeholder_exclusion_risk +
    0.25 * f.causality_risk +
    0.20 * f.political_distortion_risk AS framing_risk_index,
    (
        s.explanatory_adequacy_weight * f.explanatory_adequacy +
        s.stakeholder_coverage_weight * f.stakeholder_coverage +
        s.opportunity_value_weight * f.opportunity_value -
        s.framing_risk_weight * f.framing_risk
    ) * (0.75 + 0.25 * (0.5 * f.evidence_quality + 0.5 * f.frame_confidence)) AS confidence_adjusted_value
FROM problem_frames f
CROSS JOIN scenario_weights s;

DROP VIEW IF EXISTS ranked_frame_scores;

CREATE VIEW ranked_frame_scores AS
SELECT
    sw.scenario_name,
    pf.frame_name,
    fs.frame_value,
    fs.framing_risk_index,
    fs.confidence_adjusted_value,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY fs.frame_value DESC
    ) AS scenario_rank,
    pf.explanatory_adequacy,
    pf.stakeholder_coverage,
    pf.opportunity_value,
    pf.framing_risk,
    pf.evidence_quality,
    pf.frame_confidence,
    pf.implementation_scope
FROM frame_scores fs
JOIN problem_frames pf
    ON fs.frame_id = pf.frame_id
JOIN scenario_weights sw
    ON fs.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS counterframe_test_priority;

CREATE VIEW counterframe_test_priority AS
SELECT
    dominant_frame,
    counterframe,
    reason_to_test,
    missing_evidence_risk,
    power_convenience_risk,
    0.55 * missing_evidence_risk +
    0.45 * power_convenience_risk AS counterframe_test_priority
FROM counterframes;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    frame_name,
    ROUND(frame_value, 3) AS frame_value,
    ROUND(framing_risk_index, 3) AS framing_risk_index,
    ROUND(confidence_adjusted_value, 3) AS confidence_adjusted_value
FROM ranked_frame_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    frame_name,
    COUNT(*) AS times_ranked_first
FROM ranked_frame_scores
WHERE scenario_rank = 1
GROUP BY frame_name
ORDER BY times_ranked_first DESC, frame_name;

SELECT
    frame_name,
    ROUND(AVG(frame_value), 3) AS average_frame_value,
    ROUND(MIN(frame_value), 3) AS minimum_frame_value,
    ROUND(MAX(frame_value), 3) AS maximum_frame_value,
    ROUND(AVG(framing_risk_index), 3) AS average_framing_risk_index
FROM ranked_frame_scores
GROUP BY frame_name
ORDER BY average_frame_value DESC;

SELECT
    dominant_frame,
    counterframe,
    ROUND(counterframe_test_priority, 3) AS counterframe_test_priority,
    reason_to_test
FROM counterframe_test_priority
ORDER BY counterframe_test_priority DESC;
