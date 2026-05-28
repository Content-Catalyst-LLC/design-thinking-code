#!/usr/bin/env python3
"""
Professional ethics, power, and inclusion analysis engine for design thinking.

This script evaluates stakeholder inclusion, burden, power gaps, ethical risk,
participation influence, governance risk, accessibility need, repairability,
privacy sensitivity, autonomy risk, and manipulation risk.

It supports:
- inclusion and burden scoring by stakeholder group;
- design decision ethical-risk analysis;
- participation-power analysis;
- scenario-weighted review;
- Monte Carlo uncertainty analysis;
- bootstrap rank stability;
- random-weight sensitivity;
- governance risk-register prioritization;
- reproducible reports, plots, and traceable outputs.

The workflow supports deliberation. It does not automate ethical decisions.
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


SCENARIO_CRITERIA = [
    "inclusion_score",
    "burden_score",
    "power_gap",
    "ethical_risk",
    "public_value",
    "repairability",
    "privacy_sensitivity",
    "autonomy_risk",
    "manipulation_risk",
    "accessibility_need",
    "trust_level",
]


@dataclass(frozen=True)
class EngineConfig:
    stakeholders_path: Path
    decisions_path: Path
    participation_path: Path | None
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


def read_csv_required(path: Path, name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{name} file not found: {path}")
    return pd.read_csv(path)


def read_optional_csv(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None
    return pd.read_csv(path)


def read_weights(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame(
            [
                {
                    "scenario": "Balanced",
                    "inclusion_score": 0.16,
                    "burden_score": 0.14,
                    "power_gap": 0.14,
                    "ethical_risk": 0.18,
                    "public_value": 0.09,
                    "repairability": 0.08,
                    "privacy_sensitivity": 0.07,
                    "autonomy_risk": 0.06,
                    "manipulation_risk": 0.05,
                    "accessibility_need": 0.02,
                    "trust_level": 0.01,
                }
            ]
        )

    df = pd.read_csv(path)
    required = ["scenario", *SCENARIO_CRITERIA]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Scenario weights missing required columns: {missing}")

    df = df.copy()
    df["scenario"] = df["scenario"].astype(str).str.strip()

    for col in SCENARIO_CRITERIA:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[SCENARIO_CRITERIA].isna().any().any():
        raise ValueError("Scenario weights contain missing or non-numeric values.")

    sums = df[SCENARIO_CRITERIA].sum(axis=1)
    if not np.allclose(sums, 1.0, atol=1e-6):
        raise ValueError("Each scenario weight row must sum to 1.0.")

    return df


def validate_range(df: pd.DataFrame, columns: Iterable[str], low: float, high: float) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for col in columns:
        if col not in df.columns:
            issues.append(ValidationIssue("error", col, f"Missing required column: {col}."))
            continue
        numeric = pd.to_numeric(df[col], errors="coerce")
        invalid = df[numeric.isna() | (numeric < low) | (numeric > high)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    "error",
                    col,
                    f"Column must be numeric and in the inclusive range [{low}, {high}].",
                )
            )
    return issues


def validate_inputs(stakeholders: pd.DataFrame, decisions: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    stakeholder_required = [
        "group",
        "stakeholder_type",
        "access",
        "voice",
        "safety",
        "compensation",
        "representation",
        "accountability",
        "time_burden",
        "cognitive_burden",
        "emotional_burden",
        "documentation_burden",
        "uncertainty_burden",
        "coordination_burden",
        "affectedness",
        "trust_level",
        "accessibility_need",
    ]
    missing_stakeholder = [col for col in stakeholder_required if col not in stakeholders.columns]
    for col in missing_stakeholder:
        issues.append(ValidationIssue("error", col, "Missing stakeholder column."))

    score_cols = [
        "access",
        "voice",
        "safety",
        "compensation",
        "representation",
        "accountability",
        "time_burden",
        "cognitive_burden",
        "emotional_burden",
        "documentation_burden",
        "uncertainty_burden",
        "coordination_burden",
        "trust_level",
    ]
    issues.extend(validate_range(stakeholders, score_cols, 1, 10))
    issues.extend(validate_range(stakeholders, ["affectedness", "accessibility_need"], 0, 1))

    decision_required = [
        "design_decision",
        "decision_type",
        "harm_severity",
        "probability",
        "exposure",
        "detectability",
        "accountability",
        "inclusion_strength",
        "public_value",
        "repairability",
        "privacy_sensitivity",
        "autonomy_risk",
        "manipulation_risk",
    ]
    missing_decision = [col for col in decision_required if col not in decisions.columns]
    for col in missing_decision:
        issues.append(ValidationIssue("error", col, "Missing design decision column."))

    decision_numeric = [
        "harm_severity",
        "probability",
        "exposure",
        "detectability",
        "accountability",
        "inclusion_strength",
        "public_value",
        "repairability",
        "privacy_sensitivity",
        "autonomy_risk",
        "manipulation_risk",
    ]
    issues.extend(validate_range(decisions, decision_numeric, 0, 1))

    return issues


def score_stakeholders(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.copy()

    numeric_cols = [
        "access",
        "voice",
        "safety",
        "compensation",
        "representation",
        "accountability",
        "time_burden",
        "cognitive_burden",
        "emotional_burden",
        "documentation_burden",
        "uncertainty_burden",
        "coordination_burden",
        "affectedness",
        "trust_level",
        "accessibility_need",
    ]
    for col in numeric_cols:
        scored[col] = pd.to_numeric(scored[col], errors="coerce")

    scored["inclusion_score"] = (
        0.20 * scored["access"]
        + 0.20 * scored["voice"]
        + 0.16 * scored["safety"]
        + 0.14 * scored["compensation"]
        + 0.14 * scored["representation"]
        + 0.16 * scored["accountability"]
    )

    scored["burden_score"] = (
        0.18 * scored["time_burden"]
        + 0.22 * scored["cognitive_burden"]
        + 0.18 * scored["emotional_burden"]
        + 0.16 * scored["documentation_burden"]
        + 0.16 * scored["uncertainty_burden"]
        + 0.10 * scored["coordination_burden"]
    )

    scored["power_gap"] = (
        10.0
        - (
            0.40 * scored["voice"]
            + 0.34 * scored["accountability"]
            + 0.16 * scored["compensation"]
            + 0.10 * scored["representation"]
        )
    )

    scored["accessibility_gap"] = scored["accessibility_need"] * (10.0 - scored["access"])
    scored["trust_gap"] = 10.0 - scored["trust_level"]

    scored["ethical_attention_priority"] = (
        0.28 * scored["affectedness"] * scored["burden_score"]
        + 0.24 * scored["affectedness"] * scored["power_gap"]
        + 0.18 * (10.0 - scored["inclusion_score"])
        + 0.14 * scored["accessibility_gap"]
        + 0.10 * scored["trust_gap"]
        + 0.06 * scored["affectedness"] * scored["emotional_burden"]
    )

    scored["review_flag"] = np.select(
        [
            scored["ethical_attention_priority"] >= 8.0,
            scored["burden_score"] >= 7.0,
            scored["power_gap"] >= 5.0,
            scored["accessibility_gap"] >= 3.5,
        ],
        [
            "urgent_ethics_review",
            "burden_reduction_required",
            "power_sharing_required",
            "accessibility_review_required",
        ],
        default="monitor",
    )

    return scored.sort_values("ethical_attention_priority", ascending=False).reset_index(drop=True)


def score_decisions(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.copy()
    numeric_cols = [
        "harm_severity",
        "probability",
        "exposure",
        "detectability",
        "accountability",
        "inclusion_strength",
        "public_value",
        "repairability",
        "privacy_sensitivity",
        "autonomy_risk",
        "manipulation_risk",
    ]
    for col in numeric_cols:
        scored[col] = pd.to_numeric(scored[col], errors="coerce")

    scored["ethical_risk"] = (
        scored["harm_severity"]
        * scored["probability"]
        * scored["exposure"]
        * (1.0 - scored["detectability"])
        * (1.0 - scored["accountability"])
    )

    scored["governance_need"] = (
        0.24 * scored["harm_severity"]
        + 0.16 * scored["exposure"]
        + 0.14 * (1.0 - scored["detectability"])
        + 0.14 * (1.0 - scored["accountability"])
        + 0.12 * scored["privacy_sensitivity"]
        + 0.10 * scored["autonomy_risk"]
        + 0.10 * scored["manipulation_risk"]
    )

    scored["review_priority"] = (
        0.32 * scored["ethical_risk"]
        + 0.20 * scored["harm_severity"]
        + 0.14 * scored["exposure"]
        + 0.10 * (1.0 - scored["accountability"])
        + 0.08 * (1.0 - scored["detectability"])
        + 0.06 * (1.0 - scored["inclusion_strength"])
        + 0.05 * scored["privacy_sensitivity"]
        + 0.03 * scored["autonomy_risk"]
        + 0.02 * scored["manipulation_risk"]
    )

    scored["repair_deficit"] = 1.0 - scored["repairability"]
    scored["public_value_adjusted_risk"] = scored["review_priority"] - 0.12 * scored["public_value"] + 0.10 * scored["repair_deficit"]

    scored["governance_action"] = np.select(
        [
            scored["public_value_adjusted_risk"] >= 0.55,
            scored["ethical_risk"] >= 0.09,
            scored["privacy_sensitivity"] >= 0.75,
            scored["autonomy_risk"] >= 0.65,
            scored["manipulation_risk"] >= 0.60,
        ],
        [
            "pause_until_governance_review",
            "harm_review_required",
            "privacy_review_required",
            "autonomy_review_required",
            "manipulation_review_required",
        ],
        default="proceed_with_monitoring",
    )

    return scored.sort_values("public_value_adjusted_risk", ascending=False).reset_index(drop=True)


def score_participation(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()

    required = [
        "process_component",
        "participation_level",
        "participant_influence",
        "decision_authority",
        "compensation_quality",
        "accessibility_quality",
        "feedback_loop_strength",
        "community_control",
        "documentation_transparency",
        "safety_quality",
        "interpretation_sharedness",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Participation file missing required columns: {missing}")

    scored = df.copy()
    numeric_cols = [col for col in required if col not in ["process_component", "participation_level"]]
    for col in numeric_cols:
        scored[col] = pd.to_numeric(scored[col], errors="coerce")

    scored["participation_power_score"] = (
        0.18 * scored["participant_influence"]
        + 0.18 * scored["decision_authority"]
        + 0.12 * scored["compensation_quality"]
        + 0.12 * scored["accessibility_quality"]
        + 0.12 * scored["feedback_loop_strength"]
        + 0.12 * scored["community_control"]
        + 0.08 * scored["documentation_transparency"]
        + 0.04 * scored["safety_quality"]
        + 0.04 * scored["interpretation_sharedness"]
    )

    scored["tokenism_risk"] = (
        0.30 * (1.0 - scored["decision_authority"])
        + 0.22 * (1.0 - scored["participant_influence"])
        + 0.18 * (1.0 - scored["community_control"])
        + 0.12 * (1.0 - scored["feedback_loop_strength"])
        + 0.10 * (1.0 - scored["documentation_transparency"])
        + 0.08 * (1.0 - scored["interpretation_sharedness"])
    )

    scored["participation_action"] = np.select(
        [
            scored["tokenism_risk"] >= 0.58,
            scored["decision_authority"] < 0.35,
            scored["community_control"] < 0.30,
        ],
        [
            "do_not_label_as_codesign",
            "increase_decision_authority",
            "increase_community_control",
        ],
        default="participation_strengthening_recommended",
    )

    return scored.sort_values("tokenism_risk", ascending=False).reset_index(drop=True)


def run_scenario_review(
    stakeholder_scores: pd.DataFrame,
    decision_scores: pd.DataFrame,
    weights: pd.DataFrame,
) -> pd.DataFrame:
    rows: List[dict] = []

    stakeholder_aggregate = {
        "inclusion_score": float(stakeholder_scores["inclusion_score"].mean()),
        "burden_score": float(stakeholder_scores["burden_score"].mean()),
        "power_gap": float(stakeholder_scores["power_gap"].mean()),
        "accessibility_need": float(stakeholder_scores["accessibility_need"].mean()),
        "trust_level": float(stakeholder_scores["trust_level"].mean()),
    }

    for _, scenario in weights.iterrows():
        for _, decision in decision_scores.iterrows():
            score = (
                scenario["inclusion_score"] * (10.0 - stakeholder_aggregate["inclusion_score"]) / 10.0
                + scenario["burden_score"] * stakeholder_aggregate["burden_score"] / 10.0
                + scenario["power_gap"] * stakeholder_aggregate["power_gap"] / 10.0
                + scenario["ethical_risk"] * decision["public_value_adjusted_risk"]
                + scenario["public_value"] * (1.0 - decision["public_value"])
                + scenario["repairability"] * (1.0 - decision["repairability"])
                + scenario["privacy_sensitivity"] * decision["privacy_sensitivity"]
                + scenario["autonomy_risk"] * decision["autonomy_risk"]
                + scenario["manipulation_risk"] * decision["manipulation_risk"]
                + scenario["accessibility_need"] * stakeholder_aggregate["accessibility_need"]
                + scenario["trust_level"] * (10.0 - stakeholder_aggregate["trust_level"]) / 10.0
            )

            rows.append(
                {
                    "scenario": scenario["scenario"],
                    "design_decision": decision["design_decision"],
                    "decision_type": decision["decision_type"],
                    "scenario_review_score": float(score),
                    "ethical_risk": float(decision["ethical_risk"]),
                    "review_priority": float(decision["review_priority"]),
                    "public_value_adjusted_risk": float(decision["public_value_adjusted_risk"]),
                    "governance_action": decision["governance_action"],
                }
            )

    result = pd.DataFrame(rows)
    result["scenario_rank"] = (
        result.groupby("scenario")["scenario_review_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    return result.sort_values(["scenario", "scenario_rank", "design_decision"]).reset_index(drop=True)


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "design_decision",
        "risk_category",
        "risk_description",
        "severity",
        "likelihood",
        "detectability",
        "repair_difficulty",
        "mitigation_owner",
        "mitigation_status",
    ]
    missing = [col for col in required if col not in risk_register.columns]
    if missing:
        raise ValueError(f"Risk register missing required columns: {missing}")

    df = risk_register.copy()
    for col in ["severity", "likelihood", "detectability", "repair_difficulty"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["risk_priority_number"] = df["severity"] * df["likelihood"] * df["detectability"] * df["repair_difficulty"]
    df["normalized_risk_priority"] = df["risk_priority_number"] / df["risk_priority_number"].max()
    return df.sort_values("risk_priority_number", ascending=False).reset_index(drop=True)


def monte_carlo_decision_stability(
    decisions: pd.DataFrame,
    simulations: int,
    probability_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    highest_counts: Counter[str] = Counter()
    records: List[dict] = []

    bounded_cols = [
        "harm_severity",
        "probability",
        "exposure",
        "detectability",
        "accountability",
        "inclusion_strength",
        "public_value",
        "repairability",
        "privacy_sensitivity",
        "autonomy_risk",
        "manipulation_risk",
    ]

    for simulation_id in range(simulations):
        simulated = decisions.copy()

        for col in bounded_cols:
            simulated[col] = rng.normal(
                loc=decisions[col].to_numpy(dtype=float),
                scale=probability_sd,
            ).clip(0.0, 1.0)

        scored = score_decisions(simulated)
        highest_counts[str(scored.iloc[0]["design_decision"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "design_decision": row["design_decision"],
                    "decision_type": row["decision_type"],
                    "ethical_risk": float(row["ethical_risk"]),
                    "governance_need": float(row["governance_need"]),
                    "review_priority": float(row["review_priority"]),
                    "public_value_adjusted_risk": float(row["public_value_adjusted_risk"]),
                    "rank": int(row.name) + 1,
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "design_decision": decision,
                    "times_highest_review_priority": count,
                    "probability_highest_review_priority": count / simulations,
                }
                for decision, count in highest_counts.items()
            ]
        )
        .sort_values("probability_highest_review_priority", ascending=False)
        .reset_index(drop=True)
    )
    return winners, pd.DataFrame(records)


def bootstrap_stakeholder_stability(
    stakeholders: pd.DataFrame,
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = stakeholders.sample(
            n=len(stakeholders),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_stakeholders(sampled)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "group": row["group"],
                    "inclusion_score": float(row["inclusion_score"]),
                    "burden_score": float(row["burden_score"]),
                    "power_gap": float(row["power_gap"]),
                    "ethical_attention_priority": float(row["ethical_attention_priority"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("group")
        .agg(
            mean_inclusion_score=("inclusion_score", "mean"),
            mean_burden_score=("burden_score", "mean"),
            mean_power_gap=("power_gap", "mean"),
            mean_ethical_attention_priority=("ethical_attention_priority", "mean"),
            sd_ethical_attention_priority=("ethical_attention_priority", "std"),
        )
        .reset_index()
        .sort_values("mean_ethical_attention_priority", ascending=False)
    )


def random_weight_sensitivity(
    stakeholder_scores: pd.DataFrame,
    decision_scores: pd.DataFrame,
    samples: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()

    stakeholder_aggregate = {
        "inclusion_score": float(stakeholder_scores["inclusion_score"].mean()),
        "burden_score": float(stakeholder_scores["burden_score"].mean()),
        "power_gap": float(stakeholder_scores["power_gap"].mean()),
        "accessibility_need": float(stakeholder_scores["accessibility_need"].mean()),
        "trust_level": float(stakeholder_scores["trust_level"].mean()),
    }

    for _ in range(samples):
        weights = dict(zip(SCENARIO_CRITERIA, rng.dirichlet(np.ones(len(SCENARIO_CRITERIA)))))

        values = []
        for _, decision in decision_scores.iterrows():
            score = (
                weights["inclusion_score"] * (10.0 - stakeholder_aggregate["inclusion_score"]) / 10.0
                + weights["burden_score"] * stakeholder_aggregate["burden_score"] / 10.0
                + weights["power_gap"] * stakeholder_aggregate["power_gap"] / 10.0
                + weights["ethical_risk"] * decision["public_value_adjusted_risk"]
                + weights["public_value"] * (1.0 - decision["public_value"])
                + weights["repairability"] * (1.0 - decision["repairability"])
                + weights["privacy_sensitivity"] * decision["privacy_sensitivity"]
                + weights["autonomy_risk"] * decision["autonomy_risk"]
                + weights["manipulation_risk"] * decision["manipulation_risk"]
                + weights["accessibility_need"] * stakeholder_aggregate["accessibility_need"]
                + weights["trust_level"] * (10.0 - stakeholder_aggregate["trust_level"]) / 10.0
            )
            values.append((decision["design_decision"], score))

        winner_counts[max(values, key=lambda x: x[1])[0]] += 1

    return (
        pd.DataFrame(
            [
                {
                    "design_decision": decision,
                    "times_highest_under_random_weights": count,
                    "probability_highest_under_random_weights": count / samples,
                }
                for decision, count in winner_counts.items()
            ]
        )
        .sort_values("probability_highest_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_plot_stakeholders(stakeholders: pd.DataFrame, output_path: Path) -> None:
    plot_df = stakeholders.sort_values("ethical_attention_priority", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["group"], plot_df["ethical_attention_priority"])
    plt.title("Ethical Attention Priority by Stakeholder Group")
    plt.xlabel("Ethical attention priority")
    plt.ylabel("Stakeholder group")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_decisions(decisions: pd.DataFrame, output_path: Path) -> None:
    plot_df = decisions.sort_values("public_value_adjusted_risk", ascending=True)
    plt.figure(figsize=(12, 6))
    plt.barh(plot_df["design_decision"], plot_df["public_value_adjusted_risk"])
    plt.title("Public-Value-Adjusted Ethical Risk by Design Decision")
    plt.xlabel("Public-value-adjusted risk")
    plt.ylabel("Design decision")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_monte_carlo(winners: pd.DataFrame, output_path: Path) -> None:
    if winners.empty:
        return
    plot_df = winners.copy()
    plot_df["probability_pct"] = plot_df["probability_highest_review_priority"] * 100.0
    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["design_decision"], plot_df["probability_pct"])
    plt.title("Probability of Highest Ethical Review Priority")
    plt.ylabel("Probability (%)")
    plt.xlabel("Design decision")
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
    stakeholder_scores: pd.DataFrame,
    decision_scores: pd.DataFrame,
    participation_scores: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top_group = stakeholder_scores.iloc[0]["group"] if not stakeholder_scores.empty else "Not available"
    top_decision = decision_scores.iloc[0]["design_decision"] if not decision_scores.empty else "Not available"

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    participation_section = "No participation-power data provided."
    if not participation_scores.empty:
        participation_section = dataframe_to_markdown_safe(participation_scores)

    risk_section = "No governance risk-register data provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Ethics, Power, and Inclusion in Design Thinking Report

## Summary

This report evaluates stakeholder inclusion, burden, power gaps, accessibility need, trust gaps, design-decision ethical risk, participation power, tokenism risk, governance risk, scenario-weighted review priorities, and uncertainty.

## Highest ethical attention stakeholder group

- Group: **{top_group}**

## Highest public-value-adjusted design risk

- Design decision: **{top_decision}**

## Validation notes

{issue_lines}

## Stakeholder inclusion, burden, and power scores

{dataframe_to_markdown_safe(stakeholder_scores)}

## Design decision ethical-risk scores

{dataframe_to_markdown_safe(decision_scores)}

## Participation power and tokenism risk

{participation_section}

## Scenario review results

{dataframe_to_markdown_safe(scenario_results.head(50))}

## Monte Carlo review priority stability

{dataframe_to_markdown_safe(winners)}

## Stakeholder bootstrap stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Governance risk-register priority

{risk_section}

## Responsible interpretation

These outputs do not decide ethics. They support structured deliberation about who has access, who has voice, who carries burden, who holds power, who can detect harm, who can demand repair, and which design decisions require stronger governance before testing or scaling.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional ethics, power, and inclusion analysis engine.")
    parser.add_argument("--stakeholders", type=Path, default=Path("../data/raw/stakeholder_groups_raw.csv"))
    parser.add_argument("--decisions", type=Path, default=Path("../data/raw/ethical_design_decisions_raw.csv"))
    parser.add_argument("--participation", type=Path, default=Path("../data/raw/participation_power_raw.csv"))
    parser.add_argument("--weights", type=Path, default=Path("../data/raw/ethics_scenario_weights.csv"))
    parser.add_argument("--risk-register", type=Path, default=Path("../data/raw/design_governance_risk_register_raw.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.55)
    parser.add_argument("--probability-sd", type=float, default=0.08)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        stakeholders_path=args.stakeholders,
        decisions_path=args.decisions,
        participation_path=args.participation if args.participation.exists() else None,
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

    stakeholders_raw = read_csv_required(config.stakeholders_path, "Stakeholders")
    decisions_raw = read_csv_required(config.decisions_path, "Design decisions")
    participation_raw = read_optional_csv(config.participation_path)
    weights = read_weights(config.weights_path)
    risk_register = read_optional_csv(config.risk_register_path)

    issues = validate_inputs(stakeholders_raw, decisions_raw)
    fatal = [issue for issue in issues if issue.level == "error"]
    if fatal:
        for issue in fatal:
            print(f"ERROR [{issue.field}]: {issue.message}", file=sys.stderr)
        return 2

    stakeholder_scores = score_stakeholders(stakeholders_raw)
    decision_scores = score_decisions(decisions_raw)
    participation_scores = score_participation(participation_raw)
    scenario_results = run_scenario_review(stakeholder_scores, decision_scores, weights)
    risk_summary = analyze_risk_register(risk_register)

    winners, simulation_records = monte_carlo_decision_stability(
        decisions=decisions_raw,
        simulations=config.simulations,
        probability_sd=config.probability_sd,
        seed=config.seed,
    )

    simulation_summary = (
        simulation_records.groupby("design_decision")
        .agg(
            mean_ethical_risk=("ethical_risk", "mean"),
            sd_ethical_risk=("ethical_risk", "std"),
            mean_governance_need=("governance_need", "mean"),
            mean_review_priority=("review_priority", "mean"),
            mean_public_value_adjusted_risk=("public_value_adjusted_risk", "mean"),
            median_rank=("rank", "median"),
            p90_rank=("rank", lambda x: float(np.quantile(x, 0.90))),
        )
        .reset_index()
        .sort_values("mean_public_value_adjusted_risk", ascending=False)
    )

    bootstrap = bootstrap_stakeholder_stability(
        stakeholders=stakeholders_raw,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        stakeholder_scores=stakeholder_scores,
        decision_scores=decision_scores,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    stakeholder_scores.to_csv(config.output_dir / "stakeholder_inclusion_burden_power_scores.csv", index=False)
    decision_scores.to_csv(config.output_dir / "ethical_design_decision_scores.csv", index=False)
    participation_scores.to_csv(config.output_dir / "participation_power_scores.csv", index=False)
    scenario_results.to_csv(config.output_dir / "scenario_review_results.csv", index=False)
    winners.to_csv(config.output_dir / "ethical_design_monte_carlo_winners.csv", index=False)
    simulation_records.to_csv(config.output_dir / "ethical_design_simulation_records.csv", index=False)
    simulation_summary.to_csv(config.output_dir / "ethical_design_simulation_summary.csv", index=False)
    bootstrap.to_csv(config.output_dir / "stakeholder_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "random_weight_sensitivity.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "design_governance_risk_priority.csv", index=False)

    save_plot_stakeholders(stakeholder_scores, config.output_dir / "stakeholder_ethical_attention_priority.png")
    save_plot_decisions(decision_scores, config.output_dir / "design_decision_ethical_risk.png")
    save_plot_monte_carlo(winners, config.output_dir / "ethical_design_monte_carlo_winners.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "stakeholders_path": str(config.stakeholders_path),
                "decisions_path": str(config.decisions_path),
                "participation_path": str(config.participation_path) if config.participation_path else None,
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "scenario_criteria": SCENARIO_CRITERIA,
            "ethical_risk_model": "R = H * P * X * (1 - D) * (1 - A)",
            "inclusion_model": "I = weighted access + voice + safety + compensation + representation + accountability",
            "burden_model": "B = weighted time + cognitive + emotional + documentation + uncertainty + coordination burden",
        },
    )

    report = build_report(
        stakeholder_scores=stakeholder_scores,
        decision_scores=decision_scores,
        participation_scores=participation_scores,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "ethics_power_inclusion_report.md").write_text(report, encoding="utf-8")

    print("Ethics, power, and inclusion analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- stakeholder_inclusion_burden_power_scores.csv")
    print("- ethical_design_decision_scores.csv")
    print("- participation_power_scores.csv")
    print("- scenario_review_results.csv")
    print("- ethical_design_monte_carlo_winners.csv")
    print("- design_governance_risk_priority.csv")
    print("- ethics_power_inclusion_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
