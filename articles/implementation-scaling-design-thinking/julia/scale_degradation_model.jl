#!/usr/bin/env julia

# Implementation value and scale degradation model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "implementation_portfolio_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Intervention
    name::String
    adoption_readiness::Float64
    operational_fit::Float64
    durability::Float64
    governance_readiness::Float64
    equity_readiness::Float64
    financial_sustainability::Float64
    operational_risk::Float64
    governance_risk::Float64
    technical_risk::Float64
    equity_risk::Float64
    financial_risk::Float64
    context_complexity::Float64
    scale_sensitivity::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_portfolio(path::String)
    lines = readlines(path)
    interventions = Intervention[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 19
            error("Malformed row: $(line)")
        end

        push!(
            interventions,
            Intervention(
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
                parse_float(fields[17]),
                parse_float(fields[18])
            )
        )
    end

    return interventions
end

function composite_risk(x::Intervention)
    return 0.25 * x.operational_risk +
           0.22 * x.governance_risk +
           0.18 * x.technical_risk +
           0.22 * x.equity_risk +
           0.13 * x.financial_risk
end

function implementation_value(x::Intervention)
    return 0.20 * x.adoption_readiness +
           0.18 * x.operational_fit +
           0.18 * x.durability +
           0.15 * x.governance_readiness +
           0.14 * x.equity_readiness +
           0.10 * x.financial_sustainability -
           0.05 * composite_risk(x)
end

function scaled_quality(x::Intervention)
    return implementation_value(x) - x.scale_sensitivity * x.context_complexity
end

interventions = load_portfolio(input_path)
scored = [(x.name, implementation_value(x), scaled_quality(x), composite_risk(x)) for x in interventions]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_implementation_scores.csv"), "w") do io
    println(io, "rank,intervention,implementation_value,scaled_quality_estimate,composite_risk")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4])
    end
end

println("Julia implementation and scale degradation model complete.")
println("Outputs written to: $(output_dir)")
