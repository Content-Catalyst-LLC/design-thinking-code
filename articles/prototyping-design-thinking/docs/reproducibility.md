# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python prototype_portfolio_engine.py \
  --portfolio ../data/raw/prototype_portfolio_raw.csv \
  --weights ../data/raw/prototype_scenario_weights.csv \
  --rounds ../data/raw/prototype_test_rounds_raw.csv \
  --risk-register ../data/raw/prototype_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript prototype_scenario_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/prototype_portfolio.db < sql/schema.sql
sqlite3 outputs/prototype_portfolio.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw prototype evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document scoring assumptions and weights.
- Preserve test conditions, participant groups, and fidelity level.
- Do not treat prototype evidence as implementation proof.
