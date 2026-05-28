#!/usr/bin/env python3
"""
Professional problem-framing decision-support engine.

This script provides a reproducible workflow for comparing candidate problem
frames across explanatory adequacy, stakeholder/system coverage, opportunity
value, framing risk, risk decomposition, counterframe diagnostics, scenario
priorities, Monte Carlo uncertainty, bootstrap stability, and weight sensitivity.

It is intended for design researchers, service designers, public-sector labs,
strategy teams, systems thinkers, civic technologists, UX researchers, and
institutional innovation teams that need transparent decision support before
committing to solution pathways.

Example:

    python problem_framing_decision_engine.py \
      --input ../data/raw/problem_frames_raw.csv \
      --weights ../data/raw/problem_framing_scenario_weights.csv \
      --counterframes ../data/raw/counterframes_raw.csv \
      --output-dir ../outputs \
      --simulations 10000

The model is intentionally interpretable:

    V_i = w_e E_i + w_s S_i + w_o O_i - w_r R_i

A framing-risk index may also be decomposed as:

    R_i = λ_N N_i + λ_X X_i + λ_C C_i + λ_P P_i

The output should support research interpretation, stakeholder deliberation,
counterframe testing, and institutional learning. It should not be treated as
an automated definition of the problem.
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
    "explanatory_adequacy",
    "stakeholder_coverage",
    "opportunity_value",
    "framing_risk",
]

POSITIVE_CRITERIA = [
    "explanatory_adequacy",
    "stakeholder_coverage",
    "opportunity_value",
]

NEGATIVE_CRITERIA = [
    "framing_risk",
]

RISK_COMPONENTS = [
    "narrowness_risk",
    "stakeholder_exclusion_risk",
    "causality_risk",
    "political_distortion_risk",
]

OPTIONAL_DIAGNOSTIC_COLUMNS = [
    "evidence_quality",
    "frame_confidence",
    "implementation_scope",
]


@dataclass(frozen=True)
class EngineConfig:
    input_path: Path
    weights_path: Path | None
    counterframes_path: Path | None
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


def read_problem_frames(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input dataset not found: {path}")

    df = pd.read_csv(path)
    required = ["frame", *CORE_CRITERIA]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Input dataset missing required columns: {missing}")

    df = df.copy()
    df["frame"] = df["frame"].astype(str).str.strip()

    numeric_cols = CORE_CRITERIA + [
        col for col in RISK_COMPONENTS + OPTIONAL_DIAGNOSTIC_COLUMNS
        if col in df.columns
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_counterframes(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None

    df = pd.read_csv(path)
    required = [
        "dominant_frame",
        "counterframe",
        "reason_to_test",
        "missing_evidence_risk",
        "power_convenience_risk",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Counterframe file missing required columns: {missing}")

    df = df.copy()
    df["dominant_frame"] = df["dominant_frame"].astype(str).str.strip()
    df["counterframe"] = df["counterframe"].astype(str).str.strip()
    for col in ["missing_evidence_risk", "power_convenience_risk"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def validate_problem_frames(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["frame"].duplicated().any():
        duplicates = df.loc[df["frame"].duplicated(), "frame"].tolist()
        issues.append(
            ValidationIssue(
                level="error",
                field="frame",
                message=f"Duplicate frame names detected: {duplicates}",
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

    for col in ["evidence_quality", "frame_confidence"]:
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
                field="frame",
                message="Fewer than three frames limits ranking and robustness interpretation.",
            )
        )

    return issues


def validate_counterframes(df: pd.DataFrame | None) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df is None:
        return issues

    for col in ["missing_evidence_risk", "power_convenience_risk"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Counterframe risk scores should be numeric and in [0, 1].",
                )
            )

    return issues


def default_scenarios() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scenario": "Balanced",
                "explanatory_adequacy": 0.30,
                "stakeholder_coverage": 0.25,
                "opportunity_value": 0.30,
                "framing_risk": 0.15,
            },
            {
                "scenario": "Explanation First",
                "explanatory_adequacy": 0.45,
                "stakeholder_coverage": 0.20,
                "opportunity_value": 0.20,
                "framing_risk": 0.15,
            },
            {
                "scenario": "Coverage First",
                "explanatory_adequacy": 0.20,
                "stakeholder_coverage": 0.45,
                "opportunity_value": 0.20,
                "framing_risk": 0.15,
            },
            {
                "scenario": "Opportunity First",
                "explanatory_adequacy": 0.20,
                "stakeholder_coverage": 0.20,
                "opportunity_value": 0.45,
                "framing_risk": 0.15,
            },
            {
                "scenario": "Risk Sensitive",
                "explanatory_adequacy": 0.25,
                "stakeholder_coverage": 0.20,
                "opportunity_value": 0.20,
                "framing_risk": 0.35,
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


def compute_framing_risk_index(
    df: pd.DataFrame,
    lambdas: Dict[str, float] | None = None,
) -> pd.Series:
    if lambdas is None:
        lambdas = {
            "narrowness_risk": 0.25,
            "stakeholder_exclusion_risk": 0.30,
            "causality_risk": 0.25,
            "political_distortion_risk": 0.20,
        }

    available = [col for col in RISK_COMPONENTS if col in df.columns]
    if not available:
        return df["framing_risk"]

    total_weight = sum(lambdas[col] for col in available)
    risk_index = sum((lambdas[col] / total_weight) * df[col] for col in available)
    return risk_index


def score_frames(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["framing_risk_index"] = compute_framing_risk_index(scored)

    scored["frame_value"] = (
        weights["explanatory_adequacy"] * scored["explanatory_adequacy"]
        + weights["stakeholder_coverage"] * scored["stakeholder_coverage"]
        + weights["opportunity_value"] * scored["opportunity_value"]
        - weights["framing_risk"] * scored["framing_risk"]
    )

    scored["risk_index_adjusted_value"] = (
        weights["explanatory_adequacy"] * scored["explanatory_adequacy"]
        + weights["stakeholder_coverage"] * scored["stakeholder_coverage"]
        + weights["opportunity_value"] * scored["opportunity_value"]
        - weights["framing_risk"] * scored["framing_risk_index"]
    )

    scored["risk_adjusted_opportunity"] = (
        scored["opportunity_value"] - 0.40 * scored["framing_risk_index"]
    )

    if "evidence_quality" in scored.columns and "frame_confidence" in scored.columns:
        scored["evidence_confidence_index"] = (
            0.5 * scored["evidence_quality"] + 0.5 * scored["frame_confidence"]
        )
        scored["confidence_adjusted_value"] = (
            scored["frame_value"] * (0.75 + 0.25 * scored["evidence_confidence_index"])
        )
    else:
        scored["confidence_adjusted_value"] = scored["frame_value"]

    if "implementation_scope" in scored.columns:
        scored["actionability_adjusted_value"] = (
            scored["confidence_adjusted_value"] - 0.06 * scored["implementation_scope"]
        )
    else:
        scored["actionability_adjusted_value"] = scored["confidence_adjusted_value"]

    scored = scored.sort_values("frame_value", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(frames: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    outputs: List[pd.DataFrame] = []

    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_CRITERIA}
        scored = score_frames(frames, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_CRITERIA:
            scored[f"weight_{col}"] = weights[col]
        outputs.append(scored)

    return pd.concat(outputs, ignore_index=True)


def monte_carlo_rank_stability(
    frames: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    frame_names = frames["frame"].to_numpy()
    winner_counts = {name: 0 for name in frame_names}
    value_records: List[Dict[str, float | str | int]] = []

    means = frames[CORE_CRITERIA].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)

        sim_df = frames.copy()
        sim_df[CORE_CRITERIA] = simulated_scores

        if all(col in sim_df.columns for col in RISK_COMPONENTS):
            risk_component_means = frames[RISK_COMPONENTS].to_numpy(dtype=float)
            risk_component_scores = rng.normal(loc=risk_component_means, scale=score_sd)
            sim_df[RISK_COMPONENTS] = np.clip(risk_component_scores, 1.0, 10.0)

        scored = score_frames(sim_df, weights)
        winner = str(scored.iloc[0]["frame"])
        winner_counts[winner] += 1

        for _, row in scored.iterrows():
            value_records.append(
                {
                    "simulation_id": simulation_id,
                    "frame": row["frame"],
                    "frame_value": float(row["frame_value"]),
                    "framing_risk_index": float(row["framing_risk_index"]),
                    "confidence_adjusted_value": float(row["confidence_adjusted_value"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = pd.DataFrame(
        [
            {
                "frame": frame,
                "probability_ranked_first": count / simulations,
                "times_ranked_first": count,
            }
            for frame, count in winner_counts.items()
        ]
    ).sort_values("probability_ranked_first", ascending=False)

    simulation_values = pd.DataFrame(value_records)
    return winners, simulation_values


def bootstrap_frame_scores(
    frames: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[Dict[str, float | str | int]] = []

    for iteration in range(iterations):
        sampled = frames.sample(
            n=len(frames),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_frames(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "frame": row["frame"],
                    "frame_value": float(row["frame_value"]),
                    "framing_risk_index": float(row["framing_risk_index"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    summary = (
        boot.groupby("frame")
        .agg(
            mean_frame_value=("frame_value", "mean"),
            sd_frame_value=("frame_value", "std"),
            mean_framing_risk_index=("framing_risk_index", "mean"),
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
    frames: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    frame_names = frames["frame"].to_numpy()
    winner_counts = {name: 0 for name in frame_names}
    records: List[Dict[str, float | str]] = []

    for _ in range(samples):
        weights_arr = rng.dirichlet(alpha=np.ones(len(CORE_CRITERIA)))
        weights = dict(zip(CORE_CRITERIA, weights_arr))
        scored = score_frames(frames, weights)
        winner = str(scored.iloc[0]["frame"])
        winner_counts[winner] += 1

        records.append(
            {
                "winner": winner,
                "explanatory_adequacy_weight": weights["explanatory_adequacy"],
                "stakeholder_coverage_weight": weights["stakeholder_coverage"],
                "opportunity_value_weight": weights["opportunity_value"],
                "framing_risk_weight": weights["framing_risk"],
            }
        )

    raw = pd.DataFrame(records)
    summary = (
        raw["winner"]
        .value_counts(normalize=True)
        .rename_axis("frame")
        .reset_index(name="probability_winning_under_random_weights")
    )
    summary["times_won"] = raw["winner"].value_counts().reindex(summary["frame"]).to_numpy()

    return summary.sort_values("probability_winning_under_random_weights", ascending=False)


def counterframe_diagnostics(counterframes: pd.DataFrame | None) -> pd.DataFrame | None:
    if counterframes is None:
        return None

    df = counterframes.copy()
    df["counterframe_test_priority"] = (
        0.55 * df["missing_evidence_risk"] + 0.45 * df["power_convenience_risk"]
    )
    return df.sort_values("counterframe_test_priority", ascending=False)


def rank_correlation_matrix(scenario_results: pd.DataFrame) -> pd.DataFrame:
    pivot = scenario_results.pivot_table(
        index="frame",
        columns="scenario",
        values="rank",
        aggfunc="first",
    )
    return pivot.corr(method="spearman")


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="frame",
        columns="scenario",
        values="frame_value",
        aggfunc="first",
    )

    ax = pivot.plot(kind="bar", figsize=(13, 7))
    ax.set_title("Problem Frame Value Across Strategic Scenarios")
    ax.set_xlabel("Candidate frame")
    ax.set_ylabel("Weighted frame value")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0

    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["frame"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for Candidate Problem Frames")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Candidate frame")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_counterframe_priority(counterframes: pd.DataFrame | None, output_path: Path) -> None:
    if counterframes is None or counterframes.empty:
        return

    plot_df = counterframes.sort_values("counterframe_test_priority", ascending=True)
    labels = plot_df["dominant_frame"] + " → " + plot_df["counterframe"]

    plt.figure(figsize=(12, 7))
    plt.barh(labels, plot_df["counterframe_test_priority"])
    plt.title("Counterframe Test Priority")
    plt.xlabel("Composite counterframe test priority")
    plt.ylabel("Dominant frame → counterframe")
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
    frames: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
    counterframe_summary: pd.DataFrame | None,
    issues: Iterable[ValidationIssue],
) -> str:
    top_balanced = (
        scenario_results[scenario_results["scenario"] == "Balanced"]
        .sort_values("rank")
        .head(1)
    )

    top_name = top_balanced.iloc[0]["frame"] if not top_balanced.empty else "Not available"
    top_value = (
        float(top_balanced.iloc[0]["frame_value"]) if not top_balanced.empty else math.nan
    )

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    counterframe_section = "No counterframe diagnostic file was provided."
    if counterframe_summary is not None:
        counterframe_section = dataframe_to_markdown_safe(
            counterframe_summary[
                [
                    "dominant_frame",
                    "counterframe",
                    "reason_to_test",
                    "missing_evidence_risk",
                    "power_convenience_risk",
                    "counterframe_test_priority",
                ]
            ]
        )

    report = f"""# Problem Framing Decision-Support Report

## Article

Problem Framing in Design Thinking

## Summary

This report compares candidate problem frames using a transparent multi-criteria model. It includes scenario analysis, framing-risk decomposition, counterframe diagnostics, uncertainty modeling, bootstrap stability, and weight sensitivity analysis.

## Balanced scenario leader

- Frame: **{top_name}**
- Weighted frame value: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
V_i = w_e E_i + w_s S_i + w_o O_i - w_r R_i
\\]

where:

- \\(E_i\\) = explanatory adequacy;
- \\(S_i\\) = stakeholder/system coverage;
- \\(O_i\\) = opportunity value;
- \\(R_i\\) = framing risk.

## Framing-risk index

\\[
R_i = \\lambda_N N_i + \\lambda_X X_i + \\lambda_C C_i + \\lambda_P P_i
\\]

where:

- \\(N_i\\) = narrowness risk;
- \\(X_i\\) = stakeholder exclusion risk;
- \\(C_i\\) = causality risk;
- \\(P_i\\) = political distortion risk.

## Scenario count

{len(scenarios)}

## Frame count

{len(frames)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap_summary)}

## Weight sensitivity

{dataframe_to_markdown_safe(sensitivity_summary)}

## Counterframe diagnostics

{counterframe_section}

## Interpretation

The analysis is intended to support professional design judgment. It should be read alongside stakeholder research, field observation, insight synthesis, systems mapping, prototype evidence, political context, and institutional constraints.

A frame that ranks highly across scenarios may be strategically robust. A frame that performs well only under one weighting scheme may require additional deliberation. A frame with high opportunity value but high framing risk may require further research before being used as the basis for ideation or prototyping. Counterframes with high test-priority scores should be examined before a dominant frame becomes official.

## Responsible use

These outputs should not be treated as an automated problem definition. The purpose is to make assumptions visible, support team deliberation, identify missing evidence, and guide further research.
"""
    return report


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(
        description="Professional problem-framing decision-support engine."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("../data/raw/problem_frames_raw.csv"),
        help="Candidate problem frames CSV file.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/problem_framing_scenario_weights.csv"),
        help="Scenario weights CSV file.",
    )
    parser.add_argument(
        "--counterframes",
        type=Path,
        default=Path("../data/raw/counterframes_raw.csv"),
        help="Counterframe diagnostics CSV file.",
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
    counterframes_path = args.counterframes if args.counterframes and args.counterframes.exists() else None

    return EngineConfig(
        input_path=args.input,
        weights_path=weights_path,
        counterframes_path=counterframes_path,
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

    frames = read_problem_frames(config.input_path)
    counterframes = read_counterframes(config.counterframes_path)

    issues = validate_problem_frames(frames)
    issues.extend(validate_counterframes(counterframes))

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

    scenario_results = run_scenario_analysis(frames, scenarios)

    winners, simulation_values = monte_carlo_rank_stability(
        frames=frames,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap_summary = bootstrap_frame_scores(
        frames=frames,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity_summary = weight_sensitivity_analysis(
        frames=frames,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    counterframe_summary = counterframe_diagnostics(counterframes)
    rank_corr = rank_correlation_matrix(scenario_results)

    scenario_results.to_csv(config.output_dir / "problem_framing_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "problem_framing_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "problem_framing_simulation_values.csv", index=False)
    bootstrap_summary.to_csv(config.output_dir / "problem_framing_bootstrap_summary.csv", index=False)
    sensitivity_summary.to_csv(config.output_dir / "problem_framing_weight_sensitivity.csv", index=False)
    rank_corr.to_csv(config.output_dir / "problem_framing_rank_correlations.csv")

    if counterframe_summary is not None:
        counterframe_summary.to_csv(config.output_dir / "counterframe_test_priorities.csv", index=False)
        save_plot_counterframe_priority(
            counterframe_summary,
            config.output_dir / "counterframe_test_priorities.png",
        )

    save_plot_scenario_values(
        scenario_results,
        config.output_dir / "problem_framing_scenario_values.png",
    )
    save_plot_rank_stability(
        winners,
        config.output_dir / "problem_framing_rank_stability.png",
    )

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "input_path": str(config.input_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "counterframes_path": str(config.counterframes_path) if config.counterframes_path else None,
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
        frames=frames,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap_summary=bootstrap_summary,
        sensitivity_summary=sensitivity_summary,
        counterframe_summary=counterframe_summary,
        issues=issues,
    )
    (config.output_dir / "problem_framing_decision_report.md").write_text(report, encoding="utf-8")

    print("Analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- problem_framing_scenario_results.csv")
    print("- problem_framing_monte_carlo_winners.csv")
    print("- problem_framing_weight_sensitivity.csv")
    print("- problem_framing_decision_report.md")
    if counterframe_summary is not None:
        print("- counterframe_test_priorities.csv")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
