#!/usr/bin/env python3
"""
Professional co-design and participatory design decision-support engine.

This script evaluates participatory design activities across representation,
accessibility, participant influence, trust, evidence quality, implementation
accountability, decision impact, and ethical risk. It also analyzes participant
group coverage, affectedness-weighted participation gaps, stage-specific
influence, participatory prototype learning, risk-register priority, Monte
Carlo uncertainty, bootstrap stability, and random-weight sensitivity.

The model is intentionally interpretable:

    Q_i = w_r R_i + w_a A_i + w_p P_i + w_t T_i + w_e E_i + w_m M_i + w_d D_i - w_x X_i

where:
    R_i = representation quality
    A_i = accessibility and participation support
    P_i = participant influence
    T_i = trust and safety quality
    E_i = evidence quality
    M_i = implementation accountability
    D_i = decision impact
    X_i = ethical, tokenism, or extraction risk

The workflow supports design research, participation planning, ethical review,
and governance documentation. It does not automate community, public, ethical,
or institutional decisions.
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
    "representation",
    "accessibility",
    "participant_influence",
    "trust_quality",
    "evidence_quality",
    "implementation_accountability",
    "decision_impact",
]

CORE_WEIGHTS = [*POSITIVE_CRITERIA, "ethical_risk"]


@dataclass(frozen=True)
class EngineConfig:
    activities_path: Path
    participants_path: Path | None
    weights_path: Path | None
    learning_path: Path | None
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


def read_activities(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Co-design activities file not found: {path}")

    df = pd.read_csv(path)
    required = [
        "activity",
        "activity_type",
        "design_stage",
        *POSITIVE_CRITERIA,
        "ethical_risk",
        "affectedness_weight",
        "compensation_quality",
        "feedback_loop_quality",
        "tokenism_risk",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Co-design activities missing required columns: {missing}")

    df = df.copy()
    for col in ["activity", "activity_type", "design_stage"]:
        df[col] = df[col].astype(str).str.strip()

    numeric_cols = POSITIVE_CRITERIA + [
        "ethical_risk",
        "affectedness_weight",
        "compensation_quality",
        "feedback_loop_quality",
        "tokenism_risk",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_weights(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame(
            [
                {
                    "scenario": "Balanced",
                    "representation": 0.18,
                    "accessibility": 0.14,
                    "participant_influence": 0.22,
                    "trust_quality": 0.12,
                    "evidence_quality": 0.12,
                    "implementation_accountability": 0.12,
                    "decision_impact": 0.14,
                    "ethical_risk": 0.08,
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


def validate_activities(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["activity"].duplicated().any():
        issues.append(
            ValidationIssue(
                level="error",
                field="activity",
                message="Duplicate activity names detected.",
            )
        )

    for col in POSITIVE_CRITERIA + ["ethical_risk", "compensation_quality", "feedback_loop_quality", "tokenism_risk"]:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    invalid_weight = df[df["affectedness_weight"].isna() | (df["affectedness_weight"] < 0) | (df["affectedness_weight"] > 1)]
    if not invalid_weight.empty:
        issues.append(
            ValidationIssue(
                level="warning",
                field="affectedness_weight",
                message="Affectedness weights should be in [0, 1].",
            )
        )

    if len(df) < 3:
        issues.append(
            ValidationIssue(
                level="warning",
                field="activity",
                message="Fewer than three activities limits portfolio comparison.",
            )
        )

    return issues


def score_activities(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    scored = df.copy()

    scored["participation_quality"] = (
        weights["representation"] * scored["representation"]
        + weights["accessibility"] * scored["accessibility"]
        + weights["participant_influence"] * scored["participant_influence"]
        + weights["trust_quality"] * scored["trust_quality"]
        + weights["evidence_quality"] * scored["evidence_quality"]
        + weights["implementation_accountability"] * scored["implementation_accountability"]
        + weights["decision_impact"] * scored["decision_impact"]
        - weights["ethical_risk"] * scored["ethical_risk"]
    )

    scored["equity_participation_index"] = (
        0.26 * scored["representation"]
        + 0.24 * scored["accessibility"]
        + 0.22 * scored["participant_influence"]
        + 0.14 * scored["trust_quality"]
        + 0.08 * scored["compensation_quality"]
        + 0.06 * scored["feedback_loop_quality"]
        - 0.10 * scored["ethical_risk"]
        - 0.08 * scored["tokenism_risk"]
    )

    scored["implementation_legitimacy_index"] = (
        0.26 * scored["participant_influence"]
        + 0.24 * scored["implementation_accountability"]
        + 0.20 * scored["decision_impact"]
        + 0.14 * scored["feedback_loop_quality"]
        + 0.10 * scored["trust_quality"]
        - 0.06 * scored["tokenism_risk"]
    )

    scored["participatory_evidence_index"] = (
        0.30 * scored["evidence_quality"]
        + 0.22 * scored["representation"]
        + 0.18 * scored["participant_influence"]
        + 0.16 * scored["trust_quality"]
        + 0.14 * scored["feedback_loop_quality"]
    )

    scored["affectedness_adjusted_quality"] = (
        scored["participation_quality"] * (0.80 + 0.20 * scored["affectedness_weight"])
    )

    scored["learning_priority"] = (
        0.24 * scored["ethical_risk"]
        + 0.22 * scored["tokenism_risk"]
        + 0.16 * (10.0 - scored["representation"])
        + 0.14 * (10.0 - scored["participant_influence"])
        + 0.12 * (10.0 - scored["implementation_accountability"])
        + 0.12 * (10.0 - scored["accessibility"])
    )

    scored["process_resilience"] = (
        0.30 * scored["participation_quality"]
        + 0.26 * scored["implementation_legitimacy_index"]
        + 0.24 * scored["equity_participation_index"]
        + 0.20 * scored["participatory_evidence_index"]
        - 0.10 * scored["ethical_risk"]
    )

    scored = scored.sort_values("participation_quality", ascending=False).reset_index(drop=True)
    scored["rank"] = np.arange(1, len(scored) + 1)

    return scored


def run_scenario_analysis(activities: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_WEIGHTS}
        scored = score_activities(activities, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_WEIGHTS:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def analyze_participant_groups(participants: pd.DataFrame | None) -> pd.DataFrame:
    if participants is None:
        return pd.DataFrame()

    required = [
        "group",
        "stakeholder_type",
        "affectedness",
        "presence",
        "framing_influence",
        "synthesis_influence",
        "concept_influence",
        "testing_influence",
        "implementation_influence",
        "governance_influence",
        "access_support",
        "trust_score",
        "compensation_support",
        "language_access",
        "disability_access",
    ]
    missing = [col for col in required if col not in participants.columns]
    if missing:
        raise ValueError(f"Participant group data missing required columns: {missing}")

    df = participants.copy()
    for col in required:
        if col not in ["group", "stakeholder_type"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["stage_influence_index"] = (
        0.20 * df["framing_influence"]
        + 0.16 * df["synthesis_influence"]
        + 0.16 * df["concept_influence"]
        + 0.14 * df["testing_influence"]
        + 0.18 * df["implementation_influence"]
        + 0.16 * df["governance_influence"]
    )

    df["accessibility_support_index"] = (
        0.34 * df["access_support"]
        + 0.24 * df["language_access"]
        + 0.24 * df["disability_access"]
        + 0.18 * df["compensation_support"]
    )

    df["weighted_legitimacy"] = (
        df["affectedness"]
        * df["presence"]
        * df["stage_influence_index"]
    )

    df["participation_gap"] = df["affectedness"] * (1.0 - df["presence"])
    df["influence_gap"] = df["affectedness"] * df["presence"] * (1.0 - df["stage_influence_index"])
    df["access_gap"] = df["affectedness"] * (1.0 - df["accessibility_support_index"])
    df["trust_gap"] = df["affectedness"] * (1.0 - df["trust_score"])

    df["attention_priority"] = (
        0.32 * df["participation_gap"]
        + 0.30 * df["influence_gap"]
        + 0.22 * df["access_gap"]
        + 0.16 * df["trust_gap"]
    )

    return df.sort_values("attention_priority", ascending=False)


def summarize_participant_process(participant_summary: pd.DataFrame) -> pd.DataFrame:
    if participant_summary.empty:
        return pd.DataFrame()

    affectedness_sum = participant_summary["affectedness"].sum()

    return pd.DataFrame(
        [
            {
                "affectedness_weighted_presence": np.average(
                    participant_summary["presence"],
                    weights=participant_summary["affectedness"],
                ),
                "affectedness_weighted_influence": np.average(
                    participant_summary["stage_influence_index"],
                    weights=participant_summary["affectedness"],
                ),
                "affectedness_weighted_access_support": np.average(
                    participant_summary["accessibility_support_index"],
                    weights=participant_summary["affectedness"],
                ),
                "affectedness_weighted_trust": np.average(
                    participant_summary["trust_score"],
                    weights=participant_summary["affectedness"],
                ),
                "participatory_legitimacy": participant_summary["weighted_legitimacy"].sum() / affectedness_sum,
                "total_participation_gap": participant_summary["participation_gap"].sum(),
                "total_influence_gap": participant_summary["influence_gap"].sum(),
                "total_access_gap": participant_summary["access_gap"].sum(),
                "total_trust_gap": participant_summary["trust_gap"].sum(),
            }
        ]
    )


def analyze_prototype_learning(learning: pd.DataFrame | None) -> pd.DataFrame:
    if learning is None:
        return pd.DataFrame()

    required = [
        "activity",
        "round",
        "participant_comprehension",
        "participant_influence",
        "trust_score",
        "prototype_clarity",
        "accessibility_score",
        "burden_score",
        "decision_traceability",
        "implementation_commitment",
    ]
    missing = [col for col in required if col not in learning.columns]
    if missing:
        raise ValueError(f"Prototype learning data missing required columns: {missing}")

    df = learning.copy()
    for col in required:
        if col != "activity":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(["activity", "round"])

    df["comprehension_delta"] = df.groupby("activity")["participant_comprehension"].diff()
    df["influence_delta"] = df.groupby("activity")["participant_influence"].diff()
    df["trust_delta"] = df.groupby("activity")["trust_score"].diff()
    df["clarity_delta"] = df.groupby("activity")["prototype_clarity"].diff()
    df["accessibility_delta"] = df.groupby("activity")["accessibility_score"].diff()
    df["burden_delta"] = df.groupby("activity")["burden_score"].diff()
    df["traceability_delta"] = df.groupby("activity")["decision_traceability"].diff()
    df["implementation_delta"] = df.groupby("activity")["implementation_commitment"].diff()

    df["participatory_learning_delta"] = (
        0.15 * df["comprehension_delta"].fillna(0.0)
        + 0.20 * df["influence_delta"].fillna(0.0)
        + 0.14 * df["trust_delta"].fillna(0.0)
        + 0.13 * df["clarity_delta"].fillna(0.0)
        + 0.13 * df["accessibility_delta"].fillna(0.0)
        - 0.10 * df["burden_delta"].fillna(0.0)
        + 0.13 * df["traceability_delta"].fillna(0.0)
        + 0.12 * df["implementation_delta"].fillna(0.0)
    )

    summary = (
        df.groupby("activity")
        .agg(
            rounds=("round", "max"),
            start_comprehension=("participant_comprehension", "first"),
            final_comprehension=("participant_comprehension", "last"),
            start_influence=("participant_influence", "first"),
            final_influence=("participant_influence", "last"),
            start_trust=("trust_score", "first"),
            final_trust=("trust_score", "last"),
            start_accessibility=("accessibility_score", "first"),
            final_accessibility=("accessibility_score", "last"),
            start_burden=("burden_score", "first"),
            final_burden=("burden_score", "last"),
            start_traceability=("decision_traceability", "first"),
            final_traceability=("decision_traceability", "last"),
            start_implementation=("implementation_commitment", "first"),
            final_implementation=("implementation_commitment", "last"),
            total_participatory_learning_delta=("participatory_learning_delta", "sum"),
        )
        .reset_index()
    )

    summary["comprehension_gain"] = summary["final_comprehension"] - summary["start_comprehension"]
    summary["influence_gain"] = summary["final_influence"] - summary["start_influence"]
    summary["trust_gain"] = summary["final_trust"] - summary["start_trust"]
    summary["accessibility_gain"] = summary["final_accessibility"] - summary["start_accessibility"]
    summary["burden_reduction"] = summary["start_burden"] - summary["final_burden"]
    summary["traceability_gain"] = summary["final_traceability"] - summary["start_traceability"]
    summary["implementation_gain"] = summary["final_implementation"] - summary["start_implementation"]

    return summary.sort_values("total_participatory_learning_delta", ascending=False)


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "activity",
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
    activities: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    winner_counts: Counter[str] = Counter()
    records: List[dict] = []

    score_columns = POSITIVE_CRITERIA + ["ethical_risk"]
    means = activities[score_columns].to_numpy(dtype=float)

    for simulation_id in range(simulations):
        simulated = activities.copy()
        simulated_scores = rng.normal(loc=means, scale=score_sd)
        simulated_scores = np.clip(simulated_scores, 1.0, 10.0)
        simulated[score_columns] = simulated_scores

        scored = score_activities(simulated, weights)
        winner_counts[str(scored.iloc[0]["activity"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "activity": row["activity"],
                    "activity_type": row["activity_type"],
                    "design_stage": row["design_stage"],
                    "participation_quality": float(row["participation_quality"]),
                    "affectedness_adjusted_quality": float(row["affectedness_adjusted_quality"]),
                    "equity_participation_index": float(row["equity_participation_index"]),
                    "implementation_legitimacy_index": float(row["implementation_legitimacy_index"]),
                    "participatory_evidence_index": float(row["participatory_evidence_index"]),
                    "process_resilience": float(row["process_resilience"]),
                    "learning_priority": float(row["learning_priority"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "activity": activity,
                    "times_ranked_first": count,
                    "probability_ranked_first": count / simulations,
                }
                for activity, count in winner_counts.items()
            ]
        )
        .sort_values("probability_ranked_first", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_stability(
    activities: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = activities.sample(
            n=len(activities),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_activities(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "activity": row["activity"],
                    "participation_quality": float(row["participation_quality"]),
                    "affectedness_adjusted_quality": float(row["affectedness_adjusted_quality"]),
                    "equity_participation_index": float(row["equity_participation_index"]),
                    "implementation_legitimacy_index": float(row["implementation_legitimacy_index"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("activity")
        .agg(
            mean_participation_quality=("participation_quality", "mean"),
            sd_participation_quality=("participation_quality", "std"),
            mean_affectedness_adjusted_quality=("affectedness_adjusted_quality", "mean"),
            mean_equity_participation_index=("equity_participation_index", "mean"),
            mean_implementation_legitimacy_index=("implementation_legitimacy_index", "mean"),
            median_rank=("rank", "median"),
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
        )
        .reset_index()
        .sort_values(["median_rank", "mean_rank"])
    )


def random_weight_sensitivity(
    activities: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()

    for _ in range(samples):
        arr = rng.dirichlet(np.ones(len(CORE_WEIGHTS)))
        weights = dict(zip(CORE_WEIGHTS, arr))
        scored = score_activities(activities, weights)
        winner_counts[str(scored.iloc[0]["activity"])] += 1

    return (
        pd.DataFrame(
            [
                {
                    "activity": activity,
                    "times_won": count,
                    "probability_winning_under_random_weights": count / samples,
                }
                for activity, count in winner_counts.items()
            ]
        )
        .sort_values("probability_winning_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_plot_scenario_values(results: pd.DataFrame, output_path: Path) -> None:
    pivot = results.pivot_table(
        index="activity",
        columns="scenario",
        values="participation_quality",
        aggfunc="first",
    )
    ax = pivot.plot(kind="bar", figsize=(14, 7))
    ax.set_title("Co-Design Participation Quality Across Strategic Scenarios")
    ax.set_xlabel("Participatory design activity")
    ax.set_ylabel("Weighted participation quality")
    ax.legend(title="Scenario", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_rank_stability(winners: pd.DataFrame, output_path: Path) -> None:
    plot_df = winners.copy()
    plot_df["probability_ranked_first_pct"] = plot_df["probability_ranked_first"] * 100.0
    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["activity"], plot_df["probability_ranked_first_pct"])
    plt.title("Monte Carlo Rank Stability for Participatory Design Activities")
    plt.ylabel("Probability of ranking first (%)")
    plt.xlabel("Activity")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_participant_gaps(participant_summary: pd.DataFrame, output_path: Path) -> None:
    if participant_summary.empty:
        return
    plot_df = participant_summary.sort_values("attention_priority", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["group"], plot_df["attention_priority"])
    plt.title("Affectedness-Weighted Participation Attention Priority")
    plt.xlabel("Attention priority")
    plt.ylabel("Participant group")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_learning(learning_summary: pd.DataFrame, output_path: Path) -> None:
    if learning_summary.empty:
        return
    plot_df = learning_summary.sort_values("total_participatory_learning_delta", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["activity"], plot_df["total_participatory_learning_delta"])
    plt.title("Participatory Prototype Learning Delta")
    plt.xlabel("Total participatory learning delta")
    plt.ylabel("Activity")
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
    activities: pd.DataFrame,
    scenarios: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    participant_summary: pd.DataFrame,
    process_summary: pd.DataFrame,
    learning_summary: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    balanced = scenario_results[scenario_results["scenario"].str.lower() == "balanced"]
    top = balanced.sort_values("rank").head(1)
    top_name = top.iloc[0]["activity"] if not top.empty else "Not available"
    top_value = float(top.iloc[0]["participation_quality"]) if not top.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    participant_section = "No participant-group data provided."
    if not participant_summary.empty:
        participant_section = dataframe_to_markdown_safe(participant_summary)

    process_section = "No process summary available."
    if not process_summary.empty:
        process_section = dataframe_to_markdown_safe(process_summary)

    learning_section = "No participatory prototype-learning data provided."
    if not learning_summary.empty:
        learning_section = dataframe_to_markdown_safe(learning_summary)

    risk_section = "No risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Co-Design and Participatory Design Report

## Article

Co-Design and Participatory Design

## Summary

This report compares participatory design activities using transparent multi-criteria scoring, scenario analysis, affectedness-weighted participant-group diagnostics, accessibility and influence gaps, implementation-legitimacy review, participatory prototype-learning pathways, risk-register priority, uncertainty modeling, bootstrap stability, and random-weight sensitivity.

## Balanced scenario leader

- Activity: **{top_name}**
- Weighted participation quality: **{top_value:.3f}**

## Validation notes

{issue_lines}

## Model

\\[
Q_i = w_rR_i + w_aA_i + w_pP_i + w_tT_i + w_eE_i + w_mM_i + w_dD_i - w_xX_i
\\]

## Activity count

{len(activities)}

## Scenario count

{len(scenarios)}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Participant process summary

{process_section}

## Participant-group attention priorities

{participant_section}

## Participatory prototype-learning summary

{learning_section}

## Participation risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not automate decisions about participation, community engagement, public accountability, or design legitimacy. They support structured deliberation about representation, access, influence, trust, evidence quality, implementation accountability, decision impact, tokenism risk, ethical risk, and participation gaps. A high-scoring activity may still require community review, accessibility review, compensation review, data governance, facilitation redesign, institutional accountability, and transparent reporting before legitimacy claims are made.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional co-design and participatory design analysis engine.")
    parser.add_argument(
        "--activities",
        type=Path,
        default=Path("../data/raw/codesign_activities_raw.csv"),
        help="Co-design activities CSV.",
    )
    parser.add_argument(
        "--participants",
        type=Path,
        default=Path("../data/raw/participant_groups_raw.csv"),
        help="Participant groups CSV.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/participation_scenario_weights.csv"),
        help="Scenario weights CSV.",
    )
    parser.add_argument(
        "--learning",
        type=Path,
        default=Path("../data/raw/participatory_prototype_learning_raw.csv"),
        help="Participatory prototype learning CSV.",
    )
    parser.add_argument(
        "--risk-register",
        type=Path,
        default=Path("../data/raw/participation_risk_register_raw.csv"),
        help="Participation risk register CSV.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.55)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        activities_path=args.activities,
        participants_path=args.participants if args.participants.exists() else None,
        weights_path=args.weights if args.weights.exists() else None,
        learning_path=args.learning if args.learning.exists() else None,
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

    activities = read_activities(config.activities_path)
    scenarios = read_weights(config.weights_path)
    participants = read_optional_csv(config.participants_path)
    learning = read_optional_csv(config.learning_path)
    risk_register = read_optional_csv(config.risk_register_path)

    issues = validate_activities(activities)
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

    scenario_results = run_scenario_analysis(activities, scenarios)
    participant_summary = analyze_participant_groups(participants)
    process_summary = summarize_participant_process(participant_summary)
    learning_summary = analyze_prototype_learning(learning)
    risk_summary = analyze_risk_register(risk_register)

    winners, simulation_values = monte_carlo_rank_stability(
        activities=activities,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap = bootstrap_stability(
        activities=activities,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        activities=activities,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    review_priority = (
        score_activities(activities, balanced_weights)
        .sort_values("learning_priority", ascending=False)
        [
            [
                "activity",
                "activity_type",
                "design_stage",
                "participation_quality",
                "affectedness_adjusted_quality",
                "equity_participation_index",
                "implementation_legitimacy_index",
                "participatory_evidence_index",
                "process_resilience",
                "learning_priority",
            ]
        ]
    )

    scenario_results.to_csv(config.output_dir / "codesign_scenario_results.csv", index=False)
    winners.to_csv(config.output_dir / "codesign_monte_carlo_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "codesign_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "codesign_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "codesign_weight_sensitivity.csv", index=False)
    review_priority.to_csv(config.output_dir / "codesign_learning_priority.csv", index=False)

    if not participant_summary.empty:
        participant_summary.to_csv(config.output_dir / "participant_group_gap_summary.csv", index=False)

    if not process_summary.empty:
        process_summary.to_csv(config.output_dir / "participation_process_summary.csv", index=False)

    if not learning_summary.empty:
        learning_summary.to_csv(config.output_dir / "participatory_prototype_learning_summary.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "participation_risk_register_priority.csv", index=False)

    save_plot_scenario_values(scenario_results, config.output_dir / "codesign_scenario_values.png")
    save_plot_rank_stability(winners, config.output_dir / "codesign_rank_stability.png")
    save_plot_participant_gaps(participant_summary, config.output_dir / "participant_group_attention_priority.png")
    save_plot_learning(learning_summary, config.output_dir / "participatory_learning_delta.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "activities_path": str(config.activities_path),
                "participants_path": str(config.participants_path) if config.participants_path else None,
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "learning_path": str(config.learning_path) if config.learning_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "criteria": CORE_WEIGHTS,
            "model": "Q_i = w_rR_i + w_aA_i + w_pP_i + w_tT_i + w_eE_i + w_mM_i + w_dD_i - w_xX_i",
        },
    )

    report = build_report(
        activities=activities,
        scenarios=scenarios,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        participant_summary=participant_summary,
        process_summary=process_summary,
        learning_summary=learning_summary,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "codesign_participatory_design_report.md").write_text(report, encoding="utf-8")

    print("Co-design and participatory design analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- codesign_scenario_results.csv")
    print("- codesign_monte_carlo_winners.csv")
    print("- codesign_weight_sensitivity.csv")
    print("- participant_group_gap_summary.csv")
    print("- participatory_prototype_learning_summary.csv")
    print("- codesign_participatory_design_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
