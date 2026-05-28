# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python design_strategy_engine.py --input ../data/raw/design_pathways_raw.csv --weights ../data/raw/scenario_weights.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript design_pathway_scenario_analysis.R
```

## Julia

```bash
cd julia
julia robust_design_portfolio.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 design_value_engine.cpp -o design_value_engine
./design_value_engine ../data/raw/design_pathways_raw.csv
```

## C

```bash
cd c
cc -O2 design_value_engine.c -o design_value_engine
./design_value_engine ../data/raw/design_pathways_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 design_value_model.f90 -o design_value_model
./design_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/design_pathways_raw.csv
```

## Go

```bash
cd go
go run design_value_engine.go ../data/raw/design_pathways_raw.csv
```

## SQL

```bash
sqlite3 outputs/design_thinking.db < sql/schema.sql
sqlite3 outputs/design_thinking.db < sql/analytical_queries.sql
```
