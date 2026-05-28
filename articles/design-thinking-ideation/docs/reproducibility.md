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
python ideation_portfolio_engine.py \
  --input ../data/raw/idea_portfolio_raw.csv \
  --weights ../data/raw/ideation_scenario_weights.csv \
  --clusters ../data/raw/idea_cluster_map_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript ideation_scenario_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/ideation_portfolio.db < sql/schema.sql
sqlite3 outputs/ideation_portfolio.db < sql/analytical_queries.sql
```

## Systems-language examples

The C, C++, Rust, Go, Julia, and Fortran examples are included to support professional engineering-style reproducibility and cross-language implementation patterns.
