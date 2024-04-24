def get_setting_result(acquisition: str, objective: str, n_runs: int, n_trials: int) -> dict[list[dict]]:
    """
    Returns dict(gap=x, runtime=y), where x is list of dicts for gap results and y likewise for runtime
    """
    gap_result = []
    for i in range(n_trials):
        gap_result.append(
            dict(
                acquisition=acquisition, objective=objective,
                trial=i,
                gap_estimate=1, gap_se=1,
                objetive_estimate=1, objetive_se=1,
                implementation="BoTorch"
            )
        )
    runtime_result = []
    total_time = 100
    for i in range(n_runs):
        runtime_result.append(
            dict(
                acquisition=acquisition, objective=objective,
                run_id=i,
                time_per_iteration=total_time / n_trials,
                implementation="BoTorch"
            )
        )
    return dict(gap=gap_result, runtime=runtime_result)