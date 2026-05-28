# Service Design in Design Thinking

This folder contains professional companion code and reproducible research assets for the article **“Service Design in Design Thinking.”**

The article frames service design as the bridge between human-centered research and operational delivery. The companion repository turns that argument into reusable workflows for service journey reliability, service blueprint diagnostics, burden analysis, equity gaps, recovery quality, frontstage/backstage dependency mapping, operational friction, staff workload, accessibility, trust, and uncertainty modeling.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/service-design-design-thinking

## Folder structure

```text
service-design-design-thinking/
├── python/
│   ├── service_design_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── service_design_analysis.R
├── julia/
│   └── service_reliability_model.jl
├── cpp/
│   └── service_quality_engine.cpp
├── fortran/
│   └── service_quality_model.f90
├── c/
│   └── service_quality_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── service_quality_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── service_design_analysis.ipynb
├── docs/
│   ├── accessibility-and-burden-protocol.md
│   ├── data-dictionary.md
│   ├── method-note.md
│   ├── model-card.md
│   ├── recovery-and-trust-protocol.md
│   ├── service-blueprint-protocol.md
│   ├── service-governance-protocol.md
│   ├── reproducibility.md
│   └── validation-protocol.md
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for service designers, design strategists, public-service teams, civic-technology teams, customer experience teams, operations leaders, product-service teams, healthcare improvement teams, public policy teams, organizational innovation groups, accessibility teams, AI service-governance teams, and institutional researchers that need to evaluate service journeys as full delivery systems rather than isolated touchpoints.

The code supports:

- service journey reliability modeling;
- service-stage quality and redesign priority scoring;
- frontstage/backstage blueprint dependency mapping;
- user burden and staff workload analysis;
- service recovery and procedural dignity review;
- accessibility and equity-gap analysis;
- omnichannel service-friction diagnostics;
- AI-assisted service risk review;
- scenario-weighted service-quality comparison;
- Monte Carlo uncertainty modeling;
- bootstrap stability analysis;
- random-weight sensitivity analysis;
- risk-register prioritization;
- SQL-backed service-stage and blueprint structures;
- reproducible reports, figures, and decision-support artifacts;
- documentation of service definitions, journey stages, user groups, evidence limits, accessibility assumptions, operational dependencies, recovery pathways, and governance commitments.

## Conceptual model

A service stage \(i\) can be evaluated as:

\[
Q_i = w_pP_i + w_cC_i + w_tT_i + w_aA_i + w_rR_i - w_bB_i - w_sS_i
\]

where:

- \(P_i\) = completion probability;
- \(C_i\) = clarity and legibility;
- \(T_i\) = trust quality;
- \(A_i\) = accessibility;
- \(R_i\) = recovery quality;
- \(B_i\) = user burden;
- \(S_i\) = staff load.

End-to-end reliability is:

\[
R = \prod_{i=1}^{n} p_i
\]

This makes clear that weak stages can undermine the whole service even when individual touchpoints appear acceptable.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/service-design-design-thinking/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python service_design_engine.py \
  --stages ../data/raw/service_journey_stages_raw.csv \
  --groups ../data/raw/service_user_groups_raw.csv \
  --blueprint ../data/raw/service_blueprint_dependencies_raw.csv \
  --weights ../data/raw/service_scenario_weights.csv \
  --risk-register ../data/raw/service_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Notes

All datasets are synthetic and intended for methodological demonstration. Replace them with documented service research, operational data, accessibility findings, support logs, staff interviews, journey maps, service blueprints, and governance commitments before using this workflow in real service decision-support settings.
