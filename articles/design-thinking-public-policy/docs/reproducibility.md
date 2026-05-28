# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python public_policy_design_engine.py \
  --pilots ../data/raw/public_policy_pilots_raw.csv \
  --weights ../data/raw/public_policy_scenario_weights.csv \
  --learning ../data/raw/policy_learning_pathways_raw.csv \
  --burdens ../data/raw/administrative_burden_raw.csv \
  --risk-register ../data/raw/public_policy_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript public_policy_design_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/public_policy_design.db < sql/schema.sql
sqlite3 outputs/public_policy_design.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw public-policy and service evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document scenario weights and scoring assumptions.
- Preserve policy boundaries, legal constraints, stakeholder coverage, and participation limits.
- Distinguish implementation success from legitimacy, equity, access, and burden outcomes.
