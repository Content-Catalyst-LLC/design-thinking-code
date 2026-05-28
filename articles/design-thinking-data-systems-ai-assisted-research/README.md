# Design Thinking, Data Systems, and AI-Assisted Research

This folder contains professional companion code and reproducible research assets for the article **“Design Thinking, Data Systems, and AI-Assisted Research.”**

The article frames AI-assisted design research as a governed evidence system rather than a substitute for human-centered inquiry. The companion materials support practical analysis of evidence confidence, source traceability, metadata quality, AI-assistance risk, bias risk, validation status, missingness, decision readiness, provenance, consent, and responsible research governance.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-thinking-data-systems-ai-assisted-research

## Folder structure

```text
design-thinking-data-systems-ai-assisted-research/
├── python/
│   ├── ai_research_evidence_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── ai_research_evidence_analysis.R
├── julia/
│   └── research_signal_model.jl
├── cpp/
│   └── research_signal_engine.cpp
├── fortran/
│   └── research_signal_model.f90
├── c/
│   └── research_signal_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── research_signal_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── ai_research_evidence_analysis.ipynb
├── docs/
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

## Professional use case

This scaffold is designed for design researchers, UX research operations teams, data systems teams, AI governance teams, service designers, public-sector research teams, civic technology programs, knowledge-architecture teams, product discovery teams, research repository owners, and institutional learning teams.

The code supports:

- research signal scoring;
- evidence confidence scoring;
- bias-risk analysis;
- missingness and representativeness review;
- AI-use risk review;
- metadata quality review;
- provenance and traceability checks;
- source-to-finding-to-decision linkage;
- validation and decision-readiness scoring;
- research governance risk registers;
- scenario-weighted evidence review;
- Monte Carlo uncertainty modeling;
- bootstrap stability analysis;
- random-weight sensitivity analysis;
- SQL-backed research evidence schemas;
- reproducible reports, figures, and audit-friendly outputs.

## Conceptual model

Evidence confidence:

\[
C_i = w_sS_i + w_rR_i + w_tT_i + w_pP_i + w_vV_i
\]

Bias risk:

\[
B_i = \alpha M_i + \beta(1-P_i) + \gamma(1-V_i) + \delta A_i + \theta(1-T_i)
\]

Decision readiness:

\[
D_i = \lambda C_i + \mu R_i + \nu V_i + \rho T_i - \omega B_i
\]

where source strength, relevance, traceability, representativeness, validation, AI assistance, and missingness determine how responsibly evidence can support design decisions.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-data-systems-ai-assisted-research/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ai_research_evidence_engine.py \
  --signals ../data/raw/research_signals_raw.csv \
  --ai-log ../data/raw/ai_assistance_log_raw.csv \
  --metadata ../data/raw/evidence_metadata_registry_raw.csv \
  --weights ../data/raw/research_scenario_weights.csv \
  --risk-register ../data/raw/research_governance_risk_register_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Notes

All datasets are synthetic and intended for methods demonstration. Replace them with documented research evidence, consent records, metadata registries, participant-group coverage, AI-use logs, validation records, and decision traces before using this workflow in real design, public-sector, AI, or institutional research settings.
