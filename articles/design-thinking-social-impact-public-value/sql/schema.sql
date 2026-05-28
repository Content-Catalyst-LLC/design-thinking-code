-- SQLite schema for professional social-impact public-value analysis.
-- Run:
--   sqlite3 outputs/public_value_impact.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS social_impact_scores;
DROP VIEW IF EXISTS stakeholder_burden_scores;
DROP VIEW IF EXISTS participation_quality_scores;
DROP TABLE IF EXISTS social_impact_risk_register;
DROP TABLE IF EXISTS participation_quality;
DROP TABLE IF EXISTS stakeholder_burden_public_value;
DROP TABLE IF EXISTS social_impact_interventions;

CREATE TABLE social_impact_interventions (
    intervention_id INTEGER PRIMARY KEY,
    intervention_name TEXT NOT NULL UNIQUE,
    intervention_type TEXT NOT NULL,
    access REAL NOT NULL CHECK (access BETWEEN 1 AND 10),
    equity REAL NOT NULL CHECK (equity BETWEEN 1 AND 10),
    dignity REAL NOT NULL CHECK (dignity BETWEEN 1 AND 10),
    legitimacy REAL NOT NULL CHECK (legitimacy BETWEEN 1 AND 10),
    accountability REAL NOT NULL CHECK (accountability BETWEEN 1 AND 10),
    outcome_strength REAL NOT NULL CHECK (outcome_strength BETWEEN 1 AND 10),
    sustainability REAL NOT NULL CHECK (sustainability BETWEEN 1 AND 10),
    learning_capacity REAL NOT NULL CHECK (learning_capacity BETWEEN 1 AND 10),
    feasibility REAL NOT NULL CHECK (feasibility BETWEEN 1 AND 10),
    governance_strength REAL NOT NULL CHECK (governance_strength BETWEEN 1 AND 10),
    implementation_risk REAL NOT NULL CHECK (implementation_risk BETWEEN 1 AND 10),
    burden_risk REAL NOT NULL CHECK (burden_risk BETWEEN 1 AND 10),
    participation_quality REAL NOT NULL CHECK (participation_quality BETWEEN 1 AND 10),
    community_defined_value REAL NOT NULL CHECK (community_defined_value BETWEEN 1 AND 10),
    repair_capacity REAL NOT NULL CHECK (repair_capacity BETWEEN 1 AND 10),
    stewardship_capacity REAL NOT NULL CHECK (stewardship_capacity BETWEEN 1 AND 10)
);

CREATE TABLE stakeholder_burden_public_value (
    stakeholder_id INTEGER PRIMARY KEY,
    stakeholder_group TEXT NOT NULL UNIQUE,
    stakeholder_type TEXT NOT NULL,
    baseline_time_burden REAL NOT NULL CHECK (baseline_time_burden BETWEEN 1 AND 10),
    baseline_cognitive_burden REAL NOT NULL CHECK (baseline_cognitive_burden BETWEEN 1 AND 10),
    baseline_emotional_burden REAL NOT NULL CHECK (baseline_emotional_burden BETWEEN 1 AND 10),
    baseline_documentation_burden REAL NOT NULL CHECK (baseline_documentation_burden BETWEEN 1 AND 10),
    baseline_uncertainty_burden REAL NOT NULL CHECK (baseline_uncertainty_burden BETWEEN 1 AND 10),
    post_time_burden REAL NOT NULL CHECK (post_time_burden BETWEEN 1 AND 10),
    post_cognitive_burden REAL NOT NULL CHECK (post_cognitive_burden BETWEEN 1 AND 10),
    post_emotional_burden REAL NOT NULL CHECK (post_emotional_burden BETWEEN 1 AND 10),
    post_documentation_burden REAL NOT NULL CHECK (post_documentation_burden BETWEEN 1 AND 10),
    post_uncertainty_burden REAL NOT NULL CHECK (post_uncertainty_burden BETWEEN 1 AND 10),
    affectedness REAL NOT NULL CHECK (affectedness BETWEEN 0 AND 1),
    voice REAL NOT NULL CHECK (voice BETWEEN 1 AND 10),
    influence REAL NOT NULL CHECK (influence BETWEEN 1 AND 10),
    repair_access REAL NOT NULL CHECK (repair_access BETWEEN 1 AND 10),
    trust_gap REAL NOT NULL CHECK (trust_gap BETWEEN 1 AND 10),
    accessibility_need REAL NOT NULL CHECK (accessibility_need BETWEEN 0 AND 1)
);

CREATE TABLE participation_quality (
    activity_id INTEGER PRIMARY KEY,
    participation_activity TEXT NOT NULL UNIQUE,
    participation_level TEXT NOT NULL,
    affected_people_involved REAL NOT NULL CHECK (affected_people_involved BETWEEN 0 AND 1),
    decision_influence REAL NOT NULL CHECK (decision_influence BETWEEN 0 AND 1),
    compensation REAL NOT NULL CHECK (compensation BETWEEN 0 AND 1),
    accessibility_support REAL NOT NULL CHECK (accessibility_support BETWEEN 0 AND 1),
    language_support REAL NOT NULL CHECK (language_support BETWEEN 0 AND 1),
    feedback_loop REAL NOT NULL CHECK (feedback_loop BETWEEN 0 AND 1),
    community_ownership REAL NOT NULL CHECK (community_ownership BETWEEN 0 AND 1),
    power_sharing REAL NOT NULL CHECK (power_sharing BETWEEN 0 AND 1),
    documentation_quality REAL NOT NULL CHECK (documentation_quality BETWEEN 0 AND 1),
    ethical_review REAL NOT NULL CHECK (ethical_review BETWEEN 0 AND 1)
);

CREATE TABLE social_impact_risk_register (
    risk_id TEXT PRIMARY KEY,
    intervention_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    repair_difficulty INTEGER NOT NULL CHECK (repair_difficulty BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO social_impact_interventions (
    intervention_name, intervention_type, access, equity, dignity, legitimacy, accountability,
    outcome_strength, sustainability, learning_capacity, feasibility, governance_strength,
    implementation_risk, burden_risk, participation_quality, community_defined_value,
    repair_capacity, stewardship_capacity
)
VALUES
('Assisted access pathway','service_access',8.8,8.6,8.4,7.8,7.6,8.0,7.2,7.6,7.2,7.0,5.8,4.8,7.4,8.2,7.2,7.0),
('Community-led research council','participatory_governance',7.6,9.0,8.8,9.2,8.8,7.4,6.8,8.2,6.2,7.4,6.8,5.6,9.2,9.4,7.6,7.2),
('Plain-language eligibility redesign','policy_service_redesign',8.4,8.0,8.6,7.6,7.4,7.8,8.0,7.4,8.0,7.2,4.8,4.2,6.8,7.8,7.0,7.6),
('Mobile outreach and navigation support','community_service_model',9.0,8.8,8.2,8.0,7.6,8.2,6.6,7.2,6.6,6.6,6.6,5.8,7.8,8.6,7.0,6.6),
('Burden audit and repair protocol','accountability_system',8.2,9.2,8.8,8.6,9.0,8.0,7.6,8.8,7.0,8.0,5.6,4.0,8.2,9.0,8.8,8.0),
('Public value dashboard','evidence_learning_system',6.8,7.2,6.8,7.4,8.2,7.0,7.4,9.0,7.6,8.2,5.4,5.2,6.4,7.0,7.4,7.8),
('Participatory budgeting prototype','participatory_resource_allocation',7.8,8.6,8.0,9.0,8.4,7.6,6.4,7.8,5.8,6.8,7.2,6.4,8.8,9.0,7.6,6.6),
('AI-assisted public comment synthesis','ai_research_governance',6.6,7.0,6.6,6.8,6.4,6.8,6.8,7.6,6.8,6.2,7.6,7.0,5.8,6.4,5.8,6.4),
('Community climate resilience hub','place_based_resilience',8.6,8.8,8.4,8.6,8.0,8.4,7.2,8.0,6.4,7.2,6.8,5.8,8.6,9.0,7.8,7.4),
('Mutual aid data cooperative','data_stewardship',7.8,8.4,8.2,8.8,8.6,7.4,7.0,8.6,5.8,7.0,7.4,6.2,9.0,9.2,8.0,7.0);
