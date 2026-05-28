from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from evaluation_learning_engine import score_interventions, validate_portfolio


def test_score_interventions_ranks_stronger_intervention_first():
    df = pd.DataFrame(
        {
            "intervention": ["A", "B"],
            "intervention_type": ["service", "service"],
            "evaluation_stage": ["post_launch", "post_launch"],
            "outcome_improvement": [9, 7],
            "burden_reduction": [9, 7],
            "equity_performance": [9, 7],
            "trust_improvement": [9, 7],
            "durability": [9, 7],
            "operational_cost": [3, 5],
            "residual_risk": [3, 5],
            "evidence_quality": [0.8, 0.7],
            "stakeholder_coverage": [0.8, 0.7],
            "method_triangulation": [0.8, 0.7],
            "uncertainty": [0.2, 0.4],
            "baseline_quality": [6, 6],
            "current_quality": [8, 7],
        }
    )
    weights = {
        "outcome_improvement": 0.24,
        "burden_reduction": 0.20,
        "equity_performance": 0.20,
        "trust_improvement": 0.16,
        "durability": 0.14,
        "penalty": 0.06,
    }
    result = score_interventions(df, weights)
    assert result.iloc[0]["intervention"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validate_portfolio_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "intervention": ["A"],
            "intervention_type": ["service"],
            "evaluation_stage": ["post_launch"],
            "outcome_improvement": [11],
            "burden_reduction": [9],
            "equity_performance": [9],
            "trust_improvement": [9],
            "durability": [9],
            "operational_cost": [3],
            "residual_risk": [3],
            "evidence_quality": [0.8],
            "stakeholder_coverage": [0.8],
            "method_triangulation": [0.8],
            "uncertainty": [0.2],
            "baseline_quality": [6],
            "current_quality": [8],
        }
    )
    issues = validate_portfolio(df)
    assert any(issue.level == "error" for issue in issues)
