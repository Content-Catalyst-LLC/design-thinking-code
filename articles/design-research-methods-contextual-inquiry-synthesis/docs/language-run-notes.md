# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contextual_inquiry_synthesis_engine.py --evidence ../data/raw/contextual_inquiry_evidence_units_raw.csv --weights ../data/raw/synthesis_scenario_weights.csv --coder-map ../data/raw/coder_theme_assignments_raw.csv --sampling-frame ../data/raw/stakeholder_sampling_frame_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript contextual_inquiry_theme_analysis.R
```

## Julia

```bash
cd julia
julia contextual_inquiry_saturation_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 theme_confidence_engine.cpp -o theme_confidence_engine
./theme_confidence_engine ../data/raw/contextual_inquiry_evidence_units_raw.csv
```

## C

```bash
cd c
cc -O2 theme_confidence_engine.c -o theme_confidence_engine
./theme_confidence_engine ../data/raw/contextual_inquiry_evidence_units_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 theme_confidence_model.f90 -o theme_confidence_model
./theme_confidence_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/contextual_inquiry_evidence_units_raw.csv
```

## Go

```bash
cd go
go run theme_confidence_engine.go ../data/raw/contextual_inquiry_evidence_units_raw.csv
```

## SQL

```bash
sqlite3 outputs/contextual_inquiry_synthesis.db < sql/schema.sql
sqlite3 outputs/contextual_inquiry_synthesis.db < sql/analytical_queries.sql
```
