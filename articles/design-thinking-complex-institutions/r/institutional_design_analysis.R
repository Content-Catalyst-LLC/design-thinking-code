#!/usr/bin/env Rscript

# Professional institutional design-thinking portfolio analysis in R.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
options_path <- file.path(article_dir, "data", "raw", "institutional_design_options_raw.csv")
stakeholders_path <- file.path(article_dir, "data", "raw", "stakeholder_burden_raw.csv")
governance_path <- file.path(article_dir, "data", "raw", "governance_decision_rights_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "institutional_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

options <- readr::read_csv(options_path, show_col_types = FALSE)
stakeholders <- readr::read_csv(stakeholders_path, show_col_types = FALSE)
governance <- readr::read_csv(governance_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

option_scores <- options %>%
  mutate(
    change_readiness =
      0.14 * desirability +
      0.13 * authority +
      0.12 * capability +
      0.10 * funding +
      0.10 * policy_fit +
      0.11 * governance_strength +
      0.08 * trust_gain +
      0.08 * burden_reduction +
      0.06 * data_readiness +
      0.05 * frontline_fit +
      0.03 * maintenance_capacity -
      0.05 * coordination_complexity -
      0.05 * implementation_risk,
    absorption_capacity =
      0.18 * authority +
      0.18 * capability +
      0.14 * funding +
      0.14 * governance_strength +
      0.12 * policy_fit +
      0.10 * frontline_fit +
      0.08 * maintenance_capacity +
      0.06 * data_readiness,
    public_value_priority =
      0.24 * public_value +
      0.20 * burden_reduction +
      0.18 * trust_gain +
      0.16 * equity_priority +
      0.12 * desirability +
      0.10 * policy_fit -
      0.08 * implementation_risk,
    sequencing_need =
      0.28 * coordination_complexity +
      0.24 * implementation_risk +
      0.14 * (10 - authority) +
      0.12 * (10 - capability) +
      0.10 * (10 - funding) +
      0.07 * (10 - maintenance_capacity) +
      0.05 * (10 - data_readiness),
    portfolio_score =
      0.30 * change_readiness +
      0.26 * public_value_priority +
      0.20 * absorption_capacity +
      0.10 * equity_priority +
      0.06 * trust_gain -
      0.12 * sequencing_need -
      0.08 * implementation_risk,
    recommended_action = case_when(
      change_readiness >= 7.1 & absorption_capacity >= 6.6 ~ "scale_with_governance",
      public_value_priority >= 7.4 & absorption_capacity < 6.4 ~ "prototype_then_build_capacity",
      sequencing_need >= 7.2 ~ "sequence_after_governance_and_capability_work",
      implementation_risk >= 7.5 ~ "risk_review_before_pilot",
      TRUE ~ "pilot_with_learning_metrics"
    )
  ) %>%
  arrange(desc(portfolio_score))

stakeholder_scores <- stakeholders %>%
  mutate(
    burden_score =
      0.18 * time_burden +
      0.20 * cognitive_burden +
      0.17 * emotional_burden +
      0.17 * documentation_burden +
      0.16 * uncertainty_burden +
      0.12 * coordination_burden,
    power_gap = 10 - (0.40 * voice + 0.36 * influence + 0.24 * repair_access),
    accessibility_burden = accessibility_need * burden_score,
    institutional_attention_priority =
      0.26 * affectedness * burden_score +
      0.22 * affectedness * power_gap +
      0.16 * trust_gap +
      0.14 * accessibility_burden +
      0.12 * emotional_burden +
      0.10 * uncertainty_burden
  ) %>%
  arrange(desc(institutional_attention_priority))

governance_scores <- governance %>%
  mutate(
    decision_rights_strength =
      0.16 * approval_authority +
      0.13 * budget_authority +
      0.13 * policy_authority +
      0.12 * data_authority +
      0.15 * implementation_authority +
      0.10 * community_accountability +
      0.08 * escalation_clarity +
      0.07 * review_cadence +
      0.06 * maintenance_ownership,
    governance_gap = 1 - decision_rights_strength
  ) %>%
  arrange(desc(governance_gap))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability * repair_difficulty,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(option_scores, file.path(output_dir, "r_institutional_design_option_scores.csv"))
readr::write_csv(stakeholder_scores, file.path(output_dir, "r_stakeholder_burden_attention_scores.csv"))
readr::write_csv(governance_scores, file.path(output_dir, "r_governance_decision_rights_scores.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_institutional_risk_priority.csv"))

portfolio_plot <- option_scores %>%
  ggplot(aes(x = reorder(option, portfolio_score), y = portfolio_score)) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Institutional Design Portfolio Score",
    x = "Institutional design option",
    y = "Portfolio score"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_institutional_design_portfolio_score.png"),
  plot = portfolio_plot,
  width = 12,
  height = 7,
  dpi = 180
)

absorption_plot <- option_scores %>%
  ggplot(aes(x = absorption_capacity, y = public_value_priority, size = burden_reduction, label = option)) +
  geom_point(alpha = 0.75) +
  geom_text(check_overlap = TRUE, vjust = -0.8, size = 3) +
  labs(
    title = "Institutional Absorption Capacity vs Public Value",
    x = "Absorption capacity",
    y = "Public value priority",
    size = "Burden reduction"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_absorption_capacity_public_value.png"),
  plot = absorption_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Institutional Design Analysis",
  "",
  "## Institutional design option scores",
  "",
  paste(capture.output(print(option_scores)), collapse = "\n"),
  "",
  "## Stakeholder burden scores",
  "",
  paste(capture.output(print(stakeholder_scores)), collapse = "\n"),
  "",
  "## Governance decision-rights scores",
  "",
  paste(capture.output(print(governance_scores)), collapse = "\n"),
  "",
  "## Institutional risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_institutional_design_report.md"))

message("R institutional design analysis complete.")
message(paste("Outputs written to:", output_dir))
