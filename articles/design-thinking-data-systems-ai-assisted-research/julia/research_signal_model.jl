#!/usr/bin/env julia

# Research signal model in Julia.
# Uses only Julia standard-library functionality.

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "research_signals_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct ResearchSignal
    name::String
    source_strength::Float64
    relevance::Float64
    traceability::Float64
    representativeness::Float64
    validation::Float64
    missingness::Float64
    ai_risk_input::Float64
    decision_relevance::Float64
    recency::Float64
    consent::Float64
    coverage::Float64
end

function parse_float(value)
    return parse(Float64, strip(value))
end

function load_signals(path::String)
    lines = readlines(path)
    items = ResearchSignal[]

    for line in lines[2:end]
        fields = split(line, ",")
        if length(fields) < 13
            error("Malformed signal row: $(line)")
        end

        push!(
            items,
            ResearchSignal(
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

function confidence(x::ResearchSignal)
    return 0.18*x.source_strength + 0.17*x.relevance + 0.15*x.traceability +
           0.15*x.representativeness + 0.15*x.validation + 0.08*x.recency +
           0.07*x.consent + 0.05*x.coverage
end

function bias_risk(x::ResearchSignal)
    return 0.26*x.missingness + 0.22*(1.0-x.representativeness) +
           0.18*(1.0-x.validation) + 0.14*x.ai_risk_input +
           0.10*(1.0-x.traceability) + 0.10*(1.0-x.coverage)
end

function ai_risk(x::ResearchSignal)
    return 0.38*x.ai_risk_input + 0.18*(1.0-x.traceability) +
           0.16*(1.0-x.validation) + 0.14*x.missingness + 0.14*(1.0-x.consent)
end

function decision_readiness(x::ResearchSignal)
    c = confidence(x)
    b = bias_risk(x)
    return min(max(0.30*c + 0.24*x.decision_relevance + 0.14*x.validation +
                   0.12*x.traceability + 0.08*x.consent + 0.08*x.coverage -
                   0.04*b, 0.0), 1.0)
end

signals = load_signals(input_path)
scored = [(x.name, confidence(x), bias_risk(x), ai_risk(x), decision_readiness(x)) for x in signals]
scored = sort(scored, by = x -> x[3] + x[4], rev = true)

open(joinpath(output_dir, "julia_research_signal_scores.csv"), "w") do io
    println(io, "rank,signal,confidence_score,bias_risk,ai_risk,decision_readiness")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4], row[5])
    end
end

println("Julia research signal model complete.")
println("Outputs written to: $(output_dir)")
