#!/usr/bin/env julia

# Ethical risk model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "ethical_design_decisions_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct DesignDecision
    name::String
    harm::Float64
    probability::Float64
    exposure::Float64
    detectability::Float64
    accountability::Float64
    inclusion::Float64
    public_value::Float64
    repairability::Float64
    privacy::Float64
    autonomy::Float64
    manipulation::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_decisions(path::String)
    lines = readlines(path)
    items = DesignDecision[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 13
            error("Malformed decision row: $(line)")
        end

        push!(
            items,
            DesignDecision(
                strip(fields[1]),
                parse_float(fields[3]),
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

    return items
end

function ethical_risk(x::DesignDecision)
    return x.harm * x.probability * x.exposure * (1.0 - x.detectability) * (1.0 - x.accountability)
end

function review_priority(x::DesignDecision)
    r = ethical_risk(x)
    repair_deficit = 1.0 - x.repairability
    return 0.32*r + 0.20*x.harm + 0.14*x.exposure + 0.10*(1.0-x.accountability) +
           0.08*(1.0-x.detectability) + 0.06*(1.0-x.inclusion) + 0.05*x.privacy +
           0.03*x.autonomy + 0.02*x.manipulation - 0.12*x.public_value + 0.10*repair_deficit
end

decisions = load_decisions(input_path)
scored = [(x.name, ethical_risk(x), review_priority(x), x.public_value, x.repairability) for x in decisions]
scored = sort(scored, by = x -> x[3], rev = true)

open(joinpath(output_dir, "julia_ethical_design_scores.csv"), "w") do io
    println(io, "rank,design_decision,ethical_risk,public_value_adjusted_review_priority,public_value,repairability")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4], row[5])
    end
end

println("Julia ethical risk model complete.")
println("Outputs written to: $(output_dir)")
