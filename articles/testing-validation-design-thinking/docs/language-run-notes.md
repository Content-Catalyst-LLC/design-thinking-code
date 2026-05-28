# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python testing_validation_engine.py --concepts ../data/raw/validation_concepts_raw.csv --weights ../data/raw/validation_scenario_weights.csv --rounds ../data/raw/testing_rounds_raw.csv --thresholds ../data/raw/decision_thresholds_raw.csv --risk-register ../data/raw/validation_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript testing_validation_scenario_analysis.R
```

## Julia

```bash
cd julia
julia validation_uncertainty_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 validation_value_engine.cpp -o validation_value_engine
./validation_value_engine ../data/raw/validation_concepts_raw.csv
```

## C

```bash
cd c
cc -O2 validation_value_engine.c -o validation_value_engine
./validation_value_engine ../data/raw/validation_concepts_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 validation_value_model.f90 -o validation_value_model
./validation_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/validation_concepts_raw.csv
```

## Go

```bash
cd go
go run validation_value_engine.go ../data/raw/validation_concepts_raw.csv
```

## SQL

```bash
sqlite3 outputs/testing_validation.db < sql/schema.sql
sqlite3 outputs/testing_validation.db < sql/analytical_queries.sql
```
