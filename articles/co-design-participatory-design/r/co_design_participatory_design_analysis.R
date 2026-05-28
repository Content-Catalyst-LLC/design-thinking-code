#!/usr/bin/env Rscript

# Professional co-design and participatory design analysis in R.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
activities_path <- file.path(article_dir, "data", "raw", "codesign_activities_raw.csv")
participants_path <- file.path(article_dir, "data", "raw", "participant_groups_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "participation_scenario_weights.csv")
learning_path <- file.path(article_dir, "data", "raw", "participatory_prototype_learning_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "participation_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

activities <- readr::read_csv(activities_path, show_col_types = FALSE)
participants <- readr::read_csv(participants_path, show_col_types = FALSE)
scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)
learning <- readr::read_csv(learning_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

score_activities <- function(data, weights) {
  data %>%
    mutate(
      participation_quality =
        weights$representation * representation +
        weights$accessibility * accessibility +
        weights$participant_influence * participant_influence +
        weights$trust_quality * trust_quality +
        weights$evidence_quality * evidence_quality +
        weights$implementation_accountability * implementation_accountability +
        weights$decision_impact * decision_impact -
        weights$ethical_risk * ethical_risk,
      equity_participation_index =
        0.26 * representation +
        0.24 * accessibility +
        0.22 * participant_influence +
        0.14 * trust_quality +
        0.08 * compensation_quality +
        0.06 * feedback_loop_quality -
        0.10 * ethical_risk -
        0.08 * tokenism_risk,
      implementation_legitimacy_index =
        0.26 * participant_influence +
        0.24 * implementation_accountability +
        0.20 * decision_impact +
        0.14 * feedback_loop_quality +
        0.10 * trust_quality -
        0.06 * tokenism_risk,
      participatory_evidence_index =
        0.30 * evidence_quality +
        0.22 * representation +
        0.18 * participant_influence +
        0.16 * trust_quality +
        0.14 * feedback_loop_quality,
      learning_priority =
        0.24 * ethical_risk +
        0.22 * tokenism_risk +
        0.16 * (10 - representation) +
        0.14 * (10 - participant_influence) +
        0.12 * (10 - implementation_accountability) +
        0.12 * (10 - accessibility)
    ) %>%
    arrange(desc(participation_quality))
}

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_activities(activities, .) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup() %>%
  group_by(scenario) %>%
  arrange(desc(participation_quality), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

participant_summary <- participants %>%
  mutate(
    stage_influence_index =
      0.20 * framing_influence +
      0.16 * synthesis_influence +
      0.16 * concept_influence +
      0.14 * testing_influence +
      0.18 * implementation_influence +
      0.16 * governance_influence,
    accessibility_support_index =
      0.34 * access_support +
      0.24 * language_access +
      0.24 * disability_access +
      0.18 * compensation_support,
    weighted_legitimacy =
      affectedness * presence * stage_influence_index,
    participation_gap =
      affectedness * (1 - presence),
    influence_gap =
      affectedness * presence * (1 - stage_influence_index),
    access_gap =
      affectedness * (1 - accessibility_support_index),
    trust_gap =
      affectedness * (1 - trust_score),
    attention_priority =
      0.32 * participation_gap +
      0.30 * influence_gap +
      0.22 * access_gap +
      0.16 * trust_gap
  ) %>%
  arrange(desc(attention_priority))

process_summary <- participant_summary %>%
  summarize(
    affectedness_weighted_presence = weighted.mean(presence, affectedness),
    affectedness_weighted_influence = weighted.mean(stage_influence_index, affectedness),
    affectedness_weighted_access_support = weighted.mean(accessibility_support_index, affectedness),
    affectedness_weighted_trust = weighted.mean(trust_score, affectedness),
    participatory_legitimacy = sum(weighted_legitimacy) / sum(affectedness),
    total_participation_gap = sum(participation_gap),
    total_influence_gap = sum(influence_gap),
    total_access_gap = sum(access_gap),
    total_trust_gap = sum(trust_gap)
  )

learning_summary <- learning %>%
  arrange(activity, round) %>%
  group_by(activity) %>%
  mutate(
    comprehension_delta = participant_comprehension - lag(participant_comprehension),
    influence_delta = participant_influence - lag(participant_influence),
    trust_delta = trust_score - lag(trust_score),
    clarity_delta = prototype_clarity - lag(prototype_clarity),
    accessibility_delta = accessibility_score - lag(accessibility_score),
    burden_delta = burden_score - lag(burden_score),
    traceability_delta = decision_traceability - lag(decision_traceability),
    implementation_delta = implementation_commitment - lag(implementation_commitment),
    participatory_learning_delta =
      0.15 * replace_na(comprehension_delta, 0) +
      0.20 * replace_na(influence_delta, 0) +
      0.14 * replace_na(trust_delta, 0) +
      0.13 * replace_na(clarity_delta, 0) +
      0.13 * replace_na(accessibility_delta, 0) -
      0.10 * replace_na(burden_delta, 0) +
      0.13 * replace_na(traceability_delta, 0) +
      0.12 * replace_na(implementation_delta, 0)
  ) %>%
  summarize(
    rounds = max(round),
    start_comprehension = first(participant_comprehension),
    final_comprehension = last(participant_comprehension),
    start_influence = first(participant_influence),
    final_influence = last(participant_influence),
    start_trust = first(trust_score),
    final_trust = last(trust_score),
    start_accessibility = first(accessibility_score),
    final_accessibility = last(accessibility_score),
    start_burden = first(burden_score),
    final_burden = last(burden_score),
    start_traceability = first(decision_traceability),
    final_traceability = last(decision_traceability),
    start_implementation = first(implementation_commitment),
    final_implementation = last(implementation_commitment),
    total_participatory_learning_delta = sum(participatory_learning_delta),
    .groups = "drop"
  ) %>%
  mutate(
    comprehension_gain = final_comprehension - start_comprehension,
    influence_gain = final_influence - start_influence,
    trust_gain = final_trust - start_trust,
    accessibility_gain = final_accessibility - start_accessibility,
    burden_reduction = start_burden - final_burden,
    traceability_gain = final_traceability - start_traceability,
    implementation_gain = final_implementation - start_implementation
  ) %>%
  arrange(desc(total_participatory_learning_delta))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

rank_stability <- scenario_results %>%
  group_by(activity, activity_type, design_stage) %>%
  summarize(
    mean_rank = mean(rank),
    best_rank = min(rank),
    worst_rank = max(rank),
    rank_range = worst_rank - best_rank,
    mean_participation_quality = mean(participation_quality),
    mean_equity_participation_index = mean(equity_participation_index),
    mean_implementation_legitimacy_index = mean(implementation_legitimacy_index),
    mean_learning_priority = mean(learning_priority),
    .groups = "drop"
  ) %>%
  arrange(mean_rank, rank_range)

readr::write_csv(scenario_results, file.path(output_dir, "r_codesign_scenario_results.csv"))
readr::write_csv(rank_stability, file.path(output_dir, "r_codesign_rank_stability.csv"))
readr::write_csv(participant_summary, file.path(output_dir, "r_participant_group_gap_summary.csv"))
readr::write_csv(process_summary, file.path(output_dir, "r_participation_process_summary.csv"))
readr::write_csv(learning_summary, file.path(output_dir, "r_participatory_prototype_learning_summary.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_participation_risk_priority.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(activity, participation_quality), y = participation_quality, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Co-Design Participation Quality Across Scenarios",
    x = "Activity",
    y = "Weighted participation quality"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_codesign_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Co-Design and Participatory Design Analysis",
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Rank stability",
  "",
  paste(capture.output(print(rank_stability)), collapse = "\n"),
  "",
  "## Participant process summary",
  "",
  paste(capture.output(print(process_summary)), collapse = "\n"),
  "",
  "## Participant group priorities",
  "",
  paste(capture.output(print(participant_summary)), collapse = "\n"),
  "",
  "## Prototype learning summary",
  "",
  paste(capture.output(print(learning_summary)), collapse = "\n"),
  "",
  "## Risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_codesign_participatory_design_report.md"))

message("R co-design and participatory design analysis complete.")
message(paste("Outputs written to:", output_dir))
