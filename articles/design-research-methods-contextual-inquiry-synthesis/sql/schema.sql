-- SQLite schema for professional contextual inquiry and synthesis analysis.
-- Run:
--   sqlite3 outputs/contextual_inquiry_synthesis.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS theme_scores;
DROP TABLE IF EXISTS synthesis_scenario_weights;
DROP TABLE IF EXISTS coder_assignments;
DROP TABLE IF EXISTS stakeholder_sampling_frame;
DROP TABLE IF EXISTS evidence_units;

CREATE TABLE evidence_units (
    unit_id INTEGER PRIMARY KEY,
    participant_group TEXT NOT NULL,
    method TEXT NOT NULL,
    primary_theme TEXT NOT NULL,
    secondary_theme TEXT NOT NULL,
    evidence_strength REAL NOT NULL CHECK (evidence_strength BETWEEN 1 AND 10),
    interpretive_risk REAL NOT NULL CHECK (interpretive_risk BETWEEN 1 AND 10),
    environmental_constraint REAL NOT NULL CHECK (environmental_constraint BETWEEN 1 AND 10),
    artifact_dependency REAL NOT NULL CHECK (artifact_dependency BETWEEN 1 AND 10),
    workflow_stage TEXT NOT NULL,
    privacy_sensitivity REAL CHECK (privacy_sensitivity BETWEEN 0 AND 1),
    power_asymmetry REAL CHECK (power_asymmetry BETWEEN 0 AND 1)
);

CREATE TABLE synthesis_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    evidence_strength_weight REAL NOT NULL CHECK (evidence_strength_weight >= 0),
    stakeholder_coverage_weight REAL NOT NULL CHECK (stakeholder_coverage_weight >= 0),
    method_triangulation_weight REAL NOT NULL CHECK (method_triangulation_weight >= 0),
    interpretive_risk_weight REAL NOT NULL CHECK (interpretive_risk_weight >= 0),
    CHECK (
        ABS(
            evidence_strength_weight +
            stakeholder_coverage_weight +
            method_triangulation_weight +
            interpretive_risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE theme_scores (
    score_id INTEGER PRIMARY KEY,
    scenario_id INTEGER NOT NULL,
    primary_theme TEXT NOT NULL,
    evidence_units INTEGER NOT NULL,
    stakeholder_groups INTEGER NOT NULL,
    methods INTEGER NOT NULL,
    mean_evidence_strength REAL NOT NULL,
    mean_interpretive_risk REAL NOT NULL,
    synthesis_confidence REAL NOT NULL,
    validation_priority REAL NOT NULL,
    FOREIGN KEY (scenario_id) REFERENCES synthesis_scenario_weights(scenario_id)
);

CREATE TABLE coder_assignments (
    unit_id INTEGER PRIMARY KEY,
    coder_a TEXT NOT NULL,
    coder_b TEXT NOT NULL,
    coder_c TEXT NOT NULL
);

CREATE TABLE stakeholder_sampling_frame (
    stakeholder_group TEXT PRIMARY KEY,
    included_sessions INTEGER,
    priority_level TEXT,
    access_risk REAL CHECK (access_risk BETWEEN 0 AND 1),
    power_asymmetry REAL CHECK (power_asymmetry BETWEEN 0 AND 1),
    notes TEXT
);

INSERT INTO evidence_units (
    unit_id, participant_group, method, primary_theme, secondary_theme,
    evidence_strength, interpretive_risk, environmental_constraint,
    artifact_dependency, workflow_stage, privacy_sensitivity, power_asymmetry
)
VALUES
(1,'First-time applicants','contextual_observation','status_uncertainty','trust_gap',8.2,3.5,6.5,7.2,'submission_followup',0.55,0.68),
(2,'First-time applicants','interview','documentation_confusion','access_barrier',7.5,4.0,5.9,6.8,'preparation',0.48,0.62),
(3,'Caregivers','artifact_review','translation_labor','documentation_confusion',8.0,3.8,6.8,8.1,'preparation',0.52,0.72),
(4,'Frontline staff','contextual_observation','manual_workaround','handoff_breakdown',8.6,3.4,5.0,8.8,'case_processing',0.40,0.50),
(5,'Frontline staff','artifact_review','manual_workaround','policy_complexity',8.3,3.6,5.4,8.6,'case_processing',0.38,0.54),
(6,'Administrators','interview','policy_complexity','documentation_confusion',7.2,4.2,4.8,5.1,'policy_interpretation',0.35,0.42),
(7,'Community partners','workshop','trust_gap','access_barrier',7.8,4.1,7.5,6.4,'outreach',0.50,0.78),
(8,'Excluded users','interview','access_barrier','trust_gap',8.4,4.4,8.4,6.9,'entry_point',0.62,0.86),
(9,'Excluded users','contextual_observation','access_barrier','status_uncertainty',8.7,4.5,8.7,7.4,'entry_point',0.66,0.88),
(10,'First-time applicants','artifact_review','documentation_confusion','policy_complexity',7.6,4.0,6.1,8.0,'preparation',0.52,0.64),
(11,'Caregivers','interview','translation_labor','access_barrier',8.1,3.9,7.2,7.1,'preparation',0.57,0.76),
(12,'Frontline staff','contextual_observation','handoff_breakdown','manual_workaround',8.5,3.7,5.8,7.9,'case_transfer',0.42,0.55),
(13,'Administrators','process_walkthrough','policy_complexity','handoff_breakdown',7.3,4.3,4.6,5.8,'policy_interpretation',0.36,0.45),
(14,'Community partners','workshop','trust_gap','status_uncertainty',8.0,4.0,7.8,6.5,'outreach',0.51,0.80),
(15,'First-time applicants','interview','status_uncertainty','trust_gap',8.1,3.6,6.4,7.0,'submission_followup',0.54,0.66),
(16,'Excluded users','contextual_observation','access_barrier','documentation_confusion',8.8,4.6,8.9,7.8,'entry_point',0.68,0.90),
(17,'Caregivers','artifact_review','translation_labor','policy_complexity',8.0,3.8,7.0,8.2,'preparation',0.58,0.74),
(18,'Frontline staff','interview','handoff_breakdown','manual_workaround',8.2,3.9,5.6,7.6,'case_transfer',0.43,0.56),
(19,'Community partners','workshop','trust_gap','access_barrier',7.9,4.1,7.6,6.2,'outreach',0.53,0.81),
(20,'Administrators','process_walkthrough','policy_complexity','documentation_confusion',7.4,4.2,4.7,5.4,'policy_interpretation',0.34,0.44),
(21,'First-time applicants','contextual_observation','status_uncertainty','status_uncertainty',8.3,3.5,6.7,7.3,'submission_followup',0.56,0.67),
(22,'Excluded users','interview','access_barrier','trust_gap',8.5,4.7,8.5,6.7,'entry_point',0.67,0.89),
(23,'Caregivers','artifact_review','translation_labor','translation_labor',8.2,3.9,7.1,8.4,'preparation',0.59,0.75),
(24,'Frontline staff','contextual_observation','manual_workaround','handoff_breakdown',8.4,3.6,5.2,8.7,'case_processing',0.41,0.53),
(25,'Case supervisors','interview','handoff_breakdown','policy_complexity',7.9,4.0,5.4,6.9,'case_transfer',0.45,0.58),
(26,'Case supervisors','artifact_review','manual_workaround','handoff_breakdown',8.1,3.8,5.2,8.1,'case_processing',0.44,0.57),
(27,'Language-access advocates','workshop','translation_labor','access_barrier',8.5,4.2,7.9,7.7,'preparation',0.61,0.84),
(28,'Digital support staff','process_walkthrough','status_uncertainty','handoff_breakdown',7.8,3.9,5.7,7.5,'submission_followup',0.49,0.59),
(29,'Digital support staff','contextual_observation','documentation_confusion','manual_workaround',7.7,3.9,5.8,7.9,'preparation',0.47,0.57),
(30,'Community partners','artifact_review','access_barrier','translation_labor',8.3,4.3,8.1,7.5,'outreach',0.56,0.83);

INSERT INTO synthesis_scenario_weights (
    scenario_name,
    evidence_strength_weight,
    stakeholder_coverage_weight,
    method_triangulation_weight,
    interpretive_risk_weight
)
VALUES
('Balanced', 0.35, 0.25, 0.25, 0.15),
('Evidence First', 0.50, 0.20, 0.20, 0.10),
('Coverage First', 0.25, 0.45, 0.20, 0.10),
('Method Triangulation First', 0.25, 0.20, 0.45, 0.10),
('Risk Sensitive', 0.30, 0.20, 0.20, 0.30),
('Equity Sensitive', 0.30, 0.35, 0.20, 0.15),
('Fieldwork Sensitive', 0.40, 0.20, 0.25, 0.15),
('Validation Sensitive', 0.25, 0.25, 0.25, 0.25);

INSERT INTO coder_assignments (unit_id, coder_a, coder_b, coder_c)
VALUES
(1,'status_uncertainty','status_uncertainty','status_uncertainty'),
(2,'documentation_confusion','documentation_confusion','access_barrier'),
(3,'translation_labor','translation_labor','translation_labor'),
(4,'manual_workaround','manual_workaround','handoff_breakdown'),
(5,'manual_workaround','manual_workaround','manual_workaround'),
(6,'policy_complexity','policy_complexity','documentation_confusion'),
(7,'trust_gap','trust_gap','access_barrier'),
(8,'access_barrier','access_barrier','access_barrier'),
(9,'access_barrier','status_uncertainty','access_barrier'),
(10,'documentation_confusion','documentation_confusion','policy_complexity'),
(11,'translation_labor','translation_labor','access_barrier'),
(12,'handoff_breakdown','handoff_breakdown','manual_workaround'),
(13,'policy_complexity','policy_complexity','handoff_breakdown'),
(14,'trust_gap','trust_gap','status_uncertainty'),
(15,'status_uncertainty','status_uncertainty','trust_gap'),
(16,'access_barrier','access_barrier','access_barrier'),
(17,'translation_labor','translation_labor','policy_complexity'),
(18,'handoff_breakdown','handoff_breakdown','manual_workaround'),
(19,'trust_gap','trust_gap','access_barrier'),
(20,'policy_complexity','policy_complexity','documentation_confusion'),
(21,'status_uncertainty','status_uncertainty','status_uncertainty'),
(22,'access_barrier','access_barrier','trust_gap'),
(23,'translation_labor','translation_labor','translation_labor'),
(24,'manual_workaround','manual_workaround','handoff_breakdown'),
(25,'handoff_breakdown','handoff_breakdown','policy_complexity'),
(26,'manual_workaround','manual_workaround','handoff_breakdown'),
(27,'translation_labor','translation_labor','access_barrier'),
(28,'status_uncertainty','handoff_breakdown','status_uncertainty'),
(29,'documentation_confusion','documentation_confusion','manual_workaround'),
(30,'access_barrier','translation_labor','access_barrier');
