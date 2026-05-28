#!/usr/bin/env python3
"""
Professional implementation and scaling decision-support engine.

This script compares deployment candidates across adoption readiness, operational
fit, durability, governance readiness, equity readiness, financial sustainability,
and composite implementation risk. It also analyzes rollout-stage metrics,
scale degradation, risk-register priority, Monte Carlo uncertainty, bootstrap
stability, and random-weight sensitivity.

The model is intentionally interpretable:

    V_i = w_a A_i + w_o O_i + w_d D_i + w_g G_i + w_e E_i + w_f F_i - w_r R_i

where:
    A_i = adoption readiness
    O_i = operational fit
    D_i = durability
    G_i = governance readiness
    E_i = equity readiness
    F_i = financial sustainability
    R_i = composite implementation risk

This workflow supports implementation deliberation and documentation. It should
not automate scale decisions or replace governance, stakeholder, ethical,
technical, operational, or equity review.
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
    "adoption_readiness",
    "operational_fit",
    "durability",
    "governance_readiness",
    "equity_readiness",
    "financial_sustainability",
]

RISK_COMPONENTS = [
    "operational_risk",
    "governance_risk",
    "technical_risk",
    "equity_risk",
    "financial_risk",
]

CORE_WEIGHTS = [*POSITIVE_CRITERIA, "composite_risk"]


@dataclass(frozen=True)
class EngineConfig:
    portfolio_path: Path
    weights_path: Path | None
    rollout_path: Path | None
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
        raise FileNotFoundError(f"Implementation portfolio file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "intervention",
        "intervention_type",
        "implementation_stage",
        *POSITIVE_CRITERIA,
        *RISK_COMPONENTS,
        "evidence_quality",
        "stakeholder_coverage",
        "context_complexity",
        "scale_sensitivity",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Implementation portfolio missing required columns: {missing}")

    df = df.copy()
    for col in ["intervention", "intervention_type", "implementation_stage"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = (
        POSITIVE_CRITERIA
        + RISK_COMPONENTS
        + ["evidence_quality", "stakeholder_coverage", "context_complexity", "scale_sensitivity"]
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
                    "adoption_readiness": 0.20,
                    "operational_fit": 0.18,
                    "durability": 0.18,
                    "governance_readiness": 0.15,
                    "equity_readiness": 0.14,
                    "financial_sustainability": 0.10,
                    "composite_risk": 0.05,
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

    for col in POSITIVE_CRITERIA + RISK_COMPONENTS + ["context_complexity"]:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    for col in ["evidence_quality", "stakeholder_coverage", "scale_sensitivity"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Evidence or sensitivity indicators should be in [0, 1].",
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


def compute_composite_risk(df: pd.DataFrame) -> pd.Series:
    return (
        0.25 * df["operational_risk"]
        + 0.22 * df["governance_risk"]
        + 0.18 * df["technical_risk"]
        + 0.22 * df["equity_risk"]
        + 0.13 * df["financial_risk"]
    )


def score_interventions(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()
    scored["composite_risk"] = compute_composite_risk(scored)

    scored["implementation_value"] = (
        weights["adoption_readiness"] * scored["adoption_readiness"]
        + weights["operational_fit"] * scored["operational_fit"]
        + weights["durability"] * scored["durability"]
        + weights["governance_readiness"] * scored["governance_readiness"]
        + weights["equity_readiness"] * scored["equity_readiness"]
        + weights["financial_sustainability"] * scored["financial_sustainability"]
        - weights["composite_risk"] * scored["composite_risk"]
    )

    scored["evidence_adjusted_value"] = (
        scored["implementation_value"]
        * (0.75 + 0.15 * scored["evidence_quality"] + 0.10 * scored["stakeholder_coverage"])
    )

    scored["scaled_quality_estimate"] = (
        scored["implementation_value"] - scored["scale_sensitivity"] * scored["context_complexity"]
    )

    scored["implementation_review_priority"] = (
        0.28 * scored["composite_risk"]
        + 0.18 * (10.0 - scored["governance_readiness"])
        + 0.18 * (10.0 - scored["equity_readiness"])
        + 0.14 * (10.0 - scored["financial_sustainability"])
        + 0.12 * scored["context_complexity"]
        + 0.10 * (1.0 - scored["evidence_quality"]) * 10.0
    )

    scored["scale_readiness"] = (
        0.25 * scored["adoption_readiness"]
        + 0.20 * scored["operational_fit"]
        + 0.20 * scored["durability"]
        + 0.15 * scored["governance_readiness"]
        + 0.15 * scored["equity_readiness"]
        - 0.05 * scored["composite_risk"]
        - 0.10 * scored["scale_sensitivity"] * scored["context_complexity"]
    )

    scored["governed_durability_index"] = (
        0.35 * scored["durability"]
        + 0.30 * scored["governance_readiness"]
        + 0.20 * scored["financial_sustainability"]
        + 0.15 * scored["evidence_quality"] * 10.0
        - 0.15 * scored["governance_risk"]
    )

    scored = scored.sort_values("implementation_value", ascending=False).reset_index(drop=True)
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


def analyze_rollout(rollout: pd.DataFrame | None) -> pd.DataFrame:
    if rollout is None:
        return pd.DataFrame()

    required = [
        "intervention",
        "stage",
        "adoption_rate",
        "staff_compliance",
        "service_reliability",
        "support_ticket_rate",
        "equity_gap",
        "mean_resolution_time_hours",
        "user_trust",
        "staff_burden",
        "incident_count",
        "sites_live",
        "users_reached",
    ]
    missing = [col for col in required if col not in rollout.columns]
    if missing:
        raise ValueError(f"Rollout metrics missing required columns: {missing}")

    df = rollout.copy()
    for col in required:
        if col != "intervention":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["intervention", "stage"])
    df["adoption_delta"] = df.groupby("intervention")["adoption_rate"].diff()
    df["compliance_delta"] = df.groupby("intervention")["staff_compliance"].diff()
    df["reliability_delta"] = df.groupby("intervention")["service_reliability"].diff()
    df["ticket_delta"] = df.groupby("intervention")["support_ticket_rate"].diff()
    df["equity_gap_delta"] = df.groupby("intervention")["equity_gap"].diff()
    df["trust_delta"] = df.groupby("intervention")["user_trust"].diff()
    df["burden_delta"] = df.groupby("intervention")["staff_burden"].diff()
    df["incident_delta"] = df.groupby("intervention")["incident_count"].diff()

    df["rollout_learning_delta"] = (
        0.20 * df["adoption_delta"].fillna(0) * 10.0
        + 0.18 * df["compliance_delta"].fillna(0) * 10.0
        + 0.18 * df["reliability_delta"].fillna(0) * 10.0
        - 0.14 * df["ticket_delta"].fillna(0) * 10.0
        - 0.12 * df["equity_gap_delta"].fillna(0) * 10.0
        + 0.12 * df["trust_delta"].fillna(0)
        - 0.06 * df["burden_delta"].fillna(0)
        - 0.10 * df["incident_delta"].fillna(0)
    )

    summary = (
        df.groupby("intervention")
        .agg(
            stages=("stage", "max"),
            start_adoption=("adoption_rate", "first"),
            final_adoption=("adoption_rate", "last"),
            start_staff_compliance=("staff_compliance", "first"),
            final_staff_compliance=("staff_compliance", "last"),
            start_reliability=("service_reliability", "first"),
            final_reliability=("service_reliability", "last"),
            start_ticket_rate=("support_ticket_rate", "first"),
            final_ticket_rate=("support_ticket_rate", "last"),
            start_equity_gap=("equity_gap", "first"),
            final_equity_gap=("equity_gap", "last"),
            start_user_trust=("user_trust", "first"),
            final_user_trust=("user_trust", "last"),
            start_staff_burden=("staff_burden", "first"),
            final_staff_burden=("staff_burden", "last"),
            start_incidents=("incident_count", "first"),
            final_incidents=("incident_count", "last"),
            final_sites_live=("sites_live", "last"),
            final_users_reached=("users_reached", "last"),
            total_rollout_learning_delta=("rollout_learning_delta", "sum"),
        )
        .reset_index()
    )

    summary["adoption_improvement"] = summary["final_adoption"] - summary["start_adoption"]
    summary["staff_compliance_improvement"] = summary["final_staff_compliance"] - summary["start_staff_compliance"]
    summary["reliability_improvement"] = summary["final_reliability"] - summary["start_reliability"]
    summary["support_ticket_reduction"] = summary["start_ticket_rate"] - summary["final_ticket_rate"]
    summary["equity_gap_reduction"] = summary["start_equity_gap"] - summary["final_equity_gap"]
    summary["trust_improvement"] = summary["final_user_trust"] - summary["start_user_trust"]
    summary["staff_burden_reduction"] = summary["start_staff_burden"] - summary["final_staff_burden"]
    summary["incident_reduction"] = summary["start_incidents"] - summary["final_incidents"]

    return summary.sort_values("total_rollout_learning_delta", ascending=False)


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

    score_columns = POSITIVE_CRITERIA + RISK_COMPONENTS
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
                    "implementation_value": float(row["implementation_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "scaled_quality_estimate": float(row["scaled_quality_estimate"]),
                    "composite_risk": float(row["composite_risk"]),
                    "implementation_review_priority": float(row["implementation_review_priority"]),
                    "scale_readiness": float(row["scale_readiness"]),
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
                    "implementation_value": float(row["implementation_value"]),
                    "scaled_quality_estimate": float(row["scaled_quality_estimate"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("intervention")
        .agg(
            mean_implementation_value=("implementation_value", "mean"),
            sd_implementation_value=("implementation_value", "std"),
            mean_scaled_quality_estimate=("scaled_quality_estimate", "mean"),
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
        values="implementation_value",
        aggfunc="first",
    )
    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("Implementation Value Across Strategic Scenarios")
    ax.set_xlabel("Intervention")
    ax.set_ylabel("Weighted implementation value")
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
    plt.title("Monte Carlo Rank Stability for Implementation Decisions")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Intervention")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rollout(rollout_summary: pd.DataFrame, output_path: Path) -> None:
    if rollout_summary.empty:
        return
    plot_df = rollout_summary.sort_values("total_rollout_learning_delta", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["intervention"], plot_df["total_rollout_learning_delta"])
    plt.title("Rollout Learning Delta Across Implementation Stages")
    plt.xlabel("Total rollout learning delta")
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
    rollout_summary: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    balanced = scenario_results[scenario_results["scenario"].str.lower() == "balanced"]
    top = balanced.sort_values("rank").head(1)
    top_name = top.iloc[0]["intervention"] if not top.empty else "Not available"
    top_value = float(top.iloc[0]["implementation_value"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    rollout_section = "No rollout-stage data provided."
    if not rollout_summary.empty:
        rollout_section = dataframe_to_markdown_safe(rollout_summary)

    risk_section = "No risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Implementation and Scaling Decision-Support Report

## Article

Implementation and Scaling in Design Thinking

## Summary

This report compares implementation candidates using transparent multi-criteria readiness scoring, scenario analysis, scale sensitivity, rollout-stage diagnostics, uncertainty modeling, risk-register review, bootstrap stability, and random-weight sensitivity.

## Balanced scenario leader

- Intervention: **{top_name}**
- Weighted implementation value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_a A_i + w_o O_i + w_d D_i + w_g G_i + w_e E_i + w_f F_i - w_r R_i
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

## Rollout learning summary

{rollout_section}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate scale decisions. They support structured deliberation about implementation readiness, governance, equity, durability, scale sensitivity, uncertainty, and post-deployment learning. A high-scoring intervention may still require additional accessibility review, operational stress testing, technical hardening, governance approval, equity review, procurement review, or phased rollout before scale.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional implementation and scaling engine.")
    parser.add_argument(
        "--portfolio",
        type=Path,
        default=Path("../data/raw/implementation_portfolio_raw.csv"),
        help="Implementation portfolio CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/implementation_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--rollout",
        type=Path,
        default=Path("../data/raw/rollout_stage_metrics_raw.csv"),
        help="Rollout stage metrics CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/implementation_risk_register_raw.csv"),
        help="Implementation risk register CSV.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.6)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        portfolio_path=args.portfolio,
        weights_path=args.weights if args.weights.exists() else None,
        rollout_path=args.rollout if args.rollout.exists() else None,
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
    rollout = read_optional_csv(config.rollout_path)
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
    rollout_summary = analyze_rollout(rollout)
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
        .sort_values("implementation_review_priority", ascending=False)
        [
            [
                "intervention",
                "intervention_type",
                "implementation_stage",
                "implementation_value",
                "evidence_adjusted_value",
                "scaled_quality_estimate",
                "composite_risk",
                "implementation_review_priority",
                "scale_readiness",
                "governed_durability_index",
            ]
        ]
    )

    scenario_results.to_csv(config.output_dir / "implementation_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "implementation_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "implementation_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "implementation_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "implementation_weight_sensitivity.csv", index=False)
    review_priority.to_csv(config.output_dir / "implementation_review_priority.csv", index=False)

    if not rollout_summary.empty:
        rollout_summary.to_csv(config.output_dir / "rollout_stage_summary.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "implementation_risk_register_priority.csv", index=False)

    save_plot_scenario_values(scenario_results, config.output_dir / "implementation_scenario_values.png")
    save_plot_rank_stability(winners, config.output_dir / "implementation_rank_stability.png")
    save_plot_rollout(rollout_summary, config.output_dir / "rollout_learning_delta.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "portfolio_path": str(config.portfolio_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "rollout_path": str(config.rollout_path) if config.rollout_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "risk_components": RISK_COMPONENTS,
        },
    )

    report = build_report(
        portfolio=portfolio,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        rollout_summary=rollout_summary,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "implementation_scaling_decision_report.md").write_text(report, encoding="utf-8")

    print("Implementation and scaling analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- implementation_scenario_results.csv")
    print("- implementation_monte_carlo_winners.csv")
    print("- implementation_weight_sensitivity.csv")
    print("- rollout_stage_summary.csv")
    print("- implementation_review_priority.csv")
    print("- implementation_scaling_decision_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
