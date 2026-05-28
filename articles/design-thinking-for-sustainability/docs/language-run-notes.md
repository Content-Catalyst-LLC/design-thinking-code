# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python sustainability_design_engine.py --concepts ../data/raw/sustainability_concepts_raw.csv --weights ../data/raw/sustainability_scenario_weights.csv --transitions ../data/raw/transition_pathways_raw.csv --risk-register ../data/raw/sustainability_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript sustainability_design_analysis.R
```

## Julia

```bash
cd julia
julia sustainability_transition_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 sustainability_value_engine.cpp -o sustainability_value_engine
./sustainability_value_engine ../data/raw/sustainability_concepts_raw.csv
```

## C

```bash
cd c
cc -O2 sustainability_value_engine.c -o sustainability_value_engine
./sustainability_value_engine ../data/raw/sustainability_concepts_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 sustainability_value_model.f90 -o sustainability_value_model
./sustainability_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/sustainability_concepts_raw.csv
```

## Go

```bash
cd go
go run sustainability_value_engine.go ../data/raw/sustainability_concepts_raw.csv
```

## SQL

```bash
sqlite3 outputs/sustainability_design.db < sql/schema.sql
sqlite3 outputs/sustainability_design.db < sql/analytical_queries.sql
```
