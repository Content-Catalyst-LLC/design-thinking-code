# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ideation_portfolio_engine.py --input ../data/raw/idea_portfolio_raw.csv --weights ../data/raw/ideation_scenario_weights.csv --clusters ../data/raw/idea_cluster_map_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript ideation_scenario_analysis.R
```

## Julia

```bash
cd julia
julia ideation_portfolio_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 idea_value_engine.cpp -o idea_value_engine
./idea_value_engine ../data/raw/idea_portfolio_raw.csv
```

## C

```bash
cd c
cc -O2 idea_value_engine.c -o idea_value_engine
./idea_value_engine ../data/raw/idea_portfolio_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 idea_value_model.f90 -o idea_value_model
./idea_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/idea_portfolio_raw.csv
```

## Go

```bash
cd go
go run idea_value_engine.go ../data/raw/idea_portfolio_raw.csv
```

## SQL

```bash
sqlite3 outputs/ideation_portfolio.db < sql/schema.sql
sqlite3 outputs/ideation_portfolio.db < sql/analytical_queries.sql
```
