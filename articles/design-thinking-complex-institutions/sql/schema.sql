-- SQLite schema for professional institutional design-thinking analysis.
-- Run:
--   sqlite3 outputs/institutional_design.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS institutional_design_scores;
DROP VIEW IF EXISTS stakeholder_burden_scores;
DROP VIEW IF EXISTS governance_scores;
DROP TABLE IF EXISTS institutional_risk_register;
DROP TABLE IF EXISTS governance_decision_rights;
DROP TABLE IF EXISTS stakeholder_burden;
DROP TABLE IF EXISTS institutional_design_options;

CREATE TABLE institutional_design_options (
    option_id INTEGER PRIMARY KEY,
    option_name TEXT NOT NULL UNIQUE,
    option_type TEXT NOT NULL,
    desirability REAL NOT NULL CHECK (desirability BETWEEN 1 AND 10),
    authority REAL NOT NULL CHECK (authority BETWEEN 1 AND 10),
    capability REAL NOT NULL CHECK (capability BETWEEN 1 AND 10),
    funding REAL NOT NULL CHECK (funding BETWEEN 1 AND 10),
    policy_fit REAL NOT NULL CHECK (policy_fit BETWEEN 1 AND 10),
    governance_strength REAL NOT NULL CHECK (governance_strength BETWEEN 1 AND 10),
    trust_gain REAL NOT NULL CHECK (trust_gain BETWEEN 1 AND 10),
    burden_reduction REAL NOT NULL CHECK (burden_reduction BETWEEN 1 AND 10),
    coordination_complexity REAL NOT NULL CHECK (coordination_complexity BETWEEN 1 AND 10),
    implementation_risk REAL NOT NULL CHECK (implementation_risk BETWEEN 1 AND 10),
    data_readiness REAL NOT NULL CHECK (data_readiness BETWEEN 1 AND 10),
    frontline_fit REAL NOT NULL CHECK (frontline_fit BETWEEN 1 AND 10),
    maintenance_capacity REAL NOT NULL CHECK (maintenance_capacity BETWEEN 1 AND 10),
    equity_priority REAL NOT NULL CHECK (equity_priority BETWEEN 1 AND 10),
    public_value REAL NOT NULL CHECK (public_value BETWEEN 1 AND 10)
);

CREATE TABLE stakeholder_burden (
    stakeholder_id INTEGER PRIMARY KEY,
    stakeholder_group TEXT NOT NULL UNIQUE,
    stakeholder_type TEXT NOT NULL,
    time_burden REAL NOT NULL CHECK (time_burden BETWEEN 1 AND 10),
    cognitive_burden REAL NOT NULL CHECK (cognitive_burden BETWEEN 1 AND 10),
    emotional_burden REAL NOT NULL CHECK (emotional_burden BETWEEN 1 AND 10),
    documentation_burden REAL NOT NULL CHECK (documentation_burden BETWEEN 1 AND 10),
    uncertainty_burden REAL NOT NULL CHECK (uncertainty_burden BETWEEN 1 AND 10),
    coordination_burden REAL NOT NULL CHECK (coordination_burden BETWEEN 1 AND 10),
    accessibility_need REAL NOT NULL CHECK (accessibility_need BETWEEN 0 AND 1),
    trust_gap REAL NOT NULL CHECK (trust_gap BETWEEN 1 AND 10),
    affectedness REAL NOT NULL CHECK (affectedness BETWEEN 0 AND 1),
    voice REAL NOT NULL CHECK (voice BETWEEN 1 AND 10),
    influence REAL NOT NULL CHECK (influence BETWEEN 1 AND 10),
    repair_access REAL NOT NULL CHECK (repair_access BETWEEN 1 AND 10)
);

CREATE TABLE governance_decision_rights (
    domain_id INTEGER PRIMARY KEY,
    decision_domain TEXT NOT NULL UNIQUE,
    owner TEXT NOT NULL,
    approval_authority REAL NOT NULL CHECK (approval_authority BETWEEN 0 AND 1),
    budget_authority REAL NOT NULL CHECK (budget_authority BETWEEN 0 AND 1),
    policy_authority REAL NOT NULL CHECK (policy_authority BETWEEN 0 AND 1),
    data_authority REAL NOT NULL CHECK (data_authority BETWEEN 0 AND 1),
    implementation_authority REAL NOT NULL CHECK (implementation_authority BETWEEN 0 AND 1),
    community_accountability REAL NOT NULL CHECK (community_accountability BETWEEN 0 AND 1),
    escalation_clarity REAL NOT NULL CHECK (escalation_clarity BETWEEN 0 AND 1),
    review_cadence REAL NOT NULL CHECK (review_cadence BETWEEN 0 AND 1),
    maintenance_ownership REAL NOT NULL CHECK (maintenance_ownership BETWEEN 0 AND 1)
);

CREATE TABLE institutional_risk_register (
    risk_id TEXT PRIMARY KEY,
    option_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    repair_difficulty INTEGER NOT NULL CHECK (repair_difficulty BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO institutional_design_options (
    option_name, option_type, desirability, authority, capability, funding, policy_fit,
    governance_strength, trust_gain, burden_reduction, coordination_complexity,
    implementation_risk, data_readiness, frontline_fit, maintenance_capacity,
    equity_priority, public_value
)
VALUES
('Simplify eligibility pathway','policy_service_redesign',8.8,6.4,6.8,6.6,6.0,6.2,8.2,8.6,6.8,5.8,6.0,6.8,6.2,8.4,8.8),
('Create assisted access model','access_service_model',9.0,6.8,6.4,6.2,6.4,6.4,8.8,8.4,7.2,6.2,5.8,7.0,6.4,9.0,9.0),
('Redesign cross-department handoffs','workflow_governance',8.2,5.8,5.6,5.8,6.8,5.6,7.6,7.4,8.6,7.4,6.2,6.0,5.8,7.6,8.0),
('Build institutional learning dashboard','data_learning_system',7.6,7.2,7.0,6.8,7.4,7.2,6.8,6.2,6.4,5.6,7.4,6.6,6.8,6.8,7.4),
('Prototype community accountability board','participatory_governance',8.4,5.4,5.8,5.4,5.8,5.8,9.0,7.8,7.8,6.8,5.6,6.0,5.6,9.2,8.6),
('Modernize legacy case-management data','data_infrastructure',7.8,6.0,5.2,5.0,7.0,6.0,6.4,6.8,8.8,8.0,5.4,5.4,5.0,7.2,7.6),
('Redesign frontline escalation process','frontline_operations',8.6,7.0,7.2,6.6,7.2,7.0,7.8,8.0,6.6,5.4,6.8,8.0,7.0,7.8,8.4),
('Create AI-assisted research synthesis workflow','ai_research_governance',7.4,6.6,6.2,6.0,6.6,6.4,6.6,6.4,7.4,6.6,7.0,6.2,6.4,6.8,7.2),
('Develop burden audit and repair pathway','ethics_accountability',8.8,6.2,6.4,6.0,6.6,6.8,8.6,9.0,7.2,6.0,6.2,7.0,6.6,9.0,8.8),
('Create policy interpretation review board','policy_governance',7.8,5.8,5.8,5.4,7.6,6.4,7.4,7.6,7.8,6.8,6.0,6.2,5.8,8.0,8.2);

INSERT INTO stakeholder_burden (
    stakeholder_group, stakeholder_type, time_burden, cognitive_burden, emotional_burden,
    documentation_burden, uncertainty_burden, coordination_burden, accessibility_need,
    trust_gap, affectedness, voice, influence, repair_access
)
VALUES
('Residents using public service','public_user',7.6,7.8,7.2,8.0,8.2,7.4,0.62,7.0,0.88,4.6,3.8,4.2),
('Disabled users','public_user',8.0,8.2,7.6,7.8,8.4,8.0,0.94,7.6,0.92,4.4,3.6,4.0),
('Limited English users','public_user',7.8,8.0,7.0,7.4,8.0,7.6,0.82,7.2,0.86,4.2,3.4,3.8),
('Frontline staff','staff',7.2,7.0,7.4,6.6,6.8,7.8,0.38,5.8,0.74,6.0,5.4,5.6),
('Middle managers','staff',6.2,6.6,5.8,5.8,6.0,6.8,0.30,4.8,0.58,6.2,6.0,5.8),
('Community advocates','community_partner',6.8,6.6,7.8,6.2,7.4,7.2,0.50,7.8,0.80,5.6,4.8,4.4),
('Technology and data teams','internal_team',5.8,6.8,5.2,5.6,6.2,7.0,0.24,4.2,0.54,6.8,6.2,6.0),
('Legal and compliance teams','internal_team',5.4,6.2,4.8,6.0,5.6,6.4,0.20,3.8,0.50,6.4,6.0,5.8),
('Executive sponsors','leadership',4.8,5.4,4.4,4.6,5.0,5.8,0.18,3.6,0.48,7.2,7.0,6.4);
