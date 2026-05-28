-- Analytical queries for design-thinking strategy.
-- Run after schema.sql:
--   sqlite3 outputs/strategy_design.db < sql/schema.sql
--   sqlite3 outputs/strategy_design.db < sql/analytical_queries.sql

DELETE FROM strategy_option_scores;

INSERT INTO strategy_option_scores (
    option_id,
    scenario_id,
    strategic_score,
    portfolio_value,
    uncertainty_priority,
    implementation_readiness,
    ethical_public_value_index
)
SELECT
    o.option_id,
    w.scenario_id,
    w.desirability_weight * o.desirability +
    w.feasibility_weight * o.feasibility +
    w.viability_weight * o.viability +
    w.strategic_alignment_weight * o.strategic_alignment +
    w.ethical_quality_weight * o.ethical_quality +
    w.learning_value_weight * o.learning_value +
    w.public_value_weight * o.public_value +
    w.evidence_strength_weight * o.evidence_strength * 10.0 -
    w.strategic_risk_weight * o.strategic_risk -
    w.implementation_effort_weight * o.implementation_effort -
    w.capability_gap_weight * o.capability_gap -
    w.time_to_learn_weight * o.time_to_learn AS strategic_score,
    (
      w.desirability_weight * o.desirability +
      w.feasibility_weight * o.feasibility +
      w.viability_weight * o.viability +
      w.strategic_alignment_weight * o.strategic_alignment +
      w.ethical_quality_weight * o.ethical_quality +
      w.learning_value_weight * o.learning_value +
      w.public_value_weight * o.public_value +
      w.evidence_strength_weight * o.evidence_strength * 10.0 -
      w.strategic_risk_weight * o.strategic_risk -
      w.implementation_effort_weight * o.implementation_effort -
      w.capability_gap_weight * o.capability_gap -
      w.time_to_learn_weight * o.time_to_learn
    ) +
    0.30 * o.learning_value +
    0.20 * o.public_value +
    0.15 * o.evidence_strength * 10.0 -
    0.22 * o.strategic_risk -
    0.14 * o.implementation_effort -
    0.10 * o.capability_gap AS portfolio_value,
    0.26 * o.strategic_risk +
    0.22 * o.learning_value +
    0.16 * o.implementation_effort +
    0.14 * o.capability_gap +
    0.12 * (10.0 - o.feasibility) +
    0.10 * (1.0 - o.evidence_strength) * 10.0 AS uncertainty_priority,
    0.28 * o.feasibility +
    0.24 * o.viability +
    0.20 * (10.0 - o.implementation_effort) +
    0.16 * (10.0 - o.capability_gap) +
    0.12 * o.evidence_strength * 10.0 AS implementation_readiness,
    0.42 * o.ethical_quality +
    0.38 * o.public_value +
    0.12 * o.strategic_alignment -
    0.08 * o.strategic_risk AS ethical_public_value_index
FROM strategic_options o
CROSS JOIN strategy_scenario_weights w;

DROP VIEW IF EXISTS ranked_strategy_options;

CREATE VIEW ranked_strategy_options AS
SELECT
    w.scenario_name,
    o.option_name,
    o.option_type,
    o.strategic_hypothesis,
    s.strategic_score,
    s.portfolio_value,
    s.uncertainty_priority,
    s.implementation_readiness,
    s.ethical_public_value_index,
    RANK() OVER (
        PARTITION BY w.scenario_name
        ORDER BY s.strategic_score DESC
    ) AS scenario_rank
FROM strategy_option_scores s
JOIN strategic_options o
    ON s.option_id = o.option_id
JOIN strategy_scenario_weights w
    ON s.scenario_id = w.scenario_id;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    option_name,
    option_type,
    ROUND(strategic_score, 3) AS strategic_score,
    ROUND(portfolio_value, 3) AS portfolio_value,
    ROUND(implementation_readiness, 3) AS implementation_readiness,
    ROUND(ethical_public_value_index, 3) AS ethical_public_value_index
FROM ranked_strategy_options
ORDER BY scenario_name, scenario_rank;

SELECT
    option_name,
    COUNT(*) AS times_ranked_first
FROM ranked_strategy_options
WHERE scenario_rank = 1
GROUP BY option_name
ORDER BY times_ranked_first DESC, option_name;
