# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python implementation_scaling_engine.py --portfolio ../data/raw/implementation_portfolio_raw.csv --weights ../data/raw/implementation_scenario_weights.csv --rollout ../data/raw/rollout_stage_metrics_raw.csv --risk-register ../data/raw/implementation_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript implementation_scaling_analysis.R
```

## Julia

```bash
cd julia
julia scale_degradation_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 implementation_value_engine.cpp -o implementation_value_engine
./implementation_value_engine ../data/raw/implementation_portfolio_raw.csv
```

## C

```bash
cd c
cc -O2 implementation_value_engine.c -o implementation_value_engine
./implementation_value_engine ../data/raw/implementation_portfolio_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 implementation_value_model.f90 -o implementation_value_model
./implementation_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/implementation_portfolio_raw.csv
```

## Go

```bash
cd go
go run implementation_value_engine.go ../data/raw/implementation_portfolio_raw.csv
```

## SQL

```bash
sqlite3 outputs/implementation_scaling.db < sql/schema.sql
sqlite3 outputs/implementation_scaling.db < sql/analytical_queries.sql
```
