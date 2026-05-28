from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from implementation_scaling_engine import score_interventions, validate_portfolio


def test_score_interventions_ranks_stronger_intervention_first():
    df = pd.DataFrame(
        {
            "intervention": ["A", "B"],
            "intervention_type": ["workflow", "workflow"],
            "implementation_stage": ["pilot", "pilot"],
            "adoption_readiness": [9, 7],
            "operational_fit": [9, 7],
            "durability": [9, 7],
            "governance_readiness": [9, 7],
            "equity_readiness": [9, 7],
            "financial_sustainability": [9, 7],
            "operational_risk": [3, 5],
            "governance_risk": [3, 5],
            "technical_risk": [3, 5],
            "equity_risk": [3, 5],
            "financial_risk": [3, 5],
            "evidence_quality": [0.8, 0.7],
            "stakeholder_coverage": [0.8, 0.7],
            "context_complexity": [4, 6],
            "scale_sensitivity": [0.3, 0.5],
        }
    )
    weights = {
        "adoption_readiness": 0.20,
        "operational_fit": 0.18,
        "durability": 0.18,
        "governance_readiness": 0.15,
        "equity_readiness": 0.14,
        "financial_sustainability": 0.10,
        "composite_risk": 0.05,
    }
    result = score_interventions(df, weights)
    assert result.iloc[0]["intervention"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validate_portfolio_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "intervention": ["A"],
            "intervention_type": ["workflow"],
            "implementation_stage": ["pilot"],
            "adoption_readiness": [11],
            "operational_fit": [9],
            "durability": [9],
            "governance_readiness": [9],
            "equity_readiness": [9],
            "financial_sustainability": [9],
            "operational_risk": [3],
            "governance_risk": [3],
            "technical_risk": [3],
            "equity_risk": [3],
            "financial_risk": [3],
            "evidence_quality": [0.8],
            "stakeholder_coverage": [0.8],
            "context_complexity": [4],
            "scale_sensitivity": [0.3],
        }
    )
    issues = validate_portfolio(df)
    assert any(issue.level == "error" for issue in issues)
