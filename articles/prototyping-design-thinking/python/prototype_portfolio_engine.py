#!/usr/bin/env python3
"""
Professional prototype portfolio decision-support engine.

This script compares prototype concepts across learning gain, feasibility signal,
user response, equity value, implementation relevance, and composite risk. It
also analyzes iteration rounds, risk-register priority, Monte Carlo uncertainty,
bootstrap stability, and random-weight sensitivity.

The model is intentionally interpretable:

    V_i = w_l L_i + w_f F_i + w_u U_i + w_e E_i + w_m M_i - w_r R_i

where:
    L_i = learning gain
    F_i = feasibility signal
    U_i = user response
    E_i = equity value
    M_i = implementation relevance
    R_i = composite risk

A prototype is treated as a learning instrument, not a final product. This
workflow supports deliberation, documentation, and responsible prototype
selection. It should not automate design judgment.
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


CORE_CRITERIA = [
    "learning_gain",
    "feasibility_signal",
    "user_response",
    "equity_value",
    "implementation_relevance",
    "composite_risk",
]

POSITIVE_CRITERIA = [
    "learning_gain",
    "feasibility_signal",
    "user_response",
    "equity_value",
    "implementation_relevance",
]

RISK_COMPONENTS = [
    "ethical_risk",
    "operational_risk",
    "technical_risk",
    "scaling_risk",
]


@dataclass(frozen=True)
class EngineConfig:
    portfolio_path: Path
    weights_path: Path | None
    rounds_path: Path | None
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
        raise FileNotFoundError(f"Prototype portfolio file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "prototype",
        "prototype_type",
        "fidelity_level",
        *POSITIVE_CRITERIA,
        *RISK_COMPONENTS,
        "evidence_quality",
        "prototype_testability",
        "stakeholder_coverage",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Prototype portfolio missing required columns: {missing}")

    df = df.copy()
    for col in ["prototype", "prototype_type", "fidelity_level"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = POSITIVE_CRITERIA + RISK_COMPONENTS + [
        "evidence_quality",
        "prototype_testability",
        "stakeholder_coverage",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_weights(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame(
            [
                {
                    "scenario": "Balanced",
                    "learning_gain": 0.25,
                    "feasibility_signal": 0.18,
                    "user_response": 0.20,
                    "equity_value": 0.15,
                    "implementation_relevance": 0.12,
                    "composite_risk": 0.10,
                }
            ]
        )

    df = pd.read_csv(path)
    required = ["scenario", *CORE_CRITERIA]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Scenario weights missing required columns: {missing}")

    df = df.copy()
    df["scenario"] = df["scenario"].astype(str).str.strip()
    for col in CORE_CRITERIA:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[CORE_CRITERIA].isna().any().any():
        raise ValueError("Scenario weights contain missing or non-numeric values.")

    weight_sums = df[CORE_CRITERIA].sum(axis=1)
    if not np.allclose(weight_sums, 1.0, atol=1e-6):
        raise ValueError("Each scenario weight row must sum to 1.0.")

    return df


def read_optional_csv(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None
    return pd.read_csv(path)


def validate_portfolio(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["prototype"].duplicated().any():
        issues.append(
            ValidationIssue(
                level="error",
                field="prototype",
                message="Duplicate prototype names detected.",
            )
        )

    for col in POSITIVE_CRITERIA + RISK_COMPONENTS:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    for col in ["evidence_quality", "prototype_testability", "stakeholder_coverage"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Confidence-style columns should be in [0, 1].",
                )
            )

    if len(df) < 3:
        issues.append(
            ValidationIssue(
                level="warning",
                field="prototype",
                message="Fewer than three prototypes limits portfolio comparison.",
            )
        )

    return issues


def compute_composite_risk(
    df: pd.DataFrame,
    lambdas: Dict[str, float] | None = None,
) -> pd.Series:
    if lambdas is None:
        lambdas = {
            "ethical_risk": 0.30,
            "operational_risk": 0.30,
            "technical_risk": 0.20,
            "scaling_risk": 0.20,
        }
    total = sum(lambdas[col] for col in RISK_COMPONENTS)
    return sum((lambdas[col] / total) * df[col] for col in RISK_COMPONENTS)


def score_prototypes(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()
    scored["composite_risk"] = compute_composite_risk(scored)

    scored["prototype_value"] = (
        weights["learning_gain"] * scored["learning_gain"]
        + weights["feasibility_signal"] * scored["feasibility_signal"]
        + weights["user_response"] * scored["user_response"]
        + weights["equity_value"] * scored["equity_value"]
        + weights["implementation_relevance"] * scored["implementation_relevance"]
        - weights["composite_risk"] * scored["composite_risk"]
    )

    scored["confidence_adjusted_value"] = (
        scored["prototype_value"] * (0.75 + 0.25 * scored["evidence_quality"])
    )

    scored["testability_adjusted_value"] = (
        scored["confidence_adjusted_value"] * (0.85 + 0.15 * scored["prototype_testability"])
    )

    scored["coverage_adjusted_value"] = (
        scored["testability_adjusted_value"] * (0.85 + 0.15 * scored["stakeholder_coverage"])
    )

    scored["risk_adjusted_learning"] = (
        scored["learning_gain"] - 0.35 * scored["composite_risk"]
    )

    scored["prototype_review_priority"] = (
        0.35 * scored["composite_risk"]
        + 0.20 * (10.0 - scored["evidence_quality"] * 10.0)
        + 0.20 * scored["ethical_risk"]
        + 0.15 * scored["scaling_risk"]
        + 0.10 * (10.0 - scored["feasibility_signal"])
    )

    scored["advance_readiness"] = (
        0.30 * scored["coverage_adjusted_value"]
        + 0.25 * scored["feasibility_signal"]
        + 0.20 * scored["implementation_relevance"]
        + 0.15 * scored["stakeholder_coverage"] * 10.0
        - 0.10 * scored["composite_risk"]
    )

    scored = scored.sort_values("prototype_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)
    return scored


def run_scenario_analysis(portfolio: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_CRITERIA}
        scored = score_prototypes(portfolio, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_CRITERIA:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def analyze_iteration_rounds(rounds: pd.DataFrame | None) -> pd.DataFrame:
    if rounds is None:
        return pd.DataFrame()

    required = [
        "prototype",
        "round",
        "usability",
        "comprehension",
        "trust",
        "unresolved_friction",
        "task_success_rate",
        "mean_time_minutes",
        "critical_issue_count",
        "participant_count",
    ]
    missing = [col for col in required if col not in rounds.columns]
    if missing:
        raise ValueError(f"Prototype rounds file missing required columns: {missing}")

    df = rounds.copy()
    for col in required:
        if col not in ["prototype"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["prototype", "round"])
    df["usability_delta"] = df.groupby("prototype")["usability"].diff()
    df["comprehension_delta"] = df.groupby("prototype")["comprehension"].diff()
    df["trust_delta"] = df.groupby("prototype")["trust"].diff()
    df["friction_delta"] = df.groupby("prototype")["unresolved_friction"].diff()
    df["task_success_delta"] = df.groupby("prototype")["task_success_rate"].diff()
    df["time_delta"] = df.groupby("prototype")["mean_time_minutes"].diff()
    df["critical_issue_delta"] = df.groupby("prototype")["critical_issue_count"].diff()

    df["quality_delta"] = (
        0.30 * df["usability_delta"].fillna(0)
        + 0.25 * df["comprehension_delta"].fillna(0)
        + 0.25 * df["trust_delta"].fillna(0)
        - 0.20 * df["friction_delta"].fillna(0)
    )

    summary = (
        df.groupby("prototype")
        .agg(
            rounds=("round", "max"),
            start_usability=("usability", "first"),
            final_usability=("usability", "last"),
            start_comprehension=("comprehension", "first"),
            final_comprehension=("comprehension", "last"),
            start_trust=("trust", "first"),
            final_trust=("trust", "last"),
            start_friction=("unresolved_friction", "first"),
            final_friction=("unresolved_friction", "last"),
            start_task_success=("task_success_rate", "first"),
            final_task_success=("task_success_rate", "last"),
            start_critical_issues=("critical_issue_count", "first"),
            final_critical_issues=("critical_issue_count", "last"),
            total_quality_delta=("quality_delta", "sum"),
            participant_count=("participant_count", "sum"),
        )
        .reset_index()
    )

    summary["usability_improvement"] = summary["final_usability"] - summary["start_usability"]
    summary["comprehension_improvement"] = summary["final_comprehension"] - summary["start_comprehension"]
    summary["trust_improvement"] = summary["final_trust"] - summary["start_trust"]
    summary["friction_reduction"] = summary["start_friction"] - summary["final_friction"]
    summary["task_success_improvement"] = summary["final_task_success"] - summary["start_task_success"]
    summary["critical_issue_reduction"] = summary["start_critical_issues"] - summary["final_critical_issues"]

    return summary.sort_values("total_quality_delta", ascending=False)


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "prototype",
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

        scored = score_prototypes(simulated, weights)
        winner_counts[str(scored.iloc[0]["prototype"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "prototype": row["prototype"],
                    "prototype_type": row["prototype_type"],
                    "prototype_value": float(row["prototype_value"]),
                    "confidence_adjusted_value": float(row["confidence_adjusted_value"]),
                    "composite_risk": float(row["composite_risk"]),
                    "prototype_review_priority": float(row["prototype_review_priority"]),
                    "advance_readiness": float(row["advance_readiness"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "prototype": prototype,
                    "times_ranked_first": count,
                    "probability_ranked_first": count / simulations,
                }
                for prototype, count in winner_counts.items()
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
        scored = score_prototypes(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "prototype": row["prototype"],
                    "prototype_value": float(row["prototype_value"]),
                    "composite_risk": float(row["composite_risk"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("prototype")
        .agg(
            mean_prototype_value=("prototype_value", "mean"),
            sd_prototype_value=("prototype_value", "std"),
            mean_composite_risk=("composite_risk", "mean"),
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
        arr = rng.dirichlet(np.ones(len(CORE_CRITERIA)))
        weights = dict(zip(CORE_CRITERIA, arr))
        scored = score_prototypes(portfolio, weights)
        winner_counts[str(scored.iloc[0]["prototype"])] += 1

    out = pd.DataFrame(
        [
            {
                "prototype": prototype,
                "times_won": count,
                "probability_winning_under_random_weights": count / samples,
            }
            for prototype, count in winner_counts.items()
        ]
    )
    return out.sort_values("probability_winning_under_random_weights", ascending=False)


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="prototype",
        columns="scenario",
        values="prototype_value",
        aggfunc="first",
    )
    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("Prototype Value Across Learning Priority Scenarios")
    ax.set_xlabel("Prototype")
    ax.set_ylabel("Weighted prototype value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["prototype"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for Prototype Decisions")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Prototype")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_iteration(iteration_summary: pd.DataFrame, output_path: Path) -> None:
    if iteration_summary.empty:
        return
    plot_df = iteration_summary.sort_values("total_quality_delta", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["prototype"], plot_df["total_quality_delta"])
    plt.title("Total Prototype Quality Improvement Across Iterations")
    plt.xlabel("Total quality delta")
    plt.ylabel("Prototype")
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
    iteration_summary: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    balanced = scenario_results[scenario_results["scenario"].str.lower() == "balanced"]
    top = balanced.sort_values("rank").head(1)
    top_name = top.iloc[0]["prototype"] if not top.empty else "Not available"
    top_value = float(top.iloc[0]["prototype_value"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    iteration_section = "No iteration-round data provided."
    if not iteration_summary.empty:
        iteration_section = dataframe_to_markdown_safe(iteration_summary)

    risk_section = "No risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Prototype Portfolio Decision-Support Report

## Article

Prototyping in Design Thinking

## Summary

This report compares prototype candidates using transparent multi-criteria scoring, scenario analysis, uncertainty modeling, iteration improvement, risk-register review, bootstrap stability, and random-weight sensitivity.

## Balanced scenario leader

- Prototype: **{top_name}**
- Weighted prototype value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_l L_i + w_f F_i + w_u U_i + w_e E_i + w_m M_i - w_r R_i
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

## Iteration improvement summary

{iteration_section}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate prototype selection. They support structured deliberation about learning value, uncertainty, risk, and next-step decisions. A high-scoring prototype may still require ethical review, accessibility review, stakeholder validation, technical review, or operational testing before it advances.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional prototype portfolio engine.")
    parser.add_argument(
        "--portfolio",
        type=Path,
        default=Path("../data/raw/prototype_portfolio_raw.csv"),
        help="Prototype portfolio CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/prototype_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--rounds",
        type=Path,
        default=Path("../data/raw/prototype_test_rounds_raw.csv"),
        help="Prototype test rounds CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/prototype_risk_register_raw.csv"),
        help="Prototype risk register CSV.",
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
        rounds_path=args.rounds if args.rounds.exists() else None,
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
    rounds = read_optional_csv(config.rounds_path)
    risk_register = read_optional_csv(config.risk_register_path)

    issues = validate_portfolio(portfolio)
    fatal = [issue for issue in issues if issue.level == "error"]
    if fatal:
        for issue in fatal:
            print(f"ERROR [{issue.field}]: {issue.message}", file=sys.stderr)
        return 2

    balanced_weights = (
        scenarios[scenarios["scenario"].str.lower() == "balanced"]
        .iloc[0][CORE_CRITERIA]
        .astype(float)
        .to_dict()
    )

    scenario_results = run_scenario_analysis(portfolio, scenarios)
    iteration_summary = analyze_iteration_rounds(rounds)
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
        score_prototypes(portfolio, balanced_weights)
        .sort_values("prototype_review_priority", ascending=False)
        [
            [
                "prototype",
                "prototype_type",
                "fidelity_level",
                "prototype_value",
                "confidence_adjusted_value",
                "composite_risk",
                "prototype_review_priority",
                "advance_readiness",
            ]
        ]
    )

    scenario_results.to_csv(config.output_dir / "prototype_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "prototype_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "prototype_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "prototype_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "prototype_weight_sensitivity.csv", index=False)
    review_priority.to_csv(config.output_dir / "prototype_review_priority.csv", index=False)

    if not iteration_summary.empty:
        iteration_summary.to_csv(config.output_dir / "prototype_iteration_summary.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "prototype_risk_register_priority.csv", index=False)

    save_plot_scenario_values(scenario_results, config.output_dir / "prototype_scenario_values.png")
    save_plot_rank_stability(winners, config.output_dir / "prototype_rank_stability.png")
    save_plot_iteration(iteration_summary, config.output_dir / "prototype_iteration_quality_delta.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "portfolio_path": str(config.portfolio_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "rounds_path": str(config.rounds_path) if config.rounds_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_CRITERIA,
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
        iteration_summary=iteration_summary,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "prototype_decision_report.md").write_text(report, encoding="utf-8")

    print("Prototype portfolio analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- prototype_scenario_results.csv")
    print("- prototype_monte_carlo_winners.csv")
    print("- prototype_weight_sensitivity.csv")
    print("- prototype_iteration_summary.csv")
    print("- prototype_review_priority.csv")
    print("- prototype_decision_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
