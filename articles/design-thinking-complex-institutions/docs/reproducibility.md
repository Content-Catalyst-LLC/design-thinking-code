# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python institutional_design_engine.py \
  --options ../data/raw/institutional_design_options_raw.csv \
  --stakeholders ../data/raw/stakeholder_burden_raw.csv \
  --governance ../data/raw/governance_decision_rights_raw.csv \
  --weights ../data/raw/institutional_scenario_weights.csv \
  --risk-register ../data/raw/institutional_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript institutional_design_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/institutional_design.db < sql/schema.sql
sqlite3 outputs/institutional_design.db < sql/analytical_queries.sql
```

## Notes

Preserve assumptions, stakeholder definitions, scoring criteria, governance owners, policy constraints, implementation decisions, and evaluation evidence with each analysis run.
