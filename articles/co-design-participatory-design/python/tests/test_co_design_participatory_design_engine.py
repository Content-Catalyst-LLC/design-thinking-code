from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from co_design_participatory_design_engine import score_activities, validate_activities


def test_score_activities_ranks_stronger_activity_first():
    df = pd.DataFrame(
        {
            "activity": ["A", "B"],
            "activity_type": ["workshop", "workshop"],
            "design_stage": ["framing", "framing"],
            "representation": [9, 7],
            "accessibility": [9, 7],
            "participant_influence": [9, 7],
            "trust_quality": [9, 7],
            "evidence_quality": [9, 7],
            "implementation_accountability": [9, 7],
            "decision_impact": [9, 7],
            "ethical_risk": [3, 5],
            "affectedness_weight": [0.8, 0.8],
            "compensation_quality": [8, 6],
            "feedback_loop_quality": [8, 6],
            "tokenism_risk": [3, 5],
        }
    )
    weights = {
        "representation": 0.18,
        "accessibility": 0.14,
        "participant_influence": 0.22,
        "trust_quality": 0.12,
        "evidence_quality": 0.12,
        "implementation_accountability": 0.12,
        "decision_impact": 0.14,
        "ethical_risk": 0.08,
    }
    result = score_activities(df, weights)
    assert result.iloc[0]["activity"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validate_activities_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "activity": ["A"],
            "activity_type": ["workshop"],
            "design_stage": ["framing"],
            "representation": [11],
            "accessibility": [9],
            "participant_influence": [9],
            "trust_quality": [9],
            "evidence_quality": [9],
            "implementation_accountability": [9],
            "decision_impact": [9],
            "ethical_risk": [3],
            "affectedness_weight": [0.8],
            "compensation_quality": [8],
            "feedback_loop_quality": [8],
            "tokenism_risk": [3],
        }
    )
    issues = validate_activities(df)
    assert any(issue.level == "error" for issue in issues)
