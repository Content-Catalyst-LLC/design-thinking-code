.headers on
.mode column

SELECT
  intervention_name,
  ROUND(
    0.22*expected_behavior_gain + 0.14*importance + 0.16*equity_reach +
    0.08*transparency + 0.08*autonomy_preservation + 0.10*trust_effect +
    0.10*accessibility_effect + 0.06*durability - 0.04*ethical_risk -
    0.02*implementation_effort, 4
  ) AS intervention_priority,
  ROUND(
    0.26*transparency + 0.26*autonomy_preservation + 0.18*equity_reach +
    0.16*trust_effect + 0.14*accessibility_effect - 0.22*ethical_risk, 4
  ) AS ethical_quality_index
FROM behavioral_interventions
ORDER BY intervention_priority DESC;
