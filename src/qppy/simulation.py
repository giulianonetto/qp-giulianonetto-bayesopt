import numpy as np
import pandas as pd
import time

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

def get_setting_result2(acquisition_name: str, objective_name: str, n_runs: int, n_trials: int) -> dict[list[dict]]:
    """
    Returns dict(gap=x, runtime=y), where x is list of dicts for gap results and y likewise for runtime
    """

    gap_results, runtime_results = [], []
    for run_id in range(n_runs):
        t0 = time.monotonic()
        gap_result = run_botorch(acquisition_name=acquisition_name, objective_name=objective_name, n_trials=n_trials)
        t1 = time.monotonic()
        runtime_result = dict(
            acquisition=acquisition,
            objective=objective,
            run_id=run_id,
            runtime=t1 - t0,
            implementation="BoTorch"
        )
        gap_results.extend(gap_result)
        runtime_results.append(runtime_result)
    
    # summarise gap by trial id
    def _gap_estimate(x):
        return x.mean()
    def _gap_se(x):
        return np.std(x) / np.sqrt(len(x))

    gap_results = pd.DataFrame(gap_results).groupby("trial").aggregate({"gap_estimate": _gap_estimate, "gap_se": _gap_se})

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

def run_botorch(acquisition: str, objective: str, n_trials: int) -> list[dict]:
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