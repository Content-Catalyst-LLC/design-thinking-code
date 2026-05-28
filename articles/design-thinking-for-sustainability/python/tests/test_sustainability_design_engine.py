from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sustainability_design_engine import score_concepts, validate_concepts


def test_score_concepts_ranks_stronger_concept_first():
    df = pd.DataFrame(
        {
            "concept": ["A", "B"],
            "concept_type": ["service", "service"],
            "transition_domain": ["energy", "energy"],
            "usability": [9, 7],
            "feasibility": [9, 7],
            "ecological_benefit": [9, 7],
            "circularity": [9, 7],
            "equity": [9, 7],
            "durability": [9, 7],
            "risk": [3, 5],
            "evidence_quality": [0.8, 0.7],
            "stakeholder_coverage": [0.8, 0.7],
            "lifecycle_boundary_quality": [0.8, 0.7],
            "burden_shift_risk": [3, 5],
            "implementation_complexity": [4, 6],
        }
    )
    weights = {
        "usability": 0.16,
        "feasibility": 0.16,
        "ecological_benefit": 0.24,
        "circularity": 0.16,
        "equity": 0.14,
        "durability": 0.08,
        "risk": 0.06,
    }
    result = score_concepts(df, weights)
    assert result.iloc[0]["concept"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validate_concepts_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "concept": ["A"],
            "concept_type": ["service"],
            "transition_domain": ["energy"],
            "usability": [11],
            "feasibility": [9],
            "ecological_benefit": [9],
            "circularity": [9],
            "equity": [9],
            "durability": [9],
            "risk": [3],
            "evidence_quality": [0.8],
            "stakeholder_coverage": [0.8],
            "lifecycle_boundary_quality": [0.8],
            "burden_shift_risk": [3],
            "implementation_complexity": [4],
        }
    )
    issues = validate_concepts(df)
    assert any(issue.level == "error" for issue in issues)
