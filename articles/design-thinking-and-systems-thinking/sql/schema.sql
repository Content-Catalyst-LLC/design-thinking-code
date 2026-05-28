-- SQLite schema for professional design thinking and systems thinking analysis.
-- Run:
--   sqlite3 outputs/system_design.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS system_design_scores;
DROP TABLE IF EXISTS system_design_scenario_weights;
DROP TABLE IF EXISTS feedback_dynamics;
DROP TABLE IF EXISTS system_intervention_risk_register;
DROP TABLE IF EXISTS system_intervention_portfolio;

CREATE TABLE system_intervention_portfolio (
    intervention_id INTEGER PRIMARY KEY,
    intervention_name TEXT NOT NULL UNIQUE,
    intervention_type TEXT NOT NULL,
    leverage_level TEXT NOT NULL,
    human_value REAL NOT NULL CHECK (human_value BETWEEN 1 AND 10),
    system_leverage REAL NOT NULL CHECK (system_leverage BETWEEN 1 AND 10),
    feasibility REAL NOT NULL CHECK (feasibility BETWEEN 1 AND 10),
    equity_sensitivity REAL NOT NULL CHECK (equity_sensitivity BETWEEN 1 AND 10),
    durability REAL NOT NULL CHECK (durability BETWEEN 1 AND 10),
    risk REAL NOT NULL CHECK (risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    stakeholder_coverage REAL CHECK (stakeholder_coverage BETWEEN 0 AND 1),
    context_complexity REAL CHECK (context_complexity BETWEEN 1 AND 10),
    delay_sensitivity REAL CHECK (delay_sensitivity BETWEEN 0 AND 1),
    burden_shift_risk REAL CHECK (burden_shift_risk BETWEEN 1 AND 10)
);

CREATE TABLE system_design_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    human_value_weight REAL NOT NULL CHECK (human_value_weight >= 0),
    system_leverage_weight REAL NOT NULL CHECK (system_leverage_weight >= 0),
    feasibility_weight REAL NOT NULL CHECK (feasibility_weight >= 0),
    equity_sensitivity_weight REAL NOT NULL CHECK (equity_sensitivity_weight >= 0),
    durability_weight REAL NOT NULL CHECK (durability_weight >= 0),
    risk_weight REAL NOT NULL CHECK (risk_weight >= 0),
    CHECK (
        ABS(
            human_value_weight +
            system_leverage_weight +
            feasibility_weight +
            equity_sensitivity_weight +
            durability_weight +
            risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE system_design_scores (
    score_id INTEGER PRIMARY KEY,
    intervention_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    system_design_value REAL NOT NULL,
    evidence_adjusted_value REAL NOT NULL,
    context_adjusted_value REAL NOT NULL,
    evidence_strength REAL NOT NULL,
    learning_priority REAL NOT NULL,
    deep_leverage_index REAL NOT NULL,
    burden_shift_index REAL NOT NULL,
    FOREIGN KEY (intervention_id) REFERENCES system_intervention_portfolio(intervention_id),
    FOREIGN KEY (scenario_id) REFERENCES system_design_scenario_weights(scenario_id)
);

CREATE TABLE feedback_dynamics (
    feedback_id INTEGER PRIMARY KEY,
    intervention_name TEXT NOT NULL,
    period INTEGER NOT NULL,
    intervention_intensity REAL NOT NULL,
    visible_performance REAL NOT NULL,
    adaptation_pressure REAL NOT NULL,
    system_burden REAL NOT NULL,
    equity_gap REAL NOT NULL,
    trust_score REAL NOT NULL,
    queue_pressure REAL NOT NULL,
    implementation_drift REAL NOT NULL
);

CREATE TABLE system_intervention_risk_register (
    risk_id INTEGER PRIMARY KEY,
    intervention_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO system_intervention_portfolio (
    intervention_name, intervention_type, leverage_level,
    human_value, system_leverage, feasibility, equity_sensitivity, durability,
    risk, evidence_quality, stakeholder_coverage, context_complexity,
    delay_sensitivity, burden_shift_risk
)
VALUES
('Service Navigation Redesign','service_redesign','workflow',8.7,6.8,8.1,7.9,7.5,3.5,0.78,0.74,5.0,0.35,3.9),
('Eligibility Rule Simplification','policy_rule','rule',8.1,8.6,6.9,8.2,8.3,4.7,0.74,0.68,6.7,0.48,4.2),
('Information Flow Dashboard','information_flow','information_flow',7.2,8.2,7.8,7.4,7.6,4.0,0.77,0.70,5.8,0.42,3.8),
('Cross-Agency Referral Protocol','coordination_protocol','governance',7.8,8.4,6.7,7.8,8.1,5.1,0.72,0.71,7.1,0.55,4.9),
('Participatory Governance Review','governance_change','governance',7.6,8.7,6.3,8.8,8.5,5.3,0.70,0.82,7.4,0.58,4.4),
('Community Support Infrastructure','support_infrastructure','infrastructure',8.4,8.0,7.1,8.6,8.0,4.6,0.76,0.80,6.4,0.50,3.7),
('Burden-Aware Intake Redesign','service_redesign','workflow',8.6,7.4,7.7,8.5,7.6,4.1,0.79,0.78,5.6,0.40,3.4),
('Institutional Learning Loop','learning_system','feedback_loop',7.7,8.8,7.0,8.0,8.6,4.8,0.75,0.77,6.8,0.62,4.0);

INSERT INTO system_design_scenario_weights (
    scenario_name,
    human_value_weight,
    system_leverage_weight,
    feasibility_weight,
    equity_sensitivity_weight,
    durability_weight,
    risk_weight
)
VALUES
('Balanced',0.24,0.26,0.18,0.14,0.12,0.06),
('Human Centered',0.40,0.20,0.16,0.10,0.10,0.04),
('Leverage First',0.16,0.44,0.14,0.10,0.10,0.06),
('Feasibility First',0.20,0.18,0.36,0.10,0.10,0.06),
('Equity Sensitive',0.18,0.22,0.14,0.34,0.08,0.04),
('Durability First',0.18,0.22,0.14,0.10,0.32,0.04),
('Risk Sensitive',0.20,0.22,0.16,0.12,0.10,0.20),
('Deep Leverage',0.14,0.50,0.10,0.12,0.10,0.04);

INSERT INTO system_intervention_risk_register (
    intervention_name, risk_category, risk_description, severity, likelihood, detectability, mitigation_owner, mitigation_status
)
VALUES
('Service Navigation Redesign','local_optimization','Touchpoint improvements may leave upstream eligibility burdens untouched',4,3,3,'service_owner','active'),
('Eligibility Rule Simplification','policy_complexity','Simplification may create difficult edge cases requiring discretion and appeals',5,3,4,'policy_owner','active'),
('Information Flow Dashboard','metric_distortion','Dashboard visibility may encourage optimization of visible metrics rather than meaningful outcomes',4,3,4,'evaluation_lead','active'),
('Cross-Agency Referral Protocol','coordination_failure','Referral protocol may fail if agencies lack aligned incentives and decision rights',5,4,3,'governance_owner','active'),
('Participatory Governance Review','power_asymmetry','Participation may become symbolic if authority remains unchanged',5,3,4,'governance_owner','active'),
('Community Support Infrastructure','partner_burden','Community partners may absorb institutional burden without adequate funding',5,4,3,'partnership_owner','active'),
('Burden-Aware Intake Redesign','burden_shift','Reduced user effort may increase frontline staff workload without support',4,3,3,'operations_lead','active'),
('Institutional Learning Loop','no_action','Learning loop may produce reports without decision authority or resource commitments',4,3,4,'learning_owner','active');
