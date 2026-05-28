from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from prototype_portfolio_engine import compute_composite_risk, score_prototypes, validate_portfolio


def test_score_prototypes_orders_by_value():
    df = pd.DataFrame(
        {
            "prototype": ["A", "B"],
            "prototype_type": ["paper", "digital"],
            "fidelity_level": ["low", "mid"],
            "learning_gain": [9, 7],
            "feasibility_signal": [8, 8],
            "user_response": [8, 7],
            "equity_value": [9, 7],
            "implementation_relevance": [8, 7],
            "ethical_risk": [3, 5],
            "operational_risk": [3, 5],
            "technical_risk": [3, 5],
            "scaling_risk": [3, 5],
            "evidence_quality": [0.8, 0.7],
            "prototype_testability": [0.8, 0.7],
            "stakeholder_coverage": [0.8, 0.7],
        }
    )
    weights = {
        "learning_gain": 0.25,
        "feasibility_signal": 0.18,
        "user_response": 0.20,
        "equity_value": 0.15,
        "implementation_relevance": 0.12,
        "composite_risk": 0.10,
    }
    result = score_prototypes(df, weights)
    assert result.iloc[0]["prototype"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validation_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "prototype": ["A"],
            "prototype_type": ["paper"],
            "fidelity_level": ["low"],
            "learning_gain": [11],
            "feasibility_signal": [8],
            "user_response": [8],
            "equity_value": [8],
            "implementation_relevance": [8],
            "ethical_risk": [3],
            "operational_risk": [3],
            "technical_risk": [3],
            "scaling_risk": [3],
            "evidence_quality": [0.8],
            "prototype_testability": [0.8],
            "stakeholder_coverage": [0.8],
        }
    )
    issues = validate_portfolio(df)
    assert any(issue.level == "error" for issue in issues)


def test_composite_risk_range():
    df = pd.DataFrame(
        {
            "ethical_risk": [4.0],
            "operational_risk": [5.0],
            "technical_risk": [6.0],
            "scaling_risk": [7.0],
        }
    )
    risk = compute_composite_risk(df)
    assert 1.0 <= float(risk.iloc[0]) <= 10.0
