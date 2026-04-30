"""Synthetic design thinking uncertainty simulation.

This script compares design pathways under uncertainty.
It is educational only and not a consulting, public-policy, product-validation,
or automated design-decision tool.
"""

from pathlib import Path
import csv
import random
import statistics

random.seed(4242)

pathways = [
    {
        "pathway": "Service Redesign Pathway",
        "human_relevance": 8.8,
        "feasibility": 7.4,
        "learning_value": 8.1,
        "residual_risk": 4.0,
    },
    {
        "pathway": "Digital Platform Pathway",
        "human_relevance": 7.9,
        "feasibility": 8.3,
        "learning_value": 7.7,
        "residual_risk": 4.3,
    },
    {
        "pathway": "Workflow Coordination Pathway",
        "human_relevance": 8.2,
        "feasibility": 7.8,
        "learning_value": 8.4,
        "residual_risk": 3.8,
    },
    {
        "pathway": "Community Partnership Pathway",
        "human_relevance": 8.6,
        "feasibility": 7.1,
        "learning_value": 8.5,
        "residual_risk": 4.2,
    },
]

weights = {
    "human_relevance": 0.35,
    "feasibility": 0.25,
    "learning_value": 0.25,
    "residual_risk": 0.15,
}

def design_value(row):
    return (
        weights["human_relevance"] * row["human_relevance"] +
        weights["feasibility"] * row["feasibility"] +
        weights["learning_value"] * row["learning_value"] -
        weights["residual_risk"] * row["residual_risk"]
    )

n_simulations = 5000
winner_counts = {row["pathway"]: 0 for row in pathways}
simulated_rows = []

for simulation_id in range(1, n_simulations + 1):
    scored = []

    for row in pathways:
        simulated = row.copy()
        for key in ["human_relevance", "feasibility", "learning_value", "residual_risk"]:
            simulated[key] = max(1.0, min(10.0, random.gauss(row[key], 0.6)))
        simulated["design_value"] = design_value(simulated)
        scored.append(simulated)

    scored.sort(key=lambda item: item["design_value"], reverse=True)
    winner_counts[scored[0]["pathway"]] += 1

    for rank, row in enumerate(scored, start=1):
        simulated_rows.append({
            "simulation_id": simulation_id,
            "rank": rank,
            "pathway": row["pathway"],
            "human_relevance": round(row["human_relevance"], 3),
            "feasibility": round(row["feasibility"], 3),
            "learning_value": round(row["learning_value"], 3),
            "residual_risk": round(row["residual_risk"], 3),
            "design_value": round(row["design_value"], 3),
        })

summary_rows = []
for pathway, count in winner_counts.items():
    values = [row["design_value"] for row in simulated_rows if row["pathway"] == pathway]
    summary_rows.append({
        "pathway": pathway,
        "probability_ranked_first_percent": round(100.0 * count / n_simulations, 2),
        "mean_design_value": round(statistics.mean(values), 3),
        "sd_design_value": round(statistics.stdev(values), 3),
    })

processed = Path(__file__).resolve().parents[1] / "data" / "processed"
processed.mkdir(parents=True, exist_ok=True)

simulation_path = processed / "synthetic_design_strategy_simulations.csv"
summary_path = processed / "synthetic_design_strategy_summary.csv"

for path, rows in [
    (simulation_path, simulated_rows),
    (summary_path, summary_rows),
]:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

print(f"Wrote {len(simulated_rows)} simulation rows to {simulation_path}")
print(f"Wrote {len(summary_rows)} summary rows to {summary_path}")
