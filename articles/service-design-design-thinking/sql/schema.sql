-- SQLite schema for professional service design analysis.
-- Run:
--   sqlite3 outputs/service_design.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS service_stage_scores;
DROP TABLE IF EXISTS service_scenario_weights;
DROP TABLE IF EXISTS service_user_groups;
DROP TABLE IF EXISTS service_blueprint_dependencies;
DROP TABLE IF EXISTS service_risk_register;
DROP TABLE IF EXISTS service_journey_stages;

CREATE TABLE service_journey_stages (
    stage_id INTEGER PRIMARY KEY,
    stage_name TEXT NOT NULL UNIQUE,
    stage_order INTEGER NOT NULL,
    channel TEXT NOT NULL,
    completion_probability REAL NOT NULL CHECK (completion_probability > 0 AND completion_probability <= 1),
    clarity REAL NOT NULL CHECK (clarity BETWEEN 1 AND 10),
    trust REAL NOT NULL CHECK (trust BETWEEN 1 AND 10),
    accessibility REAL NOT NULL CHECK (accessibility BETWEEN 1 AND 10),
    user_burden REAL NOT NULL CHECK (user_burden BETWEEN 1 AND 10),
    staff_load REAL NOT NULL CHECK (staff_load BETWEEN 1 AND 10),
    recovery_quality REAL NOT NULL CHECK (recovery_quality BETWEEN 1 AND 10),
    frontstage_quality REAL NOT NULL CHECK (frontstage_quality BETWEEN 1 AND 10),
    backstage_readiness REAL NOT NULL CHECK (backstage_readiness BETWEEN 1 AND 10),
    policy_complexity REAL NOT NULL CHECK (policy_complexity BETWEEN 1 AND 10),
    data_dependency REAL NOT NULL CHECK (data_dependency BETWEEN 1 AND 10)
);

CREATE TABLE service_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    completion_probability_weight REAL NOT NULL CHECK (completion_probability_weight >= 0),
    clarity_weight REAL NOT NULL CHECK (clarity_weight >= 0),
    trust_weight REAL NOT NULL CHECK (trust_weight >= 0),
    accessibility_weight REAL NOT NULL CHECK (accessibility_weight >= 0),
    recovery_quality_weight REAL NOT NULL CHECK (recovery_quality_weight >= 0),
    user_burden_weight REAL NOT NULL CHECK (user_burden_weight >= 0),
    staff_load_weight REAL NOT NULL CHECK (staff_load_weight >= 0),
    CHECK (
        ABS(
            completion_probability_weight +
            clarity_weight +
            trust_weight +
            accessibility_weight +
            recovery_quality_weight +
            user_burden_weight +
            staff_load_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE service_stage_scores (
    score_id INTEGER PRIMARY KEY,
    stage_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    service_stage_quality REAL NOT NULL,
    failure_risk REAL NOT NULL,
    burden_risk REAL NOT NULL,
    operational_friction_index REAL NOT NULL,
    procedural_dignity_index REAL NOT NULL,
    redesign_priority REAL NOT NULL,
    service_resilience REAL NOT NULL,
    FOREIGN KEY (stage_id) REFERENCES service_journey_stages(stage_id),
    FOREIGN KEY (scenario_id) REFERENCES service_scenario_weights(scenario_id)
);

CREATE TABLE service_user_groups (
    group_id INTEGER PRIMARY KEY,
    group_name TEXT NOT NULL UNIQUE,
    affectedness REAL NOT NULL CHECK (affectedness BETWEEN 0 AND 1),
    completion_rate REAL NOT NULL CHECK (completion_rate BETWEEN 0 AND 1),
    clarity REAL NOT NULL CHECK (clarity BETWEEN 1 AND 10),
    accessibility REAL NOT NULL CHECK (accessibility BETWEEN 1 AND 10),
    trust REAL NOT NULL CHECK (trust BETWEEN 1 AND 10),
    burden REAL NOT NULL CHECK (burden BETWEEN 1 AND 10),
    recovery_access REAL NOT NULL CHECK (recovery_access BETWEEN 1 AND 10),
    assisted_support REAL NOT NULL CHECK (assisted_support BETWEEN 1 AND 10),
    device_access REAL NOT NULL CHECK (device_access BETWEEN 1 AND 10),
    language_access REAL NOT NULL CHECK (language_access BETWEEN 1 AND 10),
    disability_access REAL NOT NULL CHECK (disability_access BETWEEN 1 AND 10)
);

CREATE TABLE service_blueprint_dependencies (
    dependency_id INTEGER PRIMARY KEY,
    stage_name TEXT NOT NULL,
    frontstage_actor TEXT NOT NULL,
    backstage_owner TEXT NOT NULL,
    support_system TEXT NOT NULL,
    dependency_strength REAL NOT NULL CHECK (dependency_strength BETWEEN 1 AND 10),
    handoff_risk REAL NOT NULL CHECK (handoff_risk BETWEEN 1 AND 10),
    data_quality REAL NOT NULL CHECK (data_quality BETWEEN 1 AND 10),
    ownership_clarity REAL NOT NULL CHECK (ownership_clarity BETWEEN 1 AND 10),
    staff_discretion REAL NOT NULL CHECK (staff_discretion BETWEEN 1 AND 10),
    automation_opacity REAL NOT NULL CHECK (automation_opacity BETWEEN 1 AND 10),
    governance_readiness REAL NOT NULL CHECK (governance_readiness BETWEEN 1 AND 10)
);

CREATE TABLE service_risk_register (
    risk_id INTEGER PRIMARY KEY,
    stage_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO service_journey_stages (
    stage_name, stage_order, channel, completion_probability, clarity, trust, accessibility,
    user_burden, staff_load, recovery_quality, frontstage_quality, backstage_readiness,
    policy_complexity, data_dependency
)
VALUES
('Discover Service',1,'web_search',0.92,7.4,7.0,7.2,3.5,3.0,6.8,7.2,6.5,4.2,4.0),
('Understand Eligibility',2,'website_phone',0.78,5.8,5.8,5.6,5.8,5.2,5.4,5.7,5.4,7.2,5.2),
('Prepare Documents',3,'documents',0.70,5.2,5.4,5.0,7.4,6.0,4.8,5.1,5.2,7.8,5.8),
('Submit Request',4,'digital_form',0.84,6.8,6.4,6.8,6.2,5.8,5.8,6.7,6.0,6.0,6.4),
('Wait for Review',5,'status_portal',0.76,5.5,5.3,5.4,6.8,6.5,4.6,5.2,5.4,6.4,7.2),
('Receive Decision',6,'email_letter',0.88,6.4,6.2,6.0,5.6,5.6,5.2,6.2,6.0,6.8,6.0),
('Resolve Issue',7,'phone_support',0.62,5.0,5.5,5.8,7.2,7.4,5.0,5.3,4.9,6.6,6.8),
('Maintain Access',8,'portal_staff',0.80,6.2,6.0,6.4,5.9,6.2,5.6,6.1,5.8,5.8,6.2),
('Renew Service',9,'portal_email',0.74,5.9,5.7,5.8,6.5,6.4,5.0,5.8,5.5,6.2,6.7),
('Exit or Transition',10,'staff_email',0.82,6.0,6.1,6.0,5.4,5.2,5.8,6.0,5.9,5.4,5.2);

INSERT INTO service_scenario_weights (
    scenario_name,
    completion_probability_weight,
    clarity_weight,
    trust_weight,
    accessibility_weight,
    recovery_quality_weight,
    user_burden_weight,
    staff_load_weight
)
VALUES
('Balanced',0.22,0.18,0.18,0.16,0.14,0.07,0.05),
('Reliability First',0.38,0.14,0.12,0.12,0.10,0.08,0.06),
('Accessibility First',0.18,0.16,0.14,0.34,0.10,0.05,0.03),
('Trust and Recovery',0.18,0.14,0.26,0.12,0.22,0.05,0.03),
('Burden Sensitive',0.18,0.14,0.14,0.14,0.10,0.22,0.08),
('Staff Sustainability',0.18,0.14,0.14,0.12,0.12,0.08,0.22),
('Public Service Equity',0.20,0.16,0.18,0.22,0.14,0.07,0.03);
