suppressPackageStartupMessages(library(tidyverse, warn.conflicts = FALSE))
import::from("src/qpr/simulation.r", run_simulation_r)
import::from("src/qpr/plotting_results.r", plot_gap_results, plot_runtime_results)

run_qp5_r <- function(n_runs = NULL, n_trials = NULL, output_dir = NULL) {
    if isFALSE(is.null(n_runs)) {
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
    
    # run BayesOpt simulation with DiceOptim
    run_simulation_r(n_runs = n_runs, n_trials = n_trials, output_dir = output_dir)
    results_gap <- list()
    results_runtime <- list()
    for (acquisition in c("ei", "kg", "pes")) {
        for (objective in c("h6", "gp", "shu")) {
            msg = f"Running DiceOptim simulation for acquisition={acquisition}, objective={objective}."
            print(msg)
            result = get_setting_result(acquisition=acquisition, objective=objective, n_runs=n_runs, n_trials=n_trials)
            results_gap <- append(results_gap, result["gap"])
            results_runtime <- append(results_runtime, result["runtime"])
        }
    }

    results_gap <- bind_rows(results_gap)
    results_runtime <- bind_rows(results_runtime)

    write_tsv(results_gap, file.path(output_dir, "results_diceoptim_gap.tsv"))
    write_tsv(results_gap, file.path(output_dir, "results_diceoptim_runtime.tsv"))
    # plot all results (including python-based ones)
    plot_results(output_dir = output_dir)
}

plot_results <- function(output_dir) {
    gap_plot <- plot_gap_results(output_dir = output_dir)
    ggsave(
        file.path(output_dir, "gap_results.png"),
        gap_plot,
        dpi = 600, width = 12, height = 6.5
    )

    runtime_plot <- plot_runtime_results(output_dir = output_dir)
    ggsave(
        file.path(output_dir, "runtime_results.png"),
        runtime_plot,
        dpi = 600, width = 12, height = 6.5
    )
}


# Define actual script --------------------------------------------------------

""" Run all R-based analyses (DiceOptim + plotting)
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
""" -> doc

arguments <- docopt::docopt(doc)

# run all analyses
run_qp5_r(
    n_runs=arguments.["--n_runs"],
    n_trials=arguments.["--n_trials"],
    output_dir=arguments.["--output_dir"]
)