# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python systems_design_engine.py --portfolio ../data/raw/system_intervention_portfolio_raw.csv --weights ../data/raw/system_design_scenario_weights.csv --feedback ../data/raw/feedback_dynamics_raw.csv --risk-register ../data/raw/system_intervention_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript systems_design_analysis.R
```

## Julia

```bash
cd julia
julia systems_feedback_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 system_design_value_engine.cpp -o system_design_value_engine
./system_design_value_engine ../data/raw/system_intervention_portfolio_raw.csv
```

## C

```bash
cd c
cc -O2 system_design_value_engine.c -o system_design_value_engine
./system_design_value_engine ../data/raw/system_intervention_portfolio_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 system_design_value_model.f90 -o system_design_value_model
./system_design_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/system_intervention_portfolio_raw.csv
```

## Go

```bash
cd go
go run system_design_value_engine.go ../data/raw/system_intervention_portfolio_raw.csv
```

## SQL

```bash
sqlite3 outputs/system_design.db < sql/schema.sql
sqlite3 outputs/system_design.db < sql/analytical_queries.sql
```
