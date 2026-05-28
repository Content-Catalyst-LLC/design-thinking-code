# Ethics, Power, and Inclusion in Design Thinking

This folder contains professional companion code and reproducible research assets for the article **“Ethics, Power, and Inclusion in Design Thinking.”**

The article frames ethics, power, and inclusion as core design-thinking concerns rather than late-stage checklists. The companion materials support practical analysis of access, voice, safety, compensation, representation, accountability, burden, harm, detectability, repair, governance, participation power, accessibility, public value, and uncertainty.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/ethics-power-inclusion-design-thinking

## Folder structure

```text
ethics-power-inclusion-design-thinking/
├── python/
│   ├── ethics_power_inclusion_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── ethics_power_inclusion_analysis.R
├── julia/
│   └── ethical_risk_model.jl
├── cpp/
│   └── ethical_risk_engine.cpp
├── fortran/
│   └── ethical_risk_model.f90
├── c/
│   └── ethical_risk_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── ethical_risk_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── ethics_power_inclusion_analysis.ipynb
├── docs/
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for design researchers, ethical design reviewers, service designers, public policy teams, civic technology teams, accessibility teams, AI governance groups, organizational designers, institutional researchers, participatory design teams, and community-accountable design programs.

The code supports:

- inclusion score analysis;
- stakeholder burden analysis;
- power-gap scoring;
- participation influence review;
- ethical risk scoring;
- accessibility and assisted-access review;
- harm detectability and accountability modeling;
- design-governance risk review;
- repair pathway scoring;
- scenario-weighted ethics review;
- Monte Carlo uncertainty analysis;
- bootstrap rank stability;
- random-weight sensitivity analysis;
- SQL-backed ethics and inclusion schemas;
- reproducible reports, figures, and decision-support artifacts.

## Conceptual model

Inclusion for stakeholder group \(g\):

\[
I_g = w_aA_g + w_vV_g + w_sS_g + w_cC_g + w_rR_g + w_kK_g
\]

Burden for stakeholder group \(g\):

\[
B_g = \alpha T_g + \beta C_g + \gamma E_g + \delta D_g + \lambda U_g + \theta O_g
\]

Ethical risk for a design decision:

\[
R = H \times P \times X \times (1-D) \times (1-A)
\]

where harm severity, probability, and exposure increase risk, while detectability and accountability reduce unmanaged risk.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/ethics-power-inclusion-design-thinking/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ethics_power_inclusion_engine.py \
  --stakeholders ../data/raw/stakeholder_groups_raw.csv \
  --decisions ../data/raw/ethical_design_decisions_raw.csv \
  --participation ../data/raw/participation_power_raw.csv \
  --weights ../data/raw/ethics_scenario_weights.csv \
  --risk-register ../data/raw/design_governance_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Notes

All datasets are synthetic and intended for methods demonstration. Replace them with documented stakeholder research, accessibility evidence, participatory review, community governance records, ethical review data, service burden evidence, and post-launch harm monitoring before using this workflow in real decisions.
