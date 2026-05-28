#!/usr/bin/env julia

# Public-policy design value and policy-learning model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "public_policy_pilots_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct PolicyPilot
    name::String
    accessibility::Float64
    feasibility::Float64
    legitimacy::Float64
    equity::Float64
    burden_reduction::Float64
    durability::Float64
    risk::Float64
    evidence_quality::Float64
    stakeholder_coverage::Float64
    participation_quality::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_pilots(path::String)
    lines = readlines(path)
    pilots = PolicyPilot[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 16
            error("Malformed row: $(line)")
        end

        push!(
            pilots,
            PolicyPilot(
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
                parse_float(fields[15])
            )
        )
    end

    return pilots
end

function evidence_strength(x::PolicyPilot)
    return 0.40 * x.evidence_quality + 0.35 * x.stakeholder_coverage + 0.25 * x.participation_quality
end

function policy_value(x::PolicyPilot)
    return 0.20 * x.accessibility +
           0.16 * x.feasibility +
           0.16 * x.legitimacy +
           0.20 * x.equity +
           0.14 * x.burden_reduction +
           0.08 * x.durability -
           0.06 * x.risk
end

function evidence_adjusted_value(x::PolicyPilot)
    return policy_value(x) * (0.75 + 0.25 * evidence_strength(x))
end

function policy_learning_path(; uptake_start=0.25, friction_start=6.0, error_start=0.20, trust_start=6.8, equity_start=7.2, periods=12)
    rows = []
    uptake = uptake_start
    friction = friction_start
    error = error_start
    trust = trust_start
    equity = equity_start

    for t in 0:periods
        quality = 0.25 * uptake * 10.0 - 0.18 * friction - 0.20 * error * 10.0 + 0.18 * trust + 0.19 * equity
        push!(rows, (t, uptake, friction, error, trust, equity, quality))
        uptake = min(0.95, uptake + 0.045)
        friction = max(2.0, friction - 0.18)
        error = max(0.03, error - 0.010)
        trust = min(9.5, trust + 0.09)
        equity = min(9.5, equity + 0.08)
    end

    return rows
end

pilots = load_pilots(input_path)
scored = [(x.name, policy_value(x), evidence_adjusted_value(x), evidence_strength(x)) for x in pilots]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_public_policy_scores.csv"), "w") do io
    println(io, "rank,pilot,policy_value,evidence_adjusted_value,evidence_strength")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4])
    end
end

path = policy_learning_path()

open(joinpath(output_dir, "julia_policy_learning_path.csv"), "w") do io
    println(io, "period,uptake,friction,error,trust,equity,policy_quality")
    for row in path
        @printf(io, "%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n", row[1], row[2], row[3], row[4], row[5], row[6], row[7])
    end
end

println("Julia public-policy learning model complete.")
println("Outputs written to: $(output_dir)")
