-- SQLite schema for professional design-thinking strategy analysis.
-- Run:
--   sqlite3 outputs/strategy_design.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS strategy_option_scores;
DROP TABLE IF EXISTS strategy_scenario_weights;
DROP TABLE IF EXISTS strategic_assumptions;
DROP TABLE IF EXISTS strategy_risk_register;
DROP TABLE IF EXISTS strategic_options;

CREATE TABLE strategic_options (
    option_id INTEGER PRIMARY KEY,
    option_name TEXT NOT NULL UNIQUE,
    option_type TEXT NOT NULL,
    strategic_hypothesis TEXT NOT NULL,
    desirability REAL NOT NULL CHECK (desirability BETWEEN 1 AND 10),
    feasibility REAL NOT NULL CHECK (feasibility BETWEEN 1 AND 10),
    viability REAL NOT NULL CHECK (viability BETWEEN 1 AND 10),
    strategic_alignment REAL NOT NULL CHECK (strategic_alignment BETWEEN 1 AND 10),
    ethical_quality REAL NOT NULL CHECK (ethical_quality BETWEEN 1 AND 10),
    learning_value REAL NOT NULL CHECK (learning_value BETWEEN 1 AND 10),
    implementation_effort REAL NOT NULL CHECK (implementation_effort BETWEEN 1 AND 10),
    strategic_risk REAL NOT NULL CHECK (strategic_risk BETWEEN 1 AND 10),
    capability_gap REAL NOT NULL CHECK (capability_gap BETWEEN 1 AND 10),
    evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 0 AND 1),
    time_to_learn REAL NOT NULL CHECK (time_to_learn BETWEEN 1 AND 10),
    public_value REAL NOT NULL CHECK (public_value BETWEEN 1 AND 10)
);

CREATE TABLE strategy_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    desirability_weight REAL NOT NULL CHECK (desirability_weight >= 0),
    feasibility_weight REAL NOT NULL CHECK (feasibility_weight >= 0),
    viability_weight REAL NOT NULL CHECK (viability_weight >= 0),
    strategic_alignment_weight REAL NOT NULL CHECK (strategic_alignment_weight >= 0),
    ethical_quality_weight REAL NOT NULL CHECK (ethical_quality_weight >= 0),
    learning_value_weight REAL NOT NULL CHECK (learning_value_weight >= 0),
    public_value_weight REAL NOT NULL CHECK (public_value_weight >= 0),
    evidence_strength_weight REAL NOT NULL CHECK (evidence_strength_weight >= 0),
    strategic_risk_weight REAL NOT NULL CHECK (strategic_risk_weight >= 0),
    implementation_effort_weight REAL NOT NULL CHECK (implementation_effort_weight >= 0),
    capability_gap_weight REAL NOT NULL CHECK (capability_gap_weight >= 0),
    time_to_learn_weight REAL NOT NULL CHECK (time_to_learn_weight >= 0),
    CHECK (
        ABS(
            desirability_weight +
            feasibility_weight +
            viability_weight +
            strategic_alignment_weight +
            ethical_quality_weight +
            learning_value_weight +
            public_value_weight +
            evidence_strength_weight +
            strategic_risk_weight +
            implementation_effort_weight +
            capability_gap_weight +
            time_to_learn_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE strategy_option_scores (
    score_id INTEGER PRIMARY KEY,
    option_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    strategic_score REAL NOT NULL,
    portfolio_value REAL NOT NULL,
    uncertainty_priority REAL NOT NULL,
    implementation_readiness REAL NOT NULL,
    ethical_public_value_index REAL NOT NULL,
    FOREIGN KEY (option_id) REFERENCES strategic_options(option_id),
    FOREIGN KEY (scenario_id) REFERENCES strategy_scenario_weights(scenario_id)
);

CREATE TABLE strategic_assumptions (
    assumption_id INTEGER PRIMARY KEY,
    option_name TEXT NOT NULL,
    assumption TEXT NOT NULL,
    assumption_type TEXT NOT NULL,
    importance REAL NOT NULL CHECK (importance BETWEEN 0 AND 1),
    confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    test_cost REAL NOT NULL CHECK (test_cost BETWEEN 0 AND 1),
    time_to_test REAL NOT NULL CHECK (time_to_test BETWEEN 0 AND 10),
    ethical_sensitivity REAL NOT NULL CHECK (ethical_sensitivity BETWEEN 0 AND 1),
    decision_threshold REAL NOT NULL CHECK (decision_threshold BETWEEN 0 AND 1),
    current_evidence TEXT
);

CREATE TABLE strategy_risk_register (
    risk_id INTEGER PRIMARY KEY,
    option_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO strategic_options (
    option_name, option_type, strategic_hypothesis,
    desirability, feasibility, viability, strategic_alignment, ethical_quality,
    learning_value, implementation_effort, strategic_risk, capability_gap,
    evidence_strength, time_to_learn, public_value
)
VALUES
('Simplify Core Service Journey','core_improvement','Reducing service friction will improve trust completion and retention',8.6,7.4,7.8,8.8,8.2,7.4,6.2,4.2,4.8,0.72,4.0,8.0),
('Launch Assisted Access Model','equity_access','Assisted access will improve completion for high-burden groups',8.8,6.8,7.0,8.4,9.0,8.2,7.0,4.6,5.8,0.66,5.0,9.2),
('Build AI-Supported Research Synthesis','capability_bet','AI-assisted synthesis can increase strategic learning speed if governed carefully',7.4,6.6,7.2,7.8,6.8,8.8,7.6,6.8,6.8,0.54,4.5,7.0),
('Create Community Partnership Channel','partnership_bet','Community partnerships will improve trust problem framing and legitimacy',8.2,6.2,6.8,8.0,8.6,8.0,6.8,5.4,6.4,0.60,6.0,9.0),
('Redesign Onboarding and Adoption System','adoption_bet','Behaviorally informed onboarding will increase adoption and sustained use',8.0,7.2,7.4,8.2,7.8,7.6,6.4,4.8,5.2,0.70,3.5,7.6),
('Develop Strategic Learning Dashboard','learning_capability','Better evidence loops will improve portfolio decisions and adaptation',7.6,7.0,7.0,8.6,7.6,8.6,7.2,5.8,6.0,0.62,4.0,7.4),
('Prototype Public Value Governance Review','governance_bet','Governance review will reduce ethical drift and improve accountable scaling',7.8,6.4,6.6,8.0,9.2,8.4,6.6,5.2,5.6,0.58,5.0,9.4),
('Build Frontline Implementation Lab','implementation_bet','Frontline prototyping will reduce implementation failure and hidden labor',8.4,6.6,7.0,8.4,8.4,8.6,7.4,5.6,6.2,0.64,5.5,8.8);

INSERT INTO strategy_scenario_weights (
    scenario_name, desirability_weight, feasibility_weight, viability_weight,
    strategic_alignment_weight, ethical_quality_weight, learning_value_weight,
    public_value_weight, evidence_strength_weight, strategic_risk_weight,
    implementation_effort_weight, capability_gap_weight, time_to_learn_weight
)
VALUES
('Balanced',0.17,0.13,0.13,0.16,0.11,0.10,0.08,0.05,0.03,0.02,0.01,0.01),
('Public Value First',0.13,0.10,0.09,0.14,0.18,0.10,0.20,0.03,0.01,0.01,0.00,0.01),
('Implementation Ready',0.14,0.18,0.16,0.14,0.08,0.06,0.06,0.06,0.02,0.05,0.04,0.01),
('Learning First',0.12,0.10,0.10,0.12,0.08,0.24,0.06,0.08,0.03,0.02,0.01,0.04),
('Ethics and Legitimacy',0.12,0.09,0.09,0.14,0.24,0.08,0.16,0.03,0.02,0.01,0.01,0.01),
('Risk Sensitive',0.14,0.14,0.14,0.15,0.10,0.08,0.07,0.06,0.07,0.03,0.01,0.01);
