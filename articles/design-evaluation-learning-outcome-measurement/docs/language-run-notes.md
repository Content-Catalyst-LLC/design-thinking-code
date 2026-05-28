# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python evaluation_learning_engine.py --portfolio ../data/raw/evaluation_portfolio_raw.csv --weights ../data/raw/evaluation_scenario_weights.csv --outcomes ../data/raw/outcome_timeseries_raw.csv --learning-agenda ../data/raw/learning_agenda_raw.csv --risk-register ../data/raw/evaluation_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript design_evaluation_learning_analysis.R
```

## Julia

```bash
cd julia
julia evaluation_learning_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 evaluation_value_engine.cpp -o evaluation_value_engine
./evaluation_value_engine ../data/raw/evaluation_portfolio_raw.csv
```

## C

```bash
cd c
cc -O2 evaluation_value_engine.c -o evaluation_value_engine
./evaluation_value_engine ../data/raw/evaluation_portfolio_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 evaluation_value_model.f90 -o evaluation_value_model
./evaluation_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/evaluation_portfolio_raw.csv
```

## Go

```bash
cd go
go run evaluation_value_engine.go ../data/raw/evaluation_portfolio_raw.csv
```

## SQL

```bash
sqlite3 outputs/design_evaluation.db < sql/schema.sql
sqlite3 outputs/design_evaluation.db < sql/analytical_queries.sql
```
