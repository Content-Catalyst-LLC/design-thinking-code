# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python institutional_design_engine.py --options ../data/raw/institutional_design_options_raw.csv --stakeholders ../data/raw/stakeholder_burden_raw.csv --governance ../data/raw/governance_decision_rights_raw.csv --weights ../data/raw/institutional_scenario_weights.csv --risk-register ../data/raw/institutional_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript institutional_design_analysis.R
```

## Julia

```bash
cd julia
julia institutional_readiness_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 institutional_readiness_engine.cpp -o institutional_readiness_engine
./institutional_readiness_engine ../data/raw/institutional_design_options_raw.csv
```

## C

```bash
cd c
cc -O2 institutional_readiness_engine.c -o institutional_readiness_engine
./institutional_readiness_engine ../data/raw/institutional_design_options_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 institutional_readiness_model.f90 -o institutional_readiness_model
./institutional_readiness_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/institutional_design_options_raw.csv
```

## Go

```bash
cd go
go run institutional_readiness_engine.go ../data/raw/institutional_design_options_raw.csv
```

## SQL

```bash
sqlite3 outputs/institutional_design.db < sql/schema.sql
sqlite3 outputs/institutional_design.db < sql/analytical_queries.sql
```
