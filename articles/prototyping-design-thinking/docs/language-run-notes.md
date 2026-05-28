# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python prototype_portfolio_engine.py --portfolio ../data/raw/prototype_portfolio_raw.csv --weights ../data/raw/prototype_scenario_weights.csv --rounds ../data/raw/prototype_test_rounds_raw.csv --risk-register ../data/raw/prototype_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript prototype_scenario_analysis.R
```

## Julia

```bash
cd julia
julia prototype_iteration_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 prototype_value_engine.cpp -o prototype_value_engine
./prototype_value_engine ../data/raw/prototype_portfolio_raw.csv
```

## C

```bash
cd c
cc -O2 prototype_value_engine.c -o prototype_value_engine
./prototype_value_engine ../data/raw/prototype_portfolio_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 prototype_value_model.f90 -o prototype_value_model
./prototype_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/prototype_portfolio_raw.csv
```

## Go

```bash
cd go
go run prototype_value_engine.go ../data/raw/prototype_portfolio_raw.csv
```

## SQL

```bash
sqlite3 outputs/prototype_portfolio.db < sql/schema.sql
sqlite3 outputs/prototype_portfolio.db < sql/analytical_queries.sql
```
