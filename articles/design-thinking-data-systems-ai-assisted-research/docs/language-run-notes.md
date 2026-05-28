# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ai_research_evidence_engine.py --signals ../data/raw/research_signals_raw.csv --ai-log ../data/raw/ai_assistance_log_raw.csv --metadata ../data/raw/evidence_metadata_registry_raw.csv --weights ../data/raw/research_scenario_weights.csv --risk-register ../data/raw/research_governance_risk_register_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript ai_research_evidence_analysis.R
```

## Julia

```bash
cd julia
julia research_signal_model.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 research_signal_engine.cpp -o research_signal_engine
./research_signal_engine ../data/raw/research_signals_raw.csv
```

## C

```bash
cd c
cc -O2 research_signal_engine.c -o research_signal_engine
./research_signal_engine ../data/raw/research_signals_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 research_signal_model.f90 -o research_signal_model
./research_signal_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/research_signals_raw.csv
```

## Go

```bash
cd go
go run research_signal_engine.go ../data/raw/research_signals_raw.csv
```

## SQL

```bash
sqlite3 outputs/ai_research_evidence.db < sql/schema.sql
sqlite3 outputs/ai_research_evidence.db < sql/analytical_queries.sql
```
