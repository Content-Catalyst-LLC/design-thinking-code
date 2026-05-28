#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

POSITIVE = [
    "expected_behavior_gain", "importance", "equity_reach", "transparency",
    "autonomy_preservation", "trust_effect", "accessibility_effect", "durability"
]
NEGATIVE = ["ethical_risk", "implementation_effort"]
WEIGHTS = POSITIVE + NEGATIVE

@dataclass(frozen=True)
class EngineConfig:
    barriers_path: Path
    interventions_path: Path
    experiments_path: Path | None
    weights_path: Path | None
    risk_register_path: Path | None
    output_dir: Path
    simulations: int
    seed: int
    score_sd: float
    gain_sd: float
    bootstrap_iterations: int
    sensitivity_samples: int

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)

def read_weights(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame([{
            "scenario": "Balanced",
            "expected_behavior_gain": .22, "importance": .14, "equity_reach": .16,
            "transparency": .08, "autonomy_preservation": .08, "trust_effect": .10,
            "accessibility_effect": .10, "durability": .06,
            "ethical_risk": .04, "implementation_effort": .02
        }])
    df = pd.read_csv(path)
    sums = df[WEIGHTS].sum(axis=1)
    if not np.allclose(sums, 1.0, atol=1e-6):
        raise ValueError("Each scenario-weight row must sum to 1.0")
    return df

def score_barriers(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    for col in ["motivation","capability","opportunity","trust","friction","affectedness",
                "time_pressure","cognitive_load","emotional_load","social_support","institutional_risk"]:
        x[col] = pd.to_numeric(x[col], errors="raise")

    m = (x["motivation"] - 5.5) / 2.5
    c = (x["capability"] - 5.5) / 2.5
    o = (x["opportunity"] - 5.5) / 2.5
    t = (x["trust"] - 5.5) / 2.5
    f = (x["friction"] - 5.5) / 2.5

    x["predicted_action_probability"] = sigmoid(-0.15 + .70*m + .72*c + .76*o + .58*t - .88*f)
    x["action_readiness_index"] = .22*x["motivation"] + .22*x["capability"] + .22*x["opportunity"] + .20*x["trust"] - .14*x["friction"]
    x["friction_composition_index"] = .24*x["time_pressure"] + .24*x["cognitive_load"] + .20*x["emotional_load"] + .18*x["friction"] + .14*x["institutional_risk"]
    x["behavioral_gap"] = 10 - x["action_readiness_index"]
    x["affectedness_weighted_gap"] = x["affectedness"] * x["behavioral_gap"]
    x["support_need_index"] = .22*(10-x["capability"]) + .22*(10-x["opportunity"]) + .18*x["cognitive_load"] + .16*x["time_pressure"] + .12*x["emotional_load"] + .10*(10-x["social_support"])
    x["redesign_priority"] = .30*x["affectedness_weighted_gap"] + .22*x["friction"] + .16*(10-x["opportunity"]) + .12*(10-x["trust"]) + .10*(10-x["capability"]) + .10*x["friction_composition_index"]
    return x.sort_values("redesign_priority", ascending=False).reset_index(drop=True)

def score_interventions(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    x = df.copy()
    for col in WEIGHTS:
        x[col] = pd.to_numeric(x[col], errors="raise").clip(0, 1)

    x["intervention_priority"] = (
        weights["expected_behavior_gain"]*x["expected_behavior_gain"] +
        weights["importance"]*x["importance"] +
        weights["equity_reach"]*x["equity_reach"] +
        weights["transparency"]*x["transparency"] +
        weights["autonomy_preservation"]*x["autonomy_preservation"] +
        weights["trust_effect"]*x["trust_effect"] +
        weights["accessibility_effect"]*x["accessibility_effect"] +
        weights["durability"]*x["durability"] -
        weights["ethical_risk"]*x["ethical_risk"] -
        weights["implementation_effort"]*x["implementation_effort"]
    )
    x["intervention_value"] = x["expected_behavior_gain"] * x["importance"] * x["equity_reach"] * (.50 + .50*x["durability"]) - x["ethical_risk"] - .20*x["implementation_effort"]
    x["ethical_quality_index"] = .26*x["transparency"] + .26*x["autonomy_preservation"] + .18*x["equity_reach"] + .16*x["trust_effect"] + .14*x["accessibility_effect"] - .22*x["ethical_risk"]
    x["scale_readiness_index"] = .24*x["expected_behavior_gain"] + .20*x["durability"] + .18*x["trust_effect"] + .16*x["accessibility_effect"] + .12*x["importance"] - .10*x["implementation_effort"]
    x["testing_priority"] = .34*x["expected_behavior_gain"] + .22*x["equity_reach"] + .16*x["importance"] + .12*x["trust_effect"] + .08*x["accessibility_effect"] - .05*x["ethical_risk"] - .03*x["implementation_effort"]
    x = x.sort_values("intervention_priority", ascending=False).reset_index(drop=True)
    x["rank"] = np.arange(1, len(x)+1)
    return x

def scenario_analysis(interventions: pd.DataFrame, weights_df: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, row in weights_df.iterrows():
        weights = {col: float(row[col]) for col in WEIGHTS}
        scored = score_interventions(interventions, weights)
        scored["scenario"] = row["scenario"]
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)

def analyze_experiments(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    x = df.copy()
    numeric = [c for c in x.columns if c not in ["experiment_id","intervention","segment"]]
    for col in numeric:
        x[col] = pd.to_numeric(x[col], errors="raise")
    x["control_rate"] = x["control_successes"] / x["control_n"]
    x["treatment_rate"] = x["treatment_successes"] / x["treatment_n"]
    x["absolute_lift"] = x["treatment_rate"] - x["control_rate"]
    x["relative_lift"] = x["absolute_lift"] / x["control_rate"].replace(0, np.nan)
    x["time_reduction"] = x["mean_completion_time_control"] - x["mean_completion_time_treatment"]
    x["complaint_delta"] = x["complaint_rate_treatment"] - x["complaint_rate_control"]
    x["trust_delta"] = x["trust_score_treatment"] - x["trust_score_control"]
    x["experiment_quality_signal"] = .36*(x["absolute_lift"] > 0).astype(float) + .24*np.clip(x["absolute_lift"]/.15,0,1) + .16*np.clip(x["time_reduction"]/8,0,1) + .14*np.clip(x["trust_delta"]/2,0,1) - .10*np.clip(x["complaint_delta"]/.05,0,1)
    return x.sort_values("experiment_quality_signal", ascending=False)

def analyze_risks(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()
    x = df.copy()
    for col in ["severity","likelihood","detectability"]:
        x[col] = pd.to_numeric(x[col], errors="raise")
    x["risk_priority_number"] = x["severity"] * x["likelihood"] * x["detectability"]
    x["normalized_risk_priority"] = x["risk_priority_number"] / x["risk_priority_number"].max()
    return x.sort_values("risk_priority_number", ascending=False)

def monte_carlo(interventions: pd.DataFrame, weights: Dict[str,float], simulations: int, gain_sd: float, score_sd: float, seed: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    records = []
    winners = Counter()
    score_cols = [c for c in WEIGHTS if c != "expected_behavior_gain"]
    for sid in range(simulations):
        sim = interventions.copy()
        sim["expected_behavior_gain"] = rng.normal(interventions["expected_behavior_gain"], gain_sd).clip(0, .40)
        for col in score_cols:
            sim[col] = rng.normal(interventions[col], score_sd).clip(0, 1)
        scored = score_interventions(sim, weights)
        winners[str(scored.iloc[0]["intervention"])] += 1
        for _, row in scored.iterrows():
            records.append({
                "simulation_id": sid, "intervention": row["intervention"],
                "intervention_priority": row["intervention_priority"],
                "intervention_value": row["intervention_value"],
                "ethical_quality_index": row["ethical_quality_index"],
                "scale_readiness_index": row["scale_readiness_index"],
                "testing_priority": row["testing_priority"], "rank": int(row["rank"])
            })
    winner_df = pd.DataFrame([{"intervention": k, "times_ranked_first": v, "probability_ranked_first": v/simulations} for k,v in winners.items()]).sort_values("probability_ranked_first", ascending=False)
    return winner_df, pd.DataFrame(records)

def bootstrap(interventions: pd.DataFrame, weights: Dict[str,float], iterations: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records = []
    for i in range(iterations):
        sample = interventions.sample(n=len(interventions), replace=True, random_state=int(rng.integers(0, 2**31-1)))
        scored = score_interventions(sample, weights)
        for _, row in scored.iterrows():
            records.append({"iteration": i, "intervention": row["intervention"], "intervention_priority": row["intervention_priority"], "rank": int(row["rank"])})
    b = pd.DataFrame(records)
    return b.groupby("intervention").agg(
        mean_intervention_priority=("intervention_priority","mean"),
        sd_intervention_priority=("intervention_priority","std"),
        median_rank=("rank","median"), mean_rank=("rank","mean"),
        best_rank=("rank","min"), worst_rank=("rank","max")
    ).reset_index().sort_values(["median_rank","mean_rank"])

def random_weight_sensitivity(interventions: pd.DataFrame, samples: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winners = Counter()
    for _ in range(samples):
        arr = rng.dirichlet(np.ones(len(WEIGHTS)))
        weights = dict(zip(WEIGHTS, arr))
        scored = score_interventions(interventions, weights)
        winners[str(scored.iloc[0]["intervention"])] += 1
    return pd.DataFrame([{"intervention": k, "times_won": v, "probability_winning_under_random_weights": v/samples} for k,v in winners.items()]).sort_values("probability_winning_under_random_weights", ascending=False)

def save_barh(df, label, value, title, path):
    plot_df = df.sort_values(value, ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df[label], plot_df[value])
    plt.title(title)
    plt.xlabel(value.replace("_"," ").title())
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()

def parse_args(argv=None) -> EngineConfig:
    p = argparse.ArgumentParser()
    p.add_argument("--barriers", type=Path, default=Path("../data/raw/behavioral_barriers_raw.csv"))
    p.add_argument("--interventions", type=Path, default=Path("../data/raw/behavioral_interventions_raw.csv"))
    p.add_argument("--experiments", type=Path, default=Path("../data/raw/behavioral_experiment_results_raw.csv"))
    p.add_argument("--weights", type=Path, default=Path("../data/raw/behavioral_scenario_weights.csv"))
    p.add_argument("--risk-register", type=Path, default=Path("../data/raw/behavioral_risk_register_raw.csv"))
    p.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    p.add_argument("--simulations", type=int, default=10000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--score-sd", type=float, default=.07)
    p.add_argument("--gain-sd", type=float, default=.025)
    p.add_argument("--bootstrap-iterations", type=int, default=2500)
    p.add_argument("--sensitivity-samples", type=int, default=10000)
    a = p.parse_args(argv)
    return EngineConfig(a.barriers, a.interventions, a.experiments if a.experiments.exists() else None, a.weights if a.weights.exists() else None, a.risk_register if a.risk_register.exists() else None, a.output_dir, a.simulations, a.seed, a.score_sd, a.gain_sd, a.bootstrap_iterations, a.sensitivity_samples)

def main(argv=None) -> int:
    cfg = parse_args(argv)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    barriers_raw = read_csv(cfg.barriers_path)
    interventions_raw = read_csv(cfg.interventions_path)
    weights_df = read_weights(cfg.weights_path)
    experiments_raw = read_csv(cfg.experiments_path) if cfg.experiments_path else None
    risk_raw = read_csv(cfg.risk_register_path) if cfg.risk_register_path else None

    balanced_weights = weights_df[weights_df["scenario"].str.lower() == "balanced"].iloc[0][WEIGHTS].astype(float).to_dict()

    barriers = score_barriers(barriers_raw)
    interventions = score_interventions(interventions_raw, balanced_weights)
    scenarios = scenario_analysis(interventions_raw, weights_df)
    experiments = analyze_experiments(experiments_raw)
    risks = analyze_risks(risk_raw)
    winners, sims = monte_carlo(interventions_raw, balanced_weights, cfg.simulations, cfg.gain_sd, cfg.score_sd, cfg.seed)
    boot = bootstrap(interventions_raw, balanced_weights, cfg.bootstrap_iterations, cfg.seed)
    sens = random_weight_sensitivity(interventions_raw, cfg.sensitivity_samples, cfg.seed)

    outputs = {
        "behavioral_barrier_scores.csv": barriers,
        "behavioral_intervention_balanced_scores.csv": interventions,
        "behavioral_intervention_scenario_results.csv": scenarios,
        "behavioral_experiment_analysis.csv": experiments,
        "behavioral_risk_register_priority.csv": risks,
        "behavioral_intervention_monte_carlo_winners.csv": winners,
        "behavioral_intervention_simulation_records.csv": sims,
        "behavioral_intervention_bootstrap_stability.csv": boot,
        "behavioral_intervention_weight_sensitivity.csv": sens,
    }
    for name, df in outputs.items():
        if df is not None and not df.empty:
            df.to_csv(cfg.output_dir / name, index=False)

    save_barh(barriers, "segment", "redesign_priority", "Behavioral Redesign Priority by Segment", cfg.output_dir / "behavioral_barrier_redesign_priority.png")
    save_barh(interventions, "intervention", "intervention_priority", "Behavioral Intervention Priority", cfg.output_dir / "behavioral_intervention_priority.png")

    report = [
        "# Design Thinking and Behavioral Design Report",
        "",
        "## Top barriers",
        barriers.head(8).to_markdown(index=False),
        "",
        "## Balanced intervention scores",
        interventions.to_markdown(index=False),
        "",
        "## Monte Carlo winners",
        winners.to_markdown(index=False),
        "",
        "## Experiment evidence",
        experiments.to_markdown(index=False) if not experiments.empty else "No experiment data.",
        "",
        "## Risk register",
        risks.to_markdown(index=False) if not risks.empty else "No risk data.",
        "",
        "## Responsible interpretation",
        "These outputs support deliberation about behavioral barriers and intervention choices. They do not automate behavioral targeting or replace ethical review, accessibility review, participatory review, privacy review, or field testing."
    ]
    (cfg.output_dir / "behavioral_design_report.md").write_text("\n".join(report), encoding="utf-8")
    (cfg.output_dir / "analysis_metadata.json").write_text(json.dumps({"config": asdict(cfg), "weights": WEIGHTS}, indent=2, default=str), encoding="utf-8")

    print("Behavioral design analysis complete.")
    print(f"Outputs written to: {cfg.output_dir.resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
