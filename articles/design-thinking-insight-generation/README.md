# Insight Generation in Design Thinking

This folder contains professional companion code and reproducible research assets for the article **“Insight Generation in Design Thinking.”**

The article frames insight generation as the interpretive core of design thinking: the disciplined movement from observation to pattern, from pattern to meaning, from meaning to opportunity, and from opportunity to testable design direction. This companion repository translates that discussion into reusable analytical workflows for assessing candidate insights, evidence strength, explanatory depth, opportunity value, interpretive risk, bias exposure, stakeholder coverage, and uncertainty in synthesis decisions.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-thinking-insight-generation

## Folder structure

```text
design-thinking-insight-generation/
├── python/
│   ├── insight_generation_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── insight_generation_scenario_analysis.R
├── julia/
│   └── insight_portfolio_model.jl
├── cpp/
│   └── insight_value_engine.cpp
├── fortran/
│   └── insight_value_model.f90
├── c/
│   └── insight_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── insight_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── insight_generation_analysis.ipynb
├── docs/
│   ├── data-dictionary.md
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

This scaffold is designed for design researchers, UX researchers, service designers, public-sector innovation teams, civic technologists, product strategists, organizational researchers, qualitative analysts, and applied research teams that need to evaluate candidate insights before turning them into ideation prompts, prototypes, pilots, or implementation priorities.

The code supports:

- candidate insight scoring;
- scenario analysis under different synthesis priorities;
- evidence strength and pattern-support modeling;
- explanatory-depth and opportunity-value diagnostics;
- interpretive-risk decomposition;
- bias and solution-capture diagnostics;
- stakeholder-coverage and evidence-source review;
- Monte Carlo uncertainty modeling;
- bootstrap stability checks;
- weight sensitivity analysis;
- SQL-backed evidence and insight tables;
- reproducible reporting and output generation;
- documentation of assumptions, limitations, and responsible-use constraints.

## Conceptual model

A candidate insight \(i\) is scored as:

\[
V_i = w_p P_i + w_e E_i + w_o O_i - w_r R_i
\]

where:

- \(P_i\) = pattern support;
- \(E_i\) = explanatory depth;
- \(O_i\) = opportunity value;
- \(R_i\) = interpretive risk;
- \(w_p, w_e, w_o, w_r\) = synthesis-priority weights.

A separate interpretive-risk index may be modeled as:

\[
R_i = \lambda_S S_i + \lambda_B B_i + \lambda_T T_i + \lambda_L L_i
\]

where:

- \(S_i\) = sampling risk;
- \(B_i\) = confirmation-bias risk;
- \(T_i\) = evidence-thinness risk;
- \(L_i\) = solution-capture risk.

These models are not intended to automate interpretation. They are transparent decision-support structures for making synthesis assumptions visible, comparing candidate insights, identifying interpretive risk, and documenting where further research or prototype testing is needed.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-insight-generation/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python insight_generation_engine.py \
  --input ../data/raw/candidate_insights_raw.csv \
  --weights ../data/raw/insight_scenario_weights.csv \
  --evidence ../data/raw/insight_evidence_sources_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/design-thinking-insight-generation
sqlite3 outputs/insight_generation.db < sql/schema.sql
sqlite3 outputs/insight_generation.db < sql/analytical_queries.sql
```

## Notes

All scores in the example dataset are synthetic and intended for methodological demonstration. Replace them with documented design-research evidence before using this workflow in real decision-support settings.
