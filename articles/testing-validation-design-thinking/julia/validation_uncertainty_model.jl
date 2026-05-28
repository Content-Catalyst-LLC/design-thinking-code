#!/usr/bin/env julia

# Testing and validation portfolio model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "validation_concepts_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Concept
    name::String
    desirability::Float64
    feasibility::Float64
    viability::Float64
    responsibility::Float64
    friction::Float64
    residual_risk::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_concepts(path::String)
    lines = readlines(path)
    concepts = Concept[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 9
            error("Malformed row: $(line)")
        end

        push!(
            concepts,
            Concept(
                strip(fields[1]),
                parse_float(fields[4]),
                parse_float(fields[5]),
                parse_float(fields[6]),
                parse_float(fields[7]),
                parse_float(fields[8]),
                parse_float(fields[9])
            )
        )
    end

    return concepts
end

function combined_risk(c::Concept)
    return 0.50 * c.friction + 0.50 * c.residual_risk
end

function validation_value(c::Concept)
    return 0.25 * c.desirability +
           0.20 * c.feasibility +
           0.20 * c.viability +
           0.20 * c.responsibility -
           0.15 * combined_risk(c)
end

concepts = load_concepts(input_path)
scored = [(c.name, validation_value(c), combined_risk(c)) for c in concepts]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_validation_scores.csv"), "w") do io
    println(io, "rank,concept,validation_value,combined_risk")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f\n", rank, row[1], row[2], row[3])
    end
end

println("Julia testing and validation model complete.")
println("Outputs written to: $(output_dir)")
