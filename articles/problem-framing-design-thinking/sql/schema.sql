-- SQLite schema for professional problem-framing analysis.
-- Run:
--   sqlite3 outputs/problem_framing.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS frame_scores;
DROP TABLE IF EXISTS scenario_weights;
DROP TABLE IF EXISTS counterframes;
DROP TABLE IF EXISTS problem_frames;

CREATE TABLE problem_frames (
    frame_id INTEGER PRIMARY KEY,
    frame_name TEXT NOT NULL UNIQUE,
    explanatory_adequacy REAL NOT NULL CHECK (explanatory_adequacy BETWEEN 1 AND 10),
    stakeholder_coverage REAL NOT NULL CHECK (stakeholder_coverage BETWEEN 1 AND 10),
    opportunity_value REAL NOT NULL CHECK (opportunity_value BETWEEN 1 AND 10),
    framing_risk REAL NOT NULL CHECK (framing_risk BETWEEN 1 AND 10),
    narrowness_risk REAL CHECK (narrowness_risk BETWEEN 1 AND 10),
    stakeholder_exclusion_risk REAL CHECK (stakeholder_exclusion_risk BETWEEN 1 AND 10),
    causality_risk REAL CHECK (causality_risk BETWEEN 1 AND 10),
    political_distortion_risk REAL CHECK (political_distortion_risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    frame_confidence REAL CHECK (frame_confidence BETWEEN 0 AND 1),
    implementation_scope REAL CHECK (implementation_scope BETWEEN 1 AND 10),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    explanatory_adequacy_weight REAL NOT NULL CHECK (explanatory_adequacy_weight >= 0),
    stakeholder_coverage_weight REAL NOT NULL CHECK (stakeholder_coverage_weight >= 0),
    opportunity_value_weight REAL NOT NULL CHECK (opportunity_value_weight >= 0),
    framing_risk_weight REAL NOT NULL CHECK (framing_risk_weight >= 0),
    CHECK (
        ABS(
            explanatory_adequacy_weight +
            stakeholder_coverage_weight +
            opportunity_value_weight +
            framing_risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE frame_scores (
    score_id INTEGER PRIMARY KEY,
    frame_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    frame_value REAL NOT NULL,
    framing_risk_index REAL,
    confidence_adjusted_value REAL,
    rank_in_scenario INTEGER,
    FOREIGN KEY (frame_id) REFERENCES problem_frames(frame_id),
    FOREIGN KEY (scenario_id) REFERENCES scenario_weights(scenario_id)
);

CREATE TABLE counterframes (
    counterframe_id INTEGER PRIMARY KEY,
    dominant_frame TEXT NOT NULL,
    counterframe TEXT NOT NULL,
    reason_to_test TEXT,
    missing_evidence_risk REAL CHECK (missing_evidence_risk BETWEEN 0 AND 1),
    power_convenience_risk REAL CHECK (power_convenience_risk BETWEEN 0 AND 1)
);

INSERT INTO problem_frames (
    frame_name,
    explanatory_adequacy,
    stakeholder_coverage,
    opportunity_value,
    framing_risk,
    narrowness_risk,
    stakeholder_exclusion_risk,
    causality_risk,
    political_distortion_risk,
    evidence_quality,
    frame_confidence,
    implementation_scope
)
VALUES
('Improve transit capacity', 7.2, 6.8, 7.1, 4.8, 5.4, 4.8, 4.6, 4.4, 0.68, 0.66, 5.5),
('Improve transit reliability', 8.3, 7.9, 8.2, 3.9, 3.8, 3.6, 3.9, 4.1, 0.78, 0.76, 6.1),
('Reduce commuter uncertainty', 8.6, 7.5, 8.5, 3.7, 3.6, 3.9, 3.4, 3.8, 0.76, 0.75, 5.8),
('Redesign cross-network coordination', 8.0, 8.7, 8.4, 4.2, 3.7, 3.4, 4.4, 5.0, 0.80, 0.78, 7.2),
('Reduce institutional travel burden', 8.4, 8.2, 8.1, 3.8, 3.5, 3.3, 3.8, 4.4, 0.74, 0.73, 6.6),
('Rebuild trust in mobility services', 8.1, 8.5, 8.3, 4.1, 3.8, 3.5, 4.2, 4.9, 0.72, 0.70, 6.9),
('Clarify service status and disruptions', 7.9, 7.6, 8.0, 3.6, 3.4, 3.8, 3.7, 3.5, 0.77, 0.74, 5.6);

INSERT INTO scenario_weights (
    scenario_name,
    explanatory_adequacy_weight,
    stakeholder_coverage_weight,
    opportunity_value_weight,
    framing_risk_weight
)
VALUES
('Balanced', 0.30, 0.25, 0.30, 0.15),
('Explanation First', 0.45, 0.20, 0.20, 0.15),
('Coverage First', 0.20, 0.45, 0.20, 0.15),
('Opportunity First', 0.20, 0.20, 0.45, 0.15),
('Risk Sensitive', 0.25, 0.20, 0.20, 0.35),
('Systems Sensitive', 0.25, 0.35, 0.25, 0.15),
('Actionability First', 0.25, 0.20, 0.40, 0.15),
('Power Aware', 0.25, 0.35, 0.20, 0.20);

INSERT INTO counterframes (
    dominant_frame,
    counterframe,
    reason_to_test,
    missing_evidence_risk,
    power_convenience_risk
)
VALUES
('Improve transit capacity', 'Reduce commuter uncertainty', 'Capacity framing may miss reliability and information needs.', 0.70, 0.55),
('Improve transit reliability', 'Rebuild trust in mobility services', 'Reliability may not be enough where institutional trust is damaged.', 0.58, 0.50),
('Reduce commuter uncertainty', 'Redesign cross-network coordination', 'Uncertainty may be produced by coordination failures across systems.', 0.62, 0.54),
('Redesign cross-network coordination', 'Reduce institutional travel burden', 'Coordination framing may understate user burden and access barriers.', 0.57, 0.52),
('Reduce institutional travel burden', 'Clarify service status and disruptions', 'Burden may be driven by lack of timely service visibility.', 0.54, 0.47),
('Rebuild trust in mobility services', 'Improve transit reliability', 'Trust framing may become too broad unless connected to operational evidence.', 0.64, 0.58),
('Clarify service status and disruptions', 'Improve transit reliability', 'Communication framing may hide deeper reliability problems.', 0.60, 0.56);
