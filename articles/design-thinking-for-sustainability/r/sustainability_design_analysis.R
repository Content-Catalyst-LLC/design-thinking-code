#!/usr/bin/env Rscript

# Professional sustainability design analysis in R.
#
# This workflow evaluates sustainability concepts across usability,
# feasibility, ecological benefit, circularity, equity, durability, risk,
# evidence strength, lifecycle boundary quality, and transition learning.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
concepts_path <- file.path(article_dir, "data", "raw", "sustainability_concepts_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "sustainability_scenario_weights.csv")
transitions_path <- file.path(article_dir, "data", "raw", "transition_pathways_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "sustainability_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

concepts <- readr::read_csv(concepts_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
transitions <- readr::read_csv(transitions_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

score_concepts <- function(data, weights) {
  data %>%
    mutate(
      evidence_strength =
        0.35 * evidence_quality +
        0.30 * stakeholder_coverage +
        0.35 * lifecycle_boundary_quality,
      sustainability_value =
        weights$usability * usability +
        weights$feasibility * feasibility +
        weights$ecological_benefit * ecological_benefit +
        weights$circularity * circularity +
        weights$equity * equity +
        weights$durability * durability -
        weights$risk * risk,
      evidence_adjusted_value =
        sustainability_value * (0.75 + 0.25 * evidence_strength),
      transition_readiness =
        0.24 * usability +
        0.22 * feasibility +
        0.18 * stakeholder_coverage * 10 +
        0.18 * durability +
        0.18 * evidence_strength * 10 -
        0.12 * implementation_complexity,
      ecological_integrity_index =
        0.40 * ecological_benefit +
        0.25 * circularity +
        0.20 * lifecycle_boundary_quality * 10 +
        0.15 * durability -
        0.12 * risk,
      justice_burden_index =
        0.40 * equity +
        0.25 * stakeholder_coverage * 10 +
        0.20 * usability -
        0.15 * burden_shift_risk,
      learning_priority =
        0.22 * risk +
        0.18 * implementation_complexity +
        0.17 * burden_shift_risk +
        0.16 * (1 - evidence_quality) * 10 +
        0.14 * (1 - stakeholder_coverage) * 10 +
        0.13 * (1 - lifecycle_boundary_quality) * 10
    ) %>%
    arrange(desc(sustainability_value))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_concepts(concepts, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(sustainability_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

rank_stability <- scenario_results %>%
  group_by(concept, concept_type, transition_domain) %>%
  summarize(
    mean_rank = mean(rank),
    best_rank = min(rank),
    worst_rank = max(rank),
    rank_range = worst_rank - best_rank,
    mean_sustainability_value = mean(sustainability_value),
    mean_evidence_adjusted_value = mean(evidence_adjusted_value),
    mean_transition_readiness = mean(transition_readiness),
    mean_ecological_integrity_index = mean(ecological_integrity_index),
    mean_justice_burden_index = mean(justice_burden_index),
    mean_learning_priority = mean(learning_priority),
    .groups = "drop"
  ) %>%
  arrange(mean_rank, rank_range)

transition_summary <- transitions %>%
  arrange(concept, period) %>%
  group_by(concept) %>%
  mutate(
    adoption_delta = adoption_rate - lag(adoption_rate),
    friction_delta = friction_score - lag(friction_score),
    ecological_delta = ecological_impact_reduction - lag(ecological_impact_reduction),
    equity_delta = equity_score - lag(equity_score),
    cost_delta = implementation_cost - lag(implementation_cost),
    maintenance_delta = maintenance_burden - lag(maintenance_burden),
    trust_delta = trust_score - lag(trust_score),
    participation_delta = participation_quality - lag(participation_quality),
    transition_learning_delta =
      0.22 * replace_na(adoption_delta, 0) * 10 -
      0.18 * replace_na(friction_delta, 0) +
      0.24 * replace_na(ecological_delta, 0) * 10 +
      0.18 * replace_na(equity_delta, 0) -
      0.07 * replace_na(cost_delta, 0) -
      0.05 * replace_na(maintenance_delta, 0) +
      0.04 * replace_na(trust_delta, 0) +
      0.02 * replace_na(participation_delta, 0) * 10
  ) %>%
  summarize(
    periods = max(period),
    start_adoption = first(adoption_rate),
    final_adoption = last(adoption_rate),
    start_friction = first(friction_score),
    final_friction = last(friction_score),
    start_ecological_reduction = first(ecological_impact_reduction),
    final_ecological_reduction = last(ecological_impact_reduction),
    start_equity = first(equity_score),
    final_equity = last(equity_score),
    start_cost = first(implementation_cost),
    final_cost = last(implementation_cost),
    start_maintenance = first(maintenance_burden),
    final_maintenance = last(maintenance_burden),
    start_trust = first(trust_score),
    final_trust = last(trust_score),
    start_participation = first(participation_quality),
    final_participation = last(participation_quality),
    total_transition_learning_delta = sum(transition_learning_delta),
    .groups = "drop"
  ) %>%
  mutate(
    adoption_gain = final_adoption - start_adoption,
    friction_reduction = start_friction - final_friction,
    ecological_reduction_gain = final_ecological_reduction - start_ecological_reduction,
    equity_gain = final_equity - start_equity,
    cost_reduction = start_cost - final_cost,
    maintenance_reduction = start_maintenance - final_maintenance,
    trust_gain = final_trust - start_trust,
    participation_gain = final_participation - start_participation
  ) %>%
  arrange(desc(total_transition_learning_delta))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(scenario_results, file.path(output_dir, "r_sustainability_scenario_results.csv"))
readr::write_csv(rank_stability, file.path(output_dir, "r_sustainability_rank_stability.csv"))
readr::write_csv(transition_summary, file.path(output_dir, "r_transition_pathway_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_sustainability_risk_priority.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(concept, sustainability_value), y = sustainability_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Sustainability Concept Value Across Strategic Scenarios",
    x = "Concept",
    y = "Weighted sustainability value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_sustainability_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Sustainability Design Analysis",
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Rank stability",
  "",
  paste(capture.output(print(rank_stability)), collapse = "\n"),
  "",
  "## Transition pathway summary",
  "",
  paste(capture.output(print(transition_summary)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_sustainability_design_report.md"))

message("R sustainability design analysis complete.")
message(paste("Outputs written to:", output_dir))
