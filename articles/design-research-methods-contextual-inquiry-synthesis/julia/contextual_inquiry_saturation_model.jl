#!/usr/bin/env julia

# Contextual inquiry saturation and theme confidence model in Julia.
# Uses only Julia standard-library functionality.

using Printf
using Random

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "contextual_inquiry_evidence_units_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct EvidenceUnit
    unit_id::Int
    participant_group::String
    method::String
    primary_theme::String
    evidence_strength::Float64
    interpretive_risk::Float64
end

function parse_float(value::SubString{String})
    return parse(Float64, strip(value))
end

function parse_int(value::SubString{String})
    return parse(Int, strip(value))
end

function load_evidence(path::String)
    lines = readlines(path)
    evidence = EvidenceUnit[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 7
            error("Malformed row: $(line)")
        end

        push!(
            evidence,
            EvidenceUnit(
                parse_int(fields[1]),
                strip(fields[2]),
                strip(fields[3]),
                strip(fields[4]),
                parse_float(fields[6]),
                parse_float(fields[7])
            )
        )
    end

    return evidence
end

function theme_summary(evidence)
    themes = unique([e.primary_theme for e in evidence])
    rows = []

    for theme in themes
        subset = filter(e -> e.primary_theme == theme, evidence)
        evidence_units = length(subset)
        stakeholder_groups = length(unique([e.participant_group for e in subset]))
        methods = length(unique([e.method for e in subset]))
        mean_strength = sum(e.evidence_strength for e in subset) / evidence_units
        mean_risk = sum(e.interpretive_risk for e in subset) / evidence_units
        confidence = 0.35 * mean_strength + 0.25 * stakeholder_groups + 0.25 * methods - 0.15 * mean_risk
        push!(rows, (theme, evidence_units, stakeholder_groups, methods, mean_strength, mean_risk, confidence))
    end

    return sort(rows, by = x -> x[7], rev = true)
end

function saturation(evidence)
    sorted_evidence = sort(evidence, by = e -> e.unit_id)
    observed = Set{String}()
    rows = []
    previous = 0

    for e in sorted_evidence
        push!(observed, e.primary_theme)
        current = length(observed)
        push!(rows, (e.unit_id, current, current - previous))
        previous = current
    end

    return rows
end

evidence = load_evidence(input_path)
summary = theme_summary(evidence)
sat = saturation(evidence)

open(joinpath(output_dir, "julia_theme_summary.csv"), "w") do io
    println(io, "rank,theme,evidence_units,stakeholder_groups,methods,mean_evidence_strength,mean_interpretive_risk,synthesis_confidence")
    for (rank, row) in enumerate(summary)
        @printf(io, "%d,%s,%d,%d,%d,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4], row[5], row[6], row[7])
    end
end

open(joinpath(output_dir, "julia_saturation_analysis.csv"), "w") do io
    println(io, "unit_id,cumulative_theme_count,marginal_theme_discovery")
    for row in sat
        @printf(io, "%d,%d,%d\n", row[1], row[2], row[3])
    end
end

println("Julia contextual inquiry saturation analysis complete.")
println("Outputs written to: $(output_dir)")
