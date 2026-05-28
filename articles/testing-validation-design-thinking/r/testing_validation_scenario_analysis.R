#!/usr/bin/env Rscript

# Professional testing and validation scenario analysis in R.
#
# This workflow evaluates tested concepts across desirability, feasibility,
# viability, responsibility, friction, residual risk, evidence quality,
# stakeholder coverage, and validation review priority.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
concepts_path <- file.path(article_dir, "data", "raw", "validation_concepts_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "validation_scenario_weights.csv")
rounds_path <- file.path(article_dir, "data", "raw", "testing_rounds_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "validation_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

concepts <- readr::read_csv(concepts_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
rounds <- readr::read_csv(rounds_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

score_concepts <- function(data, weights) {
  data %>%
    mutate(
      combined_risk = 0.50 * friction + 0.50 * residual_risk,
      validation_value =
        weights$desirability * desirability +
        weights$feasibility * feasibility +
        weights$viability * viability +
        weights$responsibility * responsibility -
        weights$risk_penalty * combined_risk,
      evidence_confidence_index =
        0.45 * evidence_quality +
        0.35 * stakeholder_coverage +
        0.20 * method_triangulation,
      confidence_adjusted_value =
        validation_value * (0.75 + 0.25 * evidence_confidence_index),
      equity_access_index =
        0.50 * equity_signal +
        0.35 * accessibility_signal +
        0.15 * stakeholder_coverage * 10,
      validation_review_priority =
        0.30 * residual_risk +
        0.25 * friction +
        0.15 * (1 - evidence_quality) * 10 +
        0.15 * (1 - stakeholder_coverage) * 10 +
        0.15 * (10 - responsibility)
    ) %>%
    arrange(desc(validation_value))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_concepts(concepts, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(validation_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

rank_stability <- scenario_results %>%
  group_by(concept, prototype_type, fidelity_level) %>%
  summarize(
    mean_rank = mean(rank),
    best_rank = min(rank),
    worst_rank = max(rank),
    rank_range = worst_rank - best_rank,
    mean_validation_value = mean(validation_value),
    mean_confidence_adjusted_value = mean(confidence_adjusted_value),
    mean_review_priority = mean(validation_review_priority),
    .groups = "drop"
  ) %>%
  arrange(mean_rank, rank_range)

iteration_summary <- rounds %>%
  arrange(concept, round) %>%
  group_by(concept) %>%
  mutate(
    adoption_delta = adoption_likelihood - lag(adoption_likelihood),
    comprehension_delta = comprehension - lag(comprehension),
    trust_delta = trust - lag(trust),
    friction_delta = observed_friction - lag(observed_friction),
    learning_quality_delta =
      0.25 * replace_na(adoption_delta, 0) +
      0.25 * replace_na(comprehension_delta, 0) +
      0.25 * replace_na(trust_delta, 0) -
      0.20 * replace_na(friction_delta, 0) -
      0.05 * replace_na(critical_issue_count - lag(critical_issue_count), 0)
  ) %>%
  summarize(
    rounds = max(round),
    start_adoption = first(adoption_likelihood),
    final_adoption = last(adoption_likelihood),
    start_comprehension = first(comprehension),
    final_comprehension = last(comprehension),
    start_trust = first(trust),
    final_trust = last(trust),
    start_friction = first(observed_friction),
    final_friction = last(observed_friction),
    start_task_success = first(task_success_rate),
    final_task_success = last(task_success_rate),
    start_error_rate = first(error_rate),
    final_error_rate = last(error_rate),
    start_critical_issues = first(critical_issue_count),
    final_critical_issues = last(critical_issue_count),
    total_learning_quality_delta = sum(learning_quality_delta),
    participant_count = sum(participant_count),
    .groups = "drop"
  ) %>%
  mutate(
    adoption_improvement = final_adoption - start_adoption,
    comprehension_improvement = final_comprehension - start_comprehension,
    trust_improvement = final_trust - start_trust,
    friction_reduction = start_friction - final_friction,
    task_success_improvement = final_task_success - start_task_success,
    error_reduction = start_error_rate - final_error_rate,
    critical_issue_reduction = start_critical_issues - final_critical_issues
  ) %>%
  arrange(desc(total_learning_quality_delta))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(scenario_results, file.path(output_dir, "r_validation_scenario_results.csv"))
readr::write_csv(rank_stability, file.path(output_dir, "r_validation_rank_stability.csv"))
readr::write_csv(iteration_summary, file.path(output_dir, "r_testing_iteration_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_validation_risk_priority.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(concept, validation_value), y = validation_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Validation Value Across Testing Scenarios",
    x = "Concept",
    y = "Weighted validation value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_validation_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Testing and Validation Analysis",
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Rank stability",
  "",
  paste(capture.output(print(rank_stability)), collapse = "\n"),
  "",
  "## Iteration summary",
  "",
  paste(capture.output(print(iteration_summary)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_testing_validation_report.md"))

message("R testing and validation analysis complete.")
message(paste("Outputs written to:", output_dir))
