from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from strategy_design_engine import analyze_assumptions, score_options, validate_options


def test_score_options_prioritizes_stronger_option():
    df = pd.DataFrame(
        {
            "option": ["Weak", "Strong"],
            "option_type": ["test", "test"],
            "strategic_hypothesis": ["weak", "strong"],
            "desirability": [5, 9],
            "feasibility": [5, 8],
            "viability": [5, 8],
            "strategic_alignment": [5, 9],
            "ethical_quality": [5, 9],
            "learning_value": [5, 8],
            "implementation_effort": [8, 4],
            "strategic_risk": [8, 3],
            "capability_gap": [8, 3],
            "evidence_strength": [0.2, 0.8],
            "time_to_learn": [8, 3],
            "public_value": [5, 9],
        }
    )
    weights = {
        "desirability": 0.17,
        "feasibility": 0.13,
        "viability": 0.13,
        "strategic_alignment": 0.16,
        "ethical_quality": 0.11,
        "learning_value": 0.10,
        "public_value": 0.08,
        "evidence_strength": 0.05,
        "strategic_risk": 0.03,
        "implementation_effort": 0.02,
        "capability_gap": 0.01,
        "time_to_learn": 0.01,
    }
    result = score_options(df, weights)
    assert result.iloc[0]["option"] == "Strong"


def test_analyze_assumptions_prioritizes_low_confidence_high_importance():
    df = pd.DataFrame(
        {
            "option": ["A", "B"],
            "assumption": ["Low confidence", "High confidence"],
            "assumption_type": ["market", "market"],
            "importance": [0.9, 0.5],
            "confidence": [0.3, 0.9],
            "test_cost": [0.2, 0.2],
            "time_to_test": [3, 3],
            "ethical_sensitivity": [0.6, 0.2],
            "decision_threshold": [0.7, 0.7],
            "current_evidence": ["weak", "strong"],
        }
    )
    result = analyze_assumptions(df)
    assert result.iloc[0]["assumption"] == "Low confidence"


def test_validate_options_flags_out_of_range_score():
    df = pd.DataFrame(
        {
            "option": ["Bad"],
            "option_type": ["x"],
            "strategic_hypothesis": ["x"],
            "desirability": [11],
            "feasibility": [5],
            "viability": [5],
            "strategic_alignment": [5],
            "ethical_quality": [5],
            "learning_value": [5],
            "implementation_effort": [5],
            "strategic_risk": [5],
            "capability_gap": [5],
            "evidence_strength": [0.5],
            "time_to_learn": [5],
            "public_value": [5],
        }
    )
    issues = validate_options(df)
    assert any(issue.level == "error" for issue in issues)
