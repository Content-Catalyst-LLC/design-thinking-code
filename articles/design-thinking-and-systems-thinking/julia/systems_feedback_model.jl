#!/usr/bin/env julia

# Systems-design value and delayed-feedback model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "system_intervention_portfolio_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Intervention
    name::String
    human_value::Float64
    system_leverage::Float64
    feasibility::Float64
    equity_sensitivity::Float64
    durability::Float64
    risk::Float64
    evidence_quality::Float64
    stakeholder_coverage::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_portfolio(path::String)
    lines = readlines(path)
    interventions = Intervention[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 12
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
                parse_float(fields[11])
            )
        )
    end

    return interventions
end

function evidence_strength(x::Intervention)
    return 0.55 * x.evidence_quality + 0.45 * x.stakeholder_coverage
end

function system_design_value(x::Intervention)
    return 0.24 * x.human_value +
           0.26 * x.system_leverage +
           0.18 * x.feasibility +
           0.14 * x.equity_sensitivity +
           0.12 * x.durability -
           0.06 * x.risk
end

function evidence_adjusted_value(x::Intervention)
    return system_design_value(x) * (0.75 + 0.25 * evidence_strength(x))
end

function delayed_feedback_path(starting_performance::Float64, intensity::Float64, adaptation::Float64; alpha=0.65, beta=0.40, delay=2, periods=16)
    performance = Float64[starting_performance]
    for t in 1:periods
        delayed = t <= delay ? 0.0 : min(1.0, adaptation + 0.02 * (t - delay))
        next_value = performance[end] + alpha * intensity - beta * delayed
        push!(performance, min(max(next_value, 0.0), 10.0))
    end
    return performance
end

interventions = load_portfolio(input_path)
scored = [(x.name, system_design_value(x), evidence_adjusted_value(x), evidence_strength(x)) for x in interventions]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_system_design_scores.csv"), "w") do io
    println(io, "rank,intervention,system_design_value,evidence_adjusted_value,evidence_strength")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4])
    end
end

path = delayed_feedback_path(6.5, 0.75, 0.36)

open(joinpath(output_dir, "julia_delayed_feedback_path.csv"), "w") do io
    println(io, "period,simulated_performance")
    for (idx, value) in enumerate(path)
        @printf(io, "%d,%.6f\n", idx - 1, value)
    end
end

println("Julia systems feedback model complete.")
println("Outputs written to: $(output_dir)")
