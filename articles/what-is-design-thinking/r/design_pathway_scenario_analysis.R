#!/usr/bin/env Rscript

# Professional design pathway scenario analysis in R.
#
# This workflow supports transparent comparison of design thinking pathways
# across strategic priority scenarios, bootstrap stability, and diagnostic
# interpretation.

suppressPackageStartupMessages({
  library(tidyverse)
})

args <- commandArgs(trailingOnly = TRUE)

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
input_path <- file.path(article_dir, "data", "raw", "design_pathways_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "scenario_weights.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

read_design_data <- function(path) {
  if (!file.exists(path)) {
    stop(paste("Input data not found:", path))
  }

  data <- readr::read_csv(path, show_col_types = FALSE)

  required <- c(
    "pathway",
    "human_relevance",
    "feasibility",
    "learning_value",
    "residual_risk"
  )

  missing <- setdiff(required, names(data))
  if (length(missing) > 0) {
    stop(paste("Missing required columns:", paste(missing, collapse = ", ")))
  }

  data %>%
    mutate(
      across(
        c(human_relevance, feasibility, learning_value, residual_risk),
        as.numeric
      )
    )
}

validate_design_data <- function(data) {
  score_columns <- c(
    "human_relevance",
    "feasibility",
    "learning_value",
    "residual_risk"
  )

  issues <- tibble(level = character(), field = character(), message = character())

  for (column in score_columns) {
    invalid_count <- data %>%
      filter(is.na(.data[[column]]) | .data[[column]] < 1 | .data[[column]] > 10) %>%
      nrow()

    if (invalid_count > 0) {
      issues <- bind_rows(
        issues,
        tibble(
          level = "error",
          field = column,
          message = "Scores must be numeric and in the inclusive range [1, 10]."
        )
      )
    }
  }

  duplicate_count <- data %>%
    count(pathway) %>%
    filter(n > 1) %>%
    nrow()

  if (duplicate_count > 0) {
    issues <- bind_rows(
      issues,
      tibble(
        level = "error",
        field = "pathway",
        message = "Duplicate pathway names detected."
      )
    )
  }

  issues
}

score_pathways <- function(data, weights) {
  data %>%
    mutate(
      design_value =
        weights$human_relevance * human_relevance +
        weights$feasibility * feasibility +
        weights$learning_value * learning_value -
        weights$residual_risk * residual_risk,
      risk_adjusted_learning = learning_value - 0.5 * residual_risk
    ) %>%
    arrange(desc(design_value)) %>%
    mutate(rank = row_number())
}

run_scenarios <- function(data, scenarios) {
  scenario_results <- purrr::map_dfr(
    seq_len(nrow(scenarios)),
    function(i) {
      scenario <- scenarios[i, ]

      weights <- list(
        human_relevance = scenario$human_relevance,
        feasibility = scenario$feasibility,
        learning_value = scenario$learning_value,
        residual_risk = scenario$residual_risk
      )

      score_pathways(data, weights) %>%
        mutate(
          scenario = scenario$scenario,
          weight_human_relevance = scenario$human_relevance,
          weight_feasibility = scenario$feasibility,
          weight_learning_value = scenario$learning_value,
          weight_residual_risk = scenario$residual_risk
        )
    }
  )

  scenario_results
}

bootstrap_stability <- function(data, weights, iterations = 2500, seed = 42) {
  set.seed(seed)

  boot_results <- purrr::map_dfr(
    seq_len(iterations),
    function(iteration) {
      sampled <- data %>%
        slice_sample(n = nrow(data), replace = TRUE)

      score_pathways(sampled, weights) %>%
        mutate(iteration = iteration)
    }
  )

  boot_results %>%
    group_by(pathway) %>%
    summarize(
      mean_design_value = mean(design_value),
      sd_design_value = sd(design_value),
      median_rank = median(rank),
      mean_rank = mean(rank),
      best_rank = min(rank),
      worst_rank = max(rank),
      .groups = "drop"
    ) %>%
    arrange(median_rank, mean_rank)
}

run_weight_sensitivity <- function(data, samples = 10000, seed = 42) {
  set.seed(seed)

  random_weights <- matrix(rexp(samples * 4, rate = 1), ncol = 4)
  random_weights <- random_weights / rowSums(random_weights)

  colnames(random_weights) <- c(
    "human_relevance",
    "feasibility",
    "learning_value",
    "residual_risk"
  )

  winners <- purrr::map_dfr(
    seq_len(samples),
    function(i) {
      weights <- as.list(random_weights[i, ])
      scored <- score_pathways(data, weights)

      tibble(
        sample = i,
        winner = scored$pathway[1],
        human_relevance_weight = weights$human_relevance,
        feasibility_weight = weights$feasibility,
        learning_value_weight = weights$learning_value,
        residual_risk_weight = weights$residual_risk
      )
    }
  )

  winners %>%
    count(winner, name = "times_won") %>%
    mutate(probability_winning_under_random_weights = times_won / samples) %>%
    arrange(desc(probability_winning_under_random_weights))
}

design_data <- read_design_data(input_path)
validation_issues <- validate_design_data(design_data)

if (any(validation_issues$level == "error")) {
  print(validation_issues)
  stop("Validation failed.")
}

scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)

scenario_weight_sums <- scenarios %>%
  mutate(weight_sum = human_relevance + feasibility + learning_value + residual_risk)

if (any(abs(scenario_weight_sums$weight_sum - 1) > 1e-6)) {
  stop("Each scenario weight row must sum to 1.0.")
}

scenario_results <- run_scenarios(design_data, scenarios)

balanced_weights <- scenarios %>%
  filter(str_to_lower(scenario) == "balanced") %>%
  slice(1) %>%
  select(human_relevance, feasibility, learning_value, residual_risk) %>%
  as.list()

bootstrap_summary <- bootstrap_stability(
  data = design_data,
  weights = balanced_weights,
  iterations = 2500,
  seed = 42
)

sensitivity_summary <- run_weight_sensitivity(
  data = design_data,
  samples = 10000,
  seed = 42
)

readr::write_csv(scenario_results, file.path(output_dir, "r_design_pathway_scenario_results.csv"))
readr::write_csv(bootstrap_summary, file.path(output_dir, "r_design_pathway_bootstrap_summary.csv"))
readr::write_csv(sensitivity_summary, file.path(output_dir, "r_design_pathway_weight_sensitivity.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(pathway, design_value), y = design_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Design Pathway Value Across Strategic Scenarios",
    x = "Design pathway",
    y = "Weighted design value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_design_pathway_scenario_plot.png"),
  plot = scenario_plot,
  width = 11,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Design Pathway Analysis",
  "",
  "This report summarizes the R-based scenario and robustness workflow.",
  "",
  "## Scenario results",
  "",
  paste(capture.output(print(scenario_results)), collapse = "\n"),
  "",
  "## Bootstrap stability",
  "",
  paste(capture.output(print(bootstrap_summary)), collapse = "\n"),
  "",
  "## Weight sensitivity",
  "",
  paste(capture.output(print(sensitivity_summary)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_design_pathway_analysis_report.md"))

message("R design pathway analysis complete.")
message(paste("Outputs written to:", output_dir))
