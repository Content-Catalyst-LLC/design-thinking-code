# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python iteration_experimentation_engine.py --input ../data/raw/experiments_raw.csv --weights ../data/raw/experiment_scenario_weights.csv --ethics ../data/raw/experiment_ethics_review_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript iteration_experimentation_scenario_analysis.R
```

## Julia

```bash
cd julia
julia experiment_portfolio_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 experiment_value_engine.cpp -o experiment_value_engine
./experiment_value_engine ../data/raw/experiments_raw.csv
```

## C

```bash
cd c
cc -O2 experiment_value_engine.c -o experiment_value_engine
./experiment_value_engine ../data/raw/experiments_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 experiment_value_model.f90 -o experiment_value_model
./experiment_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/experiments_raw.csv
```

## Go

```bash
cd go
go run experiment_value_engine.go ../data/raw/experiments_raw.csv
```

## SQL

```bash
sqlite3 outputs/iteration_experimentation.db < sql/schema.sql
sqlite3 outputs/iteration_experimentation.db < sql/analytical_queries.sql
```
