#!/usr/bin/env Rscript

# Professional AI-assisted design research evidence analysis in R.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
signals_path <- file.path(article_dir, "data", "raw", "research_signals_raw.csv")
ai_log_path <- file.path(article_dir, "data", "raw", "ai_assistance_log_raw.csv")
metadata_path <- file.path(article_dir, "data", "raw", "evidence_metadata_registry_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "research_governance_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

signals <- readr::read_csv(signals_path, show_col_types = FALSE)
ai_log <- readr::read_csv(ai_log_path, show_col_types = FALSE)
metadata <- readr::read_csv(metadata_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

signal_scores <- signals %>%
  mutate(
    confidence_score =
      0.18 * source_strength +
      0.17 * relevance +
      0.15 * traceability +
      0.15 * representativeness +
      0.15 * validation +
      0.08 * recency +
      0.07 * consent_alignment +
      0.05 * participant_coverage,
    bias_risk =
      0.26 * missingness_risk +
      0.22 * (1 - representativeness) +
      0.18 * (1 - validation) +
      0.14 * ai_assistance_risk +
      0.10 * (1 - traceability) +
      0.10 * (1 - participant_coverage),
    ai_risk =
      0.38 * ai_assistance_risk +
      0.18 * (1 - traceability) +
      0.16 * (1 - validation) +
      0.14 * missingness_risk +
      0.14 * (1 - consent_alignment),
    decision_readiness = pmax(
      pmin(
        0.30 * confidence_score +
          0.24 * decision_relevance +
          0.14 * validation +
          0.12 * traceability +
          0.08 * consent_alignment +
          0.08 * participant_coverage -
          0.04 * bias_risk,
        1
      ),
      0
    ),
    governance_priority =
      0.24 * bias_risk +
      0.22 * ai_risk +
      0.16 * (1 - traceability) +
      0.14 * (1 - consent_alignment) +
      0.12 * (1 - validation) +
      0.12 * decision_relevance,
    review_action = case_when(
      bias_risk >= 0.50 ~ "review_bias_missingness_and_coverage",
      ai_risk >= 0.55 ~ "validate_ai_output_against_sources",
      consent_alignment < 0.60 ~ "review_consent_and_reuse_limits",
      confidence_score < 0.65 ~ "collect_or_validate_more_evidence",
      decision_readiness >= 0.75 ~ "ready_for_design_decision_review",
      TRUE ~ "use_as_directional_evidence"
    )
  ) %>%
  arrange(desc(governance_priority))

ai_scores <- ai_log %>%
  mutate(
    ai_governance_score = pmax(
      pmin(
        0.18 * source_grounding +
          0.18 * human_review +
          0.14 * output_reliability +
          0.14 * prompt_traceability +
          0.12 * model_version_recorded +
          0.12 * minority_signal_preservation -
          0.07 * sensitive_data_exposure -
          0.05 * hallucination_risk,
        1
      ),
      0
    ),
    ai_review_risk =
      0.22 * (1 - source_grounding) +
      0.20 * (1 - human_review) +
      0.16 * hallucination_risk +
      0.14 * sensitive_data_exposure +
      0.12 * (1 - prompt_traceability) +
      0.10 * (1 - minority_signal_preservation) +
      0.06 * (1 - model_version_recorded)
  ) %>%
  arrange(desc(ai_review_risk))

metadata_scores <- metadata %>%
  mutate(
    metadata_quality =
      0.18 * consent_recorded +
      0.13 * method_recorded +
      0.13 * participant_group_recorded +
      0.12 * limitations_recorded +
      0.12 * ai_use_recorded +
      0.12 * reviewer_recorded +
      0.10 * decision_link_recorded +
      0.10 * retention_rule_recorded,
    metadata_gap_count =
      8 - (
        consent_recorded +
          method_recorded +
          participant_group_recorded +
          limitations_recorded +
          ai_use_recorded +
          reviewer_recorded +
          decision_link_recorded +
          retention_rule_recorded
      )
  ) %>%
  arrange(metadata_quality)

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability * repair_difficulty,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(signal_scores, file.path(output_dir, "r_research_signal_scores.csv"))
readr::write_csv(ai_scores, file.path(output_dir, "r_ai_assistance_review_scores.csv"))
readr::write_csv(metadata_scores, file.path(output_dir, "r_metadata_registry_quality_scores.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_research_governance_risk_priority.csv"))

signal_plot <- signal_scores %>%
  ggplot(aes(x = reorder(signal, governance_priority), y = governance_priority)) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Research Evidence Governance Priority",
    x = "Research signal",
    y = "Governance priority"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_research_signal_governance_priority.png"),
  plot = signal_plot,
  width = 12,
  height = 7,
  dpi = 180
)

readiness_plot <- signal_scores %>%
  ggplot(aes(x = bias_risk, y = decision_readiness, size = confidence_score, label = signal)) +
  geom_point(alpha = 0.75) +
  geom_text(check_overlap = TRUE, vjust = -0.8, size = 3) +
  labs(
    title = "Decision Readiness vs Bias Risk",
    x = "Bias risk",
    y = "Decision readiness",
    size = "Confidence"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_research_signal_decision_readiness.png"),
  plot = readiness_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R AI-Assisted Research Evidence Analysis",
  "",
  "## Research signal scores",
  "",
  paste(capture.output(print(signal_scores)), collapse = "\n"),
  "",
  "## AI assistance review",
  "",
  paste(capture.output(print(ai_scores)), collapse = "\n"),
  "",
  "## Metadata registry quality",
  "",
  paste(capture.output(print(metadata_scores)), collapse = "\n"),
  "",
  "## Research governance risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_ai_research_evidence_report.md"))

message("R AI-assisted design research evidence analysis complete.")
message(paste("Outputs written to:", output_dir))
