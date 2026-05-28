# Design Thinking in Public Policy

This folder contains professional companion code and reproducible research assets for the article **“Design Thinking in Public Policy.”**

The article frames public-policy design as a serious practice for connecting law, public administration, lived experience, administrative burden, legitimacy, equity, implementation capacity, systems thinking, and iterative policy learning. The companion repository turns that argument into reusable workflows for public-policy pilot prioritization, accessibility analysis, administrative-burden scoring, legitimacy and trust review, equity diagnostics, implementation-risk analysis, uncertainty modeling, policy feedback, and public-value documentation.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-thinking-public-policy

## Folder structure

```text
design-thinking-public-policy/
├── python/
│   ├── public_policy_design_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── public_policy_design_analysis.R
├── julia/
│   └── policy_learning_model.jl
├── cpp/
│   └── policy_value_engine.cpp
├── fortran/
│   └── policy_value_model.f90
├── c/
│   └── policy_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── policy_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── public_policy_design_analysis.ipynb
├── docs/
│   ├── administrative-burden-protocol.md
│   ├── data-dictionary.md
│   ├── method-note.md
│   ├── model-card.md
│   ├── participation-and-legitimacy-protocol.md
│   ├── policy-feedback-template.md
│   ├── reproducibility.md
│   └── validation-protocol.md
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for public-sector design teams, policy labs, civic-technology groups, public administrators, implementation researchers, service designers, policy analysts, social scientists, evaluation teams, public-benefit offices, public-health teams, housing agencies, climate-adaptation offices, licensing agencies, regulatory bodies, and institutional research teams that need to compare policy pilots across public-value dimensions.

The code supports:

- public-policy pilot portfolio scoring;
- accessibility, feasibility, legitimacy, equity, burden reduction, durability, and risk analysis;
- evidence-strength and stakeholder-coverage diagnostics;
- administrative-burden distribution analysis;
- scenario-weighted public-value comparison;
- Monte Carlo uncertainty modeling;
- bootstrap stability analysis;
- random-weight sensitivity analysis;
- policy-learning pathway diagnostics;
- policy risk-register prioritization;
- SQL-backed public-policy evidence structures;
- reproducible reports, figures, and decision-support artifacts;
- documentation of assumptions, public-value weights, evidence limits, participation quality, implementation constraints, and responsible-use boundaries.

## Conceptual model

A policy pilot \(i\) can be evaluated as:

\[
V_i = w_a A_i + w_f F_i + w_l L_i + w_e E_i + w_b B_i + w_d D_i - w_r R_i
\]

where:

- \(A_i\) = accessibility and public legibility;
- \(F_i\) = feasibility;
- \(L_i\) = legitimacy, trust, and public acceptability;
- \(E_i\) = equity adequacy;
- \(B_i\) = administrative-burden reduction;
- \(D_i\) = implementation durability;
- \(R_i\) = implementation and unintended-consequence risk.

Policy learning across pilots can be represented as:

\[
\Delta Q_t = \alpha \Delta U_t - \beta \Delta C_t - \gamma \Delta I_t + \theta \Delta T_t + \lambda \Delta E_t
\]

where uptake, citizen friction, implementation error, trust, and equity change shape whether a public-policy prototype is improving across rounds.

These models are not intended to automate policy decisions. They help teams make assumptions visible, compare competing public values, identify fragile conclusions, and decide what should be prototyped, revised, governed, scaled, paused, or retired.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-public-policy/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python public_policy_design_engine.py \
  --pilots ../data/raw/public_policy_pilots_raw.csv \
  --weights ../data/raw/public_policy_scenario_weights.csv \
  --learning ../data/raw/policy_learning_pathways_raw.csv \
  --burdens ../data/raw/administrative_burden_raw.csv \
  --risk-register ../data/raw/public_policy_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-public-policy
sqlite3 outputs/public_policy_design.db < sql/schema.sql
sqlite3 outputs/public_policy_design.db < sql/analytical_queries.sql
```

## Notes

All datasets are synthetic and intended for methodological demonstration. Replace them with documented policy, administrative, service, legal, public participation, stakeholder, implementation, and governance evidence before using this workflow in real decision-support settings.
