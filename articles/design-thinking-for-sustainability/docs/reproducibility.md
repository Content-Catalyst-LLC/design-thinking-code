# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python sustainability_design_engine.py \
  --concepts ../data/raw/sustainability_concepts_raw.csv \
  --weights ../data/raw/sustainability_scenario_weights.csv \
  --transitions ../data/raw/transition_pathways_raw.csv \
  --risk-register ../data/raw/sustainability_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript sustainability_design_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/sustainability_design.db < sql/schema.sql
sqlite3 outputs/sustainability_design.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw sustainability and lifecycle evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document scenario weights and scoring assumptions.
- Preserve lifecycle boundaries, stakeholder coverage, and evidence limitations.
- Distinguish ecological claims from usability, adoption, or branding claims.
