# Reproducibility Guide

## Recommended workflow

1. Store original or synthetic source data in `data/raw/`.
2. Store cleaned or transformed data in `data/processed/`.
3. Store generated tables, reports, charts, and model outputs in `outputs/`.
4. Preserve assumptions and interpretation notes in `docs/`.
5. Use deterministic seeds for simulations.
6. Avoid overwriting raw data.
7. Review validation warnings before interpreting results.

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python human_centered_decision_engine.py \
  --input ../data/raw/human_centered_options_raw.csv \
  --weights ../data/raw/human_centered_scenario_weights.csv \
  --stakeholders ../data/raw/stakeholder_groups_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript human_centered_scenario_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/human_centered_problem_solving.db < sql/schema.sql
sqlite3 outputs/human_centered_problem_solving.db < sql/analytical_queries.sql
```

## Systems-language examples

The C, C++, Rust, Go, Julia, and Fortran examples are included to support professional engineering-style reproducibility and cross-language implementation patterns.
