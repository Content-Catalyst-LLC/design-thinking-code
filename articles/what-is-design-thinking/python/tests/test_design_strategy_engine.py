from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from design_strategy_engine import score_pathways, validate_pathway_data


def test_score_pathways_orders_by_design_value():
    df = pd.DataFrame(
        {
            "pathway": ["A", "B"],
            "human_relevance": [9, 7],
            "feasibility": [8, 8],
            "learning_value": [9, 7],
            "residual_risk": [3, 5],
        }
    )

    weights = {
        "human_relevance": 0.35,
        "feasibility": 0.25,
        "learning_value": 0.25,
        "residual_risk": 0.15,
    }

    result = score_pathways(df, weights)
    assert result.iloc[0]["pathway"] == "A"
    assert result.iloc[0]["rank"] == 1


def test_validation_flags_out_of_range_scores():
    df = pd.DataFrame(
        {
            "pathway": ["A"],
            "human_relevance": [11],
            "feasibility": [8],
            "learning_value": [9],
            "residual_risk": [3],
        }
    )

    issues = validate_pathway_data(df)
    assert any(issue.level == "error" for issue in issues)
