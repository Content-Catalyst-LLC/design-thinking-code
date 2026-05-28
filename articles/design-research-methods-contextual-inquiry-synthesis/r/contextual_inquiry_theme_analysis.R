#!/usr/bin/env Rscript

# Professional contextual inquiry theme analysis in R.
#
# This workflow summarizes evidence units, estimates synthesis confidence,
# evaluates validation priority, compares coder assignments, and exports
# reproducible design-research artifacts.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
evidence_path <- file.path(article_dir, "data", "raw", "contextual_inquiry_evidence_units_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "synthesis_scenario_weights.csv")
coder_path <- file.path(article_dir, "data", "raw", "coder_theme_assignments_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

scale_to_10 <- function(x) {
  if (max(x, na.rm = TRUE) == min(x, na.rm = TRUE)) {
    return(rep(5.5, length(x)))
  }
  1 + (x - min(x, na.rm = TRUE)) * 9 / (max(x, na.rm = TRUE) - min(x, na.rm = TRUE))
}

evidence <- readr::read_csv(evidence_path, show_col_types = FALSE)
weights <- readr::read_csv(weights_path, show_col_types = FALSE)
coder_map <- readr::read_csv(coder_path, show_col_types = FALSE)

required <- c(
  "unit_id",
  "participant_group",
  "method",
  "primary_theme",
  "secondary_theme",
  "evidence_strength",
  "interpretive_risk",
  "environmental_constraint",
  "artifact_dependency",
  "workflow_stage",
  "privacy_sensitivity",
  "power_asymmetry"
)

missing <- setdiff(required, names(evidence))
if (length(missing) > 0) {
  stop(paste("Missing required columns:", paste(missing, collapse = ", ")))
}

summarize_themes <- function(data, scenario_weights) {
  data %>%
    group_by(primary_theme) %>%
    summarize(
      evidence_units = n(),
      stakeholder_groups = n_distinct(participant_group),
      methods = n_distinct(method),
      workflow_stages = n_distinct(workflow_stage),
      mean_evidence_strength = mean(evidence_strength),
      mean_interpretive_risk = mean(interpretive_risk),
      mean_environmental_constraint = mean(environmental_constraint),
      mean_artifact_dependency = mean(artifact_dependency),
      mean_privacy_sensitivity = mean(privacy_sensitivity),
      mean_power_asymmetry = mean(power_asymmetry),
      .groups = "drop"
    ) %>%
    mutate(
      stakeholder_coverage_score = scale_to_10(stakeholder_groups),
      method_triangulation_score = scale_to_10(methods),
      workflow_breadth_score = scale_to_10(workflow_stages),
      synthesis_confidence =
        scenario_weights$evidence_strength * mean_evidence_strength +
        scenario_weights$stakeholder_coverage * stakeholder_coverage_score +
        scenario_weights$method_triangulation * method_triangulation_score -
        scenario_weights$interpretive_risk * mean_interpretive_risk,
      contextual_depth_index =
        0.30 * mean_environmental_constraint +
        0.30 * mean_artifact_dependency +
        0.20 * workflow_breadth_score +
        0.20 * mean_evidence_strength,
      ethics_review_priority =
        0.35 * mean_power_asymmetry +
        0.35 * mean_privacy_sensitivity +
        0.15 * (mean_interpretive_risk / 10) +
        0.15 * (mean_environmental_constraint / 10),
      validation_priority =
        0.35 * mean_interpretive_risk +
        0.25 * (10 - mean_evidence_strength) +
        0.20 * (10 - stakeholder_coverage_score) +
        0.20 * (10 - method_triangulation_score)
    ) %>%
    arrange(desc(synthesis_confidence))
}

balanced_weights <- weights %>%
  filter(str_to_lower(scenario) == "balanced") %>%
  slice(1)

theme_summary <- summarize_themes(evidence, balanced_weights)

scenario_results <- weights %>%
  rowwise() %>%
  do(
    summarize_themes(evidence, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(synthesis_confidence), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

theme_edges <- evidence %>%
  filter(primary_theme != secondary_theme) %>%
  count(primary_theme, secondary_theme, name = "weight") %>%
  arrange(desc(weight))

coder_summary <- coder_map %>%
  rowwise() %>%
  mutate(
    assignments = list(c(coder_a, coder_b, coder_c)),
    consensus_theme = names(sort(table(unlist(assignments)), decreasing = TRUE))[1],
    agreement_ratio = max(table(unlist(assignments))) / length(unlist(assignments)),
    unique_assignments = length(unique(unlist(assignments)))
  ) %>%
  ungroup() %>%
  select(unit_id, consensus_theme, agreement_ratio, unique_assignments) %>%
  group_by(consensus_theme) %>%
  summarize(
    coded_units = n(),
    mean_agreement_ratio = mean(agreement_ratio),
    low_agreement_units = sum(agreement_ratio < 1),
    .groups = "drop"
  ) %>%
  arrange(mean_agreement_ratio, desc(coded_units))

saturation <- evidence %>%
  arrange(unit_id) %>%
  mutate(
    cumulative_theme_count = purrr::map_int(
      seq_along(primary_theme),
      ~ n_distinct(primary_theme[1:.x])
    ),
    lag_theme_count = lag(cumulative_theme_count, default = 0),
    new_theme_discovered = as.integer(cumulative_theme_count > lag_theme_count),
    marginal_theme_discovery = cumulative_theme_count - lag_theme_count
  ) %>%
  select(unit_id, cumulative_theme_count, new_theme_discovered, marginal_theme_discovery)

validation_priority <- theme_summary %>%
  arrange(desc(validation_priority))

readr::write_csv(theme_summary, file.path(output_dir, "r_theme_synthesis_summary.csv"))
readr::write_csv(scenario_results, file.path(output_dir, "r_theme_scenario_results.csv"))
readr::write_csv(theme_edges, file.path(output_dir, "r_theme_network_edges.csv"))
readr::write_csv(coder_summary, file.path(output_dir, "r_coder_agreement_summary.csv"))
readr::write_csv(saturation, file.path(output_dir, "r_theme_saturation_analysis.csv"))
readr::write_csv(validation_priority, file.path(output_dir, "r_theme_validation_priority.csv"))

confidence_plot <- theme_summary %>%
  ggplot(aes(x = reorder(primary_theme, synthesis_confidence), y = synthesis_confidence)) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Contextual Inquiry Theme Synthesis Confidence",
    x = "Theme",
    y = "Synthesis confidence"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_theme_synthesis_confidence.png"),
  plot = confidence_plot,
  width = 11,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Contextual Inquiry and Synthesis Analysis",
  "",
  "## Theme summary",
  "",
  paste(capture.output(print(theme_summary)), collapse = "\n"),
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Coder summary",
  "",
  paste(capture.output(print(coder_summary)), collapse = "\n"),
  "",
  "## Saturation",
  "",
  paste(capture.output(print(tail(saturation, 10))), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_contextual_inquiry_synthesis_report.md"))

message("R contextual inquiry synthesis analysis complete.")
message(paste("Outputs written to:", output_dir))
