#!/usr/bin/env python3
"""
Professional ideation portfolio decision-support engine.

This script provides a reproducible workflow for comparing candidate ideas
across desirability, feasibility, novelty, equity value, learning value,
composite risk, cluster diversity, scenario priorities, Monte Carlo uncertainty,
bootstrap stability, and random-weight sensitivity.

It is intended for design researchers, UX researchers, service designers,
public-sector innovation teams, civic technologists, product strategists,
organizational innovation teams, and applied researchers that need transparent
idea-selection support before committing to prototyping, testing, or
implementation.

Example:

    python ideation_portfolio_engine.py \
      --input ../data/raw/idea_portfolio_raw.csv \
      --weights ../data/raw/ideation_scenario_weights.csv \
      --clusters ../data/raw/idea_cluster_map_raw.csv \
      --output-dir ../outputs \
      --simulations 10000

The model is intentionally interpretable:

    V_i = w_d D_i + w_f F_i + w_n N_i + w_e E_i + w_l L_i - w_r R_i

A composite risk index may also be decomposed as:

    R_i = λ_H H_i + λ_O O_i + λ_T T_i + λ_S S_i

The output should support research interpretation, idea portfolio review,
prototype prioritization, convergence discipline, and institutional learning.
It should not be treated as an automated idea-selection system.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CORE_CRITERIA = [
    "desirability",
    "feasibility",
    "novelty",
    "equity_value",
    "learning_value",
    "composite_risk",
]

POSITIVE_CRITERIA = [
    "desirability",
    "feasibility",
    "novelty",
    "equity_value",
    "learning_value",
]

RISK_COMPONENTS = [
    "residual_risk",
    "ethical_risk",
    "operational_risk",
    "technical_risk",
    "scaling_risk",
]

OPTIONAL_DIAGNOSTIC_COLUMNS = [
    "evidence_quality",
    "prototype_testability",
    "implementation_relevance",
]


@dataclass(frozen=True)
class EngineConfig:
    input_path: Path
    weights_path: Path | None
    clusters_path: Path | None
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


def read_ideas(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input dataset not found: {path}")

    df = pd.read_csv(path)
    required = ["idea", "idea_cluster", *POSITIVE_CRITERIA, *RISK_COMPONENTS]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Input dataset missing required columns: {missing}")

    df = df.copy()
    df["idea"] = df["idea"].astype(str).str.strip()
    df["idea_cluster"] = df["idea_cluster"].astype(str).str.strip()

    numeric_cols = POSITIVE_CRITERIA + RISK_COMPONENTS + [
        col for col in OPTIONAL_DIAGNOSTIC_COLUMNS if col in df.columns
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_clusters(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None

    df = pd.read_csv(path)
    required = [
        "idea",
        "idea_cluster",
        "cluster_distance",
        "stakeholder_groups",
        "methods_supporting",
        "evidence_source_count",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Cluster file missing required columns: {missing}")

    df = df.copy()
    df["idea"] = df["idea"].astype(str).str.strip()
    df["idea_cluster"] = df["idea_cluster"].astype(str).str.strip()
    for col in required[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def validate_ideas(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["idea"].duplicated().any():
        duplicates = df.loc[df["idea"].duplicated(), "idea"].tolist()
        issues.append(
            ValidationIssue(
                level="error",
                field="idea",
                message=f"Duplicate idea names detected: {duplicates}",
            )
        )

    for col in POSITIVE_CRITERIA + RISK_COMPONENTS:
        if df[col].isna().any():
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Column contains missing or non-numeric values.",
                )
            )
        invalid = df[(df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be in the inclusive range [1, 10].",
                )
            )

    for col in ["evidence_quality", "prototype_testability"]:
        if col in df.columns:
            invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
            if not invalid.empty:
                issues.append(
                    ValidationIssue(
                        level="warning",
                        field=col,
                        message="Confidence-style columns are expected to be in [0, 1].",
                    )
                )

    if len(df) < 3:
        issues.append(
            ValidationIssue(
                level="warning",
                field="idea",
                message="Fewer than three candidate ideas limits ranking and robustness interpretation.",
            )
        )

    return issues


def validate_clusters(df: pd.DataFrame | None) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if df is None:
        return issues

    for col in ["cluster_distance", "stakeholder_groups", "methods_supporting", "evidence_source_count"]:
        invalid = df[df[col].isna() | (df[col] < 0)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Cluster diagnostics should be non-negative numeric values.",
                )
            )

    return issues


def read_scenarios(path: Path | None) -> pd.DataFrame:
    if path is None:
        return pd.DataFrame(
            [
                {
                    "scenario": "Balanced",
                    "desirability": 0.24,
                    "feasibility": 0.18,
                    "novelty": 0.18,
                    "equity_value": 0.18,
                    "learning_value": 0.12,
                    "composite_risk": 0.10,
                }
            ]
        )

    if not path.exists():
        raise FileNotFoundError(f"Scenario weight file not found: {path}")

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


def compute_composite_risk(
    df: pd.DataFrame,
    lambdas: Dict[str, float] | None = None,
) -> pd.Series:
    if lambdas is None:
        lambdas = {
            "residual_risk": 0.25,
            "ethical_risk": 0.25,
            "operational_risk": 0.20,
            "technical_risk": 0.15,
            "scaling_risk": 0.15,
        }

    available = [col for col in RISK_COMPONENTS if col in df.columns]
    total_weight = sum(lambdas[col] for col in available)
    return sum((lambdas[col] / total_weight) * df[col] for col in available)


def score_ideas(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["composite_risk"] = compute_composite_risk(scored)

    scored["idea_value"] = (
        weights["desirability"] * scored["desirability"]
        + weights["feasibility"] * scored["feasibility"]
        + weights["novelty"] * scored["novelty"]
        + weights["equity_value"] * scored["equity_value"]
        + weights["learning_value"] * scored["learning_value"]
        - weights["composite_risk"] * scored["composite_risk"]
    )

    scored["risk_adjusted_learning"] = (
        scored["learning_value"] - 0.35 * scored["composite_risk"]
    )

    scored["prototype_priority"] = (
        0.30 * scored["desirability"]
        + 0.25 * scored["learning_value"]
        + 0.20 * scored["feasibility"]
        + 0.15 * scored["equity_value"]
        - 0.10 * scored["composite_risk"]
    )

    if "evidence_quality" in scored.columns:
        scored["confidence_adjusted_value"] = (
            scored["idea_value"] * (0.75 + 0.25 * scored["evidence_quality"])
        )
    else:
        scored["confidence_adjusted_value"] = scored["idea_value"]

    if "prototype_testability" in scored.columns:
        scored["testability_adjusted_value"] = (
            scored["confidence_adjusted_value"] * (0.85 + 0.15 * scored["prototype_testability"])
        )
    else:
        scored["testability_adjusted_value"] = scored["confidence_adjusted_value"]

    if "implementation_relevance" in scored.columns:
        scored["implementation_adjusted_value"] = (
            scored["testability_adjusted_value"] + 0.03 * scored["implementation_relevance"]
        )
    else:
        scored["implementation_adjusted_value"] = scored["testability_adjusted_value"]

    scored["review_priority"] = (
        0.30 * scored["composite_risk"]
        + 0.20 * (10.0 - scored["feasibility"])
        + 0.20 * (10.0 - scored["evidence_quality"].fillna(0) * 10.0 if "evidence_quality" in scored.columns else 5.0)
        + 0.15 * scored["ethical_risk"]
        + 0.15 * scored["scaling_risk"]
    )

    scored = scored.sort_values("idea_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(ideas: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    outputs: List[pd.DataFrame] = []

    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_CRITERIA}
        scored = score_ideas(ideas, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_CRITERIA:
            scored[f"weight_{col}"] = weights[col]
        outputs.append(scored)

    return pd.concat(outputs, ignore_index=True)


def cluster_divergence_summary(ideas: pd.DataFrame, clusters: pd.DataFrame | None) -> pd.DataFrame:
    base = ideas[["idea", "idea_cluster"]].copy()

    cluster_count = base["idea_cluster"].nunique()
    idea_count = len(base)
    cluster_proportion = cluster_count / idea_count if idea_count else 0.0

    if clusters is not None:
        merged = base.merge(
            clusters[
                [
                    "idea",
                    "cluster_distance",
                    "stakeholder_groups",
                    "methods_supporting",
                    "evidence_source_count",
                ]
            ],
            on="idea",
            how="left",
        )
    else:
        merged = base.copy()
        merged["cluster_distance"] = np.nan
        merged["stakeholder_groups"] = np.nan
        merged["methods_supporting"] = np.nan
        merged["evidence_source_count"] = np.nan

    summary = (
        merged.groupby("idea_cluster")
        .agg(
            idea_count=("idea", "count"),
            mean_cluster_distance=("cluster_distance", "mean"),
            stakeholder_groups=("stakeholder_groups", "max"),
            methods_supporting=("methods_supporting", "max"),
            evidence_source_count=("evidence_source_count", "sum"),
        )
        .reset_index()
    )

    summary["portfolio_cluster_count"] = cluster_count
    summary["portfolio_idea_count"] = idea_count
    summary["exploratory_breadth_ratio"] = cluster_proportion

    return summary.sort_values(["idea_count", "evidence_source_count"], ascending=False)


def monte_carlo_rank_stability(
    ideas: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    idea_names = ideas["idea"].to_numpy()
    winner_counts = {name: 0 for name in idea_names}
    value_records: List[Dict[str, float | str | int]] = []

    score_columns = POSITIVE_CRITERIA + RISK_COMPONENTS
    means = ideas[score_columns].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)

        sim_df = ideas.copy()
        sim_df[score_columns] = simulated_scores

        scored = score_ideas(sim_df, weights)
        winner = str(scored.iloc[0]["idea"])
        winner_counts[winner] += 1

        for _, row in scored.iterrows():
            value_records.append(
                {
                    "simulation_id": simulation_id,
                    "idea": row["idea"],
                    "idea_value": float(row["idea_value"]),
                    "composite_risk": float(row["composite_risk"]),
                    "prototype_priority": float(row["prototype_priority"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = pd.DataFrame(
        [
            {
                "idea": idea,
                "probability_ranked_first": count / simulations,
                "times_ranked_first": count,
            }
            for idea, count in winner_counts.items()
        ]
    ).sort_values("probability_ranked_first", ascending=False)

    simulation_values = pd.DataFrame(value_records)
    return winners, simulation_values


def bootstrap_idea_scores(
    ideas: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[Dict[str, float | str | int]] = []

    for iteration in range(iterations):
        sampled = ideas.sample(
            n=len(ideas),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_ideas(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "idea": row["idea"],
                    "idea_value": float(row["idea_value"]),
                    "composite_risk": float(row["composite_risk"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    summary = (
        boot.groupby("idea")
        .agg(
            mean_idea_value=("idea_value", "mean"),
            sd_idea_value=("idea_value", "std"),
            mean_composite_risk=("composite_risk", "mean"),
            median_rank=("rank", "median"),
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
        )
        .reset_index()
        .sort_values(["median_rank", "mean_rank"])
    )

    return summary


def weight_sensitivity_analysis(
    ideas: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    idea_names = ideas["idea"].to_numpy()
    winner_counts = {name: 0 for name in idea_names}
    records: List[Dict[str, float | str]] = []

    for _ in range(samples):
        weights_arr = rng.dirichlet(alpha=np.ones(len(CORE_CRITERIA)))
        weights = dict(zip(CORE_CRITERIA, weights_arr))
        scored = score_ideas(ideas, weights)
        winner = str(scored.iloc[0]["idea"])
        winner_counts[winner] += 1

        records.append(
            {
                "winner": winner,
                "desirability_weight": weights["desirability"],
                "feasibility_weight": weights["feasibility"],
                "novelty_weight": weights["novelty"],
                "equity_value_weight": weights["equity_value"],
                "learning_value_weight": weights["learning_value"],
                "composite_risk_weight": weights["composite_risk"],
            }
        )

    raw = pd.DataFrame(records)
    summary = (
        raw["winner"]
        .value_counts(normalize=True)
        .rename_axis("idea")
        .reset_index(name="probability_winning_under_random_weights")
    )
    summary["times_won"] = raw["winner"].value_counts().reindex(summary["idea"]).to_numpy()

    return summary.sort_values("probability_winning_under_random_weights", ascending=False)


def rank_correlation_matrix(scenario_results: pd.DataFrame) -> pd.DataFrame:
    pivot = scenario_results.pivot_table(
        index="idea",
        columns="scenario",
        values="rank",
        aggfunc="first",
    )
    return pivot.corr(method="spearman")


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="idea",
        columns="scenario",
        values="idea_value",
        aggfunc="first",
    )

    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("Idea Portfolio Value Across Ideation Scenarios")
    ax.set_xlabel("Idea")
    ax.set_ylabel("Weighted idea value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["idea"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for Candidate Ideas")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Idea")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_cluster_breadth(cluster_summary: pd.DataFrame, output_path: Path) -> None:
    if cluster_summary.empty:
        return

    plt.figure(figsize=(11, 6))
    plt.bar(cluster_summary["idea_cluster"], cluster_summary["idea_count"])
    plt.title("Idea Cluster Breadth")
    plt.ylabel("Number of ideas")
    plt.xlabel("Idea cluster")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def dataframe_to_markdown_safe(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except Exception:
        return df.to_string(index=False)


def build_report(
    ideas: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
    cluster_summary: pd.DataFrame,
    review_priority: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top_balanced = (
        scenario_results[scenario_results["scenario"] == "Balanced"]
        .sort_values("rank")
        .head(1)
    )

    top_name = top_balanced.iloc[0]["idea"] if not top_balanced.empty else "Not available"
    top_value = (
        float(top_balanced.iloc[0]["idea_value"]) if not top_balanced.empty else math.nan
    )

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    report = f"""# Ideation Portfolio Decision-Support Report

## Article

Ideation in Design Thinking

## Summary

This report compares candidate ideas using a transparent multi-criteria model. It includes scenario analysis, composite-risk decomposition, cluster breadth diagnostics, uncertainty modeling, bootstrap stability, random-weight sensitivity analysis, and review-priority scoring.

## Balanced scenario leader

- Candidate idea: **{top_name}**
- Weighted idea value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_d D_i + w_f F_i + w_n N_i + w_e E_i + w_l L_i - w_r R_i
\\]

where:

- \\(D_i\\) = desirability;
- \\(F_i\\) = feasibility;
- \\(N_i\\) = novelty;
- \\(E_i\\) = equity value;
- \\(L_i\\) = learning value;
- \\(R_i\\) = composite risk.

## Risk index

\\[
R_i = \\lambda_H H_i + \\lambda_O O_i + \\lambda_T T_i + \\lambda_S S_i
\\]

where:

- \\(H_i\\) = ethical risk;
- \\(O_i\\) = operational risk;
- \\(T_i\\) = technical risk;
- \\(S_i\\) = scaling risk.

## Scenario count

{len(scenarios)}

## Idea count

{len(ideas)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap_summary)}

## Weight sensitivity

{dataframe_to_markdown_safe(sensitivity_summary)}

## Cluster breadth

{dataframe_to_markdown_safe(cluster_summary)}

## Review priority

{dataframe_to_markdown_safe(review_priority)}

## Interpretation

The analysis is intended to support professional ideation judgment, not replace it. It should be read alongside stakeholder research, problem frames, insight statements, ethical review, prototype plans, operational constraints, and system context.

A candidate idea that ranks highly across scenarios may be a strong candidate for prototyping. A candidate idea that performs well only under one weighting scheme may require additional deliberation. An idea with high value but high risk should be reviewed before moving into testing. An idea with strong learning value may be worth prototyping even if it is not the highest-scoring implementation candidate.

## Responsible use

These outputs should not be treated as an automated idea-selection system. The purpose is to make assumptions visible, support team deliberation, identify missing evidence, and guide responsible prototyping.
"""
    return report


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(
        description="Professional ideation portfolio decision-support engine."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("../data/raw/idea_portfolio_raw.csv"),
        help="Candidate idea portfolio CSV file.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/ideation_scenario_weights.csv"),
        help="Scenario weights CSV file.",
    )
    parser.add_argument(
        "--clusters",
        type=Path,
        default=Path("../data/raw/idea_cluster_map_raw.csv"),
        help="Idea cluster diagnostics CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../outputs"),
        help="Output directory.",
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=10000,
        help="Monte Carlo simulation count.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )
    parser.add_argument(
        "--score-sd",
        type=float,
        default=0.6,
        help="Standard deviation for simulated criterion scores.",
    )
    parser.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=2500,
        help="Bootstrap iteration count.",
    )
    parser.add_argument(
        "--sensitivity-samples",
        type=int,
        default=10000,
        help="Random weight samples for sensitivity analysis.",
    )

    args = parser.parse_args(argv)

    weights_path = args.weights if args.weights and args.weights.exists() else None
    clusters_path = args.clusters if args.clusters and args.clusters.exists() else None

    return EngineConfig(
        input_path=args.input,
        weights_path=weights_path,
        clusters_path=clusters_path,
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

    ideas = read_ideas(config.input_path)
    clusters = read_clusters(config.clusters_path)

    issues = validate_ideas(ideas)
    issues.extend(validate_clusters(clusters))

    fatal_issues = [issue for issue in issues if issue.level == "error"]

    if fatal_issues:
        for issue in fatal_issues:
            print(f"ERROR [{issue.field}]: {issue.message}", file=sys.stderr)
        return 2

    scenarios = read_scenarios(config.weights_path)
    balanced_weights = (
        scenarios[scenarios["scenario"].str.lower() == "balanced"]
        .iloc[0][CORE_CRITERIA]
        .astype(float)
        .to_dict()
    )

    scenario_results = run_scenario_analysis(ideas, scenarios)

    winners, simulation_values = monte_carlo_rank_stability(
        ideas=ideas,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap_summary = bootstrap_idea_scores(
        ideas=ideas,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity_summary = weight_sensitivity_analysis(
        ideas=ideas,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    cluster_summary = cluster_divergence_summary(ideas, clusters)
    rank_corr = rank_correlation_matrix(scenario_results)

    review_priority = (
        score_ideas(ideas, balanced_weights)
        .sort_values("review_priority", ascending=False)
        [
            [
                "idea",
                "idea_cluster",
                "idea_value",
                "prototype_priority",
                "composite_risk",
                "ethical_risk",
                "scaling_risk",
                "review_priority",
            ]
        ]
    )

    scenario_results.to_csv(config.output_dir / "ideation_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "ideation_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "ideation_simulation_values.csv", index=False)
    bootstrap_summary.to_csv(config.output_dir / "ideation_bootstrap_summary.csv", index=False)
    sensitivity_summary.to_csv(config.output_dir / "ideation_weight_sensitivity.csv", index=False)
    cluster_summary.to_csv(config.output_dir / "ideation_cluster_breadth.csv", index=False)
    review_priority.to_csv(config.output_dir / "ideation_review_priority.csv", index=False)
    rank_corr.to_csv(config.output_dir / "ideation_rank_correlations.csv")

    save_plot_scenario_values(
        scenario_results,
        config.output_dir / "ideation_scenario_values.png",
    )
    save_plot_rank_stability(
        winners,
        config.output_dir / "ideation_rank_stability.png",
    )
    save_plot_cluster_breadth(
        cluster_summary,
        config.output_dir / "ideation_cluster_breadth.png",
    )

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "input_path": str(config.input_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "clusters_path": str(config.clusters_path) if config.clusters_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_CRITERIA,
            "positive_criteria": POSITIVE_CRITERIA,
            "risk_components": RISK_COMPONENTS,
        },
    )

    report = build_report(
        ideas=ideas,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap_summary=bootstrap_summary,
        sensitivity_summary=sensitivity_summary,
        cluster_summary=cluster_summary,
        review_priority=review_priority,
        issues=issues,
    )
    (config.output_dir / "ideation_decision_report.md").write_text(report, encoding="utf-8")

    print("Analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- ideation_scenario_results.csv")
    print("- ideation_monte_carlo_winners.csv")
    print("- ideation_weight_sensitivity.csv")
    print("- ideation_cluster_breadth.csv")
    print("- ideation_review_priority.csv")
    print("- ideation_decision_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
