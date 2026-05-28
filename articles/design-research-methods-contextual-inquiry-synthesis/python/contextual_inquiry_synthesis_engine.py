#!/usr/bin/env python3
"""
Professional contextual inquiry and synthesis decision-support engine.

This script provides a reproducible workflow for design research teams working
with contextual inquiry evidence. It summarizes evidence units, estimates
theme-level synthesis confidence, computes stakeholder coverage and method
triangulation, builds theme co-occurrence networks, estimates validation
priority, runs Monte Carlo uncertainty analysis, and generates auditable outputs.

The model is intentionally interpretable:

    C_i = w_e E_i + w_s S_i + w_m M_i - w_r R_i

where:
    C_i = synthesis confidence
    E_i = evidence support
    S_i = stakeholder coverage
    M_i = method triangulation
    R_i = interpretive risk

This code supports research documentation and team deliberation. It does not
automate qualitative interpretation or replace stakeholder validation.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


CORE_WEIGHTS = [
    "evidence_strength",
    "stakeholder_coverage",
    "method_triangulation",
    "interpretive_risk",
]

REQUIRED_EVIDENCE_COLUMNS = [
    "unit_id",
    "participant_group",
    "method",
    "primary_theme",
    "secondary_theme",
    "evidence_strength",
    "interpretive_risk",
    "environmental_constraint",
    "artifact_dependency",
    "workflow_stage",
    "privacy_sensitivity",
    "power_asymmetry",
]


@dataclass(frozen=True)
class EngineConfig:
    evidence_path: Path
    weights_path: Path | None
    coder_map_path: Path | None
    sampling_frame_path: Path | None
    output_dir: Path
    simulations: int
    seed: int
    score_sd: float
    bootstrap_iterations: int


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    field: str
    message: str


def minmax_scale(series: pd.Series, low: float = 1.0, high: float = 10.0) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    if values.max() == values.min():
        return pd.Series(np.repeat((low + high) / 2.0, len(values)), index=values.index)
    return low + (values - values.min()) * (high - low) / (values.max() - values.min())


def read_evidence(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Evidence file not found: {path}")

    df = pd.read_csv(path)
    missing = [col for col in REQUIRED_EVIDENCE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Evidence file missing required columns: {missing}")

    df = df.copy()
    for col in ["participant_group", "method", "primary_theme", "secondary_theme", "workflow_stage"]:
        df[col] = df[col].astype(str).str.strip()

    for col in [
        "unit_id",
        "evidence_strength",
        "interpretive_risk",
        "environmental_constraint",
        "artifact_dependency",
        "privacy_sensitivity",
        "power_asymmetry",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def read_weights(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame(
            [
                {
                    "scenario": "Balanced",
                    "evidence_strength": 0.35,
                    "stakeholder_coverage": 0.25,
                    "method_triangulation": 0.25,
                    "interpretive_risk": 0.15,
                }
            ]
        )

    df = pd.read_csv(path)
    required = ["scenario", *CORE_WEIGHTS]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Weights file missing required columns: {missing}")

    df = df.copy()
    df["scenario"] = df["scenario"].astype(str).str.strip()
    for col in CORE_WEIGHTS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[CORE_WEIGHTS].isna().any().any():
        raise ValueError("Scenario weights contain missing or non-numeric values.")

    sums = df[CORE_WEIGHTS].sum(axis=1)
    if not np.allclose(sums, 1.0, atol=1e-6):
        raise ValueError("Each scenario weight row must sum to 1.0.")

    return df


def read_optional_csv(path: Path | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None
    return pd.read_csv(path)


def validate_evidence(df: pd.DataFrame) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if df["unit_id"].duplicated().any():
        issues.append(
            ValidationIssue(
                level="error",
                field="unit_id",
                message="Duplicate evidence unit identifiers detected.",
            )
        )

    for col in [
        "evidence_strength",
        "interpretive_risk",
        "environmental_constraint",
        "artifact_dependency",
    ]:
        invalid = df[df[col].isna() | (df[col] < 1) | (df[col] > 10)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="error",
                    field=col,
                    message="Scores must be numeric and in the inclusive range [1, 10].",
                )
            )

    for col in ["privacy_sensitivity", "power_asymmetry"]:
        invalid = df[df[col].isna() | (df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=col,
                    message="Privacy and power-asymmetry scores should be in [0, 1].",
                )
            )

    if df["primary_theme"].nunique() < 3:
        issues.append(
            ValidationIssue(
                level="warning",
                field="primary_theme",
                message="Very few themes detected; synthesis diversity may be limited.",
            )
        )

    return issues


def summarize_themes(evidence: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    summary = (
        evidence.groupby("primary_theme")
        .agg(
            evidence_units=("unit_id", "count"),
            stakeholder_groups=("participant_group", "nunique"),
            methods=("method", "nunique"),
            workflow_stages=("workflow_stage", "nunique"),
            mean_evidence_strength=("evidence_strength", "mean"),
            mean_interpretive_risk=("interpretive_risk", "mean"),
            mean_environmental_constraint=("environmental_constraint", "mean"),
            mean_artifact_dependency=("artifact_dependency", "mean"),
            mean_privacy_sensitivity=("privacy_sensitivity", "mean"),
            mean_power_asymmetry=("power_asymmetry", "mean"),
        )
        .reset_index()
    )

    summary["stakeholder_coverage_score"] = minmax_scale(summary["stakeholder_groups"])
    summary["method_triangulation_score"] = minmax_scale(summary["methods"])
    summary["workflow_breadth_score"] = minmax_scale(summary["workflow_stages"])

    summary["synthesis_confidence"] = (
        weights["evidence_strength"] * summary["mean_evidence_strength"]
        + weights["stakeholder_coverage"] * summary["stakeholder_coverage_score"]
        + weights["method_triangulation"] * summary["method_triangulation_score"]
        - weights["interpretive_risk"] * summary["mean_interpretive_risk"]
    )

    summary["contextual_depth_index"] = (
        0.30 * summary["mean_environmental_constraint"]
        + 0.30 * summary["mean_artifact_dependency"]
        + 0.20 * summary["workflow_breadth_score"]
        + 0.20 * summary["mean_evidence_strength"]
    )

    summary["ethics_review_priority"] = (
        0.35 * summary["mean_power_asymmetry"]
        + 0.35 * summary["mean_privacy_sensitivity"]
        + 0.15 * (summary["mean_interpretive_risk"] / 10.0)
        + 0.15 * (summary["mean_environmental_constraint"] / 10.0)
    )

    summary["validation_priority"] = (
        0.35 * summary["mean_interpretive_risk"]
        + 0.25 * (10.0 - summary["mean_evidence_strength"])
        + 0.20 * (10.0 - summary["stakeholder_coverage_score"])
        + 0.20 * (10.0 - summary["method_triangulation_score"])
    )

    summary = summary.sort_values("synthesis_confidence", ascending=False).reset_index(drop=True)
    summary["rank"] = np.arange(1, len(summary) + 1)

    return summary


def run_scenario_analysis(evidence: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []

    for _, scenario in scenarios.iterrows():
        weights = {col: float(scenario[col]) for col in CORE_WEIGHTS}
        scored = summarize_themes(evidence, weights)
        scored["scenario"] = scenario["scenario"]
        for col in CORE_WEIGHTS:
            scored[f"weight_{col}"] = weights[col]
        frames.append(scored)

    return pd.concat(frames, ignore_index=True)


def build_theme_network(evidence: pd.DataFrame) -> Tuple[nx.Graph, pd.DataFrame, pd.DataFrame]:
    graph = nx.Graph()

    for _, row in evidence.iterrows():
        primary = row["primary_theme"]
        secondary = row["secondary_theme"]

        graph.add_node(primary)
        graph.add_node(secondary)

        if primary == secondary:
            continue

        if graph.has_edge(primary, secondary):
            graph[primary][secondary]["weight"] += 1
        else:
            graph.add_edge(primary, secondary, weight=1)

    centrality = nx.degree_centrality(graph) if len(graph) > 1 else {node: 0.0 for node in graph.nodes}
    betweenness = nx.betweenness_centrality(graph, weight="weight") if len(graph) > 1 else {node: 0.0 for node in graph.nodes}

    centrality_df = (
        pd.DataFrame(
            {
                "theme": list(centrality.keys()),
                "degree_centrality": list(centrality.values()),
                "betweenness_centrality": [betweenness[node] for node in centrality.keys()],
            }
        )
        .sort_values(["degree_centrality", "betweenness_centrality"], ascending=False)
        .reset_index(drop=True)
    )

    edges_df = pd.DataFrame(
        [
            {"source": u, "target": v, "weight": data.get("weight", 1)}
            for u, v, data in graph.edges(data=True)
        ]
    ).sort_values("weight", ascending=False)

    return graph, centrality_df, edges_df


def coder_agreement_summary(coder_map: pd.DataFrame | None) -> pd.DataFrame | None:
    if coder_map is None:
        return None

    coder_cols = [col for col in coder_map.columns if col.startswith("coder_")]
    if len(coder_cols) < 2:
        return None

    records = []
    for _, row in coder_map.iterrows():
        assignments = [str(row[col]) for col in coder_cols]
        counts = Counter(assignments)
        most_common_theme, most_common_count = counts.most_common(1)[0]
        agreement_ratio = most_common_count / len(coder_cols)
        records.append(
            {
                "unit_id": row["unit_id"],
                "consensus_theme": most_common_theme,
                "agreement_ratio": agreement_ratio,
                "coder_count": len(coder_cols),
                "unique_assignments": len(counts),
            }
        )

    summary = pd.DataFrame(records)

    theme_level = (
        summary.groupby("consensus_theme")
        .agg(
            coded_units=("unit_id", "count"),
            mean_agreement_ratio=("agreement_ratio", "mean"),
            low_agreement_units=("agreement_ratio", lambda x: int((x < 1.0).sum())),
        )
        .reset_index()
        .sort_values(["mean_agreement_ratio", "coded_units"], ascending=[True, False])
    )

    return theme_level


def stakeholder_sampling_diagnostic(
    evidence: pd.DataFrame,
    sampling_frame: pd.DataFrame | None,
) -> pd.DataFrame:
    observed = (
        evidence.groupby("participant_group")
        .agg(
            evidence_units=("unit_id", "count"),
            themes_observed=("primary_theme", "nunique"),
            methods_observed=("method", "nunique"),
            mean_power_asymmetry=("power_asymmetry", "mean"),
            mean_privacy_sensitivity=("privacy_sensitivity", "mean"),
        )
        .reset_index()
        .rename(columns={"participant_group": "stakeholder_group"})
    )

    if sampling_frame is not None:
        frame = sampling_frame.copy()
        for col in ["included_sessions", "access_risk", "power_asymmetry"]:
            if col in frame.columns:
                frame[col] = pd.to_numeric(frame[col], errors="coerce")

        diagnostic = frame.merge(observed, on="stakeholder_group", how="left")
        for col in ["evidence_units", "themes_observed", "methods_observed"]:
            diagnostic[col] = diagnostic[col].fillna(0)

        diagnostic["coverage_gap"] = np.maximum(
            diagnostic["included_sessions"].fillna(0) - diagnostic["evidence_units"], 0
        )
        diagnostic["sampling_priority"] = (
            0.35 * diagnostic["access_risk"].fillna(0)
            + 0.35 * diagnostic["power_asymmetry"].fillna(0)
            + 0.15 * np.clip(diagnostic["coverage_gap"] / 5.0, 0, 1)
            + 0.15 * (1 - np.clip(diagnostic["methods_observed"] / 5.0, 0, 1))
        )
        return diagnostic.sort_values("sampling_priority", ascending=False)

    observed["coverage_gap"] = np.nan
    observed["sampling_priority"] = (
        0.50 * observed["mean_power_asymmetry"]
        + 0.25 * observed["mean_privacy_sensitivity"]
        + 0.25 * (1 - np.clip(observed["methods_observed"] / 5.0, 0, 1))
    )
    return observed.sort_values("sampling_priority", ascending=False)


def saturation_analysis(evidence: pd.DataFrame, order_col: str = "unit_id") -> pd.DataFrame:
    sorted_evidence = evidence.sort_values(order_col)
    observed_themes: set[str] = set()
    records = []

    previous_count = 0
    for _, row in sorted_evidence.iterrows():
        observed_themes.add(row["primary_theme"])
        current_count = len(observed_themes)
        records.append(
            {
                "unit_id": row["unit_id"],
                "cumulative_theme_count": current_count,
                "new_theme_discovered": int(current_count > previous_count),
                "marginal_theme_discovery": current_count - previous_count,
            }
        )
        previous_count = current_count

    return pd.DataFrame(records)


def monte_carlo_theme_stability(
    evidence: pd.DataFrame,
    weights: Dict[str, float],
    simulations: int,
    score_sd: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    winner_counts: Counter[str] = Counter()
    records: List[dict] = []

    for simulation_id in range(simulations):
        sim = evidence.copy()
        for col in ["evidence_strength", "interpretive_risk", "environmental_constraint", "artifact_dependency"]:
            sim[col] = np.clip(
                rng.normal(loc=evidence[col].to_numpy(dtype=float), scale=score_sd),
                1.0,
                10.0,
            )
        scored = summarize_themes(sim, weights)
        winner_counts[str(scored.iloc[0]["primary_theme"])] += 1

        for _, row in scored.iterrows():
            records.append(
                {
                    "simulation_id": simulation_id,
                    "primary_theme": row["primary_theme"],
                    "synthesis_confidence": float(row["synthesis_confidence"]),
                    "validation_priority": float(row["validation_priority"]),
                    "contextual_depth_index": float(row["contextual_depth_index"]),
                    "rank": int(row["rank"]),
                }
            )

    winners = (
        pd.DataFrame(
            [
                {
                    "primary_theme": theme,
                    "times_ranked_first": count,
                    "probability_ranked_first": count / simulations,
                }
                for theme, count in winner_counts.items()
            ]
        )
        .sort_values("probability_ranked_first", ascending=False)
        .reset_index(drop=True)
    )

    return winners, pd.DataFrame(records)


def bootstrap_theme_scores(
    evidence: pd.DataFrame,
    weights: Dict[str, float],
    iterations: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 101)
    records: List[dict] = []

    for iteration in range(iterations):
        sampled = evidence.sample(
            n=len(evidence),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        scored = summarize_themes(sampled, weights)

        for _, row in scored.iterrows():
            records.append(
                {
                    "iteration": iteration,
                    "primary_theme": row["primary_theme"],
                    "synthesis_confidence": float(row["synthesis_confidence"]),
                    "validation_priority": float(row["validation_priority"]),
                    "rank": int(row["rank"]),
                }
            )

    boot = pd.DataFrame(records)
    return (
        boot.groupby("primary_theme")
        .agg(
            mean_synthesis_confidence=("synthesis_confidence", "mean"),
            sd_synthesis_confidence=("synthesis_confidence", "std"),
            mean_validation_priority=("validation_priority", "mean"),
            median_rank=("rank", "median"),
            mean_rank=("rank", "mean"),
            best_rank=("rank", "min"),
            worst_rank=("rank", "max"),
        )
        .reset_index()
        .sort_values(["median_rank", "mean_rank"])
    )


def save_plot_theme_confidence(theme_summary: pd.DataFrame, output_path: Path) -> None:
    plot_df = theme_summary.sort_values("synthesis_confidence", ascending=True)

    plt.figure(figsize=(11, 7))
    plt.barh(plot_df["primary_theme"], plot_df["synthesis_confidence"])
    plt.title("Contextual Inquiry Theme Synthesis Confidence")
    plt.xlabel("Synthesis confidence")
    plt.ylabel("Theme")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_validation_priority(theme_summary: pd.DataFrame, output_path: Path) -> None:
    plot_df = theme_summary.sort_values("validation_priority", ascending=True)

    plt.figure(figsize=(11, 7))
    plt.barh(plot_df["primary_theme"], plot_df["validation_priority"])
    plt.title("Contextual Inquiry Theme Validation Priority")
    plt.xlabel("Validation priority")
    plt.ylabel("Theme")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_plot_saturation(saturation: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(saturation["unit_id"], saturation["cumulative_theme_count"], marker="o")
    plt.title("Cumulative Theme Discovery During Contextual Inquiry")
    plt.xlabel("Evidence unit sequence")
    plt.ylabel("Cumulative theme count")
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
    evidence: pd.DataFrame,
    scenarios: pd.DataFrame,
    theme_summary: pd.DataFrame,
    scenario_results: pd.DataFrame,
    network_centrality: pd.DataFrame,
    coder_summary: pd.DataFrame | None,
    sampling_diagnostic: pd.DataFrame,
    saturation: pd.DataFrame,
    winners: pd.DataFrame,
    bootstrap: pd.DataFrame,
    issues: Iterable[ValidationIssue],
) -> str:
    top_theme = theme_summary.iloc[0]["primary_theme"] if not theme_summary.empty else "Not available"
    top_confidence = float(theme_summary.iloc[0]["synthesis_confidence"]) if not theme_summary.empty else math.nan

    issue_lines = "\n".join(
        f"- **{issue.level.upper()}** `{issue.field}`: {issue.message}" for issue in issues
    )
    if not issue_lines:
        issue_lines = "- No validation issues detected."

    coder_section = "No coder assignment file was provided."
    if coder_summary is not None:
        coder_section = dataframe_to_markdown_safe(coder_summary)

    report = f"""# Contextual Inquiry and Synthesis Research Report

## Article

Design Research Methods: Contextual Inquiry and Synthesis

## Summary

This report summarizes synthetic contextual inquiry evidence and demonstrates a reproducible research-synthesis workflow. It includes theme confidence scoring, validation-priority diagnostics, stakeholder coverage review, method triangulation, theme-network analysis, saturation analysis, coder-agreement summaries, Monte Carlo uncertainty modeling, and bootstrap stability.

## Leading theme in balanced scenario

- Theme: **{top_theme}**
- Synthesis confidence: **{top_confidence:.3f}**

## Validation notes

{issue_lines}

## Evidence count

- Evidence units: **{len(evidence)}**
- Participant groups: **{evidence["participant_group"].nunique()}**
- Methods: **{evidence["method"].nunique()}**
- Primary themes: **{evidence["primary_theme"].nunique()}**
- Scenarios: **{len(scenarios)}**

## Theme summary

{dataframe_to_markdown_safe(theme_summary)}

## Scenario results

{dataframe_to_markdown_safe(scenario_results[["scenario", "rank", "primary_theme", "synthesis_confidence", "validation_priority"]].head(30))}

## Theme network centrality

{dataframe_to_markdown_safe(network_centrality)}

## Coder agreement summary

{coder_section}

## Sampling diagnostic

{dataframe_to_markdown_safe(sampling_diagnostic)}

## Saturation tail

{dataframe_to_markdown_safe(saturation.tail(10))}

## Monte Carlo rank stability

{dataframe_to_markdown_safe(winners)}

## Bootstrap stability

{dataframe_to_markdown_safe(bootstrap)}

## Responsible interpretation

These outputs do not automate qualitative interpretation. They are designed to make synthesis traceable, reveal gaps, support research-team deliberation, and identify which themes require additional validation before they guide design direction.
"""
    return report


def parse_args(argv: List[str]) -> EngineConfig:
    parser = argparse.ArgumentParser(
        description="Professional contextual inquiry and synthesis engine."
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("../data/raw/contextual_inquiry_evidence_units_raw.csv"),
        help="Contextual inquiry evidence units CSV file.",
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("../data/raw/synthesis_scenario_weights.csv"),
        help="Scenario weights CSV file.",
    )
    parser.add_argument(
        "--coder-map",
        type=Path,
        default=Path("../data/raw/coder_theme_assignments_raw.csv"),
        help="Coder theme assignment CSV file.",
    )
    parser.add_argument(
        "--sampling-frame",
        type=Path,
        default=Path("../data/raw/stakeholder_sampling_frame_raw.csv"),
        help="Stakeholder sampling frame CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../outputs"),
        help="Output directory.",
    )
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--score-sd", type=float, default=0.5)
    parser.add_argument("--bootstrap-iterations", type=int, default=2500)

    args = parser.parse_args(argv)

    return EngineConfig(
        evidence_path=args.evidence,
        weights_path=args.weights if args.weights.exists() else None,
        coder_map_path=args.coder_map if args.coder_map.exists() else None,
        sampling_frame_path=args.sampling_frame if args.sampling_frame.exists() else None,
        output_dir=args.output_dir,
        simulations=args.simulations,
        seed=args.seed,
        score_sd=args.score_sd,
        bootstrap_iterations=args.bootstrap_iterations,
    )


def main(argv: List[str] | None = None) -> int:
    config = parse_args(argv or sys.argv[1:])
    config.output_dir.mkdir(parents=True, exist_ok=True)

    evidence = read_evidence(config.evidence_path)
    scenarios = read_weights(config.weights_path)
    coder_map = read_optional_csv(config.coder_map_path)
    sampling_frame = read_optional_csv(config.sampling_frame_path)

    issues = validate_evidence(evidence)
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

    theme_summary = summarize_themes(evidence, balanced_weights)
    scenario_results = run_scenario_analysis(evidence, scenarios)
    graph, network_centrality, network_edges = build_theme_network(evidence)
    coder_summary = coder_agreement_summary(coder_map)
    sampling_diagnostic = stakeholder_sampling_diagnostic(evidence, sampling_frame)
    saturation = saturation_analysis(evidence)

    winners, simulation_values = monte_carlo_theme_stability(
        evidence=evidence,
        weights=balanced_weights,
        simulations=config.simulations,
        score_sd=config.score_sd,
        seed=config.seed,
    )

    bootstrap = bootstrap_theme_scores(
        evidence=evidence,
        weights=balanced_weights,
        iterations=config.bootstrap_iterations,
        seed=config.seed,
    )

    theme_summary.to_csv(config.output_dir / "theme_synthesis_summary.csv", index=False)
    scenario_results.to_csv(config.output_dir / "theme_scenario_results.csv", index=False)
    network_centrality.to_csv(config.output_dir / "theme_network_centrality.csv", index=False)
    network_edges.to_csv(config.output_dir / "theme_network_edges.csv", index=False)
    sampling_diagnostic.to_csv(config.output_dir / "stakeholder_sampling_diagnostic.csv", index=False)
    saturation.to_csv(config.output_dir / "theme_saturation_analysis.csv", index=False)
    winners.to_csv(config.output_dir / "monte_carlo_theme_winners.csv", index=False)
    simulation_values.to_csv(config.output_dir / "theme_simulation_values.csv", index=False)
    bootstrap.to_csv(config.output_dir / "bootstrap_theme_stability.csv", index=False)

    if coder_summary is not None:
        coder_summary.to_csv(config.output_dir / "coder_agreement_summary.csv", index=False)

    save_plot_theme_confidence(theme_summary, config.output_dir / "theme_synthesis_confidence.png")
    save_plot_validation_priority(theme_summary, config.output_dir / "theme_validation_priority.png")
    save_plot_saturation(saturation, config.output_dir / "theme_saturation_curve.png")

    write_json(
        config.output_dir / "analysis_metadata.json",
        {
            "config": {
                **asdict(config),
                "evidence_path": str(config.evidence_path),
                "weights_path": str(config.weights_path) if config.weights_path else None,
                "coder_map_path": str(config.coder_map_path) if config.coder_map_path else None,
                "sampling_frame_path": str(config.sampling_frame_path) if config.sampling_frame_path else None,
                "output_dir": str(config.output_dir),
            },
            "validation_issues": [asdict(issue) for issue in issues],
            "nodes": list(graph.nodes),
            "edges": [
                {"source": u, "target": v, "weight": data.get("weight", 1)}
                for u, v, data in graph.edges(data=True)
            ],
        },
    )

    report = build_report(
        evidence=evidence,
        scenarios=scenarios,
        theme_summary=theme_summary,
        scenario_results=scenario_results,
        network_centrality=network_centrality,
        coder_summary=coder_summary,
        sampling_diagnostic=sampling_diagnostic,
        saturation=saturation,
        winners=winners,
        bootstrap=bootstrap,
        issues=issues,
    )
    (config.output_dir / "contextual_inquiry_synthesis_report.md").write_text(report, encoding="utf-8")

    print("Contextual inquiry synthesis analysis complete.")
    print(f"Outputs written to: {config.output_dir.resolve()}")
    print("Key files:")
    print("- theme_synthesis_summary.csv")
    print("- theme_scenario_results.csv")
    print("- theme_network_centrality.csv")
    print("- stakeholder_sampling_diagnostic.csv")
    print("- theme_saturation_analysis.csv")
    print("- contextual_inquiry_synthesis_report.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
