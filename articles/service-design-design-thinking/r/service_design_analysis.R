#!/usr/bin/env Rscript

# Professional service design analysis in R.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
stages_path <- file.path(article_dir, "data", "raw", "service_journey_stages_raw.csv")
groups_path <- file.path(article_dir, "data", "raw", "service_user_groups_raw.csv")
blueprint_path <- file.path(article_dir, "data", "raw", "service_blueprint_dependencies_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "service_scenario_weights.csv")
risk_path <- file.path(article_dir, "data", "raw", "service_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

stages <- readr::read_csv(stages_path, show_col_types = FALSE)
groups <- readr::read_csv(groups_path, show_col_types = FALSE)
blueprint <- readr::read_csv(blueprint_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

score_stages <- function(data, weights) {
  data %>%
    mutate(
      service_stage_quality =
        weights$completion_probability * completion_probability * 10 +
        weights$clarity * clarity +
        weights$trust * trust +
        weights$accessibility * accessibility +
        weights$recovery_quality * recovery_quality -
        weights$user_burden * user_burden -
        weights$staff_load * staff_load,
      failure_risk = 1 - completion_probability,
      burden_risk = 0.55 * user_burden + 0.45 * staff_load,
      operational_friction_index =
        0.22 * policy_complexity +
        0.22 * data_dependency +
        0.20 * staff_load +
        0.18 * (10 - backstage_readiness) +
        0.18 * failure_risk * 10,
      frontstage_backstage_gap = abs(frontstage_quality - backstage_readiness),
      procedural_dignity_index =
        0.26 * clarity +
        0.24 * trust +
        0.20 * accessibility +
        0.18 * recovery_quality -
        0.12 * user_burden,
      redesign_priority =
        0.30 * failure_risk * 10 +
        0.22 * burden_risk +
        0.16 * (10 - clarity) +
        0.12 * (10 - accessibility) +
        0.10 * (10 - recovery_quality) +
        0.10 * operational_friction_index,
      service_resilience =
        0.30 * service_stage_quality +
        0.25 * backstage_readiness +
        0.20 * recovery_quality +
        0.15 * procedural_dignity_index -
        0.10 * operational_friction_index
    ) %>%
    arrange(desc(redesign_priority))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_stages(stages, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(redesign_priority), .by_group = TRUE) %>%
  mutate(redesign_rank = row_number()) %>%
  ungroup()

service_reliability <- prod(stages$completion_probability)

group_scores <- groups %>%
  mutate(
    group_service_quality =
      0.24 * completion_rate * 10 +
      0.18 * clarity +
      0.18 * accessibility +
      0.16 * trust +
      0.14 * recovery_access +
      0.10 * assisted_support -
      0.14 * burden,
    access_support_index =
      0.25 * assisted_support +
      0.25 * device_access +
      0.25 * language_access +
      0.25 * disability_access,
    equity_gap = max(group_service_quality) - group_service_quality,
    affectedness_weighted_gap = affectedness * equity_gap,
    group_attention_priority =
      0.34 * affectedness_weighted_gap +
      0.22 * (10 - accessibility) +
      0.18 * burden +
      0.14 * (10 - trust) +
      0.12 * (10 - recovery_access)
  ) %>%
  arrange(desc(group_attention_priority))

blueprint_scores <- blueprint %>%
  mutate(
    blueprint_friction_index =
      0.24 * dependency_strength +
      0.24 * handoff_risk +
      0.16 * (10 - data_quality) +
      0.16 * (10 - ownership_clarity) +
      0.10 * automation_opacity +
      0.10 * (10 - governance_readiness),
    governance_attention_priority =
      0.28 * blueprint_friction_index +
      0.22 * (10 - ownership_clarity) +
      0.20 * (10 - governance_readiness) +
      0.16 * handoff_risk +
      0.14 * automation_opacity
  ) %>%
  arrange(desc(governance_attention_priority))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

service_summary <- tibble(
  service_reliability = service_reliability,
  mean_completion_probability = mean(stages$completion_probability),
  mean_clarity = mean(stages$clarity),
  mean_trust = mean(stages$trust),
  mean_accessibility = mean(stages$accessibility),
  mean_user_burden = mean(stages$user_burden),
  mean_staff_load = mean(stages$staff_load),
  mean_recovery_quality = mean(stages$recovery_quality)
)

readr::write_csv(scenario_results, file.path(output_dir, "r_service_design_scenario_results.csv"))
readr::write_csv(service_summary, file.path(output_dir, "r_service_summary.csv"))
readr::write_csv(group_scores, file.path(output_dir, "r_service_user_group_equity_summary.csv"))
readr::write_csv(blueprint_scores, file.path(output_dir, "r_service_blueprint_dependency_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_service_risk_priority.csv"))

plot <- scenario_results %>%
  filter(scenario == "Balanced") %>%
  ggplot(aes(x = reorder(stage, redesign_priority), y = redesign_priority)) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Service Stage Redesign Priority",
    x = "Service stage",
    y = "Redesign priority"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_service_stage_redesign_priority.png"),
  plot = plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Service Design Analysis",
  "",
  paste("End-to-end service reliability:", round(service_reliability, 4)),
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Service summary",
  "",
  paste(capture.output(print(service_summary)), collapse = "\n"),
  "",
  "## User group equity summary",
  "",
  paste(capture.output(print(group_scores)), collapse = "\n"),
  "",
  "## Blueprint dependency summary",
  "",
  paste(capture.output(print(blueprint_scores)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_service_design_report.md"))

message("R service design analysis complete.")
message(paste("Outputs written to:", output_dir))
