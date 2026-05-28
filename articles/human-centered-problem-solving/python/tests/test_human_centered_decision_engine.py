from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from human_centered_decision_engine import (
    compute_burden_index,
    score_options,
    validate_design_options,
)


def test_score_options_orders_by_hc_value():
    df = pd.DataFrame(
        {
            "option": ["A", "B"],
            "human_benefit": [9, 7],
            "usability": [8, 8],
            "stakeholder_fit": [9, 7],
            "burden": [3, 5],
        }
    )

    weights = {
        "human_benefit": 0.30,
        "usability": 0.25,
        "stakeholder_fit": 0.30,
        "burden": 0.15,
    }

    result = score_options(df, weights)
    assert result.iloc[0]["option"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validation_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "option": ["A"],
            "human_benefit": [11],
            "usability": [8],
            "stakeholder_fit": [9],
            "burden": [3],
        }
    )

    issues = validate_design_options(df)
    assert any(issue.level == "error" for issue in issues)


def test_burden_index_uses_components_when_available():
    df = pd.DataFrame(
        {
            "burden": [5.0],
            "learning_cost": [2.0],
            "compliance_cost": [4.0],
            "psychological_cost": [6.0],
            "access_cost": [8.0],
        }
    )

    index = compute_burden_index(df)
    assert float(index.iloc[0]) != 5.0
    assert 1.0 <= float(index.iloc[0]) <= 10.0
