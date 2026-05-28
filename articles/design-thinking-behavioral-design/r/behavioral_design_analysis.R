#!/usr/bin/env Rscript

suppressPackageStartupMessages({ library(tidyverse) })

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
out <- file.path(article_dir, "outputs")
dir.create(out, recursive = TRUE, showWarnings = FALSE)

barriers <- readr::read_csv(file.path(article_dir, "data/raw/behavioral_barriers_raw.csv"), show_col_types = FALSE)
interventions <- readr::read_csv(file.path(article_dir, "data/raw/behavioral_interventions_raw.csv"), show_col_types = FALSE)
experiments <- readr::read_csv(file.path(article_dir, "data/raw/behavioral_experiment_results_raw.csv"), show_col_types = FALSE)
risks <- readr::read_csv(file.path(article_dir, "data/raw/behavioral_risk_register_raw.csv"), show_col_types = FALSE)

logistic <- function(x) 1 / (1 + exp(-x))

barrier_scores <- barriers %>%
  mutate(
    predicted_action_probability = logistic(
      -0.15 + 0.70*((motivation-5.5)/2.5) + 0.72*((capability-5.5)/2.5) +
      0.76*((opportunity-5.5)/2.5) + 0.58*((trust-5.5)/2.5) - 0.88*((friction-5.5)/2.5)
    ),
    action_readiness_index = 0.22*motivation + 0.22*capability + 0.22*opportunity + 0.20*trust - 0.14*friction,
    friction_composition_index = 0.24*time_pressure + 0.24*cognitive_load + 0.20*emotional_load + 0.18*friction + 0.14*institutional_risk,
    behavioral_gap = 10 - action_readiness_index,
    affectedness_weighted_gap = affectedness * behavioral_gap,
    redesign_priority = 0.30*affectedness_weighted_gap + 0.22*friction + 0.16*(10-opportunity) + 0.12*(10-trust) + 0.10*(10-capability) + 0.10*friction_composition_index
  ) %>% arrange(desc(redesign_priority))

intervention_scores <- interventions %>%
  mutate(
    intervention_priority =
      0.22*expected_behavior_gain + 0.14*importance + 0.16*equity_reach +
      0.08*transparency + 0.08*autonomy_preservation + 0.10*trust_effect +
      0.10*accessibility_effect + 0.06*durability - 0.04*ethical_risk -
      0.02*implementation_effort,
    intervention_value = expected_behavior_gain * importance * equity_reach * (0.50 + 0.50*durability) - ethical_risk - 0.20*implementation_effort,
    ethical_quality_index = 0.26*transparency + 0.26*autonomy_preservation + 0.18*equity_reach + 0.16*trust_effect + 0.14*accessibility_effect - 0.22*ethical_risk
  ) %>% arrange(desc(intervention_priority))

experiment_scores <- experiments %>%
  mutate(
    control_rate = control_successes / control_n,
    treatment_rate = treatment_successes / treatment_n,
    absolute_lift = treatment_rate - control_rate,
    relative_lift = absolute_lift / control_rate,
    time_reduction = mean_completion_time_control - mean_completion_time_treatment,
    complaint_delta = complaint_rate_treatment - complaint_rate_control,
    trust_delta = trust_score_treatment - trust_score_control
  ) %>% arrange(desc(absolute_lift))

risk_priority <- risks %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>% arrange(desc(risk_priority_number))

readr::write_csv(barrier_scores, file.path(out, "r_behavioral_barrier_scores.csv"))
readr::write_csv(intervention_scores, file.path(out, "r_behavioral_intervention_scores.csv"))
readr::write_csv(experiment_scores, file.path(out, "r_behavioral_experiment_scores.csv"))
readr::write_csv(risk_priority, file.path(out, "r_behavioral_risk_priority.csv"))

plot <- ggplot(barrier_scores, aes(x = reorder(segment, redesign_priority), y = redesign_priority)) +
  geom_col() + coord_flip() +
  labs(title = "Behavioral Redesign Priority by Segment", x = "Segment", y = "Redesign priority") +
  theme_minimal(base_size = 12)

ggsave(file.path(out, "r_behavioral_barrier_redesign_priority.png"), plot, width = 12, height = 7, dpi = 180)

writeLines(c(
  "# R Behavioral Design Analysis",
  "",
  "## Barrier scores",
  paste(capture.output(print(barrier_scores)), collapse = "\n"),
  "",
  "## Intervention scores",
  paste(capture.output(print(intervention_scores)), collapse = "\n"),
  "",
  "## Experiment scores",
  paste(capture.output(print(experiment_scores)), collapse = "\n"),
  "",
  "## Risk priority",
  paste(capture.output(print(risk_priority)), collapse = "\n")
), file.path(out, "r_behavioral_design_report.md"))

message("R behavioral design analysis complete.")
