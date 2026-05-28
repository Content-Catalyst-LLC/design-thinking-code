-- Analytical queries for human-centered design option evaluation.
-- Run after schema.sql:
--   sqlite3 outputs/human_centered_problem_solving.db < sql/analytical_queries.sql

DELETE FROM option_scores;

INSERT INTO option_scores (
    option_id,
    scenario_id,
    hc_value,
    burden_index,
    confidence_adjusted_value
)
SELECT
    o.option_id,
    s.scenario_id,
    s.human_benefit_weight * o.human_benefit +
    s.usability_weight * o.usability +
    s.stakeholder_fit_weight * o.stakeholder_fit -
    s.burden_weight * o.burden AS hc_value,
    0.25 * o.learning_cost +
    0.30 * o.compliance_cost +
    0.25 * o.psychological_cost +
    0.20 * o.access_cost AS burden_index,
    (
        s.human_benefit_weight * o.human_benefit +
        s.usability_weight * o.usability +
        s.stakeholder_fit_weight * o.stakeholder_fit -
        s.burden_weight * o.burden
    ) * (0.75 + 0.25 * (0.5 * o.evidence_quality + 0.5 * o.stakeholder_confidence)) AS confidence_adjusted_value
FROM human_centered_options o
CROSS JOIN scenario_weights s;

DROP VIEW IF EXISTS ranked_option_scores;

CREATE VIEW ranked_option_scores AS
SELECT
    sw.scenario_name,
    hco.option_name,
    os.hc_value,
    os.burden_index,
    os.confidence_adjusted_value,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY os.hc_value DESC
    ) AS scenario_rank,
    hco.human_benefit,
    hco.usability,
    hco.stakeholder_fit,
    hco.burden,
    hco.evidence_quality,
    hco.stakeholder_confidence,
    hco.implementation_complexity
FROM option_scores os
JOIN human_centered_options hco
    ON os.option_id = hco.option_id
JOIN scenario_weights sw
    ON os.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS stakeholder_exclusion_risk;

CREATE VIEW stakeholder_exclusion_risk AS
SELECT
    stakeholder_group,
    visibility_to_institution,
    power_to_influence_design,
    burden_exposure,
    access_risk,
    1.0 - visibility_to_institution AS invisibility_risk,
    1.0 - power_to_influence_design AS power_gap,
    0.30 * (1.0 - visibility_to_institution) +
    0.25 * (1.0 - power_to_influence_design) +
    0.25 * burden_exposure +
    0.20 * access_risk AS human_centered_exclusion_risk,
    notes
FROM stakeholder_groups;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    option_name,
    ROUND(hc_value, 3) AS hc_value,
    ROUND(burden_index, 3) AS burden_index,
    ROUND(confidence_adjusted_value, 3) AS confidence_adjusted_value
FROM ranked_option_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    option_name,
    COUNT(*) AS times_ranked_first
FROM ranked_option_scores
WHERE scenario_rank = 1
GROUP BY option_name
ORDER BY times_ranked_first DESC, option_name;

SELECT
    option_name,
    ROUND(AVG(hc_value), 3) AS average_hc_value,
    ROUND(MIN(hc_value), 3) AS minimum_hc_value,
    ROUND(MAX(hc_value), 3) AS maximum_hc_value,
    ROUND(AVG(burden_index), 3) AS average_burden_index
FROM ranked_option_scores
GROUP BY option_name
ORDER BY average_hc_value DESC;

SELECT
    stakeholder_group,
    ROUND(human_centered_exclusion_risk, 3) AS human_centered_exclusion_risk,
    notes
FROM stakeholder_exclusion_risk
ORDER BY human_centered_exclusion_risk DESC;
