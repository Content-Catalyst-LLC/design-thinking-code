-- Analytical queries for co-design and participatory design.
-- Run after schema.sql:
--   sqlite3 outputs/codesign_participatory_design.db < sql/schema.sql
--   sqlite3 outputs/codesign_participatory_design.db < sql/analytical_queries.sql

DELETE FROM participation_scores;

INSERT INTO participation_scores (
    activity_id,
    scenario_id,
    participation_quality,
    affectedness_adjusted_quality,
    equity_participation_index,
    implementation_legitimacy_index,
    participatory_evidence_index,
    learning_priority,
    process_resilience
)
SELECT
    a.activity_id,
    w.scenario_id,
    w.representation_weight * a.representation +
    w.accessibility_weight * a.accessibility +
    w.participant_influence_weight * a.participant_influence +
    w.trust_quality_weight * a.trust_quality +
    w.evidence_quality_weight * a.evidence_quality +
    w.implementation_accountability_weight * a.implementation_accountability +
    w.decision_impact_weight * a.decision_impact -
    w.ethical_risk_weight * a.ethical_risk AS participation_quality,
    (
        w.representation_weight * a.representation +
        w.accessibility_weight * a.accessibility +
        w.participant_influence_weight * a.participant_influence +
        w.trust_quality_weight * a.trust_quality +
        w.evidence_quality_weight * a.evidence_quality +
        w.implementation_accountability_weight * a.implementation_accountability +
        w.decision_impact_weight * a.decision_impact -
        w.ethical_risk_weight * a.ethical_risk
    ) * (0.80 + 0.20 * a.affectedness_weight) AS affectedness_adjusted_quality,
    0.26 * a.representation +
    0.24 * a.accessibility +
    0.22 * a.participant_influence +
    0.14 * a.trust_quality +
    0.08 * a.compensation_quality +
    0.06 * a.feedback_loop_quality -
    0.10 * a.ethical_risk -
    0.08 * a.tokenism_risk AS equity_participation_index,
    0.26 * a.participant_influence +
    0.24 * a.implementation_accountability +
    0.20 * a.decision_impact +
    0.14 * a.feedback_loop_quality +
    0.10 * a.trust_quality -
    0.06 * a.tokenism_risk AS implementation_legitimacy_index,
    0.30 * a.evidence_quality +
    0.22 * a.representation +
    0.18 * a.participant_influence +
    0.16 * a.trust_quality +
    0.14 * a.feedback_loop_quality AS participatory_evidence_index,
    0.24 * a.ethical_risk +
    0.22 * a.tokenism_risk +
    0.16 * (10.0 - a.representation) +
    0.14 * (10.0 - a.participant_influence) +
    0.12 * (10.0 - a.implementation_accountability) +
    0.12 * (10.0 - a.accessibility) AS learning_priority,
    0.30 * (
        w.representation_weight * a.representation +
        w.accessibility_weight * a.accessibility +
        w.participant_influence_weight * a.participant_influence +
        w.trust_quality_weight * a.trust_quality +
        w.evidence_quality_weight * a.evidence_quality +
        w.implementation_accountability_weight * a.implementation_accountability +
        w.decision_impact_weight * a.decision_impact -
        w.ethical_risk_weight * a.ethical_risk
    ) +
    0.26 * (
        0.26 * a.participant_influence +
        0.24 * a.implementation_accountability +
        0.20 * a.decision_impact +
        0.14 * a.feedback_loop_quality +
        0.10 * a.trust_quality -
        0.06 * a.tokenism_risk
    ) +
    0.24 * (
        0.26 * a.representation +
        0.24 * a.accessibility +
        0.22 * a.participant_influence +
        0.14 * a.trust_quality +
        0.08 * a.compensation_quality +
        0.06 * a.feedback_loop_quality -
        0.10 * a.ethical_risk -
        0.08 * a.tokenism_risk
    ) +
    0.20 * (
        0.30 * a.evidence_quality +
        0.22 * a.representation +
        0.18 * a.participant_influence +
        0.16 * a.trust_quality +
        0.14 * a.feedback_loop_quality
    ) -
    0.10 * a.ethical_risk AS process_resilience
FROM codesign_activities a
CROSS JOIN participation_scenario_weights w;

DROP VIEW IF EXISTS ranked_participation_scores;

CREATE VIEW ranked_participation_scores AS
SELECT
    sw.scenario_name,
    a.activity_name,
    a.activity_type,
    a.design_stage,
    s.participation_quality,
    s.affectedness_adjusted_quality,
    s.equity_participation_index,
    s.implementation_legitimacy_index,
    s.participatory_evidence_index,
    s.learning_priority,
    s.process_resilience,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY s.participation_quality DESC
    ) AS scenario_rank
FROM participation_scores s
JOIN codesign_activities a
    ON s.activity_id = a.activity_id
JOIN participation_scenario_weights sw
    ON s.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS participant_group_gap_analysis;

CREATE VIEW participant_group_gap_analysis AS
SELECT
    group_name,
    stakeholder_type,
    affectedness,
    presence,
    0.20 * framing_influence +
    0.16 * synthesis_influence +
    0.16 * concept_influence +
    0.14 * testing_influence +
    0.18 * implementation_influence +
    0.16 * governance_influence AS stage_influence_index,
    0.34 * access_support +
    0.24 * language_access +
    0.24 * disability_access +
    0.18 * compensation_support AS accessibility_support_index,
    affectedness * (1.0 - presence) AS participation_gap,
    affectedness * presence * (
        1.0 - (
            0.20 * framing_influence +
            0.16 * synthesis_influence +
            0.16 * concept_influence +
            0.14 * testing_influence +
            0.18 * implementation_influence +
            0.16 * governance_influence
        )
    ) AS influence_gap,
    affectedness * (
        1.0 - (
            0.34 * access_support +
            0.24 * language_access +
            0.24 * disability_access +
            0.18 * compensation_support
        )
    ) AS access_gap,
    affectedness * (1.0 - trust_score) AS trust_gap
FROM participant_groups;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    activity_name,
    activity_type,
    design_stage,
    ROUND(participation_quality, 3) AS participation_quality,
    ROUND(affectedness_adjusted_quality, 3) AS affectedness_adjusted_quality,
    ROUND(equity_participation_index, 3) AS equity_participation_index,
    ROUND(implementation_legitimacy_index, 3) AS implementation_legitimacy_index
FROM ranked_participation_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    activity_name,
    COUNT(*) AS times_ranked_first
FROM ranked_participation_scores
WHERE scenario_rank = 1
GROUP BY activity_name
ORDER BY times_ranked_first DESC, activity_name;

SELECT
    group_name,
    stakeholder_type,
    ROUND(participation_gap, 3) AS participation_gap,
    ROUND(influence_gap, 3) AS influence_gap,
    ROUND(access_gap, 3) AS access_gap,
    ROUND(trust_gap, 3) AS trust_gap
FROM participant_group_gap_analysis
ORDER BY (participation_gap + influence_gap + access_gap + trust_gap) DESC;
