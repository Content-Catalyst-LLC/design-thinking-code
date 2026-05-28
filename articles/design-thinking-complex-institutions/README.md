# Design Thinking for Complex Institutions

This folder contains professional companion code and reproducible research assets for the article **“Design Thinking for Complex Institutions.”**

The article frames institutional design thinking as a systems-aware, governance-conscious, human-centered practice for public agencies, universities, hospitals, courts, school systems, civic infrastructures, research institutions, nonprofits, foundations, and mature organizations. The companion materials support analysis of change readiness, institutional absorption capacity, public value, stakeholder burden, governance strength, decision rights, implementation risk, policy fit, data-system readiness, trust, and portfolio sequencing.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-thinking-complex-institutions

## Folder structure

```text
design-thinking-complex-institutions/
├── python/
│   ├── institutional_design_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── institutional_design_analysis.R
├── julia/
│   └── institutional_readiness_model.jl
├── cpp/
│   └── institutional_readiness_engine.cpp
├── fortran/
│   └── institutional_readiness_model.f90
├── c/
│   └── institutional_readiness_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── institutional_readiness_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── institutional_design_analysis.ipynb
├── docs/
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for design researchers, public-sector innovation teams, service designers, civic technology teams, institutional researchers, organizational change teams, healthcare transformation groups, higher-education transformation teams, nonprofit strategy teams, policy implementation teams, governance analysts, and institutional learning programs.

The code supports:

- institutional design option scoring;
- change-readiness modeling;
- absorption-capacity analysis;
- public-value prioritization;
- burden-reduction modeling;
- policy-fit and governance-strength review;
- data-system readiness review;
- trust and legitimacy review;
- implementation-risk and coordination-complexity scoring;
- stakeholder burden analysis;
- governance risk-register prioritization;
- scenario-weighted portfolio review;
- Monte Carlo uncertainty simulation;
- bootstrap stability analysis;
- random-weight sensitivity analysis;
- SQL-backed institutional design schemas;
- reproducible reports, figures, and audit-friendly outputs.

## Conceptual model

Institutional change readiness:

\[
R_i = w_dD_i + w_aA_i + w_cC_i + w_fF_i + w_pP_i + w_gG_i + w_tT_i - w_bB_i - w_kK_i
\]

Institutional absorption capacity:

\[
A_i = \alpha O_i + \beta S_i + \gamma M_i + \delta L_i + \theta Q_i
\]

Stakeholder burden:

\[
B_g = \lambda T_g + \mu C_g + \nu E_g + \rho D_g + \sigma U_g
\]

where readiness depends on desirability, authority, capability, funding, policy fit, governance, trust, burden, and coordination complexity.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-complex-institutions/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python institutional_design_engine.py \
  --options ../data/raw/institutional_design_options_raw.csv \
  --stakeholders ../data/raw/stakeholder_burden_raw.csv \
  --governance ../data/raw/governance_decision_rights_raw.csv \
  --weights ../data/raw/institutional_scenario_weights.csv \
  --risk-register ../data/raw/institutional_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Notes

All datasets are synthetic and intended for methods demonstration. Replace them with documented institutional evidence, stakeholder research, governance records, burden audits, implementation records, policy analysis, data-system assessments, and evaluation data before using this workflow in real institutional decisions.
