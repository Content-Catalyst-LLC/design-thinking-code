-- SQLite schema for professional organizational innovation analysis.
-- Run:
--   sqlite3 outputs/organizational_innovation.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS innovation_scores;
DROP TABLE IF EXISTS innovation_scenario_weights;
DROP TABLE IF EXISTS prototype_learning_rounds;
DROP TABLE IF EXISTS organizational_friction;
DROP TABLE IF EXISTS innovation_risk_register;
DROP TABLE IF EXISTS innovation_concepts;

CREATE TABLE innovation_concepts (
    concept_id INTEGER PRIMARY KEY,
    concept_name TEXT NOT NULL UNIQUE,
    concept_type TEXT NOT NULL,
    organizational_domain TEXT NOT NULL,
    desirability REAL NOT NULL CHECK (desirability BETWEEN 1 AND 10),
    feasibility REAL NOT NULL CHECK (feasibility BETWEEN 1 AND 10),
    viability REAL NOT NULL CHECK (viability BETWEEN 1 AND 10),
    equity REAL NOT NULL CHECK (equity BETWEEN 1 AND 10),
    learning_value REAL NOT NULL CHECK (learning_value BETWEEN 1 AND 10),
    implementation_readiness REAL NOT NULL CHECK (implementation_readiness BETWEEN 1 AND 10),
    risk REAL NOT NULL CHECK (risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    stakeholder_coverage REAL CHECK (stakeholder_coverage BETWEEN 0 AND 1),
    technical_complexity REAL CHECK (technical_complexity BETWEEN 1 AND 10),
    organizational_complexity REAL CHECK (organizational_complexity BETWEEN 1 AND 10),
    ethical_risk REAL CHECK (ethical_risk BETWEEN 1 AND 10)
);

CREATE TABLE innovation_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    desirability_weight REAL NOT NULL CHECK (desirability_weight >= 0),
    feasibility_weight REAL NOT NULL CHECK (feasibility_weight >= 0),
    viability_weight REAL NOT NULL CHECK (viability_weight >= 0),
    equity_weight REAL NOT NULL CHECK (equity_weight >= 0),
    learning_value_weight REAL NOT NULL CHECK (learning_value_weight >= 0),
    implementation_readiness_weight REAL NOT NULL CHECK (implementation_readiness_weight >= 0),
    risk_weight REAL NOT NULL CHECK (risk_weight >= 0),
    CHECK (
        ABS(
            desirability_weight +
            feasibility_weight +
            viability_weight +
            equity_weight +
            learning_value_weight +
            implementation_readiness_weight +
            risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE innovation_scores (
    score_id INTEGER PRIMARY KEY,
    concept_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    design_value REAL NOT NULL,
    evidence_adjusted_value REAL NOT NULL,
    evidence_strength REAL NOT NULL,
    implementation_resilience REAL NOT NULL,
    ethical_innovation_index REAL NOT NULL,
    organizational_learning_index REAL NOT NULL,
    learning_priority REAL NOT NULL,
    portfolio_strength REAL NOT NULL,
    FOREIGN KEY (concept_id) REFERENCES innovation_concepts(concept_id),
    FOREIGN KEY (scenario_id) REFERENCES innovation_scenario_weights(scenario_id)
);

CREATE TABLE prototype_learning_rounds (
    learning_id INTEGER PRIMARY KEY,
    concept_name TEXT NOT NULL,
    round INTEGER NOT NULL,
    adoption_likelihood REAL NOT NULL,
    user_friction REAL NOT NULL,
    trust_score REAL NOT NULL,
    operational_burden REAL NOT NULL,
    equity_score REAL NOT NULL,
    task_success_rate REAL NOT NULL,
    cycle_time REAL NOT NULL,
    employee_confidence REAL NOT NULL
);

CREATE TABLE organizational_friction (
    friction_id INTEGER PRIMARY KEY,
    concept_name TEXT NOT NULL,
    silo_friction REAL NOT NULL,
    decision_latency REAL NOT NULL,
    legacy_system_constraint REAL NOT NULL,
    metric_misalignment REAL NOT NULL,
    training_gap REAL NOT NULL,
    ownership_ambiguity REAL NOT NULL,
    frontline_workload REAL NOT NULL,
    governance_gap REAL NOT NULL
);

CREATE TABLE innovation_risk_register (
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

INSERT INTO innovation_concepts (
    concept_name, concept_type, organizational_domain,
    desirability, feasibility, viability, equity, learning_value, implementation_readiness,
    risk, evidence_quality, stakeholder_coverage, technical_complexity, organizational_complexity, ethical_risk
)
VALUES
('Service Workflow Redesign','service_design','operations',8.6,7.3,7.7,8.1,8.4,7.2,3.6,0.76,0.72,4.8,5.5,3.8),
('Self-Service Support Portal','digital_service','customer_support',7.9,8.5,8.2,7.1,7.2,8.0,4.1,0.72,0.66,5.4,5.0,4.2),
('AI Triage Assistant','ai_assisted_workflow','service_operations',6.8,5.9,7.5,5.8,8.8,5.6,6.8,0.64,0.58,8.2,7.1,7.8),
('Onboarding Simplification','employee_experience','people_operations',9.0,8.2,8.1,8.5,7.6,8.1,3.4,0.78,0.80,4.4,5.1,3.5),
('Cross-Functional Escalation Model','operating_model','cross_functional',8.2,6.8,7.4,7.8,8.6,6.5,5.1,0.70,0.70,4.9,7.6,4.7),
('Employee Knowledge Base Redesign','knowledge_system','organizational_learning',8.4,7.8,7.9,8.2,7.5,7.4,4.0,0.74,0.76,5.8,5.9,3.6),
('Customer Recovery Playbook','service_recovery','customer_experience',8.7,7.6,8.0,8.0,7.8,7.1,3.8,0.75,0.74,4.6,6.0,4.0),
('Manager Decision-Support Dashboard','decision_support','management_systems',7.4,6.9,7.8,6.8,8.2,6.3,5.7,0.68,0.62,7.5,6.6,6.4),
('Accessibility-First Service Redesign','inclusive_design','customer_experience',8.8,7.0,7.6,9.2,8.1,6.8,4.3,0.73,0.82,5.6,6.4,3.7),
('Innovation Governance Cadence','governance_model','innovation_management',7.8,7.4,8.0,7.9,8.7,7.0,4.5,0.71,0.69,4.2,7.0,4.4);

INSERT INTO innovation_scenario_weights (
    scenario_name,
    desirability_weight,
    feasibility_weight,
    viability_weight,
    equity_weight,
    learning_value_weight,
    implementation_readiness_weight,
    risk_weight
)
VALUES
('Balanced',0.22,0.16,0.16,0.18,0.12,0.10,0.06),
('Feasibility First',0.16,0.34,0.14,0.12,0.08,0.10,0.06),
('Equity First',0.16,0.12,0.12,0.34,0.10,0.10,0.06),
('Growth First',0.30,0.12,0.28,0.08,0.08,0.08,0.06),
('Learning First',0.16,0.12,0.12,0.12,0.34,0.08,0.06),
('Implementation First',0.14,0.18,0.14,0.12,0.08,0.28,0.06),
('Risk Sensitive',0.20,0.15,0.15,0.16,0.10,0.08,0.16),
('Responsible Innovation',0.16,0.12,0.12,0.30,0.14,0.08,0.08);

INSERT INTO innovation_risk_register (
    concept_name, risk_category, risk_description, severity, likelihood, detectability, mitigation_owner, mitigation_status
)
VALUES
('Service Workflow Redesign','burden_shift','Workflow redesign may shift hidden labor onto frontline employees if backstage capacity is not redesigned',4,3,3,'operations_owner','active'),
('Self-Service Support Portal','digital_exclusion','Portal may improve efficiency for confident users while excluding users needing assisted service',4,4,3,'service_design_owner','active'),
('AI Triage Assistant','algorithmic_harm','AI triage may encode bias or reduce contestability in service routing decisions',5,4,4,'ai_governance_owner','active'),
('Onboarding Simplification','oversimplification','Simplification may omit role-specific context needed for complex employee situations',3,3,3,'people_operations_owner','active'),
('Cross-Functional Escalation Model','authority_conflict','Escalation model may fail if decision rights and accountability remain ambiguous',4,4,4,'transformation_owner','active'),
('Employee Knowledge Base Redesign','knowledge_staleness','Knowledge base may decay without ownership review cadence and governance',4,3,3,'knowledge_owner','active'),
('Customer Recovery Playbook','script_rigidity','Playbook may reduce discretion or dignity if treated as compliance script rather than recovery guide',4,3,3,'customer_experience_owner','active'),
('Manager Decision-Support Dashboard','metric_tunnel_vision','Dashboard may privilege measurable efficiency over trust equity and employee burden',5,3,4,'analytics_governance_owner','active'),
('Accessibility-First Service Redesign','token_inclusion','Accessibility work may be symbolic if disabled users and high-burden groups lack decision influence',5,3,4,'inclusive_design_owner','active'),
('Innovation Governance Cadence','innovation_theater','Governance cadence may become reporting theater without decision authority or funding pathways',4,4,3,'innovation_governance_owner','active');
