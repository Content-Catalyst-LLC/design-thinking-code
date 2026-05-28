-- Analytical queries for AI-assisted design research evidence.
-- Run after schema.sql:
--   sqlite3 outputs/ai_research_evidence.db < sql/schema.sql
--   sqlite3 outputs/ai_research_evidence.db < sql/analytical_queries.sql

DROP VIEW IF EXISTS research_signal_scores;

CREATE VIEW research_signal_scores AS
SELECT
    signal,
    evidence_type,
    0.18 * source_strength +
    0.17 * relevance +
    0.15 * traceability +
    0.15 * representativeness +
    0.15 * validation +
    0.08 * recency +
    0.07 * consent_alignment +
    0.05 * participant_coverage AS confidence_score,
    0.26 * missingness_risk +
    0.22 * (1.0 - representativeness) +
    0.18 * (1.0 - validation) +
    0.14 * ai_assistance_risk +
    0.10 * (1.0 - traceability) +
    0.10 * (1.0 - participant_coverage) AS bias_risk,
    0.38 * ai_assistance_risk +
    0.18 * (1.0 - traceability) +
    0.16 * (1.0 - validation) +
    0.14 * missingness_risk +
    0.14 * (1.0 - consent_alignment) AS ai_risk,
    MIN(
      MAX(
        0.30 * (
            0.18 * source_strength +
            0.17 * relevance +
            0.15 * traceability +
            0.15 * representativeness +
            0.15 * validation +
            0.08 * recency +
            0.07 * consent_alignment +
            0.05 * participant_coverage
        ) +
        0.24 * decision_relevance +
        0.14 * validation +
        0.12 * traceability +
        0.08 * consent_alignment +
        0.08 * participant_coverage -
        0.04 * (
            0.26 * missingness_risk +
            0.22 * (1.0 - representativeness) +
            0.18 * (1.0 - validation) +
            0.14 * ai_assistance_risk +
            0.10 * (1.0 - traceability) +
            0.10 * (1.0 - participant_coverage)
        ),
        0.0
      ),
      1.0
    ) AS decision_readiness
FROM research_signals;

DROP VIEW IF EXISTS metadata_quality_scores;

CREATE VIEW metadata_quality_scores AS
SELECT
    evidence_id,
    evidence_type,
    source_owner,
    collection_date,
    0.18 * consent_recorded +
    0.13 * method_recorded +
    0.13 * participant_group_recorded +
    0.12 * limitations_recorded +
    0.12 * ai_use_recorded +
    0.12 * reviewer_recorded +
    0.10 * decision_link_recorded +
    0.10 * retention_rule_recorded AS metadata_quality,
    8 - (
        consent_recorded +
        method_recorded +
        participant_group_recorded +
        limitations_recorded +
        ai_use_recorded +
        reviewer_recorded +
        decision_link_recorded +
        retention_rule_recorded
    ) AS metadata_gap_count
FROM evidence_metadata_registry;

.headers on
.mode column

SELECT
    signal,
    evidence_type,
    ROUND(confidence_score, 3) AS confidence_score,
    ROUND(bias_risk, 3) AS bias_risk,
    ROUND(ai_risk, 3) AS ai_risk,
    ROUND(decision_readiness, 3) AS decision_readiness
FROM research_signal_scores
ORDER BY bias_risk + ai_risk DESC;

SELECT
    evidence_id,
    evidence_type,
    source_owner,
    ROUND(metadata_quality, 3) AS metadata_quality,
    metadata_gap_count
FROM metadata_quality_scores
ORDER BY metadata_quality ASC, metadata_gap_count DESC;
