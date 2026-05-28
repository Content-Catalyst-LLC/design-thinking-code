-- Analytical queries for contextual inquiry and synthesis.
-- Run after schema.sql:
--   sqlite3 outputs/contextual_inquiry_synthesis.db < sql/analytical_queries.sql

DELETE FROM theme_scores;

INSERT INTO theme_scores (
    scenario_id,
    primary_theme,
    evidence_units,
    stakeholder_groups,
    methods,
    mean_evidence_strength,
    mean_interpretive_risk,
    synthesis_confidence,
    validation_priority
)
WITH theme_base AS (
    SELECT
        primary_theme,
        COUNT(*) AS evidence_units,
        COUNT(DISTINCT participant_group) AS stakeholder_groups,
        COUNT(DISTINCT method) AS methods,
        AVG(evidence_strength) AS mean_evidence_strength,
        AVG(interpretive_risk) AS mean_interpretive_risk
    FROM evidence_units
    GROUP BY primary_theme
),
scored AS (
    SELECT
        sw.scenario_id,
        tb.primary_theme,
        tb.evidence_units,
        tb.stakeholder_groups,
        tb.methods,
        tb.mean_evidence_strength,
        tb.mean_interpretive_risk,
        sw.evidence_strength_weight * tb.mean_evidence_strength +
        sw.stakeholder_coverage_weight * tb.stakeholder_groups +
        sw.method_triangulation_weight * tb.methods -
        sw.interpretive_risk_weight * tb.mean_interpretive_risk AS synthesis_confidence,
        0.35 * tb.mean_interpretive_risk +
        0.25 * (10.0 - tb.mean_evidence_strength) +
        0.20 * (6.0 - tb.stakeholder_groups) +
        0.20 * (5.0 - tb.methods) AS validation_priority
    FROM theme_base tb
    CROSS JOIN synthesis_scenario_weights sw
)
SELECT * FROM scored;

DROP VIEW IF EXISTS ranked_theme_scores;

CREATE VIEW ranked_theme_scores AS
SELECT
    sw.scenario_name,
    ts.primary_theme,
    ts.evidence_units,
    ts.stakeholder_groups,
    ts.methods,
    ts.mean_evidence_strength,
    ts.mean_interpretive_risk,
    ts.synthesis_confidence,
    ts.validation_priority,
    RANK() OVER (
        PARTITION BY sw.scenario_name
        ORDER BY ts.synthesis_confidence DESC
    ) AS scenario_rank
FROM theme_scores ts
JOIN synthesis_scenario_weights sw
    ON ts.scenario_id = sw.scenario_id;

DROP VIEW IF EXISTS theme_network_edges;

CREATE VIEW theme_network_edges AS
SELECT
    primary_theme AS source,
    secondary_theme AS target,
    COUNT(*) AS weight
FROM evidence_units
WHERE primary_theme != secondary_theme
GROUP BY primary_theme, secondary_theme
ORDER BY weight DESC;

DROP VIEW IF EXISTS coder_agreement;

CREATE VIEW coder_agreement AS
SELECT
    unit_id,
    coder_a,
    coder_b,
    coder_c,
    CASE
        WHEN coder_a = coder_b AND coder_b = coder_c THEN 1.0
        WHEN coder_a = coder_b OR coder_a = coder_c OR coder_b = coder_c THEN 0.6666667
        ELSE 0.3333333
    END AS agreement_ratio
FROM coder_assignments;

DROP VIEW IF EXISTS stakeholder_coverage;

CREATE VIEW stakeholder_coverage AS
SELECT
    participant_group,
    COUNT(*) AS evidence_units,
    COUNT(DISTINCT primary_theme) AS themes_observed,
    COUNT(DISTINCT method) AS methods_observed,
    AVG(power_asymmetry) AS mean_power_asymmetry,
    AVG(privacy_sensitivity) AS mean_privacy_sensitivity
FROM evidence_units
GROUP BY participant_group;

.headers on
.mode column

SELECT
    scenario_name,
    scenario_rank,
    primary_theme,
    evidence_units,
    stakeholder_groups,
    methods,
    ROUND(synthesis_confidence, 3) AS synthesis_confidence,
    ROUND(validation_priority, 3) AS validation_priority
FROM ranked_theme_scores
ORDER BY scenario_name, scenario_rank;

SELECT
    source,
    target,
    weight
FROM theme_network_edges
ORDER BY weight DESC, source, target;

SELECT
    ROUND(AVG(agreement_ratio), 3) AS mean_coder_agreement,
    COUNT(*) AS coded_units,
    SUM(CASE WHEN agreement_ratio < 1.0 THEN 1 ELSE 0 END) AS disputed_units
FROM coder_agreement;

SELECT
    participant_group,
    evidence_units,
    themes_observed,
    methods_observed,
    ROUND(mean_power_asymmetry, 3) AS mean_power_asymmetry,
    ROUND(mean_privacy_sensitivity, 3) AS mean_privacy_sensitivity
FROM stakeholder_coverage
ORDER BY mean_power_asymmetry DESC, evidence_units ASC;
