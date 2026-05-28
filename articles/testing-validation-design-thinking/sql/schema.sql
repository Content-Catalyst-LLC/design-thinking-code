-- SQLite schema for professional testing and validation analysis.
-- Run:
--   sqlite3 outputs/testing_validation.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS validation_scores;
DROP TABLE IF EXISTS validation_scenario_weights;
DROP TABLE IF EXISTS testing_rounds;
DROP TABLE IF EXISTS decision_thresholds;
DROP TABLE IF EXISTS validation_risk_register;
DROP TABLE IF EXISTS validation_concepts;

CREATE TABLE validation_concepts (
    concept_id INTEGER PRIMARY KEY,
    concept_name TEXT NOT NULL UNIQUE,
    prototype_type TEXT NOT NULL,
    fidelity_level TEXT NOT NULL,
    desirability REAL NOT NULL CHECK (desirability BETWEEN 1 AND 10),
    feasibility REAL NOT NULL CHECK (feasibility BETWEEN 1 AND 10),
    viability REAL NOT NULL CHECK (viability BETWEEN 1 AND 10),
    responsibility REAL NOT NULL CHECK (responsibility BETWEEN 1 AND 10),
    friction REAL NOT NULL CHECK (friction BETWEEN 1 AND 10),
    residual_risk REAL NOT NULL CHECK (residual_risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    stakeholder_coverage REAL CHECK (stakeholder_coverage BETWEEN 0 AND 1),
    method_triangulation REAL CHECK (method_triangulation BETWEEN 0 AND 1),
    equity_signal REAL CHECK (equity_signal BETWEEN 1 AND 10),
    accessibility_signal REAL CHECK (accessibility_signal BETWEEN 1 AND 10),
    operational_signal REAL CHECK (operational_signal BETWEEN 1 AND 10)
);

CREATE TABLE validation_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    desirability_weight REAL NOT NULL CHECK (desirability_weight >= 0),
    feasibility_weight REAL NOT NULL CHECK (feasibility_weight >= 0),
    viability_weight REAL NOT NULL CHECK (viability_weight >= 0),
    responsibility_weight REAL NOT NULL CHECK (responsibility_weight >= 0),
    risk_penalty_weight REAL NOT NULL CHECK (risk_penalty_weight >= 0),
    CHECK (
        ABS(
            desirability_weight +
            feasibility_weight +
            viability_weight +
            responsibility_weight +
            risk_penalty_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE validation_scores (
    score_id INTEGER PRIMARY KEY,
    concept_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    validation_value REAL NOT NULL,
    combined_risk REAL NOT NULL,
    confidence_adjusted_value REAL NOT NULL,
    validation_review_priority REAL NOT NULL,
    advance_readiness REAL NOT NULL,
    FOREIGN KEY (concept_id) REFERENCES validation_concepts(concept_id),
    FOREIGN KEY (scenario_id) REFERENCES validation_scenario_weights(scenario_id)
);

CREATE TABLE testing_rounds (
    round_id INTEGER PRIMARY KEY,
    concept_name TEXT NOT NULL,
    round INTEGER NOT NULL,
    adoption_likelihood REAL NOT NULL,
    comprehension REAL NOT NULL,
    trust REAL NOT NULL,
    observed_friction REAL NOT NULL,
    task_success_rate REAL NOT NULL,
    error_rate REAL NOT NULL,
    mean_time_minutes REAL NOT NULL,
    critical_issue_count INTEGER NOT NULL,
    participant_count INTEGER NOT NULL
);

CREATE TABLE decision_thresholds (
    threshold_id INTEGER PRIMARY KEY,
    metric TEXT NOT NULL,
    threshold_direction TEXT NOT NULL,
    threshold_value REAL NOT NULL,
    decision_implication TEXT NOT NULL
);

CREATE TABLE validation_risk_register (
    risk_id INTEGER PRIMARY KEY,
    concept_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO validation_concepts (
    concept_name, prototype_type, fidelity_level, desirability, feasibility, viability,
    responsibility, friction, residual_risk, evidence_quality, stakeholder_coverage,
    method_triangulation, equity_signal, accessibility_signal, operational_signal
)
VALUES
('Guided Onboarding Flow','digital_flow','mid',8.5,7.6,7.8,7.6,3.9,4.0,0.76,0.70,0.72,7.4,7.2,7.5),
('Simplified Intake Form','form_redesign','low',8.0,8.4,8.0,8.2,3.4,3.5,0.81,0.74,0.76,8.0,7.9,8.2),
('Service Navigation Wizard','guided_service','mid',7.9,7.3,7.5,7.3,4.5,4.6,0.72,0.66,0.68,7.1,6.9,7.0),
('Follow-Up Reminder System','communication_system','mid',7.6,8.1,8.2,7.8,3.7,3.9,0.78,0.69,0.73,7.5,7.4,8.0),
('Human Support Escalation Pathway','service_pathway','mid',8.4,7.2,7.4,8.5,4.1,4.3,0.79,0.78,0.75,8.6,8.3,7.1),
('Status Visibility Dashboard','status_system','high',8.2,7.8,7.7,7.9,3.8,4.1,0.75,0.72,0.74,7.8,7.6,7.7),
('Exception Handling Service Blueprint','service_blueprint','low',8.1,7.5,7.6,8.3,4.0,4.2,0.77,0.80,0.78,8.4,8.1,7.6),
('Plain-Language Eligibility Guide','content_prototype','low',8.3,8.6,8.1,8.4,3.2,3.3,0.84,0.76,0.80,8.2,8.5,8.3);

INSERT INTO validation_scenario_weights (
    scenario_name,
    desirability_weight,
    feasibility_weight,
    viability_weight,
    responsibility_weight,
    risk_penalty_weight
)
VALUES
('Balanced',0.25,0.20,0.20,0.20,0.15),
('Desirability First',0.42,0.16,0.16,0.16,0.10),
('Feasibility First',0.16,0.42,0.16,0.16,0.10),
('Viability First',0.16,0.18,0.42,0.14,0.10),
('Responsibility First',0.16,0.16,0.16,0.42,0.10),
('Risk Sensitive',0.20,0.16,0.16,0.18,0.30),
('Equity Sensitive',0.20,0.16,0.16,0.33,0.15),
('Pilot Readiness',0.18,0.26,0.24,0.18,0.14);

INSERT INTO validation_risk_register (
    concept_name, risk_category, risk_description, severity, likelihood, detectability, mitigation_owner, mitigation_status
)
VALUES
('Guided Onboarding Flow','comprehension','Users may follow the flow without understanding downstream consequences',4,3,4,'research_lead','active'),
('Simplified Intake Form','policy','Simplified form language may omit legally relevant nuance',4,3,3,'policy_counsel','active'),
('Service Navigation Wizard','trust','Wizard may create false confidence if guidance is incomplete',5,3,3,'research_lead','active'),
('Follow-Up Reminder System','privacy','Reminder content may expose sensitive service participation',5,2,4,'privacy_owner','active'),
('Human Support Escalation Pathway','capacity','Escalation pathway may create unsustainable staff demand',4,4,3,'operations','active'),
('Status Visibility Dashboard','data_quality','Dashboard may show stale or misleading status information',5,3,3,'engineering','active'),
('Exception Handling Service Blueprint','governance','Exception ownership may remain unclear across roles',4,4,4,'program_owner','active'),
('Plain-Language Eligibility Guide','equity','Guide may work for average cases but fail complex edge cases',4,3,4,'research_lead','active');
