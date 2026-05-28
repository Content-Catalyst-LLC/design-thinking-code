-- SQLite schema for professional prototype portfolio analysis.
-- Run:
--   sqlite3 outputs/prototype_portfolio.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS prototype_scores;
DROP TABLE IF EXISTS prototype_scenario_weights;
DROP TABLE IF EXISTS prototype_test_rounds;
DROP TABLE IF EXISTS prototype_risk_register;
DROP TABLE IF EXISTS prototypes;

CREATE TABLE prototypes (
    prototype_id INTEGER PRIMARY KEY,
    prototype_name TEXT NOT NULL UNIQUE,
    prototype_type TEXT NOT NULL,
    fidelity_level TEXT NOT NULL,
    learning_gain REAL NOT NULL CHECK (learning_gain BETWEEN 1 AND 10),
    feasibility_signal REAL NOT NULL CHECK (feasibility_signal BETWEEN 1 AND 10),
    user_response REAL NOT NULL CHECK (user_response BETWEEN 1 AND 10),
    equity_value REAL NOT NULL CHECK (equity_value BETWEEN 1 AND 10),
    implementation_relevance REAL NOT NULL CHECK (implementation_relevance BETWEEN 1 AND 10),
    ethical_risk REAL NOT NULL CHECK (ethical_risk BETWEEN 1 AND 10),
    operational_risk REAL NOT NULL CHECK (operational_risk BETWEEN 1 AND 10),
    technical_risk REAL NOT NULL CHECK (technical_risk BETWEEN 1 AND 10),
    scaling_risk REAL NOT NULL CHECK (scaling_risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    prototype_testability REAL CHECK (prototype_testability BETWEEN 0 AND 1),
    stakeholder_coverage REAL CHECK (stakeholder_coverage BETWEEN 0 AND 1),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prototype_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    learning_gain_weight REAL NOT NULL CHECK (learning_gain_weight >= 0),
    feasibility_signal_weight REAL NOT NULL CHECK (feasibility_signal_weight >= 0),
    user_response_weight REAL NOT NULL CHECK (user_response_weight >= 0),
    equity_value_weight REAL NOT NULL CHECK (equity_value_weight >= 0),
    implementation_relevance_weight REAL NOT NULL CHECK (implementation_relevance_weight >= 0),
    composite_risk_weight REAL NOT NULL CHECK (composite_risk_weight >= 0),
    CHECK (
        ABS(
            learning_gain_weight +
            feasibility_signal_weight +
            user_response_weight +
            equity_value_weight +
            implementation_relevance_weight +
            composite_risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE prototype_scores (
    score_id INTEGER PRIMARY KEY,
    prototype_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    prototype_value REAL NOT NULL,
    composite_risk REAL NOT NULL,
    confidence_adjusted_value REAL NOT NULL,
    prototype_review_priority REAL NOT NULL,
    advance_readiness REAL NOT NULL,
    FOREIGN KEY (prototype_id) REFERENCES prototypes(prototype_id),
    FOREIGN KEY (scenario_id) REFERENCES prototype_scenario_weights(scenario_id)
);

CREATE TABLE prototype_test_rounds (
    round_id INTEGER PRIMARY KEY,
    prototype_name TEXT NOT NULL,
    round INTEGER NOT NULL,
    usability REAL NOT NULL,
    comprehension REAL NOT NULL,
    trust REAL NOT NULL,
    unresolved_friction REAL NOT NULL,
    task_success_rate REAL NOT NULL,
    mean_time_minutes REAL NOT NULL,
    critical_issue_count INTEGER NOT NULL,
    participant_count INTEGER NOT NULL
);

CREATE TABLE prototype_risk_register (
    risk_id INTEGER PRIMARY KEY,
    prototype_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO prototypes (
    prototype_name, prototype_type, fidelity_level,
    learning_gain, feasibility_signal, user_response, equity_value, implementation_relevance,
    ethical_risk, operational_risk, technical_risk, scaling_risk,
    evidence_quality, prototype_testability, stakeholder_coverage
)
VALUES
('Paper Service Blueprint','service_blueprint','low',8.6,7.1,8.0,7.8,7.4,3.8,4.2,2.8,3.6,0.74,0.89,0.72),
('Clickable Interface Mockup','digital_mockup','mid',7.9,8.0,8.3,7.0,7.8,3.6,4.0,4.1,4.0,0.77,0.86,0.68),
('Role-Played Intake Scenario','experience_prototype','low',8.2,7.4,8.5,8.3,7.6,4.2,4.5,3.0,4.4,0.79,0.82,0.75),
('Limited Workflow Pilot','pilot','high',8.0,8.4,7.8,7.7,8.7,4.4,3.8,4.6,4.8,0.82,0.72,0.70),
('Wizard-of-Oz Status Assistant','wizard_of_oz','mid',8.4,7.2,8.2,7.5,7.9,5.1,4.8,5.4,5.2,0.70,0.79,0.64),
('Exception-Case Service Simulation','service_simulation','mid',8.7,7.6,8.4,8.6,8.3,4.3,4.9,3.5,5.0,0.78,0.81,0.78),
('Plain-Language Policy Mockup','policy_prototype','low',8.1,8.2,8.0,8.4,7.9,3.2,3.6,2.6,3.8,0.81,0.88,0.74),
('Operational Tabletop Exercise','governance_prototype','mid',8.3,7.9,7.4,7.8,8.6,4.0,5.2,3.2,5.5,0.76,0.73,0.69);

INSERT INTO prototype_scenario_weights (
    scenario_name,
    learning_gain_weight,
    feasibility_signal_weight,
    user_response_weight,
    equity_value_weight,
    implementation_relevance_weight,
    composite_risk_weight
)
VALUES
('Balanced',0.25,0.18,0.20,0.15,0.12,0.10),
('Learning First',0.45,0.12,0.16,0.12,0.08,0.07),
('Feasibility First',0.16,0.38,0.16,0.10,0.12,0.08),
('User Response First',0.16,0.14,0.38,0.12,0.10,0.10),
('Equity Sensitive',0.18,0.14,0.16,0.35,0.09,0.08),
('Implementation Sensitive',0.16,0.20,0.14,0.12,0.28,0.10),
('Risk Sensitive',0.20,0.16,0.16,0.14,0.09,0.25),
('Pilot Readiness',0.18,0.24,0.16,0.12,0.22,0.08);

INSERT INTO prototype_risk_register (
    prototype_name, risk_category, risk_description, severity, likelihood, detectability, mitigation_owner, mitigation_status
)
VALUES
('Paper Service Blueprint','operational','Backstage steps may be oversimplified in paper representation',3,3,4,'service_design','active'),
('Clickable Interface Mockup','technical','Interactive mockup may hide integration and data-flow complexity',4,3,3,'engineering','active'),
('Role-Played Intake Scenario','ethical','Participants may disclose stressful service experiences during role play',4,3,4,'research_lead','active'),
('Limited Workflow Pilot','scaling','Pilot may work under protected staffing conditions that cannot be sustained',5,4,3,'operations','active'),
('Wizard-of-Oz Status Assistant','ethical','Participants may overtrust simulated automation if status is unclear',5,3,3,'research_lead','active'),
('Exception-Case Service Simulation','operational','Exception cases may reveal unresolved decision-rights conflicts',4,4,4,'program_owner','active'),
('Plain-Language Policy Mockup','policy','Simplified language may conflict with formal eligibility language',4,3,4,'policy_counsel','active'),
('Operational Tabletop Exercise','governance','Decision authority may remain unresolved after simulation',5,4,3,'governance_owner','active');
