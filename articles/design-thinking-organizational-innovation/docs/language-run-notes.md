# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python organizational_innovation_engine.py --concepts ../data/raw/organizational_innovation_concepts_raw.csv --weights ../data/raw/innovation_scenario_weights.csv --learning ../data/raw/prototype_learning_rounds_raw.csv --friction ../data/raw/organizational_friction_raw.csv --risk-register ../data/raw/innovation_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript organizational_innovation_analysis.R
```

## Julia

```bash
cd julia
julia organizational_learning_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 innovation_value_engine.cpp -o innovation_value_engine
./innovation_value_engine ../data/raw/organizational_innovation_concepts_raw.csv
```

## C

```bash
cd c
cc -O2 innovation_value_engine.c -o innovation_value_engine
./innovation_value_engine ../data/raw/organizational_innovation_concepts_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 innovation_value_model.f90 -o innovation_value_model
./innovation_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/organizational_innovation_concepts_raw.csv
```

## Go

```bash
cd go
go run innovation_value_engine.go ../data/raw/organizational_innovation_concepts_raw.csv
```

## SQL

```bash
sqlite3 outputs/organizational_innovation.db < sql/schema.sql
sqlite3 outputs/organizational_innovation.db < sql/analytical_queries.sql
```
