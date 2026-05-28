# Model Card: Iteration and Experimentation Decision-Support Model

## Model name

Experiment Portfolio Value Model

## Intended use

The model supports transparent comparison of design experiments during research synthesis, prototype planning, pilot selection, implementation review, and responsible experimentation governance.

## Not intended for

- Automated experiment approval.
- Replacement of stakeholder research.
- Replacement of ethical review.
- Replacement of domain expertise.
- Final approval of public policy, clinical, educational, financial, or safety-critical experiments.
- Testing on people without appropriate consent, safeguards, or governance.

## Inputs

- Candidate experiment.
- Learning gain score.
- Update flexibility score.
- Expected improvement score.
- Residual risk score.
- Optional risk components.
- Optional evidence quality.
- Optional team confidence.
- Optional implementation complexity.
- Optional ethics-review diagnostics.

## Outputs

- Weighted experiment value.
- Risk index.
- Confidence-adjusted value.
- Rank within scenario.
- Monte Carlo rank stability.
- Bootstrap stability.
- Weight sensitivity summary.
- Ethics-review priority.

## Assumptions

The model assumes that experiment scores are provisional and that weights represent explicit institutional priorities. It also assumes that uncertainty, ethics, and implementation conditions should be documented rather than hidden.

## Limitations

The model cannot determine whether an experiment is ethically justified, legally permissible, politically legitimate, or contextually appropriate. Those judgments require human deliberation, stakeholder participation, fieldwork, domain expertise, and governance.

## Responsible use

Use this model as a documentation and deliberation tool. Treat disagreement about scores, weights, risk, or ethics as useful evidence that the design team needs further inquiry.
