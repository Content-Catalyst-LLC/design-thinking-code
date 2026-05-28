# Design Thinking for Sustainability

This folder contains professional companion code and reproducible research assets for the article **“Design Thinking for Sustainability.”**

The article frames sustainability design as a disciplined practice for translating ecological limits, human needs, institutional constraints, behavioral realities, and long-term resilience into usable, equitable, measurable, and governable interventions. The companion repository turns that argument into reusable workflows for sustainability concept prioritization, ecological trade-off analysis, circularity assessment, equity and burden evaluation, lifecycle-evidence documentation, implementation risk review, and uncertainty modeling.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-thinking-for-sustainability

## Folder structure

```text
design-thinking-for-sustainability/
├── python/
│   ├── sustainability_design_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── sustainability_design_analysis.R
├── julia/
│   └── sustainability_transition_model.jl
├── cpp/
│   └── sustainability_value_engine.cpp
├── fortran/
│   └── sustainability_value_model.f90
├── c/
│   └── sustainability_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── sustainability_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── sustainability_design_analysis.ipynb
├── docs/
│   ├── data-dictionary.md
│   ├── lifecycle-evidence-protocol.md
│   ├── method-note.md
│   ├── model-card.md
│   ├── reproducibility.md
│   ├── transition-design-template.md
│   └── validation-protocol.md
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for sustainability designers, service designers, design researchers, environmental analysts, circular-economy teams, urban innovation teams, public-sector sustainability offices, institutional transformation teams, lifecycle analysts, policy labs, climate-adaptation programs, infrastructure teams, UX researchers, and applied research teams that need to compare sustainability interventions across human, ecological, institutional, and implementation dimensions.

The code supports:

- sustainability concept portfolio scoring;
- ecological benefit, circularity, equity, usability, durability, feasibility, and risk comparison;
- strategic scenario weighting;
- Monte Carlo uncertainty analysis;
- bootstrap stability analysis;
- random-weight sensitivity analysis;
- transition-pathway time-series diagnostics;
- lifecycle-evidence review;
- burden-shift and equity-risk review;
- SQL-backed sustainability evidence structures;
- reproducible reports, figures, and decision-support artifacts;
- documentation of assumptions, data provenance, system boundaries, validation steps, and responsible-use limits.

## Conceptual model

A sustainability concept \(i\) can be evaluated as:

\[
V_i = w_u U_i + w_f F_i + w_e E_i + w_c C_i + w_q Q_i + w_d D_i - w_r R_i
\]

where:

- \(U_i\) = usability and stakeholder adoption value;
- \(F_i\) = feasibility;
- \(E_i\) = ecological benefit;
- \(C_i\) = circularity and material stewardship;
- \(Q_i\) = equity and justice performance;
- \(D_i\) = durability and institutional persistence;
- \(R_i\) = implementation and unintended-consequence risk.

Transition learning can be represented as:

\[
\Delta Q_t = \alpha \Delta A_t - \beta \Delta F_t + \gamma \Delta G_t + \theta \Delta E_t
\]

where adoption, friction, ecological impact reduction, and equity improvement shape whether a prototype is improving across rounds.

These models are not intended to automate sustainability decisions. They help teams make assumptions visible, compare competing priorities, identify fragile conclusions, and decide what should be prototyped, revised, governed, scaled, paused, or retired.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-for-sustainability/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python sustainability_design_engine.py \
  --concepts ../data/raw/sustainability_concepts_raw.csv \
  --weights ../data/raw/sustainability_scenario_weights.csv \
  --transitions ../data/raw/transition_pathways_raw.csv \
  --risk-register ../data/raw/sustainability_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-for-sustainability
sqlite3 outputs/sustainability_design.db < sql/schema.sql
sqlite3 outputs/sustainability_design.db < sql/analytical_queries.sql
```

## Notes

All datasets are synthetic and intended for methodological demonstration. Replace them with documented sustainability, lifecycle, service, stakeholder, implementation, and governance evidence before using this workflow in real decision-support settings.
