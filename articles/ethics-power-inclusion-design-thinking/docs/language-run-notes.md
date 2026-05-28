# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ethics_power_inclusion_engine.py --stakeholders ../data/raw/stakeholder_groups_raw.csv --decisions ../data/raw/ethical_design_decisions_raw.csv --participation ../data/raw/participation_power_raw.csv --weights ../data/raw/ethics_scenario_weights.csv --risk-register ../data/raw/design_governance_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript ethics_power_inclusion_analysis.R
```

## Julia

```bash
cd julia
julia ethical_risk_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 ethical_risk_engine.cpp -o ethical_risk_engine
./ethical_risk_engine ../data/raw/ethical_design_decisions_raw.csv
```

## C

```bash
cd c
cc -O2 ethical_risk_engine.c -o ethical_risk_engine
./ethical_risk_engine ../data/raw/ethical_design_decisions_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 ethical_risk_model.f90 -o ethical_risk_model
./ethical_risk_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/ethical_design_decisions_raw.csv
```

## Go

```bash
cd go
go run ethical_risk_engine.go ../data/raw/ethical_design_decisions_raw.csv
```

## SQL

```bash
sqlite3 outputs/ethics_power_inclusion.db < sql/schema.sql
sqlite3 outputs/ethics_power_inclusion.db < sql/analytical_queries.sql
```
