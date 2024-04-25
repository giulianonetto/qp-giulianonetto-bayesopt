#!/usr/bin/env python3

from docopt import docopt
import subprocess
import time
import logging


args = """ Run all QP5 analyses
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
    arguments = docopt(args, version=f"QP5")
    n_runs = arguments["--n_runs"]
    n_trials = arguments["--n_trials"]
    output_dir = arguments["--output_dir"]

    # build commands
    cmd_python_pipeline = ["python3.10", "src/qppy/submain.py"]
    cmd_r_pipeline = ["Rscript", "src/qpr/submain.r"]

    # add arguments if present
    if n_runs:
      n_runs_cmd = ["--n_runs", n_runs]
      cmd_python_pipeline.extend(n_runs_cmd)
      cmd_r_pipeline.extend(n_runs_cmd)
    
    if n_trials:
      n_trials_cmd = ["--n_trials", n_trials]
      cmd_python_pipeline.extend(n_trials_cmd)
      cmd_r_pipeline.extend(n_trials_cmd)
    
    if output_dir:
      output_dir_cmd = ["--output_dir", output_dir]
      cmd_python_pipeline.extend(output_dir_cmd)
      cmd_r_pipeline.extend(output_dir_cmd)

    # run all analyses
    t0 = time.time()
    logging.info(f"Running python-based simulation with BoTorch")
    subprocess.run(cmd_python_pipeline)
    logging.info(f"Running R-based simulation with DiceOptim + plotting all results")
    subprocess.run(cmd_r_pipeline)
    t1 = time.time()
    logging.info(f"Done after {t1-t0:>4.2} seconds.")
 