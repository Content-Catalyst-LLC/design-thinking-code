# Model Card: Insight Generation Decision-Support Model

## Model name

Candidate Insight Value Model

## Intended use

The model supports transparent comparison of candidate insights during qualitative synthesis, evidence review, design research interpretation, opportunity translation, ideation planning, and prototype prioritization.

## Not intended for

- Automated interpretation.
- Replacement of qualitative judgment.
- Replacement of stakeholder validation.
- Declaring that an insight is true without evidence.
- Overriding contradictory evidence.
- Reducing lived experience to a score.
- Justifying a solution the team already wanted.

## Inputs

- Candidate insight.
- Pattern support score.
- Explanatory depth score.
- Opportunity value score.
- Interpretive risk score.
- Optional risk components.
- Optional evidence quality.
- Optional stakeholder diversity.
- Optional prototype testability.
- Optional evidence-source diagnostics.

## Outputs

- Weighted insight value.
- Interpretive-risk index.
- Confidence-adjusted value.
- Testability-adjusted value.
- Interpretation review priority.
- Rank within scenario.
- Monte Carlo rank stability.
- Bootstrap stability.
- Weight sensitivity summary.
- Evidence validation priority.

## Assumptions

The model assumes that candidate insights are provisional and that weights represent explicit synthesis priorities. It also assumes that uncertainty, interpretive risk, stakeholder coverage, and evidence limitations should be documented rather than hidden.

## Limitations

The model cannot determine whether an insight is correct, ethical, representative, or adequate by itself. Those judgments require qualitative interpretation, stakeholder validation, domain expertise, design judgment, and prototype testing.

## Responsible use

Use this model as a documentation and deliberation tool. Treat disagreement about scores, weights, or risks as useful evidence that the research team needs further inquiry.
