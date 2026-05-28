# Problem Framing in Design Thinking

This folder contains professional companion code and reproducible research assets for the article **“Problem Framing in Design Thinking.”**

The article frames problem framing as one of the core intellectual disciplines of design thinking: the process of defining, interpreting, testing, and revising the problem before committing to solution pathways. This repository folder translates that discussion into reusable analytical workflows for comparing candidate frames, modeling framing risk, documenting counterframes, stress-testing uncertainty, and preserving evidence trails for design-research decisions.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/problem-framing-design-thinking

## Folder structure

```text
problem-framing-design-thinking/
├── python/
│   ├── problem_framing_decision_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── problem_framing_scenario_analysis.R
├── julia/
│   └── problem_frame_portfolio.jl
├── cpp/
│   └── problem_frame_value_engine.cpp
├── fortran/
│   └── problem_frame_value_model.f90
├── c/
│   └── problem_frame_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── problem_frame_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── problem_framing_analysis.ipynb
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

This scaffold is designed for design researchers, strategy teams, public-sector labs, service designers, systems thinkers, civic technologists, UX researchers, organizational innovation teams, and applied researchers who need to evaluate competing problem definitions before investing heavily in solutions.

The code supports:

- candidate frame scoring;
- frame-risk decomposition;
- counterframe analysis;
- stakeholder/system coverage diagnostics;
- scenario analysis under different strategic priorities;
- Monte Carlo uncertainty modeling;
- weight sensitivity analysis;
- bootstrap stability checks;
- SQL-backed frame evidence structure;
- reproducible reporting and output generation;
- documentation of assumptions, risks, and limitations.

## Conceptual model

A candidate problem frame \(i\) is scored as:

\[
V_i = w_e E_i + w_s S_i + w_o O_i - w_r R_i
\]

where:

- \(E_i\) = explanatory adequacy;
- \(S_i\) = stakeholder or system coverage;
- \(O_i\) = opportunity value for downstream design;
- \(R_i\) = framing risk;
- \(w_e, w_s, w_o, w_r\) = institutional priority weights.

A separate framing-risk index may be modeled as:

\[
R_i = \lambda_N N_i + \lambda_X X_i + \lambda_C C_i + \lambda_P P_i
\]

where:

- \(N_i\) = narrowness risk;
- \(X_i\) = stakeholder exclusion risk;
- \(C_i\) = causality risk;
- \(P_i\) = political distortion risk.

These models are not intended to automate problem definition. They are transparent decision-support structures for making assumptions visible, comparing alternative frames, and identifying where additional research, stakeholder engagement, or prototype testing is needed.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/problem-framing-design-thinking/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python problem_framing_decision_engine.py \
  --input ../data/raw/problem_frames_raw.csv \
  --weights ../data/raw/problem_framing_scenario_weights.csv \
  --counterframes ../data/raw/counterframes_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/problem-framing-design-thinking
sqlite3 outputs/problem_framing.db < sql/schema.sql
sqlite3 outputs/problem_framing.db < sql/analytical_queries.sql
```

## Notes

All scores in the example dataset are synthetic and intended for methodological demonstration. Replace them with documented design-research evidence before using this workflow in real decision-support settings.
