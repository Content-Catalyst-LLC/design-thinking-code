# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python systems_design_engine.py \
  --portfolio ../data/raw/system_intervention_portfolio_raw.csv \
  --weights ../data/raw/system_design_scenario_weights.csv \
  --feedback ../data/raw/feedback_dynamics_raw.csv \
  --risk-register ../data/raw/system_intervention_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript systems_design_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/system_design.db < sql/schema.sql
sqlite3 outputs/system_design.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw system and service evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document scoring assumptions and scenario weights.
- Preserve system-map boundaries, stakeholder coverage, and evidence limits.
- Distinguish local prototype success from system-level change.
