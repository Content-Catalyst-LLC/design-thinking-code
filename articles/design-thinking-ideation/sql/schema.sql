-- SQLite schema for professional ideation portfolio analysis.
-- Run:
--   sqlite3 outputs/ideation_portfolio.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS idea_scores;
DROP TABLE IF EXISTS scenario_weights;
DROP TABLE IF EXISTS idea_cluster_map;
DROP TABLE IF EXISTS ideas;

CREATE TABLE ideas (
    idea_id INTEGER PRIMARY KEY,
    idea_name TEXT NOT NULL UNIQUE,
    idea_cluster TEXT NOT NULL,
    desirability REAL NOT NULL CHECK (desirability BETWEEN 1 AND 10),
    feasibility REAL NOT NULL CHECK (feasibility BETWEEN 1 AND 10),
    novelty REAL NOT NULL CHECK (novelty BETWEEN 1 AND 10),
    equity_value REAL NOT NULL CHECK (equity_value BETWEEN 1 AND 10),
    learning_value REAL NOT NULL CHECK (learning_value BETWEEN 1 AND 10),
    residual_risk REAL NOT NULL CHECK (residual_risk BETWEEN 1 AND 10),
    ethical_risk REAL NOT NULL CHECK (ethical_risk BETWEEN 1 AND 10),
    operational_risk REAL NOT NULL CHECK (operational_risk BETWEEN 1 AND 10),
    technical_risk REAL NOT NULL CHECK (technical_risk BETWEEN 1 AND 10),
    scaling_risk REAL NOT NULL CHECK (scaling_risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    prototype_testability REAL CHECK (prototype_testability BETWEEN 0 AND 1),
    implementation_relevance REAL CHECK (implementation_relevance BETWEEN 1 AND 10),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    desirability_weight REAL NOT NULL CHECK (desirability_weight >= 0),
    feasibility_weight REAL NOT NULL CHECK (feasibility_weight >= 0),
    novelty_weight REAL NOT NULL CHECK (novelty_weight >= 0),
    equity_value_weight REAL NOT NULL CHECK (equity_value_weight >= 0),
    learning_value_weight REAL NOT NULL CHECK (learning_value_weight >= 0),
    composite_risk_weight REAL NOT NULL CHECK (composite_risk_weight >= 0),
    CHECK (
        ABS(
            desirability_weight +
            feasibility_weight +
            novelty_weight +
            equity_value_weight +
            learning_value_weight +
            composite_risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE idea_scores (
    score_id INTEGER PRIMARY KEY,
    idea_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    idea_value REAL NOT NULL,
    composite_risk REAL,
    prototype_priority REAL,
    confidence_adjusted_value REAL,
    rank_in_scenario INTEGER,
    FOREIGN KEY (idea_id) REFERENCES ideas(idea_id),
    FOREIGN KEY (scenario_id) REFERENCES scenario_weights(scenario_id)
);

CREATE TABLE idea_cluster_map (
    cluster_id INTEGER PRIMARY KEY,
    idea_name TEXT NOT NULL,
    idea_cluster TEXT NOT NULL,
    cluster_distance REAL CHECK (cluster_distance >= 0),
    stakeholder_groups INTEGER CHECK (stakeholder_groups >= 0),
    methods_supporting INTEGER CHECK (methods_supporting >= 0),
    evidence_source_count INTEGER CHECK (evidence_source_count >= 0),
    notes TEXT
);

INSERT INTO ideas (
    idea_name,
    idea_cluster,
    desirability,
    feasibility,
    novelty,
    equity_value,
    learning_value,
    residual_risk,
    ethical_risk,
    operational_risk,
    technical_risk,
    scaling_risk,
    evidence_quality,
    prototype_testability,
    implementation_relevance
)
VALUES
('Peer Support Navigation Model', 'Human Support Models', 8.4, 7.3, 7.6, 8.1, 8.0, 4.0, 3.4, 4.4, 3.7, 4.2, 0.78, 0.82, 7.9),
('Self-Service Digital Triage', 'Digital Self-Service', 7.8, 8.2, 7.2, 6.8, 7.6, 3.8, 3.7, 3.8, 4.2, 4.0, 0.72, 0.80, 7.6),
('Mobile Outreach Partnership', 'Community Infrastructure', 8.6, 7.0, 8.1, 8.7, 8.2, 4.5, 4.1, 5.1, 3.9, 5.0, 0.80, 0.78, 8.3),
('AI-Assisted Intake Guidance', 'AI-Assisted Guidance', 7.4, 6.8, 8.5, 6.9, 8.4, 5.2, 5.8, 5.0, 5.7, 5.4, 0.68, 0.76, 7.8),
('Status Visibility and Ownership Dashboard', 'Status Transparency', 8.2, 7.6, 7.8, 7.9, 8.1, 4.2, 3.9, 4.6, 4.5, 4.7, 0.76, 0.84, 8.1),
('Community-Based Service Liaison Model', 'Community Infrastructure', 8.7, 6.9, 8.0, 8.8, 8.5, 4.7, 4.0, 5.4, 3.8, 5.2, 0.79, 0.77, 8.4),
('Plain-Language Decision Guide', 'Guidance and Clarity', 8.1, 8.4, 6.9, 8.2, 7.8, 3.4, 2.8, 3.2, 3.1, 3.6, 0.82, 0.88, 7.7),
('Exception Handling Workflow Redesign', 'Operational Redesign', 8.0, 7.1, 7.7, 8.0, 8.3, 4.6, 3.8, 5.8, 4.1, 5.5, 0.77, 0.79, 8.6);

INSERT INTO scenario_weights (
    scenario_name,
    desirability_weight,
    feasibility_weight,
    novelty_weight,
    equity_value_weight,
    learning_value_weight,
    composite_risk_weight
)
VALUES
('Balanced', 0.24, 0.18, 0.18, 0.18, 0.12, 0.10),
('Novelty First', 0.18, 0.12, 0.35, 0.15, 0.10, 0.10),
('Feasibility First', 0.18, 0.35, 0.12, 0.15, 0.10, 0.10),
('Equity First', 0.18, 0.12, 0.12, 0.35, 0.13, 0.10),
('Learning First', 0.18, 0.14, 0.16, 0.17, 0.25, 0.10),
('Risk Sensitive', 0.20, 0.16, 0.14, 0.16, 0.09, 0.25),
('Prototype Oriented', 0.24, 0.22, 0.14, 0.14, 0.18, 0.08),
('Implementation Aware', 0.22, 0.24, 0.12, 0.16, 0.10, 0.16);

INSERT INTO idea_cluster_map (
    idea_name,
    idea_cluster,
    cluster_distance,
    stakeholder_groups,
    methods_supporting,
    evidence_source_count,
    notes
)
VALUES
('Peer Support Navigation Model', 'Human Support Models', 0.18, 5, 4, 21, 'Strongly connected to support and trust insights.'),
('Self-Service Digital Triage', 'Digital Self-Service', 0.25, 4, 3, 18, 'Feasible but may underperform for low-trust stakeholders.'),
('Mobile Outreach Partnership', 'Community Infrastructure', 0.21, 6, 4, 23, 'High equity value but operational partnerships need validation.'),
('AI-Assisted Intake Guidance', 'AI-Assisted Guidance', 0.34, 3, 3, 16, 'High novelty but high ethical and technical review priority.'),
('Status Visibility and Ownership Dashboard', 'Status Transparency', 0.19, 5, 4, 22, 'Strong response to uncertainty and procedural silence.'),
('Community-Based Service Liaison Model', 'Community Infrastructure', 0.22, 6, 4, 24, 'High equity and trust potential; resource model requires testing.'),
('Plain-Language Decision Guide', 'Guidance and Clarity', 0.16, 5, 4, 20, 'Low-risk clarity improvement with strong testability.'),
('Exception Handling Workflow Redesign', 'Operational Redesign', 0.23, 4, 4, 19, 'Strong systems intervention but depends on internal capacity.');
