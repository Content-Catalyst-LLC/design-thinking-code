from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from problem_framing_decision_engine import (
    compute_framing_risk_index,
    score_frames,
    validate_problem_frames,
)


def test_score_frames_orders_by_frame_value():
    df = pd.DataFrame(
        {
            "frame": ["A", "B"],
            "explanatory_adequacy": [9, 7],
            "stakeholder_coverage": [8, 8],
            "opportunity_value": [9, 7],
            "framing_risk": [3, 5],
        }
    )

    weights = {
        "explanatory_adequacy": 0.30,
        "stakeholder_coverage": 0.25,
        "opportunity_value": 0.30,
        "framing_risk": 0.15,
    }

    result = score_frames(df, weights)
    assert result.iloc[0]["frame"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validation_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "frame": ["A"],
            "explanatory_adequacy": [11],
            "stakeholder_coverage": [8],
            "opportunity_value": [9],
            "framing_risk": [3],
        }
    )

    issues = validate_problem_frames(df)
    assert any(issue.level == "error" for issue in issues)


def test_risk_index_uses_components_when_available():
    df = pd.DataFrame(
        {
            "framing_risk": [5.0],
            "narrowness_risk": [2.0],
            "stakeholder_exclusion_risk": [4.0],
            "causality_risk": [6.0],
            "political_distortion_risk": [8.0],
        }
    )

    index = compute_framing_risk_index(df)
    assert float(index.iloc[0]) != 5.0
    assert 1.0 <= float(index.iloc[0]) <= 10.0
