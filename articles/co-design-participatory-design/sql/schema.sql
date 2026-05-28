-- SQLite schema for professional co-design and participatory design analysis.
-- Run:
--   sqlite3 outputs/codesign_participatory_design.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS participation_scores;
DROP TABLE IF EXISTS participation_scenario_weights;
DROP TABLE IF EXISTS participant_groups;
DROP TABLE IF EXISTS participatory_prototype_learning;
DROP TABLE IF EXISTS participation_risk_register;
DROP TABLE IF EXISTS codesign_activities;

CREATE TABLE codesign_activities (
    activity_id INTEGER PRIMARY KEY,
    activity_name TEXT NOT NULL UNIQUE,
    activity_type TEXT NOT NULL,
    design_stage TEXT NOT NULL,
    representation REAL NOT NULL CHECK (representation BETWEEN 1 AND 10),
    accessibility REAL NOT NULL CHECK (accessibility BETWEEN 1 AND 10),
    participant_influence REAL NOT NULL CHECK (participant_influence BETWEEN 1 AND 10),
    trust_quality REAL NOT NULL CHECK (trust_quality BETWEEN 1 AND 10),
    evidence_quality REAL NOT NULL CHECK (evidence_quality BETWEEN 1 AND 10),
    implementation_accountability REAL NOT NULL CHECK (implementation_accountability BETWEEN 1 AND 10),
    decision_impact REAL NOT NULL CHECK (decision_impact BETWEEN 1 AND 10),
    ethical_risk REAL NOT NULL CHECK (ethical_risk BETWEEN 1 AND 10),
    affectedness_weight REAL CHECK (affectedness_weight BETWEEN 0 AND 1),
    compensation_quality REAL CHECK (compensation_quality BETWEEN 1 AND 10),
    feedback_loop_quality REAL CHECK (feedback_loop_quality BETWEEN 1 AND 10),
    tokenism_risk REAL CHECK (tokenism_risk BETWEEN 1 AND 10)
);

CREATE TABLE participation_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    representation_weight REAL NOT NULL CHECK (representation_weight >= 0),
    accessibility_weight REAL NOT NULL CHECK (accessibility_weight >= 0),
    participant_influence_weight REAL NOT NULL CHECK (participant_influence_weight >= 0),
    trust_quality_weight REAL NOT NULL CHECK (trust_quality_weight >= 0),
    evidence_quality_weight REAL NOT NULL CHECK (evidence_quality_weight >= 0),
    implementation_accountability_weight REAL NOT NULL CHECK (implementation_accountability_weight >= 0),
    decision_impact_weight REAL NOT NULL CHECK (decision_impact_weight >= 0),
    ethical_risk_weight REAL NOT NULL CHECK (ethical_risk_weight >= 0),
    CHECK (
        ABS(
            representation_weight +
            accessibility_weight +
            participant_influence_weight +
            trust_quality_weight +
            evidence_quality_weight +
            implementation_accountability_weight +
            decision_impact_weight +
            ethical_risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE participant_groups (
    group_id INTEGER PRIMARY KEY,
    group_name TEXT NOT NULL UNIQUE,
    stakeholder_type TEXT NOT NULL,
    affectedness REAL NOT NULL CHECK (affectedness BETWEEN 0 AND 1),
    presence REAL NOT NULL CHECK (presence BETWEEN 0 AND 1),
    framing_influence REAL NOT NULL CHECK (framing_influence BETWEEN 0 AND 1),
    synthesis_influence REAL NOT NULL CHECK (synthesis_influence BETWEEN 0 AND 1),
    concept_influence REAL NOT NULL CHECK (concept_influence BETWEEN 0 AND 1),
    testing_influence REAL NOT NULL CHECK (testing_influence BETWEEN 0 AND 1),
    implementation_influence REAL NOT NULL CHECK (implementation_influence BETWEEN 0 AND 1),
    governance_influence REAL NOT NULL CHECK (governance_influence BETWEEN 0 AND 1),
    access_support REAL NOT NULL CHECK (access_support BETWEEN 0 AND 1),
    trust_score REAL NOT NULL CHECK (trust_score BETWEEN 0 AND 1),
    compensation_support REAL NOT NULL CHECK (compensation_support BETWEEN 0 AND 1),
    language_access REAL NOT NULL CHECK (language_access BETWEEN 0 AND 1),
    disability_access REAL NOT NULL CHECK (disability_access BETWEEN 0 AND 1)
);

CREATE TABLE participation_scores (
    score_id INTEGER PRIMARY KEY,
    activity_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    participation_quality REAL NOT NULL,
    affectedness_adjusted_quality REAL NOT NULL,
    equity_participation_index REAL NOT NULL,
    implementation_legitimacy_index REAL NOT NULL,
    participatory_evidence_index REAL NOT NULL,
    learning_priority REAL NOT NULL,
    process_resilience REAL NOT NULL,
    FOREIGN KEY (activity_id) REFERENCES codesign_activities(activity_id),
    FOREIGN KEY (scenario_id) REFERENCES participation_scenario_weights(scenario_id)
);

CREATE TABLE participatory_prototype_learning (
    learning_id INTEGER PRIMARY KEY,
    activity_name TEXT NOT NULL,
    round INTEGER NOT NULL,
    participant_comprehension REAL NOT NULL,
    participant_influence REAL NOT NULL,
    trust_score REAL NOT NULL,
    prototype_clarity REAL NOT NULL,
    accessibility_score REAL NOT NULL,
    burden_score REAL NOT NULL,
    decision_traceability REAL NOT NULL,
    implementation_commitment REAL NOT NULL
);

CREATE TABLE participation_risk_register (
    risk_id INTEGER PRIMARY KEY,
    activity_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO codesign_activities (
    activity_name, activity_type, design_stage,
    representation, accessibility, participant_influence, trust_quality, evidence_quality,
    implementation_accountability, decision_impact, ethical_risk, affectedness_weight,
    compensation_quality, feedback_loop_quality, tokenism_risk
)
VALUES
('Community Problem-Framing Sessions','problem_framing','framing',7.8,7.4,7.6,7.0,7.2,6.8,7.4,3.8,0.88,7.0,6.8,3.9),
('Frontline Worker Journey Mapping','journey_mapping','research',8.0,7.8,7.2,7.4,8.0,6.6,7.0,3.4,0.80,7.2,6.5,3.6),
('Non-User Contextual Inquiry','field_research','research',6.4,6.2,6.8,5.8,6.6,5.8,6.2,5.2,0.92,6.0,5.5,5.4),
('Accessible Prototype Workshops','prototype_workshop','prototyping',7.2,8.4,7.8,7.2,7.4,6.4,6.8,4.0,0.86,7.8,6.8,4.0),
('Participatory Synthesis Review','synthesis_review','synthesis',6.8,7.0,7.0,6.8,7.0,7.0,7.2,3.6,0.82,6.8,7.6,3.8),
('AI Decision-Scenario Walkthroughs','ai_governance','governance',6.0,6.6,6.4,6.2,6.5,7.2,6.6,6.4,0.90,6.2,6.8,5.8),
('Implementation Governance Board','implementation_governance','implementation',7.0,7.2,8.0,7.0,7.2,8.4,8.2,4.2,0.78,7.0,8.2,3.8),
('Community Feedback and Accountability Forum','feedback_loop','governance',7.6,8.0,7.4,7.8,7.4,8.0,7.8,3.5,0.86,7.6,8.5,3.4),
('Caregiver Service Blueprinting','service_blueprinting','research',7.4,7.2,7.0,6.9,7.5,6.7,6.9,4.1,0.80,6.9,6.6,4.0),
('Participatory Data Rights Review','data_governance','governance',6.8,6.8,7.2,6.6,7.1,7.8,7.4,5.6,0.88,6.7,7.8,4.9);

INSERT INTO participation_scenario_weights (
    scenario_name,
    representation_weight,
    accessibility_weight,
    participant_influence_weight,
    trust_quality_weight,
    evidence_quality_weight,
    implementation_accountability_weight,
    decision_impact_weight,
    ethical_risk_weight
)
VALUES
('Balanced',0.18,0.14,0.22,0.12,0.12,0.12,0.14,0.08),
('Influence First',0.14,0.12,0.34,0.10,0.10,0.12,0.12,0.06),
('Accessibility First',0.16,0.30,0.18,0.12,0.10,0.08,0.10,0.06),
('Implementation First',0.12,0.10,0.18,0.10,0.10,0.30,0.14,0.06),
('Decision Impact First',0.14,0.10,0.20,0.10,0.10,0.12,0.28,0.06),
('Ethics Sensitive',0.18,0.14,0.20,0.12,0.10,0.10,0.10,0.16),
('Representation First',0.32,0.14,0.18,0.10,0.10,0.08,0.08,0.00),
('Trust and Safety',0.16,0.16,0.18,0.24,0.10,0.08,0.08,0.00);

INSERT INTO participant_groups (
    group_name, stakeholder_type, affectedness, presence,
    framing_influence, synthesis_influence, concept_influence, testing_influence,
    implementation_influence, governance_influence, access_support, trust_score,
    compensation_support, language_access, disability_access
)
VALUES
('Current Users','user_group',0.75,0.85,0.58,0.50,0.62,0.70,0.42,0.38,0.72,0.68,0.70,0.72,0.68),
('Non-Users','excluded_group',0.80,0.42,0.32,0.28,0.30,0.36,0.20,0.18,0.45,0.42,0.52,0.50,0.44),
('Frontline Workers','worker_group',0.78,0.76,0.64,0.56,0.60,0.68,0.50,0.46,0.70,0.64,0.72,0.70,0.66),
('Disabled Participants','accessibility_group',0.92,0.48,0.38,0.34,0.42,0.52,0.30,0.28,0.56,0.50,0.60,0.58,0.62),
('Low-Income Participants','equity_group',0.88,0.52,0.40,0.36,0.40,0.48,0.28,0.26,0.58,0.48,0.68,0.56,0.50),
('Community Advocates','community_partner',0.82,0.68,0.55,0.48,0.52,0.56,0.38,0.44,0.66,0.60,0.70,0.64,0.60),
('Technical Implementers','implementation_group',0.65,0.82,0.50,0.52,0.58,0.64,0.62,0.58,0.78,0.72,0.62,0.70,0.66),
('Institutional Decision-Makers','authority_group',0.70,0.90,0.72,0.68,0.66,0.60,0.80,0.78,0.82,0.78,0.58,0.70,0.68),
('Caregivers and Intermediaries','intermediary_group',0.84,0.58,0.46,0.42,0.48,0.54,0.32,0.30,0.62,0.54,0.64,0.60,0.56),
('Affected Publics','affected_public',0.90,0.46,0.34,0.30,0.36,0.42,0.24,0.22,0.52,0.46,0.56,0.54,0.48);
