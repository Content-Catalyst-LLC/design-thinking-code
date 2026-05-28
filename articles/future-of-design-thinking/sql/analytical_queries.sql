DROP VIEW IF EXISTS future_design_scores;

CREATE VIEW future_design_scores AS
SELECT
    initiative_name,
    initiative_type,
    0.11 * human_centered_quality +
    0.12 * systems_literacy +
    0.12 * evidence_quality +
    0.12 * ethical_maturity +
    0.10 * ai_governance +
    0.10 * implementation_capacity +
    0.12 * public_value +
    0.09 * stewardship_capacity +
    0.06 * participation_quality +
    0.06 * organizational_learning +
    0.04 * data_infrastructure +
    0.04 * climate_responsibility +
    0.04 * burden_awareness -
    0.10 * unmanaged_risk AS future_design_readiness
FROM future_design_initiatives;

.headers on
.mode column

SELECT *
FROM future_design_scores
ORDER BY future_design_readiness DESC;
