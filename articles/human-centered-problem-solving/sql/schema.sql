-- SQLite schema for professional human-centered problem-solving analysis.
-- Run:
--   sqlite3 outputs/human_centered_problem_solving.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS option_scores;
DROP TABLE IF EXISTS scenario_weights;
DROP TABLE IF EXISTS stakeholder_groups;
DROP TABLE IF EXISTS human_centered_options;

CREATE TABLE human_centered_options (
    option_id INTEGER PRIMARY KEY,
    option_name TEXT NOT NULL UNIQUE,
    human_benefit REAL NOT NULL CHECK (human_benefit BETWEEN 1 AND 10),
    usability REAL NOT NULL CHECK (usability BETWEEN 1 AND 10),
    stakeholder_fit REAL NOT NULL CHECK (stakeholder_fit BETWEEN 1 AND 10),
    burden REAL NOT NULL CHECK (burden BETWEEN 1 AND 10),
    learning_cost REAL CHECK (learning_cost BETWEEN 1 AND 10),
    compliance_cost REAL CHECK (compliance_cost BETWEEN 1 AND 10),
    psychological_cost REAL CHECK (psychological_cost BETWEEN 1 AND 10),
    access_cost REAL CHECK (access_cost BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    stakeholder_confidence REAL CHECK (stakeholder_confidence BETWEEN 0 AND 1),
    implementation_complexity REAL CHECK (implementation_complexity BETWEEN 1 AND 10),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    human_benefit_weight REAL NOT NULL CHECK (human_benefit_weight >= 0),
    usability_weight REAL NOT NULL CHECK (usability_weight >= 0),
    stakeholder_fit_weight REAL NOT NULL CHECK (stakeholder_fit_weight >= 0),
    burden_weight REAL NOT NULL CHECK (burden_weight >= 0),
    CHECK (
        ABS(
            human_benefit_weight +
            usability_weight +
            stakeholder_fit_weight +
            burden_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE option_scores (
    score_id INTEGER PRIMARY KEY,
    option_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    hc_value REAL NOT NULL,
    burden_index REAL,
    confidence_adjusted_value REAL,
    rank_in_scenario INTEGER,
    FOREIGN KEY (option_id) REFERENCES human_centered_options(option_id),
    FOREIGN KEY (scenario_id) REFERENCES scenario_weights(scenario_id)
);

CREATE TABLE stakeholder_groups (
    stakeholder_id INTEGER PRIMARY KEY,
    stakeholder_group TEXT NOT NULL UNIQUE,
    visibility_to_institution REAL NOT NULL CHECK (visibility_to_institution BETWEEN 0 AND 1),
    power_to_influence_design REAL NOT NULL CHECK (power_to_influence_design BETWEEN 0 AND 1),
    burden_exposure REAL NOT NULL CHECK (burden_exposure BETWEEN 0 AND 1),
    access_risk REAL NOT NULL CHECK (access_risk BETWEEN 0 AND 1),
    notes TEXT
);

INSERT INTO human_centered_options (
    option_name,
    human_benefit,
    usability,
    stakeholder_fit,
    burden,
    learning_cost,
    compliance_cost,
    psychological_cost,
    access_cost,
    evidence_quality,
    stakeholder_confidence,
    implementation_complexity
)
VALUES
('Guided Intake Redesign', 8.7, 8.2, 8.1, 3.9, 3.4, 4.1, 3.8, 4.3, 0.78, 0.80, 5.8),
('Simplified Mobile Access Flow', 8.0, 8.8, 7.7, 3.5, 3.1, 3.4, 3.2, 4.4, 0.72, 0.74, 6.2),
('Community Support Navigator', 8.9, 7.6, 8.6, 4.2, 3.8, 4.4, 4.0, 4.7, 0.76, 0.82, 6.8),
('AI Self-Service Assistant', 7.4, 8.1, 6.9, 5.0, 4.2, 4.8, 5.2, 5.8, 0.63, 0.61, 7.4),
('Hybrid Human-Digital Support Model', 8.6, 8.4, 8.3, 3.7, 3.2, 3.8, 3.6, 4.2, 0.80, 0.83, 6.5),
('In-Person Assisted Enrollment', 8.8, 7.3, 8.7, 4.6, 3.5, 4.9, 4.1, 5.6, 0.81, 0.85, 7.1),
('Plain-Language Eligibility Redesign', 8.4, 8.6, 8.2, 3.2, 2.8, 3.1, 3.0, 3.7, 0.84, 0.79, 5.4);

INSERT INTO scenario_weights (
    scenario_name,
    human_benefit_weight,
    usability_weight,
    stakeholder_fit_weight,
    burden_weight
)
VALUES
('Balanced', 0.30, 0.25, 0.30, 0.15),
('Benefit First', 0.45, 0.20, 0.20, 0.15),
('Usability First', 0.20, 0.45, 0.20, 0.15),
('Stakeholder First', 0.20, 0.20, 0.45, 0.15),
('Burden Sensitive', 0.25, 0.20, 0.20, 0.35),
('Equity Sensitive', 0.35, 0.15, 0.35, 0.15),
('Administrative Burden Reduction', 0.20, 0.20, 0.20, 0.40),
('Institutional Adoption', 0.25, 0.30, 0.25, 0.20);

INSERT INTO stakeholder_groups (
    stakeholder_group,
    visibility_to_institution,
    power_to_influence_design,
    burden_exposure,
    access_risk,
    notes
)
VALUES
('Digitally confident users', 0.85, 0.65, 0.35, 0.20, 'Often easiest to observe through digital analytics.'),
('Low-bandwidth users', 0.35, 0.25, 0.75, 0.85, 'May be excluded by digital-first processes.'),
('Frontline staff', 0.65, 0.55, 0.70, 0.30, 'Often create workarounds when formal systems fail.'),
('Caregivers and helpers', 0.30, 0.20, 0.68, 0.55, 'Frequently invisible in formal service design.'),
('Non-native language users', 0.28, 0.18, 0.80, 0.82, 'May face translation and trust barriers.'),
('Policy administrators', 0.80, 0.75, 0.40, 0.20, 'High institutional visibility and influence.');
