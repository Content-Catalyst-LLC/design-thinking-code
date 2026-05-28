# Co-Design and Participatory Design

This folder contains professional companion code and reproducible research assets for the article **“Co-Design and Participatory Design.”**

The article frames co-design and participatory design as more than stakeholder engagement or workshop practice. It treats participation as an evidence, legitimacy, influence, ethics, accessibility, governance, and implementation problem. The companion repository turns that argument into reusable workflows for participation-quality scoring, representation-gap analysis, participant-influence modeling, stakeholder-coverage diagnostics, process-legitimacy review, ethical-risk assessment, participatory-prototype learning, and uncertainty modeling.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/co-design-participatory-design

## Folder structure

```text
co-design-participatory-design/
├── python/
│   ├── co_design_participatory_design_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── co_design_participatory_design_analysis.R
├── julia/
│   └── participation_influence_model.jl
├── cpp/
│   └── participation_quality_engine.cpp
├── fortran/
│   └── participation_quality_model.f90
├── c/
│   └── participation_quality_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── participation_quality_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── co_design_participatory_design_analysis.ipynb
├── docs/
│   ├── data-dictionary.md
│   ├── ethical-participation-protocol.md
│   ├── facilitation-and-accessibility-protocol.md
│   ├── method-note.md
│   ├── model-card.md
│   ├── participation-contract-template.md
│   ├── participatory-synthesis-protocol.md
│   ├── reproducibility.md
│   └── validation-protocol.md
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for co-design teams, participatory design researchers, public-sector design labs, civic-technology teams, service designers, community-engaged researchers, healthcare improvement teams, education researchers, organizational design teams, design justice practitioners, public policy teams, AI governance teams, and institutional researchers that need to evaluate whether participation is meaningful, representative, accessible, influential, ethical, and connected to implementation.

The code supports:

- participatory design activity scoring;
- representation-gap and influence-gap diagnostics;
- affectedness-weighted stakeholder coverage analysis;
- accessibility, trust, and compensation review;
- design-stage influence modeling across framing, synthesis, concept generation, testing, implementation, and governance;
- co-design activity portfolio comparison;
- ethical-risk and tokenism-risk analysis;
- participatory-prototype learning analysis;
- scenario-weighted participation-quality comparison;
- Monte Carlo uncertainty modeling;
- bootstrap stability analysis;
- random-weight sensitivity analysis;
- risk-register prioritization;
- SQL-backed participation-evidence structures;
- reproducible reports, figures, and decision-support artifacts;
- documentation of participation rights, recruitment limits, facilitation conditions, access supports, ethical risks, synthesis review, decision influence, and feedback obligations.

## Conceptual model

A participatory design process can be evaluated as:

\[
Q_i = w_rR_i + w_aA_i + w_pP_i + w_tT_i + w_eE_i + w_mM_i + w_dD_i - w_xX_i
\]

where:

- \(R_i\) = representation quality;
- \(A_i\) = accessibility and participation support;
- \(P_i\) = participant influence;
- \(T_i\) = trust and safety quality;
- \(E_i\) = evidence quality;
- \(M_i\) = implementation accountability;
- \(D_i\) = decision impact;
- \(X_i\) = ethical, tokenism, or extraction risk.

An affectedness-weighted participation gap can be represented as:

\[
G = \sum_{i=1}^{n} A_i(1 - C_i)
\]

where \(A_i\) is affectedness and \(C_i\) is coverage or meaningful representation. This makes clear why participation cannot be evaluated by attendance alone.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/co-design-participatory-design/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python co_design_participatory_design_engine.py \
  --activities ../data/raw/codesign_activities_raw.csv \
  --participants ../data/raw/participant_groups_raw.csv \
  --weights ../data/raw/participation_scenario_weights.csv \
  --learning ../data/raw/participatory_prototype_learning_raw.csv \
  --risk-register ../data/raw/participation_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Notes

All datasets are synthetic and intended for methodological demonstration. Replace them with documented stakeholder research, participation logs, recruitment notes, facilitation evidence, accessibility records, synthesis decisions, prototype-learning data, and governance commitments before using this workflow in real participatory design settings.
