#!/usr/bin/env julia

# Robust human-centered design portfolio analysis in Julia.
#
# Uses only Julia standard-library functionality so the script is easy
# to run in professional environments without package installation.

using Random
using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "human_centered_options_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct DesignOption
    name::String
    human_benefit::Float64
    usability::Float64
    stakeholder_fit::Float64
    burden::Float64
end

function parse_float(value)
    try
        return parse(Float64, strip(value))
    catch
        error("Unable to parse numeric value: $(value)")
    end
end

function load_options(path::String)
    lines = readlines(path)
    if length(lines) < 2
        error("Input CSV contains no data rows.")
    end

    options = DesignOption[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 5
            error("Malformed row: $(line)")
        end

        push!(
            options,
            DesignOption(
                strip(fields[1]),
                parse_float(fields[2]),
                parse_float(fields[3]),
                parse_float(fields[4]),
                parse_float(fields[5])
            )
        )
    end

    return options
end

function hc_value(option::DesignOption, weights::Dict{String, Float64})
    return (
        weights["human_benefit"] * option.human_benefit +
        weights["usability"] * option.usability +
        weights["stakeholder_fit"] * option.stakeholder_fit -
        weights["burden"] * option.burden
    )
end

function score_options(options, weights)
    scored = [(o.name, hc_value(o, weights)) for o in options]
    return sort(scored, by = x -> x[2], rev = true)
end

function monte_carlo(options, weights; simulations = 10000, score_sd = 0.6, seed = 42)
    Random.seed!(seed)

    winner_counts = Dict(o.name => 0 for o in options)

    for _ in 1:simulations
        simulated = DesignOption[]

        for o in options
            push!(
                simulated,
                DesignOption(
                    o.name,
                    clamp(o.human_benefit + randn() * score_sd, 1.0, 10.0),
                    clamp(o.usability + randn() * score_sd, 1.0, 10.0),
                    clamp(o.stakeholder_fit + randn() * score_sd, 1.0, 10.0),
                    clamp(o.burden + randn() * score_sd, 1.0, 10.0)
                )
            )
        end

        scored = score_options(simulated, weights)
        winner_counts[scored[1][1]] += 1
    end

    return winner_counts
end

options = load_options(input_path)

weights = Dict(
    "human_benefit" => 0.30,
    "usability" => 0.25,
    "stakeholder_fit" => 0.30,
    "burden" => 0.15
)

scored = score_options(options, weights)
winners = monte_carlo(options, weights, simulations = 10000, score_sd = 0.6, seed = 42)

open(joinpath(output_dir, "julia_human_centered_results.csv"), "w") do io
    println(io, "rank,option,hc_value")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f\n", rank, row[1], row[2])
    end
end

open(joinpath(output_dir, "julia_human_centered_monte_carlo_winners.csv"), "w") do io
    println(io, "option,times_ranked_first,probability_ranked_first")
    for (name, count) in sort(collect(winners), by = x -> x[2], rev = true)
        @printf(io, "%s,%d,%.6f\n", name, count, count / 10000)
    end
end

println("Julia human-centered design portfolio analysis complete.")
println("Outputs written to: $(output_dir)")
