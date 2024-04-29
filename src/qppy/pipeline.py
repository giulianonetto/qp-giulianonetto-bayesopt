#!/usr/bin/env python3
import os
import time
from .bayesopt import get_setting_result
from typing import Optional
from docopt import docopt
from pathlib import Path
import pandas as pd


def run_qp5_python(n_runs: Optional[int], n_trials: Optional[int], output_dir: Optional[str]):
    if n_runs:
        n_runs = int(n_runs)
    else:
        n_runs = 2
    if n_trials:
        n_trials = int(n_trials)
    else:
        n_trials = 10
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = Path("output")

    output_dir.mkdir(parents=True, exist_ok=True)

    botorch_gap_results_file = output_dir.joinpath("results_botorch_gap.tsv")
    botorch_runtime_results_file = output_dir.joinpath("results_botorch_runtime.tsv")

    results_exist = botorch_gap_results_file.exists() and botorch_runtime_results_file.exists()

    if not results_exist:

        results_gap, results_runtime = [], []
        for acquisition_name in ["ei", "kg", "lpi", "random"]:
            for objective_name in ["h6", "gp", "ros"]:
                msg = f"Running BoTorch simulation for acquisition={acquisition_name}, objective={objective_name}."
                print(msg)
                t0 = time.monotonic()
                result = get_setting_result(acquisition_name=acquisition_name, objective_name=objective_name, n_runs=n_runs, n_trials=n_trials)
                print(f"Took {time.monotonic() - t0:>4.4} seconds")
                results_gap.extend(result["gap"])
                results_runtime.extend(result["runtime"])
        
        print("Saving BoTorch results.")
        results_gap = pd.DataFrame(results_gap)
        results_gap.to_csv(botorch_gap_results_file, sep="\t", index=False)
        results_runtime = pd.DataFrame(results_runtime)
        results_runtime.to_csv(botorch_runtime_results_file, sep="\t", index=False)
    else:
        print(f"Skipping BoTorch simulation as results already exist in output_dir: {output_dir}.")
