#!/usr/bin/env julia

# Robust candidate-insight portfolio analysis in Julia.
#
# Uses only Julia standard-library functionality so the script is easy
# to run in professional environments without package installation.

using Random
using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "candidate_insights_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Insight
    name::String
    pattern_support::Float64
    explanatory_depth::Float64
    opportunity_value::Float64
    interpretive_risk::Float64
end

function parse_float(value)
    try
        return parse(Float64, strip(value))
    catch
        error("Unable to parse numeric value: $(value)")
    end
end

function load_insights(path::String)
    lines = readlines(path)
    if length(lines) < 2
        error("Input CSV contains no data rows.")
    end

    insights = Insight[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 5
            error("Malformed row: $(line)")
        end

        push!(
            insights,
            Insight(
                strip(fields[1]),
                parse_float(fields[2]),
                parse_float(fields[3]),
                parse_float(fields[4]),
                parse_float(fields[5])
            )
        )
    end

    return insights
end

function insight_value(insight::Insight, weights::Dict{String, Float64})
    return (
        weights["pattern_support"] * insight.pattern_support +
        weights["explanatory_depth"] * insight.explanatory_depth +
        weights["opportunity_value"] * insight.opportunity_value -
        weights["interpretive_risk"] * insight.interpretive_risk
    )
end

function score_insights(insights, weights)
    scored = [(i.name, insight_value(i, weights)) for i in insights]
    return sort(scored, by = x -> x[2], rev = true)
end

function monte_carlo(insights, weights; simulations = 10000, score_sd = 0.6, seed = 42)
    Random.seed!(seed)

    winner_counts = Dict(i.name => 0 for i in insights)

    for _ in 1:simulations
        simulated = Insight[]

        for i in insights
            push!(
                simulated,
                Insight(
                    i.name,
                    clamp(i.pattern_support + randn() * score_sd, 1.0, 10.0),
                    clamp(i.explanatory_depth + randn() * score_sd, 1.0, 10.0),
                    clamp(i.opportunity_value + randn() * score_sd, 1.0, 10.0),
                    clamp(i.interpretive_risk + randn() * score_sd, 1.0, 10.0)
                )
            )
        end

        scored = score_insights(simulated, weights)
        winner_counts[scored[1][1]] += 1
    end

    return winner_counts
end

insights = load_insights(input_path)

weights = Dict(
    "pattern_support" => 0.30,
    "explanatory_depth" => 0.30,
    "opportunity_value" => 0.25,
    "interpretive_risk" => 0.15
)

scored = score_insights(insights, weights)
winners = monte_carlo(insights, weights, simulations = 10000, score_sd = 0.6, seed = 42)

open(joinpath(output_dir, "julia_insight_generation_results.csv"), "w") do io
    println(io, "rank,insight,insight_value")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f\n", rank, row[1], row[2])
    end
end

open(joinpath(output_dir, "julia_insight_generation_monte_carlo_winners.csv"), "w") do io
    println(io, "insight,times_ranked_first,probability_ranked_first")
    for (name, count) in sort(collect(winners), by = x -> x[2], rev = true)
        @printf(io, "%s,%d,%.6f\n", name, count, count / 10000)
    end
end

println("Julia insight portfolio analysis complete.")
println("Outputs written to: $(output_dir)")
