from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from contextual_inquiry_synthesis_engine import (
    minmax_scale,
    summarize_themes,
    validate_evidence,
)


def test_minmax_scale_constant_series():
    series = pd.Series([3, 3, 3])
    scaled = minmax_scale(series)
    assert all(value == 5.5 for value in scaled)


def test_validate_evidence_flags_out_of_range_strength():
    df = pd.DataFrame(
        {
            "unit_id": [1],
            "participant_group": ["A"],
            "method": ["interview"],
            "primary_theme": ["theme"],
            "secondary_theme": ["theme"],
            "evidence_strength": [11],
            "interpretive_risk": [3],
            "environmental_constraint": [4],
            "artifact_dependency": [5],
            "workflow_stage": ["stage"],
            "privacy_sensitivity": [0.5],
            "power_asymmetry": [0.5],
        }
    )
    issues = validate_evidence(df)
    assert any(issue.level == "error" for issue in issues)


def test_summarize_themes_returns_confidence():
    df = pd.DataFrame(
        {
            "unit_id": [1, 2, 3],
            "participant_group": ["A", "B", "C"],
            "method": ["interview", "observation", "artifact"],
            "primary_theme": ["status", "status", "access"],
            "secondary_theme": ["trust", "trust", "status"],
            "evidence_strength": [8, 9, 7],
            "interpretive_risk": [3, 4, 5],
            "environmental_constraint": [6, 7, 8],
            "artifact_dependency": [7, 8, 9],
            "workflow_stage": ["x", "y", "z"],
            "privacy_sensitivity": [0.4, 0.5, 0.6],
            "power_asymmetry": [0.5, 0.6, 0.7],
        }
    )
    weights = {
        "evidence_strength": 0.35,
        "stakeholder_coverage": 0.25,
        "method_triangulation": 0.25,
        "interpretive_risk": 0.15,
    }
    summary = summarize_themes(df, weights)
    assert "synthesis_confidence" in summary.columns
    assert len(summary) == 2
