#!/usr/bin/env Rscript

# Professional insight-generation scenario analysis in R.
#
# This workflow supports transparent comparison of candidate insights
# across pattern support, explanatory depth, opportunity value, interpretive risk,
# risk decomposition, evidence validation, bootstrap stability, and priority sensitivity.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
input_path <- file.path(article_dir, "data", "raw", "candidate_insights_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "insight_scenario_weights.csv")
evidence_path <- file.path(article_dir, "data", "raw", "insight_evidence_sources_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

read_insight_data <- function(path) {
  if (!file.exists(path)) {
    stop(paste("Input data not found:", path))
  }

  data <- readr::read_csv(path, show_col_types = FALSE)

  required <- c(
    "insight",
    "pattern_support",
    "explanatory_depth",
    "opportunity_value",
    "interpretive_risk"
  )

  missing <- setdiff(required, names(data))
  if (length(missing) > 0) {
    stop(paste("Missing required columns:", paste(missing, collapse = ", ")))
  }

  data %>%
    mutate(across(where(is.numeric), as.numeric))
}

validate_insight_data <- function(data) {
  score_columns <- c(
    "pattern_support",
    "explanatory_depth",
    "opportunity_value",
    "interpretive_risk"
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
    count(insight) %>%
    filter(n > 1) %>%
    nrow()

  if (duplicate_count > 0) {
    issues <- bind_rows(
      issues,
      tibble(
        level = "error",
        field = "insight",
        message = "Duplicate insight names detected."
      )
    )
  }

  issues
}

compute_interpretive_risk_index <- function(data) {
  component_columns <- c(
    "sampling_risk",
    "confirmation_bias_risk",
    "evidence_thinness_risk",
    "solution_capture_risk"
  )

  if (!all(component_columns %in% names(data))) {
    return(data$interpretive_risk)
  }

  0.30 * data$sampling_risk +
    0.25 * data$confirmation_bias_risk +
    0.25 * data$evidence_thinness_risk +
    0.20 * data$solution_capture_risk
}

score_insights <- function(data, weights) {
  data %>%
    mutate(
      interpretive_risk_index = compute_interpretive_risk_index(.),
      insight_value =
        weights$pattern_support * pattern_support +
        weights$explanatory_depth * explanatory_depth +
        weights$opportunity_value * opportunity_value -
        weights$interpretive_risk * interpretive_risk,
      risk_index_adjusted_value =
        weights$pattern_support * pattern_support +
        weights$explanatory_depth * explanatory_depth +
        weights$opportunity_value * opportunity_value -
        weights$interpretive_risk * interpretive_risk_index,
      risk_adjusted_opportunity = opportunity_value - 0.40 * interpretive_risk_index,
      evidence_diversity_index = if_else(
        "evidence_quality" %in% names(.) & "stakeholder_diversity" %in% names(.),
        0.5 * evidence_quality + 0.5 * stakeholder_diversity,
        1.0
      ),
      confidence_adjusted_value = insight_value * (0.75 + 0.25 * evidence_diversity_index),
      testability_adjusted_value = if_else(
        "prototype_testability" %in% names(.),
        confidence_adjusted_value * (0.85 + 0.15 * prototype_testability),
        confidence_adjusted_value
      ),
      interpretation_review_priority =
        0.35 * interpretive_risk_index +
        0.25 * (10 - pattern_support) +
        0.20 * (10 - explanatory_depth) +
        0.20 * (10 - opportunity_value)
    ) %>%
    arrange(desc(insight_value))
}

run_scenarios <- function(data, scenarios) {
  purrr::map_dfr(
    seq_len(nrow(scenarios)),
    function(i) {
      scenario <- scenarios[i, ]

      weights <- list(
        pattern_support = scenario$pattern_support,
        explanatory_depth = scenario$explanatory_depth,
        opportunity_value = scenario$opportunity_value,
        interpretive_risk = scenario$interpretive_risk
      )

      score_insights(data, weights) %>%
        mutate(
          scenario = scenario$scenario,
          weight_pattern_support = scenario$pattern_support,
          weight_explanatory_depth = scenario$explanatory_depth,
          weight_opportunity_value = scenario$opportunity_value,
          weight_interpretive_risk = scenario$interpretive_risk
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

      score_insights(sampled, weights) %>%
        mutate(iteration = iteration) %>%
        group_by(iteration) %>%
        arrange(desc(insight_value), .by_group = TRUE) %>%
        mutate(rank = row_number()) %>%
        ungroup()
    }
  )

  boot_results %>%
    group_by(insight) %>%
    summarize(
      mean_insight_value = mean(insight_value),
      sd_insight_value = sd(insight_value),
      mean_interpretive_risk_index = mean(interpretive_risk_index),
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
    "pattern_support",
    "explanatory_depth",
    "opportunity_value",
    "interpretive_risk"
  )

  winners <- purrr::map_dfr(
    seq_len(samples),
    function(i) {
      weights <- as.list(random_weights[i, ])
      scored <- score_insights(data, weights)

      tibble(
        sample = i,
        winner = scored$insight[1],
        pattern_support_weight = weights$pattern_support,
        explanatory_depth_weight = weights$explanatory_depth,
        opportunity_value_weight = weights$opportunity_value,
        interpretive_risk_weight = weights$interpretive_risk
      )
    }
  )

  winners %>%
    count(winner, name = "times_won") %>%
    mutate(probability_winning_under_random_weights = times_won / samples) %>%
    arrange(desc(probability_winning_under_random_weights))
}

compute_evidence_validation_priority <- function(path) {
  if (!file.exists(path)) {
    return(NULL)
  }

  readr::read_csv(path, show_col_types = FALSE) %>%
    mutate(
      computed_validation_priority =
        0.30 * validation_priority +
        0.20 * pmin(contradictory_cases / 5, 1) +
        0.20 * (1 - pmin(evidence_source_count / 25, 1)) +
        0.15 * (1 - pmin(stakeholder_groups / 6, 1)) +
        0.15 * (1 - pmin(method_count / 5, 1))
    ) %>%
    arrange(desc(computed_validation_priority))
}

insight_data <- read_insight_data(input_path)
validation_issues <- validate_insight_data(insight_data)

if (any(validation_issues$level == "error")) {
  print(validation_issues)
  stop("Validation failed.")
}

scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)

scenario_weight_sums <- scenarios %>%
  mutate(
    weight_sum =
      pattern_support +
      explanatory_depth +
      opportunity_value +
      interpretive_risk
  )

if (any(abs(scenario_weight_sums$weight_sum - 1) > 1e-6)) {
  stop("Each scenario weight row must sum to 1.0.")
}

scenario_results <- run_scenarios(insight_data, scenarios) %>%
  group_by(scenario) %>%
  arrange(desc(insight_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

balanced_weights <- scenarios %>%
  filter(str_to_lower(scenario) == "balanced") %>%
  slice(1) %>%
  select(pattern_support, explanatory_depth, opportunity_value, interpretive_risk) %>%
  as.list()

bootstrap_summary <- bootstrap_stability(
  data = insight_data,
  weights = balanced_weights,
  iterations = 2500,
  seed = 42
)

sensitivity_summary <- run_weight_sensitivity(
  data = insight_data,
  samples = 10000,
  seed = 42
)

evidence_priority <- compute_evidence_validation_priority(evidence_path)

review_priority <- score_insights(insight_data, balanced_weights) %>%
  arrange(desc(interpretation_review_priority)) %>%
  select(
    insight,
    pattern_support,
    explanatory_depth,
    opportunity_value,
    interpretive_risk_index,
    interpretation_review_priority
  )

readr::write_csv(scenario_results, file.path(output_dir, "r_insight_generation_scenario_results.csv"))
readr::write_csv(bootstrap_summary, file.path(output_dir, "r_insight_generation_bootstrap_summary.csv"))
readr::write_csv(sensitivity_summary, file.path(output_dir, "r_insight_generation_weight_sensitivity.csv"))
readr::write_csv(review_priority, file.path(output_dir, "r_insight_interpretation_review_priority.csv"))

if (!is.null(evidence_priority)) {
  readr::write_csv(evidence_priority, file.path(output_dir, "r_insight_evidence_validation_priorities.csv"))
}

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(insight, insight_value), y = insight_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Candidate Insight Value Across Synthesis Scenarios",
    x = "Candidate insight",
    y = "Weighted insight value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_insight_generation_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Insight Generation Analysis",
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
  "## Interpretation review priority",
  "",
  paste(capture.output(print(review_priority)), collapse = "\n"),
  "",
  "## Evidence validation priority",
  "",
  if (!is.null(evidence_priority)) paste(capture.output(print(evidence_priority)), collapse = "\n") else "No evidence-source data provided."
)

writeLines(report, file.path(output_dir, "r_insight_generation_analysis_report.md"))

message("R insight-generation analysis complete.")
message(paste("Outputs written to:", output_dir))
