# What Is Design Thinking?

This folder contains professional companion code and reproducible research assets for the article **“What Is Design Thinking?”**

The article frames design thinking as a disciplined methodology for human-centered inquiry, problem framing, ideation, prototyping, testing, systems-aware interpretation, and iterative institutional learning. This repository folder translates that conceptual discussion into reusable analytical workflows for comparing design pathways, stress-testing strategic assumptions, modeling uncertainty, documenting research decisions, and preserving reproducible outputs.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/what-is-design-thinking

## Folder structure

```text
what-is-design-thinking/
├── python/
│   ├── design_strategy_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── design_pathway_scenario_analysis.R
├── julia/
│   └── robust_design_portfolio.jl
├── cpp/
│   └── design_value_engine.cpp
├── fortran/
│   └── design_value_model.f90
├── c/
│   └── design_value_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── design_value_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── design_strategy_analysis.ipynb
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

This scaffold is designed for design researchers, innovation teams, service designers, public-sector labs, institutional strategy teams, and applied researchers who need to move beyond informal workshop artifacts toward documented, reproducible, evidence-informed design decision support.

The code supports:

- multi-criteria design pathway scoring;
- scenario analysis under different institutional priorities;
- Monte Carlo uncertainty modeling;
- weight sensitivity analysis;
- bootstrap stability checks;
- SQL-backed design-research data structure;
- reproducible output generation;
- transparent documentation of assumptions and limitations.

## Conceptual model

A candidate design pathway \(i\) is scored as:

\[
V_i = w_h H_i + w_f F_i + w_l L_i - w_r R_i
\]

where:

- \(H_i\) = human-centered relevance;
- \(F_i\) = feasibility;
- \(L_i\) = learning value;
- \(R_i\) = residual risk;
- \(w_h, w_f, w_l, w_r\) = institutional priority weights.

This model is not intended to automate design judgment. It is a transparent decision-support structure for making assumptions explicit, comparing alternatives, and identifying where additional research is needed.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/what-is-design-thinking/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python design_strategy_engine.py \
  --input ../data/raw/design_pathways_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/what-is-design-thinking
sqlite3 outputs/design_thinking.db < sql/schema.sql
sqlite3 outputs/design_thinking.db < sql/analytical_queries.sql
```

## Notes

All scores in the example dataset are synthetic and intended for methodological demonstration. Replace them with documented research findings before using this workflow in real decision-support settings.
