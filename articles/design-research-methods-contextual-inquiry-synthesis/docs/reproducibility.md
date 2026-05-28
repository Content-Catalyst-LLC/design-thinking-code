# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contextual_inquiry_synthesis_engine.py \
  --evidence ../data/raw/contextual_inquiry_evidence_units_raw.csv \
  --weights ../data/raw/synthesis_scenario_weights.csv \
  --coder-map ../data/raw/coder_theme_assignments_raw.csv \
  --sampling-frame ../data/raw/stakeholder_sampling_frame_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript contextual_inquiry_theme_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/contextual_inquiry_synthesis.db < sql/schema.sql
sqlite3 outputs/contextual_inquiry_synthesis.db < sql/analytical_queries.sql
```

## General reproducibility notes

- Store raw evidence in `data/raw/`.
- Store cleaned or coded data in `data/processed/`.
- Store generated figures, tables, and reports in `outputs/`.
- Document assumptions and interpretation decisions in `docs/`.
- Preserve links between evidence units, themes, and design decisions.
- Review validation priorities before using themes to guide prototyping.
