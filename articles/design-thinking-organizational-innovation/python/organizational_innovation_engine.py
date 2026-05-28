#!/usr/bin/env python3
"""
Professional organizational innovation decision-support engine.

This script compares organizational innovation concepts across desirability,
feasibility, viability, equity, learning value, implementation readiness, risk,
evidence quality, stakeholder coverage, technical complexity, organizational
complexity, and ethical risk. It also analyzes prototype-learning pathways,
organizational friction, risk-register priority, Monte Carlo uncertainty,
bootstrap stability, and random-weight sensitivity.

The model is intentionally interpretable:

    V_i = w_d D_i + w_f F_i + w_v V_i + w_e E_i + w_l L_i + w_m M_i - w_r R_i

where:
    D_i = desirability and stakeholder value
    F_i = feasibility
    V_i = viability
    E_i = equity and ethical adequacy
    L_i = learning value
    M_i = implementation readiness
    R_i = implementation and unintended-consequence risk

This workflow supports organizational design deliberation and documentation.
It does not automate strategic, personnel, ethical, or governance decisions.
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
    "equity",
    "learning_value",
    "implementation_readiness",
]

CORE_WEIGHTS = [*POSITIVE_CRITERIA, "risk"]


@dataclass(frozen=True)
class EngineConfig:
    concepts_path: Path
    weights_path: Path | None
    learning_path: Path | None
    friction_path: Path | None
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
        raise FileNotFoundError(f"Organizational innovation concepts file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "concept",
        "concept_type",
        "organizational_domain",
        *POSITIVE_CRITERIA,
        "risk",
        "evidence_quality",
        "stakeholder_coverage",
        "technical_complexity",
        "organizational_complexity",
        "ethical_risk",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Organizational innovation concepts missing required columns: {missing}")

    df = df.copy()
    for col in ["concept", "concept_type", "organizational_domain"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = (
        POSITIVE_CRITERIA
        + [
            "risk",
            "evidence_quality",
            "stakeholder_coverage",
            "technical_complexity",
            "organizational_complexity",
            "ethical_risk",
        ]
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
                    "desirability": 0.22,
                    "feasibility": 0.16,
                    "viability": 0.16,
                    "equity": 0.18,
                    "learning_value": 0.12,
                    "implementation_readiness": 0.10,
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

    for col in POSITIVE_CRITERIA + ["risk", "technical_complexity", "organizational_complexity", "ethical_risk"]:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    for col in ["evidence_quality", "stakeholder_coverage"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Evidence and stakeholder coverage indicators should be in [0, 1].",
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


def score_concepts(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["evidence_strength"] = (
        0.55 * scored["evidence_quality"]
        + 0.45 * scored["stakeholder_coverage"]
    ).clip(0.0, 1.0)

    scored["design_value"] = (
        weights["desirability"] * scored["desirability"]
        + weights["feasibility"] * scored["feasibility"]
        + weights["viability"] * scored["viability"]
        + weights["equity"] * scored["equity"]
        + weights["learning_value"] * scored["learning_value"]
        + weights["implementation_readiness"] * scored["implementation_readiness"]
        - weights["risk"] * scored["risk"]
    )

    scored["evidence_adjusted_value"] = (
        scored["design_value"] * (0.75 + 0.25 * scored["evidence_strength"])
    )

    scored["implementation_resilience"] = (
        0.26 * scored["implementation_readiness"]
        + 0.22 * scored["feasibility"]
        + 0.18 * scored["viability"]
        + 0.16 * scored["evidence_strength"] * 10.0
        - 0.09 * scored["technical_complexity"]
        - 0.09 * scored["organizational_complexity"]
    )

    scored["ethical_innovation_index"] = (
        0.34 * scored["equity"]
        + 0.22 * scored["stakeholder_coverage"] * 10.0
        + 0.18 * scored["desirability"]
        + 0.16 * scored["learning_value"]
        - 0.10 * scored["ethical_risk"]
    )

    scored["organizational_learning_index"] = (
        0.30 * scored["learning_value"]
        + 0.22 * scored["evidence_strength"] * 10.0
        + 0.18 * scored["stakeholder_coverage"] * 10.0
        + 0.16 * scored["implementation_readiness"]
        - 0.07 * scored["risk"]
        - 0.07 * scored["organizational_complexity"]
    )

    scored["learning_priority"] = (
        0.22 * scored["risk"]
        + 0.18 * scored["technical_complexity"]
        + 0.18 * scored["organizational_complexity"]
        + 0.16 * scored["ethical_risk"]
        + 0.14 * (1.0 - scored["evidence_quality"]) * 10.0
        + 0.12 * (1.0 - scored["stakeholder_coverage"]) * 10.0
    )

    scored["portfolio_strength"] = (
        0.30 * scored["design_value"]
        + 0.24 * scored["implementation_resilience"]
        + 0.24 * scored["ethical_innovation_index"]
        + 0.22 * scored["organizational_learning_index"]
        - 0.12 * scored["risk"]
    )

    scored = scored.sort_values("design_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(concepts: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_WEIGHTS}
        scored = score_concepts(concepts, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_WEIGHTS:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def analyze_prototype_learning(learning: pd.DataFrame | None) -> pd.DataFrame:
    if learning is None:
        return pd.DataFrame()

    required = [
        "concept",
        "round",
        "adoption_likelihood",
        "user_friction",
        "trust_score",
        "operational_burden",
        "equity_score",
        "task_success_rate",
        "cycle_time",
        "employee_confidence",
    ]
    missing = [col for col in required if col not in learning.columns]
    if missing:
        raise ValueError(f"Prototype learning data missing required columns: {missing}")

    df = learning.copy()
    for col in required:
        if col != "concept":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["concept", "round"])

    df["adoption_delta"] = df.groupby("concept")["adoption_likelihood"].diff()
    df["friction_delta"] = df.groupby("concept")["user_friction"].diff()
    df["trust_delta"] = df.groupby("concept")["trust_score"].diff()
    df["burden_delta"] = df.groupby("concept")["operational_burden"].diff()
    df["equity_delta"] = df.groupby("concept")["equity_score"].diff()
    df["task_success_delta"] = df.groupby("concept")["task_success_rate"].diff()
    df["cycle_time_delta"] = df.groupby("concept")["cycle_time"].diff()
    df["employee_confidence_delta"] = df.groupby("concept")["employee_confidence"].diff()

    df["prototype_learning_delta"] = (
        0.20 * df["adoption_delta"].fillna(0.0) * 10.0
        - 0.16 * df["friction_delta"].fillna(0.0)
        + 0.16 * df["trust_delta"].fillna(0.0)
        - 0.14 * df["burden_delta"].fillna(0.0)
        + 0.14 * df["equity_delta"].fillna(0.0)
        + 0.10 * df["task_success_delta"].fillna(0.0) * 10.0
        - 0.05 * df["cycle_time_delta"].fillna(0.0) / 2.0
        + 0.05 * df["employee_confidence_delta"].fillna(0.0)
    )

    summary = (
        df.groupby("concept")
        .agg(
            rounds=("round", "max"),
            start_adoption=("adoption_likelihood", "first"),
            final_adoption=("adoption_likelihood", "last"),
            start_friction=("user_friction", "first"),
            final_friction=("user_friction", "last"),
            start_trust=("trust_score", "first"),
            final_trust=("trust_score", "last"),
            start_burden=("operational_burden", "first"),
            final_burden=("operational_burden", "last"),
            start_equity=("equity_score", "first"),
            final_equity=("equity_score", "last"),
            start_task_success=("task_success_rate", "first"),
            final_task_success=("task_success_rate", "last"),
            start_cycle_time=("cycle_time", "first"),
            final_cycle_time=("cycle_time", "last"),
            start_employee_confidence=("employee_confidence", "first"),
            final_employee_confidence=("employee_confidence", "last"),
            total_prototype_learning_delta=("prototype_learning_delta", "sum"),
        )
        .reset_index()
    )

    summary["adoption_gain"] = summary["final_adoption"] - summary["start_adoption"]
    summary["friction_reduction"] = summary["start_friction"] - summary["final_friction"]
    summary["trust_gain"] = summary["final_trust"] - summary["start_trust"]
    summary["burden_reduction"] = summary["start_burden"] - summary["final_burden"]
    summary["equity_gain"] = summary["final_equity"] - summary["start_equity"]
    summary["task_success_gain"] = summary["final_task_success"] - summary["start_task_success"]
    summary["cycle_time_reduction"] = summary["start_cycle_time"] - summary["final_cycle_time"]
    summary["employee_confidence_gain"] = summary["final_employee_confidence"] - summary["start_employee_confidence"]

    return summary.sort_values("total_prototype_learning_delta", ascending=False)


def analyze_organizational_friction(friction: pd.DataFrame | None) -> pd.DataFrame:
    if friction is None:
        return pd.DataFrame()

    required = [
        "concept",
        "silo_friction",
        "decision_latency",
        "legacy_system_constraint",
        "metric_misalignment",
        "training_gap",
        "ownership_ambiguity",
        "frontline_workload",
        "governance_gap",
    ]
    missing = [col for col in required if col not in friction.columns]
    if missing:
        raise ValueError(f"Organizational friction data missing required columns: {missing}")

    df = friction.copy()
    friction_cols = [col for col in required if col != "concept"]
    for col in friction_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["coordination_friction_index"] = (
        0.24 * df["silo_friction"]
        + 0.24 * df["decision_latency"]
        + 0.20 * df["ownership_ambiguity"]
        + 0.16 * df["metric_misalignment"]
        + 0.16 * df["governance_gap"]
    )

    df["implementation_friction_index"] = (
        0.24 * df["legacy_system_constraint"]
        + 0.22 * df["training_gap"]
        + 0.22 * df["frontline_workload"]
        + 0.18 * df["governance_gap"]
        + 0.14 * df["decision_latency"]
    )

    df["total_friction_index"] = (
        0.52 * df["coordination_friction_index"]
        + 0.48 * df["implementation_friction_index"]
    )

    df["friction_attention_priority"] = (
        0.30 * df["total_friction_index"]
        + 0.20 * df["governance_gap"]
        + 0.20 * df["ownership_ambiguity"]
        + 0.15 * df["frontline_workload"]
        + 0.15 * df["legacy_system_constraint"]
    )

    return df.sort_values("friction_attention_priority", ascending=False)


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

    score_columns = POSITIVE_CRITERIA + ["risk"]
    means = concepts[score_columns].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated = concepts.copy()
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)
        simulated[score_columns] = simulated_scores

        scored = score_concepts(simulated, weights)
        winner_counts[str(scored.iloc[0]["concept"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "concept": row["concept"],
                    "concept_type": row["concept_type"],
                    "organizational_domain": row["organizational_domain"],
                    "design_value": float(row["design_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "implementation_resilience": float(row["implementation_resilience"]),
                    "ethical_innovation_index": float(row["ethical_innovation_index"]),
                    "organizational_learning_index": float(row["organizational_learning_index"]),
                    "portfolio_strength": float(row["portfolio_strength"]),
                    "learning_priority": float(row["learning_priority"]),
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
        scored = score_concepts(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "concept": row["concept"],
                    "design_value": float(row["design_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "ethical_innovation_index": float(row["ethical_innovation_index"]),
                    "implementation_resilience": float(row["implementation_resilience"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("concept")
        .agg(
            mean_design_value=("design_value", "mean"),
            sd_design_value=("design_value", "std"),
            mean_evidence_adjusted_value=("evidence_adjusted_value", "mean"),
            mean_ethical_innovation_index=("ethical_innovation_index", "mean"),
            mean_implementation_resilience=("implementation_resilience", "mean"),
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
        scored = score_concepts(concepts, weights)
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
        values="design_value",
        aggfunc="first",
    )
    ax = pivot.plot(kind="bar", figsize=(14, 7))
    ax.set_title("Organizational Innovation Value Across Strategic Scenarios")
    ax.set_xlabel("Innovation concept")
    ax.set_ylabel("Weighted design value")
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
    plt.title("Monte Carlo Rank Stability for Organizational Innovation Concepts")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Innovation concept")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_prototype_learning(learning_summary: pd.DataFrame, output_path: Path) -> None:
    if learning_summary.empty:
        return
    plot_df = learning_summary.sort_values("total_prototype_learning_delta", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["concept"], plot_df["total_prototype_learning_delta"])
    plt.title("Prototype Learning Delta Across Organizational Innovation Concepts")
    plt.xlabel("Total prototype learning delta")
    plt.ylabel("Innovation concept")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_friction(friction_summary: pd.DataFrame, output_path: Path) -> None:
    if friction_summary.empty:
        return
    plot_df = friction_summary.sort_values("friction_attention_priority", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["concept"], plot_df["friction_attention_priority"])
    plt.title("Organizational Friction Attention Priority")
    plt.xlabel("Friction attention priority")
    plt.ylabel("Innovation concept")
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
    learning_summary: pd.DataFrame,
    friction_summary: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    balanced = scenario_results[scenario_results["scenario"].str.lower() == "balanced"]
    top = balanced.sort_values("rank").head(1)
    top_name = top.iloc[0]["concept"] if not top.empty else "Not available"
    top_value = float(top.iloc[0]["design_value"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    learning_section = "No prototype-learning data provided."
    if not learning_summary.empty:
        learning_section = dataframe_to_markdown_safe(learning_summary)

    friction_section = "No organizational-friction data provided."
    if not friction_summary.empty:
        friction_section = dataframe_to_markdown_safe(friction_summary)

    risk_section = "No risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Design Thinking and Organizational Innovation Report

## Article

Design Thinking and Organizational Innovation

## Summary

This report compares organizational innovation concepts using transparent multi-criteria scoring, scenario analysis, evidence-strength diagnostics, ethical innovation review, implementation-resilience analysis, prototype-learning pathways, organizational-friction analysis, risk-register priority, uncertainty modeling, bootstrap stability, and random-weight sensitivity.

## Balanced scenario leader

- Concept: **{top_name}**
- Weighted design value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_d D_i + w_f F_i + w_v V_i + w_e E_i + w_l L_i + w_m M_i - w_r R_i
\\]

## Portfolio size

{len(concepts)}

## Scenario count

{len(scenarios)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Prototype-learning summary

{learning_section}

## Organizational-friction summary

{friction_section}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate organizational innovation decisions. They support structured deliberation about desirability, feasibility, viability, equity, learning value, implementation readiness, risk, evidence strength, stakeholder coverage, organizational friction, ethical risk, and prototype learning. A high-scoring concept may still require qualitative research, employee participation, technical review, labor review, accessibility review, AI governance review, privacy review, budget review, leadership sponsorship, and implementation testing before scale.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional organizational innovation concept engine.")
    parser.add_argument(
        "--concepts",
        type=Path,
        default=Path("../data/raw/organizational_innovation_concepts_raw.csv"),
        help="Organizational innovation concepts CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/innovation_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--learning",
        type=Path,
        default=Path("../data/raw/prototype_learning_rounds_raw.csv"),
        help="Prototype learning rounds CSV.",
    )
    parser.add_argument(
        "--friction",
        type=Path,
        default=Path("../data/raw/organizational_friction_raw.csv"),
        help="Organizational friction CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/innovation_risk_register_raw.csv"),
        help="Innovation risk register CSV.",
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
        learning_path=args.learning if args.learning.exists() else None,
        friction_path=args.friction if args.friction.exists() else None,
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
    learning = read_optional_csv(config.learning_path)
    friction = read_optional_csv(config.friction_path)
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
    learning_summary = analyze_prototype_learning(learning)
    friction_summary = analyze_organizational_friction(friction)
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
        score_concepts(concepts, balanced_weights)
        .sort_values("learning_priority", ascending=False)
        [
            [
                "concept",
                "concept_type",
                "organizational_domain",
                "design_value",
                "evidence_adjusted_value",
                "implementation_resilience",
                "ethical_innovation_index",
                "organizational_learning_index",
                "portfolio_strength",
                "learning_priority",
            ]
        ]
    )

    scenario_results.to_csv(config.output_dir / "organizational_innovation_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "organizational_innovation_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "organizational_innovation_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "organizational_innovation_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "organizational_innovation_weight_sensitivity.csv", index=False)
    review_priority.to_csv(config.output_dir / "organizational_innovation_learning_priority.csv", index=False)

    if not learning_summary.empty:
        learning_summary.to_csv(config.output_dir / "prototype_learning_summary.csv", index=False)

    if not friction_summary.empty:
        friction_summary.to_csv(config.output_dir / "organizational_friction_summary.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "innovation_risk_register_priority.csv", index=False)

    save_plot_scenario_values(scenario_results, config.output_dir / "organizational_innovation_scenario_values.png")
    save_plot_rank_stability(winners, config.output_dir / "organizational_innovation_rank_stability.png")
    save_plot_prototype_learning(learning_summary, config.output_dir / "prototype_learning_delta.png")
    save_plot_friction(friction_summary, config.output_dir / "organizational_friction_priority.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "concepts_path": str(config.concepts_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "learning_path": str(config.learning_path) if config.learning_path else None,
                "friction_path": str(config.friction_path) if config.friction_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "model": "V_i = w_d D_i + w_f F_i + w_v V_i + w_e E_i + w_l L_i + w_m M_i - w_r R_i",
        },
    )

    report = build_report(
        concepts=concepts,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        learning_summary=learning_summary,
        friction_summary=friction_summary,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "organizational_innovation_report.md").write_text(report, encoding="utf-8")

    print("Organizational innovation analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- organizational_innovation_scenario_results.csv")
    print("- organizational_innovation_monte_carlo_winners.csv")
    print("- organizational_innovation_weight_sensitivity.csv")
    print("- prototype_learning_summary.csv")
    print("- organizational_friction_summary.csv")
    print("- organizational_innovation_learning_priority.csv")
    print("- organizational_innovation_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
