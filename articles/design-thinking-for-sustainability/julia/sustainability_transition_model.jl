#!/usr/bin/env julia

# Sustainability design value and transition learning model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "sustainability_concepts_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Concept
    name::String
    usability::Float64
    feasibility::Float64
    ecological_benefit::Float64
    circularity::Float64
    equity::Float64
    durability::Float64
    risk::Float64
    evidence_quality::Float64
    stakeholder_coverage::Float64
    lifecycle_boundary_quality::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_concepts(path::String)
    lines = readlines(path)
    concepts = Concept[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 13
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
                parse_float(fields[9]),
                parse_float(fields[10]),
                parse_float(fields[11]),
                parse_float(fields[12]),
                parse_float(fields[13])
            )
        )
    end

    return concepts
end

function evidence_strength(x::Concept)
    return 0.35 * x.evidence_quality + 0.30 * x.stakeholder_coverage + 0.35 * x.lifecycle_boundary_quality
end

function sustainability_value(x::Concept)
    return 0.16 * x.usability +
           0.16 * x.feasibility +
           0.24 * x.ecological_benefit +
           0.16 * x.circularity +
           0.14 * x.equity +
           0.08 * x.durability -
           0.06 * x.risk
end

function evidence_adjusted_value(x::Concept)
    return sustainability_value(x) * (0.75 + 0.25 * evidence_strength(x))
end

function transition_quality_path(; adoption_start=0.20, friction_start=6.0, ecological_start=0.15, equity_start=7.0, periods=12)
    rows = []
    adoption = adoption_start
    friction = friction_start
    ecological = ecological_start
    equity = equity_start

    for t in 0:periods
        quality = 0.30 * adoption * 10.0 - 0.20 * friction + 0.32 * ecological * 10.0 + 0.18 * equity
        push!(rows, (t, adoption, friction, ecological, equity, quality))
        adoption = min(0.95, adoption + 0.045)
        friction = max(2.0, friction - 0.18)
        ecological = min(0.75, ecological + 0.035)
        equity = min(9.5, equity + 0.08)
    end

    return rows
end

concepts = load_concepts(input_path)
scored = [(x.name, sustainability_value(x), evidence_adjusted_value(x), evidence_strength(x)) for x in concepts]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_sustainability_scores.csv"), "w") do io
    println(io, "rank,concept,sustainability_value,evidence_adjusted_value,evidence_strength")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4])
    end
end

path = transition_quality_path()

open(joinpath(output_dir, "julia_transition_quality_path.csv"), "w") do io
    println(io, "period,adoption,friction,ecological_reduction,equity,transition_quality")
    for row in path
        @printf(io, "%d,%.6f,%.6f,%.6f,%.6f,%.6f\n", row[1], row[2], row[3], row[4], row[5], row[6])
    end
end

println("Julia sustainability transition model complete.")
println("Outputs written to: $(output_dir)")
