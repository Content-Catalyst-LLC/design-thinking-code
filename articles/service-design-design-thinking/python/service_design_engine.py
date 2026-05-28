#!/usr/bin/env python3
"""
Professional service design decision-support engine.

This script evaluates service journeys across completion probability, clarity,
trust, accessibility, user burden, staff load, recovery quality, frontstage
quality, backstage readiness, policy complexity, and data dependency. It also
analyzes user-group equity gaps, frontstage/backstage blueprint dependencies,
service risk registers, Monte Carlo uncertainty, bootstrap stability, and
random-weight sensitivity.

The model is intentionally interpretable:

    Q_i = w_p P_i + w_c C_i + w_t T_i + w_a A_i + w_r R_i - w_b B_i - w_s S_i

where:
    P_i = stage completion probability
    C_i = clarity and legibility
    T_i = trust quality
    A_i = accessibility
    R_i = recovery quality
    B_i = user burden
    S_i = staff load

End-to-end service reliability is the product of stage completion probabilities.
This workflow supports service design deliberation and documentation. It does
not automate public, organizational, or service governance decisions.
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
    "completion_probability",
    "clarity",
    "trust",
    "accessibility",
    "recovery_quality",
]

NEGATIVE_CRITERIA = [
    "user_burden",
    "staff_load",
]

CORE_WEIGHTS = [*POSITIVE_CRITERIA, *NEGATIVE_CRITERIA]


@dataclass(frozen=True)
class EngineConfig:
    stages_path: Path
    groups_path: Path | None
    blueprint_path: Path | None
    weights_path: Path | None
    risk_register_path: Path | None
    output_dir: Path
    simulations: int
    seed: int
    score_sd: float
    probability_sd: float
    bootstrap_iterations: int
    sensitivity_samples: int


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    field: str
    message: str


def read_stages(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Service journey stage file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "stage",
        "stage_order",
        "channel",
        "completion_probability",
        "clarity",
        "trust",
        "accessibility",
        "user_burden",
        "staff_load",
        "recovery_quality",
        "frontstage_quality",
        "backstage_readiness",
        "policy_complexity",
        "data_dependency",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Service journey stages missing required columns: {missing}")

    df = df.copy()
    for col in ["stage", "channel"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = [
        "stage_order",
        "completion_probability",
        "clarity",
        "trust",
        "accessibility",
        "user_burden",
        "staff_load",
        "recovery_quality",
        "frontstage_quality",
        "backstage_readiness",
        "policy_complexity",
        "data_dependency",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values("stage_order").reset_index(drop=True)


def read_weights(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame(
            [
                {
                    "scenario": "Balanced",
                    "completion_probability": 0.22,
                    "clarity": 0.18,
                    "trust": 0.18,
                    "accessibility": 0.16,
                    "recovery_quality": 0.14,
                    "user_burden": 0.07,
                    "staff_load": 0.05,
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


def validate_stages(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["stage"].duplicated().any():
        issues.append(
            ValidationIssue(
                level="error",
                field="stage",
                message="Duplicate service-stage names detected.",
            )
        )

    invalid_probability = df[
        df["completion_probability"].isna()
        | (df["completion_probability"] <= 0)
        | (df["completion_probability"] > 1)
    ]
    if not invalid_probability.empty:
        issues.append(
            ValidationIssue(
                level="error",
                field="completion_probability",
                message="Completion probability must be numeric and in the interval (0, 1].",
            )
        )

    score_cols = [
        "clarity",
        "trust",
        "accessibility",
        "user_burden",
        "staff_load",
        "recovery_quality",
        "frontstage_quality",
        "backstage_readiness",
        "policy_complexity",
        "data_dependency",
    ]
    for col in score_cols:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    if len(df) < 3:
        issues.append(
            ValidationIssue(
                level="warning",
                field="stage",
                message="Fewer than three service stages limits journey reliability analysis.",
            )
        )

    return issues


def score_stages(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["service_stage_quality"] = (
        weights["completion_probability"] * scored["completion_probability"] * 10.0
        + weights["clarity"] * scored["clarity"]
        + weights["trust"] * scored["trust"]
        + weights["accessibility"] * scored["accessibility"]
        + weights["recovery_quality"] * scored["recovery_quality"]
        - weights["user_burden"] * scored["user_burden"]
        - weights["staff_load"] * scored["staff_load"]
    )

    scored["failure_risk"] = 1.0 - scored["completion_probability"]

    scored["burden_risk"] = (
        0.55 * scored["user_burden"]
        + 0.45 * scored["staff_load"]
    )

    scored["operational_friction_index"] = (
        0.22 * scored["policy_complexity"]
        + 0.22 * scored["data_dependency"]
        + 0.20 * scored["staff_load"]
        + 0.18 * (10.0 - scored["backstage_readiness"])
        + 0.18 * scored["failure_risk"] * 10.0
    )

    scored["frontstage_backstage_gap"] = (
        scored["frontstage_quality"] - scored["backstage_readiness"]
    ).abs()

    scored["procedural_dignity_index"] = (
        0.26 * scored["clarity"]
        + 0.24 * scored["trust"]
        + 0.20 * scored["accessibility"]
        + 0.18 * scored["recovery_quality"]
        - 0.12 * scored["user_burden"]
    )

    scored["redesign_priority"] = (
        0.30 * scored["failure_risk"] * 10.0
        + 0.22 * scored["burden_risk"]
        + 0.16 * (10.0 - scored["clarity"])
        + 0.12 * (10.0 - scored["accessibility"])
        + 0.10 * (10.0 - scored["recovery_quality"])
        + 0.10 * scored["operational_friction_index"]
    )

    scored["service_resilience"] = (
        0.30 * scored["service_stage_quality"]
        + 0.25 * scored["backstage_readiness"]
        + 0.20 * scored["recovery_quality"]
        + 0.15 * scored["procedural_dignity_index"]
        - 0.10 * scored["operational_friction_index"]
    )

    scored = scored.sort_values("redesign_priority", ascending=False).reset_index(drop=True)
    scored["redesign_rank"] = np.arange(1, len(scored) + 1)

    return scored


def end_to_end_reliability(stages: pd.DataFrame) -> float:
    return float(np.prod(stages["completion_probability"].to_numpy(dtype=float)))


def run_scenario_analysis(stages: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_WEIGHTS}
        scored = score_stages(stages, weights)
        scored["scenario"] = scenario["scenario"]
        scored["end_to_end_reliability"] = end_to_end_reliability(stages)
        for col in CORE_WEIGHTS:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def analyze_groups(groups: pd.DataFrame | None) -> pd.DataFrame:
    if groups is None:
        return pd.DataFrame()

    required = [
        "group",
        "affectedness",
        "completion_rate",
        "clarity",
        "accessibility",
        "trust",
        "burden",
        "recovery_access",
        "assisted_support",
        "device_access",
        "language_access",
        "disability_access",
    ]
    missing = [col for col in required if col not in groups.columns]
    if missing:
        raise ValueError(f"Service user-group data missing required columns: {missing}")

    df = groups.copy()
    df["group"] = df["group"].astype(str).str.strip()
    for col in required:
        if col != "group":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["group_service_quality"] = (
        0.24 * df["completion_rate"] * 10.0
        + 0.18 * df["clarity"]
        + 0.18 * df["accessibility"]
        + 0.16 * df["trust"]
        + 0.14 * df["recovery_access"]
        + 0.10 * df["assisted_support"]
        - 0.14 * df["burden"]
    )

    df["access_support_index"] = (
        0.25 * df["assisted_support"]
        + 0.25 * df["device_access"]
        + 0.25 * df["language_access"]
        + 0.25 * df["disability_access"]
    )

    max_quality = df["group_service_quality"].max()
    df["equity_gap"] = max_quality - df["group_service_quality"]
    df["affectedness_weighted_gap"] = df["affectedness"] * df["equity_gap"]

    df["group_attention_priority"] = (
        0.34 * df["affectedness_weighted_gap"]
        + 0.22 * (10.0 - df["accessibility"])
        + 0.18 * df["burden"]
        + 0.14 * (10.0 - df["trust"])
        + 0.12 * (10.0 - df["recovery_access"])
    )

    return df.sort_values("group_attention_priority", ascending=False)


def analyze_blueprint(blueprint: pd.DataFrame | None) -> pd.DataFrame:
    if blueprint is None:
        return pd.DataFrame()

    required = [
        "stage",
        "frontstage_actor",
        "backstage_owner",
        "support_system",
        "dependency_strength",
        "handoff_risk",
        "data_quality",
        "ownership_clarity",
        "staff_discretion",
        "automation_opacity",
        "governance_readiness",
    ]
    missing = [col for col in required if col not in blueprint.columns]
    if missing:
        raise ValueError(f"Service blueprint dependency data missing required columns: {missing}")

    df = blueprint.copy()
    for col in ["stage", "frontstage_actor", "backstage_owner", "support_system"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = [
        "dependency_strength",
        "handoff_risk",
        "data_quality",
        "ownership_clarity",
        "staff_discretion",
        "automation_opacity",
        "governance_readiness",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["blueprint_friction_index"] = (
        0.24 * df["dependency_strength"]
        + 0.24 * df["handoff_risk"]
        + 0.16 * (10.0 - df["data_quality"])
        + 0.16 * (10.0 - df["ownership_clarity"])
        + 0.10 * df["automation_opacity"]
        + 0.10 * (10.0 - df["governance_readiness"])
    )

    df["governance_attention_priority"] = (
        0.28 * df["blueprint_friction_index"]
        + 0.22 * (10.0 - df["ownership_clarity"])
        + 0.20 * (10.0 - df["governance_readiness"])
        + 0.16 * df["handoff_risk"]
        + 0.14 * df["automation_opacity"]
    )

    return df.sort_values("governance_attention_priority", ascending=False)


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "stage",
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


def monte_carlo_service_reliability(
    stages: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    probability_sd: float,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    top_priority_counts: Counter[str] = Counter()
    records: List[dict] = []

    score_columns = [
        "clarity",
        "trust",
        "accessibility",
        "user_burden",
        "staff_load",
        "recovery_quality",
        "frontstage_quality",
        "backstage_readiness",
        "policy_complexity",
        "data_dependency",
    ]

    score_means = stages[score_columns].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated = stages.copy()

        simulated["completion_probability"] = rng.normal(
            loc=stages["completion_probability"].to_numpy(dtype=float),
            scale=probability_sd,
        )
        simulated["completion_probability"] = simulated["completion_probability"].clip(0.05, 0.99)

        simulated_scores = rng.normal(loc=score_means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)
        simulated[score_columns] = simulated_scores

        scored = score_stages(simulated, weights)
        reliability = end_to_end_reliability(simulated)
        top_priority_counts[str(scored.iloc[0]["stage"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "stage": row["stage"],
                    "channel": row["channel"],
                    "service_reliability": reliability,
                    "service_stage_quality": float(row["service_stage_quality"]),
                    "failure_risk": float(row["failure_risk"]),
                    "burden_risk": float(row["burden_risk"]),
                    "operational_friction_index": float(row["operational_friction_index"]),
                    "procedural_dignity_index": float(row["procedural_dignity_index"]),
                    "redesign_priority": float(row["redesign_priority"]),
                    "service_resilience": float(row["service_resilience"]),
                    "redesign_rank": int(row["redesign_rank"]),
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "stage": stage,
                    "times_highest_priority": count,
                    "probability_highest_redesign_priority": count / simulations,
                }
                for stage, count in top_priority_counts.items()
            ]
        )
        .sort_values("probability_highest_redesign_priority", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_stability(
    stages: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = stages.sample(
            n=len(stages),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_stages(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "stage": row["stage"],
                    "service_stage_quality": float(row["service_stage_quality"]),
                    "redesign_priority": float(row["redesign_priority"]),
                    "service_resilience": float(row["service_resilience"]),
                    "redesign_rank": int(row["redesign_rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("stage")
        .agg(
            mean_service_stage_quality=("service_stage_quality", "mean"),
            sd_service_stage_quality=("service_stage_quality", "std"),
            mean_redesign_priority=("redesign_priority", "mean"),
            mean_service_resilience=("service_resilience", "mean"),
            median_redesign_rank=("redesign_rank", "median"),
            mean_redesign_rank=("redesign_rank", "mean"),
            best_redesign_rank=("redesign_rank", "min"),
            worst_redesign_rank=("redesign_rank", "max"),
        )
        .reset_index()
        .sort_values(["median_redesign_rank", "mean_redesign_rank"])
    )


def random_weight_sensitivity(
    stages: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    top_priority_counts: Counter[str] = Counter()

    for _ in range(samples):
        arr = rng.dirichlet(np.ones(len(CORE_WEIGHTS)))
        weights = dict(zip(CORE_WEIGHTS, arr))
        scored = score_stages(stages, weights)
        top_priority_counts[str(scored.iloc[0]["stage"])] += 1

    return (
        pd.DataFrame(
            [
                {
                    "stage": stage,
                    "times_highest_priority": count,
                    "probability_highest_priority_under_random_weights": count / samples,
                }
                for stage, count in top_priority_counts.items()
            ]
        )
        .sort_values("probability_highest_priority_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_plot_redesign_priority(scored: pd.DataFrame, output_path: Path) -> None:
    plot_df = scored.sort_values("redesign_priority", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["stage"], plot_df["redesign_priority"])
    plt.title("Service Journey Redesign Priority")
    plt.xlabel("Redesign priority")
    plt.ylabel("Service stage")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_group_gaps(groups: pd.DataFrame, output_path: Path) -> None:
    if groups.empty:
        return
    plot_df = groups.sort_values("group_attention_priority", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["group"], plot_df["group_attention_priority"])
    plt.title("Service Equity Group Attention Priority")
    plt.xlabel("Attention priority")
    plt.ylabel("User or stakeholder group")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_monte_carlo(winners: pd.DataFrame, output_path: Path) -> None:
    if winners.empty:
        return
    plot_df = winners.copy()
    plot_df["probability_pct"] = plot_df["probability_highest_redesign_priority"] * 100.0
    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["stage"], plot_df["probability_pct"])
    plt.title("Probability of Highest Redesign Priority Under Uncertainty")
    plt.ylabel("Probability (%)")
    plt.xlabel("Service stage")
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
    stages: pd.DataFrame,
    scenario_results: pd.DataFrame,
    reliability: float,
    monte_carlo_winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    groups: pd.DataFrame,
    blueprint: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top = scenario_results[scenario_results["scenario"].str.lower() == "balanced"].sort_values("redesign_rank").head(1)
    top_stage = top.iloc[0]["stage"] if not top.empty else "Not available"
    top_priority = float(top.iloc[0]["redesign_priority"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    group_section = "No user-group data provided."
    if not groups.empty:
        group_section = dataframe_to_markdown_safe(groups)

    blueprint_section = "No service-blueprint dependency data provided."
    if not blueprint.empty:
        blueprint_section = dataframe_to_markdown_safe(blueprint)

    risk_section = "No service risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Service Design in Design Thinking Report

## Summary

This report evaluates the service journey as an end-to-end delivery system. It includes service-stage quality, end-to-end reliability, redesign priorities, operational friction, procedural dignity, user-group equity gaps, blueprint dependency risk, service risk-register priority, uncertainty modeling, bootstrap stability, and random-weight sensitivity.

## End-to-end reliability

- Baseline end-to-end service reliability: **{reliability:.4f}**

## Highest balanced-scenario redesign priority

- Stage: **{top_stage}**
- Redesign priority: **{top_priority:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
Q_i = w_pP_i + w_cC_i + w_tT_i + w_aA_i + w_rR_i - w_bB_i - w_sS_i
\\]

## Service-stage count

{len(stages)}

## Monte Carlo highest-priority stages

{dataframe_to_markdown_safe(monte_carlo_winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## User-group equity and attention priorities

{group_section}

## Service-blueprint dependency diagnostics

{blueprint_section}

## Service risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate service decisions. They support structured deliberation about service reliability, clarity, accessibility, trust, recovery, user burden, staff load, operational dependencies, equity gaps, and governance risk. A high redesign-priority stage should be reviewed through direct user research, staff research, accessibility testing, operational analysis, service blueprinting, implementation review, and accountable governance.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional service design journey and blueprint analysis engine.")
    parser.add_argument(
        "--stages",
        type=Path,
        default=Path("../data/raw/service_journey_stages_raw.csv"),
        help="Service journey stages CSV.",
    )
    parser.add_argument(
        "--groups",
        type=Path,
        default=Path("../data/raw/service_user_groups_raw.csv"),
        help="Service user groups CSV.",
    )
    parser.add_argument(
        "--blueprint",
        type=Path,
        default=Path("../data/raw/service_blueprint_dependencies_raw.csv"),
        help="Service blueprint dependencies CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/service_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/service_risk_register_raw.csv"),
        help="Service risk register CSV.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.45)
    parser.add_argument("--probability-sd", type=float, default=0.04)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        stages_path=args.stages,
        groups_path=args.groups if args.groups.exists() else None,
        blueprint_path=args.blueprint if args.blueprint.exists() else None,
        weights_path=args.weights if args.weights.exists() else None,
        risk_register_path=args.risk_register if args.risk_register.exists() else None,
        output_dir=args.output_dir,
        simulations=args.simulations,
        seed=args.seed,
        score_sd=args.score_sd,
        probability_sd=args.probability_sd,
        bootstrap_iterations=args.bootstrap_iterations,
        sensitivity_samples=args.sensitivity_samples,
    )


def main(argv: List[str] | None = None) -> int:
    config = parse_args(argv or sys.argv[1:])
    config.output_dir.mkdir(parents=True, exist_ok=True)

    stages = read_stages(config.stages_path)
    scenarios = read_weights(config.weights_path)
    groups_raw = read_optional_csv(config.groups_path)
    blueprint_raw = read_optional_csv(config.blueprint_path)
    risk_register = read_optional_csv(config.risk_register_path)

    issues = validate_stages(stages)
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

    scenario_results = run_scenario_analysis(stages, scenarios)
    balanced_stage_scores = score_stages(stages, balanced_weights)
    groups = analyze_groups(groups_raw)
    blueprint = analyze_blueprint(blueprint_raw)
    risk_summary = analyze_risk_register(risk_register)
    reliability = end_to_end_reliability(stages)

    monte_carlo_winners, simulation_records = monte_carlo_service_reliability(
        stages=stages,
        weights=balanced_weights,
        simulations=config.simulations,
        probability_sd=config.probability_sd,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    simulation_stage_summary = (
        simulation_records.groupby("stage")
        .agg(
            mean_service_reliability=("service_reliability", "mean"),
            sd_service_reliability=("service_reliability", "std"),
            mean_service_stage_quality=("service_stage_quality", "mean"),
            mean_failure_risk=("failure_risk", "mean"),
            mean_burden_risk=("burden_risk", "mean"),
            mean_operational_friction_index=("operational_friction_index", "mean"),
            mean_redesign_priority=("redesign_priority", "mean"),
            p90_redesign_priority=("redesign_priority", lambda x: float(np.quantile(x, 0.90))),
            median_redesign_rank=("redesign_rank", "median"),
        )
        .reset_index()
        .sort_values("mean_redesign_priority", ascending=False)
    )

    bootstrap = bootstrap_stability(
        stages=stages,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        stages=stages,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    scenario_results.to_csv(config.output_dir / "service_design_scenario_results.csv", index=False)
    balanced_stage_scores.to_csv(config.output_dir / "service_stage_balanced_scores.csv", index=False)
    monte_carlo_winners.to_csv(config.output_dir / "service_design_monte_carlo_priority_winners.csv", index=False)
    simulation_records.to_csv(config.output_dir / "service_design_simulation_records.csv", index=False)
    simulation_stage_summary.to_csv(config.output_dir / "service_design_simulation_stage_summary.csv", index=False)
    bootstrap.to_csv(config.output_dir / "service_design_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "service_design_weight_sensitivity.csv", index=False)

    if not groups.empty:
        groups.to_csv(config.output_dir / "service_user_group_equity_summary.csv", index=False)

    if not blueprint.empty:
        blueprint.to_csv(config.output_dir / "service_blueprint_dependency_summary.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "service_risk_register_priority.csv", index=False)

    save_plot_redesign_priority(balanced_stage_scores, config.output_dir / "service_stage_redesign_priority.png")
    save_plot_group_gaps(groups, config.output_dir / "service_user_group_attention_priority.png")
    save_plot_monte_carlo(monte_carlo_winners, config.output_dir / "service_stage_uncertainty_priority.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "stages_path": str(config.stages_path),
                "groups_path": str(config.groups_path) if config.groups_path else None,
                "blueprint_path": str(config.blueprint_path) if config.blueprint_path else None,
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "end_to_end_reliability": reliability,
            "model": "Q_i = w_pP_i + w_cC_i + w_tT_i + w_aA_i + w_rR_i - w_bB_i - w_sS_i",
        },
    )

    report = build_report(
        stages=stages,
        scenario_results=scenario_results,
        reliability=reliability,
        monte_carlo_winners=monte_carlo_winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        groups=groups,
        blueprint=blueprint,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "service_design_report.md").write_text(report, encoding="utf-8")

    print("Service design analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- service_design_scenario_results.csv")
    print("- service_stage_balanced_scores.csv")
    print("- service_design_monte_carlo_priority_winners.csv")
    print("- service_design_simulation_stage_summary.csv")
    print("- service_user_group_equity_summary.csv")
    print("- service_blueprint_dependency_summary.csv")
    print("- service_design_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
