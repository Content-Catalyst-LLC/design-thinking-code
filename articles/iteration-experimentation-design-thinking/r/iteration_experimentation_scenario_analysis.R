#!/usr/bin/env Rscript

# Professional iteration and experimentation scenario analysis in R.
#
# This workflow supports transparent comparison of candidate experiments
# across learning gain, update flexibility, expected improvement, residual risk,
# risk decomposition, bootstrap stability, and priority sensitivity.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
input_path <- file.path(article_dir, "data", "raw", "experiments_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "experiment_scenario_weights.csv")
ethics_path <- file.path(article_dir, "data", "raw", "experiment_ethics_review_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

read_experiment_data <- function(path) {
  if (!file.exists(path)) {
    stop(paste("Input data not found:", path))
  }

  data <- readr::read_csv(path, show_col_types = FALSE)

  required <- c(
    "experiment",
    "learning_gain",
    "update_flexibility",
    "expected_improvement",
    "residual_risk"
  )

  missing <- setdiff(required, names(data))
  if (length(missing) > 0) {
    stop(paste("Missing required columns:", paste(missing, collapse = ", ")))
  }

  data %>%
    mutate(
      across(
        where(is.numeric),
        as.numeric
      )
    )
}

validate_experiment_data <- function(data) {
  score_columns <- c(
    "learning_gain",
    "update_flexibility",
    "expected_improvement",
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
    count(experiment) %>%
    filter(n > 1) %>%
    nrow()

  if (duplicate_count > 0) {
    issues <- bind_rows(
      issues,
      tibble(
        level = "error",
        field = "experiment",
        message = "Duplicate experiment names detected."
      )
    )
  }

  issues
}

compute_risk_index <- function(data) {
  component_columns <- c(
    "ethical_risk",
    "operational_risk",
    "interpretive_risk",
    "scaling_risk"
  )

  if (!all(component_columns %in% names(data))) {
    return(data$residual_risk)
  }

  0.30 * data$ethical_risk +
    0.25 * data$operational_risk +
    0.20 * data$interpretive_risk +
    0.25 * data$scaling_risk
}

score_experiments <- function(data, weights) {
  data %>%
    mutate(
      risk_index = compute_risk_index(.),
      experiment_value =
        weights$learning_gain * learning_gain +
        weights$update_flexibility * update_flexibility +
        weights$expected_improvement * expected_improvement -
        weights$residual_risk * residual_risk,
      risk_index_adjusted_value =
        weights$learning_gain * learning_gain +
        weights$update_flexibility * update_flexibility +
        weights$expected_improvement * expected_improvement -
        weights$residual_risk * risk_index,
      risk_adjusted_learning = learning_gain - 0.40 * risk_index,
      evidence_confidence_index = if_else(
        "evidence_quality" %in% names(.) & "team_confidence" %in% names(.),
        0.5 * evidence_quality + 0.5 * team_confidence,
        1.0
      ),
      confidence_adjusted_value = experiment_value * (0.75 + 0.25 * evidence_confidence_index)
    ) %>%
    arrange(desc(experiment_value))
}

run_scenarios <- function(data, scenarios) {
  purrr::map_dfr(
    seq_len(nrow(scenarios)),
    function(i) {
      scenario <- scenarios[i, ]

      weights <- list(
        learning_gain = scenario$learning_gain,
        update_flexibility = scenario$update_flexibility,
        expected_improvement = scenario$expected_improvement,
        residual_risk = scenario$residual_risk
      )

      score_experiments(data, weights) %>%
        mutate(
          scenario = scenario$scenario,
          weight_learning_gain = scenario$learning_gain,
          weight_update_flexibility = scenario$update_flexibility,
          weight_expected_improvement = scenario$expected_improvement,
          weight_residual_risk = scenario$residual_risk
        )
    }
  )
}

bootstrap_stability <- function(data, weights, iterations = 2500, seed = 42) {
  set.seed(seed)

  boot_results <- purrr::map_dfr(
    seq_len(iterations),
    function(iteration) {
      sampled <- data %>%
        slice_sample(n = nrow(data), replace = TRUE)

      score_experiments(sampled, weights) %>%
        mutate(iteration = iteration) %>%
        group_by(iteration) %>%
        arrange(desc(experiment_value), .by_group = TRUE) %>%
        mutate(rank = row_number()) %>%
        ungroup()
    }
  )

  boot_results %>%
    group_by(experiment) %>%
    summarize(
      mean_experiment_value = mean(experiment_value),
      sd_experiment_value = sd(experiment_value),
      mean_risk_index = mean(risk_index),
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
    "learning_gain",
    "update_flexibility",
    "expected_improvement",
    "residual_risk"
  )

  winners <- purrr::map_dfr(
    seq_len(samples),
    function(i) {
      weights <- as.list(random_weights[i, ])
      scored <- score_experiments(data, weights)

      tibble(
        sample = i,
        winner = scored$experiment[1],
        learning_gain_weight = weights$learning_gain,
        update_flexibility_weight = weights$update_flexibility,
        expected_improvement_weight = weights$expected_improvement,
        residual_risk_weight = weights$residual_risk
      )
    }
  )

  winners %>%
    count(winner, name = "times_won") %>%
    mutate(probability_winning_under_random_weights = times_won / samples) %>%
    arrange(desc(probability_winning_under_random_weights))
}

compute_ethics_review_priority <- function(path) {
  if (!file.exists(path)) {
    return(NULL)
  }

  readr::read_csv(path, show_col_types = FALSE) %>%
    mutate(
      computed_review_priority =
        0.25 * requires_informed_consent +
        0.25 * participant_burden +
        0.25 * privacy_sensitivity +
        0.25 * power_asymmetry,
      review_priority_gap = computed_review_priority - review_priority
    ) %>%
    arrange(desc(computed_review_priority))
}

experiment_data <- read_experiment_data(input_path)
validation_issues <- validate_experiment_data(experiment_data)

if (any(validation_issues$level == "error")) {
  print(validation_issues)
  stop("Validation failed.")
}

scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)

scenario_weight_sums <- scenarios %>%
  mutate(
    weight_sum =
      learning_gain +
      update_flexibility +
      expected_improvement +
      residual_risk
  )

if (any(abs(scenario_weight_sums$weight_sum - 1) > 1e-6)) {
  stop("Each scenario weight row must sum to 1.0.")
}

scenario_results <- run_scenarios(experiment_data, scenarios) %>%
  group_by(scenario) %>%
  arrange(desc(experiment_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

balanced_weights <- scenarios %>%
  filter(str_to_lower(scenario) == "balanced") %>%
  slice(1) %>%
  select(learning_gain, update_flexibility, expected_improvement, residual_risk) %>%
  as.list()

bootstrap_summary <- bootstrap_stability(
  data = experiment_data,
  weights = balanced_weights,
  iterations = 2500,
  seed = 42
)

sensitivity_summary <- run_weight_sensitivity(
  data = experiment_data,
  samples = 10000,
  seed = 42
)

ethics_priority <- compute_ethics_review_priority(ethics_path)

readr::write_csv(scenario_results, file.path(output_dir, "r_iteration_experimentation_scenario_results.csv"))
readr::write_csv(bootstrap_summary, file.path(output_dir, "r_iteration_experimentation_bootstrap_summary.csv"))
readr::write_csv(sensitivity_summary, file.path(output_dir, "r_iteration_experimentation_weight_sensitivity.csv"))

if (!is.null(ethics_priority)) {
  readr::write_csv(ethics_priority, file.path(output_dir, "r_experiment_ethics_review_priorities.csv"))
}

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(experiment, experiment_value), y = experiment_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Experiment Portfolio Value Across Learning Scenarios",
    x = "Experiment",
    y = "Weighted experiment value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_iteration_experimentation_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Iteration and Experimentation Analysis",
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
  paste(capture.output(print(sensitivity_summary)), collapse = "\n"),
  "",
  "## Ethics review priority",
  "",
  if (!is.null(ethics_priority)) paste(capture.output(print(ethics_priority)), collapse = "\n") else "No ethics review data provided."
)

writeLines(report, file.path(output_dir, "r_iteration_experimentation_analysis_report.md"))

message("R iteration and experimentation analysis complete.")
message(paste("Outputs written to:", output_dir))
