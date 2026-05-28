#!/usr/bin/env python3
"""
Professional design evaluation, learning, and outcome-measurement engine.

This script compares design interventions across outcome improvement, burden
reduction, equity performance, trust improvement, durability, operational cost,
residual risk, evidence quality, stakeholder coverage, method triangulation,
and uncertainty. It also analyzes outcome time series, learning agendas,
risk-register priority, Monte Carlo uncertainty, bootstrap stability, and
random-weight sensitivity.

The model is intentionally interpretable:

    V_i = w_o O_i + w_b B_i + w_e E_i + w_t T_i + w_d D_i - w_p P_i

where:
    O_i = outcome improvement
    B_i = burden reduction
    E_i = equity performance
    T_i = trust improvement
    D_i = durability
    P_i = penalty from operational cost and residual risk

This workflow supports professional evaluation deliberation and documentation.
It does not automate evaluation conclusions or replace governance, stakeholder,
ethical, equity, privacy, domain, or implementation review.
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
    "outcome_improvement",
    "burden_reduction",
    "equity_performance",
    "trust_improvement",
    "durability",
]

PENALTY_COMPONENTS = [
    "operational_cost",
    "residual_risk",
]

EVIDENCE_COMPONENTS = [
    "evidence_quality",
    "stakeholder_coverage",
    "method_triangulation",
]

CORE_WEIGHTS = [*POSITIVE_CRITERIA, "penalty"]


@dataclass(frozen=True)
class EngineConfig:
    portfolio_path: Path
    weights_path: Path | None
    outcomes_path: Path | None
    learning_agenda_path: Path | None
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


def read_portfolio(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Evaluation portfolio file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "intervention",
        "intervention_type",
        "evaluation_stage",
        *POSITIVE_CRITERIA,
        *PENALTY_COMPONENTS,
        *EVIDENCE_COMPONENTS,
        "uncertainty",
        "baseline_quality",
        "current_quality",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Evaluation portfolio missing required columns: {missing}")

    df = df.copy()
    for col in ["intervention", "intervention_type", "evaluation_stage"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = (
        POSITIVE_CRITERIA
        + PENALTY_COMPONENTS
        + EVIDENCE_COMPONENTS
        + ["uncertainty", "baseline_quality", "current_quality"]
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
                    "outcome_improvement": 0.24,
                    "burden_reduction": 0.20,
                    "equity_performance": 0.20,
                    "trust_improvement": 0.16,
                    "durability": 0.14,
                    "penalty": 0.06,
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

    for col in POSITIVE_CRITERIA + PENALTY_COMPONENTS + ["baseline_quality", "current_quality"]:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    for col in EVIDENCE_COMPONENTS + ["uncertainty"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Evidence and uncertainty indicators should be in [0, 1].",
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


def compute_penalty(df: pd.DataFrame) -> pd.Series:
    return 0.50 * df["operational_cost"] + 0.50 * df["residual_risk"]


def score_interventions(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["penalty"] = compute_penalty(scored)
    scored["quality_delta"] = scored["current_quality"] - scored["baseline_quality"]

    scored["evaluation_value"] = (
        weights["outcome_improvement"] * scored["outcome_improvement"]
        + weights["burden_reduction"] * scored["burden_reduction"]
        + weights["equity_performance"] * scored["equity_performance"]
        + weights["trust_improvement"] * scored["trust_improvement"]
        + weights["durability"] * scored["durability"]
        - weights["penalty"] * scored["penalty"]
    )

    scored["evidence_strength"] = (
        0.40 * scored["evidence_quality"]
        + 0.35 * scored["stakeholder_coverage"]
        + 0.25 * scored["method_triangulation"]
        - 0.20 * scored["uncertainty"]
    ).clip(lower=0.0, upper=1.0)

    scored["evidence_adjusted_value"] = (
        scored["evaluation_value"] * (0.75 + 0.25 * scored["evidence_strength"])
    )

    scored["learning_priority"] = (
        0.25 * scored["residual_risk"]
        + 0.20 * (1.0 - scored["evidence_quality"]) * 10.0
        + 0.18 * (1.0 - scored["stakeholder_coverage"]) * 10.0
        + 0.16 * scored["operational_cost"]
        + 0.13 * (1.0 - scored["method_triangulation"]) * 10.0
        + 0.08 * scored["uncertainty"] * 10.0
    )

    scored["accountability_index"] = (
        0.25 * scored["equity_performance"]
        + 0.20 * scored["trust_improvement"]
        + 0.20 * scored["evidence_strength"] * 10.0
        + 0.20 * scored["burden_reduction"]
        + 0.15 * scored["durability"]
        - 0.10 * scored["penalty"]
    )

    scored["learning_value"] = (
        0.35 * scored["quality_delta"]
        + 0.30 * scored["evidence_strength"] * 10.0
        + 0.20 * scored["evaluation_value"]
        - 0.15 * scored["learning_priority"]
    )

    scored = scored.sort_values("evaluation_value", ascending=False).reset_index(drop=True)
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


def analyze_outcomes(outcomes: pd.DataFrame | None) -> pd.DataFrame:
    if outcomes is None:
        return pd.DataFrame()

    required = [
        "intervention",
        "period",
        "outcome_score",
        "burden_score",
        "equity_gap",
        "trust_score",
        "reliability_score",
        "staff_burden",
        "support_ticket_rate",
        "complaint_rate",
        "users_reached",
    ]
    missing = [col for col in required if col not in outcomes.columns]
    if missing:
        raise ValueError(f"Outcome timeseries missing required columns: {missing}")

    df = outcomes.copy()
    for col in required:
        if col != "intervention":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["intervention", "period"])
    df["outcome_delta"] = df.groupby("intervention")["outcome_score"].diff()
    df["burden_delta"] = df.groupby("intervention")["burden_score"].diff()
    df["equity_gap_delta"] = df.groupby("intervention")["equity_gap"].diff()
    df["trust_delta"] = df.groupby("intervention")["trust_score"].diff()
    df["reliability_delta"] = df.groupby("intervention")["reliability_score"].diff()
    df["staff_burden_delta"] = df.groupby("intervention")["staff_burden"].diff()
    df["ticket_delta"] = df.groupby("intervention")["support_ticket_rate"].diff()
    df["complaint_delta"] = df.groupby("intervention")["complaint_rate"].diff()

    df["learning_quality_delta"] = (
        0.25 * df["outcome_delta"].fillna(0.0)
        - 0.18 * df["burden_delta"].fillna(0.0)
        - 0.18 * df["equity_gap_delta"].fillna(0.0) * 10.0
        + 0.18 * df["trust_delta"].fillna(0.0)
        + 0.13 * df["reliability_delta"].fillna(0.0) * 10.0
        - 0.04 * df["staff_burden_delta"].fillna(0.0)
        - 0.02 * df["ticket_delta"].fillna(0.0) * 10.0
        - 0.02 * df["complaint_delta"].fillna(0.0) * 10.0
    )

    summary = (
        df.groupby("intervention")
        .agg(
            periods=("period", "max"),
            start_outcome=("outcome_score", "first"),
            final_outcome=("outcome_score", "last"),
            start_burden=("burden_score", "first"),
            final_burden=("burden_score", "last"),
            start_equity_gap=("equity_gap", "first"),
            final_equity_gap=("equity_gap", "last"),
            start_trust=("trust_score", "first"),
            final_trust=("trust_score", "last"),
            start_reliability=("reliability_score", "first"),
            final_reliability=("reliability_score", "last"),
            start_staff_burden=("staff_burden", "first"),
            final_staff_burden=("staff_burden", "last"),
            start_ticket_rate=("support_ticket_rate", "first"),
            final_ticket_rate=("support_ticket_rate", "last"),
            start_complaint_rate=("complaint_rate", "first"),
            final_complaint_rate=("complaint_rate", "last"),
            final_users_reached=("users_reached", "last"),
            total_learning_quality_delta=("learning_quality_delta", "sum"),
        )
        .reset_index()
    )

    summary["outcome_improvement"] = summary["final_outcome"] - summary["start_outcome"]
    summary["burden_reduction"] = summary["start_burden"] - summary["final_burden"]
    summary["equity_gap_reduction"] = summary["start_equity_gap"] - summary["final_equity_gap"]
    summary["trust_improvement"] = summary["final_trust"] - summary["start_trust"]
    summary["reliability_improvement"] = summary["final_reliability"] - summary["start_reliability"]
    summary["staff_burden_reduction"] = summary["start_staff_burden"] - summary["final_staff_burden"]
    summary["support_ticket_reduction"] = summary["start_ticket_rate"] - summary["final_ticket_rate"]
    summary["complaint_reduction"] = summary["start_complaint_rate"] - summary["final_complaint_rate"]

    return summary.sort_values("total_learning_quality_delta", ascending=False)


def analyze_learning_agenda(agenda: pd.DataFrame | None, portfolio: pd.DataFrame) -> pd.DataFrame:
    if agenda is None:
        return pd.DataFrame()

    required = [
        "learning_question",
        "claim_type",
        "primary_metric",
        "secondary_metric",
        "decision_use",
        "evidence_source",
        "review_cadence",
    ]
    missing = [col for col in required if col not in agenda.columns]
    if missing:
        raise ValueError(f"Learning agenda missing required columns: {missing}")

    available_metrics = set(portfolio.columns)
    records = []

    for _, row in agenda.iterrows():
        primary = str(row["primary_metric"])
        secondary = str(row["secondary_metric"])
        records.append(
            {
                "learning_question": row["learning_question"],
                "claim_type": row["claim_type"],
                "primary_metric": primary,
                "primary_metric_available": primary in available_metrics,
                "secondary_metric": secondary,
                "secondary_metric_available": secondary in available_metrics,
                "decision_use": row["decision_use"],
                "evidence_source": row["evidence_source"],
                "review_cadence": row["review_cadence"],
            }
        )

    return pd.DataFrame(records)


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

    score_columns = POSITIVE_CRITERIA + PENALTY_COMPONENTS
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
                    "evaluation_value": float(row["evaluation_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "evidence_strength": float(row["evidence_strength"]),
                    "learning_priority": float(row["learning_priority"]),
                    "accountability_index": float(row["accountability_index"]),
                    "learning_value": float(row["learning_value"]),
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
                    "evaluation_value": float(row["evaluation_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "learning_priority": float(row["learning_priority"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("intervention")
        .agg(
            mean_evaluation_value=("evaluation_value", "mean"),
            sd_evaluation_value=("evaluation_value", "std"),
            mean_evidence_adjusted_value=("evidence_adjusted_value", "mean"),
            mean_learning_priority=("learning_priority", "mean"),
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
        values="evaluation_value",
        aggfunc="first",
    )
    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("Design Evaluation Value Across Learning Scenarios")
    ax.set_xlabel("Intervention")
    ax.set_ylabel("Weighted evaluation value")
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
    plt.title("Monte Carlo Rank Stability for Evaluation Conclusions")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Intervention")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_outcome_learning(outcome_summary: pd.DataFrame, output_path: Path) -> None:
    if outcome_summary.empty:
        return

    plot_df = outcome_summary.sort_values("total_learning_quality_delta", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["intervention"], plot_df["total_learning_quality_delta"])
    plt.title("Outcome Learning Delta Across Evaluation Periods")
    plt.xlabel("Total learning quality delta")
    plt.ylabel("Intervention")
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
    outcome_summary: pd.DataFrame,
    learning_agenda_review: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    balanced = scenario_results[scenario_results["scenario"].str.lower() == "balanced"]
    top = balanced.sort_values("rank").head(1)
    top_name = top.iloc[0]["intervention"] if not top.empty else "Not available"
    top_value = float(top.iloc[0]["evaluation_value"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    outcome_section = "No outcome time-series data provided."
    if not outcome_summary.empty:
        outcome_section = dataframe_to_markdown_safe(outcome_summary)

    agenda_section = "No learning agenda data provided."
    if not learning_agenda_review.empty:
        agenda_section = dataframe_to_markdown_safe(learning_agenda_review)

    risk_section = "No risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Design Evaluation, Learning, and Outcome Measurement Report

## Article

Design Evaluation, Learning, and Outcome Measurement

## Summary

This report compares design interventions using transparent outcome-measurement scoring, scenario analysis, evidence-strength diagnostics, learning-priority review, outcome time-series analysis, uncertainty modeling, risk-register review, bootstrap stability, and random-weight sensitivity.

## Balanced scenario leader

- Intervention: **{top_name}**
- Weighted evaluation value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_o O_i + w_b B_i + w_e E_i + w_t T_i + w_d D_i - w_p P_i
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

## Outcome learning summary

{outcome_section}

## Learning agenda review

{agenda_section}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate evaluation conclusions. They support structured deliberation about outcomes, burden, equity, trust, durability, evidence strength, uncertainty, and learning priorities. A high-scoring intervention may still require additional qualitative review, subgroup analysis, governance review, privacy safeguards, causal assessment, or longitudinal monitoring before stronger outcome claims are made.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional design evaluation and learning engine.")
    parser.add_argument(
        "--portfolio",
        type=Path,
        default=Path("../data/raw/evaluation_portfolio_raw.csv"),
        help="Evaluation portfolio CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/evaluation_scenario_weights.csv"),
        help="Evaluation scenario weights CSV.",
    )
    parser.add_argument(
        "--outcomes",
        type=Path,
        default=Path("../data/raw/outcome_timeseries_raw.csv"),
        help="Outcome time-series CSV.",
    )
    parser.add_argument(
        "--learning-agenda",
        type=Path,
        default=Path("../data/raw/learning_agenda_raw.csv"),
        help="Learning agenda CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/evaluation_risk_register_raw.csv"),
        help="Evaluation risk register CSV.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.55)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        portfolio_path=args.portfolio,
        weights_path=args.weights if args.weights.exists() else None,
        outcomes_path=args.outcomes if args.outcomes.exists() else None,
        learning_agenda_path=args.learning_agenda if args.learning_agenda.exists() else None,
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

    portfolio = read_portfolio(config.portfolio_path)
    scenarios = read_weights(config.weights_path)
    outcomes = read_optional_csv(config.outcomes_path)
    learning_agenda = read_optional_csv(config.learning_agenda_path)
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
    outcome_summary = analyze_outcomes(outcomes)
    learning_agenda_review = analyze_learning_agenda(learning_agenda, portfolio)
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
                "evaluation_stage",
                "evaluation_value",
                "evidence_adjusted_value",
                "evidence_strength",
                "learning_priority",
                "accountability_index",
                "learning_value",
                "quality_delta",
            ]
        ]
    )

    scenario_results.to_csv(config.output_dir / "evaluation_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "evaluation_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "evaluation_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "evaluation_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "evaluation_weight_sensitivity.csv", index=False)
    review_priority.to_csv(config.output_dir / "evaluation_learning_priority.csv", index=False)

    if not outcome_summary.empty:
        outcome_summary.to_csv(config.output_dir / "outcome_learning_summary.csv", index=False)

    if not learning_agenda_review.empty:
        learning_agenda_review.to_csv(config.output_dir / "learning_agenda_review.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "evaluation_risk_register_priority.csv", index=False)

    save_plot_scenario_values(scenario_results, config.output_dir / "evaluation_scenario_values.png")
    save_plot_rank_stability(winners, config.output_dir / "evaluation_rank_stability.png")
    save_plot_outcome_learning(outcome_summary, config.output_dir / "outcome_learning_delta.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "portfolio_path": str(config.portfolio_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "outcomes_path": str(config.outcomes_path) if config.outcomes_path else None,
                "learning_agenda_path": str(config.learning_agenda_path) if config.learning_agenda_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "evidence_components": EVIDENCE_COMPONENTS,
        },
    )

    report = build_report(
        portfolio=portfolio,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        outcome_summary=outcome_summary,
        learning_agenda_review=learning_agenda_review,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "design_evaluation_learning_report.md").write_text(report, encoding="utf-8")

    print("Design evaluation and learning analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- evaluation_scenario_results.csv")
    print("- evaluation_monte_carlo_winners.csv")
    print("- evaluation_weight_sensitivity.csv")
    print("- outcome_learning_summary.csv")
    print("- evaluation_learning_priority.csv")
    print("- design_evaluation_learning_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
