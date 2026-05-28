# Prototyping in Design Thinking

This folder contains professional companion code and reproducible research assets for the article **“Prototyping in Design Thinking.”**

The article frames prototyping as disciplined learning under uncertainty: a way of making ideas tangible enough to be observed, misunderstood, tested, revised, compared, abandoned, or advanced on the basis of evidence. This companion repository translates that argument into reusable analytical workflows for prototype portfolio scoring, scenario weighting, uncertainty analysis, iteration improvement, risk review, and prototype decision documentation.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/prototyping-design-thinking

## Folder structure

```text
prototyping-design-thinking/
├── python/
│   ├── prototype_portfolio_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── prototype_scenario_analysis.R
├── julia/
│   └── prototype_iteration_model.jl
├── cpp/
│   └── prototype_value_engine.cpp
├── fortran/
│   └── prototype_value_model.f90
├── c/
│   └── prototype_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── prototype_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── prototype_portfolio_analysis.ipynb
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

This scaffold is designed for design researchers, UX researchers, service designers, product strategists, civic technologists, public-sector innovation teams, healthcare improvement teams, organizational innovation groups, and applied research teams that need to evaluate prototypes before moving into higher-fidelity testing, pilots, implementation, or scaling.

The code supports:

- prototype portfolio scoring;
- learning-value and feasibility-signal evaluation;
- user-response, equity-value, and implementation-relevance comparison;
- composite ethical, operational, technical, and scaling-risk modeling;
- scenario analysis under different prototyping priorities;
- Monte Carlo uncertainty modeling;
- bootstrap stability checks;
- random-weight sensitivity analysis;
- iteration improvement modeling;
- risk-register review;
- SQL-backed prototype evidence structures;
- reproducible reports, figures, and validation outputs;
- documentation of assumptions, limitations, responsible use, and next-step decisions.

## Conceptual model

A prototype \(i\) can be scored as:

\[
V_i = w_l L_i + w_f F_i + w_u U_i + w_e E_i + w_m M_i - w_r R_i
\]

where:

- \(L_i\) = learning gain;
- \(F_i\) = feasibility signal;
- \(U_i\) = user-response strength;
- \(E_i\) = equity or access value;
- \(M_i\) = implementation relevance;
- \(R_i\) = composite unresolved risk;
- \(w_l, w_f, w_u, w_e, w_m, w_r\) = explicit prototyping-priority weights.

A composite risk index may be represented as:

\[
R_i = \lambda_H H_i + \lambda_O O_i + \lambda_T T_i + \lambda_S S_i
\]

where:

- \(H_i\) = ethical risk;
- \(O_i\) = operational risk;
- \(T_i\) = technical risk;
- \(S_i\) = scaling risk.

A prototype improvement measure across rounds can be represented as:

\[
\Delta Q_t = \alpha (U_t - U_{t-1}) + \beta (C_t - C_{t-1}) + \theta (T_t - T_{t-1}) - \gamma (R_t - R_{t-1})
\]

where usability, comprehension, trust, and unresolved friction are tracked across iterative test rounds.

These models are not intended to automate prototype selection. They are transparent decision-support structures for making assumptions visible, comparing learning priorities, identifying uncertainty, and deciding what should be tested, revised, advanced, or stopped.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/prototyping-design-thinking/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python prototype_portfolio_engine.py \
  --portfolio ../data/raw/prototype_portfolio_raw.csv \
  --weights ../data/raw/prototype_scenario_weights.csv \
  --rounds ../data/raw/prototype_test_rounds_raw.csv \
  --risk-register ../data/raw/prototype_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/prototyping-design-thinking
sqlite3 outputs/prototype_portfolio.db < sql/schema.sql
sqlite3 outputs/prototype_portfolio.db < sql/analytical_queries.sql
```

## Notes

All datasets are synthetic and intended for methodological demonstration. Replace them with documented prototype-test evidence before using this workflow in real decision-support settings.
