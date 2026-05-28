#!/usr/bin/env julia

# Robust idea portfolio analysis in Julia.
#
# Uses only Julia standard-library functionality so the script is easy
# to run in professional environments without package installation.

using Random
using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "idea_portfolio_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Idea
    name::String
    desirability::Float64
    feasibility::Float64
    novelty::Float64
    equity_value::Float64
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

function load_ideas(path::String)
    lines = readlines(path)
    if length(lines) < 2
        error("Input CSV contains no data rows.")
    end

    ideas = Idea[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 8
            error("Malformed row: $(line)")
        end

        push!(
            ideas,
            Idea(
                strip(fields[1]),
                parse_float(fields[3]),
                parse_float(fields[4]),
                parse_float(fields[5]),
                parse_float(fields[6]),
                parse_float(fields[7]),
                parse_float(fields[8])
            )
        )
    end

    return ideas
end

function idea_value(idea::Idea, weights::Dict{String, Float64})
    return (
        weights["desirability"] * idea.desirability +
        weights["feasibility"] * idea.feasibility +
        weights["novelty"] * idea.novelty +
        weights["equity_value"] * idea.equity_value +
        weights["learning_value"] * idea.learning_value -
        weights["composite_risk"] * idea.residual_risk
    )
end

function score_ideas(ideas, weights)
    scored = [(i.name, idea_value(i, weights)) for i in ideas]
    return sort(scored, by = x -> x[2], rev = true)
end

function monte_carlo(ideas, weights; simulations = 10000, score_sd = 0.6, seed = 42)
    Random.seed!(seed)

    winner_counts = Dict(i.name => 0 for i in ideas)

    for _ in 1:simulations
        simulated = Idea[]

        for i in ideas
            push!(
                simulated,
                Idea(
                    i.name,
                    clamp(i.desirability + randn() * score_sd, 1.0, 10.0),
                    clamp(i.feasibility + randn() * score_sd, 1.0, 10.0),
                    clamp(i.novelty + randn() * score_sd, 1.0, 10.0),
                    clamp(i.equity_value + randn() * score_sd, 1.0, 10.0),
                    clamp(i.learning_value + randn() * score_sd, 1.0, 10.0),
                    clamp(i.residual_risk + randn() * score_sd, 1.0, 10.0)
                )
            )
        end

        scored = score_ideas(simulated, weights)
        winner_counts[scored[1][1]] += 1
    end

    return winner_counts
end

ideas = load_ideas(input_path)

weights = Dict(
    "desirability" => 0.24,
    "feasibility" => 0.18,
    "novelty" => 0.18,
    "equity_value" => 0.18,
    "learning_value" => 0.12,
    "composite_risk" => 0.10
)

scored = score_ideas(ideas, weights)
winners = monte_carlo(ideas, weights, simulations = 10000, score_sd = 0.6, seed = 42)

open(joinpath(output_dir, "julia_ideation_results.csv"), "w") do io
    println(io, "rank,idea,idea_value")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f\n", rank, row[1], row[2])
    end
end

open(joinpath(output_dir, "julia_ideation_monte_carlo_winners.csv"), "w") do io
    println(io, "idea,times_ranked_first,probability_ranked_first")
    for (name, count) in sort(collect(winners), by = x -> x[2], rev = true)
        @printf(io, "%s,%d,%.6f\n", name, count, count / 10000)
    end
end

println("Julia ideation portfolio analysis complete.")
println("Outputs written to: $(output_dir)")
