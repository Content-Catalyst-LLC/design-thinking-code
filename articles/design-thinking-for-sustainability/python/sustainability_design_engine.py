#!/usr/bin/env python3
"""
Professional sustainability design decision-support engine.

This script compares sustainability design concepts across usability,
feasibility, ecological benefit, circularity, equity, durability, risk,
evidence quality, stakeholder coverage, lifecycle boundary quality,
burden-shift risk, and implementation complexity. It also analyzes
transition pathways, risk-register priority, Monte Carlo uncertainty,
bootstrap stability, and random-weight sensitivity.

The model is intentionally interpretable:

    V_i = w_u U_i + w_f F_i + w_e E_i + w_c C_i + w_q Q_i + w_d D_i - w_r R_i

where:
    U_i = usability and stakeholder adoption value
    F_i = feasibility
    E_i = ecological benefit
    C_i = circularity and material stewardship
    Q_i = equity and justice performance
    D_i = durability
    R_i = implementation and unintended-consequence risk

This workflow supports sustainability design deliberation and documentation.
It does not automate ecological, policy, lifecycle, or justice judgments.
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
    "usability",
    "feasibility",
    "ecological_benefit",
    "circularity",
    "equity",
    "durability",
]

CORE_WEIGHTS = [*POSITIVE_CRITERIA, "risk"]


@dataclass(frozen=True)
class EngineConfig:
    concepts_path: Path
    weights_path: Path | None
    transitions_path: Path | None
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
        raise FileNotFoundError(f"Sustainability concepts file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "concept",
        "concept_type",
        "transition_domain",
        *POSITIVE_CRITERIA,
        "risk",
        "evidence_quality",
        "stakeholder_coverage",
        "lifecycle_boundary_quality",
        "burden_shift_risk",
        "implementation_complexity",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Sustainability concepts missing required columns: {missing}")

    df = df.copy()
    for col in ["concept", "concept_type", "transition_domain"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = (
        POSITIVE_CRITERIA
        + ["risk", "evidence_quality", "stakeholder_coverage", "lifecycle_boundary_quality", "burden_shift_risk", "implementation_complexity"]
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
                    "usability": 0.16,
                    "feasibility": 0.16,
                    "ecological_benefit": 0.24,
                    "circularity": 0.16,
                    "equity": 0.14,
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

    for col in POSITIVE_CRITERIA + ["risk", "burden_shift_risk", "implementation_complexity"]:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    for col in ["evidence_quality", "stakeholder_coverage", "lifecycle_boundary_quality"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Evidence and lifecycle-quality indicators should be in [0, 1].",
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
        0.35 * scored["evidence_quality"]
        + 0.30 * scored["stakeholder_coverage"]
        + 0.35 * scored["lifecycle_boundary_quality"]
    ).clip(0.0, 1.0)

    scored["sustainability_value"] = (
        weights["usability"] * scored["usability"]
        + weights["feasibility"] * scored["feasibility"]
        + weights["ecological_benefit"] * scored["ecological_benefit"]
        + weights["circularity"] * scored["circularity"]
        + weights["equity"] * scored["equity"]
        + weights["durability"] * scored["durability"]
        - weights["risk"] * scored["risk"]
    )

    scored["evidence_adjusted_value"] = (
        scored["sustainability_value"] * (0.75 + 0.25 * scored["evidence_strength"])
    )

    scored["transition_readiness"] = (
        0.24 * scored["usability"]
        + 0.22 * scored["feasibility"]
        + 0.18 * scored["stakeholder_coverage"] * 10.0
        + 0.18 * scored["durability"]
        + 0.18 * scored["evidence_strength"] * 10.0
        - 0.12 * scored["implementation_complexity"]
    )

    scored["ecological_integrity_index"] = (
        0.40 * scored["ecological_benefit"]
        + 0.25 * scored["circularity"]
        + 0.20 * scored["lifecycle_boundary_quality"] * 10.0
        + 0.15 * scored["durability"]
        - 0.12 * scored["risk"]
    )

    scored["justice_burden_index"] = (
        0.40 * scored["equity"]
        + 0.25 * scored["stakeholder_coverage"] * 10.0
        + 0.20 * scored["usability"]
        - 0.15 * scored["burden_shift_risk"]
    )

    scored["learning_priority"] = (
        0.22 * scored["risk"]
        + 0.18 * scored["implementation_complexity"]
        + 0.17 * scored["burden_shift_risk"]
        + 0.16 * (1.0 - scored["evidence_quality"]) * 10.0
        + 0.14 * (1.0 - scored["stakeholder_coverage"]) * 10.0
        + 0.13 * (1.0 - scored["lifecycle_boundary_quality"]) * 10.0
    )

    scored["portfolio_resilience"] = (
        0.30 * scored["durability"]
        + 0.25 * scored["transition_readiness"]
        + 0.25 * scored["ecological_integrity_index"]
        + 0.20 * scored["justice_burden_index"]
        - 0.12 * scored["risk"]
    )

    scored = scored.sort_values("sustainability_value", ascending=False).reset_index(drop=True)
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


def analyze_transitions(transitions: pd.DataFrame | None) -> pd.DataFrame:
    if transitions is None:
        return pd.DataFrame()

    required = [
        "concept",
        "period",
        "adoption_rate",
        "friction_score",
        "ecological_impact_reduction",
        "equity_score",
        "implementation_cost",
        "maintenance_burden",
        "trust_score",
        "participation_quality",
    ]
    missing = [col for col in required if col not in transitions.columns]
    if missing:
        raise ValueError(f"Transition pathway data missing required columns: {missing}")

    df = transitions.copy()
    for col in required:
        if col != "concept":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["concept", "period"])

    df["adoption_delta"] = df.groupby("concept")["adoption_rate"].diff()
    df["friction_delta"] = df.groupby("concept")["friction_score"].diff()
    df["ecological_delta"] = df.groupby("concept")["ecological_impact_reduction"].diff()
    df["equity_delta"] = df.groupby("concept")["equity_score"].diff()
    df["cost_delta"] = df.groupby("concept")["implementation_cost"].diff()
    df["maintenance_delta"] = df.groupby("concept")["maintenance_burden"].diff()
    df["trust_delta"] = df.groupby("concept")["trust_score"].diff()
    df["participation_delta"] = df.groupby("concept")["participation_quality"].diff()

    df["transition_learning_delta"] = (
        0.22 * df["adoption_delta"].fillna(0.0) * 10.0
        - 0.18 * df["friction_delta"].fillna(0.0)
        + 0.24 * df["ecological_delta"].fillna(0.0) * 10.0
        + 0.18 * df["equity_delta"].fillna(0.0)
        - 0.07 * df["cost_delta"].fillna(0.0)
        - 0.05 * df["maintenance_delta"].fillna(0.0)
        + 0.04 * df["trust_delta"].fillna(0.0)
        + 0.02 * df["participation_delta"].fillna(0.0) * 10.0
    )

    summary = (
        df.groupby("concept")
        .agg(
            periods=("period", "max"),
            start_adoption=("adoption_rate", "first"),
            final_adoption=("adoption_rate", "last"),
            start_friction=("friction_score", "first"),
            final_friction=("friction_score", "last"),
            start_ecological_reduction=("ecological_impact_reduction", "first"),
            final_ecological_reduction=("ecological_impact_reduction", "last"),
            start_equity=("equity_score", "first"),
            final_equity=("equity_score", "last"),
            start_cost=("implementation_cost", "first"),
            final_cost=("implementation_cost", "last"),
            start_maintenance=("maintenance_burden", "first"),
            final_maintenance=("maintenance_burden", "last"),
            start_trust=("trust_score", "first"),
            final_trust=("trust_score", "last"),
            start_participation=("participation_quality", "first"),
            final_participation=("participation_quality", "last"),
            total_transition_learning_delta=("transition_learning_delta", "sum"),
        )
        .reset_index()
    )

    summary["adoption_gain"] = summary["final_adoption"] - summary["start_adoption"]
    summary["friction_reduction"] = summary["start_friction"] - summary["final_friction"]
    summary["ecological_reduction_gain"] = summary["final_ecological_reduction"] - summary["start_ecological_reduction"]
    summary["equity_gain"] = summary["final_equity"] - summary["start_equity"]
    summary["cost_reduction"] = summary["start_cost"] - summary["final_cost"]
    summary["maintenance_reduction"] = summary["start_maintenance"] - summary["final_maintenance"]
    summary["trust_gain"] = summary["final_trust"] - summary["start_trust"]
    summary["participation_gain"] = summary["final_participation"] - summary["start_participation"]

    return summary.sort_values("total_transition_learning_delta", ascending=False)


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
                    "transition_domain": row["transition_domain"],
                    "sustainability_value": float(row["sustainability_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "transition_readiness": float(row["transition_readiness"]),
                    "ecological_integrity_index": float(row["ecological_integrity_index"]),
                    "justice_burden_index": float(row["justice_burden_index"]),
                    "portfolio_resilience": float(row["portfolio_resilience"]),
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
                    "sustainability_value": float(row["sustainability_value"]),
                    "evidence_adjusted_value": float(row["evidence_adjusted_value"]),
                    "ecological_integrity_index": float(row["ecological_integrity_index"]),
                    "justice_burden_index": float(row["justice_burden_index"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("concept")
        .agg(
            mean_sustainability_value=("sustainability_value", "mean"),
            sd_sustainability_value=("sustainability_value", "std"),
            mean_evidence_adjusted_value=("evidence_adjusted_value", "mean"),
            mean_ecological_integrity_index=("ecological_integrity_index", "mean"),
            mean_justice_burden_index=("justice_burden_index", "mean"),
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
        values="sustainability_value",
        aggfunc="first",
    )
    ax = pivot.plot(kind="bar", figsize=(14, 7))
    ax.set_title("Sustainability Concept Value Across Strategic Scenarios")
    ax.set_xlabel("Concept")
    ax.set_ylabel("Weighted sustainability value")
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
    plt.title("Monte Carlo Rank Stability for Sustainability Concepts")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Concept")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_transition_learning(transition_summary: pd.DataFrame, output_path: Path) -> None:
    if transition_summary.empty:
        return
    plot_df = transition_summary.sort_values("total_transition_learning_delta", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["concept"], plot_df["total_transition_learning_delta"])
    plt.title("Transition Learning Delta Across Sustainability Concepts")
    plt.xlabel("Total transition learning delta")
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
    transition_summary: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    balanced = scenario_results[scenario_results["scenario"].str.lower() == "balanced"]
    top = balanced.sort_values("rank").head(1)
    top_name = top.iloc[0]["concept"] if not top.empty else "Not available"
    top_value = float(top.iloc[0]["sustainability_value"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    transition_section = "No transition pathway data provided."
    if not transition_summary.empty:
        transition_section = dataframe_to_markdown_safe(transition_summary)

    risk_section = "No risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Design Thinking for Sustainability Report

## Article

Design Thinking for Sustainability

## Summary

This report compares sustainability design concepts using transparent multi-criteria scoring, scenario analysis, evidence-strength diagnostics, lifecycle-boundary review, transition-pathway learning, risk-register priority, uncertainty modeling, bootstrap stability, and random-weight sensitivity.

## Balanced scenario leader

- Concept: **{top_name}**
- Weighted sustainability value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_u U_i + w_f F_i + w_e E_i + w_c C_i + w_q Q_i + w_d D_i - w_r R_i
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

## Transition pathway summary

{transition_section}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate sustainability decisions. They support structured deliberation about ecological benefit, circularity, usability, feasibility, equity, durability, risk, lifecycle evidence, burden shifting, implementation complexity, and transition learning. A high-scoring concept may still require additional lifecycle assessment, community review, governance review, labor analysis, ecological expertise, and long-term evaluation before scale.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional sustainability design concept engine.")
    parser.add_argument(
        "--concepts",
        type=Path,
        default=Path("../data/raw/sustainability_concepts_raw.csv"),
        help="Sustainability concepts CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/sustainability_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--transitions",
        type=Path,
        default=Path("../data/raw/transition_pathways_raw.csv"),
        help="Transition pathways CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/sustainability_risk_register_raw.csv"),
        help="Sustainability risk register CSV.",
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
        transitions_path=args.transitions if args.transitions.exists() else None,
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
    transitions = read_optional_csv(config.transitions_path)
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
    transition_summary = analyze_transitions(transitions)
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
                "transition_domain",
                "sustainability_value",
                "evidence_adjusted_value",
                "transition_readiness",
                "ecological_integrity_index",
                "justice_burden_index",
                "portfolio_resilience",
                "learning_priority",
            ]
        ]
    )

    scenario_results.to_csv(config.output_dir / "sustainability_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "sustainability_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "sustainability_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "sustainability_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "sustainability_weight_sensitivity.csv", index=False)
    review_priority.to_csv(config.output_dir / "sustainability_learning_priority.csv", index=False)

    if not transition_summary.empty:
        transition_summary.to_csv(config.output_dir / "transition_pathway_summary.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "sustainability_risk_register_priority.csv", index=False)

    save_plot_scenario_values(scenario_results, config.output_dir / "sustainability_scenario_values.png")
    save_plot_rank_stability(winners, config.output_dir / "sustainability_rank_stability.png")
    save_plot_transition_learning(transition_summary, config.output_dir / "transition_learning_delta.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "concepts_path": str(config.concepts_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "transitions_path": str(config.transitions_path) if config.transitions_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "model": "V_i = w_u U_i + w_f F_i + w_e E_i + w_c C_i + w_q Q_i + w_d D_i - w_r R_i",
        },
    )

    report = build_report(
        concepts=concepts,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        transition_summary=transition_summary,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "sustainability_design_report.md").write_text(report, encoding="utf-8")

    print("Sustainability design analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- sustainability_scenario_results.csv")
    print("- sustainability_monte_carlo_winners.csv")
    print("- sustainability_weight_sensitivity.csv")
    print("- transition_pathway_summary.csv")
    print("- sustainability_learning_priority.csv")
    print("- sustainability_design_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
