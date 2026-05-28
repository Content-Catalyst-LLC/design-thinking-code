#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
output_dir <- file.path(article_dir, "outputs")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

initiatives <- readr::read_csv(
  file.path(article_dir, "data", "raw", "future_design_initiatives_raw.csv"),
  show_col_types = FALSE
)

scores <- initiatives %>%
  mutate(
    future_design_readiness =
      0.11 * human_centered_quality +
      0.12 * systems_literacy +
      0.12 * evidence_quality +
      0.12 * ethical_maturity +
      0.10 * ai_governance +
      0.10 * implementation_capacity +
      0.12 * public_value +
      0.09 * stewardship_capacity +
      0.06 * participation_quality +
      0.06 * organizational_learning +
      0.04 * data_infrastructure +
      0.04 * climate_responsibility +
      0.04 * burden_awareness -
      0.10 * unmanaged_risk,
    stewardship_need =
      0.26 * unmanaged_risk +
      0.17 * (10 - stewardship_capacity) +
      0.15 * (10 - implementation_capacity) +
      0.12 * (10 - ethical_maturity) +
      0.10 * (10 - evidence_quality) +
      0.08 * (10 - systems_literacy) +
      0.07 * (10 - organizational_learning) +
      0.05 * (10 - burden_awareness),
    ai_design_maturity =
      0.28 * ai_governance +
      0.18 * evidence_quality +
      0.16 * data_infrastructure +
      0.14 * ethical_maturity +
      0.12 * human_centered_quality +
      0.12 * organizational_learning -
      0.10 * unmanaged_risk,
    portfolio_priority =
      0.36 * future_design_readiness +
      0.20 * public_value +
      0.14 * ethical_maturity +
      0.10 * systems_literacy +
      0.08 * evidence_quality +
      0.06 * participation_quality -
      0.10 * stewardship_need -
      0.06 * unmanaged_risk
  ) %>%
  arrange(desc(portfolio_priority))

readr::write_csv(scores, file.path(output_dir, "r_future_design_initiative_scores.csv"))

portfolio_plot <- scores %>%
  ggplot(aes(x = reorder(initiative, portfolio_priority), y = portfolio_priority)) +
  geom_col() +
  coord_flip() +
  labs(
    title = "Future Design-Thinking Portfolio Priority",
    x = "Initiative",
    y = "Portfolio priority"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_future_design_portfolio_priority.png"),
  plot = portfolio_plot,
  width = 12,
  height = 7,
  dpi = 180
)

readiness_plot <- scores %>%
  ggplot(aes(x = stewardship_need, y = future_design_readiness, size = public_value, label = initiative)) +
  geom_point(alpha = 0.75) +
  geom_text(check_overlap = TRUE, vjust = -0.8, size = 3) +
  labs(
    title = "Future Design Readiness vs Stewardship Need",
    x = "Stewardship need",
    y = "Future design readiness",
    size = "Public value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_future_design_readiness_stewardship_need.png"),
  plot = readiness_plot,
  width = 12,
  height = 7,
  dpi = 180
)

writeLines(
  c("# R Future Design-Thinking Readiness Analysis", "", capture.output(print(scores))),
  file.path(output_dir, "r_future_design_readiness_report.md")
)

message("R future design-thinking readiness analysis complete.")
