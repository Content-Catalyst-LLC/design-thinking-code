# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python human_centered_decision_engine.py --input ../data/raw/human_centered_options_raw.csv --weights ../data/raw/human_centered_scenario_weights.csv --stakeholders ../data/raw/stakeholder_groups_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript human_centered_scenario_analysis.R
```

## Julia

```bash
cd julia
julia human_centered_portfolio.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 human_centered_value_engine.cpp -o human_centered_value_engine
./human_centered_value_engine ../data/raw/human_centered_options_raw.csv
```

## C

```bash
cd c
cc -O2 human_centered_value_engine.c -o human_centered_value_engine
./human_centered_value_engine ../data/raw/human_centered_options_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 human_centered_value_model.f90 -o human_centered_value_model
./human_centered_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/human_centered_options_raw.csv
```

## Go

```bash
cd go
go run human_centered_value_engine.go ../data/raw/human_centered_options_raw.csv
```

## SQL

```bash
sqlite3 outputs/human_centered_problem_solving.db < sql/schema.sql
sqlite3 outputs/human_centered_problem_solving.db < sql/analytical_queries.sql
```
