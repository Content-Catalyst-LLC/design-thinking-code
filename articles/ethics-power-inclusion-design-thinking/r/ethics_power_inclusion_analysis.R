#!/usr/bin/env Rscript

# Professional ethics, power, and inclusion analysis in R.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
stakeholders_path <- file.path(article_dir, "data", "raw", "stakeholder_groups_raw.csv")
decisions_path <- file.path(article_dir, "data", "raw", "ethical_design_decisions_raw.csv")
participation_path <- file.path(article_dir, "data", "raw", "participation_power_raw.csv")
risk_path <- file.path(article_dir, "data", "raw", "design_governance_risk_register_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

stakeholders <- readr::read_csv(stakeholders_path, show_col_types = FALSE)
decisions <- readr::read_csv(decisions_path, show_col_types = FALSE)
participation <- readr::read_csv(participation_path, show_col_types = FALSE)
risk_register <- readr::read_csv(risk_path, show_col_types = FALSE)

stakeholder_scores <- stakeholders %>%
  mutate(
    inclusion_score =
      0.20 * access +
      0.20 * voice +
      0.16 * safety +
      0.14 * compensation +
      0.14 * representation +
      0.16 * accountability,
    burden_score =
      0.18 * time_burden +
      0.22 * cognitive_burden +
      0.18 * emotional_burden +
      0.16 * documentation_burden +
      0.16 * uncertainty_burden +
      0.10 * coordination_burden,
    power_gap =
      10 - (
        0.40 * voice +
        0.34 * accountability +
        0.16 * compensation +
        0.10 * representation
      ),
    accessibility_gap = accessibility_need * (10 - access),
    trust_gap = 10 - trust_level,
    ethical_attention_priority =
      0.28 * affectedness * burden_score +
      0.24 * affectedness * power_gap +
      0.18 * (10 - inclusion_score) +
      0.14 * accessibility_gap +
      0.10 * trust_gap +
      0.06 * affectedness * emotional_burden
  ) %>%
  arrange(desc(ethical_attention_priority))

decision_scores <- decisions %>%
  mutate(
    ethical_risk =
      harm_severity *
      probability *
      exposure *
      (1 - detectability) *
      (1 - accountability),
    governance_need =
      0.24 * harm_severity +
      0.16 * exposure +
      0.14 * (1 - detectability) +
      0.14 * (1 - accountability) +
      0.12 * privacy_sensitivity +
      0.10 * autonomy_risk +
      0.10 * manipulation_risk,
    review_priority =
      0.32 * ethical_risk +
      0.20 * harm_severity +
      0.14 * exposure +
      0.10 * (1 - accountability) +
      0.08 * (1 - detectability) +
      0.06 * (1 - inclusion_strength) +
      0.05 * privacy_sensitivity +
      0.03 * autonomy_risk +
      0.02 * manipulation_risk,
    repair_deficit = 1 - repairability,
    public_value_adjusted_risk = review_priority - 0.12 * public_value + 0.10 * repair_deficit
  ) %>%
  arrange(desc(public_value_adjusted_risk))

participation_scores <- participation %>%
  mutate(
    participation_power_score =
      0.18 * participant_influence +
      0.18 * decision_authority +
      0.12 * compensation_quality +
      0.12 * accessibility_quality +
      0.12 * feedback_loop_strength +
      0.12 * community_control +
      0.08 * documentation_transparency +
      0.04 * safety_quality +
      0.04 * interpretation_sharedness,
    tokenism_risk =
      0.30 * (1 - decision_authority) +
      0.22 * (1 - participant_influence) +
      0.18 * (1 - community_control) +
      0.12 * (1 - feedback_loop_strength) +
      0.10 * (1 - documentation_transparency) +
      0.08 * (1 - interpretation_sharedness)
  ) %>%
  arrange(desc(tokenism_risk))

risk_priority <- risk_register %>%
  mutate(
    risk_priority_number = severity * likelihood * detectability * repair_difficulty,
    normalized_risk_priority = risk_priority_number / max(risk_priority_number)
  ) %>%
  arrange(desc(risk_priority_number))

readr::write_csv(stakeholder_scores, file.path(output_dir, "r_stakeholder_inclusion_burden_power_scores.csv"))
readr::write_csv(decision_scores, file.path(output_dir, "r_ethical_design_decision_scores.csv"))
readr::write_csv(participation_scores, file.path(output_dir, "r_participation_power_scores.csv"))
readr::write_csv(risk_priority, file.path(output_dir, "r_design_governance_risk_priority.csv"))

stakeholder_plot <- stakeholder_scores %>%
  ggplot(aes(x = reorder(group, ethical_attention_priority), y = ethical_attention_priority)) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Ethical Attention Priority by Stakeholder Group",
    x = "Stakeholder group",
    y = "Ethical attention priority"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_stakeholder_ethical_attention_priority.png"),
  plot = stakeholder_plot,
  width = 12,
  height = 7,
  dpi = 180
)

decision_plot <- decision_scores %>%
  ggplot(aes(x = reorder(design_decision, public_value_adjusted_risk), y = public_value_adjusted_risk)) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Public-Value-Adjusted Ethical Risk by Design Decision",
    x = "Design decision",
    y = "Public-value-adjusted risk"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_design_decision_ethical_risk.png"),
  plot = decision_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Ethics, Power, and Inclusion Analysis",
  "",
  "## Stakeholder scores",
  "",
  paste(capture.output(print(stakeholder_scores)), collapse = "\n"),
  "",
  "## Design decision scores",
  "",
  paste(capture.output(print(decision_scores)), collapse = "\n"),
  "",
  "## Participation power scores",
  "",
  paste(capture.output(print(participation_scores)), collapse = "\n"),
  "",
  "## Governance risk priority",
  "",
  paste(capture.output(print(risk_priority)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_ethics_power_inclusion_report.md"))

message("R ethics, power, and inclusion analysis complete.")
message(paste("Outputs written to:", output_dir))
