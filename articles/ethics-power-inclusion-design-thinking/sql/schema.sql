-- SQLite schema for professional ethics, power, and inclusion analysis.
-- Run:
--   sqlite3 outputs/ethics_power_inclusion.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS stakeholder_scores;
DROP VIEW IF EXISTS design_decision_scores;
DROP TABLE IF EXISTS participation_power;
DROP TABLE IF EXISTS design_governance_risk_register;
DROP TABLE IF EXISTS ethical_design_decisions;
DROP TABLE IF EXISTS stakeholder_groups;

CREATE TABLE stakeholder_groups (
    stakeholder_id INTEGER PRIMARY KEY,
    group_name TEXT NOT NULL UNIQUE,
    stakeholder_type TEXT NOT NULL,
    access REAL NOT NULL CHECK (access BETWEEN 1 AND 10),
    voice REAL NOT NULL CHECK (voice BETWEEN 1 AND 10),
    safety REAL NOT NULL CHECK (safety BETWEEN 1 AND 10),
    compensation REAL NOT NULL CHECK (compensation BETWEEN 1 AND 10),
    representation REAL NOT NULL CHECK (representation BETWEEN 1 AND 10),
    accountability REAL NOT NULL CHECK (accountability BETWEEN 1 AND 10),
    time_burden REAL NOT NULL CHECK (time_burden BETWEEN 1 AND 10),
    cognitive_burden REAL NOT NULL CHECK (cognitive_burden BETWEEN 1 AND 10),
    emotional_burden REAL NOT NULL CHECK (emotional_burden BETWEEN 1 AND 10),
    documentation_burden REAL NOT NULL CHECK (documentation_burden BETWEEN 1 AND 10),
    uncertainty_burden REAL NOT NULL CHECK (uncertainty_burden BETWEEN 1 AND 10),
    coordination_burden REAL NOT NULL CHECK (coordination_burden BETWEEN 1 AND 10),
    affectedness REAL NOT NULL CHECK (affectedness BETWEEN 0 AND 1),
    trust_level REAL NOT NULL CHECK (trust_level BETWEEN 1 AND 10),
    accessibility_need REAL NOT NULL CHECK (accessibility_need BETWEEN 0 AND 1)
);

CREATE TABLE ethical_design_decisions (
    decision_id INTEGER PRIMARY KEY,
    design_decision TEXT NOT NULL UNIQUE,
    decision_type TEXT NOT NULL,
    harm_severity REAL NOT NULL CHECK (harm_severity BETWEEN 0 AND 1),
    probability REAL NOT NULL CHECK (probability BETWEEN 0 AND 1),
    exposure REAL NOT NULL CHECK (exposure BETWEEN 0 AND 1),
    detectability REAL NOT NULL CHECK (detectability BETWEEN 0 AND 1),
    accountability REAL NOT NULL CHECK (accountability BETWEEN 0 AND 1),
    inclusion_strength REAL NOT NULL CHECK (inclusion_strength BETWEEN 0 AND 1),
    public_value REAL NOT NULL CHECK (public_value BETWEEN 0 AND 1),
    repairability REAL NOT NULL CHECK (repairability BETWEEN 0 AND 1),
    privacy_sensitivity REAL NOT NULL CHECK (privacy_sensitivity BETWEEN 0 AND 1),
    autonomy_risk REAL NOT NULL CHECK (autonomy_risk BETWEEN 0 AND 1),
    manipulation_risk REAL NOT NULL CHECK (manipulation_risk BETWEEN 0 AND 1)
);

CREATE TABLE participation_power (
    component_id INTEGER PRIMARY KEY,
    process_component TEXT NOT NULL,
    participation_level TEXT NOT NULL,
    participant_influence REAL NOT NULL CHECK (participant_influence BETWEEN 0 AND 1),
    decision_authority REAL NOT NULL CHECK (decision_authority BETWEEN 0 AND 1),
    compensation_quality REAL NOT NULL CHECK (compensation_quality BETWEEN 0 AND 1),
    accessibility_quality REAL NOT NULL CHECK (accessibility_quality BETWEEN 0 AND 1),
    feedback_loop_strength REAL NOT NULL CHECK (feedback_loop_strength BETWEEN 0 AND 1),
    community_control REAL NOT NULL CHECK (community_control BETWEEN 0 AND 1),
    documentation_transparency REAL NOT NULL CHECK (documentation_transparency BETWEEN 0 AND 1),
    safety_quality REAL NOT NULL CHECK (safety_quality BETWEEN 0 AND 1),
    interpretation_sharedness REAL NOT NULL CHECK (interpretation_sharedness BETWEEN 0 AND 1)
);

CREATE TABLE design_governance_risk_register (
    risk_id INTEGER PRIMARY KEY,
    design_decision TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    repair_difficulty INTEGER NOT NULL CHECK (repair_difficulty BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO stakeholder_groups (
    group_name, stakeholder_type, access, voice, safety, compensation, representation,
    accountability, time_burden, cognitive_burden, emotional_burden, documentation_burden,
    uncertainty_burden, coordination_burden, affectedness, trust_level, accessibility_need
)
VALUES
('Confident digital users','user_group',8.2,6.8,7.6,5.0,7.4,6.4,3.2,3.4,3.0,3.8,3.6,3.4,0.55,7.4,0.28),
('Disabled users','user_group',5.0,5.2,5.8,4.8,5.4,5.0,7.2,7.4,6.8,7.0,7.2,7.0,0.92,5.2,0.92),
('Limited English users','user_group',5.4,5.0,5.6,4.6,5.2,5.0,6.8,7.2,6.4,6.6,7.0,6.8,0.88,5.4,0.78),
('Low digital access users','user_group',4.8,4.8,5.4,4.4,5.0,4.6,7.0,7.6,6.6,7.2,7.4,7.0,0.86,5.0,0.74),
('Frontline staff','staff_group',7.2,6.0,6.2,5.2,6.4,5.8,6.4,6.6,6.8,5.8,6.2,6.4,0.72,6.0,0.42),
('Caregivers and intermediaries','support_group',6.4,5.8,6.0,5.0,5.8,5.4,7.4,6.8,7.0,6.8,7.0,7.6,0.78,5.8,0.58),
('Low-trust community members','community_group',5.8,4.6,4.8,4.2,4.8,4.4,6.8,7.0,7.8,7.0,7.8,7.2,0.84,4.2,0.62),
('Community advocates','community_group',6.8,6.4,6.4,5.8,6.6,5.6,6.2,6.4,6.6,5.8,6.4,7.0,0.74,5.8,0.50);

INSERT INTO ethical_design_decisions (
    design_decision, decision_type, harm_severity, probability, exposure, detectability,
    accountability, inclusion_strength, public_value, repairability, privacy_sensitivity,
    autonomy_risk, manipulation_risk
)
VALUES
('Digital-first access','service_channel',0.72,0.54,0.80,0.46,0.42,0.52,0.70,0.46,0.44,0.48,0.30),
('AI-assisted case prioritization','ai_system',0.86,0.48,0.62,0.38,0.36,0.46,0.74,0.36,0.82,0.62,0.44),
('Behavioral reminder campaign','behavioral_design',0.42,0.40,0.74,0.66,0.58,0.62,0.64,0.58,0.50,0.54,0.66),
('Reduced human support','service_operations',0.76,0.58,0.68,0.42,0.40,0.44,0.62,0.34,0.38,0.46,0.28),
('Community co-design process','participatory_design',0.28,0.30,0.42,0.72,0.76,0.78,0.88,0.74,0.32,0.22,0.18),
('Data-driven personalization','data_ai',0.70,0.46,0.66,0.44,0.38,0.48,0.68,0.44,0.84,0.68,0.58),
('Automated eligibility triage','public_service_ai',0.90,0.42,0.56,0.34,0.32,0.40,0.80,0.30,0.78,0.72,0.48),
('Plain-language redesign','communication',0.22,0.24,0.70,0.78,0.72,0.74,0.76,0.78,0.26,0.18,0.16);
