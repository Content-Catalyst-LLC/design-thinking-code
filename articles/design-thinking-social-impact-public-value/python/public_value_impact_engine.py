#!/usr/bin/env python3
"""
Professional public-value and social-impact design analysis engine.

This workflow evaluates social impact interventions using public value,
impact readiness, burden reduction, stewardship need, equity, access, dignity,
legitimacy, accountability, governance strength, participation quality,
community-defined value, repair capacity, and implementation risk.

It supports:
- public-value scoring;
- impact-readiness analysis;
- stewardship and repair analysis;
- stakeholder burden-reduction analysis;
- participation-quality and power-sharing review;
- risk-register prioritization;
- scenario-weighted portfolio review;
- Monte Carlo uncertainty simulation;
- bootstrap stability analysis;
- random-weight sensitivity analysis;
- reproducible reports, plots, and audit-friendly outputs.

The workflow supports structured public-value deliberation. It does not
automate community decisions, ethics review, public policy decisions,
funding allocation, or institutional accountability.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCENARIO_CRITERIA = [
    "public_value_score",
    "impact_readiness",
    "stewardship_need",
    "access",
    "equity",
    "dignity",
    "legitimacy",
    "accountability",
    "burden_reduction",
    "governance_strength",
    "participation_quality",
]


@dataclass(frozen=True)
class EngineConfig:
    interventions_path: Path
    stakeholders_path: Path | None
    participation_path: Path | None
    weights_path: Path | None
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


def read_required_csv(path: Path, name: str) -> pd.DataFrame:
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
                    "public_value_score": 0.18,
                    "impact_readiness": 0.18,
                    "stewardship_need": 0.11,
                    "access": 0.08,
                    "equity": 0.09,
                    "dignity": 0.07,
                    "legitimacy": 0.08,
                    "accountability": 0.08,
                    "burden_reduction": 0.09,
                    "governance_strength": 0.07,
                    "participation_quality": 0.07,
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


def validate_interventions(interventions: pd.DataFrame) -> List[ValidationIssue]:
    required = [
        "intervention",
        "intervention_type",
        "access",
        "equity",
        "dignity",
        "legitimacy",
        "accountability",
        "outcome_strength",
        "sustainability",
        "learning_capacity",
        "feasibility",
        "governance_strength",
        "implementation_risk",
        "burden_risk",
        "participation_quality",
        "community_defined_value",
        "repair_capacity",
        "stewardship_capacity",
    ]

    issues: List[ValidationIssue] = []
    for col in required:
        if col not in interventions.columns:
            issues.append(ValidationIssue("error", col, "Missing social impact intervention column."))

    numeric_cols = [col for col in required if col not in ["intervention", "intervention_type"]]
    issues.extend(validate_range(interventions, numeric_cols, 1, 10))
    return issues


def score_interventions(interventions: pd.DataFrame) -> pd.DataFrame:
    df = interventions.copy()

    numeric_cols = [
        "access",
        "equity",
        "dignity",
        "legitimacy",
        "accountability",
        "outcome_strength",
        "sustainability",
        "learning_capacity",
        "feasibility",
        "governance_strength",
        "implementation_risk",
        "burden_risk",
        "participation_quality",
        "community_defined_value",
        "repair_capacity",
        "stewardship_capacity",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["public_value_score"] = (
        0.13 * df["access"]
        + 0.15 * df["equity"]
        + 0.12 * df["dignity"]
        + 0.12 * df["legitimacy"]
        + 0.13 * df["accountability"]
        + 0.11 * df["outcome_strength"]
        + 0.08 * df["sustainability"]
        + 0.07 * df["learning_capacity"]
        + 0.05 * df["community_defined_value"]
        + 0.04 * df["repair_capacity"]
    )

    df["impact_readiness"] = (
        0.30 * df["public_value_score"]
        + 0.17 * df["feasibility"]
        + 0.16 * df["governance_strength"]
        + 0.12 * df["learning_capacity"]
        + 0.10 * df["participation_quality"]
        + 0.08 * df["stewardship_capacity"]
        + 0.07 * df["repair_capacity"]
        - 0.07 * df["implementation_risk"]
        - 0.07 * df["burden_risk"]
    )

    df["stewardship_need"] = (
        0.24 * df["implementation_risk"]
        + 0.22 * df["burden_risk"]
        + 0.16 * (10.0 - df["governance_strength"])
        + 0.12 * (10.0 - df["sustainability"])
        + 0.10 * (10.0 - df["learning_capacity"])
        + 0.08 * (10.0 - df["repair_capacity"])
        + 0.08 * (10.0 - df["stewardship_capacity"])
    )

    df["equity_burden_priority"] = (
        0.34 * df["equity"]
        + 0.24 * (10.0 - df["burden_risk"])
        + 0.18 * df["access"]
        + 0.12 * df["dignity"]
        + 0.12 * df["community_defined_value"]
    )

    df["portfolio_priority"] = (
        0.36 * df["public_value_score"]
        + 0.28 * df["impact_readiness"]
        + 0.14 * df["equity"]
        + 0.10 * df["community_defined_value"]
        + 0.06 * df["participation_quality"]
        - 0.14 * df["stewardship_need"]
        - 0.06 * df["implementation_risk"]
    )

    df["recommended_action"] = np.select(
        [
            (df["public_value_score"] >= 8.2) & (df["impact_readiness"] >= 7.2),
            (df["public_value_score"] >= 8.2) & (df["impact_readiness"] < 7.2),
            df["stewardship_need"] >= 6.6,
            df["burden_risk"] >= 6.8,
            df["participation_quality"] < 6.2,
            (df["feasibility"] >= 7.5) & (df["public_value_score"] >= 7.6),
        ],
        [
            "pilot_with_public_learning",
            "build_governance_before_pilot",
            "risk_and_stewardship_review",
            "burden_safeguards_required",
            "strengthen_participation_before_pilot",
            "implement_with_evaluation",
        ],
        default="develop_evidence_and_participation",
    )

    return df.sort_values("portfolio_priority", ascending=False).reset_index(drop=True)


def score_stakeholder_burden(stakeholders: pd.DataFrame | None) -> pd.DataFrame:
    if stakeholders is None:
        return pd.DataFrame()

    required = [
        "stakeholder_group",
        "stakeholder_type",
        "baseline_time_burden",
        "baseline_cognitive_burden",
        "baseline_emotional_burden",
        "baseline_documentation_burden",
        "baseline_uncertainty_burden",
        "post_time_burden",
        "post_cognitive_burden",
        "post_emotional_burden",
        "post_documentation_burden",
        "post_uncertainty_burden",
        "affectedness",
        "voice",
        "influence",
        "repair_access",
        "trust_gap",
        "accessibility_need",
    ]
    missing = [col for col in required if col not in stakeholders.columns]
    if missing:
        raise ValueError(f"Stakeholder burden file missing required columns: {missing}")

    df = stakeholders.copy()
    numeric_cols = [col for col in required if col not in ["stakeholder_group", "stakeholder_type"]]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["baseline_burden"] = (
        0.20 * df["baseline_time_burden"]
        + 0.22 * df["baseline_cognitive_burden"]
        + 0.20 * df["baseline_emotional_burden"]
        + 0.20 * df["baseline_documentation_burden"]
        + 0.18 * df["baseline_uncertainty_burden"]
    )

    df["post_burden"] = (
        0.20 * df["post_time_burden"]
        + 0.22 * df["post_cognitive_burden"]
        + 0.20 * df["post_emotional_burden"]
        + 0.20 * df["post_documentation_burden"]
        + 0.18 * df["post_uncertainty_burden"]
    )

    df["burden_reduction"] = df["baseline_burden"] - df["post_burden"]
    df["power_gap"] = 10.0 - (0.40 * df["voice"] + 0.36 * df["influence"] + 0.24 * df["repair_access"])
    df["accessibility_burden"] = df["accessibility_need"] * df["baseline_burden"]

    df["public_value_attention_priority"] = (
        0.24 * df["affectedness"] * df["baseline_burden"]
        + 0.20 * df["affectedness"] * df["power_gap"]
        + 0.16 * df["trust_gap"]
        + 0.14 * df["accessibility_burden"]
        + 0.14 * (10.0 - df["repair_access"])
        - 0.12 * df["burden_reduction"]
    )

    df["priority_action"] = np.select(
        [
            df["public_value_attention_priority"] >= 8.0,
            df["accessibility_burden"] >= 6.0,
            df["burden_reduction"] < 1.0,
            df["power_gap"] >= 5.5,
        ],
        [
            "urgent_burden_and_repair_review",
            "accessibility_and_assisted_access_review",
            "insufficient_burden_reduction",
            "power_and_voice_review",
        ],
        default="monitor_with_disaggregated_evidence",
    )

    return df.sort_values("public_value_attention_priority", ascending=False).reset_index(drop=True)


def score_participation(participation: pd.DataFrame | None) -> pd.DataFrame:
    if participation is None:
        return pd.DataFrame()

    required = [
        "participation_activity",
        "participation_level",
        "affected_people_involved",
        "decision_influence",
        "compensation",
        "accessibility_support",
        "language_support",
        "feedback_loop",
        "community_ownership",
        "power_sharing",
        "documentation_quality",
        "ethical_review",
    ]
    missing = [col for col in required if col not in participation.columns]
    if missing:
        raise ValueError(f"Participation-quality file missing required columns: {missing}")

    df = participation.copy()
    numeric_cols = [col for col in required if col not in ["participation_activity", "participation_level"]]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["participation_quality_score"] = (
        0.14 * df["affected_people_involved"]
        + 0.16 * df["decision_influence"]
        + 0.10 * df["compensation"]
        + 0.10 * df["accessibility_support"]
        + 0.08 * df["language_support"]
        + 0.10 * df["feedback_loop"]
        + 0.13 * df["community_ownership"]
        + 0.15 * df["power_sharing"]
        + 0.07 * df["documentation_quality"]
        + 0.07 * df["ethical_review"]
    )

    df["participation_gap"] = 1.0 - df["participation_quality_score"]

    df["participation_action"] = np.select(
        [
            df["participation_quality_score"] < 0.50,
            df["power_sharing"] < 0.45,
            df["decision_influence"] < 0.45,
            df["accessibility_support"] < 0.55,
            df["feedback_loop"] < 0.55,
        ],
        [
            "redesign_participation_before_use",
            "increase_power_sharing",
            "clarify_decision_influence",
            "strengthen_accessibility_support",
            "create_feedback_loop",
        ],
        default="participation_ready_with_monitoring",
    )

    return df.sort_values("participation_gap", ascending=False).reset_index(drop=True)


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "risk_id",
        "intervention",
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
        raise ValueError(f"Social impact risk register missing required columns: {missing}")

    df = risk_register.copy()
    for col in ["severity", "likelihood", "detectability", "repair_difficulty"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["risk_priority_number"] = (
        df["severity"] * df["likelihood"] * df["detectability"] * df["repair_difficulty"]
    )
    df["normalized_risk_priority"] = df["risk_priority_number"] / df["risk_priority_number"].max()

    df["risk_action"] = np.select(
        [
            df["risk_priority_number"] >= 300,
            df["severity"] >= 5,
            df["repair_difficulty"] >= 5,
        ],
        [
            "pause_until_stewardship_and_mitigation_plan",
            "ethics_and_governance_review_required",
            "repair_pathway_required_before_pilot",
        ],
        default="monitor_with_named_owner",
    )

    return df.sort_values("risk_priority_number", ascending=False).reset_index(drop=True)


def run_scenario_review(intervention_scores: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    rows: List[dict] = []

    for _, scenario in weights.iterrows():
        for _, intervention in intervention_scores.iterrows():
            priority = (
                scenario["public_value_score"] * intervention["public_value_score"] / 10.0
                + scenario["impact_readiness"] * intervention["impact_readiness"] / 10.0
                + scenario["stewardship_need"] * (10.0 - intervention["stewardship_need"]) / 10.0
                + scenario["access"] * intervention["access"] / 10.0
                + scenario["equity"] * intervention["equity"] / 10.0
                + scenario["dignity"] * intervention["dignity"] / 10.0
                + scenario["legitimacy"] * intervention["legitimacy"] / 10.0
                + scenario["accountability"] * intervention["accountability"] / 10.0
                + scenario["burden_reduction"] * (10.0 - intervention["burden_risk"]) / 10.0
                + scenario["governance_strength"] * intervention["governance_strength"] / 10.0
                + scenario["participation_quality"] * intervention["participation_quality"] / 10.0
            )

            rows.append(
                {
                    "scenario": scenario["scenario"],
                    "intervention": intervention["intervention"],
                    "intervention_type": intervention["intervention_type"],
                    "scenario_priority_score": float(priority),
                    "public_value_score": float(intervention["public_value_score"]),
                    "impact_readiness": float(intervention["impact_readiness"]),
                    "stewardship_need": float(intervention["stewardship_need"]),
                    "recommended_action": intervention["recommended_action"],
                }
            )

    result = pd.DataFrame(rows)
    result["scenario_rank"] = (
        result.groupby("scenario")["scenario_priority_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    return result.sort_values(["scenario", "scenario_rank", "intervention"]).reset_index(drop=True)


def monte_carlo_impact_stability(
    interventions: pd.DataFrame,
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    top_counts: Counter[str] = Counter()
    records: List[dict] = []

    score_cols = [
        "access",
        "equity",
        "dignity",
        "legitimacy",
        "accountability",
        "outcome_strength",
        "sustainability",
        "learning_capacity",
        "feasibility",
        "governance_strength",
        "implementation_risk",
        "burden_risk",
        "participation_quality",
        "community_defined_value",
        "repair_capacity",
        "stewardship_capacity",
    ]

    for simulation_id in range(simulations):
        simulated = interventions.copy()

        for col in score_cols:
            simulated[col] = rng.normal(
                loc=interventions[col].to_numpy(dtype=float),
                scale=score_sd,
            ).clip(1.0, 10.0)

        scored = score_interventions(simulated)
        top_counts[str(scored.iloc[0]["intervention"])] += 1

        for rank, (_, row) in enumerate(scored.iterrows(), start=1):
            records.append(
                {
                    "simulation_id": simulation_id,
                    "intervention": row["intervention"],
                    "intervention_type": row["intervention_type"],
                    "public_value_score": float(row["public_value_score"]),
                    "impact_readiness": float(row["impact_readiness"]),
                    "stewardship_need": float(row["stewardship_need"]),
                    "portfolio_priority": float(row["portfolio_priority"]),
                    "rank": rank,
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "intervention": intervention,
                    "times_top_intervention": count,
                    "probability_top_intervention": count / simulations,
                }
                for intervention, count in top_counts.items()
            ]
        )
        .sort_values("probability_top_intervention", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_intervention_stability(interventions: pd.DataFrame, iterations: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = interventions.sample(
            n=len(interventions),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_interventions(sampled)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "intervention": row["intervention"],
                    "public_value_score": float(row["public_value_score"]),
                    "impact_readiness": float(row["impact_readiness"]),
                    "stewardship_need": float(row["stewardship_need"]),
                    "portfolio_priority": float(row["portfolio_priority"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("intervention")
        .agg(
            mean_public_value=("public_value_score", "mean"),
            mean_impact_readiness=("impact_readiness", "mean"),
            mean_stewardship_need=("stewardship_need", "mean"),
            mean_portfolio_priority=("portfolio_priority", "mean"),
            sd_portfolio_priority=("portfolio_priority", "std"),
        )
        .reset_index()
        .sort_values("mean_portfolio_priority", ascending=False)
    )


def random_weight_sensitivity(intervention_scores: pd.DataFrame, samples: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()

    for _ in range(samples):
        weights = dict(zip(SCENARIO_CRITERIA, rng.dirichlet(np.ones(len(SCENARIO_CRITERIA)))))
        values = []
        for _, intervention in intervention_scores.iterrows():
            score = (
                weights["public_value_score"] * intervention["public_value_score"] / 10.0
                + weights["impact_readiness"] * intervention["impact_readiness"] / 10.0
                + weights["stewardship_need"] * (10.0 - intervention["stewardship_need"]) / 10.0
                + weights["access"] * intervention["access"] / 10.0
                + weights["equity"] * intervention["equity"] / 10.0
                + weights["dignity"] * intervention["dignity"] / 10.0
                + weights["legitimacy"] * intervention["legitimacy"] / 10.0
                + weights["accountability"] * intervention["accountability"] / 10.0
                + weights["burden_reduction"] * (10.0 - intervention["burden_risk"]) / 10.0
                + weights["governance_strength"] * intervention["governance_strength"] / 10.0
                + weights["participation_quality"] * intervention["participation_quality"] / 10.0
            )
            values.append((intervention["intervention"], score))

        winner_counts[max(values, key=lambda item: item[1])[0]] += 1

    return (
        pd.DataFrame(
            [
                {
                    "intervention": intervention,
                    "times_top_under_random_weights": count,
                    "probability_top_under_random_weights": count / samples,
                }
                for intervention, count in winner_counts.items()
            ]
        )
        .sort_values("probability_top_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_portfolio_plot(scores: pd.DataFrame, output_path: Path) -> None:
    plot_df = scores.sort_values("portfolio_priority", ascending=True)
    plt.figure(figsize=(12, 7))
    plt.barh(plot_df["intervention"], plot_df["portfolio_priority"])
    plt.title("Social Impact Public-Value Portfolio Priority")
    plt.xlabel("Portfolio priority")
    plt.ylabel("Intervention")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_readiness_stewardship_plot(scores: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(11, 7))
    sizes = np.clip(scores["public_value_score"].to_numpy(dtype=float), 1, 10) * 42
    plt.scatter(scores["stewardship_need"], scores["impact_readiness"], s=sizes)
    for _, row in scores.iterrows():
        plt.annotate(row["intervention"], (row["stewardship_need"], row["impact_readiness"]), fontsize=8)
    plt.title("Impact Readiness vs Stewardship Need")
    plt.xlabel("Stewardship need")
    plt.ylabel("Impact readiness")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_monte_carlo_plot(winners: pd.DataFrame, output_path: Path) -> None:
    if winners.empty:
        return
    plot_df = winners.copy()
    plot_df["probability_pct"] = plot_df["probability_top_intervention"] * 100.0
    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["intervention"], plot_df["probability_pct"])
    plt.title("Probability of Top Social Impact Intervention")
    plt.ylabel("Probability (%)")
    plt.xlabel("Intervention")
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
    intervention_scores: pd.DataFrame,
    stakeholder_scores: pd.DataFrame,
    participation_scores: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top_intervention = intervention_scores.iloc[0]["intervention"] if not intervention_scores.empty else "Not available"

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    stakeholder_section = "No stakeholder burden data provided."
    if not stakeholder_scores.empty:
        stakeholder_section = dataframe_to_markdown_safe(stakeholder_scores)

    participation_section = "No participation-quality data provided."
    if not participation_scores.empty:
        participation_section = dataframe_to_markdown_safe(participation_scores)

    risk_section = "No social impact risk register provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Design Thinking for Social Impact and Public Value Report

## Summary

This report evaluates social impact interventions using public value, impact readiness, stewardship need, access, equity, dignity, legitimacy, accountability, outcomes, sustainability, learning capacity, governance, burden risk, participation quality, repair capacity, and implementation risk.

## Highest portfolio-priority intervention

- Intervention: **{top_intervention}**

## Validation notes

{issue_lines}

## Social impact intervention scores

{dataframe_to_markdown_safe(intervention_scores)}

## Stakeholder burden and public-value attention priority

{stakeholder_section}

## Participation quality and power-sharing review

{participation_section}

## Scenario-weighted public-value review

{dataframe_to_markdown_safe(scenario_results.head(90))}

## Monte Carlo intervention stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap intervention stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Social impact risk-register priority

{risk_section}

## Responsible interpretation

These outputs support public-value deliberation. They do not replace community authority, public accountability, ethics review, legal review, funding decisions, implementation governance, or participatory judgment.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional public-value social impact design analysis engine.")
    parser.add_argument("--interventions", type=Path, default=Path("../data/raw/social_impact_interventions_raw.csv"))
    parser.add_argument("--stakeholders", type=Path, default=Path("../data/raw/stakeholder_burden_public_value_raw.csv"))
    parser.add_argument("--participation", type=Path, default=Path("../data/raw/participation_quality_raw.csv"))
    parser.add_argument("--weights", type=Path, default=Path("../data/raw/public_value_scenario_weights.csv"))
    parser.add_argument("--risk-register", type=Path, default=Path("../data/raw/social_impact_risk_register_raw.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.55)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        interventions_path=args.interventions,
        stakeholders_path=args.stakeholders if args.stakeholders.exists() else None,
        participation_path=args.participation if args.participation.exists() else None,
        weights_path=args.weights if args.weights.exists() else None,
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

    interventions_raw = read_required_csv(config.interventions_path, "Social impact interventions")
    stakeholders_raw = read_optional_csv(config.stakeholders_path)
    participation_raw = read_optional_csv(config.participation_path)
    weights = read_weights(config.weights_path)
    risk_register_raw = read_optional_csv(config.risk_register_path)

    issues = validate_interventions(interventions_raw)
    fatal = [issue for issue in issues if issue.level == "error"]
    if fatal:
        for issue in fatal:
            print(f"ERROR [{issue.field}]: {issue.message}", file=sys.stderr)
        return 2

    intervention_scores = score_interventions(interventions_raw)
    stakeholder_scores = score_stakeholder_burden(stakeholders_raw)
    participation_scores = score_participation(participation_raw)
    risk_summary = analyze_risk_register(risk_register_raw)
    scenario_results = run_scenario_review(intervention_scores, weights)

    winners, simulation_records = monte_carlo_impact_stability(
        interventions=interventions_raw,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    simulation_summary = (
        simulation_records.groupby("intervention")
        .agg(
            mean_public_value=("public_value_score", "mean"),
            mean_impact_readiness=("impact_readiness", "mean"),
            mean_stewardship_need=("stewardship_need", "mean"),
            mean_portfolio_priority=("portfolio_priority", "mean"),
            sd_portfolio_priority=("portfolio_priority", "std"),
            median_rank=("rank", "median"),
            p90_rank=("rank", lambda x: float(np.quantile(x, 0.90))),
        )
        .reset_index()
        .sort_values("mean_portfolio_priority", ascending=False)
    )

    bootstrap = bootstrap_intervention_stability(
        interventions=interventions_raw,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        intervention_scores=intervention_scores,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    intervention_scores.to_csv(config.output_dir / "social_impact_intervention_scores.csv", index=False)
    stakeholder_scores.to_csv(config.output_dir / "stakeholder_burden_public_value_scores.csv", index=False)
    participation_scores.to_csv(config.output_dir / "participation_quality_scores.csv", index=False)
    scenario_results.to_csv(config.output_dir / "public_value_scenario_review_results.csv", index=False)
    winners.to_csv(config.output_dir / "social_impact_monte_carlo_winners.csv", index=False)
    simulation_records.to_csv(config.output_dir / "social_impact_simulation_records.csv", index=False)
    simulation_summary.to_csv(config.output_dir / "social_impact_simulation_summary.csv", index=False)
    bootstrap.to_csv(config.output_dir / "social_impact_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "social_impact_random_weight_sensitivity.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "social_impact_risk_priority.csv", index=False)

    save_portfolio_plot(intervention_scores, config.output_dir / "social_impact_portfolio_priority.png")
    save_readiness_stewardship_plot(intervention_scores, config.output_dir / "impact_readiness_stewardship_need.png")
    save_monte_carlo_plot(winners, config.output_dir / "social_impact_monte_carlo_winners.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "interventions_path": str(config.interventions_path),
                "stakeholders_path": str(config.stakeholders_path) if config.stakeholders_path else None,
                "participation_path": str(config.participation_path) if config.participation_path else None,
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "scenario_criteria": SCENARIO_CRITERIA,
            "public_value_model": "weighted access, equity, dignity, legitimacy, accountability, outcomes, sustainability, learning, community-defined value, and repair capacity",
            "impact_readiness_model": "public value plus feasibility, governance, learning, participation, stewardship, repair, less implementation and burden risk",
            "burden_reduction_model": "baseline stakeholder burden minus post-intervention burden",
        },
    )

    report = build_report(
        intervention_scores=intervention_scores,
        stakeholder_scores=stakeholder_scores,
        participation_scores=participation_scores,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "public_value_impact_report.md").write_text(report, encoding="utf-8")

    print("Public-value social impact analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- social_impact_intervention_scores.csv")
    print("- stakeholder_burden_public_value_scores.csv")
    print("- participation_quality_scores.csv")
    print("- public_value_scenario_review_results.csv")
    print("- social_impact_monte_carlo_winners.csv")
    print("- social_impact_risk_priority.csv")
    print("- public_value_impact_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
