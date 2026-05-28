# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python organizational_innovation_engine.py \
  --concepts ../data/raw/organizational_innovation_concepts_raw.csv \
  --weights ../data/raw/innovation_scenario_weights.csv \
  --learning ../data/raw/prototype_learning_rounds_raw.csv \
  --friction ../data/raw/organizational_friction_raw.csv \
  --risk-register ../data/raw/innovation_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript organizational_innovation_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/organizational_innovation.db < sql/schema.sql
sqlite3 outputs/organizational_innovation.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw design research and operational evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document portfolio weights and scoring assumptions.
- Preserve stakeholder coverage, implementation constraints, and ethical risk notes.
- Distinguish adoption success from equity, trust, burden, and durability outcomes.
