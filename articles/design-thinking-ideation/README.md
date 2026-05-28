# Ideation in Design Thinking

This folder contains professional companion code and reproducible research assets for the article **“Ideation in Design Thinking.”**

The article frames ideation as a disciplined method for expanding the solution space before judgment narrows it again. Ideation is treated as structured imagination grounded in stakeholder research, problem framing, insight generation, ethics, constraints, systems thinking, and later validation. This companion repository translates that discussion into reusable analytical workflows for comparing idea portfolios, modeling divergence, evaluating idea value, examining residual risk, assessing equity and learning value, and testing selection robustness under uncertainty.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-thinking-ideation

## Folder structure

```text
design-thinking-ideation/
├── python/
│   ├── ideation_portfolio_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── ideation_scenario_analysis.R
├── julia/
│   └── ideation_portfolio_model.jl
├── cpp/
│   └── idea_value_engine.cpp
├── fortran/
│   └── idea_value_model.f90
├── c/
│   └── idea_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── idea_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── ideation_portfolio_analysis.ipynb
├── docs/
│   ├── data-dictionary.md
│   ├── method-note.md
│   ├── model-card.md
│   ├── reproducibility.md
│   └── validation-protocol.md
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for design researchers, service designers, public-sector innovation teams, civic technologists, UX researchers, product strategists, organizational innovation teams, healthcare improvement teams, and applied research groups that need to evaluate ideas before moving into prototyping, testing, iteration, or implementation planning.

The code supports:

- idea portfolio scoring;
- divergence and idea-cluster analysis;
- desirability, feasibility, novelty, equity, and learning-value modeling;
- composite risk and residual-risk decomposition;
- ethical, operational, technical, and scaling-risk diagnostics;
- scenario analysis under different selection priorities;
- Monte Carlo uncertainty modeling;
- bootstrap stability checks;
- random-weight sensitivity analysis;
- SQL-backed ideation evidence structure;
- reproducible reporting and output generation;
- documentation of assumptions, limitations, validation needs, and responsible-use constraints.

## Conceptual model

A candidate idea \(i\) is scored as:

\[
V_i = w_d D_i + w_f F_i + w_n N_i + w_e E_i + w_l L_i - w_r R_i
\]

where:

- \(D_i\) = desirability;
- \(F_i\) = feasibility;
- \(N_i\) = novelty;
- \(E_i\) = equity value;
- \(L_i\) = learning value;
- \(R_i\) = composite unresolved risk;
- \(w_d, w_f, w_n, w_e, w_l, w_r\) = ideation-priority weights.

A separate risk index may be modeled as:

\[
R_i = \lambda_H H_i + \lambda_O O_i + \lambda_T T_i + \lambda_S S_i
\]

where:

- \(H_i\) = ethical risk;
- \(O_i\) = operational risk;
- \(T_i\) = technical risk;
- \(S_i\) = scaling risk.

These models are not intended to automate idea selection. They are transparent decision-support structures for making assumptions visible, comparing ideas, identifying uncertainty, and deciding which concepts merit prototyping, refinement, or further research.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-ideation/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ideation_portfolio_engine.py \
  --input ../data/raw/idea_portfolio_raw.csv \
  --weights ../data/raw/ideation_scenario_weights.csv \
  --clusters ../data/raw/idea_cluster_map_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-ideation
sqlite3 outputs/ideation_portfolio.db < sql/schema.sql
sqlite3 outputs/ideation_portfolio.db < sql/analytical_queries.sql
```

## Notes

All scores in the example dataset are synthetic and intended for methodological demonstration. Replace them with documented design-research evidence before using this workflow in real decision-support settings.
