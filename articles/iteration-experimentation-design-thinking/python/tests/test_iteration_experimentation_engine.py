from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from iteration_experimentation_engine import (
    compute_risk_index,
    score_experiments,
    validate_experiments,
)


def test_score_experiments_orders_by_experiment_value():
    df = pd.DataFrame(
        {
            "experiment": ["A", "B"],
            "learning_gain": [9, 7],
            "update_flexibility": [8, 8],
            "expected_improvement": [9, 7],
            "residual_risk": [3, 5],
        }
    )

    weights = {
        "learning_gain": 0.35,
        "update_flexibility": 0.25,
        "expected_improvement": 0.25,
        "residual_risk": 0.15,
    }

    result = score_experiments(df, weights)
    assert result.iloc[0]["experiment"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validation_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "experiment": ["A"],
            "learning_gain": [11],
            "update_flexibility": [8],
            "expected_improvement": [9],
            "residual_risk": [3],
        }
    )

    issues = validate_experiments(df)
    assert any(issue.level == "error" for issue in issues)


def test_risk_index_uses_components_when_available():
    df = pd.DataFrame(
        {
            "residual_risk": [5.0],
            "ethical_risk": [2.0],
            "operational_risk": [4.0],
            "interpretive_risk": [6.0],
            "scaling_risk": [8.0],
        }
    )

    index = compute_risk_index(df)
    assert float(index.iloc[0]) != 5.0
    assert 1.0 <= float(index.iloc[0]) <= 10.0
