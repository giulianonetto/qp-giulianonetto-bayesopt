suppressPackageStartupMessages({
    library(tidyverse, warn.conflicts = FALSE)
})
import::from("src/qpr/simulation.r", get_setting_result)
import::from("src/qpr/plotting_results.r", plot_gap_results, plot_runtime_results, parse_labels)

run_qp5_r <- function(n_runs = NULL, n_trials = NULL, output_dir = NULL) {
    if (isFALSE(is.null(n_runs))) {
        n_runs <- as.integer(n_runs)
    } else {
        n_runs <- 2
    }
    if (isFALSE(is.null(n_trials))) {
        n_trials <- as.integer(n_trials)
    } else {
        n_trials <- 10
    }
    if (is.null(output_dir)) {
        output_dir <- "output"
    }

    diceoptim_gap_results_file <- file.path(output_dir, "results_diceoptim_gap.tsv")
    diceoptim_runtime_results_file <- file.path(output_dir, "results_diceoptim_runtime.tsv")
    # run sim only if gap results don't exist already
    results_exist <- file.exists(diceoptim_gap_results_file) & file.exists(diceoptim_runtime_results_file)
    if (isFALSE(results_exist)) {
        # run BayesOpt simulation with DiceOptim
        acquisitions <- c("ei", "kg")
        objectives <- c("h6", "gp", "ros")
        results_runtime <- results_gap <- vector("list", length = length(acquisitions) * length(objectives))
        counter <- 1
        for (i in seq_along(acquisitions)) {
            acquisition <- acquisitions[i]
            for (j in seq_along(objectives)) {
                objective <- objectives[j]
                rlang::inform(str_glue("Running DiceOptim simulation for acquisition={acquisition}, objective={objective}."))
                result <- get_setting_result(acquisition = acquisition, objective = objective, n_runs = n_runs, n_trials = n_trials)
                results_gap[[counter]] <- result[["gap"]]
                results_runtime[[counter]] <- result[["runtime"]]
                counter <- counter + 1
            }
        }

        results_gap <- bind_rows(results_gap)
        results_runtime <- bind_rows(results_runtime)

        # save diceoptim results tables
        write_tsv(results_gap, diceoptim_gap_results_file)
        write_tsv(results_runtime, diceoptim_runtime_results_file)
    } else {
        rlang::inform(stringr::str_glue("Skipping DiceOptim simulation as results already exist in output_dir: {output_dir}."))
    }

    # plot all results (including botorch ones)
    plot_results(output_dir = output_dir)
}

plot_results <- function(output_dir) {
    rlang::inform("Plotting all results.")
    gap_plot <- plot_gap_results(output_dir = output_dir)
    ggsave(
        file.path(output_dir, "gap_results.png"),
        gap_plot,
        dpi = 600, width = 15, height = 7.5
    )

    runtime_plot <- plot_runtime_results(output_dir = output_dir)
    ggsave(
        file.path(output_dir, "runtime_results.png"),
        runtime_plot,
        dpi = 600, width = 15, height = 5.5
    )
}


# Define actual script --------------------------------------------------------

" Run all R-based analyses (DiceOptim + plotting)
        Usage:
          main [--n_runs=<value>] [--n_trials=<value>] [--output_dir=<value>]
          main (-h | --help)
          main --version

        Optional arguments:

          -h --help                                     Show this screen.
          --version                                     Show version.

          --n_runs=<value>          Integer specifying number of simulation runs. Defaults to 2.
          --n_trials=<value>        Integer specifying number of BO trials. Defaults to 10.
          --output_dir=<value>      Path to output directory. Defaults is `output`.
" -> doc

arguments <- docopt::docopt(doc)

# run all analyses
run_qp5_r(
    n_runs = arguments[["--n_runs"]],
    n_trials = arguments[["--n_trials"]],
    output_dir = arguments[["--output_dir"]]
)
