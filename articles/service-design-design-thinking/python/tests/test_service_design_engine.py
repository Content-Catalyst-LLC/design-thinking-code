from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from service_design_engine import end_to_end_reliability, score_stages, validate_stages


def test_reliability_is_product_of_completion_probabilities():
    df = pd.DataFrame({"completion_probability": [0.9, 0.8, 0.5]})
    assert abs(end_to_end_reliability(df) - 0.36) < 1e-9


def test_score_stages_flags_high_burden_stage():
    df = pd.DataFrame(
        {
            "stage": ["Low burden", "High burden"],
            "stage_order": [1, 2],
            "channel": ["web", "phone"],
            "completion_probability": [0.9, 0.6],
            "clarity": [8, 5],
            "trust": [8, 5],
            "accessibility": [8, 5],
            "user_burden": [3, 8],
            "staff_load": [3, 8],
            "recovery_quality": [8, 5],
            "frontstage_quality": [8, 5],
            "backstage_readiness": [8, 5],
            "policy_complexity": [3, 8],
            "data_dependency": [3, 8],
        }
    )
    weights = {
        "completion_probability": 0.22,
        "clarity": 0.18,
        "trust": 0.18,
        "accessibility": 0.16,
        "recovery_quality": 0.14,
        "user_burden": 0.07,
        "staff_load": 0.05,
    }
    result = score_stages(df, weights)
    assert result.iloc[0]["stage"] == "High burden"


def test_validate_stages_flags_bad_probability():
    df = pd.DataFrame(
        {
            "stage": ["Bad"],
            "stage_order": [1],
            "channel": ["web"],
            "completion_probability": [1.2],
            "clarity": [8],
            "trust": [8],
            "accessibility": [8],
            "user_burden": [3],
            "staff_load": [3],
            "recovery_quality": [8],
            "frontstage_quality": [8],
            "backstage_readiness": [8],
            "policy_complexity": [3],
            "data_dependency": [3],
        }
    )
    issues = validate_stages(df)
    assert any(issue.level == "error" for issue in issues)
