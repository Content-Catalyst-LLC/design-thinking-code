-- SQLite schema for professional design thinking pathway analysis.
-- Run:
--   sqlite3 outputs/design_thinking.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS pathway_scores;
DROP TABLE IF EXISTS scenario_weights;
DROP TABLE IF EXISTS design_pathways;

CREATE TABLE design_pathways (
    pathway_id INTEGER PRIMARY KEY,
    pathway_name TEXT NOT NULL UNIQUE,
    human_relevance REAL NOT NULL CHECK (human_relevance BETWEEN 1 AND 10),
    feasibility REAL NOT NULL CHECK (feasibility BETWEEN 1 AND 10),
    learning_value REAL NOT NULL CHECK (learning_value BETWEEN 1 AND 10),
    residual_risk REAL NOT NULL CHECK (residual_risk BETWEEN 1 AND 10),
    stakeholder_confidence REAL CHECK (stakeholder_confidence BETWEEN 0 AND 1),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    implementation_complexity REAL CHECK (implementation_complexity BETWEEN 1 AND 10),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    human_relevance_weight REAL NOT NULL CHECK (human_relevance_weight >= 0),
    feasibility_weight REAL NOT NULL CHECK (feasibility_weight >= 0),
    learning_value_weight REAL NOT NULL CHECK (learning_value_weight >= 0),
    residual_risk_weight REAL NOT NULL CHECK (residual_risk_weight >= 0),
    CHECK (
        ABS(
            human_relevance_weight +
            feasibility_weight +
            learning_value_weight +
            residual_risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE pathway_scores (
    score_id INTEGER PRIMARY KEY,
    pathway_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    design_value REAL NOT NULL,
    rank_in_scenario INTEGER,
    FOREIGN KEY (pathway_id) REFERENCES design_pathways(pathway_id),
    FOREIGN KEY (scenario_id) REFERENCES scenario_weights(scenario_id)
);

INSERT INTO design_pathways (
    pathway_name,
    human_relevance,
    feasibility,
    learning_value,
    residual_risk,
    stakeholder_confidence,
    evidence_quality,
    implementation_complexity
)
VALUES
('Service Redesign Pathway', 8.8, 7.4, 8.1, 4.0, 0.78, 0.74, 5.1),
('Digital Platform Pathway', 7.9, 8.3, 7.7, 4.3, 0.70, 0.69, 6.4),
('Workflow Coordination Pathway', 8.2, 7.8, 8.4, 3.8, 0.82, 0.77, 5.8),
('Community Partnership Pathway', 8.6, 7.1, 8.5, 4.2, 0.76, 0.72, 6.0),
('Participatory Governance Pathway', 8.9, 6.8, 8.9, 4.8, 0.73, 0.71, 7.0);

INSERT INTO scenario_weights (
    scenario_name,
    human_relevance_weight,
    feasibility_weight,
    learning_value_weight,
    residual_risk_weight
)
VALUES
('Balanced', 0.35, 0.25, 0.25, 0.15),
('Human First', 0.50, 0.20, 0.20, 0.10),
('Feasibility First', 0.20, 0.50, 0.20, 0.10),
('Learning First', 0.20, 0.20, 0.45, 0.15),
('Risk Sensitive', 0.25, 0.20, 0.20, 0.35),
('Institutional Adoption', 0.25, 0.35, 0.20, 0.20),
('Equity and Inclusion', 0.45, 0.15, 0.25, 0.15);
