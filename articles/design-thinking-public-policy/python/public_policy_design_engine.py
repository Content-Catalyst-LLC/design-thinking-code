#!/usr/bin/env python3
"""
Professional public-policy design decision-support engine.

This script compares public-policy pilot concepts across accessibility,
feasibility, legitimacy, equity, administrative-burden reduction,
implementation durability, risk, evidence quality, stakeholder coverage,
legal complexity, implementation complexity, and participation quality.

It also analyzes policy-learning pathways, administrative burden distribution,
risk-register priority, Monte Carlo uncertainty, bootstrap stability, and
random-weight sensitivity.

The model is intentionally interpretable:

    V_i = w_a A_i + w_f F_i + w_l L_i + w_e E_i + w_b B_i + w_d D_i - w_r R_i

where:
    A_i = accessibility and public legibility
    F_i = feasibility
    L_i = legitimacy, trust, and public acceptability
    E_i = equity adequacy
    B_i = administrative-burden reduction
    D_i = implementation durability
    R_i = implementation and unintended-consequence risk

This workflow supports public-policy deliberation and documentation. It does
not automate policy choices or replace legal, democratic, ethical, community,
or administrative review.
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
    "accessibility",
    "feasibility",
    "legitimacy",
    "equity",
    "burden_reduction",
    "durability",
]

CORE_WEIGHTS = [*POSITIVE_CRITERIA, "risk"]


@dataclass(frozen=True)
class EngineConfig:
    pilots_path: Path
    weights_path: Path | None
    learning_path: Path | None
    burdens_path: Path | None
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


def read_pilots(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Public policy pilots file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "pilot",
        "policy_domain",
        "pilot_type",
        *POSITIVE_CRITERIA,
        "risk",
        "evidence_quality",
        "stakeholder_coverage",
        "legal_complexity",
        "implementation_complexity",
        "participation_quality",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Public policy pilots missing required columns: {missing}")

    df = df.copy()
    for col in ["pilot", "policy_domain", "pilot_type"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = (
        POSITIVE_CRITERIA
        + ["risk", "evidence_quality", "stakeholder_coverage", "legal_complexity", "implementation_complexity", "participation_quality"]
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
                    "accessibility": 0.20,
                    "feasibility": 0.16,
                    "legitimacy": 0.16,
                    "equity": 0.20,
                    "burden_reduction": 0.14,
                    "durability": 0.08,
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


def validate_pilots(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["pilot"].duplicated().any():
        issues.append(
            ValidationIssue(
                level="error",
                field="pilot",
                message="Duplicate pilot names detected.",
            )
        )

    for col in POSITIVE_CRITERIA + ["risk", "legal_complexity", "implementation_complexity"]:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    for col in ["evidence_quality", "stakeholder_coverage", "participation_quality"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Evidence, stakeholder, and participation indicators should be in [0, 1].",
                )
            )

    if len(df) < 3:
        issues.append(
            ValidationIssue(
                level="warning",
                field="pilot",
                message="Fewer than three pilots limits portfolio comparison.",
            )
        )

    return issues


def score_pilots(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["evidence_strength"] = (
        0.40 * scored["evidence_quality"]
        + 0.35 * scored["stakeholder_coverage"]
        + 0.25 * scored["participation_quality"]
    ).clip(0.0, 1.0)

    scored["policy_value"] = (
        weights["accessibility"] * scored["accessibility"]
        + weights["feasibility"] * scored["feasibility"]
        + weights["legitimacy"] * scored["legitimacy"]
        + weights["equity"] * scored["equity"]
        + weights["burden_reduction"] * scored["burden_reduction"]
        + weights["durability"] * scored["durability"]
        - weights["risk"] * scored["risk"]
    )

    scored["evidence_adjusted_value"] = (
        scored["policy_value"] * (0.75 + 0.25 * scored["evidence_strength"])
    )

    scored["implementation_readiness"] = (
        0.28 * scored["feasibility"]
        + 0.22 * scored["durability"]
        + 0.18 * scored["evidence_strength"] * 10.0
        + 0.16 * scored["accessibility"]
        + 0.16 * scored["legitimacy"]
        - 0.12 * scored["legal_complexity"]
        - 0.12 * scored["implementation_complexity"]
    )

    scored["public_legitimacy_index"] = (
        0.35 * scored["legitimacy"]
        + 0.25 * scored["participation_quality"] * 10.0
        + 0.20 * scored["stakeholder_coverage"] * 10.0
        + 0.20 * scored["equity"]
        - 0.10 * scored["risk"]
    )

    scored["equity_access_index"] = (
        0.35 * scored["equity"]
        + 0.25 * scored["accessibility"]
        + 0.20 * scored["burden_reduction"]
        + 0.20 * scored["stakeholder_coverage"] * 10.0
        - 0.10 * scored["legal_complexity"]
    )

    scored["learning_priority"] = (
        0.20 * scored["risk"]
        + 0.18 * scored["legal_complexity"]
        + 0.18 * scored["implementation_complexity"]
        + 0.16 * (1.0 - scored["evidence_quality"]) * 10.0
        + 0.14 * (1.0 - scored["stakeholder_coverage"]) * 10.0
        + 0.14 * (1.0 - scored["participation_quality"]) * 10.0
    )

    scored["policy_resilience"] = (
        0.28 * scored["implementation_readiness"]
        + 0.26 * scored["public_legitimacy_index"]
        + 0.24 * scored["equity_access_index"]
        + 0.22 * scored["durability"]
        - 0.15 * scored["risk"]
    )

    scored = scored.sort_values("policy_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(pilots: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_WEIGHTS}
        scored = score_pilots(pilots, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_WEIGHTS:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def analyze_policy_learning(learning: pd.DataFrame | None) -> pd.DataFrame:
    if learning is None:
        return pd.DataFrame()

    required = [
        "pilot",
        "period",
        "uptake_rate",
        "citizen_friction",
        "implementation_error",
        "trust_score",
        "equity_score",
        "appeal_access",
        "staff_workload",
        "case_resolution_time",
    ]
    missing = [col for col in required if col not in learning.columns]
    if missing:
        raise ValueError(f"Policy learning data missing required columns: {missing}")

    df = learning.copy()
    for col in required:
        if col != "pilot":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["pilot", "period"])

    df["uptake_delta"] = df.groupby("pilot")["uptake_rate"].diff()
    df["friction_delta"] = df.groupby("pilot")["citizen_friction"].diff()
    df["error_delta"] = df.groupby("pilot")["implementation_error"].diff()
    df["trust_delta"] = df.groupby("pilot")["trust_score"].diff()
    df["equity_delta"] = df.groupby("pilot")["equity_score"].diff()
    df["appeal_access_delta"] = df.groupby("pilot")["appeal_access"].diff()
    df["staff_workload_delta"] = df.groupby("pilot")["staff_workload"].diff()
    df["resolution_time_delta"] = df.groupby("pilot")["case_resolution_time"].diff()

    df["policy_learning_delta"] = (
        0.22 * df["uptake_delta"].fillna(0.0) * 10.0
        - 0.16 * df["friction_delta"].fillna(0.0)
        - 0.16 * df["error_delta"].fillna(0.0) * 10.0
        + 0.16 * df["trust_delta"].fillna(0.0)
        + 0.14 * df["equity_delta"].fillna(0.0)
        + 0.08 * df["appeal_access_delta"].fillna(0.0) * 10.0
        - 0.04 * df["staff_workload_delta"].fillna(0.0)
        - 0.04 * df["resolution_time_delta"].fillna(0.0) / 2.0
    )

    summary = (
        df.groupby("pilot")
        .agg(
            periods=("period", "max"),
            start_uptake=("uptake_rate", "first"),
            final_uptake=("uptake_rate", "last"),
            start_friction=("citizen_friction", "first"),
            final_friction=("citizen_friction", "last"),
            start_error=("implementation_error", "first"),
            final_error=("implementation_error", "last"),
            start_trust=("trust_score", "first"),
            final_trust=("trust_score", "last"),
            start_equity=("equity_score", "first"),
            final_equity=("equity_score", "last"),
            start_appeal_access=("appeal_access", "first"),
            final_appeal_access=("appeal_access", "last"),
            start_staff_workload=("staff_workload", "first"),
            final_staff_workload=("staff_workload", "last"),
            start_case_resolution_time=("case_resolution_time", "first"),
            final_case_resolution_time=("case_resolution_time", "last"),
            total_policy_learning_delta=("policy_learning_delta", "sum"),
        )
        .reset_index()
    )

    summary["uptake_gain"] = summary["final_uptake"] - summary["start_uptake"]
    summary["friction_reduction"] = summary["start_friction"] - summary["final_friction"]
    summary["error_reduction"] = summary["start_error"] - summary["final_error"]
    summary["trust_gain"] = summary["final_trust"] - summary["start_trust"]
    summary["equity_gain"] = summary["final_equity"] - summary["start_equity"]
    summary["appeal_access_gain"] = summary["final_appeal_access"] - summary["start_appeal_access"]
    summary["staff_workload_reduction"] = summary["start_staff_workload"] - summary["final_staff_workload"]
    summary["case_resolution_time_reduction"] = summary["start_case_resolution_time"] - summary["final_case_resolution_time"]

    return summary.sort_values("total_policy_learning_delta", ascending=False)


def analyze_administrative_burdens(burdens: pd.DataFrame | None) -> pd.DataFrame:
    if burdens is None:
        return pd.DataFrame()

    required = [
        "pilot",
        "learning_burden",
        "compliance_burden",
        "psychological_burden",
        "digital_burden",
        "time_burden",
        "appeal_burden",
        "staff_burden",
        "community_partner_burden",
    ]
    missing = [col for col in required if col not in burdens.columns]
    if missing:
        raise ValueError(f"Administrative burden data missing required columns: {missing}")

    df = burdens.copy()
    burden_cols = [col for col in required if col != "pilot"]
    for col in burden_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["citizen_burden_index"] = (
        0.20 * df["learning_burden"]
        + 0.22 * df["compliance_burden"]
        + 0.18 * df["psychological_burden"]
        + 0.12 * df["digital_burden"]
        + 0.16 * df["time_burden"]
        + 0.12 * df["appeal_burden"]
    )

    df["institutional_burden_index"] = (
        0.55 * df["staff_burden"]
        + 0.45 * df["community_partner_burden"]
    )

    df["total_burden_index"] = (
        0.70 * df["citizen_burden_index"]
        + 0.30 * df["institutional_burden_index"]
    )

    df["burden_transfer_risk"] = (
        df["institutional_burden_index"] - df["citizen_burden_index"]
    )

    return df.sort_values("total_burden_index", ascending=False)


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "pilot",
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
    pilots: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    winner_counts: Counter[str] = Counter()
    records: List[dict] = []

    score_columns = POSITIVE_CRITERIA + ["risk"]
    means = pilots[score_columns].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated = pilots.copy()
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)
        simulated[score_columns] = simulated_scores

        scored = score_pilots(simulated, weights)
        winner_counts[str(scored.iloc[0]["pilot"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "pilot": row["pilot"],
                    "policy_domain": row["policy_domain"],
                    "pilot_type": row["pilot_type"],
                    "policy_value": float(row["policy_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "implementation_readiness": float(row["implementation_readiness"]),
                    "public_legitimacy_index": float(row["public_legitimacy_index"]),
                    "equity_access_index": float(row["equity_access_index"]),
                    "policy_resilience": float(row["policy_resilience"]),
                    "learning_priority": float(row["learning_priority"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "pilot": pilot,
                    "times_ranked_first": count,
                    "probability_ranked_first": count / simulations,
                }
                for pilot, count in winner_counts.items()
            ]
        )
        .sort_values("probability_ranked_first", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_stability(
    pilots: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = pilots.sample(
            n=len(pilots),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_pilots(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "pilot": row["pilot"],
                    "policy_value": float(row["policy_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "public_legitimacy_index": float(row["public_legitimacy_index"]),
                    "equity_access_index": float(row["equity_access_index"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("pilot")
        .agg(
            mean_policy_value=("policy_value", "mean"),
            sd_policy_value=("policy_value", "std"),
            mean_evidence_adjusted_value=("evidence_adjusted_value", "mean"),
            mean_public_legitimacy_index=("public_legitimacy_index", "mean"),
            mean_equity_access_index=("equity_access_index", "mean"),
            median_rank=("rank", "median"),
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
        )
        .reset_index()
        .sort_values(["median_rank", "mean_rank"])
    )


def random_weight_sensitivity(
    pilots: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()

    for _ in range(samples):
        arr = rng.dirichlet(np.ones(len(CORE_WEIGHTS)))
        weights = dict(zip(CORE_WEIGHTS, arr))
        scored = score_pilots(pilots, weights)
        winner_counts[str(scored.iloc[0]["pilot"])] += 1

    return (
        pd.DataFrame(
            [
                {
                    "pilot": pilot,
                    "times_won": count,
                    "probability_winning_under_random_weights": count / samples,
                }
                for pilot, count in winner_counts.items()
            ]
        )
        .sort_values("probability_winning_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="pilot",
        columns="scenario",
        values="policy_value",
        aggfunc="first",
    )
    ax = pivot.plot(kind="bar", figsize=(14, 7))
    ax.set_title("Public Policy Pilot Value Across Strategic Scenarios")
    ax.set_xlabel("Policy pilot")
    ax.set_ylabel("Weighted public design value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["pilot"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for Public Policy Pilots")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Policy pilot")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_policy_learning(learning_summary: pd.DataFrame, output_path: Path) -> None:
    if learning_summary.empty:
        return
    plot_df = learning_summary.sort_values("total_policy_learning_delta", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["pilot"], plot_df["total_policy_learning_delta"])
    plt.title("Policy Learning Delta Across Public Policy Pilots")
    plt.xlabel("Total policy learning delta")
    plt.ylabel("Policy pilot")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_burdens(burden_summary: pd.DataFrame, output_path: Path) -> None:
    if burden_summary.empty:
        return
    plot_df = burden_summary.sort_values("total_burden_index", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["pilot"], plot_df["total_burden_index"])
    plt.title("Administrative Burden Index Across Public Policy Pilots")
    plt.xlabel("Total burden index")
    plt.ylabel("Policy pilot")
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
    pilots: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    learning_summary: pd.DataFrame,
    burden_summary: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    balanced = scenario_results[scenario_results["scenario"].str.lower() == "balanced"]
    top = balanced.sort_values("rank").head(1)
    top_name = top.iloc[0]["pilot"] if not top.empty else "Not available"
    top_value = float(top.iloc[0]["policy_value"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    learning_section = "No policy-learning pathway data provided."
    if not learning_summary.empty:
        learning_section = dataframe_to_markdown_safe(learning_summary)

    burden_section = "No administrative-burden data provided."
    if not burden_summary.empty:
        burden_section = dataframe_to_markdown_safe(burden_summary)

    risk_section = "No risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Design Thinking in Public Policy Report

## Article

Design Thinking in Public Policy

## Summary

This report compares public-policy pilot concepts using transparent multi-criteria scoring, scenario analysis, evidence-strength diagnostics, administrative-burden analysis, legitimacy and equity indexes, policy-learning pathways, risk-register priority, uncertainty modeling, bootstrap stability, and random-weight sensitivity.

## Balanced scenario leader

- Pilot: **{top_name}**
- Weighted public design value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_a A_i + w_f F_i + w_l L_i + w_e E_i + w_b B_i + w_d D_i - w_r R_i
\\]

## Portfolio size

{len(pilots)}

## Scenario count

{len(scenarios)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Policy-learning summary

{learning_section}

## Administrative-burden summary

{burden_section}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate public-policy decisions. They support structured deliberation about accessibility, feasibility, legitimacy, equity, burden reduction, implementation durability, risk, evidence strength, stakeholder coverage, participation quality, administrative burden, and policy learning. A high-scoring pilot may still require legal review, democratic review, community engagement, privacy assessment, accessibility testing, implementation analysis, civil-rights review, budget review, and long-term evaluation before scale.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional public-policy design pilot engine.")
    parser.add_argument(
        "--pilots",
        type=Path,
        default=Path("../data/raw/public_policy_pilots_raw.csv"),
        help="Public policy pilots CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/public_policy_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--learning",
        type=Path,
        default=Path("../data/raw/policy_learning_pathways_raw.csv"),
        help="Policy-learning pathways CSV.",
    )
    parser.add_argument(
        "--burdens",
        type=Path,
        default=Path("../data/raw/administrative_burden_raw.csv"),
        help="Administrative burden CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/public_policy_risk_register_raw.csv"),
        help="Public policy risk register CSV.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.6)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        pilots_path=args.pilots,
        weights_path=args.weights if args.weights.exists() else None,
        learning_path=args.learning if args.learning.exists() else None,
        burdens_path=args.burdens if args.burdens.exists() else None,
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

    pilots = read_pilots(config.pilots_path)
    scenarios = read_weights(config.weights_path)
    learning = read_optional_csv(config.learning_path)
    burdens = read_optional_csv(config.burdens_path)
    risk_register = read_optional_csv(config.risk_register_path)

    issues = validate_pilots(pilots)
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

    scenario_results = run_scenario_analysis(pilots, scenarios)
    learning_summary = analyze_policy_learning(learning)
    burden_summary = analyze_administrative_burdens(burdens)
    risk_summary = analyze_risk_register(risk_register)

    winners, simulation_values = monte_carlo_rank_stability(
        pilots=pilots,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap = bootstrap_stability(
        pilots=pilots,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        pilots=pilots,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    review_priority = (
        score_pilots(pilots, balanced_weights)
        .sort_values("learning_priority", ascending=False)
        [
            [
                "pilot",
                "policy_domain",
                "pilot_type",
                "policy_value",
                "evidence_adjusted_value",
                "implementation_readiness",
                "public_legitimacy_index",
                "equity_access_index",
                "policy_resilience",
                "learning_priority",
            ]
        ]
    )

    scenario_results.to_csv(config.output_dir / "public_policy_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "public_policy_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "public_policy_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "public_policy_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "public_policy_weight_sensitivity.csv", index=False)
    review_priority.to_csv(config.output_dir / "public_policy_learning_priority.csv", index=False)

    if not learning_summary.empty:
        learning_summary.to_csv(config.output_dir / "policy_learning_pathway_summary.csv", index=False)

    if not burden_summary.empty:
        burden_summary.to_csv(config.output_dir / "administrative_burden_summary.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "public_policy_risk_register_priority.csv", index=False)

    save_plot_scenario_values(scenario_results, config.output_dir / "public_policy_scenario_values.png")
    save_plot_rank_stability(winners, config.output_dir / "public_policy_rank_stability.png")
    save_plot_policy_learning(learning_summary, config.output_dir / "policy_learning_delta.png")
    save_plot_burdens(burden_summary, config.output_dir / "administrative_burden_index.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "pilots_path": str(config.pilots_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "learning_path": str(config.learning_path) if config.learning_path else None,
                "burdens_path": str(config.burdens_path) if config.burdens_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "model": "V_i = w_a A_i + w_f F_i + w_l L_i + w_e E_i + w_b B_i + w_d D_i - w_r R_i",
        },
    )

    report = build_report(
        pilots=pilots,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        learning_summary=learning_summary,
        burden_summary=burden_summary,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "public_policy_design_report.md").write_text(report, encoding="utf-8")

    print("Public policy design analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- public_policy_scenario_results.csv")
    print("- public_policy_monte_carlo_winners.csv")
    print("- public_policy_weight_sensitivity.csv")
    print("- policy_learning_pathway_summary.csv")
    print("- administrative_burden_summary.csv")
    print("- public_policy_learning_priority.csv")
    print("- public_policy_design_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
