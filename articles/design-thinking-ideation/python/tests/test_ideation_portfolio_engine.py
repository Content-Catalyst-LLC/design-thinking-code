from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ideation_portfolio_engine import compute_composite_risk, score_ideas, validate_ideas


def test_score_ideas_orders_by_idea_value():
    df = pd.DataFrame(
        {
            "idea": ["A", "B"],
            "idea_cluster": ["X", "Y"],
            "desirability": [9, 7],
            "feasibility": [8, 8],
            "novelty": [8, 7],
            "equity_value": [9, 7],
            "learning_value": [8, 7],
            "residual_risk": [3, 5],
            "ethical_risk": [3, 5],
            "operational_risk": [3, 5],
            "technical_risk": [3, 5],
            "scaling_risk": [3, 5],
            "evidence_quality": [0.8, 0.7],
            "prototype_testability": [0.8, 0.7],
            "implementation_relevance": [8, 7],
        }
    )

    weights = {
        "desirability": 0.24,
        "feasibility": 0.18,
        "novelty": 0.18,
        "equity_value": 0.18,
        "learning_value": 0.12,
        "composite_risk": 0.10,
    }

    result = score_ideas(df, weights)
    assert result.iloc[0]["idea"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validation_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "idea": ["A"],
            "idea_cluster": ["X"],
            "desirability": [11],
            "feasibility": [8],
            "novelty": [8],
            "equity_value": [8],
            "learning_value": [8],
            "residual_risk": [3],
            "ethical_risk": [3],
            "operational_risk": [3],
            "technical_risk": [3],
            "scaling_risk": [3],
        }
    )

    issues = validate_ideas(df)
    assert any(issue.level == "error" for issue in issues)


def test_composite_risk_is_in_expected_range():
    df = pd.DataFrame(
        {
            "residual_risk": [4.0],
            "ethical_risk": [6.0],
            "operational_risk": [5.0],
            "technical_risk": [7.0],
            "scaling_risk": [8.0],
        }
    )

    risk = compute_composite_risk(df)
    assert 1.0 <= float(risk.iloc[0]) <= 10.0
