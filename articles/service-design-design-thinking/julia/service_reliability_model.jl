#!/usr/bin/env julia

# Service reliability and stage quality model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "service_journey_stages_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct ServiceStage
    name::String
    completion_probability::Float64
    clarity::Float64
    trust::Float64
    accessibility::Float64
    user_burden::Float64
    staff_load::Float64
    recovery_quality::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_stages(path::String)
    lines = readlines(path)
    stages = ServiceStage[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 10
            error("Malformed row: $(line)")
        end

        push!(
            stages,
            ServiceStage(
                strip(fields[1]),
                parse_float(fields[4]),
                parse_float(fields[5]),
                parse_float(fields[6]),
                parse_float(fields[7]),
                parse_float(fields[8]),
                parse_float(fields[9]),
                parse_float(fields[10])
            )
        )
    end

    return stages
end

function stage_quality(x::ServiceStage)
    return 0.22 * x.completion_probability * 10.0 +
           0.18 * x.clarity +
           0.18 * x.trust +
           0.16 * x.accessibility +
           0.14 * x.recovery_quality -
           0.07 * x.user_burden -
           0.05 * x.staff_load
end

function redesign_priority(x::ServiceStage)
    failure_risk = 1.0 - x.completion_probability
    burden_risk = 0.55 * x.user_burden + 0.45 * x.staff_load
    return 0.34 * failure_risk * 10.0 +
           0.26 * burden_risk +
           0.18 * (10.0 - x.clarity) +
           0.12 * (10.0 - x.accessibility) +
           0.10 * (10.0 - x.recovery_quality)
end

function service_reliability(stages)
    r = 1.0
    for stage in stages
        r *= stage.completion_probability
    end
    return r
end

stages = load_stages(input_path)
scored = [(x.name, stage_quality(x), redesign_priority(x), x.completion_probability) for x in stages]
scored = sort(scored, by = x -> x[3], rev = true)

open(joinpath(output_dir, "julia_service_stage_scores.csv"), "w") do io
    println(io, "rank,stage,stage_quality,redesign_priority,completion_probability")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4])
    end
end

open(joinpath(output_dir, "julia_service_reliability.csv"), "w") do io
    println(io, "metric,value")
    @printf(io, "end_to_end_reliability,%.8f\n", service_reliability(stages))
end

println("Julia service reliability model complete.")
println("Outputs written to: $(output_dir)")
