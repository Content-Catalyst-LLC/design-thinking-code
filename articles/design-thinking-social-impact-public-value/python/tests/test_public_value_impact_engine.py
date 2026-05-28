from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from public_value_impact_engine import score_interventions, score_participation, score_stakeholder_burden


def test_score_interventions_rewards_public_value_and_low_risk():
    df = pd.DataFrame(
        {
            "intervention": ["Weak intervention", "Strong intervention"],
            "intervention_type": ["x", "x"],
            "access": [5, 9],
            "equity": [5, 9],
            "dignity": [5, 9],
            "legitimacy": [5, 9],
            "accountability": [5, 9],
            "outcome_strength": [5, 9],
            "sustainability": [5, 8],
            "learning_capacity": [5, 8],
            "feasibility": [5, 8],
            "governance_strength": [5, 8],
            "implementation_risk": [9, 4],
            "burden_risk": [9, 4],
            "participation_quality": [5, 8],
            "community_defined_value": [5, 9],
            "repair_capacity": [5, 8],
            "stewardship_capacity": [5, 8],
        }
    )
    result = score_interventions(df)
    assert result.iloc[0]["intervention"] == "Strong intervention"


def test_stakeholder_burden_flags_insufficient_reduction():
    df = pd.DataFrame(
        {
            "stakeholder_group": ["High burden group"],
            "stakeholder_type": ["community_member"],
            "baseline_time_burden": [8],
            "baseline_cognitive_burden": [8],
            "baseline_emotional_burden": [8],
            "baseline_documentation_burden": [8],
            "baseline_uncertainty_burden": [8],
            "post_time_burden": [7.8],
            "post_cognitive_burden": [7.8],
            "post_emotional_burden": [7.8],
            "post_documentation_burden": [7.8],
            "post_uncertainty_burden": [7.8],
            "affectedness": [0.9],
            "voice": [3],
            "influence": [3],
            "repair_access": [3],
            "trust_gap": [8],
            "accessibility_need": [0.8],
        }
    )
    result = score_stakeholder_burden(df)
    assert result.iloc[0]["priority_action"] in {
        "urgent_burden_and_repair_review",
        "accessibility_and_assisted_access_review",
        "insufficient_burden_reduction",
        "power_and_voice_review",
    }


def test_participation_requires_power_sharing():
    df = pd.DataFrame(
        {
            "participation_activity": ["Weak consultation"],
            "participation_level": ["consult"],
            "affected_people_involved": [0.5],
            "decision_influence": [0.2],
            "compensation": [0.2],
            "accessibility_support": [0.4],
            "language_support": [0.4],
            "feedback_loop": [0.3],
            "community_ownership": [0.2],
            "power_sharing": [0.2],
            "documentation_quality": [0.5],
            "ethical_review": [0.5],
        }
    )
    result = score_participation(df)
    assert result.iloc[0]["participation_action"] == "redesign_participation_before_use"
