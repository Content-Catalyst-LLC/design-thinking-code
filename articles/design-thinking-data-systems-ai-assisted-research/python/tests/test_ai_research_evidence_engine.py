from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ai_research_evidence_engine import score_ai_log, score_metadata, score_signals


def test_score_signals_prioritizes_high_bias_ai_risk():
    df = pd.DataFrame(
        {
            "signal": ["Clean finding", "Risky AI finding"],
            "evidence_type": ["interview", "ai_validation"],
            "source_strength": [0.8, 0.5],
            "relevance": [0.8, 0.9],
            "traceability": [0.9, 0.4],
            "representativeness": [0.8, 0.4],
            "validation": [0.9, 0.4],
            "missingness_risk": [0.2, 0.8],
            "ai_assistance_risk": [0.1, 0.9],
            "decision_relevance": [0.7, 0.9],
            "recency": [0.8, 0.8],
            "consent_alignment": [0.9, 0.4],
            "participant_coverage": [0.8, 0.3],
        }
    )
    result = score_signals(df)
    assert result.iloc[0]["signal"] == "Risky AI finding"


def test_ai_log_flags_review_risk():
    df = pd.DataFrame(
        {
            "artifact_id": ["A1"],
            "research_task": ["theme clustering"],
            "ai_tool_class": ["llm"],
            "source_grounding": [0.3],
            "human_review": [0.2],
            "output_reliability": [0.4],
            "sensitive_data_exposure": [0.8],
            "prompt_traceability": [0.2],
            "model_version_recorded": [0.0],
            "hallucination_risk": [0.8],
            "minority_signal_preservation": [0.2],
        }
    )
    result = score_ai_log(df)
    assert result.iloc[0]["ai_action"] == "full_ai_research_governance_review"


def test_metadata_requires_consent_review():
    df = pd.DataFrame(
        {
            "evidence_id": ["E1"],
            "evidence_type": ["transcript"],
            "source_owner": ["research"],
            "collection_date": ["2026-01-01"],
            "consent_recorded": [0],
            "method_recorded": [1],
            "participant_group_recorded": [1],
            "limitations_recorded": [1],
            "ai_use_recorded": [1],
            "reviewer_recorded": [1],
            "decision_link_recorded": [1],
            "retention_rule_recorded": [1],
        }
    )
    result = score_metadata(df)
    assert result.iloc[0]["metadata_action"] == "do_not_reuse_until_consent_review"
