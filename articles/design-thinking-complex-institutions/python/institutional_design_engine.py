#!/usr/bin/env python3
"""
Professional institutional design-thinking analysis engine.

This workflow evaluates institutional design options using change readiness,
absorption capacity, public value, burden reduction, governance strength,
equity priority, implementation risk, coordination complexity, data readiness,
trust gain, and stakeholder burden.

It supports:
- institutional design option scoring;
- portfolio sequencing;
- stakeholder burden and voice-gap analysis;
- governance decision-rights review;
- institutional risk-register prioritization;
- scenario-weighted portfolio review;
- Monte Carlo uncertainty simulation;
- bootstrap stability analysis;
- random-weight sensitivity analysis;
- reproducible reports, plots, and audit-friendly outputs.

The workflow supports structured institutional deliberation. It does not
automate public decisions, ethical approval, legal review, budget decisions,
or community accountability.
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
    "change_readiness",
    "absorption_capacity",
    "public_value_priority",
    "burden_reduction",
    "governance_strength",
    "implementation_risk",
    "sequencing_need",
    "equity_priority",
    "data_readiness",
    "trust_gain",
]


@dataclass(frozen=True)
class EngineConfig:
    options_path: Path
    stakeholders_path: Path | None
    governance_path: Path | None
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
                    "change_readiness": 0.18,
                    "absorption_capacity": 0.16,
                    "public_value_priority": 0.18,
                    "burden_reduction": 0.11,
                    "governance_strength": 0.10,
                    "implementation_risk": 0.10,
                    "sequencing_need": 0.08,
                    "equity_priority": 0.04,
                    "data_readiness": 0.03,
                    "trust_gain": 0.02,
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


def validate_options(options: pd.DataFrame) -> List[ValidationIssue]:
    required = [
        "option",
        "option_type",
        "desirability",
        "authority",
        "capability",
        "funding",
        "policy_fit",
        "governance_strength",
        "trust_gain",
        "burden_reduction",
        "coordination_complexity",
        "implementation_risk",
        "data_readiness",
        "frontline_fit",
        "maintenance_capacity",
        "equity_priority",
        "public_value",
    ]
    issues: List[ValidationIssue] = []
    for col in required:
        if col not in options.columns:
            issues.append(ValidationIssue("error", col, "Missing institutional option column."))

    numeric_cols = [col for col in required if col not in ["option", "option_type"]]
    issues.extend(validate_range(options, numeric_cols, 1, 10))
    return issues


def score_options(options: pd.DataFrame) -> pd.DataFrame:
    df = options.copy()

    numeric_cols = [
        "desirability",
        "authority",
        "capability",
        "funding",
        "policy_fit",
        "governance_strength",
        "trust_gain",
        "burden_reduction",
        "coordination_complexity",
        "implementation_risk",
        "data_readiness",
        "frontline_fit",
        "maintenance_capacity",
        "equity_priority",
        "public_value",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["change_readiness"] = (
        0.14 * df["desirability"]
        + 0.13 * df["authority"]
        + 0.12 * df["capability"]
        + 0.10 * df["funding"]
        + 0.10 * df["policy_fit"]
        + 0.11 * df["governance_strength"]
        + 0.08 * df["trust_gain"]
        + 0.08 * df["burden_reduction"]
        + 0.06 * df["data_readiness"]
        + 0.05 * df["frontline_fit"]
        + 0.03 * df["maintenance_capacity"]
        - 0.05 * df["coordination_complexity"]
        - 0.05 * df["implementation_risk"]
    )

    df["absorption_capacity"] = (
        0.18 * df["authority"]
        + 0.18 * df["capability"]
        + 0.14 * df["funding"]
        + 0.14 * df["governance_strength"]
        + 0.12 * df["policy_fit"]
        + 0.10 * df["frontline_fit"]
        + 0.08 * df["maintenance_capacity"]
        + 0.06 * df["data_readiness"]
    )

    df["public_value_priority"] = (
        0.24 * df["public_value"]
        + 0.20 * df["burden_reduction"]
        + 0.18 * df["trust_gain"]
        + 0.16 * df["equity_priority"]
        + 0.12 * df["desirability"]
        + 0.10 * df["policy_fit"]
        - 0.08 * df["implementation_risk"]
    )

    df["sequencing_need"] = (
        0.28 * df["coordination_complexity"]
        + 0.24 * df["implementation_risk"]
        + 0.14 * (10.0 - df["authority"])
        + 0.12 * (10.0 - df["capability"])
        + 0.10 * (10.0 - df["funding"])
        + 0.07 * (10.0 - df["maintenance_capacity"])
        + 0.05 * (10.0 - df["data_readiness"])
    )

    df["governance_gap"] = (
        0.30 * (10.0 - df["governance_strength"])
        + 0.22 * (10.0 - df["authority"])
        + 0.18 * (10.0 - df["policy_fit"])
        + 0.16 * df["implementation_risk"]
        + 0.14 * df["coordination_complexity"]
    ) / 10.0

    df["portfolio_score"] = (
        0.30 * df["change_readiness"]
        + 0.26 * df["public_value_priority"]
        + 0.20 * df["absorption_capacity"]
        + 0.10 * df["equity_priority"]
        + 0.06 * df["trust_gain"]
        - 0.12 * df["sequencing_need"]
        - 0.08 * df["implementation_risk"]
    )

    df["recommended_action"] = np.select(
        [
            (df["change_readiness"] >= 7.1) & (df["absorption_capacity"] >= 6.6),
            (df["public_value_priority"] >= 7.4) & (df["absorption_capacity"] < 6.4),
            df["sequencing_need"] >= 7.2,
            df["implementation_risk"] >= 7.5,
            df["governance_gap"] >= 0.50,
        ],
        [
            "scale_with_governance",
            "prototype_then_build_capacity",
            "sequence_after_governance_and_capability_work",
            "risk_review_before_pilot",
            "governance_design_required",
        ],
        default="pilot_with_learning_metrics",
    )

    return df.sort_values("portfolio_score", ascending=False).reset_index(drop=True)


def score_stakeholder_burden(stakeholders: pd.DataFrame | None) -> pd.DataFrame:
    if stakeholders is None:
        return pd.DataFrame()

    required = [
        "stakeholder_group",
        "stakeholder_type",
        "time_burden",
        "cognitive_burden",
        "emotional_burden",
        "documentation_burden",
        "uncertainty_burden",
        "coordination_burden",
        "accessibility_need",
        "trust_gap",
        "affectedness",
        "voice",
        "influence",
        "repair_access",
    ]
    missing = [col for col in required if col not in stakeholders.columns]
    if missing:
        raise ValueError(f"Stakeholder burden file missing required columns: {missing}")

    df = stakeholders.copy()
    burden_cols = [
        "time_burden",
        "cognitive_burden",
        "emotional_burden",
        "documentation_burden",
        "uncertainty_burden",
        "coordination_burden",
        "trust_gap",
        "voice",
        "influence",
        "repair_access",
    ]

    for col in burden_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["accessibility_need", "affectedness"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["burden_score"] = (
        0.18 * df["time_burden"]
        + 0.20 * df["cognitive_burden"]
        + 0.17 * df["emotional_burden"]
        + 0.17 * df["documentation_burden"]
        + 0.16 * df["uncertainty_burden"]
        + 0.12 * df["coordination_burden"]
    )

    df["power_gap"] = 10.0 - (0.40 * df["voice"] + 0.36 * df["influence"] + 0.24 * df["repair_access"])
    df["accessibility_burden"] = df["accessibility_need"] * df["burden_score"]

    df["institutional_attention_priority"] = (
        0.26 * df["affectedness"] * df["burden_score"]
        + 0.22 * df["affectedness"] * df["power_gap"]
        + 0.16 * df["trust_gap"]
        + 0.14 * df["accessibility_burden"]
        + 0.12 * df["emotional_burden"]
        + 0.10 * df["uncertainty_burden"]
    )

    df["priority_action"] = np.select(
        [
            df["institutional_attention_priority"] >= 8.0,
            df["accessibility_burden"] >= 6.0,
            df["power_gap"] >= 5.5,
            df["burden_score"] >= 7.5,
        ],
        [
            "urgent_institutional_repair_review",
            "accessibility_and_assisted_access_review",
            "power_and_voice_review",
            "burden_reduction_required",
        ],
        default="monitor_with_disaggregated_evidence",
    )

    return df.sort_values("institutional_attention_priority", ascending=False).reset_index(drop=True)


def score_governance(governance: pd.DataFrame | None) -> pd.DataFrame:
    if governance is None:
        return pd.DataFrame()

    required = [
        "decision_domain",
        "owner",
        "approval_authority",
        "budget_authority",
        "policy_authority",
        "data_authority",
        "implementation_authority",
        "community_accountability",
        "escalation_clarity",
        "review_cadence",
        "maintenance_ownership",
    ]
    missing = [col for col in required if col not in governance.columns]
    if missing:
        raise ValueError(f"Governance decision-rights file missing required columns: {missing}")

    df = governance.copy()
    numeric_cols = [col for col in required if col not in ["decision_domain", "owner"]]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["decision_rights_strength"] = (
        0.16 * df["approval_authority"]
        + 0.13 * df["budget_authority"]
        + 0.13 * df["policy_authority"]
        + 0.12 * df["data_authority"]
        + 0.15 * df["implementation_authority"]
        + 0.10 * df["community_accountability"]
        + 0.08 * df["escalation_clarity"]
        + 0.07 * df["review_cadence"]
        + 0.06 * df["maintenance_ownership"]
    )

    df["governance_gap"] = 1.0 - df["decision_rights_strength"]
    df["governance_action"] = np.select(
        [
            df["decision_rights_strength"] < 0.50,
            df["community_accountability"] < 0.45,
            df["maintenance_ownership"] < 0.50,
            df["escalation_clarity"] < 0.50,
        ],
        [
            "clarify_decision_rights_before_design_work",
            "increase_community_accountability",
            "assign_maintenance_ownership",
            "clarify_escalation_path",
        ],
        default="governance_ready_with_monitoring",
    )

    return df.sort_values("governance_gap", ascending=False).reset_index(drop=True)


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "risk_id",
        "option",
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
        raise ValueError(f"Institutional risk register missing required columns: {missing}")

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
            "pause_until_governance_and_mitigation_plan",
            "executive_and_ethics_review_required",
            "repair_pathway_required_before_pilot",
        ],
        default="monitor_with_named_owner",
    )

    return df.sort_values("risk_priority_number", ascending=False).reset_index(drop=True)


def run_scenario_review(option_scores: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    rows: List[dict] = []

    for _, scenario in weights.iterrows():
        for _, option in option_scores.iterrows():
            priority = (
                scenario["change_readiness"] * option["change_readiness"] / 10.0
                + scenario["absorption_capacity"] * option["absorption_capacity"] / 10.0
                + scenario["public_value_priority"] * option["public_value_priority"] / 10.0
                + scenario["burden_reduction"] * option["burden_reduction"] / 10.0
                + scenario["governance_strength"] * option["governance_strength"] / 10.0
                + scenario["implementation_risk"] * (10.0 - option["implementation_risk"]) / 10.0
                + scenario["sequencing_need"] * (10.0 - option["sequencing_need"]) / 10.0
                + scenario["equity_priority"] * option["equity_priority"] / 10.0
                + scenario["data_readiness"] * option["data_readiness"] / 10.0
                + scenario["trust_gain"] * option["trust_gain"] / 10.0
            )

            rows.append(
                {
                    "scenario": scenario["scenario"],
                    "option": option["option"],
                    "option_type": option["option_type"],
                    "scenario_priority_score": float(priority),
                    "change_readiness": float(option["change_readiness"]),
                    "absorption_capacity": float(option["absorption_capacity"]),
                    "public_value_priority": float(option["public_value_priority"]),
                    "sequencing_need": float(option["sequencing_need"]),
                    "recommended_action": option["recommended_action"],
                }
            )

    result = pd.DataFrame(rows)
    result["scenario_rank"] = (
        result.groupby("scenario")["scenario_priority_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    return result.sort_values(["scenario", "scenario_rank", "option"]).reset_index(drop=True)


def monte_carlo_portfolio_stability(
    options: pd.DataFrame,
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    top_counts: Counter[str] = Counter()
    records: List[dict] = []

    score_cols = [
        "desirability",
        "authority",
        "capability",
        "funding",
        "policy_fit",
        "governance_strength",
        "trust_gain",
        "burden_reduction",
        "coordination_complexity",
        "implementation_risk",
        "data_readiness",
        "frontline_fit",
        "maintenance_capacity",
        "equity_priority",
        "public_value",
    ]

    for simulation_id in range(simulations):
        simulated = options.copy()

        for col in score_cols:
            simulated[col] = rng.normal(
                loc=options[col].to_numpy(dtype=float),
                scale=score_sd,
            ).clip(1.0, 10.0)

        scored = score_options(simulated)
        top_counts[str(scored.iloc[0]["option"])] += 1

        for rank, (_, row) in enumerate(scored.iterrows(), start=1):
            records.append(
                {
                    "simulation_id": simulation_id,
                    "option": row["option"],
                    "option_type": row["option_type"],
                    "change_readiness": float(row["change_readiness"]),
                    "absorption_capacity": float(row["absorption_capacity"]),
                    "public_value_priority": float(row["public_value_priority"]),
                    "sequencing_need": float(row["sequencing_need"]),
                    "portfolio_score": float(row["portfolio_score"]),
                    "rank": rank,
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "option": option,
                    "times_top_portfolio_option": count,
                    "probability_top_portfolio_option": count / simulations,
                }
                for option, count in top_counts.items()
            ]
        )
        .sort_values("probability_top_portfolio_option", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_option_stability(options: pd.DataFrame, iterations: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = options.sample(
            n=len(options),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_options(sampled)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "option": row["option"],
                    "change_readiness": float(row["change_readiness"]),
                    "absorption_capacity": float(row["absorption_capacity"]),
                    "public_value_priority": float(row["public_value_priority"]),
                    "sequencing_need": float(row["sequencing_need"]),
                    "portfolio_score": float(row["portfolio_score"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("option")
        .agg(
            mean_change_readiness=("change_readiness", "mean"),
            mean_absorption_capacity=("absorption_capacity", "mean"),
            mean_public_value_priority=("public_value_priority", "mean"),
            mean_sequencing_need=("sequencing_need", "mean"),
            mean_portfolio_score=("portfolio_score", "mean"),
            sd_portfolio_score=("portfolio_score", "std"),
        )
        .reset_index()
        .sort_values("mean_portfolio_score", ascending=False)
    )


def random_weight_sensitivity(option_scores: pd.DataFrame, samples: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()

    for _ in range(samples):
        weights = dict(zip(SCENARIO_CRITERIA, rng.dirichlet(np.ones(len(SCENARIO_CRITERIA)))))
        values = []
        for _, option in option_scores.iterrows():
            score = (
                weights["change_readiness"] * option["change_readiness"] / 10.0
                + weights["absorption_capacity"] * option["absorption_capacity"] / 10.0
                + weights["public_value_priority"] * option["public_value_priority"] / 10.0
                + weights["burden_reduction"] * option["burden_reduction"] / 10.0
                + weights["governance_strength"] * option["governance_strength"] / 10.0
                + weights["implementation_risk"] * (10.0 - option["implementation_risk"]) / 10.0
                + weights["sequencing_need"] * (10.0 - option["sequencing_need"]) / 10.0
                + weights["equity_priority"] * option["equity_priority"] / 10.0
                + weights["data_readiness"] * option["data_readiness"] / 10.0
                + weights["trust_gain"] * option["trust_gain"] / 10.0
            )
            values.append((option["option"], score))

        winner_counts[max(values, key=lambda item: item[1])[0]] += 1

    return (
        pd.DataFrame(
            [
                {
                    "option": option,
                    "times_top_under_random_weights": count,
                    "probability_top_under_random_weights": count / samples,
                }
                for option, count in winner_counts.items()
            ]
        )
        .sort_values("probability_top_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_portfolio_plot(scores: pd.DataFrame, output_path: Path) -> None:
    plot_df = scores.sort_values("portfolio_score", ascending=True)
    plt.figure(figsize=(12, 7))
    plt.barh(plot_df["option"], plot_df["portfolio_score"])
    plt.title("Institutional Design Portfolio Score")
    plt.xlabel("Portfolio score")
    plt.ylabel("Institutional design option")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_absorption_public_value_plot(scores: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(11, 7))
    sizes = np.clip(scores["burden_reduction"].to_numpy(dtype=float), 1, 10) * 42
    plt.scatter(scores["absorption_capacity"], scores["public_value_priority"], s=sizes)
    for _, row in scores.iterrows():
        plt.annotate(row["option"], (row["absorption_capacity"], row["public_value_priority"]), fontsize=8)
    plt.title("Institutional Absorption Capacity vs Public Value Priority")
    plt.xlabel("Absorption capacity")
    plt.ylabel("Public value priority")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_monte_carlo_plot(winners: pd.DataFrame, output_path: Path) -> None:
    if winners.empty:
        return
    plot_df = winners.copy()
    plot_df["probability_pct"] = plot_df["probability_top_portfolio_option"] * 100.0
    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["option"], plot_df["probability_pct"])
    plt.title("Probability of Top Institutional Portfolio Option")
    plt.ylabel("Probability (%)")
    plt.xlabel("Option")
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
    option_scores: pd.DataFrame,
    stakeholder_scores: pd.DataFrame,
    governance_scores: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top_option = option_scores.iloc[0]["option"] if not option_scores.empty else "Not available"

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    stakeholder_section = "No stakeholder burden data provided."
    if not stakeholder_scores.empty:
        stakeholder_section = dataframe_to_markdown_safe(stakeholder_scores)

    governance_section = "No governance decision-rights data provided."
    if not governance_scores.empty:
        governance_section = dataframe_to_markdown_safe(governance_scores)

    risk_section = "No institutional risk register provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Design Thinking for Complex Institutions Report

## Summary

This report evaluates institutional design options using change readiness, absorption capacity, public value, governance strength, burden reduction, equity priority, trust gain, data readiness, coordination complexity, implementation risk, stakeholder burden, decision rights, and uncertainty.

## Highest portfolio-scoring option

- Option: **{top_option}**

## Validation notes

{issue_lines}

## Institutional design option scores

{dataframe_to_markdown_safe(option_scores)}

## Stakeholder burden and institutional attention priority

{stakeholder_section}

## Governance decision-rights review

{governance_section}

## Scenario-weighted portfolio review

{dataframe_to_markdown_safe(scenario_results.head(80))}

## Monte Carlo portfolio stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap option stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Institutional risk-register priority

{risk_section}

## Responsible interpretation

These outputs support institutional deliberation. They do not replace public accountability, community participation, legal review, budget authority, ethical review, frontline validation, or executive decision-making.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional institutional design-thinking analysis engine.")
    parser.add_argument("--options", type=Path, default=Path("../data/raw/institutional_design_options_raw.csv"))
    parser.add_argument("--stakeholders", type=Path, default=Path("../data/raw/stakeholder_burden_raw.csv"))
    parser.add_argument("--governance", type=Path, default=Path("../data/raw/governance_decision_rights_raw.csv"))
    parser.add_argument("--weights", type=Path, default=Path("../data/raw/institutional_scenario_weights.csv"))
    parser.add_argument("--risk-register", type=Path, default=Path("../data/raw/institutional_risk_register_raw.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.55)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        options_path=args.options,
        stakeholders_path=args.stakeholders if args.stakeholders.exists() else None,
        governance_path=args.governance if args.governance.exists() else None,
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

    options_raw = read_required_csv(config.options_path, "Institutional design options")
    stakeholders_raw = read_optional_csv(config.stakeholders_path)
    governance_raw = read_optional_csv(config.governance_path)
    weights = read_weights(config.weights_path)
    risk_register_raw = read_optional_csv(config.risk_register_path)

    issues = validate_options(options_raw)
    fatal = [issue for issue in issues if issue.level == "error"]
    if fatal:
        for issue in fatal:
            print(f"ERROR [{issue.field}]: {issue.message}", file=sys.stderr)
        return 2

    option_scores = score_options(options_raw)
    stakeholder_scores = score_stakeholder_burden(stakeholders_raw)
    governance_scores = score_governance(governance_raw)
    risk_summary = analyze_risk_register(risk_register_raw)
    scenario_results = run_scenario_review(option_scores, weights)

    winners, simulation_records = monte_carlo_portfolio_stability(
        options=options_raw,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    simulation_summary = (
        simulation_records.groupby("option")
        .agg(
            mean_change_readiness=("change_readiness", "mean"),
            mean_absorption_capacity=("absorption_capacity", "mean"),
            mean_public_value_priority=("public_value_priority", "mean"),
            mean_sequencing_need=("sequencing_need", "mean"),
            mean_portfolio_score=("portfolio_score", "mean"),
            sd_portfolio_score=("portfolio_score", "std"),
            median_rank=("rank", "median"),
            p90_rank=("rank", lambda x: float(np.quantile(x, 0.90))),
        )
        .reset_index()
        .sort_values("mean_portfolio_score", ascending=False)
    )

    bootstrap = bootstrap_option_stability(
        options=options_raw,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        option_scores=option_scores,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    option_scores.to_csv(config.output_dir / "institutional_design_option_scores.csv", index=False)
    stakeholder_scores.to_csv(config.output_dir / "stakeholder_burden_attention_scores.csv", index=False)
    governance_scores.to_csv(config.output_dir / "governance_decision_rights_scores.csv", index=False)
    scenario_results.to_csv(config.output_dir / "institutional_scenario_review_results.csv", index=False)
    winners.to_csv(config.output_dir / "institutional_portfolio_monte_carlo_winners.csv", index=False)
    simulation_records.to_csv(config.output_dir / "institutional_portfolio_simulation_records.csv", index=False)
    simulation_summary.to_csv(config.output_dir / "institutional_portfolio_simulation_summary.csv", index=False)
    bootstrap.to_csv(config.output_dir / "institutional_option_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "institutional_random_weight_sensitivity.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "institutional_risk_priority.csv", index=False)

    save_portfolio_plot(option_scores, config.output_dir / "institutional_design_portfolio_score.png")
    save_absorption_public_value_plot(option_scores, config.output_dir / "absorption_capacity_public_value.png")
    save_monte_carlo_plot(winners, config.output_dir / "institutional_portfolio_monte_carlo_winners.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "options_path": str(config.options_path),
                "stakeholders_path": str(config.stakeholders_path) if config.stakeholders_path else None,
                "governance_path": str(config.governance_path) if config.governance_path else None,
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "scenario_criteria": SCENARIO_CRITERIA,
            "readiness_model": "weighted desirability, authority, capability, funding, policy fit, governance, trust, burden reduction, data readiness, frontline fit, maintenance, less coordination complexity and implementation risk",
            "absorption_model": "weighted authority, capability, funding, governance, policy fit, frontline fit, maintenance capacity, and data readiness",
            "burden_model": "weighted time, cognitive, emotional, documentation, uncertainty, and coordination burden",
        },
    )

    report = build_report(
        option_scores=option_scores,
        stakeholder_scores=stakeholder_scores,
        governance_scores=governance_scores,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "institutional_design_report.md").write_text(report, encoding="utf-8")

    print("Institutional design analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- institutional_design_option_scores.csv")
    print("- stakeholder_burden_attention_scores.csv")
    print("- governance_decision_rights_scores.csv")
    print("- institutional_scenario_review_results.csv")
    print("- institutional_portfolio_monte_carlo_winners.csv")
    print("- institutional_risk_priority.csv")
    print("- institutional_design_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
