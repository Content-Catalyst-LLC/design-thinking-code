from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ethics_power_inclusion_engine import score_decisions, score_participation, score_stakeholders


def test_score_stakeholders_prioritizes_high_burden_low_power():
    df = pd.DataFrame(
        {
            "group": ["Low risk", "High burden"],
            "stakeholder_type": ["user", "user"],
            "access": [8, 4],
            "voice": [8, 4],
            "safety": [8, 5],
            "compensation": [7, 4],
            "representation": [8, 4],
            "accountability": [8, 4],
            "time_burden": [3, 8],
            "cognitive_burden": [3, 8],
            "emotional_burden": [3, 8],
            "documentation_burden": [3, 8],
            "uncertainty_burden": [3, 8],
            "coordination_burden": [3, 8],
            "affectedness": [0.4, 0.9],
            "trust_level": [8, 4],
            "accessibility_need": [0.2, 0.9],
        }
    )
    result = score_stakeholders(df)
    assert result.iloc[0]["group"] == "High burden"


def test_score_decisions_flags_high_risk():
    df = pd.DataFrame(
        {
            "design_decision": ["Low risk", "High risk"],
            "decision_type": ["x", "x"],
            "harm_severity": [0.2, 0.9],
            "probability": [0.2, 0.7],
            "exposure": [0.2, 0.8],
            "detectability": [0.8, 0.2],
            "accountability": [0.8, 0.2],
            "inclusion_strength": [0.8, 0.3],
            "public_value": [0.8, 0.4],
            "repairability": [0.8, 0.2],
            "privacy_sensitivity": [0.2, 0.8],
            "autonomy_risk": [0.2, 0.8],
            "manipulation_risk": [0.2, 0.8],
        }
    )
    result = score_decisions(df)
    assert result.iloc[0]["design_decision"] == "High risk"


def test_score_participation_detects_tokenism():
    df = pd.DataFrame(
        {
            "process_component": ["Problem framing"],
            "participation_level": ["consultation"],
            "participant_influence": [0.2],
            "decision_authority": [0.1],
            "compensation_quality": [0.4],
            "accessibility_quality": [0.5],
            "feedback_loop_strength": [0.2],
            "community_control": [0.1],
            "documentation_transparency": [0.4],
            "safety_quality": [0.5],
            "interpretation_sharedness": [0.2],
        }
    )
    result = score_participation(df)
    assert result.iloc[0]["participation_action"] == "do_not_label_as_codesign"
