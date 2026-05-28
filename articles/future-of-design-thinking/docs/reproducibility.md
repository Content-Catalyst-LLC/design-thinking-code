# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python future_design_readiness_engine.py --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript future_design_readiness_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/future_design_readiness.db < sql/schema.sql
sqlite3 outputs/future_design_readiness.db < sql/analytical_queries.sql
```
