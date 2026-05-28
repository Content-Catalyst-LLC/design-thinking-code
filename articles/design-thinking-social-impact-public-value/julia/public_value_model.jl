#!/usr/bin/env julia

# Public-value social impact model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "social_impact_interventions_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Intervention
    name::String
    access::Float64
    equity::Float64
    dignity::Float64
    legitimacy::Float64
    accountability::Float64
    outcome_strength::Float64
    sustainability::Float64
    learning::Float64
    feasibility::Float64
    governance::Float64
    implementation_risk::Float64
    burden_risk::Float64
    participation::Float64
    community_value::Float64
    repair::Float64
    stewardship::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_interventions(path::String)
    lines = readlines(path)
    items = Intervention[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 18
            error("Malformed intervention row: $(line)")
        end

        push!(
            items,
            Intervention(
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
                parse_float(fields[13]),
                parse_float(fields[14]),
                parse_float(fields[15]),
                parse_float(fields[16]),
                parse_float(fields[17]),
                parse_float(fields[18])
            )
        )
    end

    return items
end

function public_value(x::Intervention)
    return 0.13*x.access + 0.15*x.equity + 0.12*x.dignity +
           0.12*x.legitimacy + 0.13*x.accountability + 0.11*x.outcome_strength +
           0.08*x.sustainability + 0.07*x.learning + 0.05*x.community_value +
           0.04*x.repair
end

function impact_readiness(x::Intervention)
    pv = public_value(x)
    return 0.30*pv + 0.17*x.feasibility + 0.16*x.governance +
           0.12*x.learning + 0.10*x.participation + 0.08*x.stewardship +
           0.07*x.repair - 0.07*x.implementation_risk - 0.07*x.burden_risk
end

function stewardship_need(x::Intervention)
    return 0.24*x.implementation_risk + 0.22*x.burden_risk +
           0.16*(10.0-x.governance) + 0.12*(10.0-x.sustainability) +
           0.10*(10.0-x.learning) + 0.08*(10.0-x.repair) +
           0.08*(10.0-x.stewardship)
end

function portfolio_priority(x::Intervention)
    return 0.36*public_value(x) + 0.28*impact_readiness(x) +
           0.14*x.equity + 0.10*x.community_value + 0.06*x.participation -
           0.14*stewardship_need(x) - 0.06*x.implementation_risk
end

interventions = load_interventions(input_path)
scored = [(x.name, public_value(x), impact_readiness(x), stewardship_need(x), portfolio_priority(x)) for x in interventions]
scored = sort(scored, by = x -> x[5], rev = true)

open(joinpath(output_dir, "julia_public_value_scores.csv"), "w") do io
    println(io, "rank,intervention,public_value_score,impact_readiness,stewardship_need,portfolio_priority")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4], row[5])
    end
end

println("Julia public-value model complete.")
println("Outputs written to: $(output_dir)")
