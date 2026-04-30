-- Article-level synthetic design thinking schema.
-- Educational only. Not a consulting, validation, or automated design-decision tool.

CREATE TABLE IF NOT EXISTS design_pathways (
    pathway_id TEXT PRIMARY KEY,
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
    pathway_id TEXT NOT NULL,
    prototype_version TEXT,
    test_round INTEGER,
    usability_score REAL,
    desirability_score REAL,
    feasibility_score REAL,
    risk_observed REAL,
    learning_note TEXT
);

CREATE TABLE IF NOT EXISTS stakeholder_research_notes (
    note_id INTEGER PRIMARY KEY,
    stakeholder_group TEXT,
    research_method TEXT,
    insight_theme TEXT,
    evidence_strength REAL,
    burden_or_equity_note TEXT
);

CREATE INDEX IF NOT EXISTS idx_design_pathways_value
ON design_pathways(design_value);

CREATE INDEX IF NOT EXISTS idx_prototype_tests_pathway
ON prototype_tests(pathway_id);
