#!/usr/bin/env python3
"""
Professional testing and validation decision-support engine.

This script compares design concepts across desirability, feasibility, viability,
responsibility, friction, residual risk, evidence quality, stakeholder coverage,
and method triangulation. It supports scenario analysis, Monte Carlo uncertainty,
bootstrap stability, random-weight sensitivity, iteration learning curves,
decision-threshold checks, and risk-register priority scoring.

The model is intentionally interpretable:

    V_i = w_d D_i + w_f F_i + w_v Vi_i + w_s S_i - w_r R_i

where:
    D_i  = desirability
    F_i  = feasibility
    Vi_i = viability
    S_i  = responsibility or safety
    R_i  = combined friction / residual risk

This script supports professional design research documentation. It does not
automate validation or replace ethical, operational, accessibility, or stakeholder review.
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


CORE_WEIGHTS = [
    "desirability",
    "feasibility",
    "viability",
    "responsibility",
    "risk_penalty",
]

SCORE_COLUMNS = [
    "desirability",
    "feasibility",
    "viability",
    "responsibility",
    "friction",
    "residual_risk",
]

SIGNAL_COLUMNS = [
    "evidence_quality",
    "stakeholder_coverage",
    "method_triangulation",
    "equity_signal",
    "accessibility_signal",
    "operational_signal",
]


@dataclass(frozen=True)
class EngineConfig:
    concepts_path: Path
    weights_path: Path | None
    rounds_path: Path | None
    thresholds_path: Path | None
    risk_register_path: Path | None
    output_dir: Path
    simulations: int
    seed: int
    score_sd: float
    bootstrap_iterations: int
    sensitivity_samples: int


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    field: str
    message: str


def read_concepts(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Concept file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "concept",
        "prototype_type",
        "fidelity_level",
        *SCORE_COLUMNS,
        *SIGNAL_COLUMNS,
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Concept file missing required columns: {missing}")

    df = df.copy()
    for col in ["concept", "prototype_type", "fidelity_level"]:
        df[col] = df[col].astype(str).str.strip()

    for col in SCORE_COLUMNS + SIGNAL_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_weights(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame(
            [
                {
                    "scenario": "Balanced",
                    "desirability": 0.25,
                    "feasibility": 0.20,
                    "viability": 0.20,
                    "responsibility": 0.20,
                    "risk_penalty": 0.15,
                }
            ]
        )

    df = pd.read_csv(path)
    required = ["scenario", *CORE_WEIGHTS]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Weights file missing required columns: {missing}")

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


def validate_concepts(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["concept"].duplicated().any():
        issues.append(
            ValidationIssue(
                level="error",
                field="concept",
                message="Duplicate concept names detected.",
            )
        )

    for col in SCORE_COLUMNS + ["equity_signal", "accessibility_signal", "operational_signal"]:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    for col in ["evidence_quality", "stakeholder_coverage", "method_triangulation"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Evidence-style indicators should be in [0, 1].",
                )
            )

    if len(df) < 3:
        issues.append(
            ValidationIssue(
                level="warning",
                field="concept",
                message="Fewer than three concepts limits portfolio comparison.",
            )
        )

    return issues


def compute_validation_value(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    result = df.copy()

    result["combined_risk"] = 0.50 * result["friction"] + 0.50 * result["residual_risk"]

    result["validation_value"] = (
        weights["desirability"] * result["desirability"]
        + weights["feasibility"] * result["feasibility"]
        + weights["viability"] * result["viability"]
        + weights["responsibility"] * result["responsibility"]
        - weights["risk_penalty"] * result["combined_risk"]
    )

    result["evidence_confidence_index"] = (
        0.45 * result["evidence_quality"]
        + 0.35 * result["stakeholder_coverage"]
        + 0.20 * result["method_triangulation"]
    )

    result["confidence_adjusted_value"] = (
        result["validation_value"] * (0.75 + 0.25 * result["evidence_confidence_index"])
    )

    result["equity_access_index"] = (
        0.50 * result["equity_signal"]
        + 0.35 * result["accessibility_signal"]
        + 0.15 * result["stakeholder_coverage"] * 10.0
    )

    result["implementation_readiness"] = (
        0.30 * result["feasibility"]
        + 0.25 * result["viability"]
        + 0.20 * result["operational_signal"]
        + 0.15 * result["confidence_adjusted_value"]
        - 0.10 * result["combined_risk"]
    )

    result["validation_review_priority"] = (
        0.30 * result["residual_risk"]
        + 0.25 * result["friction"]
        + 0.15 * (1.0 - result["evidence_quality"]) * 10.0
        + 0.15 * (1.0 - result["stakeholder_coverage"]) * 10.0
        + 0.15 * (10.0 - result["responsibility"])
    )

    result["advance_readiness"] = (
        0.35 * result["confidence_adjusted_value"]
        + 0.25 * result["implementation_readiness"]
        + 0.20 * result["equity_access_index"]
        + 0.10 * result["method_triangulation"] * 10.0
        - 0.10 * result["validation_review_priority"]
    )

    result = result.sort_values("validation_value", ascending=False).reset_index(drop=True)
    result["rank"] = np.arange(1, len(result) + 1)

    return result


def run_scenario_analysis(concepts: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_WEIGHTS}
        scored = compute_validation_value(concepts, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_WEIGHTS:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def analyze_rounds(rounds: pd.DataFrame | None) -> pd.DataFrame:
    if rounds is None:
        return pd.DataFrame()

    required = [
        "concept",
        "round",
        "adoption_likelihood",
        "comprehension",
        "trust",
        "observed_friction",
        "task_success_rate",
        "error_rate",
        "mean_time_minutes",
        "critical_issue_count",
        "participant_count",
    ]
    missing = [col for col in required if col not in rounds.columns]
    if missing:
        raise ValueError(f"Testing rounds file missing required columns: {missing}")

    df = rounds.copy()
    for col in required:
        if col != "concept":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["concept", "round"])
    df["adoption_delta"] = df.groupby("concept")["adoption_likelihood"].diff()
    df["comprehension_delta"] = df.groupby("concept")["comprehension"].diff()
    df["trust_delta"] = df.groupby("concept")["trust"].diff()
    df["friction_delta"] = df.groupby("concept")["observed_friction"].diff()
    df["task_success_delta"] = df.groupby("concept")["task_success_rate"].diff()
    df["error_delta"] = df.groupby("concept")["error_rate"].diff()
    df["critical_issue_delta"] = df.groupby("concept")["critical_issue_count"].diff()

    df["learning_quality_delta"] = (
        0.25 * df["adoption_delta"].fillna(0)
        + 0.25 * df["comprehension_delta"].fillna(0)
        + 0.25 * df["trust_delta"].fillna(0)
        - 0.20 * df["friction_delta"].fillna(0)
        - 0.05 * (df["critical_issue_delta"].fillna(0))
    )

    summary = (
        df.groupby("concept")
        .agg(
            rounds=("round", "max"),
            start_adoption=("adoption_likelihood", "first"),
            final_adoption=("adoption_likelihood", "last"),
            start_comprehension=("comprehension", "first"),
            final_comprehension=("comprehension", "last"),
            start_trust=("trust", "first"),
            final_trust=("trust", "last"),
            start_friction=("observed_friction", "first"),
            final_friction=("observed_friction", "last"),
            start_task_success=("task_success_rate", "first"),
            final_task_success=("task_success_rate", "last"),
            start_error_rate=("error_rate", "first"),
            final_error_rate=("error_rate", "last"),
            start_critical_issues=("critical_issue_count", "first"),
            final_critical_issues=("critical_issue_count", "last"),
            total_learning_quality_delta=("learning_quality_delta", "sum"),
            participant_count=("participant_count", "sum"),
        )
        .reset_index()
    )

    summary["adoption_improvement"] = summary["final_adoption"] - summary["start_adoption"]
    summary["comprehension_improvement"] = summary["final_comprehension"] - summary["start_comprehension"]
    summary["trust_improvement"] = summary["final_trust"] - summary["start_trust"]
    summary["friction_reduction"] = summary["start_friction"] - summary["final_friction"]
    summary["task_success_improvement"] = summary["final_task_success"] - summary["start_task_success"]
    summary["error_reduction"] = summary["start_error_rate"] - summary["final_error_rate"]
    summary["critical_issue_reduction"] = summary["start_critical_issues"] - summary["final_critical_issues"]

    return summary.sort_values("total_learning_quality_delta", ascending=False)


def analyze_thresholds(rounds: pd.DataFrame | None, thresholds: pd.DataFrame | None) -> pd.DataFrame:
    if rounds is None or thresholds is None:
        return pd.DataFrame()

    latest = rounds.sort_values(["concept", "round"]).groupby("concept").tail(1).copy()
    records = []

    for _, threshold in thresholds.iterrows():
        metric = str(threshold["metric"])
        if metric not in latest.columns:
            continue

        direction = str(threshold["threshold_direction"])
        value = float(threshold["threshold_value"])
        implication = str(threshold["decision_implication"])

        for _, row in latest.iterrows():
            observed = float(row[metric])
            if direction == "greater_or_equal":
                passed = observed >= value
            elif direction == "less_or_equal":
                passed = observed <= value
            else:
                passed = False

            records.append(
                {
                    "concept": row["concept"],
                    "metric": metric,
                    "observed_value": observed,
                    "threshold_direction": direction,
                    "threshold_value": value,
                    "passed_threshold": bool(passed),
                    "decision_implication": implication,
                }
            )

    result = pd.DataFrame(records)
    if result.empty:
        return result

    summary = (
        result.groupby("concept")
        .agg(
            thresholds_evaluated=("metric", "count"),
            thresholds_passed=("passed_threshold", "sum"),
        )
        .reset_index()
    )
    summary["threshold_pass_rate"] = summary["thresholds_passed"] / summary["thresholds_evaluated"]

    return result.merge(summary, on="concept", how="left").sort_values(
        ["threshold_pass_rate", "concept"], ascending=[False, True]
    )


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "concept",
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
    concepts: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    winner_counts: Counter[str] = Counter()
    records: List[dict] = []

    means = concepts[SCORE_COLUMNS].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated = concepts.copy()
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)
        simulated[SCORE_COLUMNS] = simulated_scores

        scored = compute_validation_value(simulated, weights)
        winner_counts[str(scored.iloc[0]["concept"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "concept": row["concept"],
                    "prototype_type": row["prototype_type"],
                    "validation_value": float(row["validation_value"]),
                    "confidence_adjusted_value": float(row["confidence_adjusted_value"]),
                    "validation_review_priority": float(row["validation_review_priority"]),
                    "advance_readiness": float(row["advance_readiness"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "concept": concept,
                    "times_ranked_first": count,
                    "probability_ranked_first": count / simulations,
                }
                for concept, count in winner_counts.items()
            ]
        )
        .sort_values("probability_ranked_first", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_stability(
    concepts: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = concepts.sample(
            n=len(concepts),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = compute_validation_value(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "concept": row["concept"],
                    "validation_value": float(row["validation_value"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("concept")
        .agg(
            mean_validation_value=("validation_value", "mean"),
            sd_validation_value=("validation_value", "std"),
            median_rank=("rank", "median"),
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
        )
        .reset_index()
        .sort_values(["median_rank", "mean_rank"])
    )


def random_weight_sensitivity(
    concepts: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()

    for _ in range(samples):
        arr = rng.dirichlet(np.ones(len(CORE_WEIGHTS)))
        weights = dict(zip(CORE_WEIGHTS, arr))
        scored = compute_validation_value(concepts, weights)
        winner_counts[str(scored.iloc[0]["concept"])] += 1

    return (
        pd.DataFrame(
            [
                {
                    "concept": concept,
                    "times_won": count,
                    "probability_winning_under_random_weights": count / samples,
                }
                for concept, count in winner_counts.items()
            ]
        )
        .sort_values("probability_winning_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="concept",
        columns="scenario",
        values="validation_value",
        aggfunc="first",
    )
    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("Testing and Validation Value Across Scenarios")
    ax.set_xlabel("Concept")
    ax.set_ylabel("Weighted validation value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["concept"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for Validation Decisions")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Concept")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_iteration(iteration_summary: pd.DataFrame, output_path: Path) -> None:
    if iteration_summary.empty:
        return
    plot_df = iteration_summary.sort_values("total_learning_quality_delta", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["concept"], plot_df["total_learning_quality_delta"])
    plt.title("Testing Round Learning Quality Improvement")
    plt.xlabel("Total learning quality delta")
    plt.ylabel("Concept")
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
    concepts: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    iteration_summary: pd.DataFrame,
    threshold_results: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    balanced = scenario_results[scenario_results["scenario"].str.lower() == "balanced"]
    top = balanced.sort_values("rank").head(1)
    top_name = top.iloc[0]["concept"] if not top.empty else "Not available"
    top_value = float(top.iloc[0]["validation_value"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    iteration_section = "No iteration-round data provided."
    if not iteration_summary.empty:
        iteration_section = dataframe_to_markdown_safe(iteration_summary)

    threshold_section = "No decision-threshold data provided."
    if not threshold_results.empty:
        threshold_section = dataframe_to_markdown_safe(threshold_results)

    risk_section = "No risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Testing and Validation Decision-Support Report

## Article

Testing and Validation in Design Thinking

## Summary

This report compares tested design concepts using transparent multi-criteria validation scoring, scenario analysis, uncertainty modeling, iteration learning curves, decision-threshold review, risk-register priority, bootstrap stability, and random-weight sensitivity.

## Balanced scenario leader

- Concept: **{top_name}**
- Weighted validation value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_d D_i + w_f F_i + w_v Vi_i + w_s S_i - w_r R_i
\\]

## Concepts evaluated

{len(concepts)}

## Scenarios evaluated

{len(scenarios)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Iteration learning summary

{iteration_section}

## Decision-threshold review

{threshold_section}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate validation. They support structured deliberation about evidence strength, uncertainty, stakeholder coverage, risk, and next-step decisions. A high-scoring concept may still require additional accessibility testing, equity review, operational testing, ethical review, technical review, or governance approval before it advances.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional testing and validation engine.")
    parser.add_argument(
        "--concepts",
        type=Path,
        default=Path("../data/raw/validation_concepts_raw.csv"),
        help="Validation concepts CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/validation_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--rounds",
        type=Path,
        default=Path("../data/raw/testing_rounds_raw.csv"),
        help="Testing rounds CSV.",
    )
    parser.add_argument(
        "--thresholds",
        type=Path,
        default=Path("../data/raw/decision_thresholds_raw.csv"),
        help="Decision thresholds CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/validation_risk_register_raw.csv"),
        help="Validation risk register CSV.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.6)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        concepts_path=args.concepts,
        weights_path=args.weights if args.weights.exists() else None,
        rounds_path=args.rounds if args.rounds.exists() else None,
        thresholds_path=args.thresholds if args.thresholds.exists() else None,
        risk_register_path=args.risk_register if args.risk_register.exists() else None,
        output_dir=args.output_dir,
        simulations=args.simulations,
        seed=args.seed,
        score_sd=args.score_sd,
        bootstrap_iterations=args.bootstrap_iterations,
        sensitivity_samples=args.sensitivity_samples,
    )


def main(argv: List[str] | None = None) -> int:
    config = parse_args(argv or sys.argv[1:])
    config.output_dir.mkdir(parents=True, exist_ok=True)

    concepts = read_concepts(config.concepts_path)
    scenarios = read_weights(config.weights_path)
    rounds = read_optional_csv(config.rounds_path)
    thresholds = read_optional_csv(config.thresholds_path)
    risk_register = read_optional_csv(config.risk_register_path)

    issues = validate_concepts(concepts)
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

    scenario_results = run_scenario_analysis(concepts, scenarios)
    iteration_summary = analyze_rounds(rounds)
    threshold_results = analyze_thresholds(rounds, thresholds)
    risk_summary = analyze_risk_register(risk_register)

    winners, simulation_values = monte_carlo_rank_stability(
        concepts=concepts,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap = bootstrap_stability(
        concepts=concepts,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        concepts=concepts,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    review_priority = (
        compute_validation_value(concepts, balanced_weights)
        .sort_values("validation_review_priority", ascending=False)
        [
            [
                "concept",
                "prototype_type",
                "fidelity_level",
                "validation_value",
                "confidence_adjusted_value",
                "validation_review_priority",
                "advance_readiness",
                "equity_access_index",
                "implementation_readiness",
            ]
        ]
    )

    scenario_results.to_csv(config.output_dir / "validation_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "validation_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "validation_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "validation_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "validation_weight_sensitivity.csv", index=False)
    review_priority.to_csv(config.output_dir / "validation_review_priority.csv", index=False)

    if not iteration_summary.empty:
        iteration_summary.to_csv(config.output_dir / "testing_iteration_summary.csv", index=False)

    if not threshold_results.empty:
        threshold_results.to_csv(config.output_dir / "decision_threshold_results.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "validation_risk_register_priority.csv", index=False)

    save_plot_scenario_values(scenario_results, config.output_dir / "validation_scenario_values.png")
    save_plot_rank_stability(winners, config.output_dir / "validation_rank_stability.png")
    save_plot_iteration(iteration_summary, config.output_dir / "testing_iteration_learning_delta.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "concepts_path": str(config.concepts_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "rounds_path": str(config.rounds_path) if config.rounds_path else None,
                "thresholds_path": str(config.thresholds_path) if config.thresholds_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "score_columns": SCORE_COLUMNS,
        },
    )

    report = build_report(
        concepts=concepts,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        iteration_summary=iteration_summary,
        threshold_results=threshold_results,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "testing_validation_decision_report.md").write_text(report, encoding="utf-8")

    print("Testing and validation analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- validation_scenario_results.csv")
    print("- validation_monte_carlo_winners.csv")
    print("- validation_weight_sensitivity.csv")
    print("- testing_iteration_summary.csv")
    print("- decision_threshold_results.csv")
    print("- validation_review_priority.csv")
    print("- testing_validation_decision_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
