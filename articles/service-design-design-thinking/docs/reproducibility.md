# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python service_design_engine.py \
  --stages ../data/raw/service_journey_stages_raw.csv \
  --groups ../data/raw/service_user_groups_raw.csv \
  --blueprint ../data/raw/service_blueprint_dependencies_raw.csv \
  --weights ../data/raw/service_scenario_weights.csv \
  --risk-register ../data/raw/service_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript service_design_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/service_design.db < sql/schema.sql
sqlite3 outputs/service_design.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw service research and operational evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document scoring assumptions and scenario weights.
- Preserve journey-stage definitions, user-group definitions, accessibility assumptions, operational constraints, and governance owners.
- Distinguish average service quality from group-specific equity and accessibility gaps.
