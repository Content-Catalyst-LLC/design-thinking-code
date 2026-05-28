#!/usr/bin/env julia

using Printf

article_dir = normpath(joinpath(@__DIR__, ".."))
input_path = joinpath(article_dir, "data", "raw", "future_design_initiatives_raw.csv")
output_dir = joinpath(article_dir, "outputs")
mkpath(output_dir)

struct Row
    name::String
    values::Vector{Float64}
end

function load_rows(path::String)
    rows = Row[]
    for line in readlines(path)[2:end]
        fields = split(line, ",")
        push!(rows, Row(strip(fields[1]), [parse(Float64, strip(x)) for x in fields[3:16]]))
    end
    return rows
end

function scores(v)
    human, systems, evidence, ethics, ai, implementation, public_value, stewardship, risk, participation, learning, data, climate, burden = v

    readiness = 0.11 * human + 0.12 * systems + 0.12 * evidence +
                0.12 * ethics + 0.10 * ai + 0.10 * implementation +
                0.12 * public_value + 0.09 * stewardship +
                0.06 * participation + 0.06 * learning +
                0.04 * data + 0.04 * climate + 0.04 * burden -
                0.10 * risk

    stewardship_need = 0.26 * risk + 0.17 * (10 - stewardship) +
                       0.15 * (10 - implementation) +
                       0.12 * (10 - ethics) +
                       0.10 * (10 - evidence) +
                       0.08 * (10 - systems) +
                       0.07 * (10 - learning) +
                       0.05 * (10 - burden)

    ai_maturity = 0.28 * ai + 0.18 * evidence + 0.16 * data +
                  0.14 * ethics + 0.12 * human + 0.12 * learning -
                  0.10 * risk

    priority = 0.36 * readiness + 0.20 * public_value +
               0.14 * ethics + 0.10 * systems + 0.08 * evidence +
               0.06 * participation - 0.10 * stewardship_need -
               0.06 * risk

    return readiness, stewardship_need, ai_maturity, priority
end

rows = load_rows(input_path)
scored = [(row.name, scores(row.values)...) for row in rows]
scored = sort(scored, by = x -> x[5], rev = true)

open(joinpath(output_dir, "julia_future_design_readiness_scores.csv"), "w") do io
    println(io, "rank,initiative,future_design_readiness,stewardship_need,ai_design_maturity,portfolio_priority")
    for (rank, row) in enumerate(scored)
        @printf(io, "%d,%s,%.6f,%.6f,%.6f,%.6f\n", rank, row[1], row[2], row[3], row[4], row[5])
    end
end

println("Julia future design-thinking readiness model complete.")
