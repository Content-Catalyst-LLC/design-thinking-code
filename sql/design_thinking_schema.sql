-- Root schema for design thinking research, pathways, prototypes,
-- testing, implementation, and design decision records.
-- Educational only. Not a consulting, product-validation, or public-policy tool.

CREATE TABLE IF NOT EXISTS design_projects (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    design_domain TEXT,
    stakeholder_context TEXT,
    ethical_notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stakeholders (
    stakeholder_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    stakeholder_group TEXT,
    role_description TEXT,
    access_needs TEXT,
    burden_notes TEXT
);

CREATE TABLE IF NOT EXISTS design_pathways (
    pathway_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    pathway_name TEXT NOT NULL,
    human_relevance REAL,
    feasibility REAL,
    learning_value REAL,
    residual_risk REAL,
    equity_impact REAL,
    implementation_burden REAL,
    design_value REAL
);

CREATE TABLE IF NOT EXISTS prototype_tests (
    test_id INTEGER PRIMARY KEY,
    project_id TEXT NOT NULL,
    pathway_id TEXT NOT NULL,
    prototype_version TEXT,
    test_round INTEGER,
    usability_score REAL,
    desirability_score REAL,
    feasibility_score REAL,
    risk_observed REAL,
    learning_note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS design_decisions (
    decision_id INTEGER PRIMARY KEY,
    project_id TEXT NOT NULL,
    decision_date TEXT,
    decision_label TEXT,
    evidence_used TEXT,
    assumption_notes TEXT,
    ethical_review_notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
