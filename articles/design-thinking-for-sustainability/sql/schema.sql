-- SQLite schema for professional sustainability design analysis.
-- Run:
--   sqlite3 outputs/sustainability_design.db < sql/schema.sql

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS sustainability_scores;
DROP TABLE IF EXISTS sustainability_scenario_weights;
DROP TABLE IF EXISTS transition_pathways;
DROP TABLE IF EXISTS sustainability_risk_register;
DROP TABLE IF EXISTS sustainability_concepts;

CREATE TABLE sustainability_concepts (
    concept_id INTEGER PRIMARY KEY,
    concept_name TEXT NOT NULL UNIQUE,
    concept_type TEXT NOT NULL,
    transition_domain TEXT NOT NULL,
    usability REAL NOT NULL CHECK (usability BETWEEN 1 AND 10),
    feasibility REAL NOT NULL CHECK (feasibility BETWEEN 1 AND 10),
    ecological_benefit REAL NOT NULL CHECK (ecological_benefit BETWEEN 1 AND 10),
    circularity REAL NOT NULL CHECK (circularity BETWEEN 1 AND 10),
    equity REAL NOT NULL CHECK (equity BETWEEN 1 AND 10),
    durability REAL NOT NULL CHECK (durability BETWEEN 1 AND 10),
    risk REAL NOT NULL CHECK (risk BETWEEN 1 AND 10),
    evidence_quality REAL CHECK (evidence_quality BETWEEN 0 AND 1),
    stakeholder_coverage REAL CHECK (stakeholder_coverage BETWEEN 0 AND 1),
    lifecycle_boundary_quality REAL CHECK (lifecycle_boundary_quality BETWEEN 0 AND 1),
    burden_shift_risk REAL CHECK (burden_shift_risk BETWEEN 1 AND 10),
    implementation_complexity REAL CHECK (implementation_complexity BETWEEN 1 AND 10)
);

CREATE TABLE sustainability_scenario_weights (
    scenario_id INTEGER PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    usability_weight REAL NOT NULL CHECK (usability_weight >= 0),
    feasibility_weight REAL NOT NULL CHECK (feasibility_weight >= 0),
    ecological_benefit_weight REAL NOT NULL CHECK (ecological_benefit_weight >= 0),
    circularity_weight REAL NOT NULL CHECK (circularity_weight >= 0),
    equity_weight REAL NOT NULL CHECK (equity_weight >= 0),
    durability_weight REAL NOT NULL CHECK (durability_weight >= 0),
    risk_weight REAL NOT NULL CHECK (risk_weight >= 0),
    CHECK (
        ABS(
            usability_weight +
            feasibility_weight +
            ecological_benefit_weight +
            circularity_weight +
            equity_weight +
            durability_weight +
            risk_weight - 1.0
        ) < 0.000001
    )
);

CREATE TABLE sustainability_scores (
    score_id INTEGER PRIMARY KEY,
    concept_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    sustainability_value REAL NOT NULL,
    evidence_adjusted_value REAL NOT NULL,
    evidence_strength REAL NOT NULL,
    transition_readiness REAL NOT NULL,
    ecological_integrity_index REAL NOT NULL,
    justice_burden_index REAL NOT NULL,
    learning_priority REAL NOT NULL,
    portfolio_resilience REAL NOT NULL,
    FOREIGN KEY (concept_id) REFERENCES sustainability_concepts(concept_id),
    FOREIGN KEY (scenario_id) REFERENCES sustainability_scenario_weights(scenario_id)
);

CREATE TABLE transition_pathways (
    transition_id INTEGER PRIMARY KEY,
    concept_name TEXT NOT NULL,
    period INTEGER NOT NULL,
    adoption_rate REAL NOT NULL,
    friction_score REAL NOT NULL,
    ecological_impact_reduction REAL NOT NULL,
    equity_score REAL NOT NULL,
    implementation_cost REAL NOT NULL,
    maintenance_burden REAL NOT NULL,
    trust_score REAL NOT NULL,
    participation_quality REAL NOT NULL
);

CREATE TABLE sustainability_risk_register (
    risk_id INTEGER PRIMARY KEY,
    concept_name TEXT NOT NULL,
    risk_category TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    detectability INTEGER NOT NULL CHECK (detectability BETWEEN 1 AND 5),
    mitigation_owner TEXT,
    mitigation_status TEXT
);

INSERT INTO sustainability_concepts (
    concept_name, concept_type, transition_domain,
    usability, feasibility, ecological_benefit, circularity, equity, durability,
    risk, evidence_quality, stakeholder_coverage, lifecycle_boundary_quality,
    burden_shift_risk, implementation_complexity
)
VALUES
('Building Retrofit Service Model','service_model','built_environment',8.1,7.4,8.8,7.9,7.6,8.0,4.1,0.76,0.72,0.74,4.2,6.5),
('Reusable Packaging Loop','circular_system','materials',7.6,7.8,8.5,9.1,7.2,8.2,4.6,0.73,0.68,0.78,4.8,6.1),
('Neighborhood Mobility Hub','urban_infrastructure','mobility',8.4,6.9,8.2,7.1,8.4,7.8,5.0,0.70,0.74,0.69,4.9,7.0),
('Repair and Refurbishment Platform','repair_platform','materials',7.9,7.5,8.0,8.8,7.8,7.9,4.2,0.75,0.70,0.76,3.9,5.8),
('Community Solar Enrollment Service','energy_access','energy',8.2,7.2,8.7,7.0,8.8,8.1,4.8,0.72,0.78,0.71,4.1,6.8),
('Circular Procurement Toolkit','institutional_toolkit','procurement',7.3,8.1,7.9,8.7,7.4,8.0,3.9,0.78,0.66,0.80,3.8,5.5),
('Urban Heat Resilience Network','climate_resilience','adaptation',8.0,6.8,8.6,7.2,8.7,8.4,5.1,0.71,0.80,0.73,4.7,7.2),
('Water Reuse Participation Model','water_system','water',7.7,7.0,8.1,7.6,8.1,7.7,4.7,0.69,0.73,0.72,4.5,6.6),
('Tenant-Centered Electrification Pathway','housing_energy','energy',8.3,6.7,8.9,7.3,9.0,8.0,5.2,0.70,0.82,0.73,5.0,7.4),
('Food Waste Prevention Service','food_system','food',8.5,7.9,8.0,8.2,8.0,7.8,3.8,0.77,0.75,0.74,3.4,5.4);

INSERT INTO sustainability_scenario_weights (
    scenario_name,
    usability_weight,
    feasibility_weight,
    ecological_benefit_weight,
    circularity_weight,
    equity_weight,
    durability_weight,
    risk_weight
)
VALUES
('Balanced',0.16,0.16,0.24,0.16,0.14,0.08,0.06),
('Feasibility First',0.15,0.32,0.18,0.12,0.10,0.08,0.05),
('Ecology First',0.12,0.12,0.42,0.12,0.10,0.08,0.04),
('Circularity First',0.12,0.12,0.18,0.38,0.10,0.06,0.04),
('Equity Sensitive',0.12,0.12,0.22,0.12,0.34,0.04,0.04),
('Durability First',0.12,0.14,0.20,0.14,0.10,0.26,0.04),
('Risk Sensitive',0.14,0.16,0.22,0.14,0.12,0.08,0.14),
('Transition Justice',0.12,0.12,0.24,0.12,0.32,0.04,0.04);

INSERT INTO sustainability_risk_register (
    concept_name, risk_category, risk_description, severity, likelihood, detectability, mitigation_owner, mitigation_status
)
VALUES
('Building Retrofit Service Model','green_gentrification','Retrofit gains may raise housing costs or displacement pressure without tenant protections',5,3,4,'housing_policy_owner','active'),
('Reusable Packaging Loop','rebound_logistics','Reverse logistics may increase transport burden or energy use if poorly designed',4,3,4,'circularity_lead','active'),
('Neighborhood Mobility Hub','access_displacement','Mobility investments may increase neighborhood desirability without affordability protections',5,3,4,'urban_planning_owner','active'),
('Repair and Refurbishment Platform','labor_quality','Repair ecosystem may depend on underpaid or informal labor',4,3,3,'workforce_owner','active'),
('Community Solar Enrollment Service','participation_barrier','Enrollment process may exclude renters, low-income households, or language-minority communities',5,3,3,'energy_access_owner','active'),
('Circular Procurement Toolkit','metric_narrowness','Procurement metrics may reward nominal circularity while missing lifecycle or labor harms',4,3,4,'procurement_owner','active'),
('Urban Heat Resilience Network','maintenance_gap','Green infrastructure may fail if maintenance ownership and funding are weak',5,4,3,'resilience_owner','active'),
('Water Reuse Participation Model','trust_failure','Water reuse adoption may fail if trust, safety, and transparency are weak',5,3,3,'water_governance_owner','active'),
('Tenant-Centered Electrification Pathway','cost_shift','Electrification costs may shift to tenants or trigger rent increases',5,4,4,'housing_energy_owner','active'),
('Food Waste Prevention Service','burden_shift','Food waste prevention may shift unpaid planning and sorting labor to households or staff',3,3,3,'food_system_owner','active');
