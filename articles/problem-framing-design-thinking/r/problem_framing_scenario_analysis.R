#!/usr/bin/env Rscript

# Professional problem-framing scenario analysis in R.
#
# This workflow supports transparent comparison of candidate problem frames
# across explanatory adequacy, stakeholder/system coverage, opportunity value,
# framing risk, risk decomposition, bootstrap stability, and priority sensitivity.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
input_path <- file.path(article_dir, "data", "raw", "problem_frames_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "problem_framing_scenario_weights.csv")
counterframes_path <- file.path(article_dir, "data", "raw", "counterframes_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

read_frame_data <- function(path) {
  if (!file.exists(path)) {
    stop(paste("Input data not found:", path))
  }

  data <- readr::read_csv(path, show_col_types = FALSE)

  required <- c(
    "frame",
    "explanatory_adequacy",
    "stakeholder_coverage",
    "opportunity_value",
    "framing_risk"
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

validate_frame_data <- function(data) {
  score_columns <- c(
    "explanatory_adequacy",
    "stakeholder_coverage",
    "opportunity_value",
    "framing_risk"
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
    count(frame) %>%
    filter(n > 1) %>%
    nrow()

  if (duplicate_count > 0) {
    issues <- bind_rows(
      issues,
      tibble(
        level = "error",
        field = "frame",
        message = "Duplicate frame names detected."
      )
    )
  }

  issues
}

compute_framing_risk_index <- function(data) {
  component_columns <- c(
    "narrowness_risk",
    "stakeholder_exclusion_risk",
    "causality_risk",
    "political_distortion_risk"
  )

  if (!all(component_columns %in% names(data))) {
    return(data$framing_risk)
  }

  0.25 * data$narrowness_risk +
    0.30 * data$stakeholder_exclusion_risk +
    0.25 * data$causality_risk +
    0.20 * data$political_distortion_risk
}

score_frames <- function(data, weights) {
  data %>%
    mutate(
      framing_risk_index = compute_framing_risk_index(.),
      frame_value =
        weights$explanatory_adequacy * explanatory_adequacy +
        weights$stakeholder_coverage * stakeholder_coverage +
        weights$opportunity_value * opportunity_value -
        weights$framing_risk * framing_risk,
      risk_index_adjusted_value =
        weights$explanatory_adequacy * explanatory_adequacy +
        weights$stakeholder_coverage * stakeholder_coverage +
        weights$opportunity_value * opportunity_value -
        weights$framing_risk * framing_risk_index,
      risk_adjusted_opportunity = opportunity_value - 0.40 * framing_risk_index,
      evidence_confidence_index = if_else(
        "evidence_quality" %in% names(.) & "frame_confidence" %in% names(.),
        0.5 * evidence_quality + 0.5 * frame_confidence,
        1.0
      ),
      confidence_adjusted_value = frame_value * (0.75 + 0.25 * evidence_confidence_index)
    ) %>%
    arrange(desc(frame_value))
}

run_scenarios <- function(data, scenarios) {
  purrr::map_dfr(
    seq_len(nrow(scenarios)),
    function(i) {
      scenario <- scenarios[i, ]

      weights <- list(
        explanatory_adequacy = scenario$explanatory_adequacy,
        stakeholder_coverage = scenario$stakeholder_coverage,
        opportunity_value = scenario$opportunity_value,
        framing_risk = scenario$framing_risk
      )

      score_frames(data, weights) %>%
        mutate(
          scenario = scenario$scenario,
          weight_explanatory_adequacy = scenario$explanatory_adequacy,
          weight_stakeholder_coverage = scenario$stakeholder_coverage,
          weight_opportunity_value = scenario$opportunity_value,
          weight_framing_risk = scenario$framing_risk
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

      score_frames(sampled, weights) %>%
        mutate(iteration = iteration) %>%
        group_by(iteration) %>%
        arrange(desc(frame_value), .by_group = TRUE) %>%
        mutate(rank = row_number()) %>%
        ungroup()
    }
  )

  boot_results %>%
    group_by(frame) %>%
    summarize(
      mean_frame_value = mean(frame_value),
      sd_frame_value = sd(frame_value),
      mean_framing_risk_index = mean(framing_risk_index),
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
    "explanatory_adequacy",
    "stakeholder_coverage",
    "opportunity_value",
    "framing_risk"
  )

  winners <- purrr::map_dfr(
    seq_len(samples),
    function(i) {
      weights <- as.list(random_weights[i, ])
      scored <- score_frames(data, weights)

      tibble(
        sample = i,
        winner = scored$frame[1],
        explanatory_adequacy_weight = weights$explanatory_adequacy,
        stakeholder_coverage_weight = weights$stakeholder_coverage,
        opportunity_value_weight = weights$opportunity_value,
        framing_risk_weight = weights$framing_risk
      )
    }
  )

  winners %>%
    count(winner, name = "times_won") %>%
    mutate(probability_winning_under_random_weights = times_won / samples) %>%
    arrange(desc(probability_winning_under_random_weights))
}

compute_counterframe_priority <- function(path) {
  if (!file.exists(path)) {
    return(NULL)
  }

  readr::read_csv(path, show_col_types = FALSE) %>%
    mutate(
      counterframe_test_priority =
        0.55 * missing_evidence_risk +
        0.45 * power_convenience_risk
    ) %>%
    arrange(desc(counterframe_test_priority))
}

frame_data <- read_frame_data(input_path)
validation_issues <- validate_frame_data(frame_data)

if (any(validation_issues$level == "error")) {
  print(validation_issues)
  stop("Validation failed.")
}

scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)

scenario_weight_sums <- scenarios %>%
  mutate(
    weight_sum =
      explanatory_adequacy +
      stakeholder_coverage +
      opportunity_value +
      framing_risk
  )

if (any(abs(scenario_weight_sums$weight_sum - 1) > 1e-6)) {
  stop("Each scenario weight row must sum to 1.0.")
}

scenario_results <- run_scenarios(frame_data, scenarios) %>%
  group_by(scenario) %>%
  arrange(desc(frame_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

balanced_weights <- scenarios %>%
  filter(str_to_lower(scenario) == "balanced") %>%
  slice(1) %>%
  select(explanatory_adequacy, stakeholder_coverage, opportunity_value, framing_risk) %>%
  as.list()

bootstrap_summary <- bootstrap_stability(
  data = frame_data,
  weights = balanced_weights,
  iterations = 2500,
  seed = 42
)

sensitivity_summary <- run_weight_sensitivity(
  data = frame_data,
  samples = 10000,
  seed = 42
)

counterframe_priority <- compute_counterframe_priority(counterframes_path)

readr::write_csv(scenario_results, file.path(output_dir, "r_problem_framing_scenario_results.csv"))
readr::write_csv(bootstrap_summary, file.path(output_dir, "r_problem_framing_bootstrap_summary.csv"))
readr::write_csv(sensitivity_summary, file.path(output_dir, "r_problem_framing_weight_sensitivity.csv"))

if (!is.null(counterframe_priority)) {
  readr::write_csv(counterframe_priority, file.path(output_dir, "r_counterframe_test_priorities.csv"))
}

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(frame, frame_value), y = frame_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Problem Frame Value Across Strategic Scenarios",
    x = "Candidate frame",
    y = "Weighted frame value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_problem_framing_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Problem Framing Analysis",
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
  "## Counterframe test priorities",
  "",
  if (!is.null(counterframe_priority)) paste(capture.output(print(counterframe_priority)), collapse = "\n") else "No counterframe data provided."
)

writeLines(report, file.path(output_dir, "r_problem_framing_analysis_report.md"))

message("R problem-framing analysis complete.")
message(paste("Outputs written to:", output_dir))
