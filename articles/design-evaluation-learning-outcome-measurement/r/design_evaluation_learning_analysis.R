#!/usr/bin/env Rscript

# Professional design evaluation, learning, and outcome-measurement analysis in R.
#
# This workflow evaluates interventions across outcome improvement,
# burden reduction, equity performance, trust improvement, durability,
# operational cost, residual risk, evidence strength, and learning priority.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
portfolio_path <- file.path(article_dir, "data", "raw", "evaluation_portfolio_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "evaluation_scenario_weights.csv")
outcomes_path <- file.path(article_dir, "data", "raw", "outcome_timeseries_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "evaluation_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

portfolio <- readr::read_csv(portfolio_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
outcomes <- readr::read_csv(outcomes_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

score_interventions <- function(data, weights) {
  data %>%
    mutate(
      penalty = 0.50 * operational_cost + 0.50 * residual_risk,
      quality_delta = current_quality - baseline_quality,
      evaluation_value =
        weights$outcome_improvement * outcome_improvement +
        weights$burden_reduction * burden_reduction +
        weights$equity_performance * equity_performance +
        weights$trust_improvement * trust_improvement +
        weights$durability * durability -
        weights$penalty * penalty,
      evidence_strength =
        pmax(
          pmin(
            0.40 * evidence_quality +
            0.35 * stakeholder_coverage +
            0.25 * method_triangulation -
            0.20 * uncertainty,
            1
          ),
          0
        ),
      evidence_adjusted_value =
        evaluation_value * (0.75 + 0.25 * evidence_strength),
      learning_priority =
        0.25 * residual_risk +
        0.20 * (1 - evidence_quality) * 10 +
        0.18 * (1 - stakeholder_coverage) * 10 +
        0.16 * operational_cost +
        0.13 * (1 - method_triangulation) * 10 +
        0.08 * uncertainty * 10,
      accountability_index =
        0.25 * equity_performance +
        0.20 * trust_improvement +
        0.20 * evidence_strength * 10 +
        0.20 * burden_reduction +
        0.15 * durability -
        0.10 * penalty
    ) %>%
    arrange(desc(evaluation_value))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_interventions(portfolio, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(evaluation_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

rank_stability <- scenario_results %>%
  group_by(intervention, intervention_type, evaluation_stage) %>%
  summarize(
    mean_rank = mean(rank),
    best_rank = min(rank),
    worst_rank = max(rank),
    rank_range = worst_rank - best_rank,
    mean_evaluation_value = mean(evaluation_value),
    mean_evidence_adjusted_value = mean(evidence_adjusted_value),
    mean_learning_priority = mean(learning_priority),
    mean_accountability_index = mean(accountability_index),
    .groups = "drop"
  ) %>%
  arrange(mean_rank, rank_range)

outcome_summary <- outcomes %>%
  arrange(intervention, period) %>%
  group_by(intervention) %>%
  mutate(
    outcome_delta = outcome_score - lag(outcome_score),
    burden_delta = burden_score - lag(burden_score),
    equity_gap_delta = equity_gap - lag(equity_gap),
    trust_delta = trust_score - lag(trust_score),
    reliability_delta = reliability_score - lag(reliability_score),
    staff_burden_delta = staff_burden - lag(staff_burden),
    ticket_delta = support_ticket_rate - lag(support_ticket_rate),
    complaint_delta = complaint_rate - lag(complaint_rate),
    learning_quality_delta =
      0.25 * replace_na(outcome_delta, 0) -
      0.18 * replace_na(burden_delta, 0) -
      0.18 * replace_na(equity_gap_delta, 0) * 10 +
      0.18 * replace_na(trust_delta, 0) +
      0.13 * replace_na(reliability_delta, 0) * 10 -
      0.04 * replace_na(staff_burden_delta, 0) -
      0.02 * replace_na(ticket_delta, 0) * 10 -
      0.02 * replace_na(complaint_delta, 0) * 10
  ) %>%
  summarize(
    periods = max(period),
    start_outcome = first(outcome_score),
    final_outcome = last(outcome_score),
    start_burden = first(burden_score),
    final_burden = last(burden_score),
    start_equity_gap = first(equity_gap),
    final_equity_gap = last(equity_gap),
    start_trust = first(trust_score),
    final_trust = last(trust_score),
    start_reliability = first(reliability_score),
    final_reliability = last(reliability_score),
    start_staff_burden = first(staff_burden),
    final_staff_burden = last(staff_burden),
    start_ticket_rate = first(support_ticket_rate),
    final_ticket_rate = last(support_ticket_rate),
    start_complaint_rate = first(complaint_rate),
    final_complaint_rate = last(complaint_rate),
    final_users_reached = last(users_reached),
    total_learning_quality_delta = sum(learning_quality_delta),
    .groups = "drop"
  ) %>%
  mutate(
    outcome_improvement = final_outcome - start_outcome,
    burden_reduction = start_burden - final_burden,
    equity_gap_reduction = start_equity_gap - final_equity_gap,
    trust_improvement = final_trust - start_trust,
    reliability_improvement = final_reliability - start_reliability,
    staff_burden_reduction = start_staff_burden - final_staff_burden,
    support_ticket_reduction = start_ticket_rate - final_ticket_rate,
    complaint_reduction = start_complaint_rate - final_complaint_rate
  ) %>%
  arrange(desc(total_learning_quality_delta))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(scenario_results, file.path(output_dir, "r_evaluation_scenario_results.csv"))
readr::write_csv(rank_stability, file.path(output_dir, "r_evaluation_rank_stability.csv"))
readr::write_csv(outcome_summary, file.path(output_dir, "r_outcome_learning_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_evaluation_risk_priority.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(intervention, evaluation_value), y = evaluation_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Design Evaluation Value Across Learning Scenarios",
    x = "Intervention",
    y = "Weighted evaluation value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_evaluation_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Design Evaluation and Learning Analysis",
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Rank stability",
  "",
  paste(capture.output(print(rank_stability)), collapse = "\n"),
  "",
  "## Outcome learning summary",
  "",
  paste(capture.output(print(outcome_summary)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_design_evaluation_learning_report.md"))

message("R design evaluation and learning analysis complete.")
message(paste("Outputs written to:", output_dir))
