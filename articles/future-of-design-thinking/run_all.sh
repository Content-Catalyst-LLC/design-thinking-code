#!/usr/bin/env bash
set -euo pipefail

ARTICLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running professional future design-thinking workflows..."
echo "Article directory: ${ARTICLE_DIR}"

if command -v python3 >/dev/null 2>&1; then
  echo
  echo "Running Python workflow..."
  cd "${ARTICLE_DIR}/python"
  python3 future_design_readiness_engine.py \
    --initiatives ../data/raw/future_design_initiatives_raw.csv \
    --ai-governance ../data/raw/ai_governance_maturity_raw.csv \
    --stewardship ../data/raw/stewardship_readiness_raw.csv \
    --weights ../data/raw/future_design_scenario_weights.csv \
    --risk-register ../data/raw/future_design_risk_register_raw.csv \
    --output-dir ../outputs \
    --simulations 10000
else
  echo "python3 not found. Skipping Python workflow."
fi

if command -v Rscript >/dev/null 2>&1; then
  echo
  echo "Running R workflow..."
  cd "${ARTICLE_DIR}/r"
  Rscript future_design_readiness_analysis.R
else
  echo "Rscript not found. Skipping R workflow."
fi

if command -v sqlite3 >/dev/null 2>&1; then
  echo
  echo "Running SQL workflow..."
  cd "${ARTICLE_DIR}"
  sqlite3 outputs/future_design_readiness.db < sql/schema.sql
  sqlite3 outputs/future_design_readiness.db < sql/analytical_queries.sql > outputs/sql_analysis_results.txt
else
  echo "sqlite3 not found. Skipping SQL workflow."
fi

echo
echo "Workflow complete."
echo "Outputs are in: ${ARTICLE_DIR}/outputs"
