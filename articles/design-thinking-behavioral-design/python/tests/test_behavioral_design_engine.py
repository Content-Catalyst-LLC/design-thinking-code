from pathlib import Path
import sys
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from behavioral_design_engine import score_barriers, score_interventions, sigmoid

def test_sigmoid_bounds():
    assert 0 < sigmoid(-100) < 0.001
    assert 0.999 < sigmoid(100) < 1

def test_score_barriers_prioritizes_high_friction():
    df = pd.DataFrame({
        "segment": ["Low risk", "High risk"],
        "target_behavior": ["Act", "Act"],
        "motivation": [8, 6], "capability": [8, 5], "opportunity": [8, 5],
        "trust": [8, 5], "friction": [3, 8], "affectedness": [0.5, 0.9],
        "time_pressure": [3, 8], "cognitive_load": [3, 8],
        "emotional_load": [3, 8], "social_support": [8, 5],
        "institutional_risk": [3, 8],
    })
    result = score_barriers(df)
    assert result.iloc[0]["segment"] == "High risk"

def test_score_interventions_prioritizes_stronger_option():
    df = pd.DataFrame({
        "intervention": ["Weak", "Strong"],
        "intervention_type": ["prompt", "support"],
        "mechanism": ["timing", "access"],
        "expected_behavior_gain": [0.02, 0.14], "importance": [0.5, 0.9],
        "equity_reach": [0.4, 0.9], "ethical_risk": [0.2, 0.05],
        "implementation_effort": [0.5, 0.4], "transparency": [0.6, 0.9],
        "autonomy_preservation": [0.6, 0.9], "trust_effect": [0.4, 0.9],
        "accessibility_effect": [0.4, 0.9], "durability": [0.3, 0.8],
    })
    weights = {
        "expected_behavior_gain": .22, "importance": .14, "equity_reach": .16,
        "transparency": .08, "autonomy_preservation": .08, "trust_effect": .10,
        "accessibility_effect": .10, "durability": .06, "ethical_risk": .04,
        "implementation_effort": .02
    }
    assert score_interventions(df, weights).iloc[0]["intervention"] == "Strong"
