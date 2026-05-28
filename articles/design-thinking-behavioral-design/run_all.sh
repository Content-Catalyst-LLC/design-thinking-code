#!/usr/bin/env bash
set -euo pipefail

ARTICLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running professional behavioral design companion workflows..."
echo "Article directory: ${ARTICLE_DIR}"

if command -v python3 >/dev/null 2>&1; then
  cd "${ARTICLE_DIR}/python"
  python3 behavioral_design_engine.py     --barriers ../data/raw/behavioral_barriers_raw.csv     --interventions ../data/raw/behavioral_interventions_raw.csv     --experiments ../data/raw/behavioral_experiment_results_raw.csv     --weights ../data/raw/behavioral_scenario_weights.csv     --risk-register ../data/raw/behavioral_risk_register_raw.csv     --output-dir ../outputs     --simulations 10000
else
  echo "python3 not found. Skipping Python workflow."
fi

if command -v Rscript >/dev/null 2>&1; then
  cd "${ARTICLE_DIR}/r"
  Rscript behavioral_design_analysis.R
else
  echo "Rscript not found. Skipping R workflow."
fi

if command -v sqlite3 >/dev/null 2>&1; then
  cd "${ARTICLE_DIR}"
  sqlite3 outputs/behavioral_design.db < sql/schema.sql
  sqlite3 outputs/behavioral_design.db < sql/analytical_queries.sql > outputs/sql_analysis_results.txt
else
  echo "sqlite3 not found. Skipping SQL workflow."
fi

echo "Workflow complete."
echo "Outputs are in: ${ARTICLE_DIR}/outputs"
