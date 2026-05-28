-- Analytical queries for service design.
-- Run after schema.sql:
--   sqlite3 outputs/service_design.db < sql/schema.sql
--   sqlite3 outputs/service_design.db < sql/analytical_queries.sql

DELETE FROM service_stage_scores;

INSERT INTO service_stage_scores (
    stage_id,
    scenario_id,
    service_stage_quality,
    failure_risk,
    burden_risk,
    operational_friction_index,
    procedural_dignity_index,
    redesign_priority,
    service_resilience
)
SELECT
    s.stage_id,
    w.scenario_id,
    w.completion_probability_weight * s.completion_probability * 10.0 +
    w.clarity_weight * s.clarity +
    w.trust_weight * s.trust +
    w.accessibility_weight * s.accessibility +
    w.recovery_quality_weight * s.recovery_quality -
    w.user_burden_weight * s.user_burden -
    w.staff_load_weight * s.staff_load AS service_stage_quality,
    1.0 - s.completion_probability AS failure_risk,
    0.55 * s.user_burden + 0.45 * s.staff_load AS burden_risk,
    0.22 * s.policy_complexity +
    0.22 * s.data_dependency +
    0.20 * s.staff_load +
    0.18 * (10.0 - s.backstage_readiness) +
    0.18 * (1.0 - s.completion_probability) * 10.0 AS operational_friction_index,
    0.26 * s.clarity +
    0.24 * s.trust +
    0.20 * s.accessibility +
    0.18 * s.recovery_quality -
    0.12 * s.user_burden AS procedural_dignity_index,
    0.30 * (1.0 - s.completion_probability) * 10.0 +
    0.22 * (0.55 * s.user_burden + 0.45 * s.staff_load) +
    0.16 * (10.0 - s.clarity) +
    0.12 * (10.0 - s.accessibility) +
    0.10 * (10.0 - s.recovery_quality) +
    0.10 * (
        0.22 * s.policy_complexity +
        0.22 * s.data_dependency +
        0.20 * s.staff_load +
        0.18 * (10.0 - s.backstage_readiness) +
        0.18 * (1.0 - s.completion_probability) * 10.0
    ) AS redesign_priority,
    0.30 * (
        w.completion_probability_weight * s.completion_probability * 10.0 +
        w.clarity_weight * s.clarity +
        w.trust_weight * s.trust +
        w.accessibility_weight * s.accessibility +
        w.recovery_quality_weight * s.recovery_quality -
        w.user_burden_weight * s.user_burden -
        w.staff_load_weight * s.staff_load
    ) +
    0.25 * s.backstage_readiness +
    0.20 * s.recovery_quality +
    0.15 * (
        0.26 * s.clarity +
        0.24 * s.trust +
        0.20 * s.accessibility +
        0.18 * s.recovery_quality -
        0.12 * s.user_burden
    ) -
    0.10 * (
        0.22 * s.policy_complexity +
        0.22 * s.data_dependency +
        0.20 * s.staff_load +
        0.18 * (10.0 - s.backstage_readiness) +
        0.18 * (1.0 - s.completion_probability) * 10.0
    ) AS service_resilience
FROM service_journey_stages s
CROSS JOIN service_scenario_weights w;

DROP VIEW IF EXISTS ranked_service_stage_scores;

CREATE VIEW ranked_service_stage_scores AS
SELECT
    w.scenario_name,
    s.stage_name,
    s.stage_order,
    s.channel,
    ss.service_stage_quality,
    ss.failure_risk,
    ss.burden_risk,
    ss.operational_friction_index,
    ss.procedural_dignity_index,
    ss.redesign_priority,
    ss.service_resilience,
    RANK() OVER (
        PARTITION BY w.scenario_name
        ORDER BY ss.redesign_priority DESC
    ) AS redesign_rank
FROM service_stage_scores ss
JOIN service_journey_stages s
    ON ss.stage_id = s.stage_id
JOIN service_scenario_weights w
    ON ss.scenario_id = w.scenario_id;

.headers on
.mode column

SELECT
    scenario_name,
    redesign_rank,
    stage_name,
    channel,
    ROUND(service_stage_quality, 3) AS service_stage_quality,
    ROUND(redesign_priority, 3) AS redesign_priority,
    ROUND(operational_friction_index, 3) AS operational_friction_index,
    ROUND(procedural_dignity_index, 3) AS procedural_dignity_index
FROM ranked_service_stage_scores
ORDER BY scenario_name, redesign_rank;

SELECT
    EXP(SUM(LOG(completion_probability))) AS end_to_end_reliability
FROM service_journey_stages;

SELECT
    stage_name,
    COUNT(*) AS times_highest_priority
FROM ranked_service_stage_scores
WHERE redesign_rank = 1
GROUP BY stage_name
ORDER BY times_highest_priority DESC, stage_name;
