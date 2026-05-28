#!/usr/bin/env julia

# Robust design portfolio analysis in Julia.
#
# Uses only Julia standard-library functionality so the script is easy
# to run in professional environments without package installation.

using DelimitedFiles
using Random
using Statistics
using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "design_pathways_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct DesignPathway
    name::String
    human_relevance::Float64
    feasibility::Float64
    learning_value::Float64
    residual_risk::Float64
end

function parse_float(value)
    try
        return parse(Float64, strip(value))
    catch
        error("Unable to parse numeric value: $(value)")
    end
end

function load_pathways(path::String)
    lines = readlines(path)
    if length(lines) < 2
        error("Input CSV contains no data rows.")
    end

    pathways = DesignPathway[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 5
            error("Malformed row: $(line)")
        end

        push!(
            pathways,
            DesignPathway(
                strip(fields[1]),
                parse_float(fields[2]),
                parse_float(fields[3]),
                parse_float(fields[4]),
                parse_float(fields[5])
            )
        )
    end

    return pathways
end

function design_value(pathway::DesignPathway, weights::Dict{String, Float64})
    return (
        weights["human_relevance"] * pathway.human_relevance +
        weights["feasibility"] * pathway.feasibility +
        weights["learning_value"] * pathway.learning_value -
        weights["residual_risk"] * pathway.residual_risk
    )
end

function score_pathways(pathways, weights)
    scored = [(p.name, design_value(p, weights)) for p in pathways]
    return sort(scored, by = x -> x[2], rev = true)
end

function monte_carlo(pathways, weights; simulations = 10000, score_sd = 0.6, seed = 42)
    Random.seed!(seed)

    winner_counts = Dict(p.name => 0 for p in pathways)

    for _ in 1:simulations
        simulated = DesignPathway[]

        for p in pathways
            push!(
                simulated,
                DesignPathway(
                    p.name,
                    clamp(p.human_relevance + randn() * score_sd, 1.0, 10.0),
                    clamp(p.feasibility + randn() * score_sd, 1.0, 10.0),
                    clamp(p.learning_value + randn() * score_sd, 1.0, 10.0),
                    clamp(p.residual_risk + randn() * score_sd, 1.0, 10.0)
                )
            )
        end

        scored = score_pathways(simulated, weights)
        winner_counts[scored[1][1]] += 1
    end

    return winner_counts
end

pathways = load_pathways(input_path)

weights = Dict(
    "human_relevance" => 0.35,
    "feasibility" => 0.25,
    "learning_value" => 0.25,
    "residual_risk" => 0.15
)

scored = score_pathways(pathways, weights)
winners = monte_carlo(pathways, weights, simulations = 10000, score_sd = 0.6, seed = 42)

open(joinpath(output_dir, "julia_design_portfolio_results.csv"), "w") do io
    println(io, "rank,pathway,design_value")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f\n", rank, row[1], row[2])
    end
end

open(joinpath(output_dir, "julia_monte_carlo_winners.csv"), "w") do io
    println(io, "pathway,times_ranked_first,probability_ranked_first")
    for (name, count) in sort(collect(winners), by = x -> x[2], rev = true)
        @printf(io, "%s,%d,%.6f\n", name, count, count / 10000)
    end
end

println("Julia robust design portfolio analysis complete.")
println("Outputs written to: $(output_dir)")
