-- SQLite schema for professional implementation and scaling analysis.
-- Run:
--   sqlite3 outputs/implementation_scaling.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS implementation_scores;
DROP TABLE IF EXISTS implementation_scenario_weights;
DROP TABLE IF EXISTS rollout_stage_metrics;
DROP TABLE IF EXISTS implementation_risk_register;
DROP TABLE IF EXISTS implementation_portfolio;

CREATE TABLE implementation_portfolio (
    intervention_id INTEGER PRIMARY KEY,
    intervention_name TEXT NOT NULL UNIQUE,
    intervention_type TEXT NOT NULL,
    implementation_stage TEXT NOT NULL,
    adoption_readiness REAL NOT NULL CHECK (adoption_readiness BETWEEN 1 AND 10),
    operational_fit REAL NOT NULL CHECK (operational_fit BETWEEN 1 AND 10),
    durability REAL NOT NULL CHECK (durability BETWEEN 1 AND 10),
    governance_readiness REAL NOT NULL CHECK (governance_readiness BETWEEN 1 AND 10),
    equity_readiness REAL NOT NULL CHECK (equity_readiness BETWEEN 1 AND 10),
    financial_sustainability REAL NOT NULL CHECK (financial_sustainability BETWEEN 1 AND 10),
    operational_risk REAL NOT NULL CHECK (operational_risk BETWEEN 1 AND 10),
    governance_risk REAL NOT NULL CHECK (governance_risk BETWEEN 1 AND 10),
    technical_risk REAL NOT NULL CHECK (technical_risk BETWEEN 1 AND 10),
    equity_risk REAL NOT NULL CHECK (equity_risk BETWEEN 1 AND 10),
    financial_risk REAL NOT NULL CHECK (financial_risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    stakeholder_coverage REAL CHECK (stakeholder_coverage BETWEEN 0 AND 1),
    context_complexity REAL CHECK (context_complexity BETWEEN 1 AND 10),
    scale_sensitivity REAL CHECK (scale_sensitivity BETWEEN 0 AND 1)
);

CREATE TABLE implementation_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    adoption_readiness_weight REAL NOT NULL CHECK (adoption_readiness_weight >= 0),
    operational_fit_weight REAL NOT NULL CHECK (operational_fit_weight >= 0),
    durability_weight REAL NOT NULL CHECK (durability_weight >= 0),
    governance_readiness_weight REAL NOT NULL CHECK (governance_readiness_weight >= 0),
    equity_readiness_weight REAL NOT NULL CHECK (equity_readiness_weight >= 0),
    financial_sustainability_weight REAL NOT NULL CHECK (financial_sustainability_weight >= 0),
    composite_risk_weight REAL NOT NULL CHECK (composite_risk_weight >= 0),
    CHECK (
        ABS(
            adoption_readiness_weight +
            operational_fit_weight +
            durability_weight +
            governance_readiness_weight +
            equity_readiness_weight +
            financial_sustainability_weight +
            composite_risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE implementation_scores (
    score_id INTEGER PRIMARY KEY,
    intervention_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    implementation_value REAL NOT NULL,
    evidence_adjusted_value REAL NOT NULL,
    scaled_quality_estimate REAL NOT NULL,
    composite_risk REAL NOT NULL,
    implementation_review_priority REAL NOT NULL,
    scale_readiness REAL NOT NULL,
    FOREIGN KEY (intervention_id) REFERENCES implementation_portfolio(intervention_id),
    FOREIGN KEY (scenario_id) REFERENCES implementation_scenario_weights(scenario_id)
);

CREATE TABLE rollout_stage_metrics (
    metric_id INTEGER PRIMARY KEY,
    intervention_name TEXT NOT NULL,
    stage INTEGER NOT NULL,
    adoption_rate REAL NOT NULL,
    staff_compliance REAL NOT NULL,
    service_reliability REAL NOT NULL,
    support_ticket_rate REAL NOT NULL,
    equity_gap REAL NOT NULL,
    mean_resolution_time_hours REAL NOT NULL,
    user_trust REAL NOT NULL,
    staff_burden REAL NOT NULL,
    incident_count INTEGER NOT NULL,
    sites_live INTEGER NOT NULL,
    users_reached INTEGER NOT NULL
);

CREATE TABLE implementation_risk_register (
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

INSERT INTO implementation_portfolio (
    intervention_name, intervention_type, implementation_stage,
    adoption_readiness, operational_fit, durability, governance_readiness,
    equity_readiness, financial_sustainability, operational_risk, governance_risk,
    technical_risk, equity_risk, financial_risk, evidence_quality,
    stakeholder_coverage, context_complexity, scale_sensitivity
)
VALUES
('Digital Intake Workflow','digital_workflow','controlled_pilot',8.3,7.9,7.5,7.2,7.3,7.4,4.1,4.5,4.7,4.2,4.4,0.78,0.72,5.3,0.42),
('Frontline Service Playbook','service_playbook','multi_site_pilot',7.8,8.4,8.1,7.6,7.9,8.0,3.8,3.9,2.8,3.7,3.5,0.82,0.75,4.6,0.31),
('Cross-Team Escalation Protocol','governance_protocol','internal_simulation',7.1,7.6,7.8,8.3,7.5,7.6,4.6,3.7,3.1,4.0,3.8,0.76,0.70,5.1,0.36),
('Community Outreach Scheduling Tool','community_tool','controlled_pilot',8.0,7.2,7.0,7.1,8.5,7.2,4.3,4.4,4.2,3.5,4.6,0.74,0.78,6.0,0.48),
('Status Visibility Service','service_system','phased_rollout',8.2,7.8,7.7,7.4,7.8,7.3,4.0,4.2,4.8,4.1,4.7,0.77,0.71,5.7,0.45),
('Implementation Learning Dashboard','monitoring_system','phased_rollout',7.7,8.1,8.2,8.4,7.6,7.7,3.9,3.6,4.4,3.9,3.8,0.80,0.73,4.8,0.34),
('Training and Support System','training_system','multi_site_pilot',7.9,8.2,8.0,7.8,8.1,7.6,3.7,3.8,3.2,3.6,3.9,0.81,0.77,4.4,0.29),
('Equity Monitoring Protocol','equity_governance','internal_simulation',7.3,7.4,8.3,8.5,8.7,7.4,4.2,3.5,3.4,3.2,4.1,0.79,0.80,5.4,0.33);

INSERT INTO implementation_scenario_weights (
    scenario_name,
    adoption_readiness_weight,
    operational_fit_weight,
    durability_weight,
    governance_readiness_weight,
    equity_readiness_weight,
    financial_sustainability_weight,
    composite_risk_weight
)
VALUES
('Balanced',0.20,0.18,0.18,0.15,0.14,0.10,0.05),
('Adoption First',0.38,0.16,0.14,0.10,0.10,0.08,0.04),
('Operations First',0.14,0.38,0.16,0.12,0.10,0.06,0.04),
('Durability First',0.14,0.16,0.38,0.12,0.10,0.06,0.04),
('Governance First',0.14,0.14,0.14,0.34,0.12,0.08,0.04),
('Equity Sensitive',0.14,0.14,0.14,0.12,0.34,0.08,0.04),
('Financially Constrained',0.14,0.16,0.16,0.12,0.10,0.28,0.04),
('Risk Sensitive',0.16,0.16,0.16,0.12,0.12,0.08,0.20),
('Scale Readiness',0.18,0.18,0.20,0.16,0.14,0.10,0.04);

INSERT INTO implementation_risk_register (
    intervention_name, risk_category, risk_description, severity, likelihood, detectability, mitigation_owner, mitigation_status
)
VALUES
('Digital Intake Workflow','technical','Integration failure could disrupt intake status and downstream routing',5,3,3,'engineering','active'),
('Frontline Service Playbook','adoption','Playbook may be ignored if staff incentives remain aligned with legacy routines',4,3,4,'operations','active'),
('Cross-Team Escalation Protocol','governance','Escalation ownership may remain ambiguous across teams',5,3,3,'program_owner','active'),
('Community Outreach Scheduling Tool','equity','Digital scheduling may exclude users relying on trusted community intermediaries',4,4,3,'equity_lead','active'),
('Status Visibility Service','data_quality','Status information may become stale and reduce trust',5,4,3,'data_steward','active'),
('Implementation Learning Dashboard','measurement','Dashboard metrics may become performative without decision loops',4,3,4,'evaluation_lead','active'),
('Training and Support System','capacity','Training may not survive turnover without dedicated ownership',4,3,3,'training_owner','active'),
('Equity Monitoring Protocol','governance','Equity findings may not trigger accountable decisions',5,3,4,'equity_governance','active');
