#!/usr/bin/env Rscript

# Professional implementation and scaling analysis in R.
#
# This workflow evaluates interventions across adoption readiness,
# operational fit, durability, governance readiness, equity readiness,
# financial sustainability, composite risk, and rollout-stage learning.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
portfolio_path <- file.path(article_dir, "data", "raw", "implementation_portfolio_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "implementation_scenario_weights.csv")
rollout_path <- file.path(article_dir, "data", "raw", "rollout_stage_metrics_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "implementation_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

portfolio <- readr::read_csv(portfolio_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
rollout <- readr::read_csv(rollout_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

score_interventions <- function(data, weights) {
  data %>%
    mutate(
      composite_risk =
        0.25 * operational_risk +
        0.22 * governance_risk +
        0.18 * technical_risk +
        0.22 * equity_risk +
        0.13 * financial_risk,
      implementation_value =
        weights$adoption_readiness * adoption_readiness +
        weights$operational_fit * operational_fit +
        weights$durability * durability +
        weights$governance_readiness * governance_readiness +
        weights$equity_readiness * equity_readiness +
        weights$financial_sustainability * financial_sustainability -
        weights$composite_risk * composite_risk,
      evidence_adjusted_value =
        implementation_value * (0.75 + 0.15 * evidence_quality + 0.10 * stakeholder_coverage),
      scaled_quality_estimate =
        implementation_value - scale_sensitivity * context_complexity,
      implementation_review_priority =
        0.28 * composite_risk +
        0.18 * (10 - governance_readiness) +
        0.18 * (10 - equity_readiness) +
        0.14 * (10 - financial_sustainability) +
        0.12 * context_complexity +
        0.10 * (1 - evidence_quality) * 10
    ) %>%
    arrange(desc(implementation_value))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_interventions(portfolio, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(implementation_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

rank_stability <- scenario_results %>%
  group_by(intervention, intervention_type, implementation_stage) %>%
  summarize(
    mean_rank = mean(rank),
    best_rank = min(rank),
    worst_rank = max(rank),
    rank_range = worst_rank - best_rank,
    mean_implementation_value = mean(implementation_value),
    mean_scaled_quality_estimate = mean(scaled_quality_estimate),
    mean_review_priority = mean(implementation_review_priority),
    .groups = "drop"
  ) %>%
  arrange(mean_rank, rank_range)

rollout_summary <- rollout %>%
  arrange(intervention, stage) %>%
  group_by(intervention) %>%
  mutate(
    adoption_delta = adoption_rate - lag(adoption_rate),
    compliance_delta = staff_compliance - lag(staff_compliance),
    reliability_delta = service_reliability - lag(service_reliability),
    ticket_delta = support_ticket_rate - lag(support_ticket_rate),
    equity_gap_delta = equity_gap - lag(equity_gap),
    trust_delta = user_trust - lag(user_trust),
    burden_delta = staff_burden - lag(staff_burden),
    incident_delta = incident_count - lag(incident_count),
    rollout_learning_delta =
      0.20 * replace_na(adoption_delta, 0) * 10 +
      0.18 * replace_na(compliance_delta, 0) * 10 +
      0.18 * replace_na(reliability_delta, 0) * 10 -
      0.14 * replace_na(ticket_delta, 0) * 10 -
      0.12 * replace_na(equity_gap_delta, 0) * 10 +
      0.12 * replace_na(trust_delta, 0) -
      0.06 * replace_na(burden_delta, 0) -
      0.10 * replace_na(incident_delta, 0)
  ) %>%
  summarize(
    stages = max(stage),
    start_adoption = first(adoption_rate),
    final_adoption = last(adoption_rate),
    start_staff_compliance = first(staff_compliance),
    final_staff_compliance = last(staff_compliance),
    start_reliability = first(service_reliability),
    final_reliability = last(service_reliability),
    start_ticket_rate = first(support_ticket_rate),
    final_ticket_rate = last(support_ticket_rate),
    start_equity_gap = first(equity_gap),
    final_equity_gap = last(equity_gap),
    start_user_trust = first(user_trust),
    final_user_trust = last(user_trust),
    start_staff_burden = first(staff_burden),
    final_staff_burden = last(staff_burden),
    start_incidents = first(incident_count),
    final_incidents = last(incident_count),
    final_sites_live = last(sites_live),
    final_users_reached = last(users_reached),
    total_rollout_learning_delta = sum(rollout_learning_delta),
    .groups = "drop"
  ) %>%
  mutate(
    adoption_improvement = final_adoption - start_adoption,
    staff_compliance_improvement = final_staff_compliance - start_staff_compliance,
    reliability_improvement = final_reliability - start_reliability,
    support_ticket_reduction = start_ticket_rate - final_ticket_rate,
    equity_gap_reduction = start_equity_gap - final_equity_gap,
    trust_improvement = final_user_trust - start_user_trust,
    staff_burden_reduction = start_staff_burden - final_staff_burden,
    incident_reduction = start_incidents - final_incidents
  ) %>%
  arrange(desc(total_rollout_learning_delta))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(scenario_results, file.path(output_dir, "r_implementation_scenario_results.csv"))
readr::write_csv(rank_stability, file.path(output_dir, "r_implementation_rank_stability.csv"))
readr::write_csv(rollout_summary, file.path(output_dir, "r_rollout_stage_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_implementation_risk_priority.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(intervention, implementation_value), y = implementation_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Implementation Value Across Strategic Scenarios",
    x = "Intervention",
    y = "Weighted implementation value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_implementation_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Implementation and Scaling Analysis",
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Rank stability",
  "",
  paste(capture.output(print(rank_stability)), collapse = "\n"),
  "",
  "## Rollout summary",
  "",
  paste(capture.output(print(rollout_summary)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_implementation_scaling_report.md"))

message("R implementation and scaling analysis complete.")
message(paste("Outputs written to:", output_dir))
