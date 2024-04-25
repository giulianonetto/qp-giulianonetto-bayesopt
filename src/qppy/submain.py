#!/usr/bin/env python3

from simulation import get_setting_result
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
        for acquisition in ["ei", "kg", "pes"]:
            for objective in ["h6", "gp", "shu"]:
                msg = f"Running BoTorch simulation for acquisition={acquisition}, objective={objective}."
                print(msg)
                result = get_setting_result(acquisition=acquisition, objective=objective, n_runs=n_runs, n_trials=n_trials)
                results_gap.extend(result["gap"])
                results_runtime.extend(result["runtime"])
        
        print("Saving BoTorch results.")
        results_gap = pd.DataFrame(results_gap)
        results_gap.to_csv(botorch_gap_results_file, sep="\t", index=False)
        results_runtime = pd.DataFrame(results_runtime)
        results_runtime.to_csv(botorch_runtime_results_file, sep="\t", index=False)
    else:
        print(f"Skipping BoTorch simulation as results already exist in output_dir: {output_dir}.")


args = """ Run all python-based analyses (except plotting, which is done in R)
        Usage:
          main [--n_runs=<value>] [--n_trials=<value>] [--output_dir=<value>]
          main (-h | --help)
          main --version
        
        Optional arguments:

          -h --help                 Show this screen.
          --version                 Show version.
          
          --n_runs=<value>          Integer specifying number of simulation runs. Defaults to 2.
          --n_trials=<value>        Integer specifying number of BO trials. Defaults to 10.
          --output_dir=<value>      Path to output directory. Defaults is `output`.
"""

if __name__ == '__main__':
    arguments = docopt(args)

    # run all analyses
    run_qp5_python(
        n_runs=arguments.get("--n_runs"),
        n_trials=arguments.get("--n_trials"),
        output_dir=arguments.get("--output_dir")
    )
