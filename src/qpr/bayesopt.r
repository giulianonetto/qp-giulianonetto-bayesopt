#' Returns list(gap=x, runtime=y), where x is data.frame gap results and y likewise for runtime
get_setting_result <- function(acquisition, objective, n_runs, n_trials) {
    setting_result <- list(
        "gap" = data.frame(
            acquisition = acquisition,
            objective = objective,
            trial = (1:n_trials) - 1,
            gap_estimate = 1,
            gap_se = 1,
            objetive_estimate = 1,
            objetive_se = 1,
            implementation = "DiceOptim"
        ),
        "runtime" = data.frame(
            acquisition = acquisition,
            objective = objective,
            run_id = (1:n_runs) - 1,
            time_per_iteration = 100 / n_trials,
            implementation = "DiceOptim"
        )
    )

    return(setting_result)
}
