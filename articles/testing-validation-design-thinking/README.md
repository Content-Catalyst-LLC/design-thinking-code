# Testing and Validation in Design Thinking

This folder contains professional companion code and reproducible research assets for the article **“Testing and Validation in Design Thinking.”**

The article frames testing and validation as the stage where design claims encounter evidence. Testing is treated not as a late-stage demo ritual, but as disciplined inquiry: a way to examine whether a concept is understandable, usable, meaningful, feasible, viable, responsible, equitable, and robust enough to justify further investment.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/testing-validation-design-thinking

## Folder structure

```text
testing-validation-design-thinking/
├── python/
│   ├── testing_validation_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── testing_validation_scenario_analysis.R
├── julia/
│   └── validation_uncertainty_model.jl
├── cpp/
│   └── validation_value_engine.cpp
├── fortran/
│   └── validation_value_model.f90
├── c/
│   └── validation_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── validation_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── testing_validation_analysis.ipynb
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

This scaffold is designed for design researchers, UX researchers, service designers, product strategists, civic technologists, public-sector innovation teams, healthcare improvement teams, education researchers, organizational innovation groups, and applied research teams that need to document prototype-test evidence and make validation decisions traceable.

The code supports:

- validation portfolio scoring;
- desirability, feasibility, viability, responsibility, friction, and residual-risk analysis;
- testing outcome review across concepts;
- evidence quality and stakeholder coverage diagnostics;
- scenario analysis under different validation priorities;
- Monte Carlo uncertainty modeling;
- bootstrap rank stability;
- random-weight sensitivity analysis;
- iteration and learning-curve analysis;
- decision-threshold review;
- validation risk-register scoring;
- SQL-backed validation evidence structures;
- reproducible reports, figures, and validation artifacts;
- documentation of assumptions, limits, safeguards, and next-step decisions.

## Conceptual model

A design concept \(i\) can be evaluated as:

\[
V_i = w_d D_i + w_f F_i + w_v Vi_i + w_s S_i - w_r R_i
\]

where:

- \(D_i\) = desirability;
- \(F_i\) = feasibility;
- \(Vi_i\) = viability;
- \(S_i\) = responsibility or safety;
- \(R_i\) = residual friction or unresolved risk;
- \(w_d, w_f, w_v, w_s, w_r\) = explicit validation-priority weights.

Iteration quality can be modeled as:

\[
\Delta Q_t = \alpha(A_t - A_{t-1}) - \beta(R_t - R_{t-1}) + \gamma(C_t - C_{t-1}) + \theta(T_t - T_{t-1})
\]

where adoption, friction, comprehension, and trust are tracked across testing rounds.

These models are not intended to automate validation. They help design teams make assumptions visible, compare competing validation standards, identify uncertainty, and decide what should be revised, advanced, stopped, or tested next.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/testing-validation-design-thinking/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python testing_validation_engine.py \
  --concepts ../data/raw/validation_concepts_raw.csv \
  --weights ../data/raw/validation_scenario_weights.csv \
  --rounds ../data/raw/testing_rounds_raw.csv \
  --thresholds ../data/raw/decision_thresholds_raw.csv \
  --risk-register ../data/raw/validation_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/testing-validation-design-thinking
sqlite3 outputs/testing_validation.db < sql/schema.sql
sqlite3 outputs/testing_validation.db < sql/analytical_queries.sql
```

## Notes

All datasets are synthetic and intended for methodological demonstration. Replace them with documented validation evidence before using this workflow in real decision-support settings.
