#!/usr/bin/env python3
"""
Professional systems-design decision-support engine.

This script compares design-system interventions across human-centered value,
systemic leverage, feasibility, equity sensitivity, durability, implementation
risk, evidence quality, stakeholder coverage, context complexity, delay
sensitivity, and burden-shift risk. It also analyzes feedback dynamics,
risk-register priority, Monte Carlo uncertainty, bootstrap stability, and
random-weight sensitivity.

The model is intentionally interpretable:

    V_i = w_h H_i + w_s S_i + w_f F_i + w_e E_i + w_d D_i - w_r R_i

where:
    H_i = human-centered value
    S_i = systemic leverage
    F_i = feasibility
    E_i = equity sensitivity
    D_i = durability
    R_i = implementation and unintended-consequence risk

This workflow supports design-system deliberation and documentation. It does
not automate complex-system decisions or replace stakeholder, ethical, policy,
implementation, technical, or governance review.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


POSITIVE_CRITERIA = [
    "human_value",
    "system_leverage",
    "feasibility",
    "equity_sensitivity",
    "durability",
]

CORE_WEIGHTS = [*POSITIVE_CRITERIA, "risk"]


@dataclass(frozen=True)
class EngineConfig:
    portfolio_path: Path
    weights_path: Path | None
    feedback_path: Path | None
    risk_register_path: Path | None
    output_dir: Path
    simulations: int
    seed: int
    score_sd: float
    bootstrap_iterations: int
    sensitivity_samples: int
    delay: int


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    field: str
    message: str


def read_portfolio(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"System intervention portfolio file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "intervention",
        "intervention_type",
        "leverage_level",
        *POSITIVE_CRITERIA,
        "risk",
        "evidence_quality",
        "stakeholder_coverage",
        "context_complexity",
        "delay_sensitivity",
        "burden_shift_risk",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"System intervention portfolio missing required columns: {missing}")

    df = df.copy()
    for col in ["intervention", "intervention_type", "leverage_level"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = (
        POSITIVE_CRITERIA
        + ["risk", "evidence_quality", "stakeholder_coverage", "context_complexity", "delay_sensitivity", "burden_shift_risk"]
    )
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_weights(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame(
            [
                {
                    "scenario": "Balanced",
                    "human_value": 0.24,
                    "system_leverage": 0.26,
                    "feasibility": 0.18,
                    "equity_sensitivity": 0.14,
                    "durability": 0.12,
                    "risk": 0.06,
                }
            ]
        )

    df = pd.read_csv(path)
    required = ["scenario", *CORE_WEIGHTS]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Scenario weights missing required columns: {missing}")

    df = df.copy()
    df["scenario"] = df["scenario"].astype(str).str.strip()

    for col in CORE_WEIGHTS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[CORE_WEIGHTS].isna().any().any():
        raise ValueError("Scenario weights contain missing or non-numeric values.")

    weight_sums = df[CORE_WEIGHTS].sum(axis=1)
    if not np.allclose(weight_sums, 1.0, atol=1e-6):
        raise ValueError("Each scenario weight row must sum to 1.0.")

    return df


def read_optional_csv(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None
    return pd.read_csv(path)


def validate_portfolio(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["intervention"].duplicated().any():
        issues.append(
            ValidationIssue(
                level="error",
                field="intervention",
                message="Duplicate intervention names detected.",
            )
        )

    for col in POSITIVE_CRITERIA + ["risk", "context_complexity", "burden_shift_risk"]:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    for col in ["evidence_quality", "stakeholder_coverage", "delay_sensitivity"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Evidence and sensitivity indicators should be in [0, 1].",
                )
            )

    if len(df) < 3:
        issues.append(
            ValidationIssue(
                level="warning",
                field="intervention",
                message="Fewer than three interventions limits portfolio comparison.",
            )
        )

    return issues


def leverage_depth_score(series: pd.Series) -> pd.Series:
    mapping = {
        "parameter": 1.0,
        "workflow": 2.0,
        "information_flow": 3.0,
        "feedback_loop": 4.0,
        "rule": 5.0,
        "governance": 6.0,
        "infrastructure": 5.0,
        "purpose": 7.0,
        "paradigm": 8.0,
    }
    return series.str.lower().map(mapping).fillna(3.0)


def score_interventions(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["evidence_strength"] = (
        0.55 * scored["evidence_quality"]
        + 0.45 * scored["stakeholder_coverage"]
    ).clip(0.0, 1.0)

    scored["leverage_depth_score"] = leverage_depth_score(scored["leverage_level"])

    scored["system_design_value"] = (
        weights["human_value"] * scored["human_value"]
        + weights["system_leverage"] * scored["system_leverage"]
        + weights["feasibility"] * scored["feasibility"]
        + weights["equity_sensitivity"] * scored["equity_sensitivity"]
        + weights["durability"] * scored["durability"]
        - weights["risk"] * scored["risk"]
    )

    scored["evidence_adjusted_value"] = (
        scored["system_design_value"] * (0.75 + 0.25 * scored["evidence_strength"])
    )

    scored["context_adjusted_value"] = (
        scored["system_design_value"]
        - 0.10 * scored["context_complexity"]
        - 0.08 * scored["delay_sensitivity"] * 10.0
        - 0.06 * scored["burden_shift_risk"]
    )

    scored["learning_priority"] = (
        0.24 * scored["risk"]
        + 0.20 * (1.0 - scored["evidence_quality"]) * 10.0
        + 0.18 * (1.0 - scored["stakeholder_coverage"]) * 10.0
        + 0.14 * scored["context_complexity"]
        + 0.12 * scored["delay_sensitivity"] * 10.0
        + 0.12 * scored["burden_shift_risk"]
    )

    scored["deep_leverage_index"] = (
        0.35 * scored["system_leverage"]
        + 0.20 * scored["leverage_depth_score"]
        + 0.18 * scored["durability"]
        + 0.15 * scored["equity_sensitivity"]
        + 0.12 * scored["evidence_strength"] * 10.0
        - 0.15 * scored["risk"]
    )

    scored["burden_shift_index"] = (
        0.45 * scored["burden_shift_risk"]
        + 0.25 * scored["context_complexity"]
        + 0.20 * scored["delay_sensitivity"] * 10.0
        - 0.10 * scored["equity_sensitivity"]
    )

    scored = scored.sort_values("system_design_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(portfolio: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_WEIGHTS}
        scored = score_interventions(portfolio, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_WEIGHTS:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def analyze_feedback(feedback: pd.DataFrame | None, delay: int) -> pd.DataFrame:
    if feedback is None:
        return pd.DataFrame()

    required = [
        "intervention",
        "period",
        "intervention_intensity",
        "visible_performance",
        "adaptation_pressure",
        "system_burden",
        "equity_gap",
        "trust_score",
        "queue_pressure",
        "implementation_drift",
    ]
    missing = [col for col in required if col not in feedback.columns]
    if missing:
        raise ValueError(f"Feedback dynamics data missing required columns: {missing}")

    df = feedback.copy()
    for col in required:
        if col != "intervention":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["intervention", "period"])

    df["performance_delta"] = df.groupby("intervention")["visible_performance"].diff()
    df["burden_delta"] = df.groupby("intervention")["system_burden"].diff()
    df["equity_gap_delta"] = df.groupby("intervention")["equity_gap"].diff()
    df["trust_delta"] = df.groupby("intervention")["trust_score"].diff()
    df["queue_delta"] = df.groupby("intervention")["queue_pressure"].diff()
    df["drift_delta"] = df.groupby("intervention")["implementation_drift"].diff()

    df["delayed_adaptation"] = (
        df.groupby("intervention")["adaptation_pressure"]
        .shift(delay)
        .fillna(0.0)
    )

    df["feedback_quality_delta"] = (
        0.28 * df["performance_delta"].fillna(0.0)
        - 0.18 * df["burden_delta"].fillna(0.0)
        - 0.18 * df["equity_gap_delta"].fillna(0.0) * 10.0
        + 0.18 * df["trust_delta"].fillna(0.0)
        - 0.08 * df["queue_delta"].fillna(0.0) * 10.0
        - 0.05 * df["drift_delta"].fillna(0.0) * 10.0
        - 0.05 * df["delayed_adaptation"]
    )

    summary = (
        df.groupby("intervention")
        .agg(
            periods=("period", "max"),
            start_performance=("visible_performance", "first"),
            final_performance=("visible_performance", "last"),
            start_burden=("system_burden", "first"),
            final_burden=("system_burden", "last"),
            start_equity_gap=("equity_gap", "first"),
            final_equity_gap=("equity_gap", "last"),
            start_trust=("trust_score", "first"),
            final_trust=("trust_score", "last"),
            start_queue_pressure=("queue_pressure", "first"),
            final_queue_pressure=("queue_pressure", "last"),
            start_drift=("implementation_drift", "first"),
            final_drift=("implementation_drift", "last"),
            mean_adaptation_pressure=("adaptation_pressure", "mean"),
            mean_intervention_intensity=("intervention_intensity", "mean"),
            total_feedback_quality_delta=("feedback_quality_delta", "sum"),
        )
        .reset_index()
    )

    summary["performance_improvement"] = summary["final_performance"] - summary["start_performance"]
    summary["burden_reduction"] = summary["start_burden"] - summary["final_burden"]
    summary["equity_gap_reduction"] = summary["start_equity_gap"] - summary["final_equity_gap"]
    summary["trust_improvement"] = summary["final_trust"] - summary["start_trust"]
    summary["queue_pressure_reduction"] = summary["start_queue_pressure"] - summary["final_queue_pressure"]
    summary["drift_increase"] = summary["final_drift"] - summary["start_drift"]

    return summary.sort_values("total_feedback_quality_delta", ascending=False)


def simulate_delayed_feedback(
    starting_performance: float,
    intervention_intensity: float,
    adaptation_pressure: float,
    alpha: float = 0.65,
    beta: float = 0.40,
    delay: int = 2,
    periods: int = 16,
) -> pd.DataFrame:
    performance = [starting_performance]
    adaptation_history = [0.0 for _ in range(delay)] + [adaptation_pressure]

    for t in range(periods):
        delayed_adaptation = adaptation_history[t] if t < len(adaptation_history) else adaptation_pressure
        next_value = performance[-1] + alpha * intervention_intensity - beta * delayed_adaptation
        next_value = max(0.0, min(10.0, next_value))
        performance.append(next_value)
        adaptation_history.append(min(1.0, adaptation_pressure + 0.02 * t))

    return pd.DataFrame(
        {
            "period": np.arange(0, periods + 1),
            "simulated_performance": performance,
        }
    )


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "intervention",
        "risk_category",
        "risk_description",
        "severity",
        "likelihood",
        "detectability",
        "mitigation_owner",
        "mitigation_status",
    ]
    missing = [col for col in required if col not in risk_register.columns]
    if missing:
        raise ValueError(f"Risk register missing required columns: {missing}")

    df = risk_register.copy()
    for col in ["severity", "likelihood", "detectability"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["risk_priority_number"] = df["severity"] * df["likelihood"] * df["detectability"]
    df["normalized_risk_priority"] = df["risk_priority_number"] / df["risk_priority_number"].max()

    return df.sort_values("risk_priority_number", ascending=False)


def monte_carlo_rank_stability(
    portfolio: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    winner_counts: Counter[str] = Counter()
    records: List[dict] = []

    score_columns = POSITIVE_CRITERIA + ["risk"]
    means = portfolio[score_columns].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated = portfolio.copy()
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)
        simulated[score_columns] = simulated_scores

        scored = score_interventions(simulated, weights)
        winner_counts[str(scored.iloc[0]["intervention"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "intervention": row["intervention"],
                    "intervention_type": row["intervention_type"],
                    "leverage_level": row["leverage_level"],
                    "system_design_value": float(row["system_design_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "context_adjusted_value": float(row["context_adjusted_value"]),
                    "deep_leverage_index": float(row["deep_leverage_index"]),
                    "burden_shift_index": float(row["burden_shift_index"]),
                    "learning_priority": float(row["learning_priority"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "intervention": intervention,
                    "times_ranked_first": count,
                    "probability_ranked_first": count / simulations,
                }
                for intervention, count in winner_counts.items()
            ]
        )
        .sort_values("probability_ranked_first", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_stability(
    portfolio: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = portfolio.sample(
            n=len(portfolio),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_interventions(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "intervention": row["intervention"],
                    "system_design_value": float(row["system_design_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "deep_leverage_index": float(row["deep_leverage_index"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("intervention")
        .agg(
            mean_system_design_value=("system_design_value", "mean"),
            sd_system_design_value=("system_design_value", "std"),
            mean_evidence_adjusted_value=("evidence_adjusted_value", "mean"),
            mean_deep_leverage_index=("deep_leverage_index", "mean"),
            median_rank=("rank", "median"),
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
        )
        .reset_index()
        .sort_values(["median_rank", "mean_rank"])
    )


def random_weight_sensitivity(
    portfolio: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()

    for _ in range(samples):
        arr = rng.dirichlet(np.ones(len(CORE_WEIGHTS)))
        weights = dict(zip(CORE_WEIGHTS, arr))
        scored = score_interventions(portfolio, weights)
        winner_counts[str(scored.iloc[0]["intervention"])] += 1

    return (
        pd.DataFrame(
            [
                {
                    "intervention": intervention,
                    "times_won": count,
                    "probability_winning_under_random_weights": count / samples,
                }
                for intervention, count in winner_counts.items()
            ]
        )
        .sort_values("probability_winning_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="intervention",
        columns="scenario",
        values="system_design_value",
        aggfunc="first",
    )
    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("System Design Value Across Strategic Scenarios")
    ax.set_xlabel("Intervention")
    ax.set_ylabel("Weighted system design value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["intervention"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for System Redesign Choices")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Intervention")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_feedback(feedback_summary: pd.DataFrame, output_path: Path) -> None:
    if feedback_summary.empty:
        return
    plot_df = feedback_summary.sort_values("total_feedback_quality_delta", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["intervention"], plot_df["total_feedback_quality_delta"])
    plt.title("Feedback Quality Delta Across System Interventions")
    plt.xlabel("Total feedback quality delta")
    plt.ylabel("Intervention")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_delayed_feedback(simulated: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(simulated["period"], simulated["simulated_performance"], marker="o")
    plt.title("Delayed Feedback Simulation")
    plt.xlabel("Period")
    plt.ylabel("Simulated system performance")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def dataframe_to_markdown_safe(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except Exception:
        return df.to_string(index=False)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def build_report(
    portfolio: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    feedback_summary: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    balanced = scenario_results[scenario_results["scenario"].str.lower() == "balanced"]
    top = balanced.sort_values("rank").head(1)
    top_name = top.iloc[0]["intervention"] if not top.empty else "Not available"
    top_value = float(top.iloc[0]["system_design_value"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    feedback_section = "No feedback dynamics data provided."
    if not feedback_summary.empty:
        feedback_section = dataframe_to_markdown_safe(feedback_summary)

    risk_section = "No risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Design Thinking and Systems Thinking Report

## Article

Design Thinking and Systems Thinking

## Summary

This report compares system intervention candidates using transparent multi-criteria scoring, scenario analysis, evidence-strength diagnostics, leverage-depth classification, feedback dynamics review, uncertainty modeling, risk-register priority, bootstrap stability, and random-weight sensitivity.

## Balanced scenario leader

- Intervention: **{top_name}**
- Weighted system design value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_h H_i + w_s S_i + w_f F_i + w_e E_i + w_d D_i - w_r R_i
\\]

## Portfolio size

{len(portfolio)}

## Scenario count

{len(scenarios)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Feedback dynamics summary

{feedback_section}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate system-redesign decisions. They support structured deliberation about human-centered value, systemic leverage, feasibility, equity sensitivity, durability, risk, delayed feedback, burden shifts, uncertainty, and evidence strength. A high-scoring intervention may still require additional stakeholder research, system mapping, governance review, ethical review, implementation testing, or longitudinal evaluation before scale.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional design-system intervention engine.")
    parser.add_argument(
        "--portfolio",
        type=Path,
        default=Path("../data/raw/system_intervention_portfolio_raw.csv"),
        help="System intervention portfolio CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/system_design_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--feedback",
        type=Path,
        default=Path("../data/raw/feedback_dynamics_raw.csv"),
        help="Feedback dynamics CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/system_intervention_risk_register_raw.csv"),
        help="System intervention risk register CSV.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.6)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)
    parser.add_argument("--delay", type=int, default=1)

    args = parser.parse_args(argv)

    return EngineConfig(
        portfolio_path=args.portfolio,
        weights_path=args.weights if args.weights.exists() else None,
        feedback_path=args.feedback if args.feedback.exists() else None,
        risk_register_path=args.risk_register if args.risk_register.exists() else None,
        output_dir=args.output_dir,
        simulations=args.simulations,
        seed=args.seed,
        score_sd=args.score_sd,
        bootstrap_iterations=args.bootstrap_iterations,
        sensitivity_samples=args.sensitivity_samples,
        delay=args.delay,
    )


def main(argv: List[str] | None = None) -> int:
    config = parse_args(argv or sys.argv[1:])
    config.output_dir.mkdir(parents=True, exist_ok=True)

    portfolio = read_portfolio(config.portfolio_path)
    scenarios = read_weights(config.weights_path)
    feedback = read_optional_csv(config.feedback_path)
    risk_register = read_optional_csv(config.risk_register_path)

    issues = validate_portfolio(portfolio)
    fatal = [issue for issue in issues if issue.level == "error"]
    if fatal:
        for issue in fatal:
            print(f"ERROR [{issue.field}]: {issue.message}", file=sys.stderr)
        return 2

    balanced_weights = (
        scenarios[scenarios["scenario"].str.lower() == "balanced"]
        .iloc[0][CORE_WEIGHTS]
        .astype(float)
        .to_dict()
    )

    scenario_results = run_scenario_analysis(portfolio, scenarios)
    feedback_summary = analyze_feedback(feedback, delay=config.delay)
    risk_summary = analyze_risk_register(risk_register)

    winners, simulation_values = monte_carlo_rank_stability(
        portfolio=portfolio,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap = bootstrap_stability(
        portfolio=portfolio,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        portfolio=portfolio,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    review_priority = (
        score_interventions(portfolio, balanced_weights)
        .sort_values("learning_priority", ascending=False)
        [
            [
                "intervention",
                "intervention_type",
                "leverage_level",
                "system_design_value",
                "evidence_adjusted_value",
                "context_adjusted_value",
                "deep_leverage_index",
                "burden_shift_index",
                "learning_priority",
            ]
        ]
    )

    delayed_feedback = simulate_delayed_feedback(
        starting_performance=6.5,
        intervention_intensity=0.75,
        adaptation_pressure=0.36,
        delay=max(config.delay, 1),
    )

    scenario_results.to_csv(config.output_dir / "system_design_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "system_design_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "system_design_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "system_design_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "system_design_weight_sensitivity.csv", index=False)
    review_priority.to_csv(config.output_dir / "system_design_learning_priority.csv", index=False)
    delayed_feedback.to_csv(config.output_dir / "delayed_feedback_simulation.csv", index=False)

    if not feedback_summary.empty:
        feedback_summary.to_csv(config.output_dir / "feedback_dynamics_summary.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "system_intervention_risk_register_priority.csv", index=False)

    save_plot_scenario_values(scenario_results, config.output_dir / "system_design_scenario_values.png")
    save_plot_rank_stability(winners, config.output_dir / "system_design_rank_stability.png")
    save_plot_feedback(feedback_summary, config.output_dir / "feedback_quality_delta.png")
    save_plot_delayed_feedback(delayed_feedback, config.output_dir / "delayed_feedback_simulation.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "portfolio_path": str(config.portfolio_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "feedback_path": str(config.feedback_path) if config.feedback_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "model": "V_i = w_h H_i + w_s S_i + w_f F_i + w_e E_i + w_d D_i - w_r R_i",
        },
    )

    report = build_report(
        portfolio=portfolio,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        feedback_summary=feedback_summary,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "design_system_intervention_report.md").write_text(report, encoding="utf-8")

    print("Design-system intervention analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- system_design_scenario_results.csv")
    print("- system_design_monte_carlo_winners.csv")
    print("- system_design_weight_sensitivity.csv")
    print("- feedback_dynamics_summary.csv")
    print("- system_design_learning_priority.csv")
    print("- design_system_intervention_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
