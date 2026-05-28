#!/usr/bin/env Rscript

# Professional organizational innovation analysis in R.
#
# This workflow evaluates innovation concepts across desirability,
# feasibility, viability, equity, learning value, implementation readiness,
# risk, evidence strength, stakeholder coverage, and organizational friction.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
concepts_path <- file.path(article_dir, "data", "raw", "organizational_innovation_concepts_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "innovation_scenario_weights.csv")
learning_path <- file.path(article_dir, "data", "raw", "prototype_learning_rounds_raw.csv")
friction_path <- file.path(article_dir, "data", "raw", "organizational_friction_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "innovation_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

concepts <- readr::read_csv(concepts_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
learning <- readr::read_csv(learning_path, show_col_types = FALSE)
friction <- readr::read_csv(friction_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

score_concepts <- function(data, weights) {
  data %>%
    mutate(
      evidence_strength =
        0.55 * evidence_quality +
        0.45 * stakeholder_coverage,
      design_value =
        weights$desirability * desirability +
        weights$feasibility * feasibility +
        weights$viability * viability +
        weights$equity * equity +
        weights$learning_value * learning_value +
        weights$implementation_readiness * implementation_readiness -
        weights$risk * risk,
      evidence_adjusted_value =
        design_value * (0.75 + 0.25 * evidence_strength),
      implementation_resilience =
        0.26 * implementation_readiness +
        0.22 * feasibility +
        0.18 * viability +
        0.16 * evidence_strength * 10 -
        0.09 * technical_complexity -
        0.09 * organizational_complexity,
      ethical_innovation_index =
        0.34 * equity +
        0.22 * stakeholder_coverage * 10 +
        0.18 * desirability +
        0.16 * learning_value -
        0.10 * ethical_risk,
      organizational_learning_index =
        0.30 * learning_value +
        0.22 * evidence_strength * 10 +
        0.18 * stakeholder_coverage * 10 +
        0.16 * implementation_readiness -
        0.07 * risk -
        0.07 * organizational_complexity,
      learning_priority =
        0.22 * risk +
        0.18 * technical_complexity +
        0.18 * organizational_complexity +
        0.16 * ethical_risk +
        0.14 * (1 - evidence_quality) * 10 +
        0.12 * (1 - stakeholder_coverage) * 10
    ) %>%
    arrange(desc(design_value))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_concepts(concepts, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(design_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

rank_stability <- scenario_results %>%
  group_by(concept, concept_type, organizational_domain) %>%
  summarize(
    mean_rank = mean(rank),
    best_rank = min(rank),
    worst_rank = max(rank),
    rank_range = worst_rank - best_rank,
    mean_design_value = mean(design_value),
    mean_evidence_adjusted_value = mean(evidence_adjusted_value),
    mean_implementation_resilience = mean(implementation_resilience),
    mean_ethical_innovation_index = mean(ethical_innovation_index),
    mean_organizational_learning_index = mean(organizational_learning_index),
    mean_learning_priority = mean(learning_priority),
    .groups = "drop"
  ) %>%
  arrange(mean_rank, rank_range)

prototype_learning_summary <- learning %>%
  arrange(concept, round) %>%
  group_by(concept) %>%
  mutate(
    adoption_delta = adoption_likelihood - lag(adoption_likelihood),
    friction_delta = user_friction - lag(user_friction),
    trust_delta = trust_score - lag(trust_score),
    burden_delta = operational_burden - lag(operational_burden),
    equity_delta = equity_score - lag(equity_score),
    task_success_delta = task_success_rate - lag(task_success_rate),
    cycle_time_delta = cycle_time - lag(cycle_time),
    employee_confidence_delta = employee_confidence - lag(employee_confidence),
    prototype_learning_delta =
      0.20 * replace_na(adoption_delta, 0) * 10 -
      0.16 * replace_na(friction_delta, 0) +
      0.16 * replace_na(trust_delta, 0) -
      0.14 * replace_na(burden_delta, 0) +
      0.14 * replace_na(equity_delta, 0) +
      0.10 * replace_na(task_success_delta, 0) * 10 -
      0.05 * replace_na(cycle_time_delta, 0) / 2 +
      0.05 * replace_na(employee_confidence_delta, 0)
  ) %>%
  summarize(
    rounds = max(round),
    start_adoption = first(adoption_likelihood),
    final_adoption = last(adoption_likelihood),
    start_friction = first(user_friction),
    final_friction = last(user_friction),
    start_trust = first(trust_score),
    final_trust = last(trust_score),
    start_burden = first(operational_burden),
    final_burden = last(operational_burden),
    start_equity = first(equity_score),
    final_equity = last(equity_score),
    start_task_success = first(task_success_rate),
    final_task_success = last(task_success_rate),
    start_cycle_time = first(cycle_time),
    final_cycle_time = last(cycle_time),
    start_employee_confidence = first(employee_confidence),
    final_employee_confidence = last(employee_confidence),
    total_prototype_learning_delta = sum(prototype_learning_delta),
    .groups = "drop"
  ) %>%
  mutate(
    adoption_gain = final_adoption - start_adoption,
    friction_reduction = start_friction - final_friction,
    trust_gain = final_trust - start_trust,
    burden_reduction = start_burden - final_burden,
    equity_gain = final_equity - start_equity,
    task_success_gain = final_task_success - start_task_success,
    cycle_time_reduction = start_cycle_time - final_cycle_time,
    employee_confidence_gain = final_employee_confidence - start_employee_confidence
  ) %>%
  arrange(desc(total_prototype_learning_delta))

friction_summary <- friction %>%
  mutate(
    coordination_friction_index =
      0.24 * silo_friction +
      0.24 * decision_latency +
      0.20 * ownership_ambiguity +
      0.16 * metric_misalignment +
      0.16 * governance_gap,
    implementation_friction_index =
      0.24 * legacy_system_constraint +
      0.22 * training_gap +
      0.22 * frontline_workload +
      0.18 * governance_gap +
      0.14 * decision_latency,
    total_friction_index =
      0.52 * coordination_friction_index +
      0.48 * implementation_friction_index,
    friction_attention_priority =
      0.30 * total_friction_index +
      0.20 * governance_gap +
      0.20 * ownership_ambiguity +
      0.15 * frontline_workload +
      0.15 * legacy_system_constraint
  ) %>%
  arrange(desc(friction_attention_priority))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(scenario_results, file.path(output_dir, "r_organizational_innovation_scenario_results.csv"))
readr::write_csv(rank_stability, file.path(output_dir, "r_organizational_innovation_rank_stability.csv"))
readr::write_csv(prototype_learning_summary, file.path(output_dir, "r_prototype_learning_summary.csv"))
readr::write_csv(friction_summary, file.path(output_dir, "r_organizational_friction_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_innovation_risk_priority.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(concept, design_value), y = design_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Organizational Innovation Value Across Strategic Scenarios",
    x = "Innovation concept",
    y = "Weighted design value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_organizational_innovation_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Organizational Innovation Analysis",
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Rank stability",
  "",
  paste(capture.output(print(rank_stability)), collapse = "\n"),
  "",
  "## Prototype learning summary",
  "",
  paste(capture.output(print(prototype_learning_summary)), collapse = "\n"),
  "",
  "## Organizational friction summary",
  "",
  paste(capture.output(print(friction_summary)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_organizational_innovation_report.md"))

message("R organizational innovation analysis complete.")
message(paste("Outputs written to:", output_dir))
