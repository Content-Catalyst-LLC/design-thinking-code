# Design Evaluation, Learning, and Outcome Measurement

This folder contains professional companion code and reproducible research assets for the article **“Design Evaluation, Learning, and Outcome Measurement.”**

The article frames evaluation as the learning architecture that makes design thinking accountable over time. It connects design intent to evidence, evidence to interpretation, interpretation to learning, and learning to future decisions. The companion repository translates that argument into reusable analytical workflows for outcome measurement, learning agendas, theory-of-change evaluation, equity-sensitive outcomes, burden analysis, evidence-strength scoring, uncertainty modeling, post-implementation learning, and evaluation governance.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-evaluation-learning-outcome-measurement

## Folder structure

```text
design-evaluation-learning-outcome-measurement/
├── python/
│   ├── evaluation_learning_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── design_evaluation_learning_analysis.R
├── julia/
│   └── evaluation_learning_model.jl
├── cpp/
│   └── evaluation_value_engine.cpp
├── fortran/
│   └── evaluation_value_model.f90
├── c/
│   └── evaluation_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── evaluation_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── design_evaluation_learning_analysis.ipynb
├── docs/
│   ├── data-dictionary.md
│   ├── evaluation-governance-protocol.md
│   ├── learning-agenda-template.md
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

This scaffold is designed for design researchers, UX researchers, service designers, evaluation specialists, civic technologists, implementation teams, public-sector innovation groups, healthcare improvement teams, organizational learning teams, product strategists, and applied research teams that need to make outcome claims traceable.

The code supports:

- design evaluation portfolio scoring;
- outcome improvement, burden reduction, equity performance, trust improvement, durability, cost, and residual-risk analysis;
- evidence-strength and learning-priority diagnostics;
- learning-agenda and theory-of-change documentation;
- evaluation scenario analysis under different value definitions;
- Monte Carlo uncertainty modeling;
- bootstrap rank stability;
- random-weight sensitivity analysis;
- outcome time-series and post-deployment learning analysis;
- equity-gap and burden-shift tracking;
- evaluation risk-register review;
- SQL-backed evaluation evidence structures;
- reproducible reports, figures, and decision-support artifacts;
- documentation of assumptions, limits, safeguards, and next-step learning decisions.

## Conceptual model

A design intervention \(i\) can be evaluated as:

\[
V_i = w_o O_i + w_b B_i + w_e E_i + w_t T_i + w_d D_i - w_p P_i
\]

where:

- \(O_i\) = outcome improvement;
- \(B_i\) = burden reduction;
- \(E_i\) = equity performance;
- \(T_i\) = trust improvement;
- \(D_i\) = durability;
- \(P_i\) = penalty from operational cost and residual risk;
- \(w_o, w_b, w_e, w_t, w_d, w_p\) = explicit evaluation-priority weights.

Evidence strength can be modeled as:

\[
S_i = w_q Q_i + w_c C_i + w_m M_i - w_u U_i
\]

where data quality, stakeholder coverage, and method triangulation improve confidence, while uncertainty weakens it.

These models are not intended to automate evaluation. They help teams make assumptions visible, compare competing value definitions, identify uncertainty, and decide what should be revised, studied further, scaled, paused, or retired.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-evaluation-learning-outcome-measurement/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python evaluation_learning_engine.py \
  --portfolio ../data/raw/evaluation_portfolio_raw.csv \
  --weights ../data/raw/evaluation_scenario_weights.csv \
  --outcomes ../data/raw/outcome_timeseries_raw.csv \
  --learning-agenda ../data/raw/learning_agenda_raw.csv \
  --risk-register ../data/raw/evaluation_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/design-evaluation-learning-outcome-measurement
sqlite3 outputs/design_evaluation.db < sql/schema.sql
sqlite3 outputs/design_evaluation.db < sql/analytical_queries.sql
```

## Notes

All datasets are synthetic and intended for methodological demonstration. Replace them with documented evaluation evidence before using this workflow in real decision-support settings.
