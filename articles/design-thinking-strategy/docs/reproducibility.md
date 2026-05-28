# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python strategy_design_engine.py \
  --options ../data/raw/strategic_options_raw.csv \
  --assumptions ../data/raw/strategic_assumptions_raw.csv \
  --weights ../data/raw/strategy_scenario_weights.csv \
  --risk-register ../data/raw/strategy_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript strategy_design_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/strategy_design.db < sql/schema.sql
sqlite3 outputs/strategy_design.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw strategic evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document option definitions, assumptions, criteria, scenario weights, and decision thresholds.
- Preserve prototype evidence, stakeholder evidence, ethics review, implementation review, and governance records.
