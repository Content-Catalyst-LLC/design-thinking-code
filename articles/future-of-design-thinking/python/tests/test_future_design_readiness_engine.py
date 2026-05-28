from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from future_design_readiness_engine import score_ai_governance, score_initiatives, score_stewardship


def test_score_initiatives_rewards_readiness_and_low_risk():
    df = pd.DataFrame(
        {
            "initiative": ["Weak initiative", "Strong initiative"],
            "initiative_type": ["x", "x"],
            "human_centered_quality": [5, 9],
            "systems_literacy": [5, 9],
            "evidence_quality": [5, 9],
            "ethical_maturity": [5, 9],
            "ai_governance": [5, 8],
            "implementation_capacity": [5, 8],
            "public_value": [5, 9],
            "stewardship_capacity": [5, 9],
            "unmanaged_risk": [9, 4],
            "participation_quality": [5, 9],
            "organizational_learning": [5, 9],
            "data_infrastructure": [5, 8],
            "climate_responsibility": [5, 8],
            "burden_awareness": [5, 9],
        }
    )
    result = score_initiatives(df)
    assert result.iloc[0]["initiative"] == "Strong initiative"


def test_ai_governance_flags_weak_use_case():
    df = pd.DataFrame(
        {
            "ai_use_case": ["Weak AI"],
            "governance": [5],
            "validation": [5],
            "data_quality": [5],
            "provenance": [5],
            "human_oversight": [5],
            "uncertainty_management": [5],
            "bias_review": [5],
            "privacy_review": [5],
            "appeal_pathway": [5],
            "source_traceability": [5],
            "model_monitoring": [5],
        }
    )
    result = score_ai_governance(df)
    assert result.iloc[0]["ai_action"] == "do_not_pilot_until_governance_strengthened"


def test_stewardship_requires_repair_and_accountability():
    df = pd.DataFrame(
        {
            "initiative": ["Weak stewardship"],
            "ownership": [0.5],
            "funding": [0.5],
            "maintenance": [0.5],
            "learning_routines": [0.5],
            "repair_pathways": [0.4],
            "evaluation_cadence": [0.5],
            "public_reporting": [0.5],
            "community_accountability": [0.4],
            "sunset_criteria": [0.5],
            "implementation_owner": ["none"],
        }
    )
    result = score_stewardship(df)
    assert result.iloc[0]["stewardship_action"] == "strengthen_stewardship_before_launch"
