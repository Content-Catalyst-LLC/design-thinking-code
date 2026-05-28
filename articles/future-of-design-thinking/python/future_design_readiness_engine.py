#!/usr/bin/env python3
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
    "future_design_readiness",
    "public_value",
    "ethical_maturity",
    "systems_literacy",
    "evidence_quality",
    "ai_governance",
    "implementation_capacity",
    "stewardship_capacity",
    "climate_responsibility",
    "participation_quality",
    "unmanaged_risk",
]


@dataclass(frozen=True)
class EngineConfig:
    initiatives_path: Path
    ai_governance_path: Path | None
    stewardship_path: Path | None
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
                    "future_design_readiness": 0.17,
                    "public_value": 0.14,
                    "ethical_maturity": 0.11,
                    "systems_literacy": 0.11,
                    "evidence_quality": 0.10,
                    "ai_governance": 0.09,
                    "implementation_capacity": 0.09,
                    "stewardship_capacity": 0.08,
                    "climate_responsibility": 0.04,
                    "participation_quality": 0.04,
                    "unmanaged_risk": 0.03,
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
            issues.append(ValidationIssue("error", col, f"Column must be numeric in [{low}, {high}]."))
    return issues


def validate_initiatives(initiatives: pd.DataFrame) -> List[ValidationIssue]:
    required = [
        "initiative",
        "initiative_type",
        "human_centered_quality",
        "systems_literacy",
        "evidence_quality",
        "ethical_maturity",
        "ai_governance",
        "implementation_capacity",
        "public_value",
        "stewardship_capacity",
        "unmanaged_risk",
        "participation_quality",
        "organizational_learning",
        "data_infrastructure",
        "climate_responsibility",
        "burden_awareness",
    ]

    issues: List[ValidationIssue] = []
    for col in required:
        if col not in initiatives.columns:
            issues.append(ValidationIssue("error", col, "Missing future design initiative column."))

    numeric_cols = [col for col in required if col not in ["initiative", "initiative_type"]]
    issues.extend(validate_range(initiatives, numeric_cols, 1, 10))
    return issues


def score_initiatives(initiatives: pd.DataFrame) -> pd.DataFrame:
    df = initiatives.copy()

    numeric_cols = [
        "human_centered_quality",
        "systems_literacy",
        "evidence_quality",
        "ethical_maturity",
        "ai_governance",
        "implementation_capacity",
        "public_value",
        "stewardship_capacity",
        "unmanaged_risk",
        "participation_quality",
        "organizational_learning",
        "data_infrastructure",
        "climate_responsibility",
        "burden_awareness",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["future_design_readiness"] = (
        0.11 * df["human_centered_quality"]
        + 0.12 * df["systems_literacy"]
        + 0.12 * df["evidence_quality"]
        + 0.12 * df["ethical_maturity"]
        + 0.10 * df["ai_governance"]
        + 0.10 * df["implementation_capacity"]
        + 0.12 * df["public_value"]
        + 0.09 * df["stewardship_capacity"]
        + 0.06 * df["participation_quality"]
        + 0.06 * df["organizational_learning"]
        + 0.04 * df["data_infrastructure"]
        + 0.04 * df["climate_responsibility"]
        + 0.04 * df["burden_awareness"]
        - 0.10 * df["unmanaged_risk"]
    )

    df["stewardship_need"] = (
        0.26 * df["unmanaged_risk"]
        + 0.17 * (10.0 - df["stewardship_capacity"])
        + 0.15 * (10.0 - df["implementation_capacity"])
        + 0.12 * (10.0 - df["ethical_maturity"])
        + 0.10 * (10.0 - df["evidence_quality"])
        + 0.08 * (10.0 - df["systems_literacy"])
        + 0.07 * (10.0 - df["organizational_learning"])
        + 0.05 * (10.0 - df["burden_awareness"])
    )

    df["ai_design_maturity"] = (
        0.28 * df["ai_governance"]
        + 0.18 * df["evidence_quality"]
        + 0.16 * df["data_infrastructure"]
        + 0.14 * df["ethical_maturity"]
        + 0.12 * df["human_centered_quality"]
        + 0.12 * df["organizational_learning"]
        - 0.10 * df["unmanaged_risk"]
    )

    df["systems_public_value_priority"] = (
        0.26 * df["public_value"]
        + 0.18 * df["systems_literacy"]
        + 0.16 * df["ethical_maturity"]
        + 0.14 * df["participation_quality"]
        + 0.12 * df["burden_awareness"]
        + 0.08 * df["climate_responsibility"]
        + 0.06 * df["human_centered_quality"]
    )

    df["portfolio_priority"] = (
        0.36 * df["future_design_readiness"]
        + 0.20 * df["public_value"]
        + 0.14 * df["ethical_maturity"]
        + 0.10 * df["systems_literacy"]
        + 0.08 * df["evidence_quality"]
        + 0.06 * df["participation_quality"]
        - 0.10 * df["stewardship_need"]
        - 0.06 * df["unmanaged_risk"]
    )

    df["recommended_action"] = np.select(
        [
            (df["future_design_readiness"] >= 7.8) & (df["stewardship_need"] <= 4.6),
            (df["future_design_readiness"] >= 7.8) & (df["stewardship_need"] > 4.6),
            (df["ai_governance"] < 7.0) & df["initiative"].str.contains("AI", case=False),
            df["ethical_maturity"] < 7.5,
            df["implementation_capacity"] < 6.8,
            df["unmanaged_risk"] >= 7.0,
            df["participation_quality"] < 7.0,
        ],
        [
            "advance_with_governed_pilot",
            "strengthen_stewardship_before_scale",
            "ai_governance_required_before_pilot",
            "ethics_and_power_review_required",
            "build_absorption_capacity",
            "risk_review_before_pilot",
            "strengthen_participation_and_power_sharing",
        ],
        default="develop_with_learning_metrics",
    )

    return df.sort_values("portfolio_priority", ascending=False).reset_index(drop=True)


def score_ai_governance(ai_governance: pd.DataFrame | None) -> pd.DataFrame:
    if ai_governance is None:
        return pd.DataFrame()

    required = [
        "ai_use_case",
        "governance",
        "validation",
        "data_quality",
        "provenance",
        "human_oversight",
        "uncertainty_management",
        "bias_review",
        "privacy_review",
        "appeal_pathway",
        "source_traceability",
        "model_monitoring",
    ]
    missing = [col for col in required if col not in ai_governance.columns]
    if missing:
        raise ValueError(f"AI governance file missing required columns: {missing}")

    df = ai_governance.copy()
    for col in required:
        if col != "ai_use_case":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["ai_governance_maturity"] = (
        0.13 * df["governance"]
        + 0.13 * df["validation"]
        + 0.11 * df["data_quality"]
        + 0.12 * df["provenance"]
        + 0.12 * df["human_oversight"]
        + 0.10 * df["uncertainty_management"]
        + 0.10 * df["bias_review"]
        + 0.08 * df["privacy_review"]
        + 0.06 * df["appeal_pathway"]
        + 0.08 * df["source_traceability"]
        + 0.07 * df["model_monitoring"]
    )

    df["ai_governance_gap"] = 10.0 - df["ai_governance_maturity"]

    df["ai_action"] = np.select(
        [
            df["ai_governance_maturity"] < 6.5,
            df["appeal_pathway"] < 6.5,
            df["bias_review"] < 7.0,
            df["source_traceability"] < 7.0,
            df["human_oversight"] < 7.0,
        ],
        [
            "do_not_pilot_until_governance_strengthened",
            "appeal_and_repair_pathway_required",
            "bias_review_required",
            "source_traceability_required",
            "human_oversight_required",
        ],
        default="governed_ai_use_with_monitoring",
    )

    return df.sort_values("ai_governance_gap", ascending=False).reset_index(drop=True)


def score_stewardship(stewardship: pd.DataFrame | None) -> pd.DataFrame:
    if stewardship is None:
        return pd.DataFrame()

    required = [
        "initiative",
        "ownership",
        "funding",
        "maintenance",
        "learning_routines",
        "repair_pathways",
        "evaluation_cadence",
        "public_reporting",
        "community_accountability",
        "sunset_criteria",
        "implementation_owner",
    ]
    missing = [col for col in required if col not in stewardship.columns]
    if missing:
        raise ValueError(f"Stewardship file missing required columns: {missing}")

    df = stewardship.copy()
    numeric_cols = [col for col in required if col not in ["initiative", "implementation_owner"]]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["stewardship_readiness"] = (
        0.15 * df["ownership"]
        + 0.12 * df["funding"]
        + 0.13 * df["maintenance"]
        + 0.13 * df["learning_routines"]
        + 0.13 * df["repair_pathways"]
        + 0.10 * df["evaluation_cadence"]
        + 0.08 * df["public_reporting"]
        + 0.10 * df["community_accountability"]
        + 0.06 * df["sunset_criteria"]
    )

    df["stewardship_gap"] = 1.0 - df["stewardship_readiness"]

    df["stewardship_action"] = np.select(
        [
            df["stewardship_readiness"] < 0.65,
            df["repair_pathways"] < 0.65,
            df["community_accountability"] < 0.65,
            df["funding"] < 0.65,
            df["sunset_criteria"] < 0.65,
        ],
        [
            "strengthen_stewardship_before_launch",
            "repair_pathway_required",
            "community_accountability_required",
            "funding_pathway_required",
            "sunset_criteria_required",
        ],
        default="stewardship_ready_with_monitoring",
    )

    return df.sort_values("stewardship_gap", ascending=False).reset_index(drop=True)


def analyze_risk_register(risk_register: pd.DataFrame | None) -> pd.DataFrame:
    if risk_register is None:
        return pd.DataFrame()

    required = [
        "risk_id",
        "initiative",
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
        raise ValueError(f"Future design risk register missing required columns: {missing}")

    df = risk_register.copy()
    for col in ["severity", "likelihood", "detectability", "repair_difficulty"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["risk_priority_number"] = df["severity"] * df["likelihood"] * df["detectability"] * df["repair_difficulty"]
    df["normalized_risk_priority"] = df["risk_priority_number"] / df["risk_priority_number"].max()

    df["risk_action"] = np.select(
        [
            df["risk_priority_number"] >= 300,
            df["severity"] >= 5,
            df["repair_difficulty"] >= 5,
        ],
        [
            "pause_until_governance_and_stewardship_plan",
            "ethics_and_governance_review_required",
            "repair_pathway_required_before_pilot",
        ],
        default="monitor_with_named_owner",
    )

    return df.sort_values("risk_priority_number", ascending=False).reset_index(drop=True)


def run_scenario_review(scores: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    rows: List[dict] = []

    for _, scenario in weights.iterrows():
        for _, item in scores.iterrows():
            priority = (
                scenario["future_design_readiness"] * item["future_design_readiness"] / 10.0
                + scenario["public_value"] * item["public_value"] / 10.0
                + scenario["ethical_maturity"] * item["ethical_maturity"] / 10.0
                + scenario["systems_literacy"] * item["systems_literacy"] / 10.0
                + scenario["evidence_quality"] * item["evidence_quality"] / 10.0
                + scenario["ai_governance"] * item["ai_governance"] / 10.0
                + scenario["implementation_capacity"] * item["implementation_capacity"] / 10.0
                + scenario["stewardship_capacity"] * item["stewardship_capacity"] / 10.0
                + scenario["climate_responsibility"] * item["climate_responsibility"] / 10.0
                + scenario["participation_quality"] * item["participation_quality"] / 10.0
                + scenario["unmanaged_risk"] * (10.0 - item["unmanaged_risk"]) / 10.0
            )

            rows.append(
                {
                    "scenario": scenario["scenario"],
                    "initiative": item["initiative"],
                    "initiative_type": item["initiative_type"],
                    "scenario_priority_score": float(priority),
                    "future_design_readiness": float(item["future_design_readiness"]),
                    "stewardship_need": float(item["stewardship_need"]),
                    "portfolio_priority": float(item["portfolio_priority"]),
                    "recommended_action": item["recommended_action"],
                }
            )

    result = pd.DataFrame(rows)
    result["scenario_rank"] = (
        result.groupby("scenario")["scenario_priority_score"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    return result.sort_values(["scenario", "scenario_rank", "initiative"]).reset_index(drop=True)


def monte_carlo_stability(
    initiatives: pd.DataFrame,
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    top_counts: Counter[str] = Counter()
    records: List[dict] = []

    score_cols = [
        "human_centered_quality",
        "systems_literacy",
        "evidence_quality",
        "ethical_maturity",
        "ai_governance",
        "implementation_capacity",
        "public_value",
        "stewardship_capacity",
        "unmanaged_risk",
        "participation_quality",
        "organizational_learning",
        "data_infrastructure",
        "climate_responsibility",
        "burden_awareness",
    ]

    for simulation_id in range(simulations):
        simulated = initiatives.copy()

        for col in score_cols:
            simulated[col] = rng.normal(
                loc=initiatives[col].to_numpy(dtype=float),
                scale=score_sd,
            ).clip(1.0, 10.0)

        scored = score_initiatives(simulated)
        top_counts[str(scored.iloc[0]["initiative"])] += 1

        for rank, (_, row) in enumerate(scored.iterrows(), start=1):
            records.append(
                {
                    "simulation_id": simulation_id,
                    "initiative": row["initiative"],
                    "initiative_type": row["initiative_type"],
                    "future_design_readiness": float(row["future_design_readiness"]),
                    "stewardship_need": float(row["stewardship_need"]),
                    "ai_design_maturity": float(row["ai_design_maturity"]),
                    "portfolio_priority": float(row["portfolio_priority"]),
                    "rank": rank,
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "initiative": initiative,
                    "times_top_initiative": count,
                    "probability_top_initiative": count / simulations,
                }
                for initiative, count in top_counts.items()
            ]
        )
        .sort_values("probability_top_initiative", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_stability(initiatives: pd.DataFrame, iterations: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = initiatives.sample(
            n=len(initiatives),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_initiatives(sampled)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "initiative": row["initiative"],
                    "future_design_readiness": float(row["future_design_readiness"]),
                    "stewardship_need": float(row["stewardship_need"]),
                    "portfolio_priority": float(row["portfolio_priority"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("initiative")
        .agg(
            mean_future_design_readiness=("future_design_readiness", "mean"),
            mean_stewardship_need=("stewardship_need", "mean"),
            mean_portfolio_priority=("portfolio_priority", "mean"),
            sd_portfolio_priority=("portfolio_priority", "std"),
        )
        .reset_index()
        .sort_values("mean_portfolio_priority", ascending=False)
    )


def random_weight_sensitivity(scores: pd.DataFrame, samples: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()

    for _ in range(samples):
        weights = dict(zip(SCENARIO_CRITERIA, rng.dirichlet(np.ones(len(SCENARIO_CRITERIA)))))
        values = []
        for _, item in scores.iterrows():
            score = (
                weights["future_design_readiness"] * item["future_design_readiness"] / 10.0
                + weights["public_value"] * item["public_value"] / 10.0
                + weights["ethical_maturity"] * item["ethical_maturity"] / 10.0
                + weights["systems_literacy"] * item["systems_literacy"] / 10.0
                + weights["evidence_quality"] * item["evidence_quality"] / 10.0
                + weights["ai_governance"] * item["ai_governance"] / 10.0
                + weights["implementation_capacity"] * item["implementation_capacity"] / 10.0
                + weights["stewardship_capacity"] * item["stewardship_capacity"] / 10.0
                + weights["climate_responsibility"] * item["climate_responsibility"] / 10.0
                + weights["participation_quality"] * item["participation_quality"] / 10.0
                + weights["unmanaged_risk"] * (10.0 - item["unmanaged_risk"]) / 10.0
            )
            values.append((item["initiative"], score))

        winner_counts[max(values, key=lambda item: item[1])[0]] += 1

    return (
        pd.DataFrame(
            [
                {
                    "initiative": initiative,
                    "times_top_under_random_weights": count,
                    "probability_top_under_random_weights": count / samples,
                }
                for initiative, count in winner_counts.items()
            ]
        )
        .sort_values("probability_top_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_portfolio_plot(scores: pd.DataFrame, output_path: Path) -> None:
    plot_df = scores.sort_values("portfolio_priority", ascending=True)
    plt.figure(figsize=(12, 7))
    plt.barh(plot_df["initiative"], plot_df["portfolio_priority"])
    plt.title("Future Design-Thinking Portfolio Priority")
    plt.xlabel("Portfolio priority")
    plt.ylabel("Initiative")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_readiness_stewardship_plot(scores: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(11, 7))
    sizes = np.clip(scores["public_value"].to_numpy(dtype=float), 1, 10) * 42
    plt.scatter(scores["stewardship_need"], scores["future_design_readiness"], s=sizes)
    for _, row in scores.iterrows():
        plt.annotate(row["initiative"], (row["stewardship_need"], row["future_design_readiness"]), fontsize=8)
    plt.title("Future Design Readiness vs Stewardship Need")
    plt.xlabel("Stewardship need")
    plt.ylabel("Future design readiness")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_monte_carlo_plot(winners: pd.DataFrame, output_path: Path) -> None:
    if winners.empty:
        return
    plot_df = winners.copy()
    plot_df["probability_pct"] = plot_df["probability_top_initiative"] * 100.0
    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["initiative"], plot_df["probability_pct"])
    plt.title("Probability of Top Future Design Initiative")
    plt.ylabel("Probability (%)")
    plt.xlabel("Initiative")
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
    initiative_scores: pd.DataFrame,
    ai_scores: pd.DataFrame,
    stewardship_scores: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top_initiative = initiative_scores.iloc[0]["initiative"] if not initiative_scores.empty else "Not available"

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    ai_section = dataframe_to_markdown_safe(ai_scores) if not ai_scores.empty else "No AI governance data provided."
    stewardship_section = dataframe_to_markdown_safe(stewardship_scores) if not stewardship_scores.empty else "No stewardship-readiness data provided."
    risk_section = dataframe_to_markdown_safe(risk_summary) if not risk_summary.empty else "No future design risk register provided."

    return f"""# The Future of Design Thinking Report

## Summary

This report evaluates future design-thinking initiatives using future design readiness, public value, systems literacy, evidence quality, ethical maturity, AI governance, implementation capacity, stewardship capacity, participation quality, climate responsibility, burden awareness, and unmanaged risk.

## Highest portfolio-priority initiative

- Initiative: **{top_initiative}**

## Validation notes

{issue_lines}

## Future design initiative scores

{dataframe_to_markdown_safe(initiative_scores)}

## AI governance maturity

{ai_section}

## Stewardship readiness

{stewardship_section}

## Scenario-weighted review

{dataframe_to_markdown_safe(scenario_results.head(90))}

## Monte Carlo portfolio stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap portfolio stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Risk-register priority

{risk_section}

## Responsible interpretation

These outputs support strategic deliberation. They do not replace ethics review, public accountability, AI governance, community participation, legal review, funding decisions, or institutional stewardship.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional future design-thinking readiness analysis engine.")
    parser.add_argument("--initiatives", type=Path, default=Path("../data/raw/future_design_initiatives_raw.csv"))
    parser.add_argument("--ai-governance", type=Path, default=Path("../data/raw/ai_governance_maturity_raw.csv"))
    parser.add_argument("--stewardship", type=Path, default=Path("../data/raw/stewardship_readiness_raw.csv"))
    parser.add_argument("--weights", type=Path, default=Path("../data/raw/future_design_scenario_weights.csv"))
    parser.add_argument("--risk-register", type=Path, default=Path("../data/raw/future_design_risk_register_raw.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.55)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        initiatives_path=args.initiatives,
        ai_governance_path=args.ai_governance if args.ai_governance.exists() else None,
        stewardship_path=args.stewardship if args.stewardship.exists() else None,
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

    initiatives_raw = read_required_csv(config.initiatives_path, "Future design initiatives")
    ai_governance_raw = read_optional_csv(config.ai_governance_path)
    stewardship_raw = read_optional_csv(config.stewardship_path)
    weights = read_weights(config.weights_path)
    risk_register_raw = read_optional_csv(config.risk_register_path)

    issues = validate_initiatives(initiatives_raw)
    fatal = [issue for issue in issues if issue.level == "error"]
    if fatal:
        for issue in fatal:
            print(f"ERROR [{issue.field}]: {issue.message}", file=sys.stderr)
        return 2

    initiative_scores = score_initiatives(initiatives_raw)
    ai_scores = score_ai_governance(ai_governance_raw)
    stewardship_scores = score_stewardship(stewardship_raw)
    risk_summary = analyze_risk_register(risk_register_raw)
    scenario_results = run_scenario_review(initiative_scores, weights)

    winners, simulation_records = monte_carlo_stability(
        initiatives=initiatives_raw,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    simulation_summary = (
        simulation_records.groupby("initiative")
        .agg(
            mean_future_design_readiness=("future_design_readiness", "mean"),
            mean_stewardship_need=("stewardship_need", "mean"),
            mean_ai_design_maturity=("ai_design_maturity", "mean"),
            mean_portfolio_priority=("portfolio_priority", "mean"),
            sd_portfolio_priority=("portfolio_priority", "std"),
            median_rank=("rank", "median"),
            p90_rank=("rank", lambda x: float(np.quantile(x, 0.90))),
        )
        .reset_index()
        .sort_values("mean_portfolio_priority", ascending=False)
    )

    bootstrap = bootstrap_stability(
        initiatives=initiatives_raw,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        scores=initiative_scores,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    initiative_scores.to_csv(config.output_dir / "future_design_initiative_scores.csv", index=False)
    ai_scores.to_csv(config.output_dir / "ai_governance_maturity_scores.csv", index=False)
    stewardship_scores.to_csv(config.output_dir / "stewardship_readiness_scores.csv", index=False)
    scenario_results.to_csv(config.output_dir / "future_design_scenario_review_results.csv", index=False)
    winners.to_csv(config.output_dir / "future_design_monte_carlo_winners.csv", index=False)
    simulation_records.to_csv(config.output_dir / "future_design_simulation_records.csv", index=False)
    simulation_summary.to_csv(config.output_dir / "future_design_simulation_summary.csv", index=False)
    bootstrap.to_csv(config.output_dir / "future_design_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "future_design_random_weight_sensitivity.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "future_design_risk_priority.csv", index=False)

    save_portfolio_plot(initiative_scores, config.output_dir / "future_design_portfolio_priority.png")
    save_readiness_stewardship_plot(initiative_scores, config.output_dir / "future_design_readiness_stewardship_need.png")
    save_monte_carlo_plot(winners, config.output_dir / "future_design_monte_carlo_winners.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "initiatives_path": str(config.initiatives_path),
                "ai_governance_path": str(config.ai_governance_path) if config.ai_governance_path else None,
                "stewardship_path": str(config.stewardship_path) if config.stewardship_path else None,
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "scenario_criteria": SCENARIO_CRITERIA,
            "future_design_readiness_model": "weighted human-centered quality, systems literacy, evidence quality, ethics, AI governance, implementation, public value, stewardship, participation, learning, data infrastructure, climate responsibility, and burden awareness, less unmanaged risk",
            "ai_maturity_model": "governance, validation, data quality, provenance, oversight, uncertainty, bias review, privacy, appeal, source traceability, and monitoring",
            "stewardship_model": "ownership, funding, maintenance, learning routines, repair pathways, evaluation cadence, reporting, community accountability, and sunset criteria",
        },
    )

    report = build_report(
        initiative_scores=initiative_scores,
        ai_scores=ai_scores,
        stewardship_scores=stewardship_scores,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "future_design_readiness_report.md").write_text(report, encoding="utf-8")

    print("Future design-thinking analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- future_design_initiative_scores.csv")
    print("- ai_governance_maturity_scores.csv")
    print("- stewardship_readiness_scores.csv")
    print("- future_design_scenario_review_results.csv")
    print("- future_design_monte_carlo_winners.csv")
    print("- future_design_risk_priority.csv")
    print("- future_design_readiness_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
