# Design Research Methods: Contextual Inquiry and Synthesis

This folder contains professional companion code and reproducible research assets for the article **“Design Research Methods: Contextual Inquiry and Synthesis.”**

The article frames contextual inquiry as the situated research practice that reveals how people actually work, decide, improvise, coordinate, repair, and make sense of systems in real environments. It frames synthesis as the disciplined interpretive process that turns field notes, observations, interviews, artifacts, workflows, contradictions, and hidden labor into traceable design knowledge.

## Repository URL

https://github.com/Content-Catalyst-LLC/design-thinking-code/tree/main/articles/design-research-methods-contextual-inquiry-synthesis

## Folder structure

```text
design-research-methods-contextual-inquiry-synthesis/
├── python/
│   ├── contextual_inquiry_synthesis_engine.py
│   ├── requirements.txt
│   └── tests/
├── r/
│   └── contextual_inquiry_theme_analysis.R
├── julia/
│   └── contextual_inquiry_saturation_model.jl
├── cpp/
│   └── theme_confidence_engine.cpp
├── fortran/
│   └── theme_confidence_model.f90
├── c/
│   └── theme_confidence_engine.c
├── rust/
│   ├── Cargo.toml
│   └── src/main.rs
├── go/
│   └── theme_confidence_engine.go
├── sql/
│   ├── schema.sql
│   └── analytical_queries.sql
├── notebooks/
│   └── contextual_inquiry_synthesis_analysis.ipynb
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

This scaffold is designed for design researchers, UX researchers, service designers, qualitative researchers, civic technologists, public-sector innovation teams, healthcare improvement teams, education researchers, organizational researchers, and applied social research groups that need to make contextual inquiry and synthesis traceable, auditable, and decision-relevant.

The code supports:

- contextual inquiry evidence-unit tracking;
- theme confidence scoring;
- stakeholder coverage diagnostics;
- method triangulation summaries;
- evidence strength and interpretive-risk modeling;
- theme co-occurrence networks;
- saturation and marginal theme-discovery analysis;
- inter-coder agreement support;
- validation-priority diagnostics;
- Monte Carlo uncertainty modeling;
- bootstrap rank stability checks;
- SQL-backed evidence and coding schemas;
- reproducible reports and research artifacts;
- documentation of assumptions, ethics, limitations, and responsible-use constraints.

## Conceptual model

A synthesized theme \(i\) can be scored as:

\[
C_i = w_e E_i + w_s S_i + w_m M_i - w_r R_i
\]

where:

- \(C_i\) = synthesis confidence;
- \(E_i\) = evidence support;
- \(S_i\) = stakeholder coverage;
- \(M_i\) = method triangulation;
- \(R_i\) = interpretive risk;
- \(w_e, w_s, w_m, w_r\) = synthesis-priority weights.

A validation priority score may be modeled as:

\[
P_i = \alpha R_i + \beta (1 - E_i) + \gamma (1 - S_i) + \delta (1 - M_i)
\]

where a higher value indicates a theme that should be reviewed or validated before it drives major design decisions.

These models are not intended to automate qualitative interpretation. They are transparent decision-support structures for documenting research synthesis, identifying missing evidence, and improving interpretive discipline.

## Quick start: Python

```bash
cd ~/Downloads/design-thinking-code/articles/design-research-methods-contextual-inquiry-synthesis/python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contextual_inquiry_synthesis_engine.py \
  --evidence ../data/raw/contextual_inquiry_evidence_units_raw.csv \
  --weights ../data/raw/synthesis_scenario_weights.csv \
  --coder-map ../data/raw/coder_theme_assignments_raw.csv \
  --output-dir ../outputs \
  --simulations 10000
```

## Quick start: SQL

```bash
cd ~/Downloads/design-thinking-code/articles/design-research-methods-contextual-inquiry-synthesis
sqlite3 outputs/contextual_inquiry_synthesis.db < sql/schema.sql
sqlite3 outputs/contextual_inquiry_synthesis.db < sql/analytical_queries.sql
```

## Notes

All datasets are synthetic and intended for methodological demonstration. Replace them with documented contextual inquiry evidence before using this workflow in real design-research settings.
