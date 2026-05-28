-- Analytical queries for iteration and experimentation evaluation.
-- Run after schema.sql:
--   sqlite3 outputs/iteration_experimentation.db < sql/analytical_queries.sql

DELETE FROM experiment_scores;

INSERT INTO experiment_scores (
    experiment_id,
    scenario_id,
    experiment_value,
    risk_index,
    confidence_adjusted_value
)
SELECT
    e.experiment_id,
    s.scenario_id,
    s.learning_gain_weight * e.learning_gain +
    s.update_flexibility_weight * e.update_flexibility +
    s.expected_improvement_weight * e.expected_improvement -
    s.residual_risk_weight * e.residual_risk AS experiment_value,
    0.30 * e.ethical_risk +
    0.25 * e.operational_risk +
    0.20 * e.interpretive_risk +
    0.25 * e.scaling_risk AS risk_index,
    (
        s.learning_gain_weight * e.learning_gain +
        s.update_flexibility_weight * e.update_flexibility +
        s.expected_improvement_weight * e.expected_improvement -
        s.residual_risk_weight * e.residual_risk
    ) * (0.75 + 0.25 * (0.5 * e.evidence_quality + 0.5 * e.team_confidence)) AS confidence_adjusted_value
FROM experiments e
CROSS JOIN scenario_weights s;

DROP VIEW IF EXISTS ranked_experiment_scores;

CREATE VIEW ranked_experiment_scores AS
SELECT
    sw.scenario_name,
    e.experiment_name,
    es.experiment_value,
    es.risk_index,
    es.confidence_adjusted_value,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY es.experiment_value DESC
    ) AS scenario_rank,
    e.learning_gain,
    e.update_flexibility,
    e.expected_improvement,
    e.residual_risk,
    e.evidence_quality,
    e.team_confidence,
    e.implementation_complexity
FROM experiment_scores es
JOIN experiments e
    ON es.experiment_id = e.experiment_id
JOIN scenario_weights sw
    ON es.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS ethics_review_priority;

CREATE VIEW ethics_review_priority AS
SELECT
    experiment_name,
    requires_informed_consent,
    participant_burden,
    privacy_sensitivity,
    power_asymmetry,
    review_priority,
    0.25 * requires_informed_consent +
    0.25 * participant_burden +
    0.25 * privacy_sensitivity +
    0.25 * power_asymmetry AS computed_review_priority,
    notes
FROM experiment_ethics_review;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    experiment_name,
    ROUND(experiment_value, 3) AS experiment_value,
    ROUND(risk_index, 3) AS risk_index,
    ROUND(confidence_adjusted_value, 3) AS confidence_adjusted_value
FROM ranked_experiment_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    experiment_name,
    COUNT(*) AS times_ranked_first
FROM ranked_experiment_scores
WHERE scenario_rank = 1
GROUP BY experiment_name
ORDER BY times_ranked_first DESC, experiment_name;

SELECT
    experiment_name,
    ROUND(AVG(experiment_value), 3) AS average_experiment_value,
    ROUND(MIN(experiment_value), 3) AS minimum_experiment_value,
    ROUND(MAX(experiment_value), 3) AS maximum_experiment_value,
    ROUND(AVG(risk_index), 3) AS average_risk_index
FROM ranked_experiment_scores
GROUP BY experiment_name
ORDER BY average_experiment_value DESC;

SELECT
    experiment_name,
    ROUND(computed_review_priority, 3) AS computed_review_priority,
    notes
FROM ethics_review_priority
ORDER BY computed_review_priority DESC;
