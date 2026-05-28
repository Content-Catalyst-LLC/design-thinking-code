#!/usr/bin/env Rscript

# Professional ideation scenario analysis in R.
#
# This workflow supports transparent comparison of candidate ideas across
# desirability, feasibility, novelty, equity value, learning value, composite
# risk, cluster diversity, bootstrap stability, and priority sensitivity.

suppressPackageStartupMessages({
  library(tidyverse)
})

article_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."), mustWork = FALSE)
input_path <- file.path(article_dir, "data", "raw", "idea_portfolio_raw.csv")
weights_path <- file.path(article_dir, "data", "raw", "ideation_scenario_weights.csv")
clusters_path <- file.path(article_dir, "data", "raw", "idea_cluster_map_raw.csv")
output_dir <- file.path(article_dir, "outputs")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

read_idea_data <- function(path) {
  if (!file.exists(path)) {
    stop(paste("Input data not found:", path))
  }

  data <- readr::read_csv(path, show_col_types = FALSE)

  required <- c(
    "idea",
    "idea_cluster",
    "desirability",
    "feasibility",
    "novelty",
    "equity_value",
    "learning_value",
    "residual_risk",
    "ethical_risk",
    "operational_risk",
    "technical_risk",
    "scaling_risk"
  )

  missing <- setdiff(required, names(data))
  if (length(missing) > 0) {
    stop(paste("Missing required columns:", paste(missing, collapse = ", ")))
  }

  data %>%
    mutate(across(where(is.numeric), as.numeric))
}

validate_idea_data <- function(data) {
  score_columns <- c(
    "desirability",
    "feasibility",
    "novelty",
    "equity_value",
    "learning_value",
    "residual_risk",
    "ethical_risk",
    "operational_risk",
    "technical_risk",
    "scaling_risk"
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
    count(idea) %>%
    filter(n > 1) %>%
    nrow()

  if (duplicate_count > 0) {
    issues <- bind_rows(
      issues,
      tibble(
        level = "error",
        field = "idea",
        message = "Duplicate idea names detected."
      )
    )
  }

  issues
}

compute_composite_risk <- function(data) {
  0.25 * data$residual_risk +
    0.25 * data$ethical_risk +
    0.20 * data$operational_risk +
    0.15 * data$technical_risk +
    0.15 * data$scaling_risk
}

score_ideas <- function(data, weights) {
  data %>%
    mutate(
      composite_risk = compute_composite_risk(.),
      idea_value =
        weights$desirability * desirability +
        weights$feasibility * feasibility +
        weights$novelty * novelty +
        weights$equity_value * equity_value +
        weights$learning_value * learning_value -
        weights$composite_risk * composite_risk,
      confidence_adjusted_value =
        if_else(
          "evidence_quality" %in% names(.),
          idea_value * (0.75 + 0.25 * evidence_quality),
          idea_value
        ),
      prototype_priority =
        0.30 * desirability +
        0.25 * learning_value +
        0.20 * feasibility +
        0.15 * equity_value -
        0.10 * composite_risk,
      risk_adjusted_learning = learning_value - 0.35 * composite_risk,
      review_priority =
        0.30 * composite_risk +
        0.20 * (10 - feasibility) +
        0.15 * ethical_risk +
        0.15 * scaling_risk +
        0.20 * (10 - desirability)
    ) %>%
    arrange(desc(idea_value))
}

run_scenarios <- function(data, scenarios) {
  purrr::map_dfr(
    seq_len(nrow(scenarios)),
    function(i) {
      scenario <- scenarios[i, ]

      weights <- list(
        desirability = scenario$desirability,
        feasibility = scenario$feasibility,
        novelty = scenario$novelty,
        equity_value = scenario$equity_value,
        learning_value = scenario$learning_value,
        composite_risk = scenario$composite_risk
      )

      score_ideas(data, weights) %>%
        mutate(
          scenario = scenario$scenario,
          weight_desirability = scenario$desirability,
          weight_feasibility = scenario$feasibility,
          weight_novelty = scenario$novelty,
          weight_equity_value = scenario$equity_value,
          weight_learning_value = scenario$learning_value,
          weight_composite_risk = scenario$composite_risk
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

      score_ideas(sampled, weights) %>%
        mutate(iteration = iteration) %>%
        group_by(iteration) %>%
        arrange(desc(idea_value), .by_group = TRUE) %>%
        mutate(rank = row_number()) %>%
        ungroup()
    }
  )

  boot_results %>%
    group_by(idea) %>%
    summarize(
      mean_idea_value = mean(idea_value),
      sd_idea_value = sd(idea_value),
      mean_composite_risk = mean(composite_risk),
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

  random_weights <- matrix(rexp(samples * 6, rate = 1), ncol = 6)
  random_weights <- random_weights / rowSums(random_weights)

  colnames(random_weights) <- c(
    "desirability",
    "feasibility",
    "novelty",
    "equity_value",
    "learning_value",
    "composite_risk"
  )

  winners <- purrr::map_dfr(
    seq_len(samples),
    function(i) {
      weights <- as.list(random_weights[i, ])
      scored <- score_ideas(data, weights)

      tibble(
        sample = i,
        winner = scored$idea[1],
        desirability_weight = weights$desirability,
        feasibility_weight = weights$feasibility,
        novelty_weight = weights$novelty,
        equity_value_weight = weights$equity_value,
        learning_value_weight = weights$learning_value,
        composite_risk_weight = weights$composite_risk
      )
    }
  )

  winners %>%
    count(winner, name = "times_won") %>%
    mutate(probability_winning_under_random_weights = times_won / samples) %>%
    arrange(desc(probability_winning_under_random_weights))
}

idea_data <- read_idea_data(input_path)
validation_issues <- validate_idea_data(idea_data)

if (any(validation_issues$level == "error")) {
  print(validation_issues)
  stop("Validation failed.")
}

scenarios <- readr::read_csv(weights_path, show_col_types = FALSE)

scenario_weight_sums <- scenarios %>%
  mutate(
    weight_sum =
      desirability +
      feasibility +
      novelty +
      equity_value +
      learning_value +
      composite_risk
  )

if (any(abs(scenario_weight_sums$weight_sum - 1) > 1e-6)) {
  stop("Each scenario weight row must sum to 1.0.")
}

scenario_results <- run_scenarios(idea_data, scenarios) %>%
  group_by(scenario) %>%
  arrange(desc(idea_value), .by_group = TRUE) %>%
  mutate(rank = row_number()) %>%
  ungroup()

balanced_weights <- scenarios %>%
  filter(str_to_lower(scenario) == "balanced") %>%
  slice(1) %>%
  select(desirability, feasibility, novelty, equity_value, learning_value, composite_risk) %>%
  as.list()

bootstrap_summary <- bootstrap_stability(
  data = idea_data,
  weights = balanced_weights,
  iterations = 2500,
  seed = 42
)

sensitivity_summary <- run_weight_sensitivity(
  data = idea_data,
  samples = 10000,
  seed = 42
)

review_priority <- score_ideas(idea_data, balanced_weights) %>%
  arrange(desc(review_priority)) %>%
  select(
    idea,
    idea_cluster,
    idea_value,
    prototype_priority,
    composite_risk,
    ethical_risk,
    scaling_risk,
    review_priority
  )

cluster_summary <- idea_data %>%
  group_by(idea_cluster) %>%
  summarize(
    idea_count = n(),
    mean_desirability = mean(desirability),
    mean_novelty = mean(novelty),
    mean_equity_value = mean(equity_value),
    mean_composite_risk = mean(compute_composite_risk(cur_data())),
    .groups = "drop"
  ) %>%
  mutate(
    portfolio_cluster_count = n_distinct(idea_cluster),
    portfolio_idea_count = nrow(idea_data),
    exploratory_breadth_ratio = portfolio_cluster_count / portfolio_idea_count
  )

readr::write_csv(scenario_results, file.path(output_dir, "r_ideation_scenario_results.csv"))
readr::write_csv(bootstrap_summary, file.path(output_dir, "r_ideation_bootstrap_summary.csv"))
readr::write_csv(sensitivity_summary, file.path(output_dir, "r_ideation_weight_sensitivity.csv"))
readr::write_csv(review_priority, file.path(output_dir, "r_ideation_review_priority.csv"))
readr::write_csv(cluster_summary, file.path(output_dir, "r_ideation_cluster_summary.csv"))

scenario_plot <- scenario_results %>%
  ggplot(aes(x = reorder(idea, idea_value), y = idea_value, fill = scenario)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(
    title = "Idea Portfolio Value Across Ideation Scenarios",
    x = "Idea",
    y = "Weighted idea value"
  ) +
  theme_minimal(base_size = 12)

ggsave(
  filename = file.path(output_dir, "r_ideation_scenario_plot.png"),
  plot = scenario_plot,
  width = 12,
  height = 7,
  dpi = 180
)

report <- c(
  "# R Ideation Portfolio Analysis",
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
  "## Review priority",
  "",
  paste(capture.output(print(review_priority)), collapse = "\n"),
  "",
  "## Cluster summary",
  "",
  paste(capture.output(print(cluster_summary)), collapse = "\n")
)

writeLines(report, file.path(output_dir, "r_ideation_analysis_report.md"))

message("R ideation portfolio analysis complete.")
message(paste("Outputs written to:", output_dir))
