#!/usr/bin/env Rscript

# Professional public-value and social-impact portfolio analysis in R.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
interventions_path <- file.path(article_dir, "data", "raw", "social_impact_interventions_raw.csv")
stakeholders_path <- file.path(article_dir, "data", "raw", "stakeholder_burden_public_value_raw.csv")
participation_path <- file.path(article_dir, "data", "raw", "participation_quality_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "social_impact_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

interventions <- readr::read_csv(interventions_path, show_col_types = FALSE)
stakeholders <- readr::read_csv(stakeholders_path, show_col_types = FALSE)
participation <- readr::read_csv(participation_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

intervention_scores <- interventions %>%
  mutate(
    public_value_score =
      0.13 * access +
      0.15 * equity +
      0.12 * dignity +
      0.12 * legitimacy +
      0.13 * accountability +
      0.11 * outcome_strength +
      0.08 * sustainability +
      0.07 * learning_capacity +
      0.05 * community_defined_value +
      0.04 * repair_capacity,
    impact_readiness =
      0.30 * public_value_score +
      0.17 * feasibility +
      0.16 * governance_strength +
      0.12 * learning_capacity +
      0.10 * participation_quality +
      0.08 * stewardship_capacity +
      0.07 * repair_capacity -
      0.07 * implementation_risk -
      0.07 * burden_risk,
    stewardship_need =
      0.24 * implementation_risk +
      0.22 * burden_risk +
      0.16 * (10 - governance_strength) +
      0.12 * (10 - sustainability) +
      0.10 * (10 - learning_capacity) +
      0.08 * (10 - repair_capacity) +
      0.08 * (10 - stewardship_capacity),
    portfolio_priority =
      0.36 * public_value_score +
      0.28 * impact_readiness +
      0.14 * equity +
      0.10 * community_defined_value +
      0.06 * participation_quality -
      0.14 * stewardship_need -
      0.06 * implementation_risk,
    recommended_action = case_when(
      public_value_score >= 8.2 & impact_readiness >= 7.2 ~ "pilot_with_public_learning",
      public_value_score >= 8.2 & impact_readiness < 7.2 ~ "build_governance_before_pilot",
      stewardship_need >= 6.6 ~ "risk_and_stewardship_review",
      burden_risk >= 6.8 ~ "burden_safeguards_required",
      participation_quality < 6.2 ~ "strengthen_participation_before_pilot",
      feasibility >= 7.5 & public_value_score >= 7.6 ~ "implement_with_evaluation",
      TRUE ~ "develop_evidence_and_participation"
    )
  ) %>%
  arrange(desc(portfolio_priority))

stakeholder_scores <- stakeholders %>%
  mutate(
    baseline_burden =
      0.20 * baseline_time_burden +
      0.22 * baseline_cognitive_burden +
      0.20 * baseline_emotional_burden +
      0.20 * baseline_documentation_burden +
      0.18 * baseline_uncertainty_burden,
    post_burden =
      0.20 * post_time_burden +
      0.22 * post_cognitive_burden +
      0.20 * post_emotional_burden +
      0.20 * post_documentation_burden +
      0.18 * post_uncertainty_burden,
    burden_reduction = baseline_burden - post_burden,
    power_gap = 10 - (0.40 * voice + 0.36 * influence + 0.24 * repair_access),
    accessibility_burden = accessibility_need * baseline_burden,
    public_value_attention_priority =
      0.24 * affectedness * baseline_burden +
      0.20 * affectedness * power_gap +
      0.16 * trust_gap +
      0.14 * accessibility_burden +
      0.14 * (10 - repair_access) -
      0.12 * burden_reduction
  ) %>%
  arrange(desc(public_value_attention_priority))

participation_scores <- participation %>%
  mutate(
    participation_quality_score =
      0.14 * affected_people_involved +
      0.16 * decision_influence +
      0.10 * compensation +
      0.10 * accessibility_support +
      0.08 * language_support +
      0.10 * feedback_loop +
      0.13 * community_ownership +
      0.15 * power_sharing +
      0.07 * documentation_quality +
      0.07 * ethical_review,
    participation_gap = 1 - participation_quality_score
  ) %>%
  arrange(desc(participation_gap))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability * repair_difficulty,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(intervention_scores, file.path(output_dir, "r_social_impact_intervention_scores.csv"))
readr::write_csv(stakeholder_scores, file.path(output_dir, "r_stakeholder_burden_public_value_scores.csv"))
readr::write_csv(participation_scores, file.path(output_dir, "r_participation_quality_scores.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_social_impact_risk_priority.csv"))

portfolio_plot <- intervention_scores %>%
  ggplot(aes(x = reorder(intervention, portfolio_priority), y = portfolio_priority)) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Social Impact Public-Value Portfolio Priority",
    x = "Intervention",
    y = "Portfolio priority"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_social_impact_portfolio_priority.png"),
  plot = portfolio_plot,
  width = 12,
  height = 7,
  dpi = 180
)

readiness_plot <- intervention_scores %>%
  ggplot(aes(x = stewardship_need, y = impact_readiness, size = public_value_score, label = intervention)) +
  geom_point(alpha = 0.75) +
  geom_text(check_overlap = TRUE, vjust = -0.8, size = 3) +
  labs(
    title = "Impact Readiness vs Stewardship Need",
    x = "Stewardship need",
    y = "Impact readiness",
    size = "Public value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_impact_readiness_stewardship_need.png"),
  plot = readiness_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Public-Value Social Impact Analysis",
  "",
  "## Social impact intervention scores",
  "",
  paste(capture.output(print(intervention_scores)), collapse = "\n"),
  "",
  "## Stakeholder burden and public-value attention scores",
  "",
  paste(capture.output(print(stakeholder_scores)), collapse = "\n"),
  "",
  "## Participation-quality scores",
  "",
  paste(capture.output(print(participation_scores)), collapse = "\n"),
  "",
  "## Social impact risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_public_value_impact_report.md"))

message("R public-value social impact analysis complete.")
message(paste("Outputs written to:", output_dir))
