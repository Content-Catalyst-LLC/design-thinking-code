# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python co_design_participatory_design_engine.py --activities ../data/raw/codesign_activities_raw.csv --participants ../data/raw/participant_groups_raw.csv --weights ../data/raw/participation_scenario_weights.csv --learning ../data/raw/participatory_prototype_learning_raw.csv --risk-register ../data/raw/participation_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript co_design_participatory_design_analysis.R
```

## Julia

```bash
cd julia
julia participation_influence_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 participation_quality_engine.cpp -o participation_quality_engine
./participation_quality_engine ../data/raw/codesign_activities_raw.csv
```

## C

```bash
cd c
cc -O2 participation_quality_engine.c -o participation_quality_engine
./participation_quality_engine ../data/raw/codesign_activities_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 participation_quality_model.f90 -o participation_quality_model
./participation_quality_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/codesign_activities_raw.csv
```

## Go

```bash
cd go
go run participation_quality_engine.go ../data/raw/codesign_activities_raw.csv
```

## SQL

```bash
sqlite3 outputs/codesign_participatory_design.db < sql/schema.sql
sqlite3 outputs/codesign_participatory_design.db < sql/analytical_queries.sql
```
