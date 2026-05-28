# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python public_value_impact_engine.py \
  --interventions ../data/raw/social_impact_interventions_raw.csv \
  --stakeholders ../data/raw/stakeholder_burden_public_value_raw.csv \
  --participation ../data/raw/participation_quality_raw.csv \
  --weights ../data/raw/public_value_scenario_weights.csv \
  --risk-register ../data/raw/social_impact_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript public_value_impact_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/public_value_impact.db < sql/schema.sql
sqlite3 outputs/public_value_impact.db < sql/analytical_queries.sql
```

## Notes

Preserve assumptions, public-value definitions, stakeholder definitions, participation records, governance owners, implementation decisions, and evaluation evidence with each analysis run.
