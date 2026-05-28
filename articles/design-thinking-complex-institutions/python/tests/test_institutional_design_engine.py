from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from institutional_design_engine import score_governance, score_options, score_stakeholder_burden


def test_score_options_rewards_high_readiness():
    df = pd.DataFrame(
        {
            "option": ["Weak option", "Strong option"],
            "option_type": ["x", "x"],
            "desirability": [5, 9],
            "authority": [4, 8],
            "capability": [4, 8],
            "funding": [4, 8],
            "policy_fit": [4, 8],
            "governance_strength": [4, 8],
            "trust_gain": [4, 9],
            "burden_reduction": [4, 9],
            "coordination_complexity": [9, 4],
            "implementation_risk": [9, 4],
            "data_readiness": [4, 8],
            "frontline_fit": [4, 8],
            "maintenance_capacity": [4, 8],
            "equity_priority": [5, 9],
            "public_value": [5, 9],
        }
    )
    result = score_options(df)
    assert result.iloc[0]["option"] == "Strong option"


def test_stakeholder_burden_prioritizes_high_burden_low_voice():
    df = pd.DataFrame(
        {
            "stakeholder_group": ["Low burden", "High burden"],
            "stakeholder_type": ["user", "user"],
            "time_burden": [3, 8],
            "cognitive_burden": [3, 8],
            "emotional_burden": [3, 8],
            "documentation_burden": [3, 8],
            "uncertainty_burden": [3, 8],
            "coordination_burden": [3, 8],
            "accessibility_need": [0.2, 0.9],
            "trust_gap": [2, 8],
            "affectedness": [0.4, 0.9],
            "voice": [8, 3],
            "influence": [8, 3],
            "repair_access": [8, 3],
        }
    )
    result = score_stakeholder_burden(df)
    assert result.iloc[0]["stakeholder_group"] == "High burden"


def test_governance_flags_weak_decision_rights():
    df = pd.DataFrame(
        {
            "decision_domain": ["Weak governance"],
            "owner": ["nobody"],
            "approval_authority": [0.2],
            "budget_authority": [0.2],
            "policy_authority": [0.2],
            "data_authority": [0.2],
            "implementation_authority": [0.2],
            "community_accountability": [0.2],
            "escalation_clarity": [0.2],
            "review_cadence": [0.2],
            "maintenance_ownership": [0.2],
        }
    )
    result = score_governance(df)
    assert result.iloc[0]["governance_action"] == "clarify_decision_rights_before_design_work"
