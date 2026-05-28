#!/usr/bin/env python3
"""
Professional iteration and experimentation decision-support engine.

This script provides a reproducible workflow for comparing experiment portfolios
across learning gain, update flexibility, expected improvement, residual risk,
risk decomposition, ethics-review diagnostics, scenario priorities, Monte Carlo
uncertainty, bootstrap stability, and weight sensitivity.

It is intended for design researchers, service designers, public-sector labs,
healthcare improvement teams, civic technologists, product teams, UX researchers,
and organizational innovation teams that need transparent experiment-selection
support before committing to larger implementation.

Example:

    python iteration_experimentation_engine.py \
      --input ../data/raw/experiments_raw.csv \
      --weights ../data/raw/experiment_scenario_weights.csv \
      --ethics ../data/raw/experiment_ethics_review_raw.csv \
      --output-dir ../outputs \
      --simulations 10000

The model is intentionally interpretable:

    V_i = w_l L_i + w_u U_i + w_e E_i - w_r R_i

A residual-risk index may also be decomposed as:

    R_i = λ_H H_i + λ_O O_i + λ_I I_i + λ_S S_i

The output should support research interpretation, stakeholder deliberation,
ethical review, experiment portfolio selection, and institutional learning.
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


CORE_CRITERIA = [
    "learning_gain",
    "update_flexibility",
    "expected_improvement",
    "residual_risk",
]

POSITIVE_CRITERIA = [
    "learning_gain",
    "update_flexibility",
    "expected_improvement",
]

NEGATIVE_CRITERIA = [
    "residual_risk",
]

RISK_COMPONENTS = [
    "ethical_risk",
    "operational_risk",
    "interpretive_risk",
    "scaling_risk",
]

OPTIONAL_DIAGNOSTIC_COLUMNS = [
    "evidence_quality",
    "team_confidence",
    "implementation_complexity",
]


@dataclass(frozen=True)
class EngineConfig:
    input_path: Path
    weights_path: Path | None
    ethics_path: Path | None
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


def read_experiments(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input dataset not found: {path}")

    df = pd.read_csv(path)
    required = ["experiment", *CORE_CRITERIA]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Input dataset missing required columns: {missing}")

    df = df.copy()
    df["experiment"] = df["experiment"].astype(str).str.strip()

    numeric_cols = CORE_CRITERIA + [
        col for col in RISK_COMPONENTS + OPTIONAL_DIAGNOSTIC_COLUMNS
        if col in df.columns
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_ethics(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None

    df = pd.read_csv(path)
    required = [
        "experiment",
        "requires_informed_consent",
        "participant_burden",
        "privacy_sensitivity",
        "power_asymmetry",
        "review_priority",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Ethics file missing required columns: {missing}")

    df = df.copy()
    df["experiment"] = df["experiment"].astype(str).str.strip()
    for col in required[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def validate_experiments(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["experiment"].duplicated().any():
        duplicates = df.loc[df["experiment"].duplicated(), "experiment"].tolist()
        issues.append(
            ValidationIssue(
                level="error",
                field="experiment",
                message=f"Duplicate experiment names detected: {duplicates}",
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

    for col in RISK_COMPONENTS:
        if col in df.columns:
            invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
            if not invalid.empty:
                issues.append(
                    ValidationIssue(
                        level="warning",
                        field=col,
                        message="Risk component scores should be numeric and in [1, 10].",
                    )
                )

    for col in ["evidence_quality", "team_confidence"]:
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
                field="experiment",
                message="Fewer than three experiments limits ranking and robustness interpretation.",
            )
        )

    return issues


def validate_ethics(df: pd.DataFrame | None) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if df is None:
        return issues

    for col in [
        "requires_informed_consent",
        "participant_burden",
        "privacy_sensitivity",
        "power_asymmetry",
        "review_priority",
    ]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Ethics-review diagnostic scores should be numeric and in [0, 1].",
                )
            )

    return issues


def default_scenarios() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scenario": "Balanced",
                "learning_gain": 0.35,
                "update_flexibility": 0.25,
                "expected_improvement": 0.25,
                "residual_risk": 0.15,
            },
            {
                "scenario": "Learning First",
                "learning_gain": 0.50,
                "update_flexibility": 0.20,
                "expected_improvement": 0.20,
                "residual_risk": 0.10,
            },
            {
                "scenario": "Flexibility First",
                "learning_gain": 0.20,
                "update_flexibility": 0.50,
                "expected_improvement": 0.20,
                "residual_risk": 0.10,
            },
            {
                "scenario": "Improvement First",
                "learning_gain": 0.20,
                "update_flexibility": 0.20,
                "expected_improvement": 0.45,
                "residual_risk": 0.15,
            },
            {
                "scenario": "Risk Sensitive",
                "learning_gain": 0.25,
                "update_flexibility": 0.20,
                "expected_improvement": 0.20,
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


def compute_risk_index(
    df: pd.DataFrame,
    lambdas: Dict[str, float] | None = None,
) -> pd.Series:
    if lambdas is None:
        lambdas = {
            "ethical_risk": 0.30,
            "operational_risk": 0.25,
            "interpretive_risk": 0.20,
            "scaling_risk": 0.25,
        }

    available = [col for col in RISK_COMPONENTS if col in df.columns]
    if not available:
        return df["residual_risk"]

    total_weight = sum(lambdas[col] for col in available)
    risk_index = sum((lambdas[col] / total_weight) * df[col] for col in available)
    return risk_index


def score_experiments(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["risk_index"] = compute_risk_index(scored)

    scored["experiment_value"] = (
        weights["learning_gain"] * scored["learning_gain"]
        + weights["update_flexibility"] * scored["update_flexibility"]
        + weights["expected_improvement"] * scored["expected_improvement"]
        - weights["residual_risk"] * scored["residual_risk"]
    )

    scored["risk_index_adjusted_value"] = (
        weights["learning_gain"] * scored["learning_gain"]
        + weights["update_flexibility"] * scored["update_flexibility"]
        + weights["expected_improvement"] * scored["expected_improvement"]
        - weights["residual_risk"] * scored["risk_index"]
    )

    scored["risk_adjusted_learning"] = (
        scored["learning_gain"] - 0.40 * scored["risk_index"]
    )

    if "evidence_quality" in scored.columns and "team_confidence" in scored.columns:
        scored["evidence_confidence_index"] = (
            0.5 * scored["evidence_quality"] + 0.5 * scored["team_confidence"]
        )
        scored["confidence_adjusted_value"] = (
            scored["experiment_value"] * (0.75 + 0.25 * scored["evidence_confidence_index"])
        )
    else:
        scored["confidence_adjusted_value"] = scored["experiment_value"]

    if "implementation_complexity" in scored.columns:
        scored["implementation_adjusted_value"] = (
            scored["confidence_adjusted_value"] - 0.07 * scored["implementation_complexity"]
        )
    else:
        scored["implementation_adjusted_value"] = scored["confidence_adjusted_value"]

    scored = scored.sort_values("experiment_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(experiments: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    outputs: List[pd.DataFrame] = []

    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_CRITERIA}
        scored = score_experiments(experiments, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_CRITERIA:
            scored[f"weight_{col}"] = weights[col]
        outputs.append(scored)

    return pd.concat(outputs, ignore_index=True)


def monte_carlo_rank_stability(
    experiments: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    experiment_names = experiments["experiment"].to_numpy()
    winner_counts = {name: 0 for name in experiment_names}
    value_records: List[Dict[str, float | str | int]] = []

    means = experiments[CORE_CRITERIA].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)

        sim_df = experiments.copy()
        sim_df[CORE_CRITERIA] = simulated_scores

        if all(col in sim_df.columns for col in RISK_COMPONENTS):
            risk_component_means = experiments[RISK_COMPONENTS].to_numpy(dtype=float)
            risk_component_scores = rng.normal(loc=risk_component_means, scale=score_sd)
            sim_df[RISK_COMPONENTS] = np.clip(risk_component_scores, 1.0, 10.0)

        scored = score_experiments(sim_df, weights)
        winner = str(scored.iloc[0]["experiment"])
        winner_counts[winner] += 1

        for _, row in scored.iterrows():
            value_records.append(
                {
                    "simulation_id": simulation_id,
                    "experiment": row["experiment"],
                    "experiment_value": float(row["experiment_value"]),
                    "risk_index": float(row["risk_index"]),
                    "confidence_adjusted_value": float(row["confidence_adjusted_value"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = pd.DataFrame(
        [
            {
                "experiment": experiment,
                "probability_ranked_first": count / simulations,
                "times_ranked_first": count,
            }
            for experiment, count in winner_counts.items()
        ]
    ).sort_values("probability_ranked_first", ascending=False)

    simulation_values = pd.DataFrame(value_records)
    return winners, simulation_values


def bootstrap_experiment_scores(
    experiments: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[Dict[str, float | str | int]] = []

    for iteration in range(iterations):
        sampled = experiments.sample(
            n=len(experiments),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_experiments(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "experiment": row["experiment"],
                    "experiment_value": float(row["experiment_value"]),
                    "risk_index": float(row["risk_index"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    summary = (
        boot.groupby("experiment")
        .agg(
            mean_experiment_value=("experiment_value", "mean"),
            sd_experiment_value=("experiment_value", "std"),
            mean_risk_index=("risk_index", "mean"),
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
    experiments: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    experiment_names = experiments["experiment"].to_numpy()
    winner_counts = {name: 0 for name in experiment_names}
    records: List[Dict[str, float | str]] = []

    for _ in range(samples):
        weights_arr = rng.dirichlet(alpha=np.ones(len(CORE_CRITERIA)))
        weights = dict(zip(CORE_CRITERIA, weights_arr))
        scored = score_experiments(experiments, weights)
        winner = str(scored.iloc[0]["experiment"])
        winner_counts[winner] += 1

        records.append(
            {
                "winner": winner,
                "learning_gain_weight": weights["learning_gain"],
                "update_flexibility_weight": weights["update_flexibility"],
                "expected_improvement_weight": weights["expected_improvement"],
                "residual_risk_weight": weights["residual_risk"],
            }
        )

    raw = pd.DataFrame(records)
    summary = (
        raw["winner"]
        .value_counts(normalize=True)
        .rename_axis("experiment")
        .reset_index(name="probability_winning_under_random_weights")
    )
    summary["times_won"] = raw["winner"].value_counts().reindex(summary["experiment"]).to_numpy()

    return summary.sort_values("probability_winning_under_random_weights", ascending=False)


def ethics_review_priority(ethics: pd.DataFrame | None) -> pd.DataFrame | None:
    if ethics is None:
        return None

    df = ethics.copy()
    df["computed_review_priority"] = (
        0.25 * df["requires_informed_consent"]
        + 0.25 * df["participant_burden"]
        + 0.25 * df["privacy_sensitivity"]
        + 0.25 * df["power_asymmetry"]
    )
    df["review_priority_gap"] = df["computed_review_priority"] - df["review_priority"]
    return df.sort_values("computed_review_priority", ascending=False)


def rank_correlation_matrix(scenario_results: pd.DataFrame) -> pd.DataFrame:
    pivot = scenario_results.pivot_table(
        index="experiment",
        columns="scenario",
        values="rank",
        aggfunc="first",
    )
    return pivot.corr(method="spearman")


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="experiment",
        columns="scenario",
        values="experiment_value",
        aggfunc="first",
    )

    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("Experiment Portfolio Value Across Learning Scenarios")
    ax.set_xlabel("Experiment")
    ax.set_ylabel("Weighted experiment value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["experiment"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for Experiment Choices")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Experiment")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_ethics_priority(ethics: pd.DataFrame | None, output_path: Path) -> None:
    if ethics is None or ethics.empty:
        return

    plot_df = ethics.sort_values("computed_review_priority", ascending=True)

    plt.figure(figsize=(12, 7))
    plt.barh(plot_df["experiment"], plot_df["computed_review_priority"])
    plt.title("Ethics Review Priority by Experiment")
    plt.xlabel("Computed review priority")
    plt.ylabel("Experiment")
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
    experiments: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
    ethics_summary: pd.DataFrame | None,
    issues: Iterable[ValidationIssue],
) -> str:
    top_balanced = (
        scenario_results[scenario_results["scenario"] == "Balanced"]
        .sort_values("rank")
        .head(1)
    )

    top_name = top_balanced.iloc[0]["experiment"] if not top_balanced.empty else "Not available"
    top_value = (
        float(top_balanced.iloc[0]["experiment_value"]) if not top_balanced.empty else math.nan
    )

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    ethics_section = "No ethics-review diagnostic file was provided."
    if ethics_summary is not None:
        ethics_section = dataframe_to_markdown_safe(
            ethics_summary[
                [
                    "experiment",
                    "requires_informed_consent",
                    "participant_burden",
                    "privacy_sensitivity",
                    "power_asymmetry",
                    "computed_review_priority",
                    "notes",
                ]
            ]
        )

    report = f"""# Iteration and Experimentation Decision-Support Report

## Article

Iteration and Experimentation in Design Thinking

## Summary

This report compares candidate design experiments using a transparent multi-criteria model. It includes scenario analysis, residual-risk decomposition, ethics-review diagnostics, uncertainty modeling, bootstrap stability, and weight sensitivity analysis.

## Balanced scenario leader

- Experiment: **{top_name}**
- Weighted experiment value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_l L_i + w_u U_i + w_e E_i - w_r R_i
\\]

where:

- \\(L_i\\) = learning gain;
- \\(U_i\\) = update flexibility or reversibility;
- \\(E_i\\) = expected improvement;
- \\(R_i\\) = residual risk.

## Residual-risk index

\\[
R_i = \\lambda_H H_i + \\lambda_O O_i + \\lambda_I I_i + \\lambda_S S_i
\\]

where:

- \\(H_i\\) = ethical or human-subject risk;
- \\(O_i\\) = operational risk;
- \\(I_i\\) = interpretive risk;
- \\(S_i\\) = scaling risk.

## Scenario count

{len(scenarios)}

## Experiment count

{len(experiments)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap_summary)}

## Weight sensitivity

{dataframe_to_markdown_safe(sensitivity_summary)}

## Ethics-review diagnostics

{ethics_section}

## Interpretation

The analysis is intended to support professional design judgment. It should be read alongside stakeholder research, prototype evidence, implementation constraints, ethical review, operational capacity, and institutional context.

An experiment that ranks highly across scenarios may be a robust candidate for early testing. An experiment that performs well only under one weighting scheme may require additional deliberation. An experiment with high learning gain but high risk may require stronger safeguards before proceeding. Ethics-review priority should be evaluated before any test involving real participants, sensitive data, power asymmetry, or public-service consequences.

## Responsible use

These outputs should not be treated as an automated experiment-selection system. The purpose is to make assumptions visible, support team deliberation, identify missing evidence, and guide responsible learning.
"""
    return report


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(
        description="Professional iteration and experimentation decision-support engine."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("../data/raw/experiments_raw.csv"),
        help="Experiment portfolio CSV file.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/experiment_scenario_weights.csv"),
        help="Scenario weights CSV file.",
    )
    parser.add_argument(
        "--ethics",
        type=Path,
        default=Path("../data/raw/experiment_ethics_review_raw.csv"),
        help="Experiment ethics-review diagnostics CSV file.",
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
    ethics_path = args.ethics if args.ethics and args.ethics.exists() else None

    return EngineConfig(
        input_path=args.input,
        weights_path=weights_path,
        ethics_path=ethics_path,
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

    experiments = read_experiments(config.input_path)
    ethics = read_ethics(config.ethics_path)

    issues = validate_experiments(experiments)
    issues.extend(validate_ethics(ethics))

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

    scenario_results = run_scenario_analysis(experiments, scenarios)

    winners, simulation_values = monte_carlo_rank_stability(
        experiments=experiments,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap_summary = bootstrap_experiment_scores(
        experiments=experiments,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity_summary = weight_sensitivity_analysis(
        experiments=experiments,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    ethics_summary = ethics_review_priority(ethics)
    rank_corr = rank_correlation_matrix(scenario_results)

    scenario_results.to_csv(config.output_dir / "iteration_experimentation_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "iteration_experimentation_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "iteration_experimentation_simulation_values.csv", index=False)
    bootstrap_summary.to_csv(config.output_dir / "iteration_experimentation_bootstrap_summary.csv", index=False)
    sensitivity_summary.to_csv(config.output_dir / "iteration_experimentation_weight_sensitivity.csv", index=False)
    rank_corr.to_csv(config.output_dir / "iteration_experimentation_rank_correlations.csv")

    if ethics_summary is not None:
        ethics_summary.to_csv(config.output_dir / "experiment_ethics_review_priorities.csv", index=False)
        save_plot_ethics_priority(
            ethics_summary,
            config.output_dir / "experiment_ethics_review_priorities.png",
        )

    save_plot_scenario_values(
        scenario_results,
        config.output_dir / "iteration_experimentation_scenario_values.png",
    )
    save_plot_rank_stability(
        winners,
        config.output_dir / "iteration_experimentation_rank_stability.png",
    )

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "input_path": str(config.input_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "ethics_path": str(config.ethics_path) if config.ethics_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_CRITERIA,
            "positive_criteria": POSITIVE_CRITERIA,
            "negative_criteria": NEGATIVE_CRITERIA,
            "risk_components": RISK_COMPONENTS,
        },
    )

    report = build_report(
        experiments=experiments,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap_summary=bootstrap_summary,
        sensitivity_summary=sensitivity_summary,
        ethics_summary=ethics_summary,
        issues=issues,
    )
    (config.output_dir / "iteration_experimentation_decision_report.md").write_text(report, encoding="utf-8")

    print("Analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- iteration_experimentation_scenario_results.csv")
    print("- iteration_experimentation_monte_carlo_winners.csv")
    print("- iteration_experimentation_weight_sensitivity.csv")
    print("- iteration_experimentation_decision_report.md")
    if ethics_summary is not None:
        print("- experiment_ethics_review_priorities.csv")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
