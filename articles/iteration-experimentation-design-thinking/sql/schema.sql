-- SQLite schema for professional iteration and experimentation analysis.
-- Run:
--   sqlite3 outputs/iteration_experimentation.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS experiment_scores;
DROP TABLE IF EXISTS scenario_weights;
DROP TABLE IF EXISTS experiment_ethics_review;
DROP TABLE IF EXISTS experiments;

CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    experiment_name TEXT NOT NULL UNIQUE,
    learning_gain REAL NOT NULL CHECK (learning_gain BETWEEN 1 AND 10),
    update_flexibility REAL NOT NULL CHECK (update_flexibility BETWEEN 1 AND 10),
    expected_improvement REAL NOT NULL CHECK (expected_improvement BETWEEN 1 AND 10),
    residual_risk REAL NOT NULL CHECK (residual_risk BETWEEN 1 AND 10),
    ethical_risk REAL CHECK (ethical_risk BETWEEN 1 AND 10),
    operational_risk REAL CHECK (operational_risk BETWEEN 1 AND 10),
    interpretive_risk REAL CHECK (interpretive_risk BETWEEN 1 AND 10),
    scaling_risk REAL CHECK (scaling_risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    team_confidence REAL CHECK (team_confidence BETWEEN 0 AND 1),
    implementation_complexity REAL CHECK (implementation_complexity BETWEEN 1 AND 10),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    learning_gain_weight REAL NOT NULL CHECK (learning_gain_weight >= 0),
    update_flexibility_weight REAL NOT NULL CHECK (update_flexibility_weight >= 0),
    expected_improvement_weight REAL NOT NULL CHECK (expected_improvement_weight >= 0),
    residual_risk_weight REAL NOT NULL CHECK (residual_risk_weight >= 0),
    CHECK (
        ABS(
            learning_gain_weight +
            update_flexibility_weight +
            expected_improvement_weight +
            residual_risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE experiment_scores (
    score_id INTEGER PRIMARY KEY,
    experiment_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    experiment_value REAL NOT NULL,
    risk_index REAL,
    confidence_adjusted_value REAL,
    rank_in_scenario INTEGER,
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id),
    FOREIGN KEY (scenario_id) REFERENCES scenario_weights(scenario_id)
);

CREATE TABLE experiment_ethics_review (
    ethics_id INTEGER PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    requires_informed_consent REAL CHECK (requires_informed_consent BETWEEN 0 AND 1),
    participant_burden REAL CHECK (participant_burden BETWEEN 0 AND 1),
    privacy_sensitivity REAL CHECK (privacy_sensitivity BETWEEN 0 AND 1),
    power_asymmetry REAL CHECK (power_asymmetry BETWEEN 0 AND 1),
    review_priority REAL CHECK (review_priority BETWEEN 0 AND 1),
    notes TEXT
);

INSERT INTO experiments (
    experiment_name,
    learning_gain,
    update_flexibility,
    expected_improvement,
    residual_risk,
    ethical_risk,
    operational_risk,
    interpretive_risk,
    scaling_risk,
    evidence_quality,
    team_confidence,
    implementation_complexity
)
VALUES
('Low-Fidelity Service Simulation', 8.5, 8.8, 8.0, 3.5, 2.8, 3.4, 3.7, 4.0, 0.76, 0.78, 4.2),
('Limited Workflow Pilot', 8.2, 7.0, 8.4, 4.4, 3.6, 5.2, 4.2, 5.8, 0.78, 0.76, 6.5),
('A/B Message Framing Test', 7.6, 8.4, 7.8, 3.8, 3.1, 3.2, 4.7, 4.1, 0.70, 0.72, 3.8),
('Cross-Functional Process Trial', 8.1, 7.5, 8.3, 4.1, 3.5, 5.0, 4.1, 5.3, 0.74, 0.75, 6.8),
('Shadow-Mode Digital Service Test', 8.4, 7.8, 8.2, 4.6, 4.8, 4.4, 4.5, 5.7, 0.72, 0.70, 7.2),
('Concierge Support Prototype', 8.7, 8.1, 8.5, 3.9, 3.9, 4.2, 3.8, 5.4, 0.80, 0.82, 5.9),
('Staged Policy Pilot', 8.3, 6.8, 8.8, 5.2, 5.0, 5.6, 4.6, 6.2, 0.73, 0.71, 7.6);

INSERT INTO scenario_weights (
    scenario_name,
    learning_gain_weight,
    update_flexibility_weight,
    expected_improvement_weight,
    residual_risk_weight
)
VALUES
('Balanced', 0.35, 0.25, 0.25, 0.15),
('Learning First', 0.50, 0.20, 0.20, 0.10),
('Flexibility First', 0.20, 0.50, 0.20, 0.10),
('Improvement First', 0.20, 0.20, 0.45, 0.15),
('Risk Sensitive', 0.25, 0.20, 0.20, 0.35),
('Implementation Aware', 0.25, 0.25, 0.30, 0.20),
('Ethics Sensitive', 0.30, 0.20, 0.20, 0.30),
('Scaling Aware', 0.25, 0.20, 0.35, 0.20);

INSERT INTO experiment_ethics_review (
    experiment_name,
    requires_informed_consent,
    participant_burden,
    privacy_sensitivity,
    power_asymmetry,
    review_priority,
    notes
)
VALUES
('Low-Fidelity Service Simulation', 0, 0.30, 0.25, 0.35, 0.32, 'Low-risk simulation but should avoid misleading participants.'),
('Limited Workflow Pilot', 1, 0.55, 0.45, 0.50, 0.52, 'May affect staff workload and service access.'),
('A/B Message Framing Test', 0, 0.35, 0.40, 0.42, 0.39, 'Needs care around behavioral influence and interpretation.'),
('Cross-Functional Process Trial', 1, 0.50, 0.35, 0.48, 0.47, 'Workflow changes may redistribute labor.'),
('Shadow-Mode Digital Service Test', 1, 0.45, 0.75, 0.62, 0.62, 'High data-governance and transparency sensitivity.'),
('Concierge Support Prototype', 1, 0.48, 0.38, 0.45, 0.46, 'Potential inequity if high-touch support is temporary.'),
('Staged Policy Pilot', 1, 0.70, 0.65, 0.72, 0.70, 'High-stakes pilot requires strong governance and safeguards.');
