# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python evaluation_learning_engine.py \
  --portfolio ../data/raw/evaluation_portfolio_raw.csv \
  --weights ../data/raw/evaluation_scenario_weights.csv \
  --outcomes ../data/raw/outcome_timeseries_raw.csv \
  --learning-agenda ../data/raw/learning_agenda_raw.csv \
  --risk-register ../data/raw/evaluation_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript design_evaluation_learning_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/design_evaluation.db < sql/schema.sql
sqlite3 outputs/design_evaluation.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw evaluation evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document scoring assumptions and scenario weights.
- Preserve baseline definitions, evaluation periods, stakeholder coverage, and evidence limits.
- Distinguish evaluation findings from causal claims unless the design supports causal inference.
