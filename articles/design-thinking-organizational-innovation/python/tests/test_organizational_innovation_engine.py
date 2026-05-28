from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from organizational_innovation_engine import score_concepts, validate_concepts


def test_score_concepts_ranks_stronger_concept_first():
    df = pd.DataFrame(
        {
            "concept": ["A", "B"],
            "concept_type": ["service", "service"],
            "organizational_domain": ["operations", "operations"],
            "desirability": [9, 7],
            "feasibility": [9, 7],
            "viability": [9, 7],
            "equity": [9, 7],
            "learning_value": [9, 7],
            "implementation_readiness": [9, 7],
            "risk": [3, 5],
            "evidence_quality": [0.8, 0.7],
            "stakeholder_coverage": [0.8, 0.7],
            "technical_complexity": [4, 6],
            "organizational_complexity": [4, 6],
            "ethical_risk": [3, 5],
        }
    )
    weights = {
        "desirability": 0.22,
        "feasibility": 0.16,
        "viability": 0.16,
        "equity": 0.18,
        "learning_value": 0.12,
        "implementation_readiness": 0.10,
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
            "organizational_domain": ["operations"],
            "desirability": [11],
            "feasibility": [9],
            "viability": [9],
            "equity": [9],
            "learning_value": [9],
            "implementation_readiness": [9],
            "risk": [3],
            "evidence_quality": [0.8],
            "stakeholder_coverage": [0.8],
            "technical_complexity": [4],
            "organizational_complexity": [4],
            "ethical_risk": [3],
        }
    )
    issues = validate_concepts(df)
    assert any(issue.level == "error" for issue in issues)
