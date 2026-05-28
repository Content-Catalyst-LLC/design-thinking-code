# Human-Centered Problem Solving

This folder contains professional companion code and reproducible research assets for the article **“Human-Centered Problem Solving.”**

The article frames human-centered problem solving as a disciplined approach to innovation and institutional design that begins with lived experience, stakeholder evidence, contextual observation, burden analysis, systems awareness, and iterative learning. This repository folder translates that conceptual discussion into reusable analytical workflows for assessing human-centered design options, modeling burden, comparing stakeholder priorities, stress-testing uncertainty, and documenting research decisions.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/human-centered-problem-solving

## Folder structure

```text
human-centered-problem-solving/
├── python/
│   ├── human_centered_decision_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── human_centered_scenario_analysis.R
├── julia/
│   └── human_centered_portfolio.jl
├── cpp/
│   └── human_centered_value_engine.cpp
├── fortran/
│   └── human_centered_value_model.f90
├── c/
│   └── human_centered_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── human_centered_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── human_centered_design_analysis.ipynb
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

This scaffold is designed for human-centered design researchers, service designers, public-sector innovation teams, institutional strategy groups, healthcare improvement teams, UX researchers, civic technologists, social-impact teams, and applied researchers who need reproducible decision support rather than informal design artifacts alone.

The code supports:

- human-centered design option scoring;
- burden and friction modeling;
- stakeholder-fit analysis;
- scenario analysis under different institutional priorities;
- Monte Carlo uncertainty modeling;
- weight sensitivity analysis;
- bootstrap stability checks;
- SQL-backed design-research data structure;
- reproducible reporting and output generation;
- documentation of assumptions, constraints, and limitations.

## Conceptual model

A candidate design option \(i\) is scored as:

\[
V_i = w_b B_i + w_u U_i + w_s S_i - w_c C_i
\]

where:

- \(B_i\) = human benefit;
- \(U_i\) = usability or intelligibility;
- \(S_i\) = stakeholder fit;
- \(C_i\) = burden or user cost;
- \(w_b, w_u, w_s, w_c\) = institutional priority weights.

A separate burden index may be modeled as:

\[
C_i = \lambda_L L_i + \lambda_K K_i + \lambda_P P_i + \lambda_A A_i
\]

where:

- \(L_i\) = learning cost;
- \(K_i\) = compliance cost;
- \(P_i\) = psychological cost;
- \(A_i\) = access cost.

These models are not intended to automate design judgment. They are transparent decision-support structures for making assumptions visible, comparing alternatives, and identifying where additional research is needed.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/human-centered-problem-solving/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python human_centered_decision_engine.py \
  --input ../data/raw/human_centered_options_raw.csv \
  --weights ../data/raw/human_centered_scenario_weights.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/human-centered-problem-solving
sqlite3 outputs/human_centered_problem_solving.db < sql/schema.sql
sqlite3 outputs/human_centered_problem_solving.db < sql/analytical_queries.sql
```

## Notes

All scores in the example dataset are synthetic and intended for methodological demonstration. Replace them with documented research findings before using this workflow in real decision-support settings.
