# Design Thinking for Social Impact and Public Value

This folder contains professional companion code and reproducible research assets for the article **“Design Thinking for Social Impact and Public Value.”**

The article frames social-impact design as a public-value practice rather than a generic innovation exercise. The companion materials support analysis of access, equity, dignity, legitimacy, accountability, outcomes, sustainability, learning capacity, burden reduction, governance strength, participation quality, implementation risk, stewardship need, and portfolio uncertainty.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-thinking-social-impact-public-value

## Folder structure

```text
design-thinking-social-impact-public-value/
├── python/
│   ├── public_value_impact_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── public_value_impact_analysis.R
├── julia/
│   └── public_value_model.jl
├── cpp/
│   └── public_value_engine.cpp
├── fortran/
│   └── public_value_model.f90
├── c/
│   └── public_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── public_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── public_value_impact_analysis.ipynb
├── docs/
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for social impact teams, public-sector innovation teams, civic technology groups, nonprofits, foundations, community partnerships, participatory design teams, evaluation teams, policy labs, sustainability initiatives, public service teams, humanitarian organizations, and institutional learning programs.

The code supports:

- public-value scoring;
- social-impact portfolio prioritization;
- burden-reduction analysis;
- equity and access review;
- participation-quality assessment;
- governance and stewardship review;
- implementation-risk analysis;
- community-defined value review;
- evaluation readiness;
- intervention sequencing;
- stakeholder burden analysis;
- scenario-weighted portfolio review;
- Monte Carlo uncertainty simulation;
- bootstrap stability analysis;
- random-weight sensitivity analysis;
- SQL-backed public-value schemas;
- reproducible reports, figures, and audit-friendly outputs.

## Conceptual model

Public value:

\[
PV_i = w_aA_i + w_eE_i + w_dD_i + w_lL_i + w_cC_i + w_oO_i + w_sS_i + w_rR_i
\]

Impact readiness:

\[
IR_i = \alpha PV_i + \beta F_i + \gamma G_i + \delta T_i - \lambda R_i - \mu B_i
\]

Burden reduction:

\[
BR_g = B_{g,0} - B_{g,1}
\]

where public value depends on access, equity, dignity, legitimacy, accountability, outcomes, sustainability, and learning capacity, while readiness also depends on feasibility, governance, trust, risk, and burden.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-social-impact-public-value/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python public_value_impact_engine.py \
  --interventions ../data/raw/social_impact_interventions_raw.csv \
  --stakeholders ../data/raw/stakeholder_burden_public_value_raw.csv \
  --participation ../data/raw/participation_quality_raw.csv \
  --weights ../data/raw/public_value_scenario_weights.csv \
  --risk-register ../data/raw/social_impact_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Notes

All datasets are synthetic and intended for methods demonstration. Replace them with documented community research, public-value criteria, burden audits, governance records, consent records, evaluation data, implementation evidence, and participation records before using this workflow in real social-impact decisions.
