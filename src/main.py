#!/usr/bin/env python3

from docopt import docopt
import subprocess
import time
import logger


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
    arguments = docopt(args, version=f"qppkg v. {__version__}")

    t0 = time.time()

    # run all analyses
    logger.info(f"Running python-based simulation with BoTorch")
    cmd_python_pipeline = [
      "python3.10",
      "src/qppy/submain.py",
      "--n_runs",
      arguments["--n_runs"],
      "--n_trials",
      arguments["--n_trials"],
      "--output_dir",
      arguments["--output_dir"]
    ]
    subprocess.run(cmd_python_pipeline)

    logger.info(f"Running R-based simulation with DiceOptim + plotting all results")
    cmd_r_pipeline = [
      "Rscript",
      "src/qpr/submain.r",
      "--n_runs",
      arguments["--n_runs"],
      "--n_trials",
      arguments["--n_trials"],
      "--output_dir",
      arguments["--output_dir"]
    ]
    subprocess.run(cmd_r_pipeline)
    t1 = time.time()
    logger.info(f"Done after {t1-t0:>4.2} seconds.")