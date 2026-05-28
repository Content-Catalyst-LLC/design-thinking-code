# Reproducibility Guide

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python behavioral_design_engine.py --barriers ../data/raw/behavioral_barriers_raw.csv --interventions ../data/raw/behavioral_interventions_raw.csv --experiments ../data/raw/behavioral_experiment_results_raw.csv --weights ../data/raw/behavioral_scenario_weights.csv --risk-register ../data/raw/behavioral_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript behavioral_design_analysis.R
```

## SQL

```bash
sqlite3 outputs/behavioral_design.db < sql/schema.sql
sqlite3 outputs/behavioral_design.db < sql/analytical_queries.sql
```
