#!/usr/bin/env julia

# Prototype iteration and portfolio model in Julia.
# Uses only Julia standard-library functionality.

using Printf
using Random

article_dir = normpath(joinpath(@__DIR__, ".."))
portfolio_path = joinpath(article_dir, "data", "raw", "prototype_portfolio_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Prototype
    name::String
    learning_gain::Float64
    feasibility_signal::Float64
    user_response::Float64
    equity_value::Float64
    implementation_relevance::Float64
    ethical_risk::Float64
    operational_risk::Float64
    technical_risk::Float64
    scaling_risk::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_portfolio(path::String)
    lines = readlines(path)
    prototypes = Prototype[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 12
            error("Malformed row: $(line)")
        end

        push!(
            prototypes,
            Prototype(
                strip(fields[1]),
                parse_float(fields[4]),
                parse_float(fields[5]),
                parse_float(fields[6]),
                parse_float(fields[7]),
                parse_float(fields[8]),
                parse_float(fields[9]),
                parse_float(fields[10]),
                parse_float(fields[11]),
                parse_float(fields[12])
            )
        )
    end

    return prototypes
end

function composite_risk(p::Prototype)
    return 0.30 * p.ethical_risk +
           0.30 * p.operational_risk +
           0.20 * p.technical_risk +
           0.20 * p.scaling_risk
end

function prototype_value(p::Prototype)
    return 0.25 * p.learning_gain +
           0.18 * p.feasibility_signal +
           0.20 * p.user_response +
           0.15 * p.equity_value +
           0.12 * p.implementation_relevance -
           0.10 * composite_risk(p)
end

prototypes = load_portfolio(portfolio_path)
scored = [(p.name, prototype_value(p), composite_risk(p)) for p in prototypes]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_prototype_scores.csv"), "w") do io
    println(io, "rank,prototype,prototype_value,composite_risk")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f\n", rank, row[1], row[2], row[3])
    end
end

println("Julia prototype portfolio model complete.")
println("Outputs written to: $(output_dir)")
