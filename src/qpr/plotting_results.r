suppressPackageStartupMessages(library(tidyverse, warn.conflicts = FALSE))

parse_labels <- function(.df) {
    .df %>%
        mutate(
            objective = factor(
                as.character(objective),
                levels = c("h6", "gp", "ros"),
                labels = c("Goldstein–Price", "Hartman 6", "Rosenbrock 4")
            ),
            acquisition_abbrev = factor(
                as.character(acquisition),
                levels = c("ei", "kg", "pes"),
                labels = c(
                    "EI",
                    "KG",
                    "PES"
                )
            ),
            acquisition = factor(
                as.character(acquisition),
                levels = c("ei", "kg", "pes"),
                labels = c(
                    "Expected Improvement",
                    "Knowledge Gradient",
                    "Pred. Entropy Search"
                )
            )
        )
}

plot_gap_results <- function(output_dir) {
    botorch_gap <- file.path(output_dir, "results_botorch_gap.tsv")
    diceoptim_gap <- file.path(output_dir, "results_diceoptim_gap.tsv")

    if (isFALSE(file.exists(botorch_gap))) {
        msg <- stringr::str_glue("File not found (BoTorch gap results): {botorch_gap}")
        rlang::abort(msg)
    }
    if (isFALSE(file.exists(diceoptim_gap))) {
        msg <- stringr::str_glue("File not found (DiceOptim gap results): {diceoptim_gap}")
        rlang::abort(msg)
    }

    df <- bind_rows(
        read_tsv(botorch_gap, show_col_types = FALSE) %>% mutate(implementation = "BoTorch"),
        read_tsv(diceoptim_gap, show_col_types = FALSE) %>% mutate(implementation = "DiceOptim")
    ) %>%
        parse_labels() %>%
        # TODO: remove once you have actual data
        mutate(
            gap_estimate = trial / max(trial) + rnorm(nrow(.), sd = .05),
            gap_se = 0.05
        )


    gap_plot <- df %>%
        ggplot(
            aes(
                trial + 1,
                gap_estimate,
                ymin = gap_estimate - 1.96 * gap_se,
                ymax = gap_estimate + 1.96 * gap_se
            )
        ) +
        geom_ribbon(
            aes(fill = objective, group = objective),
            alpha = 0.3
        ) +
        geom_line(aes(color = objective, group = objective), linewidth = 1) +
        facet_grid(rows = vars(implementation), cols = vars(acquisition)) +
        labs(
            x = "Iteration",
            y = "Gap",
            color = NULL,
            fill = NULL
        ) +
        theme_classic(base_size = 20) +
        theme(
            strip.text = element_text(face = "bold"),
            legend.position = "top",
            panel.grid.major.y = element_line(),
            panel.grid.major.x = element_line(linewidth = 0.5),
            panel.grid.minor.y = element_line(linewidth = 0.5)
        ) +
        scale_x_continuous(breaks = scales::pretty_breaks(10)) +
        coord_cartesian(ylim = c(0, 1)) +
        scale_color_brewer(palette = "Set1") +
        scale_fill_brewer(palette = "Set1")

    return(gap_plot)
}

plot_runtime_results <- function(output_dir) {
    botorch_runtime <- file.path(output_dir, "results_botorch_runtime.tsv")
    diceoptim_runtime <- file.path(output_dir, "results_botorch_runtime.tsv")

    if (isFALSE(file.exists(botorch_runtime))) {
        msg <- stringr::str_glue("File not found (BoTorch runtime results): {botorch_runtime}")
        rlang::abort(msg)
    }
    if (isFALSE(file.exists(diceoptim_runtime))) {
        msg <- stringr::str_glue("File not found (DiceOptim runtime results): {diceoptim_runtime}")
        rlang::abort(msg)
    }

    df <- bind_rows(
        read_tsv(botorch_runtime, show_col_types = FALSE) %>% mutate(implementation = "BoTorch"),
        read_tsv(diceoptim_runtime, show_col_types = FALSE) %>% mutate(implementation = "DiceOptim")
    ) %>%
        parse_labels() %>%
        # TODO: remove once you have actual data
        mutate(
            time_per_iteration = rpois(nrow(.), 100)
        )

    newer_ggplot2 <- as.logical(compareVersion(as.character(packageVersion("ggplot2")), "3.4.4"))
    if (isTRUE(newer_ggplot2)) {
        my_theme <- list(
            theme(
                legend.position = "inside",
                legend.position.inside = c(0.07, 0.9),
                strip.text = element_text(face = "bold"),
                panel.grid.major.y = element_line(),
                panel.grid.major.x = element_line(linewidth = 0.5),
                panel.grid.minor.y = element_line(linewidth = 0.5)
            )
        )
    } else {
        my_theme <- list(
            theme(
                legend.position = c(0.07, 0.9),
                strip.text = element_text(face = "bold"),
                panel.grid.major.y = element_line(),
                panel.grid.major.x = element_line(linewidth = 0.5),
                panel.grid.minor.y = element_line(linewidth = 0.5)
            )
        )
    }

    runtime_plot <- df %>%
        ggplot(aes(acquisition_abbrev, time_per_iteration)) +
        geom_boxplot(
            aes(fill = implementation),
            width = 0.5,
            position = position_dodge(width = 0.6)
        ) +
        facet_wrap(~objective) +
        theme_classic(base_size = 20) +
        my_theme +
        labs(x = NULL, y = "Seconds per iteration", fill = NULL) +
        scale_fill_brewer(palette = "Dark2")

    return(runtime_plot)
}
