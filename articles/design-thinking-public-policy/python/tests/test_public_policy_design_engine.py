from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from public_policy_design_engine import score_pilots, validate_pilots


def test_score_pilots_ranks_stronger_pilot_first():
    df = pd.DataFrame(
        {
            "pilot": ["A", "B"],
            "policy_domain": ["benefits", "benefits"],
            "pilot_type": ["service", "service"],
            "accessibility": [9, 7],
            "feasibility": [9, 7],
            "legitimacy": [9, 7],
            "equity": [9, 7],
            "burden_reduction": [9, 7],
            "durability": [9, 7],
            "risk": [3, 5],
            "evidence_quality": [0.8, 0.7],
            "stakeholder_coverage": [0.8, 0.7],
            "legal_complexity": [4, 6],
            "implementation_complexity": [4, 6],
            "participation_quality": [0.8, 0.7],
        }
    )
    weights = {
        "accessibility": 0.20,
        "feasibility": 0.16,
        "legitimacy": 0.16,
        "equity": 0.20,
        "burden_reduction": 0.14,
        "durability": 0.08,
        "risk": 0.06,
    }
    result = score_pilots(df, weights)
    assert result.iloc[0]["pilot"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validate_pilots_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "pilot": ["A"],
            "policy_domain": ["benefits"],
            "pilot_type": ["service"],
            "accessibility": [11],
            "feasibility": [9],
            "legitimacy": [9],
            "equity": [9],
            "burden_reduction": [9],
            "durability": [9],
            "risk": [3],
            "evidence_quality": [0.8],
            "stakeholder_coverage": [0.8],
            "legal_complexity": [4],
            "implementation_complexity": [4],
            "participation_quality": [0.8],
        }
    )
    issues = validate_pilots(df)
    assert any(issue.level == "error" for issue in issues)
