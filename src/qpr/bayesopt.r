#' Returns list(gap=x, runtime=y), where x is data.frame gap results and y likewise for runtime
get_setting_result_old <- function(acquisition_name, objective_name, n_runs, n_trials) {
    setting_result <- list(
        "gap" = data.frame(
            acquisition = acquisition_name,
            objective = objective_name,
            trial = (1:n_trials) - 1,
            gap_estimate = 1,
            gap_se = 1,
            objetive_estimate = 1,
            objetive_se = 1,
            implementation = "DiceOptim"
        ),
        "runtime" = data.frame(
            acquisition = acquisition_name,
            objective = objective_name,
            run_id = (1:n_runs) - 1,
            time_per_iteration = 100 / n_trials,
            implementation = "DiceOptim"
        )
    )

    return(setting_result)
}

#' Returns list(gap=x, runtime=y), where x is a data.frame gap results (n_trial rows) and y likewise for runtime (n_runs rows)
get_setting_result <- function(acquisition_name, objective_name, n_runs, n_trials) {
    gap_results <- runtime_results <- vector("list", length = n_runs)
    for (run_id in seq_along(n_runs)) {
        t0 <- Sys.time()
        gaps <- run_diceoptim(acquisition_name = acquisition_name, objective_name = objective_name, n_trials = n_trials)
        t1 <- Sys.time()
        gap_results[[run_id]] <- data.frame(
            run_id = run_id - 1,
            trial = seq_len(n_trials) - 1,
            gaps = gaps
        )
        runtime_results[[run_id]] <- data.frame(
            acquisition = acquisition_name,
            objective = objective_name,
            run_id = run_id - 1,
            time_per_iteration = (t1 - t0)[[1]] / n_trials,
            implementation = "DiceOptim"
        )
    }

    # summarise gap by trial id
    gap_results <- bind_rows(gap_results) %>%
        group_by(trial) %>%
        summarise(
            gap_estimate = mean(gaps),
            gap_se = sd(gaps) / sqrt(n())
        ) %>%
        ungroup() %>%
        mutate(
            acquisition = acquisition_name,
            objective = objective_name,
            implementation = "DiceOptim"
        )
}

run_diceoptim <- function(acquisition_name, objective_name, n_trials, n_runs, initial_n = NULL) {
    objective_function <- get_objective_function(name = objective_name)
    if (is.null(initial_n)) {
        initial_n <- floor(0.2 * n_trials)
    }
    
}

get_objective_function <- function(name) {
    if (name == "h6") {
        .objective_function <- \(x) DiceOptim::hartman4(x = x)
    } else if (name == "gp") {
        .objective_function <- \(x) DiceOptim::goldsteinprice(x = x)
    } else {
        msg <- stringr::str_glue("Invalid objective function name: {name}")
        rlang::abort(msg)
    }
    return(.objective_function)
}
