#!/usr/bin/env Rscript

# Professional human-centered design option scenario analysis in R.
#
# This workflow supports transparent comparison of human-centered design
# options across benefit, usability, stakeholder fit, burden, burden
# components, bootstrap stability, and priority sensitivity.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
input_path <- file.path(article_dir, "data", "raw", "human_centered_options_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "human_centered_scenario_weights.csv")
stakeholders_path <- file.path(article_dir, "data", "raw", "stakeholder_groups_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

read_design_data <- function(path) {
  if (!file.exists(path)) {
    stop(paste("Input data not found:", path))
  }

  data <- readr::read_csv(path, show_col_types = FALSE)

  required <- c(
    "option",
    "human_benefit",
    "usability",
    "stakeholder_fit",
    "burden"
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

validate_design_data <- function(data) {
  score_columns <- c(
    "human_benefit",
    "usability",
    "stakeholder_fit",
    "burden"
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
    count(option) %>%
    filter(n > 1) %>%
    nrow()

  if (duplicate_count > 0) {
    issues <- bind_rows(
      issues,
      tibble(
        level = "error",
        field = "option",
        message = "Duplicate option names detected."
      )
    )
  }

  issues
}

compute_burden_index <- function(data) {
  component_columns <- c("learning_cost", "compliance_cost", "psychological_cost", "access_cost")

  if (!all(component_columns %in% names(data))) {
    return(data$burden)
  }

  0.25 * data$learning_cost +
    0.30 * data$compliance_cost +
    0.25 * data$psychological_cost +
    0.20 * data$access_cost
}

score_options <- function(data, weights) {
  data %>%
    mutate(
      burden_index = compute_burden_index(.),
      hc_value =
        weights$human_benefit * human_benefit +
        weights$usability * usability +
        weights$stakeholder_fit * stakeholder_fit -
        weights$burden * burden,
      burden_index_adjusted_value =
        weights$human_benefit * human_benefit +
        weights$usability * usability +
        weights$stakeholder_fit * stakeholder_fit -
        weights$burden * burden_index,
      burden_adjusted_fit = stakeholder_fit - 0.35 * burden_index,
      evidence_confidence_index = if_else(
        "evidence_quality" %in% names(.) & "stakeholder_confidence" %in% names(.),
        0.5 * evidence_quality + 0.5 * stakeholder_confidence,
        1.0
      ),
      confidence_adjusted_value = hc_value * (0.75 + 0.25 * evidence_confidence_index)
    ) %>%
    arrange(desc(hc_value))
}

run_scenarios <- function(data, scenarios) {
  purrr::map_dfr(
    seq_len(nrow(scenarios)),
    function(i) {
      scenario <- scenarios[i, ]

      weights <- list(
        human_benefit = scenario$human_benefit,
        usability = scenario$usability,
        stakeholder_fit = scenario$stakeholder_fit,
        burden = scenario$burden
      )

      score_options(data, weights) %>%
        mutate(
          scenario = scenario$scenario,
          weight_human_benefit = scenario$human_benefit,
          weight_usability = scenario$usability,
          weight_stakeholder_fit = scenario$stakeholder_fit,
          weight_burden = scenario$burden
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

      score_options(sampled, weights) %>%
        mutate(iteration = iteration) %>%
        group_by(iteration) %>%
        arrange(desc(hc_value), .by_group = TRUE) %>%
        mutate(rank = row_number()) %>%
        ungroup()
    }
  )

  boot_results %>%
    group_by(option) %>%
    summarize(
      mean_hc_value = mean(hc_value),
      sd_hc_value = sd(hc_value),
      mean_burden_index = mean(burden_index),
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
    "human_benefit",
    "usability",
    "stakeholder_fit",
    "burden"
  )

  winners <- purrr::map_dfr(
    seq_len(samples),
    function(i) {
      weights <- as.list(random_weights[i, ])
      scored <- score_options(data, weights)

      tibble(
        sample = i,
        winner = scored$option[1],
        human_benefit_weight = weights$human_benefit,
        usability_weight = weights$usability,
        stakeholder_fit_weight = weights$stakeholder_fit,
        burden_weight = weights$burden
      )
    }
  )

  winners %>%
    count(winner, name = "times_won") %>%
    mutate(probability_winning_under_random_weights = times_won / samples) %>%
    arrange(desc(probability_winning_under_random_weights))
}

compute_stakeholder_exclusion <- function(path) {
  if (!file.exists(path)) {
    return(NULL)
  }

  readr::read_csv(path, show_col_types = FALSE) %>%
    mutate(
      invisibility_risk = 1 - visibility_to_institution,
      power_gap = 1 - power_to_influence_design,
      human_centered_exclusion_risk =
        0.30 * invisibility_risk +
        0.25 * power_gap +
        0.25 * burden_exposure +
        0.20 * access_risk
    ) %>%
    arrange(desc(human_centered_exclusion_risk))
}

design_data <- read_design_data(input_path)
validation_issues <- validate_design_data(design_data)

if (any(validation_issues$level == "error")) {
  print(validation_issues)
  stop("Validation failed.")
}

scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)

scenario_weight_sums <- scenarios %>%
  mutate(weight_sum = human_benefit + usability + stakeholder_fit + burden)

if (any(abs(scenario_weight_sums$weight_sum - 1) > 1e-6)) {
  stop("Each scenario weight row must sum to 1.0.")
}

scenario_results <- run_scenarios(design_data, scenarios) %>%
  group_by(scenario) %>%
  arrange(desc(hc_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

balanced_weights <- scenarios %>%
  filter(str_to_lower(scenario) == "balanced") %>%
  slice(1) %>%
  select(human_benefit, usability, stakeholder_fit, burden) %>%
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

stakeholder_risk <- compute_stakeholder_exclusion(stakeholders_path)

readr::write_csv(scenario_results, file.path(output_dir, "r_human_centered_scenario_results.csv"))
readr::write_csv(bootstrap_summary, file.path(output_dir, "r_human_centered_bootstrap_summary.csv"))
readr::write_csv(sensitivity_summary, file.path(output_dir, "r_human_centered_weight_sensitivity.csv"))

if (!is.null(stakeholder_risk)) {
  readr::write_csv(stakeholder_risk, file.path(output_dir, "r_stakeholder_exclusion_risk.csv"))
}

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(option, hc_value), y = hc_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Human-Centered Design Value Across Strategic Scenarios",
    x = "Design option",
    y = "Weighted human-centered value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_human_centered_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

if (!is.null(stakeholder_risk)) {
  stakeholder_plot <- stakeholder_risk %>%
    ggplot(
      aes(
        x = reorder(stakeholder_group, human_centered_exclusion_risk),
        y = human_centered_exclusion_risk
      )
    ) +
    geom_col() +
    coord_flip() +
    labs(
      title = "Stakeholder Exclusion Risk",
      x = "Stakeholder group",
      y = "Composite exclusion risk"
    ) +
    theme_minimal(base_size = 12)

  ggsave(
    filename = file.path(output_dir, "r_stakeholder_exclusion_risk.png"),
    plot = stakeholder_plot,
    width = 11,
    height = 6,
    dpi = 180
  )
}

report <- c(
  "# R Human-Centered Design Analysis",
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
  "## Stakeholder exclusion risk",
  "",
  if (!is.null(stakeholder_risk)) paste(capture.output(print(stakeholder_risk)), collapse = "\n") else "No stakeholder data provided."
)

writeLines(report, file.path(output_dir, "r_human_centered_analysis_report.md"))

message("R human-centered design analysis complete.")
message(paste("Outputs written to:", output_dir))
