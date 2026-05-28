#!/usr/bin/env python3
"""
Professional AI-assisted design research evidence engine.

This script evaluates research signals, evidence confidence, bias risk,
AI-assistance risk, metadata quality, provenance, consent alignment,
validation status, participant coverage, scenario-weighted review priorities,
and decision readiness.

The workflow supports research governance. It does not automate design
decisions, ethical approval, public-sector decisions, or participant
interpretation.
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
    "confidence_score",
    "bias_risk",
    "decision_readiness",
    "traceability",
    "validation",
    "consent_alignment",
    "ai_risk",
    "metadata_quality",
    "participant_coverage",
]


@dataclass(frozen=True)
class EngineConfig:
    signals_path: Path
    ai_log_path: Path | None
    metadata_path: Path | None
    weights_path: Path | None
    risk_register_path: Path | None
    output_dir: Path
    simulations: int
    seed: int
    value_sd: float
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
                    "confidence_score": 0.20,
                    "bias_risk": 0.17,
                    "decision_readiness": 0.21,
                    "traceability": 0.10,
                    "validation": 0.10,
                    "consent_alignment": 0.08,
                    "ai_risk": 0.07,
                    "metadata_quality": 0.04,
                    "participant_coverage": 0.03,
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


def validate_inputs(signals: pd.DataFrame) -> List[ValidationIssue]:
    required = [
        "signal",
        "evidence_type",
        "source_strength",
        "relevance",
        "traceability",
        "representativeness",
        "validation",
        "missingness_risk",
        "ai_assistance_risk",
        "decision_relevance",
        "recency",
        "consent_alignment",
        "participant_coverage",
    ]
    issues: List[ValidationIssue] = []
    for col in required:
        if col not in signals.columns:
            issues.append(ValidationIssue("error", col, "Missing research signal column."))

    numeric_cols = [col for col in required if col not in ["signal", "evidence_type"]]
    issues.extend(validate_range(signals, numeric_cols, 0, 1))
    return issues


def score_signals(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.copy()

    numeric_cols = [
        "source_strength",
        "relevance",
        "traceability",
        "representativeness",
        "validation",
        "missingness_risk",
        "ai_assistance_risk",
        "decision_relevance",
        "recency",
        "consent_alignment",
        "participant_coverage",
    ]
    for col in numeric_cols:
        scored[col] = pd.to_numeric(scored[col], errors="coerce")

    scored["confidence_score"] = (
        0.18 * scored["source_strength"]
        + 0.17 * scored["relevance"]
        + 0.15 * scored["traceability"]
        + 0.15 * scored["representativeness"]
        + 0.15 * scored["validation"]
        + 0.08 * scored["recency"]
        + 0.07 * scored["consent_alignment"]
        + 0.05 * scored["participant_coverage"]
    )

    scored["bias_risk"] = (
        0.26 * scored["missingness_risk"]
        + 0.22 * (1.0 - scored["representativeness"])
        + 0.18 * (1.0 - scored["validation"])
        + 0.14 * scored["ai_assistance_risk"]
        + 0.10 * (1.0 - scored["traceability"])
        + 0.10 * (1.0 - scored["participant_coverage"])
    )

    scored["ai_risk"] = (
        0.38 * scored["ai_assistance_risk"]
        + 0.18 * (1.0 - scored["traceability"])
        + 0.16 * (1.0 - scored["validation"])
        + 0.14 * scored["missingness_risk"]
        + 0.14 * (1.0 - scored["consent_alignment"])
    )

    scored["decision_readiness"] = (
        0.30 * scored["confidence_score"]
        + 0.24 * scored["decision_relevance"]
        + 0.14 * scored["validation"]
        + 0.12 * scored["traceability"]
        + 0.08 * scored["consent_alignment"]
        + 0.08 * scored["participant_coverage"]
        - 0.04 * scored["bias_risk"]
    ).clip(0.0, 1.0)

    scored["governance_priority"] = (
        0.24 * scored["bias_risk"]
        + 0.22 * scored["ai_risk"]
        + 0.16 * (1.0 - scored["traceability"])
        + 0.14 * (1.0 - scored["consent_alignment"])
        + 0.12 * (1.0 - scored["validation"])
        + 0.12 * scored["decision_relevance"]
    )

    scored["review_action"] = np.select(
        [
            scored["bias_risk"] >= 0.50,
            scored["ai_risk"] >= 0.55,
            scored["consent_alignment"] < 0.60,
            scored["confidence_score"] < 0.65,
            scored["decision_readiness"] >= 0.75,
        ],
        [
            "review_bias_missingness_and_coverage",
            "validate_ai_output_against_sources",
            "review_consent_and_reuse_limits",
            "collect_or_validate_more_evidence",
            "ready_for_design_decision_review",
        ],
        default="use_as_directional_evidence",
    )

    return scored.sort_values("governance_priority", ascending=False).reset_index(drop=True)


def score_ai_log(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()

    required = [
        "artifact_id",
        "research_task",
        "ai_tool_class",
        "source_grounding",
        "human_review",
        "output_reliability",
        "sensitive_data_exposure",
        "prompt_traceability",
        "model_version_recorded",
        "hallucination_risk",
        "minority_signal_preservation",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"AI assistance log missing required columns: {missing}")

    scored = df.copy()
    numeric_cols = [col for col in required if col not in ["artifact_id", "research_task", "ai_tool_class"]]
    for col in numeric_cols:
        scored[col] = pd.to_numeric(scored[col], errors="coerce")

    scored["ai_governance_score"] = (
        0.18 * scored["source_grounding"]
        + 0.18 * scored["human_review"]
        + 0.14 * scored["output_reliability"]
        + 0.14 * scored["prompt_traceability"]
        + 0.12 * scored["model_version_recorded"]
        + 0.12 * scored["minority_signal_preservation"]
        - 0.07 * scored["sensitive_data_exposure"]
        - 0.05 * scored["hallucination_risk"]
    ).clip(0.0, 1.0)

    scored["ai_review_risk"] = (
        0.22 * (1.0 - scored["source_grounding"])
        + 0.20 * (1.0 - scored["human_review"])
        + 0.16 * scored["hallucination_risk"]
        + 0.14 * scored["sensitive_data_exposure"]
        + 0.12 * (1.0 - scored["prompt_traceability"])
        + 0.10 * (1.0 - scored["minority_signal_preservation"])
        + 0.06 * (1.0 - scored["model_version_recorded"])
    )

    scored["ai_action"] = np.select(
        [
            scored["ai_review_risk"] >= 0.45,
            scored["human_review"] < 0.70,
            scored["source_grounding"] < 0.70,
            scored["minority_signal_preservation"] < 0.55,
        ],
        [
            "full_ai_research_governance_review",
            "increase_human_review_before_use",
            "strengthen_source_grounding",
            "review_minority_signal_preservation",
        ],
        default="document_and_monitor",
    )

    return scored.sort_values("ai_review_risk", ascending=False).reset_index(drop=True)


def score_metadata(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()

    binary_cols = [
        "consent_recorded",
        "method_recorded",
        "participant_group_recorded",
        "limitations_recorded",
        "ai_use_recorded",
        "reviewer_recorded",
        "decision_link_recorded",
        "retention_rule_recorded",
    ]
    required = ["evidence_id", "evidence_type", "source_owner", "collection_date", *binary_cols]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Metadata registry missing required columns: {missing}")

    scored = df.copy()
    for col in binary_cols:
        scored[col] = pd.to_numeric(scored[col], errors="coerce").fillna(0).clip(0, 1)

    scored["metadata_quality"] = (
        0.18 * scored["consent_recorded"]
        + 0.13 * scored["method_recorded"]
        + 0.13 * scored["participant_group_recorded"]
        + 0.12 * scored["limitations_recorded"]
        + 0.12 * scored["ai_use_recorded"]
        + 0.12 * scored["reviewer_recorded"]
        + 0.10 * scored["decision_link_recorded"]
        + 0.10 * scored["retention_rule_recorded"]
    )

    scored["metadata_gap_count"] = 8 - scored[binary_cols].sum(axis=1)
    scored["metadata_action"] = np.select(
        [
            scored["consent_recorded"] == 0,
            scored["metadata_quality"] < 0.70,
            scored["decision_link_recorded"] == 0,
            scored["ai_use_recorded"] == 0,
        ],
        [
            "do_not_reuse_until_consent_review",
            "complete_metadata_before_reuse",
            "link_evidence_to_decision_record",
            "record_ai_use_status",
        ],
        default="metadata_ready_for_governed_reuse",
    )

    return scored.sort_values(["metadata_quality", "metadata_gap_count"], ascending=[True, False]).reset_index(drop=True)


def analyze_risk_register(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()

    required = [
        "risk_id",
        "risk_category",
        "risk_description",
        "severity",
        "likelihood",
        "detectability",
        "repair_difficulty",
        "mitigation_owner",
        "mitigation_status",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Research governance risk register missing required columns: {missing}")

    scored = df.copy()
    for col in ["severity", "likelihood", "detectability", "repair_difficulty"]:
        scored[col] = pd.to_numeric(scored[col], errors="coerce")

    scored["risk_priority_number"] = (
        scored["severity"] * scored["likelihood"] * scored["detectability"] * scored["repair_difficulty"]
    )
    scored["normalized_risk_priority"] = scored["risk_priority_number"] / scored["risk_priority_number"].max()

    return scored.sort_values("risk_priority_number", ascending=False).reset_index(drop=True)


def run_scenario_review(
    signal_scores: pd.DataFrame,
    metadata_scores: pd.DataFrame,
    weights: pd.DataFrame,
) -> pd.DataFrame:
    metadata_quality = 0.75
    if not metadata_scores.empty:
        metadata_quality = float(metadata_scores["metadata_quality"].mean())

    rows: List[dict] = []

    for _, scenario in weights.iterrows():
        for _, signal in signal_scores.iterrows():
            review_priority = (
                scenario["confidence_score"] * (1.0 - signal["confidence_score"])
                + scenario["bias_risk"] * signal["bias_risk"]
                + scenario["decision_readiness"] * (1.0 - signal["decision_readiness"])
                + scenario["traceability"] * (1.0 - signal["traceability"])
                + scenario["validation"] * (1.0 - signal["validation"])
                + scenario["consent_alignment"] * (1.0 - signal["consent_alignment"])
                + scenario["ai_risk"] * signal["ai_risk"]
                + scenario["metadata_quality"] * (1.0 - metadata_quality)
                + scenario["participant_coverage"] * (1.0 - signal["participant_coverage"])
            )

            rows.append(
                {
                    "scenario": scenario["scenario"],
                    "signal": signal["signal"],
                    "evidence_type": signal["evidence_type"],
                    "scenario_review_priority": float(review_priority),
                    "confidence_score": float(signal["confidence_score"]),
                    "bias_risk": float(signal["bias_risk"]),
                    "ai_risk": float(signal["ai_risk"]),
                    "decision_readiness": float(signal["decision_readiness"]),
                    "review_action": signal["review_action"],
                }
            )

    result = pd.DataFrame(rows)
    result["scenario_rank"] = (
        result.groupby("scenario")["scenario_review_priority"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )
    return result.sort_values(["scenario", "scenario_rank", "signal"]).reset_index(drop=True)


def monte_carlo_signal_stability(
    signals: pd.DataFrame,
    simulations: int,
    value_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    top_governance: Counter[str] = Counter()
    records: List[dict] = []

    bounded_cols = [
        "source_strength",
        "relevance",
        "traceability",
        "representativeness",
        "validation",
        "missingness_risk",
        "ai_assistance_risk",
        "decision_relevance",
        "recency",
        "consent_alignment",
        "participant_coverage",
    ]

    for simulation_id in range(simulations):
        simulated = signals.copy()

        for col in bounded_cols:
            simulated[col] = rng.normal(
                loc=signals[col].to_numpy(dtype=float),
                scale=value_sd,
            ).clip(0.0, 1.0)

        scored = score_signals(simulated)
        top_governance[str(scored.iloc[0]["signal"])] += 1

        for rank, (_, row) in enumerate(scored.iterrows(), start=1):
            records.append(
                {
                    "simulation_id": simulation_id,
                    "signal": row["signal"],
                    "evidence_type": row["evidence_type"],
                    "confidence_score": float(row["confidence_score"]),
                    "bias_risk": float(row["bias_risk"]),
                    "ai_risk": float(row["ai_risk"]),
                    "decision_readiness": float(row["decision_readiness"]),
                    "governance_priority": float(row["governance_priority"]),
                    "rank": rank,
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "signal": signal,
                    "times_highest_governance_priority": count,
                    "probability_highest_governance_priority": count / simulations,
                }
                for signal, count in top_governance.items()
            ]
        )
        .sort_values("probability_highest_governance_priority", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_signal_stability(signals: pd.DataFrame, iterations: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = signals.sample(
            n=len(signals),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = score_signals(sampled)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "signal": row["signal"],
                    "confidence_score": float(row["confidence_score"]),
                    "bias_risk": float(row["bias_risk"]),
                    "ai_risk": float(row["ai_risk"]),
                    "decision_readiness": float(row["decision_readiness"]),
                    "governance_priority": float(row["governance_priority"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("signal")
        .agg(
            mean_confidence=("confidence_score", "mean"),
            mean_bias_risk=("bias_risk", "mean"),
            mean_ai_risk=("ai_risk", "mean"),
            mean_decision_readiness=("decision_readiness", "mean"),
            mean_governance_priority=("governance_priority", "mean"),
            sd_governance_priority=("governance_priority", "std"),
        )
        .reset_index()
        .sort_values("mean_governance_priority", ascending=False)
    )


def random_weight_sensitivity(signal_scores: pd.DataFrame, metadata_scores: pd.DataFrame, samples: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 202)
    winner_counts: Counter[str] = Counter()
    metadata_quality = 0.75 if metadata_scores.empty else float(metadata_scores["metadata_quality"].mean())

    for _ in range(samples):
        weights = dict(zip(SCENARIO_CRITERIA, rng.dirichlet(np.ones(len(SCENARIO_CRITERIA)))))
        values = []
        for _, signal in signal_scores.iterrows():
            score = (
                weights["confidence_score"] * (1.0 - signal["confidence_score"])
                + weights["bias_risk"] * signal["bias_risk"]
                + weights["decision_readiness"] * (1.0 - signal["decision_readiness"])
                + weights["traceability"] * (1.0 - signal["traceability"])
                + weights["validation"] * (1.0 - signal["validation"])
                + weights["consent_alignment"] * (1.0 - signal["consent_alignment"])
                + weights["ai_risk"] * signal["ai_risk"]
                + weights["metadata_quality"] * (1.0 - metadata_quality)
                + weights["participant_coverage"] * (1.0 - signal["participant_coverage"])
            )
            values.append((signal["signal"], score))

        winner_counts[max(values, key=lambda x: x[1])[0]] += 1

    return (
        pd.DataFrame(
            [
                {
                    "signal": signal,
                    "times_highest_under_random_weights": count,
                    "probability_highest_under_random_weights": count / samples,
                }
                for signal, count in winner_counts.items()
            ]
        )
        .sort_values("probability_highest_under_random_weights", ascending=False)
        .reset_index(drop=True)
    )


def save_signal_plot(signal_scores: pd.DataFrame, output_path: Path) -> None:
    plot_df = signal_scores.sort_values("governance_priority", ascending=True)
    plt.figure(figsize=(12, 7))
    plt.barh(plot_df["signal"], plot_df["governance_priority"])
    plt.title("Research Evidence Governance Priority")
    plt.xlabel("Governance priority")
    plt.ylabel("Research signal")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_decision_readiness_plot(signal_scores: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(10, 7))
    sizes = np.clip(signal_scores["confidence_score"].to_numpy(dtype=float), 0.1, 1.0) * 420
    plt.scatter(signal_scores["bias_risk"], signal_scores["decision_readiness"], s=sizes)
    for _, row in signal_scores.iterrows():
        plt.annotate(row["signal"], (row["bias_risk"], row["decision_readiness"]), fontsize=8)
    plt.title("Decision Readiness vs Bias Risk")
    plt.xlabel("Bias risk")
    plt.ylabel("Decision readiness")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_monte_carlo_plot(winners: pd.DataFrame, output_path: Path) -> None:
    if winners.empty:
        return
    plot_df = winners.copy()
    plot_df["probability_pct"] = plot_df["probability_highest_governance_priority"] * 100.0
    plt.figure(figsize=(12, 6))
    plt.bar(plot_df["signal"], plot_df["probability_pct"])
    plt.title("Probability of Highest Governance Priority Under Uncertainty")
    plt.ylabel("Probability (%)")
    plt.xlabel("Research signal")
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
    signal_scores: pd.DataFrame,
    ai_scores: pd.DataFrame,
    metadata_scores: pd.DataFrame,
    scenario_results: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    sensitivity: pd.DataFrame,
    risk_summary: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top_signal = signal_scores.iloc[0]["signal"] if not signal_scores.empty else "Not available"
    top_ready = signal_scores.sort_values("decision_readiness", ascending=False).iloc[0]["signal"] if not signal_scores.empty else "Not available"

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    ai_section = "No AI assistance log provided."
    if not ai_scores.empty:
        ai_section = dataframe_to_markdown_safe(ai_scores)

    metadata_section = "No metadata registry provided."
    if not metadata_scores.empty:
        metadata_section = dataframe_to_markdown_safe(metadata_scores)

    risk_section = "No research governance risk register provided."
    if not risk_summary.empty:
        risk_section = dataframe_to_markdown_safe(risk_summary)

    return f"""# Design Thinking, Data Systems, and AI-Assisted Research Report

## Summary

This report evaluates research signals, evidence confidence, bias risk, AI-assistance risk, metadata quality, provenance, consent alignment, validation status, participant coverage, scenario-weighted governance priorities, and decision readiness.

## Highest governance-priority research signal

- Signal: **{top_signal}**

## Highest decision-readiness research signal

- Signal: **{top_ready}**

## Validation notes

{issue_lines}

## Research signal scores

{dataframe_to_markdown_safe(signal_scores)}

## AI assistance review

{ai_section}

## Metadata registry review

{metadata_section}

## Scenario review results

{dataframe_to_markdown_safe(scenario_results.head(60))}

## Monte Carlo governance-priority stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap signal stability

{dataframe_to_markdown_safe(bootstrap)}

## Random-weight sensitivity

{dataframe_to_markdown_safe(sensitivity)}

## Research governance risk register

{risk_section}

## Responsible interpretation

These outputs do not decide what research evidence means. They support structured review of source grounding, traceability, missingness, participant coverage, AI-assistance risk, consent alignment, validation status, and governance needs before research findings shape design decisions.
"""


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(description="Professional AI-assisted design research evidence engine.")
    parser.add_argument("--signals", type=Path, default=Path("../data/raw/research_signals_raw.csv"))
    parser.add_argument("--ai-log", type=Path, default=Path("../data/raw/ai_assistance_log_raw.csv"))
    parser.add_argument("--metadata", type=Path, default=Path("../data/raw/evidence_metadata_registry_raw.csv"))
    parser.add_argument("--weights", type=Path, default=Path("../data/raw/research_scenario_weights.csv"))
    parser.add_argument("--risk-register", type=Path, default=Path("../data/raw/research_governance_risk_register_raw.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs"))
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--value-sd", type=float, default=0.06)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)
    parser.add_argument("--sensitivity-samples", type=int, default=10000)

    args = parser.parse_args(argv)

    return EngineConfig(
        signals_path=args.signals,
        ai_log_path=args.ai_log if args.ai_log.exists() else None,
        metadata_path=args.metadata if args.metadata.exists() else None,
        weights_path=args.weights if args.weights.exists() else None,
        risk_register_path=args.risk_register if args.risk_register.exists() else None,
        output_dir=args.output_dir,
        simulations=args.simulations,
        seed=args.seed,
        value_sd=args.value_sd,
        bootstrap_iterations=args.bootstrap_iterations,
        sensitivity_samples=args.sensitivity_samples,
    )


def main(argv: List[str] | None = None) -> int:
    config = parse_args(argv or sys.argv[1:])
    config.output_dir.mkdir(parents=True, exist_ok=True)

    signals_raw = read_required_csv(config.signals_path, "Research signals")
    ai_log_raw = read_optional_csv(config.ai_log_path)
    metadata_raw = read_optional_csv(config.metadata_path)
    weights = read_weights(config.weights_path)
    risk_register_raw = read_optional_csv(config.risk_register_path)

    issues = validate_inputs(signals_raw)
    fatal = [issue for issue in issues if issue.level == "error"]
    if fatal:
        for issue in fatal:
            print(f"ERROR [{issue.field}]: {issue.message}", file=sys.stderr)
        return 2

    signal_scores = score_signals(signals_raw)
    ai_scores = score_ai_log(ai_log_raw)
    metadata_scores = score_metadata(metadata_raw)
    risk_summary = analyze_risk_register(risk_register_raw)
    scenario_results = run_scenario_review(signal_scores, metadata_scores, weights)

    winners, simulation_records = monte_carlo_signal_stability(
        signals=signals_raw,
        simulations=config.simulations,
        value_sd=config.value_sd,
        seed=config.seed,
    )

    simulation_summary = (
        simulation_records.groupby("signal")
        .agg(
            mean_confidence=("confidence_score", "mean"),
            mean_bias_risk=("bias_risk", "mean"),
            mean_ai_risk=("ai_risk", "mean"),
            mean_decision_readiness=("decision_readiness", "mean"),
            mean_governance_priority=("governance_priority", "mean"),
            sd_governance_priority=("governance_priority", "std"),
            median_rank=("rank", "median"),
            p90_rank=("rank", lambda x: float(np.quantile(x, 0.90))),
        )
        .reset_index()
        .sort_values("mean_governance_priority", ascending=False)
    )

    bootstrap = bootstrap_signal_stability(
        signals=signals_raw,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    sensitivity = random_weight_sensitivity(
        signal_scores=signal_scores,
        metadata_scores=metadata_scores,
        samples=config.sensitivity_samples,
        seed=config.seed,
    )

    signal_scores.to_csv(config.output_dir / "research_signal_scores.csv", index=False)
    ai_scores.to_csv(config.output_dir / "ai_assistance_review_scores.csv", index=False)
    metadata_scores.to_csv(config.output_dir / "metadata_registry_quality_scores.csv", index=False)
    scenario_results.to_csv(config.output_dir / "research_scenario_review_results.csv", index=False)
    winners.to_csv(config.output_dir / "research_signal_monte_carlo_winners.csv", index=False)
    simulation_records.to_csv(config.output_dir / "research_signal_simulation_records.csv", index=False)
    simulation_summary.to_csv(config.output_dir / "research_signal_simulation_summary.csv", index=False)
    bootstrap.to_csv(config.output_dir / "research_signal_bootstrap_stability.csv", index=False)
    sensitivity.to_csv(config.output_dir / "research_signal_random_weight_sensitivity.csv", index=False)

    if not risk_summary.empty:
        risk_summary.to_csv(config.output_dir / "research_governance_risk_priority.csv", index=False)

    save_signal_plot(signal_scores, config.output_dir / "research_signal_governance_priority.png")
    save_decision_readiness_plot(signal_scores, config.output_dir / "research_signal_decision_readiness.png")
    save_monte_carlo_plot(winners, config.output_dir / "research_signal_monte_carlo_winners.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "signals_path": str(config.signals_path),
                "ai_log_path": str(config.ai_log_path) if config.ai_log_path else None,
                "metadata_path": str(config.metadata_path) if config.metadata_path else None,
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "risk_register_path": str(config.risk_register_path) if config.risk_register_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "scenario_criteria": SCENARIO_CRITERIA,
            "confidence_model": "weighted source strength, relevance, traceability, representativeness, validation, recency, consent alignment, and participant coverage",
            "bias_model": "weighted missingness, weak representativeness, weak validation, AI-assistance risk, weak traceability, and weak participant coverage",
        },
    )

    report = build_report(
        signal_scores=signal_scores,
        ai_scores=ai_scores,
        metadata_scores=metadata_scores,
        scenario_results=scenario_results,
        winners=winners,
        bootstrap=bootstrap,
        sensitivity=sensitivity,
        risk_summary=risk_summary,
        issues=issues,
    )
    (config.output_dir / "ai_research_evidence_report.md").write_text(report, encoding="utf-8")

    print("AI-assisted design research evidence analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- research_signal_scores.csv")
    print("- ai_assistance_review_scores.csv")
    print("- metadata_registry_quality_scores.csv")
    print("- research_scenario_review_results.csv")
    print("- research_signal_monte_carlo_winners.csv")
    print("- research_governance_risk_priority.csv")
    print("- ai_research_evidence_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
