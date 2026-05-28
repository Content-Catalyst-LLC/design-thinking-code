-- SQLite schema for professional insight-generation analysis.
-- Run:
--   sqlite3 outputs/insight_generation.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS insight_scores;
DROP TABLE IF EXISTS scenario_weights;
DROP TABLE IF EXISTS insight_evidence_sources;
DROP TABLE IF EXISTS candidate_insights;

CREATE TABLE candidate_insights (
    insight_id INTEGER PRIMARY KEY,
    insight_text TEXT NOT NULL UNIQUE,
    pattern_support REAL NOT NULL CHECK (pattern_support BETWEEN 1 AND 10),
    explanatory_depth REAL NOT NULL CHECK (explanatory_depth BETWEEN 1 AND 10),
    opportunity_value REAL NOT NULL CHECK (opportunity_value BETWEEN 1 AND 10),
    interpretive_risk REAL NOT NULL CHECK (interpretive_risk BETWEEN 1 AND 10),
    sampling_risk REAL CHECK (sampling_risk BETWEEN 1 AND 10),
    confirmation_bias_risk REAL CHECK (confirmation_bias_risk BETWEEN 1 AND 10),
    evidence_thinness_risk REAL CHECK (evidence_thinness_risk BETWEEN 1 AND 10),
    solution_capture_risk REAL CHECK (solution_capture_risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    stakeholder_diversity REAL CHECK (stakeholder_diversity BETWEEN 0 AND 1),
    prototype_testability REAL CHECK (prototype_testability BETWEEN 0 AND 1),
    implementation_relevance REAL CHECK (implementation_relevance BETWEEN 1 AND 10),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    pattern_support_weight REAL NOT NULL CHECK (pattern_support_weight >= 0),
    explanatory_depth_weight REAL NOT NULL CHECK (explanatory_depth_weight >= 0),
    opportunity_value_weight REAL NOT NULL CHECK (opportunity_value_weight >= 0),
    interpretive_risk_weight REAL NOT NULL CHECK (interpretive_risk_weight >= 0),
    CHECK (
        ABS(
            pattern_support_weight +
            explanatory_depth_weight +
            opportunity_value_weight +
            interpretive_risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE insight_scores (
    score_id INTEGER PRIMARY KEY,
    insight_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    insight_value REAL NOT NULL,
    interpretive_risk_index REAL,
    confidence_adjusted_value REAL,
    rank_in_scenario INTEGER,
    FOREIGN KEY (insight_id) REFERENCES candidate_insights(insight_id),
    FOREIGN KEY (scenario_id) REFERENCES scenario_weights(scenario_id)
);

CREATE TABLE insight_evidence_sources (
    evidence_id INTEGER PRIMARY KEY,
    insight_text TEXT NOT NULL,
    evidence_source_count INTEGER CHECK (evidence_source_count >= 0),
    stakeholder_groups INTEGER CHECK (stakeholder_groups >= 0),
    method_count INTEGER CHECK (method_count >= 0),
    contradictory_cases INTEGER CHECK (contradictory_cases >= 0),
    validation_priority REAL CHECK (validation_priority BETWEEN 0 AND 1),
    notes TEXT
);

INSERT INTO candidate_insights (
    insight_text,
    pattern_support,
    explanatory_depth,
    opportunity_value,
    interpretive_risk,
    sampling_risk,
    confirmation_bias_risk,
    evidence_thinness_risk,
    solution_capture_risk,
    evidence_quality,
    stakeholder_diversity,
    prototype_testability,
    implementation_relevance
)
VALUES
('Users want clarity more than feature variety', 8.3, 7.9, 8.1, 3.8, 3.7, 3.8, 3.6, 4.0, 0.74, 0.70, 0.82, 7.9),
('Waiting uncertainty produces more frustration than waiting time itself', 8.7, 8.4, 8.5, 3.6, 3.5, 3.4, 3.5, 3.8, 0.80, 0.82, 0.86, 8.3),
('Staff workarounds reveal hidden system failure points', 8.1, 8.6, 8.3, 4.1, 4.0, 3.8, 4.2, 4.4, 0.78, 0.76, 0.78, 8.5),
('Users interpret procedural silence as institutional indifference', 7.8, 8.2, 7.9, 4.3, 4.4, 4.1, 4.0, 4.6, 0.72, 0.68, 0.75, 7.8),
('People ask for more information when they actually need confidence', 8.0, 8.3, 8.4, 3.9, 3.8, 3.7, 3.9, 4.1, 0.76, 0.74, 0.84, 8.1),
('Drop-off points reveal institutional burden rather than low motivation', 8.4, 8.5, 8.6, 4.2, 4.3, 3.9, 4.2, 4.5, 0.77, 0.79, 0.81, 8.6),
('Repeated calls reveal missing ownership rather than user dependency', 7.9, 8.1, 8.2, 4.0, 4.2, 3.9, 4.0, 4.2, 0.75, 0.73, 0.79, 8.0),
('Avoidance behavior signals trust breakdown more than preference', 7.7, 8.4, 8.0, 4.5, 4.7, 4.2, 4.4, 4.8, 0.71, 0.69, 0.74, 7.7);

INSERT INTO scenario_weights (
    scenario_name,
    pattern_support_weight,
    explanatory_depth_weight,
    opportunity_value_weight,
    interpretive_risk_weight
)
VALUES
('Balanced', 0.30, 0.30, 0.25, 0.15),
('Pattern First', 0.45, 0.20, 0.20, 0.15),
('Explanation First', 0.20, 0.45, 0.20, 0.15),
('Opportunity First', 0.20, 0.20, 0.45, 0.15),
('Risk Sensitive', 0.25, 0.20, 0.20, 0.35),
('Prototype Oriented', 0.25, 0.25, 0.35, 0.15),
('Evidence Sensitive', 0.35, 0.30, 0.20, 0.15),
('Power Aware', 0.25, 0.35, 0.20, 0.20);

INSERT INTO insight_evidence_sources (
    insight_text,
    evidence_source_count,
    stakeholder_groups,
    method_count,
    contradictory_cases,
    validation_priority,
    notes
)
VALUES
('Users want clarity more than feature variety', 18, 4, 3, 2, 0.48, 'Strong usability pattern but should be tested against feature-priority assumptions.'),
('Waiting uncertainty produces more frustration than waiting time itself', 23, 5, 4, 1, 0.42, 'Well-supported across interview and observation evidence.'),
('Staff workarounds reveal hidden system failure points', 20, 3, 4, 3, 0.55, 'Requires frontline validation and operational review.'),
('Users interpret procedural silence as institutional indifference', 15, 4, 3, 4, 0.62, 'High interpretive and trust implications; validate with stakeholders.'),
('People ask for more information when they actually need confidence', 17, 4, 3, 3, 0.54, 'Important distinction between content volume and decision confidence.'),
('Drop-off points reveal institutional burden rather than low motivation', 19, 5, 4, 3, 0.58, 'Needs administrative data and lived-experience triangulation.'),
('Repeated calls reveal missing ownership rather than user dependency', 14, 3, 3, 4, 0.61, 'May require workflow and service ownership mapping.'),
('Avoidance behavior signals trust breakdown more than preference', 13, 4, 3, 5, 0.68, 'High-risk insight; requires careful interpretation and validation.');
