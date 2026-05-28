-- SQLite schema for professional public-policy design analysis.
-- Run:
--   sqlite3 outputs/public_policy_design.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS policy_scores;
DROP TABLE IF EXISTS public_policy_scenario_weights;
DROP TABLE IF EXISTS policy_learning_pathways;
DROP TABLE IF EXISTS administrative_burdens;
DROP TABLE IF EXISTS public_policy_risk_register;
DROP TABLE IF EXISTS public_policy_pilots;

CREATE TABLE public_policy_pilots (
    pilot_id INTEGER PRIMARY KEY,
    pilot_name TEXT NOT NULL UNIQUE,
    policy_domain TEXT NOT NULL,
    pilot_type TEXT NOT NULL,
    accessibility REAL NOT NULL CHECK (accessibility BETWEEN 1 AND 10),
    feasibility REAL NOT NULL CHECK (feasibility BETWEEN 1 AND 10),
    legitimacy REAL NOT NULL CHECK (legitimacy BETWEEN 1 AND 10),
    equity REAL NOT NULL CHECK (equity BETWEEN 1 AND 10),
    burden_reduction REAL NOT NULL CHECK (burden_reduction BETWEEN 1 AND 10),
    durability REAL NOT NULL CHECK (durability BETWEEN 1 AND 10),
    risk REAL NOT NULL CHECK (risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    stakeholder_coverage REAL CHECK (stakeholder_coverage BETWEEN 0 AND 1),
    legal_complexity REAL CHECK (legal_complexity BETWEEN 1 AND 10),
    implementation_complexity REAL CHECK (implementation_complexity BETWEEN 1 AND 10),
    participation_quality REAL CHECK (participation_quality BETWEEN 0 AND 1)
);

CREATE TABLE public_policy_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    accessibility_weight REAL NOT NULL CHECK (accessibility_weight >= 0),
    feasibility_weight REAL NOT NULL CHECK (feasibility_weight >= 0),
    legitimacy_weight REAL NOT NULL CHECK (legitimacy_weight >= 0),
    equity_weight REAL NOT NULL CHECK (equity_weight >= 0),
    burden_reduction_weight REAL NOT NULL CHECK (burden_reduction_weight >= 0),
    durability_weight REAL NOT NULL CHECK (durability_weight >= 0),
    risk_weight REAL NOT NULL CHECK (risk_weight >= 0),
    CHECK (
        ABS(
            accessibility_weight +
            feasibility_weight +
            legitimacy_weight +
            equity_weight +
            burden_reduction_weight +
            durability_weight +
            risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE policy_scores (
    score_id INTEGER PRIMARY KEY,
    pilot_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    policy_value REAL NOT NULL,
    evidence_adjusted_value REAL NOT NULL,
    evidence_strength REAL NOT NULL,
    implementation_readiness REAL NOT NULL,
    public_legitimacy_index REAL NOT NULL,
    equity_access_index REAL NOT NULL,
    learning_priority REAL NOT NULL,
    policy_resilience REAL NOT NULL,
    FOREIGN KEY (pilot_id) REFERENCES public_policy_pilots(pilot_id),
    FOREIGN KEY (scenario_id) REFERENCES public_policy_scenario_weights(scenario_id)
);

CREATE TABLE policy_learning_pathways (
    learning_id INTEGER PRIMARY KEY,
    pilot_name TEXT NOT NULL,
    period INTEGER NOT NULL,
    uptake_rate REAL NOT NULL,
    citizen_friction REAL NOT NULL,
    implementation_error REAL NOT NULL,
    trust_score REAL NOT NULL,
    equity_score REAL NOT NULL,
    appeal_access REAL NOT NULL,
    staff_workload REAL NOT NULL,
    case_resolution_time REAL NOT NULL
);

CREATE TABLE administrative_burdens (
    burden_id INTEGER PRIMARY KEY,
    pilot_name TEXT NOT NULL,
    learning_burden REAL NOT NULL,
    compliance_burden REAL NOT NULL,
    psychological_burden REAL NOT NULL,
    digital_burden REAL NOT NULL,
    time_burden REAL NOT NULL,
    appeal_burden REAL NOT NULL,
    staff_burden REAL NOT NULL,
    community_partner_burden REAL NOT NULL
);

CREATE TABLE public_policy_risk_register (
    risk_id INTEGER PRIMARY KEY,
    pilot_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO public_policy_pilots (
    pilot_name, policy_domain, pilot_type,
    accessibility, feasibility, legitimacy, equity, burden_reduction, durability,
    risk, evidence_quality, stakeholder_coverage, legal_complexity,
    implementation_complexity, participation_quality
)
VALUES
('Benefits Application Simplification','social_protection','service_redesign',8.9,8.1,8.0,8.8,9.0,7.8,3.2,0.78,0.74,4.8,5.5,0.72),
('Mobile Community Health Enrollment','public_health','outreach_service',8.4,7.2,8.6,9.1,8.0,7.4,4.4,0.72,0.77,5.5,6.4,0.78),
('Digital Licensing Renewal Redesign','licensing','digital_service',7.5,8.5,7.4,6.9,7.6,8.0,3.8,0.76,0.66,4.2,5.2,0.60),
('School Meals Access Outreach','education','outreach_service',8.7,7.8,8.5,8.9,8.4,7.6,3.5,0.75,0.72,4.5,5.8,0.70),
('Tenant Rights Navigation Service','housing','service_navigation',8.6,7.0,8.7,9.0,8.7,7.3,4.8,0.70,0.82,6.8,7.2,0.82),
('Disability Benefit Renewal Redesign','disability_support','service_redesign',8.8,6.9,8.4,9.2,9.1,7.2,5.0,0.69,0.80,7.2,7.5,0.80),
('Climate Resilience Grant Access Pilot','climate_adaptation','grant_access',8.1,6.8,8.2,8.7,8.3,7.1,4.9,0.71,0.76,6.5,7.4,0.77),
('Small Business Compliance Assistance','economic_development','compliance_support',7.9,8.2,7.8,7.5,8.1,7.9,3.7,0.77,0.68,5.2,5.6,0.63),
('Emergency Benefits Auto-Enrollment','social_protection','automatic_enrollment',8.5,7.1,8.1,8.9,9.2,7.5,5.1,0.73,0.75,7.0,7.6,0.70),
('Public Notices Plain-Language Redesign','administration','communication_design',8.3,8.6,8.2,8.1,8.5,8.2,2.9,0.80,0.70,3.8,4.6,0.66);

INSERT INTO public_policy_scenario_weights (
    scenario_name,
    accessibility_weight,
    feasibility_weight,
    legitimacy_weight,
    equity_weight,
    burden_reduction_weight,
    durability_weight,
    risk_weight
)
VALUES
('Balanced',0.20,0.16,0.16,0.20,0.14,0.08,0.06),
('Feasibility First',0.16,0.34,0.12,0.14,0.10,0.08,0.06),
('Equity First',0.14,0.12,0.12,0.38,0.14,0.06,0.04),
('Legitimacy First',0.16,0.12,0.34,0.16,0.10,0.08,0.04),
('Burden Reduction',0.18,0.12,0.12,0.18,0.34,0.04,0.02),
('Durability First',0.14,0.16,0.14,0.16,0.10,0.26,0.04),
('Risk Sensitive',0.17,0.16,0.16,0.18,0.13,0.06,0.14),
('Access and Equity',0.30,0.10,0.10,0.30,0.12,0.04,0.04);

INSERT INTO public_policy_risk_register (
    pilot_name, risk_category, risk_description, severity, likelihood, detectability, mitigation_owner, mitigation_status
)
VALUES
('Benefits Application Simplification','verification_gap','Simplification could omit necessary safeguards or create inconsistent verification practice',4,3,3,'benefits_policy_owner','active'),
('Mobile Community Health Enrollment','coverage_gap','Mobile services may miss hard-to-reach groups if outreach routes are poorly designed',4,3,4,'public_health_owner','active'),
('Digital Licensing Renewal Redesign','digital_exclusion','Digital redesign may worsen access for users without devices connectivity or digital literacy',4,4,3,'digital_service_owner','active'),
('School Meals Access Outreach','stigma','Outreach may inadvertently reveal eligibility status or increase stigma',4,3,3,'education_program_owner','active'),
('Tenant Rights Navigation Service','retaliation_risk','Tenants may fear retaliation if navigation pathways are not confidential and trusted',5,3,4,'housing_rights_owner','active'),
('Disability Benefit Renewal Redesign','procedural_harm','Renewal redesign may still impose stress or documentation requirements on disabled people',5,4,3,'disability_policy_owner','active'),
('Climate Resilience Grant Access Pilot','elite_capture','Grant access may favor organized applicants unless support reaches under-resourced communities',5,3,4,'climate_adaptation_owner','active'),
('Small Business Compliance Assistance','unequal_access','Compliance assistance may benefit already-connected firms more than informal or marginalized businesses',4,3,3,'economic_development_owner','active'),
('Emergency Benefits Auto-Enrollment','due_process','Automatic enrollment may create notice appeal or consent issues if governance is weak',5,3,4,'social_protection_owner','active'),
('Public Notices Plain-Language Redesign','legal_precision_loss','Plain-language simplification may remove legally necessary nuance if review is weak',3,3,3,'legal_review_owner','active');
