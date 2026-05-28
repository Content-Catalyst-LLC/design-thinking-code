#!/usr/bin/env julia

# Organizational innovation design value and prototype-learning model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "organizational_innovation_concepts_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct InnovationConcept
    name::String
    desirability::Float64
    feasibility::Float64
    viability::Float64
    equity::Float64
    learning_value::Float64
    implementation_readiness::Float64
    risk::Float64
    evidence_quality::Float64
    stakeholder_coverage::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_concepts(path::String)
    lines = readlines(path)
    concepts = InnovationConcept[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 15
            error("Malformed row: $(line)")
        end

        push!(
            concepts,
            InnovationConcept(
                strip(fields[1]),
                parse_float(fields[4]),
                parse_float(fields[5]),
                parse_float(fields[6]),
                parse_float(fields[7]),
                parse_float(fields[8]),
                parse_float(fields[9]),
                parse_float(fields[10]),
                parse_float(fields[11]),
                parse_float(fields[12])
            )
        )
    end

    return concepts
end

function evidence_strength(x::InnovationConcept)
    return 0.55 * x.evidence_quality + 0.45 * x.stakeholder_coverage
end

function design_value(x::InnovationConcept)
    return 0.22 * x.desirability +
           0.16 * x.feasibility +
           0.16 * x.viability +
           0.18 * x.equity +
           0.12 * x.learning_value +
           0.10 * x.implementation_readiness -
           0.06 * x.risk
end

function evidence_adjusted_value(x::InnovationConcept)
    return design_value(x) * (0.75 + 0.25 * evidence_strength(x))
end

function prototype_learning_path(; adoption_start=0.30, friction_start=6.0, trust_start=6.7, burden_start=6.5, equity_start=7.2, periods=12)
    rows = []
    adoption = adoption_start
    friction = friction_start
    trust = trust_start
    burden = burden_start
    equity = equity_start

    for t in 0:periods
        quality = 0.24 * adoption * 10.0 - 0.18 * friction + 0.20 * trust - 0.16 * burden + 0.22 * equity
        push!(rows, (t, adoption, friction, trust, burden, equity, quality))
        adoption = min(0.95, adoption + 0.045)
        friction = max(2.0, friction - 0.18)
        trust = min(9.5, trust + 0.09)
        burden = max(2.0, burden - 0.12)
        equity = min(9.5, equity + 0.08)
    end

    return rows
end

concepts = load_concepts(input_path)
scored = [(x.name, design_value(x), evidence_adjusted_value(x), evidence_strength(x)) for x in concepts]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_organizational_innovation_scores.csv"), "w") do io
    println(io, "rank,concept,design_value,evidence_adjusted_value,evidence_strength")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4])
    end
end

path = prototype_learning_path()

open(joinpath(output_dir, "julia_prototype_learning_path.csv"), "w") do io
    println(io, "period,adoption,friction,trust,burden,equity,prototype_quality")
    for row in path
        @printf(io, "%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n", row[1], row[2], row[3], row[4], row[5], row[6], row[7])
    end
end

println("Julia organizational learning model complete.")
println("Outputs written to: $(output_dir)")
