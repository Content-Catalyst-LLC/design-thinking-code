#!/usr/bin/env python3
"""
Professional human-centered design decision-support engine.

This script provides a reproducible workflow for comparing human-centered
problem-solving options across benefit, usability, stakeholder fit, burden,
burden components, scenario priorities, Monte Carlo uncertainty, bootstrap
stability, and weight sensitivity.

It is intended for human-centered design researchers, service designers,
public-sector innovation teams, healthcare improvement teams, civic technologists,
and institutional strategy groups who need transparent decision support rather
than informal workshop scoring alone.

Example:

    python human_centered_decision_engine.py \
      --input ../data/raw/human_centered_options_raw.csv \
      --weights ../data/raw/human_centered_scenario_weights.csv \
      --stakeholders ../data/raw/stakeholder_groups_raw.csv \
      --output-dir ../outputs \
      --simulations 10000

The model is intentionally interpretable:

    V_i = w_b B_i + w_u U_i + w_s S_i - w_c C_i

A burden index may also be decomposed as:

    C_i = λ_L L_i + λ_K K_i + λ_P P_i + λ_A A_i

The output should support research interpretation, stakeholder deliberation,
prototype prioritization, and institutional learning. It should not be treated
as an automated decision system.
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
    "human_benefit",
    "usability",
    "stakeholder_fit",
    "burden",
]

POSITIVE_CRITERIA = [
    "human_benefit",
    "usability",
    "stakeholder_fit",
]

NEGATIVE_CRITERIA = [
    "burden",
]

BURDEN_COMPONENTS = [
    "learning_cost",
    "compliance_cost",
    "psychological_cost",
    "access_cost",
]

OPTIONAL_DIAGNOSTIC_COLUMNS = [
    "evidence_quality",
    "stakeholder_confidence",
    "implementation_complexity",
]


@dataclass(frozen=True)
class EngineConfig:
    input_path: Path
    weights_path: Path | None
    stakeholders_path: Path | None
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


def read_design_options(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input dataset not found: {path}")

    df = pd.read_csv(path)
    required = ["option", *CORE_CRITERIA]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Input dataset missing required columns: {missing}")

    df = df.copy()
    df["option"] = df["option"].astype(str).str.strip()

    numeric_cols = CORE_CRITERIA + [
        col for col in BURDEN_COMPONENTS + OPTIONAL_DIAGNOSTIC_COLUMNS
        if col in df.columns
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_stakeholders(path: Path | None) -> pd.DataFrame | None:
    if path is None:
        return None
    if not path.exists():
        return None

    df = pd.read_csv(path)
    expected = [
        "stakeholder_group",
        "visibility_to_institution",
        "power_to_influence_design",
        "burden_exposure",
        "access_risk",
    ]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise ValueError(f"Stakeholder file missing required columns: {missing}")

    for col in expected[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def validate_design_options(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["option"].duplicated().any():
        duplicates = df.loc[df["option"].duplicated(), "option"].tolist()
        issues.append(
            ValidationIssue(
                level="error",
                field="option",
                message=f"Duplicate option names detected: {duplicates}",
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

    for col in BURDEN_COMPONENTS:
        if col in df.columns:
            invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
            if not invalid.empty:
                issues.append(
                    ValidationIssue(
                        level="warning",
                        field=col,
                        message="Burden component scores should be numeric and in [1, 10].",
                    )
                )

    for col in ["evidence_quality", "stakeholder_confidence"]:
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
                field="option",
                message="Fewer than three options limits ranking and robustness interpretation.",
            )
        )

    return issues


def validate_stakeholders(df: pd.DataFrame | None) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df is None:
        return issues

    for col in [
        "visibility_to_institution",
        "power_to_influence_design",
        "burden_exposure",
        "access_risk",
    ]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Stakeholder diagnostic scores should be numeric and in [0, 1].",
                )
            )

    return issues


def default_scenarios() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scenario": "Balanced",
                "human_benefit": 0.30,
                "usability": 0.25,
                "stakeholder_fit": 0.30,
                "burden": 0.15,
            },
            {
                "scenario": "Benefit First",
                "human_benefit": 0.45,
                "usability": 0.20,
                "stakeholder_fit": 0.20,
                "burden": 0.15,
            },
            {
                "scenario": "Usability First",
                "human_benefit": 0.20,
                "usability": 0.45,
                "stakeholder_fit": 0.20,
                "burden": 0.15,
            },
            {
                "scenario": "Stakeholder First",
                "human_benefit": 0.20,
                "usability": 0.20,
                "stakeholder_fit": 0.45,
                "burden": 0.15,
            },
            {
                "scenario": "Burden Sensitive",
                "human_benefit": 0.25,
                "usability": 0.20,
                "stakeholder_fit": 0.20,
                "burden": 0.35,
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


def compute_burden_index(
    df: pd.DataFrame,
    lambdas: Dict[str, float] | None = None,
) -> pd.Series:
    if lambdas is None:
        lambdas = {
            "learning_cost": 0.25,
            "compliance_cost": 0.30,
            "psychological_cost": 0.25,
            "access_cost": 0.20,
        }

    available = [col for col in BURDEN_COMPONENTS if col in df.columns]
    if not available:
        return df["burden"]

    total_weight = sum(lambdas[col] for col in available)
    index = sum((lambdas[col] / total_weight) * df[col] for col in available)
    return index


def score_options(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["burden_index"] = compute_burden_index(scored)
    scored["hc_value"] = (
        weights["human_benefit"] * scored["human_benefit"]
        + weights["usability"] * scored["usability"]
        + weights["stakeholder_fit"] * scored["stakeholder_fit"]
        - weights["burden"] * scored["burden"]
    )

    scored["burden_index_adjusted_value"] = (
        weights["human_benefit"] * scored["human_benefit"]
        + weights["usability"] * scored["usability"]
        + weights["stakeholder_fit"] * scored["stakeholder_fit"]
        - weights["burden"] * scored["burden_index"]
    )

    scored["burden_adjusted_fit"] = scored["stakeholder_fit"] - 0.35 * scored["burden_index"]

    if "evidence_quality" in scored.columns and "stakeholder_confidence" in scored.columns:
        scored["evidence_confidence_index"] = (
            0.5 * scored["evidence_quality"] + 0.5 * scored["stakeholder_confidence"]
        )
        scored["confidence_adjusted_value"] = (
            scored["hc_value"] * (0.75 + 0.25 * scored["evidence_confidence_index"])
        )
    else:
        scored["confidence_adjusted_value"] = scored["hc_value"]

    if "implementation_complexity" in scored.columns:
        scored["implementation_risk_adjusted_value"] = (
            scored["confidence_adjusted_value"] - 0.10 * scored["implementation_complexity"]
        )
    else:
        scored["implementation_risk_adjusted_value"] = scored["confidence_adjusted_value"]

    scored = scored.sort_values("hc_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(options: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []

    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_CRITERIA}
        scored = score_options(options, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_CRITERIA:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)

    return pd.concat(frames, ignore_index=True)


def monte_carlo_rank_stability(
    options: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    option_names = options["option"].to_numpy()
    winner_counts = {name: 0 for name in option_names}
    value_records: List[Dict[str, float | str | int]] = []

    means = options[CORE_CRITERIA].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)

        sim_df = options.copy()
        sim_df[CORE_CRITERIA] = simulated_scores

        if all(col in sim_df.columns for col in BURDEN_COMPONENTS):
            burden_component_means = options[BURDEN_COMPONENTS].to_numpy(dtype=float)
            burden_component_scores = rng.normal(loc=burden_component_means, scale=score_sd)
            sim_df[BURDEN_COMPONENTS] = np.clip(burden_component_scores, 1.0, 10.0)

        scored = score_options(sim_df, weights)
        winner = str(scored.iloc[0]["option"])
        winner_counts[winner] += 1

        for _, row in scored.iterrows():
            value_records.append(
                {
                    "simulation_id": simulation_id,
                    "option": row["option"],
                    "hc_value": float(row["hc_value"]),
                    "burden_index": float(row["burden_index"]),
                    "confidence_adjusted_value": float(row["confidence_adjusted_value"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = pd.DataFrame(
        [
            {
                "option": option,
                "probability_ranked_first": count / simulations,
                "times_ranked_first": count,
            }
            for option, count in winner_counts.items()
        ]
    ).sort_values("probability_ranked_first", ascending=False)

    simulation_values = pd.DataFrame(value_records)
    return winners, simulation_values


def bootstrap_option_scores(
    options: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[Dict[str, float | str | int]] = []

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
                    "hc_value": float(row["hc_value"]),
                    "burden_index": float(row["burden_index"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    summary = (
        boot.groupby("option")
        .agg(
            mean_hc_value=("hc_value", "mean"),
            sd_hc_value=("hc_value", "std"),
            mean_burden_index=("burden_index", "mean"),
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
    options: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    option_names = options["option"].to_numpy()
    winner_counts = {name: 0 for name in option_names}
    records: List[Dict[str, float | str]] = []

    for _ in range(samples):
        weights_arr = rng.dirichlet(alpha=np.ones(len(CORE_CRITERIA)))
        weights = dict(zip(CORE_CRITERIA, weights_arr))
        scored = score_options(options, weights)
        winner = str(scored.iloc[0]["option"])
        winner_counts[winner] += 1

        records.append(
            {
                "winner": winner,
                "human_benefit_weight": weights["human_benefit"],
                "usability_weight": weights["usability"],
                "stakeholder_fit_weight": weights["stakeholder_fit"],
                "burden_weight": weights["burden"],
            }
        )

    raw = pd.DataFrame(records)
    summary = (
        raw["winner"]
        .value_counts(normalize=True)
        .rename_axis("option")
        .reset_index(name="probability_winning_under_random_weights")
    )
    summary["times_won"] = raw["winner"].value_counts().reindex(summary["option"]).to_numpy()

    return summary.sort_values("probability_winning_under_random_weights", ascending=False)


def stakeholder_visibility_risk(stakeholders: pd.DataFrame | None) -> pd.DataFrame | None:
    if stakeholders is None:
        return None

    df = stakeholders.copy()
    df["invisibility_risk"] = 1.0 - df["visibility_to_institution"]
    df["power_gap"] = 1.0 - df["power_to_influence_design"]
    df["human_centered_exclusion_risk"] = (
        0.30 * df["invisibility_risk"]
        + 0.25 * df["power_gap"]
        + 0.25 * df["burden_exposure"]
        + 0.20 * df["access_risk"]
    )

    return df.sort_values("human_centered_exclusion_risk", ascending=False)


def rank_correlation_matrix(scenario_results: pd.DataFrame) -> pd.DataFrame:
    pivot = scenario_results.pivot_table(
        index="option",
        columns="scenario",
        values="rank",
        aggfunc="first",
    )
    return pivot.corr(method="spearman")


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="option",
        columns="scenario",
        values="hc_value",
        aggfunc="first",
    )

    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("Human-Centered Design Value Across Strategic Scenarios")
    ax.set_xlabel("Design option")
    ax.set_ylabel("Weighted human-centered value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["option"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for Human-Centered Design Options")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Design option")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_stakeholder_risk(stakeholders: pd.DataFrame | None, output_path: Path) -> None:
    if stakeholders is None or stakeholders.empty:
        return

    plot_df = stakeholders.sort_values("human_centered_exclusion_risk", ascending=True)

    plt.figure(figsize=(11, 6))
    plt.barh(plot_df["stakeholder_group"], plot_df["human_centered_exclusion_risk"])
    plt.title("Stakeholder Exclusion Risk")
    plt.xlabel("Composite exclusion risk")
    plt.ylabel("Stakeholder group")
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
    options: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
    stakeholder_risk: pd.DataFrame | None,
    issues: Iterable[ValidationIssue],
) -> str:
    top_balanced = (
        scenario_results[scenario_results["scenario"] == "Balanced"]
        .sort_values("rank")
        .head(1)
    )

    top_name = top_balanced.iloc[0]["option"] if not top_balanced.empty else "Not available"
    top_value = (
        float(top_balanced.iloc[0]["hc_value"]) if not top_balanced.empty else math.nan
    )

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    stakeholder_section = "No stakeholder diagnostic file was provided."
    if stakeholder_risk is not None:
        stakeholder_section = dataframe_to_markdown_safe(
            stakeholder_risk[
                [
                    "stakeholder_group",
                    "visibility_to_institution",
                    "power_to_influence_design",
                    "burden_exposure",
                    "access_risk",
                    "human_centered_exclusion_risk",
                ]
            ]
        )

    report = f"""# Human-Centered Design Decision-Support Report

## Article

Human-Centered Problem Solving

## Summary

This report compares human-centered design options using a transparent multi-criteria model. It includes scenario analysis, burden decomposition, uncertainty modeling, bootstrap stability, weight sensitivity analysis, and stakeholder exclusion-risk diagnostics.

## Balanced scenario leader

- Option: **{top_name}**
- Weighted human-centered value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_b B_i + w_u U_i + w_s S_i - w_c C_i
\\]

where:

- \\(B_i\\) = human benefit;
- \\(U_i\\) = usability or intelligibility;
- \\(S_i\\) = stakeholder fit;
- \\(C_i\\) = burden or user cost.

## Burden index

\\[
C_i = \\lambda_L L_i + \\lambda_K K_i + \\lambda_P P_i + \\lambda_A A_i
\\]

where:

- \\(L_i\\) = learning cost;
- \\(K_i\\) = compliance cost;
- \\(P_i\\) = psychological cost;
- \\(A_i\\) = access cost.

## Scenario count

{len(scenarios)}

## Option count

{len(options)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap_summary)}

## Weight sensitivity

{dataframe_to_markdown_safe(sensitivity_summary)}

## Stakeholder exclusion-risk diagnostic

{stakeholder_section}

## Interpretation

The analysis is intended to support professional design judgment. It should be read alongside qualitative research, stakeholder interviews, field observation, journey mapping, administrative-burden analysis, prototype testing, ethical review, and institutional context.

A design option that ranks highly across scenarios may be strategically robust. A design option that performs well only under one weighting scheme may require additional deliberation. A design option with high value but high burden may require redesign before implementation. Stakeholder groups with high exclusion-risk scores should receive additional research attention before a design direction is treated as human-centered.

## Responsible use

These outputs should not be treated as an automated decision system. The purpose is to make assumptions visible, support team deliberation, identify missing evidence, and guide further research.
"""
    return report


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(
        description="Professional human-centered problem-solving decision-support engine."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("../data/raw/human_centered_options_raw.csv"),
        help="Human-centered design options CSV file.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/human_centered_scenario_weights.csv"),
        help="Scenario weights CSV file.",
    )
    parser.add_argument(
        "--stakeholders",
        type=Path,
        default=Path("../data/raw/stakeholder_groups_raw.csv"),
        help="Stakeholder group diagnostics CSV file.",
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
    stakeholders_path = args.stakeholders if args.stakeholders and args.stakeholders.exists() else None

    return EngineConfig(
        input_path=args.input,
        weights_path=weights_path,
        stakeholders_path=stakeholders_path,
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

    options = read_design_options(config.input_path)
    stakeholders = read_stakeholders(config.stakeholders_path)

    issues = validate_design_options(options)
    issues.extend(validate_stakeholders(stakeholders))

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

    scenario_results = run_scenario_analysis(options, scenarios)
    winners, simulation_values = monte_carlo_rank_stability(
        options=options,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap_summary = bootstrap_option_scores(
        options=options,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity_summary = weight_sensitivity_analysis(
        options=options,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    stakeholder_risk = stakeholder_visibility_risk(stakeholders)
    rank_corr = rank_correlation_matrix(scenario_results)

    scenario_results.to_csv(config.output_dir / "human_centered_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "human_centered_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "human_centered_simulation_values.csv", index=False)
    bootstrap_summary.to_csv(config.output_dir / "human_centered_bootstrap_summary.csv", index=False)
    sensitivity_summary.to_csv(config.output_dir / "human_centered_weight_sensitivity.csv", index=False)
    rank_corr.to_csv(config.output_dir / "human_centered_rank_correlations.csv")

    if stakeholder_risk is not None:
        stakeholder_risk.to_csv(config.output_dir / "stakeholder_exclusion_risk.csv", index=False)
        save_plot_stakeholder_risk(
            stakeholder_risk,
            config.output_dir / "stakeholder_exclusion_risk.png",
        )

    save_plot_scenario_values(
        scenario_results,
        config.output_dir / "human_centered_scenario_values.png",
    )
    save_plot_rank_stability(
        winners,
        config.output_dir / "human_centered_rank_stability.png",
    )

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "input_path": str(config.input_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "stakeholders_path": str(config.stakeholders_path) if config.stakeholders_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_CRITERIA,
            "positive_criteria": POSITIVE_CRITERIA,
            "negative_criteria": NEGATIVE_CRITERIA,
            "burden_components": BURDEN_COMPONENTS,
        },
    )

    report = build_report(
        options=options,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap_summary=bootstrap_summary,
        sensitivity_summary=sensitivity_summary,
        stakeholder_risk=stakeholder_risk,
        issues=issues,
    )
    (config.output_dir / "human_centered_decision_report.md").write_text(report, encoding="utf-8")

    print("Analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- human_centered_scenario_results.csv")
    print("- human_centered_monte_carlo_winners.csv")
    print("- human_centered_weight_sensitivity.csv")
    print("- human_centered_decision_report.md")
    if stakeholder_risk is not None:
        print("- stakeholder_exclusion_risk.csv")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
