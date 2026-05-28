#!/usr/bin/env python3
"""
Professional design-thinking strategy decision-support engine.

This script evaluates strategic options, assumptions, implementation readiness,
ethics, public value, learning value, risk, and portfolio balance.

Core option model:

    S_i = w_dD_i + w_fF_i + w_vV_i + w_aA_i + w_eE_i + w_lL_i
          + w_pP_i + w_qQ_i - w_rR_i - w_cC_i - w_gG_i - w_tT_i

where:
    D = desirability
    F = feasibility
    V = viability
    A = strategic alignment
    E = ethical quality
    L = learning value
    P = public value
    Q = evidence strength
    R = strategic risk
    C = implementation effort
    G = capability gap
    T = time to learn

The workflow supports strategic deliberation. It does not automate executive,
public, institutional, investment, employment, or resource-allocation decisions.
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
    "desirability",
    "feasibility",
    "viability",
    "strategic_alignment",
    "ethical_quality",
    "learning_value",
    "public_value",
    "evidence_strength",
]

NEGATIVE_CRITERIA = [
    "strategic_risk",
    "implementation_effort",
    "capability_gap",
    "time_to_learn",
]

CORE_WEIGHTS = [*POSITIVE_CRITERIA, *NEGATIVE_CRITERIA]


@dataclass(frozen=True)
class EngineConfig:
    options_path: Path
    assumptions_path: Path | None
    weights_path: Path | None
    risk_register_path: Path | None
    output_dir: Path
    simulations: int
    seed: int
    score_sd: float
    evidence_sd: float
    bootstrap_iterations: int
    sensitivity_samples: int


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    field: str
    message: str


def read_options(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Strategic options file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "option",
        "option_type",
        "strategic_hypothesis",
        "desirability",
        "feasibility",
        "viability",
        "strategic_alignment",
        "ethical_quality",
        "learning_value",
        "implementation_effort",
        "strategic_risk",
        "capability_gap",
        "evidence_strength",
        "time_to_learn",
        "public_value",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Strategic options missing required columns: {missing}")

    df = df.copy()
    for col in ["option", "option_type", "strategic_hypothesis"]:
        df[col] = df[col].astype(str).str.strip()

    score_cols = [
        "desirability",
        "feasibility",
        "viability",
        "strategic_alignment",
        "ethical_quality",
        "learning_value",
        "implementation_effort",
        "strategic_risk",
        "capability_gap",
        "time_to_learn",
        "public_value",
    ]
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["evidence_strength"] = pd.to_numeric(df["evidence_strength"], errors="coerce")

    return df


def read_weights(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame(
            [
                {
                    "scenario": "Balanced",
                    "desirability": 0.17,
                    "feasibility": 0.13,
                    "viability": 0.13,
                    "strategic_alignment": 0.16,
                    "ethical_quality": 0.11,
                    "learning_value": 0.10,
                    "public_value": 0.08,
                    "evidence_strength": 0.05,
                    "strategic_risk": 0.03,
                    "implementation_effort": 0.02,
                    "capability_gap": 0.01,
                    "time_to_learn": 0.01,
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


def validate_options(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["option"].duplicated().any():
        issues.append(
            ValidationIssue(
                level="error",
                field="option",
                message="Duplicate strategic option names detected.",
            )
        )

    score_cols = [
        "desirability",
        "feasibility",
        "viability",
        "strategic_alignment",
        "ethical_quality",
        "learning_value",
        "implementation_effort",
        "strategic_risk",
        "capability_gap",
        "time_to_learn",
        "public_value",
    ]
    for col in score_cols:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Strategic option scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    invalid_evidence = df[
        df["evidence_strength"].isna()
        | (df["evidence_strength"] < 0)
        | (df["evidence_strength"] > 1)
    ]
    if not invalid_evidence.empty:
        issues.append(
            ValidationIssue(
                level="error",
                field="evidence_strength",
                message="Evidence strength must be numeric and in [0, 1].",
            )
        )

    return issues


def score_options(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["strategic_score"] = (
        weights["desirability"] * scored["desirability"]
        + weights["feasibility"] * scored["feasibility"]
        + weights["viability"] * scored["viability"]
        + weights["strategic_alignment"] * scored["strategic_alignment"]
        + weights["ethical_quality"] * scored["ethical_quality"]
        + weights["learning_value"] * scored["learning_value"]
        + weights["public_value"] * scored["public_value"]
        + weights["evidence_strength"] * scored["evidence_strength"] * 10.0
        - weights["strategic_risk"] * scored["strategic_risk"]
        - weights["implementation_effort"] * scored["implementation_effort"]
        - weights["capability_gap"] * scored["capability_gap"]
        - weights["time_to_learn"] * scored["time_to_learn"]
    )

    scored["portfolio_value"] = (
        scored["strategic_score"]
        + 0.30 * scored["learning_value"]
        + 0.20 * scored["public_value"]
        + 0.15 * scored["evidence_strength"] * 10.0
        - 0.22 * scored["strategic_risk"]
        - 0.14 * scored["implementation_effort"]
        - 0.10 * scored["capability_gap"]
    )

    scored["uncertainty_priority"] = (
        0.26 * scored["strategic_risk"]
        + 0.22 * scored["learning_value"]
        + 0.16 * scored["implementation_effort"]
        + 0.14 * scored["capability_gap"]
        + 0.12 * (10.0 - scored["feasibility"])
        + 0.10 * (1.0 - scored["evidence_strength"]) * 10.0
    )

    scored["implementation_readiness"] = (
        0.28 * scored["feasibility"]
        + 0.24 * scored["viability"]
        + 0.20 * (10.0 - scored["implementation_effort"])
        + 0.16 * (10.0 - scored["capability_gap"])
        + 0.12 * scored["evidence_strength"] * 10.0
    )

    scored["ethical_public_value_index"] = (
        0.42 * scored["ethical_quality"]
        + 0.38 * scored["public_value"]
        + 0.12 * scored["strategic_alignment"]
        - 0.08 * scored["strategic_risk"]
    )

    conditions = [
        (scored["strategic_score"] >= 7.4) & (scored["strategic_risk"] <= 5.0) & (scored["implementation_readiness"] >= 6.8),
        (scored["learning_value"] >= 8.2) & (scored["strategic_risk"] >= 5.0),
        (scored["ethical_public_value_index"] >= 8.0),
        (scored["capability_gap"] >= 6.2) | (scored["implementation_effort"] >= 7.2),
    ]
    choices = [
        "scale_or_commit",
        "prototype_and_learn",
        "public_value_or_legitimacy_bet",
        "capability_required",
    ]
    scored["portfolio_role"] = np.select(conditions, choices, default="sequence_after_learning")

    scored = scored.sort_values("strategic_score", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(options: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_WEIGHTS}
        scored = score_options(options, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_WEIGHTS:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def analyze_assumptions(assumptions: pd.DataFrame | None) -> pd.DataFrame:
    if assumptions is None:
        return pd.DataFrame()

    required = [
        "option",
        "assumption",
        "assumption_type",
        "importance",
        "confidence",
        "test_cost",
        "time_to_test",
        "ethical_sensitivity",
        "decision_threshold",
        "current_evidence",
    ]
    missing = [col for col in required if col not in assumptions.columns]
    if missing:
        raise ValueError(f"Strategic assumptions missing required columns: {missing}")

    df = assumptions.copy()
    for col in ["option", "assumption", "assumption_type", "current_evidence"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = [
        "importance",
        "confidence",
        "test_cost",
        "time_to_test",
        "ethical_sensitivity",
        "decision_threshold",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["uncertainty_load"] = df["importance"] * (1.0 - df["confidence"])
    df["test_priority"] = (
        0.34 * df["uncertainty_load"]
        + 0.22 * df["ethical_sensitivity"]
        + 0.18 * df["importance"]
        - 0.14 * df["test_cost"]
        - 0.12 * (df["time_to_test"] / 10.0)
    )
    df["evidence_gap"] = np.maximum(df["decision_threshold"] - df["confidence"], 0.0)

    return df.sort_values("test_priority", ascending=False)


def summarize_assumptions(assumptions: pd.DataFrame) -> pd.DataFrame:
    if assumptions.empty:
        return pd.DataFrame()

    return (
        assumptions.groupby("option")
        .agg(
            assumptions_count=("assumption", "count"),
            mean_importance=("importance", "mean"),
            mean_confidence=("confidence", "mean"),
            total_uncertainty_load=("uncertainty_load", "sum"),
            mean_test_priority=("test_priority", "mean"),
            max_ethical_sensitivity=("ethical_sensitivity", "max"),
            mean_evidence_gap=("evidence_gap", "mean"),
            max_evidence_gap=("evidence_gap", "max"),
        )
        .reset_index()
        .sort_values("total_uncertainty_load", ascending=False)
    )


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "option",
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
    options: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    evidence_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    winner_counts: Counter[str] = Counter()
    records: List[dict] = []

    score_cols = [
        "desirability",
        "feasibility",
        "viability",
        "strategic_alignment",
        "ethical_quality",
        "learning_value",
        "implementation_effort",
        "strategic_risk",
        "capability_gap",
        "time_to_learn",
        "public_value",
    ]

    for simulation_id in range(simulations):
        simulated = options.copy()

        for col in score_cols:
            simulated[col] = rng.normal(
                loc=options[col].to_numpy(dtype=float),
                scale=score_sd,
            ).clip(1.0, 10.0)

        simulated["evidence_strength"] = rng.normal(
            loc=options["evidence_strength"].to_numpy(dtype=float),
            scale=evidence_sd,
        ).clip(0.0, 1.0)

        scored = score_options(simulated, weights)
        winner_counts[str(scored.iloc[0]["option"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "option": row["option"],
                    "option_type": row["option_type"],
                    "strategic_score": float(row["strategic_score"]),
                    "portfolio_value": float(row["portfolio_value"]),
                    "uncertainty_priority": float(row["uncertainty_priority"]),
                    "implementation_readiness": float(row["implementation_readiness"]),
                    "ethical_public_value_index": float(row["ethical_public_value_index"]),
                    "portfolio_role": row["portfolio_role"],
                    "rank": int(row["rank"]),
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "option": option,
                    "times_ranked_first": count,
                    "probability_ranked_first": count / simulations,
                }
                for option, count in winner_counts.items()
            ]
        )
        .sort_values("probability_ranked_first", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_stability(
    options: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = options.sample(
            n=len(options),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_options(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "option": row["option"],
                    "strategic_score": float(row["strategic_score"]),
                    "portfolio_value": float(row["portfolio_value"]),
                    "uncertainty_priority": float(row["uncertainty_priority"]),
                    "implementation_readiness": float(row["implementation_readiness"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("option")
        .agg(
            mean_strategic_score=("strategic_score", "mean"),
            sd_strategic_score=("strategic_score", "std"),
            mean_portfolio_value=("portfolio_value", "mean"),
            mean_uncertainty_priority=("uncertainty_priority", "mean"),
            mean_implementation_readiness=("implementation_readiness", "mean"),
            median_rank=("rank", "median"),
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
        )
        .reset_index()
        .sort_values(["median_rank", "mean_rank"])
    )


def random_weight_sensitivity(
    options: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()

    for _ in range(samples):
        arr = rng.dirichlet(np.ones(len(CORE_WEIGHTS)))
        weights = dict(zip(CORE_WEIGHTS, arr))
        scored = score_options(options, weights)
        winner_counts[str(scored.iloc[0]["option"])] += 1

    return (
        pd.DataFrame(
            [
                {
                    "option": option,
                    "times_won": count,
                    "probability_winning_under_random_weights": count / samples,
                }
                for option, count in winner_counts.items()
            ]
        )
        .sort_values("probability_winning_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_plot_options(scored: pd.DataFrame, output_path: Path) -> None:
    plot_df = scored.sort_values("strategic_score", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["option"], plot_df["strategic_score"])
    plt.title("Strategic Option Score")
    plt.xlabel("Strategic score")
    plt.ylabel("Strategic option")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_portfolio(scored: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(10, 7))
    sizes = np.clip(scored["learning_value"].to_numpy(dtype=float), 1, 10) * 30
    plt.scatter(scored["implementation_effort"], scored["strategic_score"], s=sizes)
    for _, row in scored.iterrows():
        plt.annotate(row["option"], (row["implementation_effort"], row["strategic_score"]), fontsize=8)
    plt.title("Strategic Option Portfolio")
    plt.xlabel("Implementation effort")
    plt.ylabel("Strategic score")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    if winners.empty:
        return
    plot_df = winners.copy()
    plot_df["probability_pct"] = plot_df["probability_ranked_first"] * 100.0
    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["option"], plot_df["probability_pct"])
    plt.title("Strategic Option Rank Stability Under Uncertainty")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Strategic option")
    plt.xticks(rotation=25, ha="right")
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
    option_scores: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    assumptions: pd.DataFrame,
    assumption_summary: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top = option_scores.sort_values("rank").head(1)
    top_option = top.iloc[0]["option"] if not top.empty else "Not available"
    top_score = float(top.iloc[0]["strategic_score"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    assumption_section = "No strategic assumption data provided."
    if not assumptions.empty:
        assumption_section = dataframe_to_markdown_safe(assumptions)

    assumption_summary_section = "No strategic assumption summary available."
    if not assumption_summary.empty:
        assumption_summary_section = dataframe_to_markdown_safe(assumption_summary)

    risk_section = "No strategy risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Design Thinking and Strategy Report

## Summary

This report evaluates strategic options using transparent multi-criteria scoring, scenario analysis, portfolio role classification, strategic assumption review, implementation readiness, ethical/public-value review, uncertainty modeling, bootstrap stability, random-weight sensitivity, and risk-register prioritization.

## Highest balanced-scenario strategic option

- Option: **{top_option}**
- Strategic score: **{top_score:.3f}**

## Validation notes

{issue_lines}

## Strategic option scores

{dataframe_to_markdown_safe(option_scores)}

## Scenario results

{dataframe_to_markdown_safe(scenario_results.head(40))}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Strategic assumption summary

{assumption_summary_section}

## Strategic assumption test priorities

{assumption_section}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate strategy. They support structured deliberation about desirability, feasibility, viability, strategic alignment, ethical quality, public value, learning value, evidence strength, implementation effort, strategic risk, capability gaps, and time-to-learn. A high-scoring option should still undergo stakeholder review, prototype evidence, implementation review, ethics and power analysis, financial/operational review, and governance approval before scaling.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional design-thinking strategy analysis engine.")
    parser.add_argument(
        "--options",
        type=Path,
        default=Path("../data/raw/strategic_options_raw.csv"),
        help="Strategic options CSV.",
    )
    parser.add_argument(
        "--assumptions",
        type=Path,
        default=Path("../data/raw/strategic_assumptions_raw.csv"),
        help="Strategic assumptions CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/strategy_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/strategy_risk_register_raw.csv"),
        help="Strategy risk register CSV.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.55)
    parser.add_argument("--evidence-sd", type=float, default=0.09)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        options_path=args.options,
        assumptions_path=args.assumptions if args.assumptions.exists() else None,
        weights_path=args.weights if args.weights.exists() else None,
        risk_register_path=args.risk_register if args.risk_register.exists() else None,
        output_dir=args.output_dir,
        simulations=args.simulations,
        seed=args.seed,
        score_sd=args.score_sd,
        evidence_sd=args.evidence_sd,
        bootstrap_iterations=args.bootstrap_iterations,
        sensitivity_samples=args.sensitivity_samples,
    )


def main(argv: List[str] | None = None) -> int:
    config = parse_args(argv or sys.argv[1:])
    config.output_dir.mkdir(parents=True, exist_ok=True)

    options = read_options(config.options_path)
    scenarios = read_weights(config.weights_path)
    assumptions_raw = read_optional_csv(config.assumptions_path)
    risk_register = read_optional_csv(config.risk_register_path)

    issues = validate_options(options)
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

    option_scores = score_options(options, balanced_weights)
    scenario_results = run_scenario_analysis(options, scenarios)
    assumptions = analyze_assumptions(assumptions_raw)
    assumption_summary = summarize_assumptions(assumptions)
    risk_summary = analyze_risk_register(risk_register)

    winners, simulation_records = monte_carlo_rank_stability(
        options=options,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        evidence_sd=config.evidence_sd,
        seed=config.seed,
    )

    simulation_summary = (
        simulation_records.groupby("option")
        .agg(
            mean_strategic_score=("strategic_score", "mean"),
            sd_strategic_score=("strategic_score", "std"),
            mean_portfolio_value=("portfolio_value", "mean"),
            mean_uncertainty_priority=("uncertainty_priority", "mean"),
            mean_implementation_readiness=("implementation_readiness", "mean"),
            mean_ethical_public_value_index=("ethical_public_value_index", "mean"),
            median_rank=("rank", "median"),
            p90_rank=("rank", lambda x: float(np.quantile(x, 0.90))),
        )
        .reset_index()
        .sort_values("mean_strategic_score", ascending=False)
    )

    bootstrap = bootstrap_stability(
        options=options,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        options=options,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    portfolio_summary = (
        option_scores.groupby("portfolio_role")
        .agg(
            options=("option", "count"),
            mean_strategic_score=("strategic_score", "mean"),
            mean_portfolio_value=("portfolio_value", "mean"),
            mean_learning_value=("learning_value", "mean"),
            mean_strategic_risk=("strategic_risk", "mean"),
            mean_implementation_readiness=("implementation_readiness", "mean"),
            mean_ethical_public_value_index=("ethical_public_value_index", "mean"),
        )
        .reset_index()
        .sort_values("mean_portfolio_value", ascending=False)
    )

    option_scores.to_csv(config.output_dir / "strategy_option_balanced_scores.csv", index=False)
    scenario_results.to_csv(config.output_dir / "strategy_option_scenario_results.csv", index=False)
    portfolio_summary.to_csv(config.output_dir / "strategy_portfolio_summary.csv", index=False)
    winners.to_csv(config.output_dir / "strategy_option_monte_carlo_winners.csv", index=False)
    simulation_records.to_csv(config.output_dir / "strategy_option_simulation_records.csv", index=False)
    simulation_summary.to_csv(config.output_dir / "strategy_option_simulation_summary.csv", index=False)
    bootstrap.to_csv(config.output_dir / "strategy_option_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "strategy_option_weight_sensitivity.csv", index=False)

    if not assumptions.empty:
        assumptions.to_csv(config.output_dir / "strategic_assumption_test_priorities.csv", index=False)
        assumption_summary.to_csv(config.output_dir / "strategic_assumption_summary.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "strategy_risk_register_priority.csv", index=False)

    save_plot_options(option_scores, config.output_dir / "strategy_option_scores.png")
    save_plot_portfolio(option_scores, config.output_dir / "strategy_portfolio_plot.png")
    save_plot_rank_stability(winners, config.output_dir / "strategy_rank_stability.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "options_path": str(config.options_path),
                "assumptions_path": str(config.assumptions_path) if config.assumptions_path else None,
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "option_model": "S_i = weighted positives - weighted negatives",
            "uncertainty_model": "U = sum(importance * (1 - confidence))",
        },
    )

    report = build_report(
        option_scores=option_scores,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        assumptions=assumptions,
        assumption_summary=assumption_summary,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "strategy_design_report.md").write_text(report, encoding="utf-8")

    print("Design-thinking strategy analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- strategy_option_balanced_scores.csv")
    print("- strategy_option_scenario_results.csv")
    print("- strategy_portfolio_summary.csv")
    print("- strategy_option_monte_carlo_winners.csv")
    print("- strategic_assumption_test_priorities.csv")
    print("- strategy_risk_register_priority.csv")
    print("- strategy_design_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
