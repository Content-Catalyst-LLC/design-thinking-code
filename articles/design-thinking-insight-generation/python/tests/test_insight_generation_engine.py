from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from insight_generation_engine import (
    compute_interpretive_risk_index,
    score_insights,
    validate_insights,
)


def test_score_insights_orders_by_insight_value():
    df = pd.DataFrame(
        {
            "insight": ["A", "B"],
            "pattern_support": [9, 7],
            "explanatory_depth": [8, 8],
            "opportunity_value": [9, 7],
            "interpretive_risk": [3, 5],
        }
    )

    weights = {
        "pattern_support": 0.30,
        "explanatory_depth": 0.30,
        "opportunity_value": 0.25,
        "interpretive_risk": 0.15,
    }

    result = score_insights(df, weights)
    assert result.iloc[0]["insight"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validation_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "insight": ["A"],
            "pattern_support": [11],
            "explanatory_depth": [8],
            "opportunity_value": [9],
            "interpretive_risk": [3],
        }
    )

    issues = validate_insights(df)
    assert any(issue.level == "error" for issue in issues)


def test_risk_index_uses_components_when_available():
    df = pd.DataFrame(
        {
            "interpretive_risk": [5.0],
            "sampling_risk": [2.0],
            "confirmation_bias_risk": [4.0],
            "evidence_thinness_risk": [6.0],
            "solution_capture_risk": [8.0],
        }
    )

    index = compute_interpretive_risk_index(df)
    assert float(index.iloc[0]) != 5.0
    assert 1.0 <= float(index.iloc[0]) <= 10.0
