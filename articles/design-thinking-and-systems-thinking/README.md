# Design Thinking and Systems Thinking

This folder contains professional companion code and reproducible research assets for the article **“Design Thinking and Systems Thinking.”**

The article frames design thinking and systems thinking as complementary methods for working with complex institutional, technological, social, ecological, and service-system problems. Design thinking keeps inquiry grounded in lived experience, touchpoints, prototypes, and human consequences. Systems thinking extends that inquiry to feedback loops, delays, leverage points, information flows, incentives, governance, stocks and flows, burden shifts, and long-horizon system behavior.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-thinking-and-systems-thinking

## Folder structure

```text
design-thinking-and-systems-thinking/
├── python/
│   ├── systems_design_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── systems_design_analysis.R
├── julia/
│   └── systems_feedback_model.jl
├── cpp/
│   └── system_design_value_engine.cpp
├── fortran/
│   └── system_design_value_model.f90
├── c/
│   └── system_design_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── system_design_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── design_system_intervention_analysis.ipynb
├── docs/
│   ├── data-dictionary.md
│   ├── leverage-mapping-protocol.md
│   ├── method-note.md
│   ├── model-card.md
│   ├── reproducibility.md
│   ├── system-mapping-template.md
│   └── validation-protocol.md
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for design researchers, service designers, systems designers, civic technologists, implementation teams, organizational strategists, public-sector innovation groups, sustainability analysts, product strategists, UX researchers, and applied research teams that need to evaluate interventions across both human-centered and system-level criteria.

The code supports:

- system intervention portfolio scoring;
- human-centered value, systemic leverage, feasibility, equity sensitivity, durability, implementation risk, and burden-shift analysis;
- strategic scenario weighting;
- Monte Carlo uncertainty modeling;
- bootstrap stability;
- random-weight sensitivity;
- feedback and delay simulation;
- simple stock-and-flow stress testing;
- leverage-level classification;
- learning-priority diagnostics;
- SQL-backed system-intervention evidence structures;
- reproducible reports, figures, and decision-support artifacts;
- documentation of assumptions, boundaries, risks, leverage hypotheses, and validation steps.

## Conceptual model

An intervention \(i\) can be evaluated as:

\[
V_i = w_h H_i + w_s S_i + w_f F_i + w_e E_i + w_d D_i - w_r R_i
\]

where:

- \(H_i\) = human-centered value;
- \(S_i\) = systemic leverage;
- \(F_i\) = feasibility;
- \(E_i\) = equity sensitivity;
- \(D_i\) = durability;
- \(R_i\) = implementation and unintended-consequence risk.

System behavior can be represented with a delayed feedback model:

\[
P_{t+1} = P_t + \alpha I_t - \beta A_{t-d}
\]

where visible performance improves through intervention intensity but can be reduced later by delayed adaptation, drift, or unintended feedback.

These models are not intended to automate system-redesign decisions. They help teams make assumptions visible, compare competing value definitions, identify uncertainty, and decide what should be prototyped, studied, governed, scaled, paused, or redesigned.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-and-systems-thinking/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python systems_design_engine.py \
  --portfolio ../data/raw/system_intervention_portfolio_raw.csv \
  --weights ../data/raw/system_design_scenario_weights.csv \
  --feedback ../data/raw/feedback_dynamics_raw.csv \
  --risk-register ../data/raw/system_intervention_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-and-systems-thinking
sqlite3 outputs/system_design.db < sql/schema.sql
sqlite3 outputs/system_design.db < sql/analytical_queries.sql
```

## Notes

All datasets are synthetic and intended for methodological demonstration. Replace them with documented system, service, policy, implementation, and stakeholder evidence before using this workflow in real decision-support settings.
