#!/usr/bin/env Rscript

# Professional design-system intervention analysis in R.
#
# This workflow evaluates candidate interventions across human-centered value,
# systemic leverage, feasibility, equity sensitivity, durability, risk,
# evidence quality, stakeholder coverage, and feedback dynamics.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
portfolio_path <- file.path(article_dir, "data", "raw", "system_intervention_portfolio_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "system_design_scenario_weights.csv")
feedback_path <- file.path(article_dir, "data", "raw", "feedback_dynamics_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "system_intervention_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

portfolio <- readr::read_csv(portfolio_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
feedback <- readr::read_csv(feedback_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

leverage_depth <- function(level) {
  case_when(
    str_to_lower(level) == "parameter" ~ 1,
    str_to_lower(level) == "workflow" ~ 2,
    str_to_lower(level) == "information_flow" ~ 3,
    str_to_lower(level) == "feedback_loop" ~ 4,
    str_to_lower(level) == "rule" ~ 5,
    str_to_lower(level) == "infrastructure" ~ 5,
    str_to_lower(level) == "governance" ~ 6,
    str_to_lower(level) == "purpose" ~ 7,
    str_to_lower(level) == "paradigm" ~ 8,
    TRUE ~ 3
  )
}

score_interventions <- function(data, weights) {
  data %>%
    mutate(
      evidence_strength =
        0.55 * evidence_quality +
        0.45 * stakeholder_coverage,
      leverage_depth_score = leverage_depth(leverage_level),
      system_design_value =
        weights$human_value * human_value +
        weights$system_leverage * system_leverage +
        weights$feasibility * feasibility +
        weights$equity_sensitivity * equity_sensitivity +
        weights$durability * durability -
        weights$risk * risk,
      evidence_adjusted_value =
        system_design_value * (0.75 + 0.25 * evidence_strength),
      context_adjusted_value =
        system_design_value -
        0.10 * context_complexity -
        0.08 * delay_sensitivity * 10 -
        0.06 * burden_shift_risk,
      learning_priority =
        0.24 * risk +
        0.20 * (1 - evidence_quality) * 10 +
        0.18 * (1 - stakeholder_coverage) * 10 +
        0.14 * context_complexity +
        0.12 * delay_sensitivity * 10 +
        0.12 * burden_shift_risk,
      deep_leverage_index =
        0.35 * system_leverage +
        0.20 * leverage_depth_score +
        0.18 * durability +
        0.15 * equity_sensitivity +
        0.12 * evidence_strength * 10 -
        0.15 * risk
    ) %>%
    arrange(desc(system_design_value))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_interventions(portfolio, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(system_design_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

rank_stability <- scenario_results %>%
  group_by(intervention, intervention_type, leverage_level) %>%
  summarize(
    mean_rank = mean(rank),
    best_rank = min(rank),
    worst_rank = max(rank),
    rank_range = worst_rank - best_rank,
    mean_system_design_value = mean(system_design_value),
    mean_evidence_adjusted_value = mean(evidence_adjusted_value),
    mean_context_adjusted_value = mean(context_adjusted_value),
    mean_deep_leverage_index = mean(deep_leverage_index),
    mean_learning_priority = mean(learning_priority),
    .groups = "drop"
  ) %>%
  arrange(mean_rank, rank_range)

feedback_summary <- feedback %>%
  arrange(intervention, period) %>%
  group_by(intervention) %>%
  mutate(
    performance_delta = visible_performance - lag(visible_performance),
    burden_delta = system_burden - lag(system_burden),
    equity_gap_delta = equity_gap - lag(equity_gap),
    trust_delta = trust_score - lag(trust_score),
    queue_delta = queue_pressure - lag(queue_pressure),
    drift_delta = implementation_drift - lag(implementation_drift),
    feedback_quality_delta =
      0.28 * replace_na(performance_delta, 0) -
      0.18 * replace_na(burden_delta, 0) -
      0.18 * replace_na(equity_gap_delta, 0) * 10 +
      0.18 * replace_na(trust_delta, 0) -
      0.08 * replace_na(queue_delta, 0) * 10 -
      0.05 * replace_na(drift_delta, 0) * 10
  ) %>%
  summarize(
    periods = max(period),
    start_performance = first(visible_performance),
    final_performance = last(visible_performance),
    start_burden = first(system_burden),
    final_burden = last(system_burden),
    start_equity_gap = first(equity_gap),
    final_equity_gap = last(equity_gap),
    start_trust = first(trust_score),
    final_trust = last(trust_score),
    start_queue_pressure = first(queue_pressure),
    final_queue_pressure = last(queue_pressure),
    start_drift = first(implementation_drift),
    final_drift = last(implementation_drift),
    mean_adaptation_pressure = mean(adaptation_pressure),
    total_feedback_quality_delta = sum(feedback_quality_delta),
    .groups = "drop"
  ) %>%
  mutate(
    performance_improvement = final_performance - start_performance,
    burden_reduction = start_burden - final_burden,
    equity_gap_reduction = start_equity_gap - final_equity_gap,
    trust_improvement = final_trust - start_trust,
    queue_pressure_reduction = start_queue_pressure - final_queue_pressure,
    drift_increase = final_drift - start_drift
  ) %>%
  arrange(desc(total_feedback_quality_delta))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(scenario_results, file.path(output_dir, "r_system_design_scenario_results.csv"))
readr::write_csv(rank_stability, file.path(output_dir, "r_system_design_rank_stability.csv"))
readr::write_csv(feedback_summary, file.path(output_dir, "r_feedback_dynamics_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_system_intervention_risk_priority.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(intervention, system_design_value), y = system_design_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "System Design Value Across Strategic Scenarios",
    x = "Intervention",
    y = "Weighted system design value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_system_design_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Design-System Intervention Analysis",
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Rank stability",
  "",
  paste(capture.output(print(rank_stability)), collapse = "\n"),
  "",
  "## Feedback dynamics summary",
  "",
  paste(capture.output(print(feedback_summary)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_system_design_report.md"))

message("R design-system analysis complete.")
message(paste("Outputs written to:", output_dir))
