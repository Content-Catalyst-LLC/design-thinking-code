#!/usr/bin/env python3
"""
Professional insight-generation decision-support engine.

This script provides a reproducible workflow for comparing candidate insights
across pattern support, explanatory depth, opportunity value, interpretive risk,
risk decomposition, evidence-source diagnostics, scenario priorities, Monte
Carlo uncertainty, bootstrap stability, and weight sensitivity.

It is intended for design researchers, UX researchers, service designers,
public-sector innovation teams, civic technologists, qualitative analysts,
product strategists, and organizational research teams that need transparent
insight-prioritization support before committing to ideation, prototyping, or
implementation decisions.

Example:

    python insight_generation_engine.py \
      --input ../data/raw/candidate_insights_raw.csv \
      --weights ../data/raw/insight_scenario_weights.csv \
      --evidence ../data/raw/insight_evidence_sources_raw.csv \
      --output-dir ../outputs \
      --simulations 10000

The model is intentionally interpretable:

    V_i = w_p P_i + w_e E_i + w_o O_i - w_r R_i

A risk index may also be decomposed as:

    R_i = λ_S S_i + λ_B B_i + λ_T T_i + λ_L L_i

The output should support research interpretation, insight-quality review,
evidence validation, prototype prioritization, and institutional learning.
It should not be treated as an automated interpretation system.
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
    "pattern_support",
    "explanatory_depth",
    "opportunity_value",
    "interpretive_risk",
]

POSITIVE_CRITERIA = [
    "pattern_support",
    "explanatory_depth",
    "opportunity_value",
]

NEGATIVE_CRITERIA = [
    "interpretive_risk",
]

RISK_COMPONENTS = [
    "sampling_risk",
    "confirmation_bias_risk",
    "evidence_thinness_risk",
    "solution_capture_risk",
]

OPTIONAL_DIAGNOSTIC_COLUMNS = [
    "evidence_quality",
    "stakeholder_diversity",
    "prototype_testability",
    "implementation_relevance",
]


@dataclass(frozen=True)
class EngineConfig:
    input_path: Path
    weights_path: Path | None
    evidence_path: Path | None
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


def read_insights(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input dataset not found: {path}")

    df = pd.read_csv(path)
    required = ["insight", *CORE_CRITERIA]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Input dataset missing required columns: {missing}")

    df = df.copy()
    df["insight"] = df["insight"].astype(str).str.strip()

    numeric_cols = CORE_CRITERIA + [
        col for col in RISK_COMPONENTS + OPTIONAL_DIAGNOSTIC_COLUMNS
        if col in df.columns
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_evidence_sources(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None

    df = pd.read_csv(path)
    required = [
        "insight",
        "evidence_source_count",
        "stakeholder_groups",
        "method_count",
        "contradictory_cases",
        "validation_priority",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Evidence file missing required columns: {missing}")

    df = df.copy()
    df["insight"] = df["insight"].astype(str).str.strip()
    for col in required[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def validate_insights(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["insight"].duplicated().any():
        duplicates = df.loc[df["insight"].duplicated(), "insight"].tolist()
        issues.append(
            ValidationIssue(
                level="error",
                field="insight",
                message=f"Duplicate insight names detected: {duplicates}",
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

    for col in ["evidence_quality", "stakeholder_diversity", "prototype_testability"]:
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
                field="insight",
                message="Fewer than three candidate insights limits ranking and robustness interpretation.",
            )
        )

    return issues


def validate_evidence(df: pd.DataFrame | None) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if df is None:
        return issues

    for col in ["evidence_source_count", "stakeholder_groups", "method_count", "contradictory_cases"]:
        invalid = df[df[col].isna() | (df[col] < 0)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Evidence-source diagnostics should be non-negative numeric values.",
                )
            )

    invalid_priority = df[df["validation_priority"].isna() | (df["validation_priority"] < 0) | (df["validation_priority"] > 1)]
    if not invalid_priority.empty:
        issues.append(
            ValidationIssue(
                level="warning",
                field="validation_priority",
                message="Validation priority should be numeric and in [0, 1].",
            )
        )

    return issues


def default_scenarios() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scenario": "Balanced",
                "pattern_support": 0.30,
                "explanatory_depth": 0.30,
                "opportunity_value": 0.25,
                "interpretive_risk": 0.15,
            },
            {
                "scenario": "Pattern First",
                "pattern_support": 0.45,
                "explanatory_depth": 0.20,
                "opportunity_value": 0.20,
                "interpretive_risk": 0.15,
            },
            {
                "scenario": "Explanation First",
                "pattern_support": 0.20,
                "explanatory_depth": 0.45,
                "opportunity_value": 0.20,
                "interpretive_risk": 0.15,
            },
            {
                "scenario": "Opportunity First",
                "pattern_support": 0.20,
                "explanatory_depth": 0.20,
                "opportunity_value": 0.45,
                "interpretive_risk": 0.15,
            },
            {
                "scenario": "Risk Sensitive",
                "pattern_support": 0.25,
                "explanatory_depth": 0.20,
                "opportunity_value": 0.20,
                "interpretive_risk": 0.35,
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


def compute_interpretive_risk_index(
    df: pd.DataFrame,
    lambdas: Dict[str, float] | None = None,
) -> pd.Series:
    if lambdas is None:
        lambdas = {
            "sampling_risk": 0.30,
            "confirmation_bias_risk": 0.25,
            "evidence_thinness_risk": 0.25,
            "solution_capture_risk": 0.20,
        }

    available = [col for col in RISK_COMPONENTS if col in df.columns]
    if not available:
        return df["interpretive_risk"]

    total_weight = sum(lambdas[col] for col in available)
    risk_index = sum((lambdas[col] / total_weight) * df[col] for col in available)
    return risk_index


def score_insights(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["interpretive_risk_index"] = compute_interpretive_risk_index(scored)

    scored["insight_value"] = (
        weights["pattern_support"] * scored["pattern_support"]
        + weights["explanatory_depth"] * scored["explanatory_depth"]
        + weights["opportunity_value"] * scored["opportunity_value"]
        - weights["interpretive_risk"] * scored["interpretive_risk"]
    )

    scored["risk_index_adjusted_value"] = (
        weights["pattern_support"] * scored["pattern_support"]
        + weights["explanatory_depth"] * scored["explanatory_depth"]
        + weights["opportunity_value"] * scored["opportunity_value"]
        - weights["interpretive_risk"] * scored["interpretive_risk_index"]
    )

    scored["risk_adjusted_opportunity"] = (
        scored["opportunity_value"] - 0.40 * scored["interpretive_risk_index"]
    )

    if "evidence_quality" in scored.columns and "stakeholder_diversity" in scored.columns:
        scored["evidence_diversity_index"] = (
            0.5 * scored["evidence_quality"] + 0.5 * scored["stakeholder_diversity"]
        )
        scored["confidence_adjusted_value"] = (
            scored["insight_value"] * (0.75 + 0.25 * scored["evidence_diversity_index"])
        )
    else:
        scored["confidence_adjusted_value"] = scored["insight_value"]

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

    scored["interpretation_review_priority"] = (
        0.35 * scored["interpretive_risk_index"]
        + 0.25 * (10.0 - scored["pattern_support"])
        + 0.20 * (10.0 - scored["explanatory_depth"])
        + 0.20 * (10.0 - scored["opportunity_value"])
    )

    scored = scored.sort_values("insight_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(insights: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    outputs: List[pd.DataFrame] = []

    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_CRITERIA}
        scored = score_insights(insights, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_CRITERIA:
            scored[f"weight_{col}"] = weights[col]
        outputs.append(scored)

    return pd.concat(outputs, ignore_index=True)


def monte_carlo_rank_stability(
    insights: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    insight_names = insights["insight"].to_numpy()
    winner_counts = {name: 0 for name in insight_names}
    value_records: List[Dict[str, float | str | int]] = []

    means = insights[CORE_CRITERIA].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)

        sim_df = insights.copy()
        sim_df[CORE_CRITERIA] = simulated_scores

        if all(col in sim_df.columns for col in RISK_COMPONENTS):
            risk_component_means = insights[RISK_COMPONENTS].to_numpy(dtype=float)
            risk_component_scores = rng.normal(loc=risk_component_means, scale=score_sd)
            sim_df[RISK_COMPONENTS] = np.clip(risk_component_scores, 1.0, 10.0)

        scored = score_insights(sim_df, weights)
        winner = str(scored.iloc[0]["insight"])
        winner_counts[winner] += 1

        for _, row in scored.iterrows():
            value_records.append(
                {
                    "simulation_id": simulation_id,
                    "insight": row["insight"],
                    "insight_value": float(row["insight_value"]),
                    "interpretive_risk_index": float(row["interpretive_risk_index"]),
                    "testability_adjusted_value": float(row["testability_adjusted_value"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = pd.DataFrame(
        [
            {
                "insight": insight,
                "probability_ranked_first": count / simulations,
                "times_ranked_first": count,
            }
            for insight, count in winner_counts.items()
        ]
    ).sort_values("probability_ranked_first", ascending=False)

    simulation_values = pd.DataFrame(value_records)
    return winners, simulation_values


def bootstrap_insight_scores(
    insights: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[Dict[str, float | str | int]] = []

    for iteration in range(iterations):
        sampled = insights.sample(
            n=len(insights),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_insights(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "insight": row["insight"],
                    "insight_value": float(row["insight_value"]),
                    "interpretive_risk_index": float(row["interpretive_risk_index"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    summary = (
        boot.groupby("insight")
        .agg(
            mean_insight_value=("insight_value", "mean"),
            sd_insight_value=("insight_value", "std"),
            mean_interpretive_risk_index=("interpretive_risk_index", "mean"),
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
    insights: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    insight_names = insights["insight"].to_numpy()
    winner_counts = {name: 0 for name in insight_names}
    records: List[Dict[str, float | str]] = []

    for _ in range(samples):
        weights_arr = rng.dirichlet(alpha=np.ones(len(CORE_CRITERIA)))
        weights = dict(zip(CORE_CRITERIA, weights_arr))
        scored = score_insights(insights, weights)
        winner = str(scored.iloc[0]["insight"])
        winner_counts[winner] += 1

        records.append(
            {
                "winner": winner,
                "pattern_support_weight": weights["pattern_support"],
                "explanatory_depth_weight": weights["explanatory_depth"],
                "opportunity_value_weight": weights["opportunity_value"],
                "interpretive_risk_weight": weights["interpretive_risk"],
            }
        )

    raw = pd.DataFrame(records)
    summary = (
        raw["winner"]
        .value_counts(normalize=True)
        .rename_axis("insight")
        .reset_index(name="probability_winning_under_random_weights")
    )
    summary["times_won"] = raw["winner"].value_counts().reindex(summary["insight"]).to_numpy()

    return summary.sort_values("probability_winning_under_random_weights", ascending=False)


def evidence_validation_priority(evidence: pd.DataFrame | None) -> pd.DataFrame | None:
    if evidence is None:
        return None

    df = evidence.copy()
    df["computed_validation_priority"] = (
        0.30 * df["validation_priority"]
        + 0.20 * np.clip(df["contradictory_cases"] / 5.0, 0, 1)
        + 0.20 * (1.0 - np.clip(df["evidence_source_count"] / 25.0, 0, 1))
        + 0.15 * (1.0 - np.clip(df["stakeholder_groups"] / 6.0, 0, 1))
        + 0.15 * (1.0 - np.clip(df["method_count"] / 5.0, 0, 1))
    )
    return df.sort_values("computed_validation_priority", ascending=False)


def rank_correlation_matrix(scenario_results: pd.DataFrame) -> pd.DataFrame:
    pivot = scenario_results.pivot_table(
        index="insight",
        columns="scenario",
        values="rank",
        aggfunc="first",
    )
    return pivot.corr(method="spearman")


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="insight",
        columns="scenario",
        values="insight_value",
        aggfunc="first",
    )

    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("Candidate Insight Value Across Synthesis Scenarios")
    ax.set_xlabel("Candidate insight")
    ax.set_ylabel("Weighted insight value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["insight"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for Candidate Insights")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Candidate insight")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_validation_priority(evidence: pd.DataFrame | None, output_path: Path) -> None:
    if evidence is None or evidence.empty:
        return

    plot_df = evidence.sort_values("computed_validation_priority", ascending=True)

    plt.figure(figsize=(12, 7))
    plt.barh(plot_df["insight"], plot_df["computed_validation_priority"])
    plt.title("Evidence Validation Priority by Candidate Insight")
    plt.xlabel("Computed validation priority")
    plt.ylabel("Candidate insight")
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
    insights: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
    validation_summary: pd.DataFrame | None,
    issues: Iterable[ValidationIssue],
) -> str:
    top_balanced = (
        scenario_results[scenario_results["scenario"] == "Balanced"]
        .sort_values("rank")
        .head(1)
    )

    top_name = top_balanced.iloc[0]["insight"] if not top_balanced.empty else "Not available"
    top_value = (
        float(top_balanced.iloc[0]["insight_value"]) if not top_balanced.empty else math.nan
    )

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    validation_section = "No evidence-source diagnostic file was provided."
    if validation_summary is not None:
        validation_section = dataframe_to_markdown_safe(
            validation_summary[
                [
                    "insight",
                    "evidence_source_count",
                    "stakeholder_groups",
                    "method_count",
                    "contradictory_cases",
                    "computed_validation_priority",
                    "notes",
                ]
            ]
        )

    report = f"""# Insight Generation Decision-Support Report

## Article

Insight Generation in Design Thinking

## Summary

This report compares candidate insights using a transparent multi-criteria model. It includes scenario analysis, interpretive-risk decomposition, evidence validation diagnostics, uncertainty modeling, bootstrap stability, and weight sensitivity analysis.

## Balanced scenario leader

- Candidate insight: **{top_name}**
- Weighted insight value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_p P_i + w_e E_i + w_o O_i - w_r R_i
\\]

where:

- \\(P_i\\) = pattern support;
- \\(E_i\\) = explanatory depth;
- \\(O_i\\) = opportunity value;
- \\(R_i\\) = interpretive risk.

## Interpretive-risk index

\\[
R_i = \\lambda_S S_i + \\lambda_B B_i + \\lambda_T T_i + \\lambda_L L_i
\\]

where:

- \\(S_i\\) = sampling risk;
- \\(B_i\\) = confirmation-bias risk;
- \\(T_i\\) = evidence-thinness risk;
- \\(L_i\\) = solution-capture risk.

## Scenario count

{len(scenarios)}

## Candidate insight count

{len(insights)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap_summary)}

## Weight sensitivity

{dataframe_to_markdown_safe(sensitivity_summary)}

## Evidence validation diagnostics

{validation_section}

## Interpretation

The analysis is intended to support professional interpretation, not replace it. It should be read alongside interview excerpts, observation records, journey maps, evidence tags, synthesis notes, stakeholder validation, and prototype test results.

A candidate insight that ranks highly across scenarios may be a robust candidate for ideation or prototype testing. A candidate insight that performs well only under one weighting scheme may require additional deliberation. An insight with high opportunity value but high interpretive risk should be validated before it becomes the basis for major design decisions.

## Responsible use

These outputs should not be treated as an automated interpretation system. The purpose is to make assumptions visible, support team deliberation, identify missing evidence, and guide responsible synthesis.
"""
    return report


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(
        description="Professional insight-generation decision-support engine."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("../data/raw/candidate_insights_raw.csv"),
        help="Candidate insights CSV file.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/insight_scenario_weights.csv"),
        help="Scenario weights CSV file.",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("../data/raw/insight_evidence_sources_raw.csv"),
        help="Evidence-source diagnostics CSV file.",
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
    evidence_path = args.evidence if args.evidence and args.evidence.exists() else None

    return EngineConfig(
        input_path=args.input,
        weights_path=weights_path,
        evidence_path=evidence_path,
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

    insights = read_insights(config.input_path)
    evidence = read_evidence_sources(config.evidence_path)

    issues = validate_insights(insights)
    issues.extend(validate_evidence(evidence))

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

    scenario_results = run_scenario_analysis(insights, scenarios)

    winners, simulation_values = monte_carlo_rank_stability(
        insights=insights,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap_summary = bootstrap_insight_scores(
        insights=insights,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity_summary = weight_sensitivity_analysis(
        insights=insights,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    validation_summary = evidence_validation_priority(evidence)
    rank_corr = rank_correlation_matrix(scenario_results)

    scenario_results.to_csv(config.output_dir / "insight_generation_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "insight_generation_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "insight_generation_simulation_values.csv", index=False)
    bootstrap_summary.to_csv(config.output_dir / "insight_generation_bootstrap_summary.csv", index=False)
    sensitivity_summary.to_csv(config.output_dir / "insight_generation_weight_sensitivity.csv", index=False)
    rank_corr.to_csv(config.output_dir / "insight_generation_rank_correlations.csv")

    review_priority = (
        score_insights(insights, balanced_weights)
        .sort_values("interpretation_review_priority", ascending=False)
        [
            [
                "insight",
                "pattern_support",
                "explanatory_depth",
                "opportunity_value",
                "interpretive_risk_index",
                "interpretation_review_priority",
            ]
        ]
    )
    review_priority.to_csv(config.output_dir / "insight_interpretation_review_priority.csv", index=False)

    if validation_summary is not None:
        validation_summary.to_csv(config.output_dir / "insight_evidence_validation_priorities.csv", index=False)
        save_plot_validation_priority(
            validation_summary,
            config.output_dir / "insight_evidence_validation_priorities.png",
        )

    save_plot_scenario_values(
        scenario_results,
        config.output_dir / "insight_generation_scenario_values.png",
    )
    save_plot_rank_stability(
        winners,
        config.output_dir / "insight_generation_rank_stability.png",
    )

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "input_path": str(config.input_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "evidence_path": str(config.evidence_path) if config.evidence_path else None,
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
        insights=insights,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap_summary=bootstrap_summary,
        sensitivity_summary=sensitivity_summary,
        validation_summary=validation_summary,
        issues=issues,
    )
    (config.output_dir / "insight_generation_decision_report.md").write_text(report, encoding="utf-8")

    print("Analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- insight_generation_scenario_results.csv")
    print("- insight_generation_monte_carlo_winners.csv")
    print("- insight_generation_weight_sensitivity.csv")
    print("- insight_interpretation_review_priority.csv")
    print("- insight_generation_decision_report.md")
    if validation_summary is not None:
        print("- insight_evidence_validation_priorities.csv")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
