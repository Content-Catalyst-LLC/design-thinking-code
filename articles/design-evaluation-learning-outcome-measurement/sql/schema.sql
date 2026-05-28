-- SQLite schema for professional design evaluation and learning analysis.
-- Run:
--   sqlite3 outputs/design_evaluation.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS evaluation_scores;
DROP TABLE IF EXISTS evaluation_scenario_weights;
DROP TABLE IF EXISTS outcome_timeseries;
DROP TABLE IF EXISTS learning_agenda;
DROP TABLE IF EXISTS evaluation_risk_register;
DROP TABLE IF EXISTS evaluation_portfolio;

CREATE TABLE evaluation_portfolio (
    intervention_id INTEGER PRIMARY KEY,
    intervention_name TEXT NOT NULL UNIQUE,
    intervention_type TEXT NOT NULL,
    evaluation_stage TEXT NOT NULL,
    outcome_improvement REAL NOT NULL CHECK (outcome_improvement BETWEEN 1 AND 10),
    burden_reduction REAL NOT NULL CHECK (burden_reduction BETWEEN 1 AND 10),
    equity_performance REAL NOT NULL CHECK (equity_performance BETWEEN 1 AND 10),
    trust_improvement REAL NOT NULL CHECK (trust_improvement BETWEEN 1 AND 10),
    durability REAL NOT NULL CHECK (durability BETWEEN 1 AND 10),
    operational_cost REAL NOT NULL CHECK (operational_cost BETWEEN 1 AND 10),
    residual_risk REAL NOT NULL CHECK (residual_risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    stakeholder_coverage REAL CHECK (stakeholder_coverage BETWEEN 0 AND 1),
    method_triangulation REAL CHECK (method_triangulation BETWEEN 0 AND 1),
    uncertainty REAL CHECK (uncertainty BETWEEN 0 AND 1),
    baseline_quality REAL CHECK (baseline_quality BETWEEN 1 AND 10),
    current_quality REAL CHECK (current_quality BETWEEN 1 AND 10)
);

CREATE TABLE evaluation_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    outcome_improvement_weight REAL NOT NULL CHECK (outcome_improvement_weight >= 0),
    burden_reduction_weight REAL NOT NULL CHECK (burden_reduction_weight >= 0),
    equity_performance_weight REAL NOT NULL CHECK (equity_performance_weight >= 0),
    trust_improvement_weight REAL NOT NULL CHECK (trust_improvement_weight >= 0),
    durability_weight REAL NOT NULL CHECK (durability_weight >= 0),
    penalty_weight REAL NOT NULL CHECK (penalty_weight >= 0),
    CHECK (
        ABS(
            outcome_improvement_weight +
            burden_reduction_weight +
            equity_performance_weight +
            trust_improvement_weight +
            durability_weight +
            penalty_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE evaluation_scores (
    score_id INTEGER PRIMARY KEY,
    intervention_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    evaluation_value REAL NOT NULL,
    evidence_adjusted_value REAL NOT NULL,
    evidence_strength REAL NOT NULL,
    learning_priority REAL NOT NULL,
    accountability_index REAL NOT NULL,
    learning_value REAL NOT NULL,
    FOREIGN KEY (intervention_id) REFERENCES evaluation_portfolio(intervention_id),
    FOREIGN KEY (scenario_id) REFERENCES evaluation_scenario_weights(scenario_id)
);

CREATE TABLE outcome_timeseries (
    outcome_id INTEGER PRIMARY KEY,
    intervention_name TEXT NOT NULL,
    period INTEGER NOT NULL,
    outcome_score REAL NOT NULL,
    burden_score REAL NOT NULL,
    equity_gap REAL NOT NULL,
    trust_score REAL NOT NULL,
    reliability_score REAL NOT NULL,
    staff_burden REAL NOT NULL,
    support_ticket_rate REAL NOT NULL,
    complaint_rate REAL NOT NULL,
    users_reached INTEGER NOT NULL
);

CREATE TABLE learning_agenda (
    question_id INTEGER PRIMARY KEY,
    learning_question TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    primary_metric TEXT NOT NULL,
    secondary_metric TEXT NOT NULL,
    decision_use TEXT NOT NULL,
    evidence_source TEXT NOT NULL,
    review_cadence TEXT NOT NULL
);

CREATE TABLE evaluation_risk_register (
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

INSERT INTO evaluation_portfolio (
    intervention_name, intervention_type, evaluation_stage,
    outcome_improvement, burden_reduction, equity_performance, trust_improvement,
    durability, operational_cost, residual_risk, evidence_quality, stakeholder_coverage,
    method_triangulation, uncertainty, baseline_quality, current_quality
)
VALUES
('Status Visibility Service','service_system','post_launch',8.1,7.6,7.4,7.8,7.5,4.4,4.2,0.78,0.72,0.74,0.34,6.2,7.9),
('Plain-Language Support Guide','content_prototype','post_launch',7.8,8.2,8.0,7.6,8.0,3.6,3.5,0.82,0.74,0.78,0.28,6.0,8.0),
('Guided Intake Workflow','digital_workflow','phased_rollout',8.3,7.8,7.3,7.4,7.6,4.2,4.4,0.76,0.70,0.72,0.38,5.9,7.8),
('Human Escalation Pathway','service_pathway','multi_site_pilot',8.0,7.4,8.2,8.3,7.7,4.8,4.1,0.79,0.77,0.76,0.32,6.1,8.1),
('Community Navigation Partnership','partnership_model','multi_site_pilot',8.4,8.1,8.7,8.5,7.9,5.1,3.8,0.81,0.80,0.82,0.30,5.8,8.4),
('Learning Dashboard','monitoring_system','post_launch',7.6,7.2,7.5,7.7,8.2,4.0,3.9,0.77,0.73,0.75,0.36,6.3,7.7),
('Evaluation Governance Charter','governance_system','early_evaluation',7.4,7.0,8.1,8.0,8.5,3.8,3.6,0.80,0.76,0.79,0.31,5.7,7.8),
('Equity Outcome Review Loop','equity_governance','post_launch',7.7,7.5,8.8,8.2,8.1,4.3,3.7,0.83,0.82,0.84,0.27,5.6,8.3);

INSERT INTO evaluation_scenario_weights (
    scenario_name,
    outcome_improvement_weight,
    burden_reduction_weight,
    equity_performance_weight,
    trust_improvement_weight,
    durability_weight,
    penalty_weight
)
VALUES
('Balanced',0.24,0.20,0.20,0.16,0.14,0.06),
('Outcome First',0.42,0.16,0.16,0.12,0.10,0.04),
('Burden Sensitive',0.18,0.38,0.18,0.12,0.10,0.04),
('Equity Sensitive',0.18,0.16,0.38,0.12,0.10,0.06),
('Trust Sensitive',0.18,0.16,0.16,0.34,0.10,0.06),
('Durability First',0.18,0.16,0.16,0.12,0.34,0.04),
('Cost Risk Sensitive',0.20,0.18,0.18,0.14,0.10,0.20),
('Evidence Sensitive',0.22,0.18,0.20,0.14,0.18,0.08);

INSERT INTO learning_agenda (
    learning_question, claim_type, primary_metric, secondary_metric, decision_use, evidence_source, review_cadence
)
VALUES
('Did the intervention improve the outcome it targeted?','outcome','outcome_score','current_quality','continue_revise_or_stop','administrative_data','quarterly'),
('Did burden decrease for users and staff?','burden','burden_score','staff_burden','redesign_support_or_workflow','journey_data_and_staff_logs','monthly'),
('Did equity gaps narrow?','equity','equity_gap','equity_performance','investigate_subgroups_and_adapt','equity_monitoring','monthly'),
('Did trust improve without exceeding reliability?','trust','trust_score','reliability_score','adjust_transparency_and_support','surveys_and_interviews','quarterly'),
('Did support demand fall or shift?','operations','support_ticket_rate','complaint_rate','adjust_training_and_help_channels','support_logs','monthly'),
('Is evidence strong enough for scale?','evidence','evidence_quality','method_triangulation','scale_pause_or_extend_evaluation','evaluation_review','quarterly'),
('Did unintended consequences appear?','risk','residual_risk','complaint_rate','escalate_review_or_redesign','risk_register_and_qualitative_review','monthly');

INSERT INTO evaluation_risk_register (
    intervention_name, risk_category, risk_description, severity, likelihood, detectability, mitigation_owner, mitigation_status
)
VALUES
('Status Visibility Service','data_quality','Stale status information may reduce trust and increase escalation',5,3,3,'data_steward','active'),
('Plain-Language Support Guide','oversimplification','Simplification may omit important edge-case or eligibility nuance',4,3,3,'content_owner','active'),
('Guided Intake Workflow','burden_shift','Digital workflow may shift work to users with lower access or confidence',5,3,4,'equity_lead','active'),
('Human Escalation Pathway','capacity','Escalation pathway may create unsustainable frontline workload',4,4,3,'operations','active'),
('Community Navigation Partnership','dependency','Intervention may depend on community partners without adequate support',5,3,4,'partnership_owner','active'),
('Learning Dashboard','metric_distortion','Dashboard metrics may encourage optimization of visible indicators only',4,3,4,'evaluation_lead','active'),
('Evaluation Governance Charter','authority_gap','Findings may not reach decision-makers with authority to act',4,3,3,'governance_owner','active'),
('Equity Outcome Review Loop','privacy','Equity monitoring may expose sensitive subgroup information if poorly governed',5,2,4,'privacy_owner','active');
