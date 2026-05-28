#!/usr/bin/env Rscript

# Professional design-thinking strategy analysis in R.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
options_path <- file.path(article_dir, "data", "raw", "strategic_options_raw.csv")
assumptions_path <- file.path(article_dir, "data", "raw", "strategic_assumptions_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "strategy_scenario_weights.csv")
risk_path <- file.path(article_dir, "data", "raw", "strategy_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

options <- readr::read_csv(options_path, show_col_types = FALSE)
assumptions <- readr::read_csv(assumptions_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

score_options <- function(data, weights) {
  data %>%
    mutate(
      strategic_score =
        weights$desirability * desirability +
        weights$feasibility * feasibility +
        weights$viability * viability +
        weights$strategic_alignment * strategic_alignment +
        weights$ethical_quality * ethical_quality +
        weights$learning_value * learning_value +
        weights$public_value * public_value +
        weights$evidence_strength * evidence_strength * 10 -
        weights$strategic_risk * strategic_risk -
        weights$implementation_effort * implementation_effort -
        weights$capability_gap * capability_gap -
        weights$time_to_learn * time_to_learn,
      portfolio_value =
        strategic_score +
        0.30 * learning_value +
        0.20 * public_value +
        0.15 * evidence_strength * 10 -
        0.22 * strategic_risk -
        0.14 * implementation_effort -
        0.10 * capability_gap,
      uncertainty_priority =
        0.26 * strategic_risk +
        0.22 * learning_value +
        0.16 * implementation_effort +
        0.14 * capability_gap +
        0.12 * (10 - feasibility) +
        0.10 * (1 - evidence_strength) * 10,
      implementation_readiness =
        0.28 * feasibility +
        0.24 * viability +
        0.20 * (10 - implementation_effort) +
        0.16 * (10 - capability_gap) +
        0.12 * evidence_strength * 10,
      ethical_public_value_index =
        0.42 * ethical_quality +
        0.38 * public_value +
        0.12 * strategic_alignment -
        0.08 * strategic_risk,
      portfolio_role = case_when(
        strategic_score >= 7.4 & strategic_risk <= 5.0 & implementation_readiness >= 6.8 ~ "scale_or_commit",
        learning_value >= 8.2 & strategic_risk >= 5.0 ~ "prototype_and_learn",
        ethical_public_value_index >= 8.0 ~ "public_value_or_legitimacy_bet",
        capability_gap >= 6.2 | implementation_effort >= 7.2 ~ "capability_required",
        TRUE ~ "sequence_after_learning"
      )
    ) %>%
    arrange(desc(strategic_score))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_options(options, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(strategic_score), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

balanced_scores <- scenario_results %>%
  filter(scenario == "Balanced")

portfolio_summary <- balanced_scores %>%
  group_by(portfolio_role) %>%
  summarize(
    options = n(),
    mean_strategic_score = mean(strategic_score),
    mean_portfolio_value = mean(portfolio_value),
    mean_learning_value = mean(learning_value),
    mean_risk = mean(strategic_risk),
    mean_implementation_readiness = mean(implementation_readiness),
    .groups = "drop"
  ) %>%
  arrange(desc(mean_portfolio_value))

assumption_scores <- assumptions %>%
  mutate(
    uncertainty_load = importance * (1 - confidence),
    test_priority =
      0.34 * uncertainty_load +
      0.22 * ethical_sensitivity +
      0.18 * importance -
      0.14 * test_cost -
      0.12 * (time_to_test / 10),
    evidence_gap = pmax(decision_threshold - confidence, 0)
  ) %>%
  arrange(desc(test_priority))

assumption_summary <- assumption_scores %>%
  group_by(option) %>%
  summarize(
    assumptions_count = n(),
    mean_importance = mean(importance),
    mean_confidence = mean(confidence),
    total_uncertainty_load = sum(uncertainty_load),
    mean_test_priority = mean(test_priority),
    max_ethical_sensitivity = max(ethical_sensitivity),
    mean_evidence_gap = mean(evidence_gap),
    .groups = "drop"
  ) %>%
  arrange(desc(total_uncertainty_load))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(scenario_results, file.path(output_dir, "r_strategy_option_scenario_results.csv"))
readr::write_csv(balanced_scores, file.path(output_dir, "r_strategy_option_balanced_scores.csv"))
readr::write_csv(portfolio_summary, file.path(output_dir, "r_strategy_portfolio_summary.csv"))
readr::write_csv(assumption_scores, file.path(output_dir, "r_strategic_assumption_test_priorities.csv"))
readr::write_csv(assumption_summary, file.path(output_dir, "r_strategic_assumption_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_strategy_risk_priority.csv"))

portfolio_plot <- balanced_scores %>%
  ggplot(aes(x = implementation_effort, y = strategic_score, size = learning_value, label = option)) +
  geom_point(alpha = 0.75) +
  geom_text(check_overlap = TRUE, vjust = -0.8, size = 3) +
  labs(
    title = "Strategic Option Portfolio",
    x = "Implementation effort",
    y = "Strategic score",
    size = "Learning value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_strategy_portfolio_plot.png"),
  plot = portfolio_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Design Thinking and Strategy Analysis",
  "",
  "## Balanced strategic option scores",
  "",
  paste(capture.output(print(balanced_scores)), collapse = "\n"),
  "",
  "## Portfolio summary",
  "",
  paste(capture.output(print(portfolio_summary)), collapse = "\n"),
  "",
  "## Strategic assumption priorities",
  "",
  paste(capture.output(print(assumption_scores)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_strategy_design_report.md"))

message("R strategy analysis complete.")
message(paste("Outputs written to:", output_dir))
