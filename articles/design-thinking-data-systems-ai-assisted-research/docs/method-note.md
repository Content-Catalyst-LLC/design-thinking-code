# Method Note: AI-Assisted Design Research Evidence

This folder provides a transparent decision-support framework for evaluating evidence confidence, bias risk, AI-assistance risk, source traceability, validation, consent alignment, participant coverage, metadata quality, and decision readiness in design-thinking research systems.

## Core models

Evidence confidence:

\[
C_i = w_sS_i + w_rR_i + w_tT_i + w_pP_i + w_vV_i
\]

Bias risk:

\[
B_i = \alpha M_i + \beta(1-P_i) + \gamma(1-V_i) + \delta A_i + \theta(1-T_i)
\]

Decision readiness:

\[
D_i = \lambda C_i + \mu R_i + \nu V_i + \rho T_i - \omega B_i
\]

## Recommended use

Use this model to support:

- research repository governance;
- AI-assisted synthesis review;
- research signal triage;
- design-decision evidence review;
- metadata quality assessment;
- provenance and traceability checks;
- research operations;
- responsible AI research workflows.

## Interpretation

Scores support research governance. They do not replace participant interpretation, researcher judgment, accessibility review, privacy review, ethics review, or design decision accountability.
