from .bayesopt import run_botorch
import numpy as np
import pandas as pd
import time


def get_setting_result(acquisition_name: str, objective_name: str, n_runs: int, n_trials: int) -> dict[list[dict]]:
    """
    Returns dict(gap=x, runtime=y), where x is list of dicts for gap results and y likewise for runtime
    """

    gap_results, runtime_results = [], []
    for run_id in range(n_runs):
        t0 = time.monotonic()
        gaps = run_botorch(acquisition_name=acquisition_name, objective_name=objective_name, n_trials=n_trials)
        t1 = time.monotonic()
        gap_results.extend([dict(run_id=run_id, trial=i, gaps=gaps[i].item()) for i in range(n_trials)])
        runtime_result = dict(
            acquisition=acquisition_name,
            objective=objective_name,
            run_id=run_id,
            time_per_trial=(t1 - t0) / n_trials,
            implementation="BoTorch"
        )
        runtime_results.append(runtime_result)
    
    # summarise gap by trial id
    def gap_estimate(x):
        return x.mean()
    def gap_se(x):
        return np.std(x) / np.sqrt(len(x))

    gap_results = (
        pd.DataFrame(gap_results)
        .groupby("trial")
        .aggregate({"gaps": [gap_estimate, gap_se]})
        .droplevel(0, axis="columns")
        .reset_index()
    )

    gap_results.insert(
        0, "acquisition", acquisition_name
    )
    gap_results.insert(
        0, "objective", objective_name
    )
    gap_results.insert(
        0, "implementation", "BoTorch"
    )

    return dict(gap=gap_results.to_dict(orient='records'), runtime=runtime_results)

# def run_botorch(acquisition: str, objective: str, n_trials: int) -> list[dict]:
#     gap_result = []
#     for i in range(n_trials):
#         gap_result.append(
#             dict(
#                 acquisition=acquisition, objective=objective,
#                 trial=i,
#                 gap_estimate=1, gap_se=1,
#                 objetive_estimate=1, objetive_se=1,
#                 implementation="BoTorch"
#             )
#         )