#!/usr/bin/env julia

# Strategy portfolio model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "strategic_options_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct StrategicOption
    name::String
    desirability::Float64
    feasibility::Float64
    viability::Float64
    alignment::Float64
    ethics::Float64
    learning::Float64
    effort::Float64
    risk::Float64
    capability_gap::Float64
    evidence::Float64
    time_to_learn::Float64
    public_value::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_options(path::String)
    lines = readlines(path)
    items = StrategicOption[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 15
            error("Malformed strategic option row: $(line)")
        end

        push!(
            items,
            StrategicOption(
                strip(fields[1]),
                parse_float(fields[4]),
                parse_float(fields[5]),
                parse_float(fields[6]),
                parse_float(fields[7]),
                parse_float(fields[8]),
                parse_float(fields[9]),
                parse_float(fields[10]),
                parse_float(fields[11]),
                parse_float(fields[12]),
                parse_float(fields[13]),
                parse_float(fields[14]),
                parse_float(fields[15])
            )
        )
    end

    return items
end

function strategic_score(x::StrategicOption)
    return 0.17 * x.desirability +
           0.13 * x.feasibility +
           0.13 * x.viability +
           0.16 * x.alignment +
           0.11 * x.ethics +
           0.10 * x.learning +
           0.08 * x.public_value +
           0.05 * x.evidence * 10.0 -
           0.03 * x.risk -
           0.02 * x.effort -
           0.01 * x.capability_gap -
           0.01 * x.time_to_learn
end

function portfolio_value(x::StrategicOption)
    s = strategic_score(x)
    return s + 0.30 * x.learning + 0.20 * x.public_value + 0.15 * x.evidence * 10.0 -
           0.22 * x.risk - 0.14 * x.effort - 0.10 * x.capability_gap
end

options = load_options(input_path)
scored = [(x.name, strategic_score(x), portfolio_value(x), x.learning, x.risk) for x in options]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_strategy_option_scores.csv"), "w") do io
    println(io, "rank,option,strategic_score,portfolio_value,learning_value,strategic_risk")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4], row[5])
    end
end

println("Julia strategy portfolio model complete.")
println("Outputs written to: $(output_dir)")
