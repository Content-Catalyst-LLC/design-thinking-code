#!/usr/bin/env Rscript

# Professional public-policy design analysis in R.
#
# This workflow evaluates public-policy pilots across accessibility,
# feasibility, legitimacy, equity, administrative-burden reduction,
# durability, risk, evidence strength, stakeholder coverage, and
# participation quality.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
pilots_path <- file.path(article_dir, "data", "raw", "public_policy_pilots_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "public_policy_scenario_weights.csv")
learning_path <- file.path(article_dir, "data", "raw", "policy_learning_pathways_raw.csv")
burdens_path <- file.path(article_dir, "data", "raw", "administrative_burden_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "public_policy_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

pilots <- readr::read_csv(pilots_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
learning <- readr::read_csv(learning_path, show_col_types = FALSE)
burdens <- readr::read_csv(burdens_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

score_pilots <- function(data, weights) {
  data %>%
    mutate(
      evidence_strength =
        0.40 * evidence_quality +
        0.35 * stakeholder_coverage +
        0.25 * participation_quality,
      policy_value =
        weights$accessibility * accessibility +
        weights$feasibility * feasibility +
        weights$legitimacy * legitimacy +
        weights$equity * equity +
        weights$burden_reduction * burden_reduction +
        weights$durability * durability -
        weights$risk * risk,
      evidence_adjusted_value =
        policy_value * (0.75 + 0.25 * evidence_strength),
      implementation_readiness =
        0.28 * feasibility +
        0.22 * durability +
        0.18 * evidence_strength * 10 +
        0.16 * accessibility +
        0.16 * legitimacy -
        0.12 * legal_complexity -
        0.12 * implementation_complexity,
      public_legitimacy_index =
        0.35 * legitimacy +
        0.25 * participation_quality * 10 +
        0.20 * stakeholder_coverage * 10 +
        0.20 * equity -
        0.10 * risk,
      equity_access_index =
        0.35 * equity +
        0.25 * accessibility +
        0.20 * burden_reduction +
        0.20 * stakeholder_coverage * 10 -
        0.10 * legal_complexity,
      learning_priority =
        0.20 * risk +
        0.18 * legal_complexity +
        0.18 * implementation_complexity +
        0.16 * (1 - evidence_quality) * 10 +
        0.14 * (1 - stakeholder_coverage) * 10 +
        0.14 * (1 - participation_quality) * 10
    ) %>%
    arrange(desc(policy_value))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_pilots(pilots, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(policy_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

rank_stability <- scenario_results %>%
  group_by(pilot, policy_domain, pilot_type) %>%
  summarize(
    mean_rank = mean(rank),
    best_rank = min(rank),
    worst_rank = max(rank),
    rank_range = worst_rank - best_rank,
    mean_policy_value = mean(policy_value),
    mean_evidence_adjusted_value = mean(evidence_adjusted_value),
    mean_implementation_readiness = mean(implementation_readiness),
    mean_public_legitimacy_index = mean(public_legitimacy_index),
    mean_equity_access_index = mean(equity_access_index),
    mean_learning_priority = mean(learning_priority),
    .groups = "drop"
  ) %>%
  arrange(mean_rank, rank_range)

policy_learning_summary <- learning %>%
  arrange(pilot, period) %>%
  group_by(pilot) %>%
  mutate(
    uptake_delta = uptake_rate - lag(uptake_rate),
    friction_delta = citizen_friction - lag(citizen_friction),
    error_delta = implementation_error - lag(implementation_error),
    trust_delta = trust_score - lag(trust_score),
    equity_delta = equity_score - lag(equity_score),
    appeal_access_delta = appeal_access - lag(appeal_access),
    staff_workload_delta = staff_workload - lag(staff_workload),
    resolution_time_delta = case_resolution_time - lag(case_resolution_time),
    policy_learning_delta =
      0.22 * replace_na(uptake_delta, 0) * 10 -
      0.16 * replace_na(friction_delta, 0) -
      0.16 * replace_na(error_delta, 0) * 10 +
      0.16 * replace_na(trust_delta, 0) +
      0.14 * replace_na(equity_delta, 0) +
      0.08 * replace_na(appeal_access_delta, 0) * 10 -
      0.04 * replace_na(staff_workload_delta, 0) -
      0.04 * replace_na(resolution_time_delta, 0) / 2
  ) %>%
  summarize(
    periods = max(period),
    start_uptake = first(uptake_rate),
    final_uptake = last(uptake_rate),
    start_friction = first(citizen_friction),
    final_friction = last(citizen_friction),
    start_error = first(implementation_error),
    final_error = last(implementation_error),
    start_trust = first(trust_score),
    final_trust = last(trust_score),
    start_equity = first(equity_score),
    final_equity = last(equity_score),
    start_appeal_access = first(appeal_access),
    final_appeal_access = last(appeal_access),
    start_staff_workload = first(staff_workload),
    final_staff_workload = last(staff_workload),
    start_resolution_time = first(case_resolution_time),
    final_resolution_time = last(case_resolution_time),
    total_policy_learning_delta = sum(policy_learning_delta),
    .groups = "drop"
  ) %>%
  mutate(
    uptake_gain = final_uptake - start_uptake,
    friction_reduction = start_friction - final_friction,
    error_reduction = start_error - final_error,
    trust_gain = final_trust - start_trust,
    equity_gain = final_equity - start_equity,
    appeal_access_gain = final_appeal_access - start_appeal_access,
    staff_workload_reduction = start_staff_workload - final_staff_workload,
    case_resolution_time_reduction = start_resolution_time - final_resolution_time
  ) %>%
  arrange(desc(total_policy_learning_delta))

burden_summary <- burdens %>%
  mutate(
    citizen_burden_index =
      0.20 * learning_burden +
      0.22 * compliance_burden +
      0.18 * psychological_burden +
      0.12 * digital_burden +
      0.16 * time_burden +
      0.12 * appeal_burden,
    institutional_burden_index =
      0.55 * staff_burden +
      0.45 * community_partner_burden,
    total_burden_index =
      0.70 * citizen_burden_index +
      0.30 * institutional_burden_index,
    burden_transfer_risk =
      institutional_burden_index - citizen_burden_index
  ) %>%
  arrange(desc(total_burden_index))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(scenario_results, file.path(output_dir, "r_public_policy_scenario_results.csv"))
readr::write_csv(rank_stability, file.path(output_dir, "r_public_policy_rank_stability.csv"))
readr::write_csv(policy_learning_summary, file.path(output_dir, "r_policy_learning_pathway_summary.csv"))
readr::write_csv(burden_summary, file.path(output_dir, "r_administrative_burden_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_public_policy_risk_priority.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(pilot, policy_value), y = policy_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Public Policy Pilot Value Across Strategic Scenarios",
    x = "Policy pilot",
    y = "Weighted public design value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_public_policy_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Public Policy Design Analysis",
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Rank stability",
  "",
  paste(capture.output(print(rank_stability)), collapse = "\n"),
  "",
  "## Policy learning summary",
  "",
  paste(capture.output(print(policy_learning_summary)), collapse = "\n"),
  "",
  "## Administrative burden summary",
  "",
  paste(capture.output(print(burden_summary)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_public_policy_design_report.md"))

message("R public policy design analysis complete.")
message(paste("Outputs written to:", output_dir))
