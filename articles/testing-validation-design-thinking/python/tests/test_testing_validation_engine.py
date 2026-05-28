from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from testing_validation_engine import compute_validation_value, validate_concepts


def test_compute_validation_value_ranks_stronger_concept_first():
    df = pd.DataFrame(
        {
            "concept": ["A", "B"],
            "prototype_type": ["flow", "flow"],
            "fidelity_level": ["mid", "mid"],
            "desirability": [9, 7],
            "feasibility": [8, 7],
            "viability": [8, 7],
            "responsibility": [9, 7],
            "friction": [3, 5],
            "residual_risk": [3, 5],
            "evidence_quality": [0.8, 0.7],
            "stakeholder_coverage": [0.8, 0.7],
            "method_triangulation": [0.8, 0.7],
            "equity_signal": [8, 7],
            "accessibility_signal": [8, 7],
            "operational_signal": [8, 7],
        }
    )
    weights = {
        "desirability": 0.25,
        "feasibility": 0.20,
        "viability": 0.20,
        "responsibility": 0.20,
        "risk_penalty": 0.15,
    }
    result = compute_validation_value(df, weights)
    assert result.iloc[0]["concept"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validate_concepts_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "concept": ["A"],
            "prototype_type": ["flow"],
            "fidelity_level": ["mid"],
            "desirability": [11],
            "feasibility": [8],
            "viability": [8],
            "responsibility": [8],
            "friction": [3],
            "residual_risk": [3],
            "evidence_quality": [0.8],
            "stakeholder_coverage": [0.8],
            "method_triangulation": [0.8],
            "equity_signal": [8],
            "accessibility_signal": [8],
            "operational_signal": [8],
        }
    )
    issues = validate_concepts(df)
    assert any(issue.level == "error" for issue in issues)
