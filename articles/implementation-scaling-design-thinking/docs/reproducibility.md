# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python implementation_scaling_engine.py \
  --portfolio ../data/raw/implementation_portfolio_raw.csv \
  --weights ../data/raw/implementation_scenario_weights.csv \
  --rollout ../data/raw/rollout_stage_metrics_raw.csv \
  --risk-register ../data/raw/implementation_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript implementation_scaling_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/implementation_scaling.db < sql/schema.sql
sqlite3 outputs/implementation_scaling.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw implementation evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document scoring assumptions and scenario weights.
- Preserve rollout conditions, sites, stakeholder groups, and governance decisions.
- Distinguish pilot success from scale readiness.
