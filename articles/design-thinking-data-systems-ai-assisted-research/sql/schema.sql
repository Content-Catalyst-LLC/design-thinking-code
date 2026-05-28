-- SQLite schema for professional AI-assisted design research evidence analysis.
-- Run:
--   sqlite3 outputs/ai_research_evidence.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS research_signal_scores;
DROP VIEW IF EXISTS metadata_quality_scores;
DROP TABLE IF EXISTS research_governance_risk_register;
DROP TABLE IF EXISTS evidence_metadata_registry;
DROP TABLE IF EXISTS ai_assistance_log;
DROP TABLE IF EXISTS research_signals;

CREATE TABLE research_signals (
    signal_id INTEGER PRIMARY KEY,
    signal TEXT NOT NULL UNIQUE,
    evidence_type TEXT NOT NULL,
    source_strength REAL NOT NULL CHECK (source_strength BETWEEN 0 AND 1),
    relevance REAL NOT NULL CHECK (relevance BETWEEN 0 AND 1),
    traceability REAL NOT NULL CHECK (traceability BETWEEN 0 AND 1),
    representativeness REAL NOT NULL CHECK (representativeness BETWEEN 0 AND 1),
    validation REAL NOT NULL CHECK (validation BETWEEN 0 AND 1),
    missingness_risk REAL NOT NULL CHECK (missingness_risk BETWEEN 0 AND 1),
    ai_assistance_risk REAL NOT NULL CHECK (ai_assistance_risk BETWEEN 0 AND 1),
    decision_relevance REAL NOT NULL CHECK (decision_relevance BETWEEN 0 AND 1),
    recency REAL NOT NULL CHECK (recency BETWEEN 0 AND 1),
    consent_alignment REAL NOT NULL CHECK (consent_alignment BETWEEN 0 AND 1),
    participant_coverage REAL NOT NULL CHECK (participant_coverage BETWEEN 0 AND 1)
);

CREATE TABLE ai_assistance_log (
    artifact_id TEXT PRIMARY KEY,
    research_task TEXT NOT NULL,
    ai_tool_class TEXT NOT NULL,
    source_grounding REAL NOT NULL CHECK (source_grounding BETWEEN 0 AND 1),
    human_review REAL NOT NULL CHECK (human_review BETWEEN 0 AND 1),
    output_reliability REAL NOT NULL CHECK (output_reliability BETWEEN 0 AND 1),
    sensitive_data_exposure REAL NOT NULL CHECK (sensitive_data_exposure BETWEEN 0 AND 1),
    prompt_traceability REAL NOT NULL CHECK (prompt_traceability BETWEEN 0 AND 1),
    model_version_recorded REAL NOT NULL CHECK (model_version_recorded BETWEEN 0 AND 1),
    hallucination_risk REAL NOT NULL CHECK (hallucination_risk BETWEEN 0 AND 1),
    minority_signal_preservation REAL NOT NULL CHECK (minority_signal_preservation BETWEEN 0 AND 1)
);

CREATE TABLE evidence_metadata_registry (
    evidence_id TEXT PRIMARY KEY,
    evidence_type TEXT NOT NULL,
    source_owner TEXT NOT NULL,
    collection_date TEXT NOT NULL,
    consent_recorded INTEGER NOT NULL CHECK (consent_recorded IN (0, 1)),
    method_recorded INTEGER NOT NULL CHECK (method_recorded IN (0, 1)),
    participant_group_recorded INTEGER NOT NULL CHECK (participant_group_recorded IN (0, 1)),
    limitations_recorded INTEGER NOT NULL CHECK (limitations_recorded IN (0, 1)),
    ai_use_recorded INTEGER NOT NULL CHECK (ai_use_recorded IN (0, 1)),
    reviewer_recorded INTEGER NOT NULL CHECK (reviewer_recorded IN (0, 1)),
    decision_link_recorded INTEGER NOT NULL CHECK (decision_link_recorded IN (0, 1)),
    retention_rule_recorded INTEGER NOT NULL CHECK (retention_rule_recorded IN (0, 1))
);

CREATE TABLE research_governance_risk_register (
    risk_id TEXT PRIMARY KEY,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    repair_difficulty INTEGER NOT NULL CHECK (repair_difficulty BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO research_signals (
    signal, evidence_type, source_strength, relevance, traceability, representativeness,
    validation, missingness_risk, ai_assistance_risk, decision_relevance, recency,
    consent_alignment, participant_coverage
)
VALUES
('Application abandonment at documentation step','analytics',0.78,0.90,0.82,0.70,0.66,0.32,0.18,0.90,0.84,0.86,0.72),
('Low trust in eligibility explanations','interviews',0.68,0.86,0.76,0.58,0.62,0.42,0.42,0.86,0.78,0.82,0.60),
('Disabled users need assisted access','accessibility_testing',0.74,0.92,0.80,0.54,0.70,0.46,0.36,0.92,0.80,0.88,0.58),
('Limited-English users misinterpret status messages','usability_testing',0.70,0.82,0.74,0.56,0.64,0.44,0.38,0.82,0.76,0.84,0.62),
('Frontline staff repair data errors manually','staff_research',0.66,0.80,0.70,0.62,0.58,0.38,0.30,0.78,0.74,0.80,0.66),
('Prototype improves next-step comprehension','prototype_test',0.76,0.84,0.78,0.68,0.76,0.30,0.24,0.84,0.88,0.86,0.70),
('AI summary misses severe edge-case failures','ai_validation',0.60,0.88,0.66,0.48,0.52,0.54,0.76,0.88,0.82,0.78,0.50),
('Service log shows repeat contact after rejection','service_logs',0.72,0.78,0.72,0.74,0.68,0.34,0.28,0.76,0.80,0.84,0.76),
('Research repository lacks consent metadata','metadata_audit',0.82,0.86,0.88,0.66,0.74,0.40,0.34,0.90,0.86,0.52,0.68),
('Semantic search over-retrieves outdated findings','retrieval_audit',0.70,0.76,0.68,0.60,0.58,0.44,0.62,0.74,0.52,0.78,0.64);

INSERT INTO evidence_metadata_registry (
    evidence_id, evidence_type, source_owner, collection_date,
    consent_recorded, method_recorded, participant_group_recorded, limitations_recorded,
    ai_use_recorded, reviewer_recorded, decision_link_recorded, retention_rule_recorded
)
VALUES
('E001','interviews','research_ops','2026-03-04',1,1,1,1,1,1,1,1),
('E002','analytics','data_team','2026-03-08',1,1,0,1,0,1,1,1),
('E003','accessibility_testing','accessibility_team','2026-03-15',1,1,1,1,1,1,1,1),
('E004','service_logs','operations','2026-03-18',1,1,0,1,1,1,1,1),
('E005','prototype_test','design_research','2026-03-22',1,1,1,1,1,1,1,0),
('E006','ai_summary','design_research','2026-03-24',0,1,0,1,1,0,1,0),
('E007','public_comments','civic_research','2026-03-27',1,1,1,1,1,1,0,1),
('E008','metadata_audit','research_ops','2026-03-29',1,1,1,1,1,1,1,1);
