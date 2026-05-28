#!/usr/bin/env julia

# Robust problem-frame portfolio analysis in Julia.
#
# Uses only Julia standard-library functionality so the script is easy
# to run in professional environments without package installation.

using Random
using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "problem_frames_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct ProblemFrame
    name::String
    explanatory_adequacy::Float64
    stakeholder_coverage::Float64
    opportunity_value::Float64
    framing_risk::Float64
end

function parse_float(value)
    try
        return parse(Float64, strip(value))
    catch
        error("Unable to parse numeric value: $(value)")
    end
end

function load_frames(path::String)
    lines = readlines(path)
    if length(lines) < 2
        error("Input CSV contains no data rows.")
    end

    frames = ProblemFrame[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 5
            error("Malformed row: $(line)")
        end

        push!(
            frames,
            ProblemFrame(
                strip(fields[1]),
                parse_float(fields[2]),
                parse_float(fields[3]),
                parse_float(fields[4]),
                parse_float(fields[5])
            )
        )
    end

    return frames
end

function frame_value(frame::ProblemFrame, weights::Dict{String, Float64})
    return (
        weights["explanatory_adequacy"] * frame.explanatory_adequacy +
        weights["stakeholder_coverage"] * frame.stakeholder_coverage +
        weights["opportunity_value"] * frame.opportunity_value -
        weights["framing_risk"] * frame.framing_risk
    )
end

function score_frames(frames, weights)
    scored = [(f.name, frame_value(f, weights)) for f in frames]
    return sort(scored, by = x -> x[2], rev = true)
end

function monte_carlo(frames, weights; simulations = 10000, score_sd = 0.6, seed = 42)
    Random.seed!(seed)

    winner_counts = Dict(f.name => 0 for f in frames)

    for _ in 1:simulations
        simulated = ProblemFrame[]

        for f in frames
            push!(
                simulated,
                ProblemFrame(
                    f.name,
                    clamp(f.explanatory_adequacy + randn() * score_sd, 1.0, 10.0),
                    clamp(f.stakeholder_coverage + randn() * score_sd, 1.0, 10.0),
                    clamp(f.opportunity_value + randn() * score_sd, 1.0, 10.0),
                    clamp(f.framing_risk + randn() * score_sd, 1.0, 10.0)
                )
            )
        end

        scored = score_frames(simulated, weights)
        winner_counts[scored[1][1]] += 1
    end

    return winner_counts
end

frames = load_frames(input_path)

weights = Dict(
    "explanatory_adequacy" => 0.30,
    "stakeholder_coverage" => 0.25,
    "opportunity_value" => 0.30,
    "framing_risk" => 0.15
)

scored = score_frames(frames, weights)
winners = monte_carlo(frames, weights, simulations = 10000, score_sd = 0.6, seed = 42)

open(joinpath(output_dir, "julia_problem_frame_results.csv"), "w") do io
    println(io, "rank,frame,frame_value")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f\n", rank, row[1], row[2])
    end
end

open(joinpath(output_dir, "julia_problem_frame_monte_carlo_winners.csv"), "w") do io
    println(io, "frame,times_ranked_first,probability_ranked_first")
    for (name, count) in sort(collect(winners), by = x -> x[2], rev = true)
        @printf(io, "%s,%d,%.6f\n", name, count, count / 10000)
    end
end

println("Julia problem-frame portfolio analysis complete.")
println("Outputs written to: $(output_dir)")
