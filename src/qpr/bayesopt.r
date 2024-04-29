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
    for (run_id in seq_len(n_runs)) {
        t0 <- Sys.time()
        gaps <- run_diceoptim(
            acquisition_name = acquisition_name,
            objective_name = objective_name,
            n_trials = n_trials,
            initial_n = 10
        )
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
    runtime_results <- bind_rows(runtime_results)

    return(list("gap" = gap_results, "runtime" = runtime_results))
}

get_objective_dimension <- function(name) {
    if (name == "h6") {
        d <- 6
    } else if (name == "h4") {
        d <- 4
    } else if (name == "gp") {
        d <- 2
    } else if (name == "ros") {
        d <- 4
    } else {
        msg <- string::str_glue("Invalid objetive_name={objetive_name}")
        rlang::abort(msg)
    }
    return(d)
}

get_global_optimum <- function(name) {
    if (name == "h6") {
        go <- -3.322368
    } else if (name == "h4") {
        go <- -3.135474
    } else if (name == "gp") {
        go <- -3.129172
    } else if (name == "ros") {
        go <- -1.019701
    } else {
        msg <- string::str_glue("Invalid objetive_name={objetive_name}")
        rlang::abort(msg)
    }
    return(go)
}

generate_initial_data <- function(n, objective_name) {
    d <- get_objective_dimension(name = objective_name)
    initial_data <- matrix(runif(n * d), nrow = n, ncol = d)
    return(initial_data)
}

compute_gap <- function(
    incumbent, initial_f, global_optimum) {
    # here global opt is global minimum
    return(
        (initial_f - incumbent) / (initial_f - global_optimum)
    )
}

run_diceoptim <- function(acquisition_name, objective_name, n_trials, initial_n = 10) {
    if (isFALSE(acquisition_name %in% c("random", "ei", "kg"))) {
        msg <- stringr::str_glue("Invalid acquisition_name={acquisition_name}")
        rlang::abort(msg)
    }

    objective_function <- get_objective_function(name = objective_name)
    objective_dim <- get_objective_dimension(name = objective_name)
    global_optimum <- get_global_optimum(name = objective_name)

    # initialize data
    input_data <- generate_initial_data(n = initial_n, objective_name = objective_name)
    observed_f <- apply(input_data, 1, objective_function)

    # initialize gaps and record initial gap
    gaps <- numeric(n_trials)
    gaps[1] <- compute_gap(
        incumbent = min(observed_f),
        initial_f = observed_f[1],
        global_optimum = global_optimum
    )
    # fit initial model
    km_control <- list(
        pop.size = 50, BFGSburin = 10, trace = FALSE,
        wait.generations = 5, max.generations = 20, print.level = 0
    )
    model <- DiceKriging::km(
        design = input_data,
        response = observed_f,
        control = km_control
    )

    # bounds for pars
    lower <- rep(0, objective_dim)
    upper <- rep(1, objective_dim)

    for (trial in 2:n_trials) {
        if (acquisition_name == "random") {
            next_x <- generate_initial_data(n = 1, objective_name = objective_name)
        } else if (acquisition_name == "ei") {
            next_x <- suppressWarnings({
                DiceOptim::max_EI(
                    model = model, lower = lower, upper = upper,
                    control = model@control
                )
            })$par
        } else if (acquisition_name == "kg") {
            next_x <- suppressWarnings({
                DiceOptim::max_AKG(
                    model = model, lower = lower, upper = upper,
                    control = model@control
                )
            })$par
        } else {
            msg <- stringr::str_glue("Invalid acquisition_name={acquisition_name}")
            rlang::abort(msg)
        }

        # update current data
        model@X <- rbind(model@X, next_x)
        model@y <- rbind(model@y, objective_function(next_x))

        # record gap
        gaps[trial] <- compute_gap(
            incumbent = min(model@y),
            initial_f = model@y[1],
            global_optimum = global_optimum
        )


        # fit new model with current data
        if (acquisition_name != "random") {
            model@control$parinit <- DiceKriging::covparam2vect(model@covariance)
            model <- DiceKriging::km(
                formula = model@trend.formula, design = model@X,
                response = model@y, covtype = model@covariance@name,
                lower = model@lower, upper = model@upper, nugget = NULL,
                penalty = model@penalty, optim.method = model@optim.method,
                parinit = model@parinit, control = model@control,
                gr = model@gr, iso = is(model@covariance, "covIso")
            )
        }
    }

    return(gaps)
}

get_objective_function <- function(name, negate = FALSE) {
    m <- (-1)^as.numeric(negate)
    if (name == "h4") {
        .objective_function <- \(x) m * DiceOptim::hartman4(x = x)
    } else if (name == "h6") {
        .objective_function <- \(x) m * DiceKriging::hartman6(x = x)
    } else if (name == "gp") {
        .objective_function <- \(x) m * DiceOptim::goldsteinprice(x = x)
    } else if (name == "ros") {
        .objective_function <- \(x) m * DiceOptim::rosenbrock4(x = x)
    } else {
        msg <- stringr::str_glue("Invalid objective function name: {name}")
        rlang::abort(msg)
    }
    return(.objective_function)
}


EGO.nsteps2 <- function(
    model, fun, nsteps, lower, upper,
    parinit = NULL,
    control = NULL,
    kmcontrol = NULL) {
    n <- nrow(model@X)
    if (is.null(kmcontrol$penalty)) {
        kmcontrol$penalty <- model@penalty
    }
    if (length(model@penalty == 0)) {
        kmcontrol$penalty <- NULL
    }
    if (is.null(kmcontrol$optim.method)) {
        kmcontrol$optim.method <- model@optim.method
    }
    if (is.null(kmcontrol$parinit)) {
        kmcontrol$parinit <- model@parinit
    }
    if (is.null(kmcontrol$control)) {
        kmcontrol$control <- model@control
    }
    for (i in 1:nsteps) {
        oEGO <- max_EI(
            model = model, lower = lower, upper = upper,
            parinit = parinit, control = control
        )
        model@X <- rbind(model@X, oEGO$par)
        model@y <- rbind(model@y, fun(t(oEGO$par)))
        kmcontrol$parinit <- covparam2vect(model@covariance)
        kmcontrol$control$trace <- FALSE
        if (model@param.estim) {
            model <- km(
                formula = model@trend.formula, design = model@X,
                response = model@y, covtype = model@covariance@name,
                lower = model@lower, upper = model@upper, nugget = NULL,
                penalty = kmcontrol$penalty, optim.method = kmcontrol$optim.method,
                parinit = kmcontrol$parinit, control = kmcontrol$control,
                gr = model@gr, iso = is(model@covariance, "covIso")
            )
        } else {
            coef.cov <- covparam2vect(model@covariance)
            model <- km(
                formula = model@trend.formula, design = model@X,
                response = model@y, covtype = model@covariance@name,
                coef.trend = model@trend.coef, coef.cov = coef.cov,
                coef.var = model@covariance@sd2, nugget = NULL,
                iso = is(model@covariance, "covIso")
            )
        }
    }
    return(list(
        par = model@X[(n + 1):(n + nsteps), , drop = FALSE],
        value = model@y[(n + 1):(n + nsteps), , drop = FALSE],
        npoints = 1, nsteps = nsteps, lastmodel = model
    ))
}
