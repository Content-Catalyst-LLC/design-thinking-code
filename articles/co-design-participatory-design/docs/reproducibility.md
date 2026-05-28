# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python co_design_participatory_design_engine.py \
  --activities ../data/raw/codesign_activities_raw.csv \
  --participants ../data/raw/participant_groups_raw.csv \
  --weights ../data/raw/participation_scenario_weights.csv \
  --learning ../data/raw/participatory_prototype_learning_raw.csv \
  --risk-register ../data/raw/participation_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript co_design_participatory_design_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/codesign_participatory_design.db < sql/schema.sql
sqlite3 outputs/codesign_participatory_design.db < sql/analytical_queries.sql
```

## Reproducibility notes

- Store raw participation evidence in `data/raw/`.
- Store transformed or scored outputs in `data/processed/` or `outputs/`.
- Document scoring assumptions and scenario weights.
- Preserve recruitment limits, missing groups, access supports, compensation notes, ethical risks, and feedback obligations.
- Distinguish participant presence from participant influence.
