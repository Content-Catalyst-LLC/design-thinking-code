# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python public_value_impact_engine.py --interventions ../data/raw/social_impact_interventions_raw.csv --stakeholders ../data/raw/stakeholder_burden_public_value_raw.csv --participation ../data/raw/participation_quality_raw.csv --weights ../data/raw/public_value_scenario_weights.csv --risk-register ../data/raw/social_impact_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript public_value_impact_analysis.R
```

## Julia

```bash
cd julia
julia public_value_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 public_value_engine.cpp -o public_value_engine
./public_value_engine ../data/raw/social_impact_interventions_raw.csv
```

## C

```bash
cd c
cc -O2 public_value_engine.c -o public_value_engine
./public_value_engine ../data/raw/social_impact_interventions_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 public_value_model.f90 -o public_value_model
./public_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/social_impact_interventions_raw.csv
```

## Go

```bash
cd go
go run public_value_engine.go ../data/raw/social_impact_interventions_raw.csv
```

## SQL

```bash
sqlite3 outputs/public_value_impact.db < sql/schema.sql
sqlite3 outputs/public_value_impact.db < sql/analytical_queries.sql
```
