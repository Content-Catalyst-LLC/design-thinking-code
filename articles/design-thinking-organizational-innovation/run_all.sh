#!/usr/bin/env bash
set -euo pipefail

ARTICLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running professional design thinking and organizational innovation companion workflows..."
echo "Article directory: ${ARTICLE_DIR}"

if command -v python3 >/dev/null 2>&1; then
  echo
  echo "Running Python workflow..."
  cd "${ARTICLE_DIR}/python"
  python3 organizational_innovation_engine.py \
    --concepts ../data/raw/organizational_innovation_concepts_raw.csv \
    --weights ../data/raw/innovation_scenario_weights.csv \
    --learning ../data/raw/prototype_learning_rounds_raw.csv \
    --friction ../data/raw/organizational_friction_raw.csv \
    --risk-register ../data/raw/innovation_risk_register_raw.csv \
    --output-dir ../outputs \
    --simulations 10000
else
  echo "python3 not found. Skipping Python workflow."
fi

if command -v Rscript >/dev/null 2>&1; then
  echo
  echo "Running R workflow..."
  cd "${ARTICLE_DIR}/r"
  Rscript organizational_innovation_analysis.R
else
  echo "Rscript not found. Skipping R workflow."
fi

if command -v sqlite3 >/dev/null 2>&1; then
  echo
  echo "Running SQL workflow..."
  cd "${ARTICLE_DIR}"
  sqlite3 outputs/organizational_innovation.db < sql/schema.sql
  sqlite3 outputs/organizational_innovation.db < sql/analytical_queries.sql > outputs/sql_analysis_results.txt
else
  echo "sqlite3 not found. Skipping SQL workflow."
fi

echo
echo "Workflow complete."
echo "Outputs are in: ${ARTICLE_DIR}/outputs"
