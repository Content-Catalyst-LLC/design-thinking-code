#!/usr/bin/env julia

# Co-design participation quality and influence-gap model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "codesign_activities_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct CodesignActivity
    name::String
    representation::Float64
    accessibility::Float64
    participant_influence::Float64
    trust_quality::Float64
    evidence_quality::Float64
    implementation_accountability::Float64
    decision_impact::Float64
    ethical_risk::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_activities(path::String)
    lines = readlines(path)
    activities = CodesignActivity[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 11
            error("Malformed row: $(line)")
        end

        push!(
            activities,
            CodesignActivity(
                strip(fields[1]),
                parse_float(fields[4]),
                parse_float(fields[5]),
                parse_float(fields[6]),
                parse_float(fields[7]),
                parse_float(fields[8]),
                parse_float(fields[9]),
                parse_float(fields[10]),
                parse_float(fields[11])
            )
        )
    end

    return activities
end

function participation_quality(x::CodesignActivity)
    return 0.18 * x.representation +
           0.14 * x.accessibility +
           0.22 * x.participant_influence +
           0.12 * x.trust_quality +
           0.12 * x.evidence_quality +
           0.12 * x.implementation_accountability +
           0.14 * x.decision_impact -
           0.08 * x.ethical_risk
end

function influence_learning_path(; presence=0.50, influence=0.42, access=0.55, trust=0.50, rounds=12)
    rows = []
    p = presence
    i = influence
    a = access
    t = trust

    for r in 0:rounds
        legitimacy = 0.30 * p + 0.32 * i + 0.20 * a + 0.18 * t
        push!(rows, (r, p, i, a, t, legitimacy))
        p = min(0.95, p + 0.030)
        i = min(0.90, i + 0.035)
        a = min(0.95, a + 0.032)
        t = min(0.90, t + 0.028)
    end

    return rows
end

activities = load_activities(input_path)
scored = [(x.name, participation_quality(x), x.ethical_risk) for x in activities]
scored = sort(scored, by = x -> x[2], rev = true)

open(joinpath(output_dir, "julia_codesign_activity_scores.csv"), "w") do io
    println(io, "rank,activity,participation_quality,ethical_risk")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f\n", rank, row[1], row[2], row[3])
    end
end

path = influence_learning_path()

open(joinpath(output_dir, "julia_participation_influence_learning_path.csv"), "w") do io
    println(io, "round,presence,influence,access,trust,legitimacy")
    for row in path
        @printf(io, "%d,%.6f,%.6f,%.6f,%.6f,%.6f\n", row[1], row[2], row[3], row[4], row[5], row[6])
    end
end

println("Julia participation influence model complete.")
println("Outputs written to: $(output_dir)")
