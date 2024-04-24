#' return list of data.frames, one for gap result and another for runtime result
get_setting_result <- function(acquisition, objective, n_runs, n_trials) {
    setting_result <- list(
        "gap" = data.frame(),
        "runtime" = data.frame()
    )

    return(setting_result)
}
