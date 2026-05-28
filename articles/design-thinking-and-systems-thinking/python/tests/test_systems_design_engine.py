from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from systems_design_engine import score_interventions, validate_portfolio


def test_score_interventions_ranks_stronger_intervention_first():
    df = pd.DataFrame(
        {
            "intervention": ["A", "B"],
            "intervention_type": ["service", "service"],
            "leverage_level": ["governance", "workflow"],
            "human_value": [9, 7],
            "system_leverage": [9, 7],
            "feasibility": [9, 7],
            "equity_sensitivity": [9, 7],
            "durability": [9, 7],
            "risk": [3, 5],
            "evidence_quality": [0.8, 0.7],
            "stakeholder_coverage": [0.8, 0.7],
            "context_complexity": [4, 6],
            "delay_sensitivity": [0.3, 0.5],
            "burden_shift_risk": [3, 5],
        }
    )
    weights = {
        "human_value": 0.24,
        "system_leverage": 0.26,
        "feasibility": 0.18,
        "equity_sensitivity": 0.14,
        "durability": 0.12,
        "risk": 0.06,
    }
    result = score_interventions(df, weights)
    assert result.iloc[0]["intervention"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validate_portfolio_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "intervention": ["A"],
            "intervention_type": ["service"],
            "leverage_level": ["workflow"],
            "human_value": [11],
            "system_leverage": [9],
            "feasibility": [9],
            "equity_sensitivity": [9],
            "durability": [9],
            "risk": [3],
            "evidence_quality": [0.8],
            "stakeholder_coverage": [0.8],
            "context_complexity": [4],
            "delay_sensitivity": [0.3],
            "burden_shift_risk": [3],
        }
    )
    issues = validate_portfolio(df)
    assert any(issue.level == "error" for issue in issues)
