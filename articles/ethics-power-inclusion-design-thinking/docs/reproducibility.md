# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ethics_power_inclusion_engine.py \
  --stakeholders ../data/raw/stakeholder_groups_raw.csv \
  --decisions ../data/raw/ethical_design_decisions_raw.csv \
  --participation ../data/raw/participation_power_raw.csv \
  --weights ../data/raw/ethics_scenario_weights.csv \
  --risk-register ../data/raw/design_governance_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript ethics_power_inclusion_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/ethics_power_inclusion.db < sql/schema.sql
sqlite3 outputs/ethics_power_inclusion.db < sql/analytical_queries.sql
```

## Notes

Keep raw evidence, scoring assumptions, stakeholder definitions, governance owners, and repair commitments documented with every analysis run.
