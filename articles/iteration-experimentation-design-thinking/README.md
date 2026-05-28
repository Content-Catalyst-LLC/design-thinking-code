# Iteration and Experimentation in Design Thinking

This folder contains professional companion code and reproducible research assets for the article **“Iteration and Experimentation in Design Thinking.”**

The article frames iteration and experimentation as disciplined methods for learning under uncertainty. Rather than treating design as a linear path from analysis to implementation, the article emphasizes prototype cycles, bounded experiments, feedback interpretation, uncertainty reduction, ethical safeguards, and cumulative revision. This companion repository translates that discussion into reusable analytical workflows for comparing experiment portfolios, modeling learning value, evaluating residual risk, documenting evidence, and preserving reproducible design-research outputs.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/iteration-experimentation-design-thinking

## Folder structure

```text
iteration-experimentation-design-thinking/
├── python/
│   ├── iteration_experimentation_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── iteration_experimentation_scenario_analysis.R
├── julia/
│   └── experiment_portfolio_model.jl
├── cpp/
│   └── experiment_value_engine.cpp
├── fortran/
│   └── experiment_value_model.f90
├── c/
│   └── experiment_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── experiment_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── iteration_experimentation_analysis.ipynb
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

This scaffold is designed for design researchers, service designers, public-sector labs, civic technologists, healthcare improvement teams, UX researchers, product teams, organizational innovation groups, and applied researchers who need to evaluate experiment portfolios before committing to larger implementation.

The code supports:

- experiment portfolio scoring;
- learning-value and reversibility modeling;
- residual-risk decomposition;
- ethical-risk and scaling-risk diagnostics;
- scenario analysis under different learning priorities;
- Monte Carlo uncertainty modeling;
- weight sensitivity analysis;
- bootstrap stability checks;
- SQL-backed experiment evidence structure;
- reproducible reporting and output generation;
- documentation of assumptions, risks, limitations, and responsible-use constraints.

## Conceptual model

A candidate experiment \(i\) is scored as:

\[
V_i = w_l L_i + w_u U_i + w_e E_i - w_r R_i
\]

where:

- \(L_i\) = learning gain;
- \(U_i\) = update flexibility or reversibility;
- \(E_i\) = expected improvement;
- \(R_i\) = residual risk;
- \(w_l, w_u, w_e, w_r\) = institutional priority weights.

A separate risk index may be modeled as:

\[
R_i = \lambda_H H_i + \lambda_O O_i + \lambda_I I_i + \lambda_S S_i
\]

where:

- \(H_i\) = ethical or human-subject risk;
- \(O_i\) = operational risk;
- \(I_i\) = interpretive risk;
- \(S_i\) = scaling risk.

These models are not intended to automate design judgment. They are transparent decision-support structures for making assumptions visible, comparing experiments, and identifying where further research, safeguards, or stakeholder review are needed.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/iteration-experimentation-design-thinking/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python iteration_experimentation_engine.py \
  --input ../data/raw/experiments_raw.csv \
  --weights ../data/raw/experiment_scenario_weights.csv \
  --ethics ../data/raw/experiment_ethics_review_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/iteration-experimentation-design-thinking
sqlite3 outputs/iteration_experimentation.db < sql/schema.sql
sqlite3 outputs/iteration_experimentation.db < sql/analytical_queries.sql
```

## Notes

All scores in the example dataset are synthetic and intended for methodological demonstration. Replace them with documented design-research evidence before using this workflow in real decision-support settings.
