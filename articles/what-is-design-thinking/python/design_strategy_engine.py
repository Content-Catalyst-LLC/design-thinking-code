#!/usr/bin/env python3
"""
Professional design strategy decision-support engine.

This script provides a reproducible workflow for comparing design thinking
pathways across weighted criteria, scenario priorities, Monte Carlo uncertainty,
bootstrap stability, and sensitivity analysis.

It is intended for design researchers, service design teams, institutional
strategy groups, public-sector labs, and applied researchers who need transparent
decision support rather than informal workshop scoring.

Example:

    python design_strategy_engine.py \
      --input ../data/raw/design_pathways_raw.csv \
      --weights ../data/raw/scenario_weights.csv \
      --output-dir ../outputs \
      --simulations 10000

The model is intentionally interpretable:

    V_i = w_h H_i + w_f F_i + w_l L_i - w_r R_i

The output should support discussion, documentation, and further inquiry.
It should not be treated as an automated decision system.
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
from scipy.stats import rankdata


CORE_CRITERIA = [
    "human_relevance",
    "feasibility",
    "learning_value",
    "residual_risk",
]

POSITIVE_CRITERIA = [
    "human_relevance",
    "feasibility",
    "learning_value",
]

NEGATIVE_CRITERIA = [
    "residual_risk",
]

OPTIONAL_DIAGNOSTIC_COLUMNS = [
    "stakeholder_confidence",
    "evidence_quality",
    "implementation_complexity",
]


@dataclass(frozen=True)
class EngineConfig:
    input_path: Path
    weights_path: Path | None
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


def read_pathway_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input dataset not found: {path}")

    df = pd.read_csv(path)
    required = ["pathway", *CORE_CRITERIA]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Input dataset missing required columns: {missing}")

    df = df.copy()
    df["pathway"] = df["pathway"].astype(str).str.strip()

    for col in CORE_CRITERIA + [c for c in OPTIONAL_DIAGNOSTIC_COLUMNS if c in df.columns]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def validate_pathway_data(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["pathway"].duplicated().any():
        duplicates = df.loc[df["pathway"].duplicated(), "pathway"].tolist()
        issues.append(
            ValidationIssue(
                level="error",
                field="pathway",
                message=f"Duplicate pathway names detected: {duplicates}",
            )
        )

    for col in CORE_CRITERIA:
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

    for col in ["stakeholder_confidence", "evidence_quality"]:
        if col in df.columns:
            invalid = df[(df[col] < 0) | (df[col] > 1)]
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
                field="pathway",
                message="Fewer than three pathways limits ranking and robustness interpretation.",
            )
        )

    return issues


def default_scenarios() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scenario": "Balanced",
                "human_relevance": 0.35,
                "feasibility": 0.25,
                "learning_value": 0.25,
                "residual_risk": 0.15,
            },
            {
                "scenario": "Human First",
                "human_relevance": 0.50,
                "feasibility": 0.20,
                "learning_value": 0.20,
                "residual_risk": 0.10,
            },
            {
                "scenario": "Feasibility First",
                "human_relevance": 0.20,
                "feasibility": 0.50,
                "learning_value": 0.20,
                "residual_risk": 0.10,
            },
            {
                "scenario": "Learning First",
                "human_relevance": 0.20,
                "feasibility": 0.20,
                "learning_value": 0.45,
                "residual_risk": 0.15,
            },
            {
                "scenario": "Risk Sensitive",
                "human_relevance": 0.25,
                "feasibility": 0.20,
                "learning_value": 0.20,
                "residual_risk": 0.35,
            },
        ]
    )


def read_scenarios(path: Path | None) -> pd.DataFrame:
    if path is None:
        return default_scenarios()

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


def score_pathways(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["design_value"] = (
        weights["human_relevance"] * scored["human_relevance"]
        + weights["feasibility"] * scored["feasibility"]
        + weights["learning_value"] * scored["learning_value"]
        - weights["residual_risk"] * scored["residual_risk"]
    )

    scored["risk_adjusted_learning"] = scored["learning_value"] - 0.5 * scored["residual_risk"]

    if "evidence_quality" in scored.columns and "stakeholder_confidence" in scored.columns:
        scored["evidence_confidence_index"] = (
            0.5 * scored["evidence_quality"] + 0.5 * scored["stakeholder_confidence"]
        )
        scored["confidence_adjusted_value"] = (
            scored["design_value"] * (0.75 + 0.25 * scored["evidence_confidence_index"])
        )
    else:
        scored["confidence_adjusted_value"] = scored["design_value"]

    scored = scored.sort_values("design_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(pathways: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []

    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_CRITERIA}
        scored = score_pathways(pathways, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_CRITERIA:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)

    return pd.concat(frames, ignore_index=True)


def monte_carlo_rank_stability(
    pathways: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    pathway_names = pathways["pathway"].to_numpy()
    winner_counts = {name: 0 for name in pathway_names}
    value_records: List[Dict[str, float | str | int]] = []

    means = pathways[CORE_CRITERIA].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)

        sim_df = pathways.copy()
        sim_df[CORE_CRITERIA] = simulated_scores

        scored = score_pathways(sim_df, weights)
        winner = str(scored.iloc[0]["pathway"])
        winner_counts[winner] += 1

        for _, row in scored.iterrows():
            value_records.append(
                {
                    "simulation_id": simulation_id,
                    "pathway": row["pathway"],
                    "design_value": float(row["design_value"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = pd.DataFrame(
        [
            {
                "pathway": pathway,
                "probability_ranked_first": count / simulations,
                "times_ranked_first": count,
            }
            for pathway, count in winner_counts.items()
        ]
    ).sort_values("probability_ranked_first", ascending=False)

    simulation_values = pd.DataFrame(value_records)
    return winners, simulation_values


def bootstrap_pathway_scores(
    pathways: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[Dict[str, float | str | int]] = []

    for iteration in range(iterations):
        sampled = pathways.sample(
            n=len(pathways),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_pathways(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "pathway": row["pathway"],
                    "design_value": float(row["design_value"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    summary = (
        boot.groupby("pathway")
        .agg(
            mean_design_value=("design_value", "mean"),
            sd_design_value=("design_value", "std"),
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
    pathways: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    pathway_names = pathways["pathway"].to_numpy()
    winner_counts = {name: 0 for name in pathway_names}
    records: List[Dict[str, float | str]] = []

    for _ in range(samples):
        weights_arr = rng.dirichlet(alpha=np.ones(len(CORE_CRITERIA)))
        weights = dict(zip(CORE_CRITERIA, weights_arr))
        scored = score_pathways(pathways, weights)
        winner = str(scored.iloc[0]["pathway"])
        winner_counts[winner] += 1

        records.append(
            {
                "winner": winner,
                "human_relevance_weight": weights["human_relevance"],
                "feasibility_weight": weights["feasibility"],
                "learning_value_weight": weights["learning_value"],
                "residual_risk_weight": weights["residual_risk"],
            }
        )

    raw = pd.DataFrame(records)
    summary = (
        raw["winner"]
        .value_counts(normalize=True)
        .rename_axis("pathway")
        .reset_index(name="probability_winning_under_random_weights")
    )
    summary["times_won"] = raw["winner"].value_counts().reindex(summary["pathway"]).to_numpy()

    return summary.sort_values("probability_winning_under_random_weights", ascending=False)


def rank_correlation_matrix(scenario_results: pd.DataFrame) -> pd.DataFrame:
    pivot = scenario_results.pivot_table(
        index="pathway",
        columns="scenario",
        values="rank",
        aggfunc="first",
    )
    return pivot.corr(method="spearman")


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="pathway",
        columns="scenario",
        values="design_value",
        aggfunc="first",
    )

    ax = pivot.plot(kind="bar", figsize=(12, 7))
    ax.set_title("Design Pathway Value Across Strategic Scenarios")
    ax.set_xlabel("Design pathway")
    ax.set_ylabel("Weighted design value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(11, 6))
    plt.bar(plot_df["pathway"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Design pathway")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def build_report(
    pathways: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top_balanced = (
        scenario_results[scenario_results["scenario"] == "Balanced"]
        .sort_values("rank")
        .head(1)
    )

    top_name = top_balanced.iloc[0]["pathway"] if not top_balanced.empty else "Not available"
    top_value = (
        float(top_balanced.iloc[0]["design_value"]) if not top_balanced.empty else math.nan
    )

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    report = f"""# Design Strategy Analysis Report

## Article

What Is Design Thinking?

## Summary

This report compares design pathways using a transparent multi-criteria model. It includes scenario analysis, uncertainty modeling, bootstrap stability, and weight sensitivity analysis.

## Balanced scenario leader

- Pathway: **{top_name}**
- Weighted design value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_h H_i + w_f F_i + w_l L_i - w_r R_i
\\]

where:

- \\(H_i\\) = human-centered relevance;
- \\(F_i\\) = feasibility;
- \\(L_i\\) = learning value;
- \\(R_i\\) = residual risk.

## Scenario count

{len(scenarios)}

## Pathway count

{len(pathways)}

## Monte Carlo rank stability

{winners.to_markdown(index=False)}

## Bootstrap stability

{bootstrap_summary.to_markdown(index=False)}

## Weight sensitivity

{sensitivity_summary.to_markdown(index=False)}

## Interpretation

The analysis is intended to support professional design judgment. It should be read alongside qualitative research, stakeholder evidence, prototype findings, ethical review, feasibility analysis, and institutional context.

A pathway that ranks highly across scenarios may be strategically robust. A pathway that performs well only under one weighting scheme may require more discussion. A pathway with high learning value but high risk may be appropriate for a bounded prototype rather than immediate implementation.

## Responsible use

These outputs should not be treated as an automated decision system. The purpose is to make assumptions visible, support team deliberation, and guide further research.
"""
    return report


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(
        description="Professional design thinking strategy analysis engine."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("../data/raw/design_pathways_raw.csv"),
        help="Pathway CSV file.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/scenario_weights.csv"),
        help="Scenario weights CSV file.",
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

    return EngineConfig(
        input_path=args.input,
        weights_path=weights_path,
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

    pathways = read_pathway_data(config.input_path)
    issues = validate_pathway_data(pathways)
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

    scenario_results = run_scenario_analysis(pathways, scenarios)
    winners, simulation_values = monte_carlo_rank_stability(
        pathways=pathways,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap_summary = bootstrap_pathway_scores(
        pathways=pathways,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity_summary = weight_sensitivity_analysis(
        pathways=pathways,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    rank_corr = rank_correlation_matrix(scenario_results)

    scenario_results.to_csv(config.output_dir / "design_pathway_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "design_pathway_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "design_pathway_simulation_values.csv", index=False)
    bootstrap_summary.to_csv(config.output_dir / "design_pathway_bootstrap_summary.csv", index=False)
    sensitivity_summary.to_csv(config.output_dir / "design_pathway_weight_sensitivity.csv", index=False)
    rank_corr.to_csv(config.output_dir / "design_pathway_rank_correlations.csv")

    save_plot_scenario_values(
        scenario_results,
        config.output_dir / "design_pathway_scenario_values.png",
    )
    save_plot_rank_stability(
        winners,
        config.output_dir / "design_pathway_rank_stability.png",
    )

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "input_path": str(config.input_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_CRITERIA,
            "positive_criteria": POSITIVE_CRITERIA,
            "negative_criteria": NEGATIVE_CRITERIA,
        },
    )

    report = build_report(
        pathways=pathways,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap_summary=bootstrap_summary,
        sensitivity_summary=sensitivity_summary,
        issues=issues,
    )
    (config.output_dir / "design_strategy_analysis_report.md").write_text(report, encoding="utf-8")

    print("Analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- design_pathway_scenario_results.csv")
    print("- design_pathway_monte_carlo_winners.csv")
    print("- design_pathway_weight_sensitivity.csv")
    print("- design_strategy_analysis_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
