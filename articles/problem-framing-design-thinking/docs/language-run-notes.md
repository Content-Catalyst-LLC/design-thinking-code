# Language Run Notes

## Python

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python problem_framing_decision_engine.py --input ../data/raw/problem_frames_raw.csv --weights ../data/raw/problem_framing_scenario_weights.csv --counterframes ../data/raw/counterframes_raw.csv --output-dir ../outputs
```

## R

```bash
cd r
Rscript problem_framing_scenario_analysis.R
```

## Julia

```bash
cd julia
julia problem_frame_portfolio.jl
```

## C++

```bash
cd cpp
g++ -std=c++17 -O2 problem_frame_value_engine.cpp -o problem_frame_value_engine
./problem_frame_value_engine ../data/raw/problem_frames_raw.csv
```

## C

```bash
cd c
cc -O2 problem_frame_value_engine.c -o problem_frame_value_engine
./problem_frame_value_engine ../data/raw/problem_frames_raw.csv
```

## Fortran

```bash
cd fortran
gfortran -O2 problem_frame_value_model.f90 -o problem_frame_value_model
./problem_frame_value_model
```

## Rust

```bash
cd rust
cargo run -- ../data/raw/problem_frames_raw.csv
```

## Go

```bash
cd go
go run problem_frame_value_engine.go ../data/raw/problem_frames_raw.csv
```

## SQL

```bash
sqlite3 outputs/problem_framing.db < sql/schema.sql
sqlite3 outputs/problem_framing.db < sql/analytical_queries.sql
```
