#!/usr/bin/env julia

# Robust experiment portfolio analysis in Julia.
#
# Uses only Julia standard-library functionality so the script is easy
# to run in professional environments without package installation.

using Random
using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "experiments_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Experiment
    name::String
    learning_gain::Float64
    update_flexibility::Float64
    expected_improvement::Float64
    residual_risk::Float64
end

function parse_float(value)
    try
        return parse(Float64, strip(value))
    catch
        error("Unable to parse numeric value: $(value)")
    end
end

function load_experiments(path::String)
    lines = readlines(path)
    if length(lines) < 2
        error("Input CSV contains no data rows.")
    end

    experiments = Experiment[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 5
            error("Malformed row: $(line)")
        end

        push!(
            experiments,
            Experiment(
                strip(fields[1]),
                parse_float(fields[2]),
                parse_float(fields[3]),
                parse_float(fields[4]),
                parse_float(fields[5])
            )
        )
    end

    return experiments
end

function experiment_value(experiment::Experiment, weights::Dict{String, Float64})
    return (
        weights["learning_gain"] * experiment.learning_gain +
        weights["update_flexibility"] * experiment.update_flexibility +
        weights["expected_improvement"] * experiment.expected_improvement -
        weights["residual_risk"] * experiment.residual_risk
    )
end

function score_experiments(experiments, weights)
    scored = [(e.name, experiment_value(e, weights)) for e in experiments]
    return sort(scored, by = x -> x[2], rev = true)
end

function monte_carlo(experiments, weights; simulations = 10000, score_sd = 0.6, seed = 42)
    Random.seed!(seed)

    winner_counts = Dict(e.name => 0 for e in experiments)

    for _ in 1:simulations
        simulated = Experiment[]

        for e in experiments
            push!(
                simulated,
                Experiment(
                    e.name,
                    clamp(e.learning_gain + randn() * score_sd, 1.0, 10.0),
                    clamp(e.update_flexibility + randn() * score_sd, 1.0, 10.0),
                    clamp(e.expected_improvement + randn() * score_sd, 1.0, 10.0),
                    clamp(e.residual_risk + randn() * score_sd, 1.0, 10.0)
                )
            )
        end

        scored = score_experiments(simulated, weights)
        winner_counts[scored[1][1]] += 1
    end

    return winner_counts
end

experiments = load_experiments(input_path)

weights = Dict(
    "learning_gain" => 0.35,
    "update_flexibility" => 0.25,
    "expected_improvement" => 0.25,
    "residual_risk" => 0.15
)

scored = score_experiments(experiments, weights)
winners = monte_carlo(experiments, weights, simulations = 10000, score_sd = 0.6, seed = 42)

open(joinpath(output_dir, "julia_experiment_portfolio_results.csv"), "w") do io
    println(io, "rank,experiment,experiment_value")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f\n", rank, row[1], row[2])
    end
end

open(joinpath(output_dir, "julia_experiment_monte_carlo_winners.csv"), "w") do io
    println(io, "experiment,times_ranked_first,probability_ranked_first")
    for (name, count) in sort(collect(winners), by = x -> x[2], rev = true)
        @printf(io, "%s,%d,%.6f\n", name, count, count / 10000)
    end
end

println("Julia experiment portfolio analysis complete.")
println("Outputs written to: $(output_dir)")
