# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python insight_generation_engine.py --input ../data/raw/candidate_insights_raw.csv --weights ../data/raw/insight_scenario_weights.csv --evidence ../data/raw/insight_evidence_sources_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript insight_generation_scenario_analysis.R
```

## Julia

```bash
cd julia
julia insight_portfolio_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 insight_value_engine.cpp -o insight_value_engine
./insight_value_engine ../data/raw/candidate_insights_raw.csv
```

## C

```bash
cd c
cc -O2 insight_value_engine.c -o insight_value_engine
./insight_value_engine ../data/raw/candidate_insights_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 insight_value_model.f90 -o insight_value_model
./insight_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/candidate_insights_raw.csv
```

## Go

```bash
cd go
go run insight_value_engine.go ../data/raw/candidate_insights_raw.csv
```

## SQL

```bash
sqlite3 outputs/insight_generation.db < sql/schema.sql
sqlite3 outputs/insight_generation.db < sql/analytical_queries.sql
```
