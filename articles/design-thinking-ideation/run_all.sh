#!/usr/bin/env bash
set -euo pipefail

ARTICLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running professional ideation companion workflows..."
echo "Article directory: ${ARTICLE_DIR}"

if command -v python3 >/dev/null 2>&1; then
  echo
  echo "Running Python workflow..."
  cd "${ARTICLE_DIR}/python"
  python3 ideation_portfolio_engine.py \
    --input ../data/raw/idea_portfolio_raw.csv \
    --weights ../data/raw/ideation_scenario_weights.csv \
    --clusters ../data/raw/idea_cluster_map_raw.csv \
    --output-dir ../outputs \
    --simulations 10000
else
  echo "python3 not found. Skipping Python workflow."
fi

if command -v Rscript >/dev/null 2>&1; then
  echo
  echo "Running R workflow..."
  cd "${ARTICLE_DIR}/r"
  Rscript ideation_scenario_analysis.R
else
  echo "Rscript not found. Skipping R workflow."
fi

if command -v sqlite3 >/dev/null 2>&1; then
  echo
  echo "Running SQL workflow..."
  cd "${ARTICLE_DIR}"
  sqlite3 outputs/ideation_portfolio.db < sql/schema.sql
  sqlite3 outputs/ideation_portfolio.db < sql/analytical_queries.sql > outputs/sql_analysis_results.txt
else
  echo "sqlite3 not found. Skipping SQL workflow."
fi

echo
echo "Workflow complete."
echo "Outputs are in: ${ARTICLE_DIR}/outputs"
