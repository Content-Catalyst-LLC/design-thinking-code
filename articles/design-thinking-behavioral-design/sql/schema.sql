PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS behavioral_interventions;
DROP TABLE IF EXISTS behavioral_barriers;

CREATE TABLE behavioral_barriers (
    barrier_id INTEGER PRIMARY KEY,
    segment TEXT NOT NULL,
    target_behavior TEXT NOT NULL,
    motivation REAL NOT NULL,
    capability REAL NOT NULL,
    opportunity REAL NOT NULL,
    trust REAL NOT NULL,
    friction REAL NOT NULL,
    affectedness REAL NOT NULL,
    time_pressure REAL NOT NULL,
    cognitive_load REAL NOT NULL,
    emotional_load REAL NOT NULL,
    social_support REAL NOT NULL,
    institutional_risk REAL NOT NULL
);

CREATE TABLE behavioral_interventions (
    intervention_id INTEGER PRIMARY KEY,
    intervention_name TEXT NOT NULL UNIQUE,
    intervention_type TEXT NOT NULL,
    mechanism TEXT NOT NULL,
    expected_behavior_gain REAL NOT NULL,
    importance REAL NOT NULL,
    equity_reach REAL NOT NULL,
    ethical_risk REAL NOT NULL,
    implementation_effort REAL NOT NULL,
    transparency REAL NOT NULL,
    autonomy_preservation REAL NOT NULL,
    trust_effect REAL NOT NULL,
    accessibility_effect REAL NOT NULL,
    durability REAL NOT NULL
);

INSERT INTO behavioral_interventions (
    intervention_name, intervention_type, mechanism, expected_behavior_gain, importance,
    equity_reach, ethical_risk, implementation_effort, transparency, autonomy_preservation,
    trust_effect, accessibility_effect, durability
)
VALUES
('Simplified Renewal Pathway','service_redesign','friction_reduction',0.11,0.88,0.80,0.12,0.42,0.86,0.88,0.78,0.82,0.74),
('Plain-Language Eligibility Message','communication','clarity_salience',0.07,0.82,0.72,0.08,0.30,0.90,0.92,0.72,0.74,0.62),
('Timely SMS Reminder','prompt','timing_memory',0.06,0.70,0.64,0.10,0.25,0.82,0.88,0.62,0.60,0.48),
('Assisted Digital Support','service_support','capability_access',0.13,0.90,0.90,0.06,0.55,0.88,0.94,0.84,0.92,0.78),
('Commitment Planning Prompt','commitment_device','intention_follow_through',0.05,0.62,0.58,0.09,0.28,0.84,0.90,0.58,0.56,0.50),
('Transparent Status and Recovery Pathway','service_recovery','trust_recovery',0.10,0.86,0.84,0.07,0.50,0.92,0.92,0.88,0.80,0.82),
('Pre-Filled Known Information','default_simplification','effort_reduction',0.09,0.84,0.78,0.16,0.46,0.78,0.76,0.76,0.78,0.70),
('Human Escalation Trigger','service_support','recovery_safety',0.08,0.82,0.86,0.05,0.58,0.90,0.94,0.86,0.84,0.76);
