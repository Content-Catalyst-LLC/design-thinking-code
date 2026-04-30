# Synthetic design thinking pathway comparison.
# Educational only. Not a consulting or automated design-decision tool.

# install.packages(c("tidyverse", "scales"))
library(tidyverse)
library(scales)

pathways <- tibble(
  pathway = c(
    "Service Redesign Pathway",
    "Digital Platform Pathway",
    "Workflow Coordination Pathway",
    "Community Partnership Pathway"
  ),
  human_relevance = c(8.8, 7.9, 8.2, 8.6),
  feasibility     = c(7.4, 8.3, 7.8, 7.1),
  learning_value  = c(8.1, 7.7, 8.4, 8.5),
  residual_risk   = c(4.0, 4.3, 3.8, 4.2)
)

score_pathways <- function(data, wh, wf, wl, wr) {
  data %>%
    mutate(
      design_value = wh * human_relevance +
        wf * feasibility +
        wl * learning_value -
        wr * residual_risk
    ) %>%
    arrange(desc(design_value))
}

scenarios <- tribble(
  ~scenario,              ~wh,  ~wf,  ~wl,  ~wr,
  "Balanced",             0.35, 0.25, 0.25, 0.15,
  "Human-first",          0.50, 0.20, 0.20, 0.10,
  "Feasibility-first",    0.20, 0.50, 0.20, 0.10,
  "Learning-first",       0.20, 0.20, 0.45, 0.15,
  "Risk-sensitive",       0.25, 0.20, 0.20, 0.35
)

scenario_results <- scenarios %>%
  rowwise() %>%
  do(
    score_pathways(
      pathways,
      wh = .$wh,
      wf = .$wf,
      wl = .$wl,
      wr = .$wr
    ) %>%
      mutate(scenario = .$scenario)
  ) %>%
  ungroup()

ranked_results <- scenario_results %>%
  group_by(scenario) %>%
  arrange(desc(design_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

dir.create("outputs", showWarnings = FALSE, recursive = TRUE)
write_csv(ranked_results, file.path("outputs", "design_pathway_rankings.csv"))

print(ranked_results)
