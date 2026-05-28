# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python testing_validation_engine.py \
  --concepts ../data/raw/validation_concepts_raw.csv \
  --weights ../data/raw/validation_scenario_weights.csv \
  --rounds ../data/raw/testing_rounds_raw.csv \
  --thresholds ../data/raw/decision_thresholds_raw.csv \
  --risk-register ../data/raw/validation_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript testing_validation_scenario_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/testing_validation.db < sql/schema.sql
sqlite3 outputs/testing_validation.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw testing evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document scoring assumptions and weights.
- Preserve test conditions, participants, fidelity level, and moderator notes.
- Distinguish concept validation from implementation proof.
