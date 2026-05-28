#!/usr/bin/env bash
set -euo pipefail

ARTICLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running professional ethics, power, and inclusion companion workflows..."
echo "Article directory: ${ARTICLE_DIR}"

if command -v python3 >/dev/null 2>&1; then
  echo
  echo "Running Python workflow..."
  cd "${ARTICLE_DIR}/python"
  python3 ethics_power_inclusion_engine.py \
    --stakeholders ../data/raw/stakeholder_groups_raw.csv \
    --decisions ../data/raw/ethical_design_decisions_raw.csv \
    --participation ../data/raw/participation_power_raw.csv \
    --weights ../data/raw/ethics_scenario_weights.csv \
    --risk-register ../data/raw/design_governance_risk_register_raw.csv \
    --output-dir ../outputs \
    --simulations 10000
else
  echo "python3 not found. Skipping Python workflow."
fi

if command -v Rscript >/dev/null 2>&1; then
  echo
  echo "Running R workflow..."
  cd "${ARTICLE_DIR}/r"
  Rscript ethics_power_inclusion_analysis.R
else
  echo "Rscript not found. Skipping R workflow."
fi

if command -v sqlite3 >/dev/null 2>&1; then
  echo
  echo "Running SQL workflow..."
  cd "${ARTICLE_DIR}"
  sqlite3 outputs/ethics_power_inclusion.db < sql/schema.sql
  sqlite3 outputs/ethics_power_inclusion.db < sql/analytical_queries.sql > outputs/sql_analysis_results.txt
else
  echo "sqlite3 not found. Skipping SQL workflow."
fi

echo
echo "Workflow complete."
echo "Outputs are in: ${ARTICLE_DIR}/outputs"
