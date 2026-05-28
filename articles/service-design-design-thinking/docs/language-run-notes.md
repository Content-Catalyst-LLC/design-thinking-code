# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python service_design_engine.py --stages ../data/raw/service_journey_stages_raw.csv --groups ../data/raw/service_user_groups_raw.csv --blueprint ../data/raw/service_blueprint_dependencies_raw.csv --weights ../data/raw/service_scenario_weights.csv --risk-register ../data/raw/service_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript service_design_analysis.R
```

## Julia

```bash
cd julia
julia service_reliability_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 service_quality_engine.cpp -o service_quality_engine
./service_quality_engine ../data/raw/service_journey_stages_raw.csv
```

## C

```bash
cd c
cc -O2 service_quality_engine.c -o service_quality_engine
./service_quality_engine ../data/raw/service_journey_stages_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 service_quality_model.f90 -o service_quality_model
./service_quality_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/service_journey_stages_raw.csv
```

## Go

```bash
cd go
go run service_quality_engine.go ../data/raw/service_journey_stages_raw.csv
```

## SQL

```bash
sqlite3 outputs/service_design.db < sql/schema.sql
sqlite3 outputs/service_design.db < sql/analytical_queries.sql
```
