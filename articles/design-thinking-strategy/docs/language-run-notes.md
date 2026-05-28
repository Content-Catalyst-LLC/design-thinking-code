# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python strategy_design_engine.py --options ../data/raw/strategic_options_raw.csv --assumptions ../data/raw/strategic_assumptions_raw.csv --weights ../data/raw/strategy_scenario_weights.csv --risk-register ../data/raw/strategy_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript strategy_design_analysis.R
```

## Julia

```bash
cd julia
julia strategy_portfolio_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 strategy_option_engine.cpp -o strategy_option_engine
./strategy_option_engine ../data/raw/strategic_options_raw.csv
```

## C

```bash
cd c
cc -O2 strategy_option_engine.c -o strategy_option_engine
./strategy_option_engine ../data/raw/strategic_options_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 strategy_option_model.f90 -o strategy_option_model
./strategy_option_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/strategic_options_raw.csv
```

## Go

```bash
cd go
go run strategy_option_engine.go ../data/raw/strategic_options_raw.csv
```

## SQL

```bash
sqlite3 outputs/strategy_design.db < sql/schema.sql
sqlite3 outputs/strategy_design.db < sql/analytical_queries.sql
```
