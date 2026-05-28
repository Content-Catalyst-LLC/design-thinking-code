#!/usr/bin/env Rscript

# Professional prototype portfolio scenario analysis in R.
#
# This workflow evaluates prototypes across learning gain, feasibility signal,
# user response, equity value, implementation relevance, and composite risk.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
portfolio_path <- file.path(article_dir, "data", "raw", "prototype_portfolio_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "prototype_scenario_weights.csv")
rounds_path <- file.path(article_dir, "data", "raw", "prototype_test_rounds_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "prototype_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

portfolio <- readr::read_csv(portfolio_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
rounds <- readr::read_csv(rounds_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

compute_composite_risk <- function(data) {
  0.30 * data$ethical_risk +
    0.30 * data$operational_risk +
    0.20 * data$technical_risk +
    0.20 * data$scaling_risk
}

score_prototypes <- function(data, weights) {
  data %>%
    mutate(
      composite_risk = compute_composite_risk(.),
      prototype_value =
        weights$learning_gain * learning_gain +
        weights$feasibility_signal * feasibility_signal +
        weights$user_response * user_response +
        weights$equity_value * equity_value +
        weights$implementation_relevance * implementation_relevance -
        weights$composite_risk * composite_risk,
      confidence_adjusted_value =
        prototype_value * (0.75 + 0.25 * evidence_quality),
      risk_adjusted_learning =
        learning_gain - 0.35 * composite_risk,
      prototype_review_priority =
        0.35 * composite_risk +
        0.20 * (10 - evidence_quality * 10) +
        0.20 * ethical_risk +
        0.15 * scaling_risk +
        0.10 * (10 - feasibility_signal),
      advance_readiness =
        0.30 * confidence_adjusted_value +
        0.25 * feasibility_signal +
        0.20 * implementation_relevance +
        0.15 * stakeholder_coverage * 10 -
        0.10 * composite_risk
    ) %>%
    arrange(desc(prototype_value))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_prototypes( portfolio, . ) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(prototype_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

rank_stability <- scenario_results %>%
  group_by(prototype, prototype_type, fidelity_level) %>%
  summarize(
    mean_rank = mean(rank),
    best_rank = min(rank),
    worst_rank = max(rank),
    rank_range = worst_rank - best_rank,
    mean_prototype_value = mean(prototype_value),
    mean_composite_risk = mean(composite_risk),
    mean_review_priority = mean(prototype_review_priority),
    .groups = "drop"
  ) %>%
  arrange(mean_rank, rank_range)

iteration_summary <- rounds %>%
  arrange(prototype, round) %>%
  group_by(prototype) %>%
  mutate(
    usability_delta = usability - lag(usability),
    comprehension_delta = comprehension - lag(comprehension),
    trust_delta = trust - lag(trust),
    friction_delta = unresolved_friction - lag(unresolved_friction),
    quality_delta =
      0.30 * replace_na(usability_delta, 0) +
      0.25 * replace_na(comprehension_delta, 0) +
      0.25 * replace_na(trust_delta, 0) -
      0.20 * replace_na(friction_delta, 0)
  ) %>%
  summarize(
    rounds = max(round),
    start_usability = first(usability),
    final_usability = last(usability),
    start_comprehension = first(comprehension),
    final_comprehension = last(comprehension),
    start_trust = first(trust),
    final_trust = last(trust),
    start_friction = first(unresolved_friction),
    final_friction = last(unresolved_friction),
    start_task_success = first(task_success_rate),
    final_task_success = last(task_success_rate),
    total_quality_delta = sum(quality_delta),
    participant_count = sum(participant_count),
    .groups = "drop"
  ) %>%
  mutate(
    usability_improvement = final_usability - start_usability,
    comprehension_improvement = final_comprehension - start_comprehension,
    trust_improvement = final_trust - start_trust,
    friction_reduction = start_friction - final_friction,
    task_success_improvement = final_task_success - start_task_success
  ) %>%
  arrange(desc(total_quality_delta))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(scenario_results, file.path(output_dir, "r_prototype_scenario_results.csv"))
readr::write_csv(rank_stability, file.path(output_dir, "r_prototype_rank_stability.csv"))
readr::write_csv(iteration_summary, file.path(output_dir, "r_prototype_iteration_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_prototype_risk_priority.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(prototype, prototype_value), y = prototype_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Prototype Value Across Learning Priority Scenarios",
    x = "Prototype",
    y = "Weighted prototype value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_prototype_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Prototype Portfolio Analysis",
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

writeLines(report, file.path(output_dir, "r_prototype_analysis_report.md"))

message("R prototype portfolio analysis complete.")
message(paste("Outputs written to:", output_dir))
