#!/usr/bin/env julia

# Institutional readiness model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "institutional_design_options_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct InstitutionalOption
    name::String
    desirability::Float64
    authority::Float64
    capability::Float64
    funding::Float64
    policy_fit::Float64
    governance::Float64
    trust_gain::Float64
    burden_reduction::Float64
    coordination::Float64
    implementation_risk::Float64
    data_readiness::Float64
    frontline_fit::Float64
    maintenance::Float64
    equity::Float64
    public_value::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_options(path::String)
    lines = readlines(path)
    items = InstitutionalOption[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 17
            error("Malformed option row: $(line)")
        end

        push!(
            items,
            InstitutionalOption(
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
                parse_float(fields[17])
            )
        )
    end

    return items
end

function readiness(x::InstitutionalOption)
    return 0.14*x.desirability + 0.13*x.authority + 0.12*x.capability +
           0.10*x.funding + 0.10*x.policy_fit + 0.11*x.governance +
           0.08*x.trust_gain + 0.08*x.burden_reduction + 0.06*x.data_readiness +
           0.05*x.frontline_fit + 0.03*x.maintenance -
           0.05*x.coordination - 0.05*x.implementation_risk
end

function absorption(x::InstitutionalOption)
    return 0.18*x.authority + 0.18*x.capability + 0.14*x.funding +
           0.14*x.governance + 0.12*x.policy_fit + 0.10*x.frontline_fit +
           0.08*x.maintenance + 0.06*x.data_readiness
end

function public_value_priority(x::InstitutionalOption)
    return 0.24*x.public_value + 0.20*x.burden_reduction + 0.18*x.trust_gain +
           0.16*x.equity + 0.12*x.desirability + 0.10*x.policy_fit -
           0.08*x.implementation_risk
end

function sequencing_need(x::InstitutionalOption)
    return 0.28*x.coordination + 0.24*x.implementation_risk +
           0.14*(10.0-x.authority) + 0.12*(10.0-x.capability) +
           0.10*(10.0-x.funding) + 0.07*(10.0-x.maintenance) +
           0.05*(10.0-x.data_readiness)
end

function portfolio_score(x::InstitutionalOption)
    return 0.30*readiness(x) + 0.26*public_value_priority(x) +
           0.20*absorption(x) + 0.10*x.equity + 0.06*x.trust_gain -
           0.12*sequencing_need(x) - 0.08*x.implementation_risk
end

options = load_options(input_path)
scored = [(x.name, readiness(x), absorption(x), public_value_priority(x), sequencing_need(x), portfolio_score(x)) for x in options]
scored = sort(scored, by = x -> x[6], rev = true)

open(joinpath(output_dir, "julia_institutional_readiness_scores.csv"), "w") do io
    println(io, "rank,option,change_readiness,absorption_capacity,public_value_priority,sequencing_need,portfolio_score")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4], row[5], row[6])
    end
end

println("Julia institutional readiness model complete.")
println("Outputs written to: $(output_dir)")
