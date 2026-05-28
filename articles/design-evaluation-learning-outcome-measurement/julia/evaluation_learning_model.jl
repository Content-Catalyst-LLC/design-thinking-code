#!/usr/bin/env julia

# Design evaluation and learning model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "evaluation_portfolio_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Intervention
    name::String
    outcome_improvement::Float64
    burden_reduction::Float64
    equity_performance::Float64
    trust_improvement::Float64
    durability::Float64
    operational_cost::Float64
    residual_risk::Float64
    evidence_quality::Float64
    stakeholder_coverage::Float64
    method_triangulation::Float64
    uncertainty::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_portfolio(path::String)
    lines = readlines(path)
    interventions = Intervention[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 14
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
                parse_float(fields[14])
            )
        )
    end

    return interventions
end

function penalty(x::Intervention)
    return 0.50 * x.operational_cost + 0.50 * x.residual_risk
end

function evidence_strength(x::Intervention)
    raw = 0.40 * x.evidence_quality +
          0.35 * x.stakeholder_coverage +
          0.25 * x.method_triangulation -
          0.20 * x.uncertainty
    return min(max(raw, 0.0), 1.0)
end

function evaluation_value(x::Intervention)
    return 0.24 * x.outcome_improvement +
           0.20 * x.burden_reduction +
           0.20 * x.equity_performance +
           0.16 * x.trust_improvement +
           0.14 * x.durability -
           0.06 * penalty(x)
end

function evidence_adjusted_value(x::Intervention)
    return evaluation_value(x) * (0.75 + 0.25 * evidence_strength(x))
end

interventions = load_portfolio(input_path)
scored = [(x.name, evaluation_value(x), evidence_adjusted_value(x), evidence_strength(x), penalty(x)) for x in interventions]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_evaluation_scores.csv"), "w") do io
    println(io, "rank,intervention,evaluation_value,evidence_adjusted_value,evidence_strength,penalty")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4], row[5])
    end
end

println("Julia design evaluation and learning model complete.")
println("Outputs written to: $(output_dir)")
