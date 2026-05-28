# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python public_policy_design_engine.py --pilots ../data/raw/public_policy_pilots_raw.csv --weights ../data/raw/public_policy_scenario_weights.csv --learning ../data/raw/policy_learning_pathways_raw.csv --burdens ../data/raw/administrative_burden_raw.csv --risk-register ../data/raw/public_policy_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript public_policy_design_analysis.R
```

## Julia

```bash
cd julia
julia policy_learning_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 policy_value_engine.cpp -o policy_value_engine
./policy_value_engine ../data/raw/public_policy_pilots_raw.csv
```

## C

```bash
cd c
cc -O2 policy_value_engine.c -o policy_value_engine
./policy_value_engine ../data/raw/public_policy_pilots_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 policy_value_model.f90 -o policy_value_model
./policy_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/public_policy_pilots_raw.csv
```

## Go

```bash
cd go
go run policy_value_engine.go ../data/raw/public_policy_pilots_raw.csv
```

## SQL

```bash
sqlite3 outputs/public_policy_design.db < sql/schema.sql
sqlite3 outputs/public_policy_design.db < sql/analytical_queries.sql
```
