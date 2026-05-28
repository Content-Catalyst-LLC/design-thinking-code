# Reproducibility Guide

## Python workflow

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ai_research_evidence_engine.py \
  --signals ../data/raw/research_signals_raw.csv \
  --ai-log ../data/raw/ai_assistance_log_raw.csv \
  --metadata ../data/raw/evidence_metadata_registry_raw.csv \
  --weights ../data/raw/research_scenario_weights.csv \
  --risk-register ../data/raw/research_governance_risk_register_raw.csv \
  --output-dir ../outputs
```

## R workflow

```bash
cd r
Rscript ai_research_evidence_analysis.R
```

## SQL workflow

```bash
sqlite3 outputs/ai_research_evidence.db < sql/schema.sql
sqlite3 outputs/ai_research_evidence.db < sql/analytical_queries.sql
```

## Notes

Preserve raw evidence, metadata, consent records, AI-use logs, and decision traces with each analysis run.
