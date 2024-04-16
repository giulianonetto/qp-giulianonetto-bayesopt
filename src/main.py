#!/usr/bin/env python3

from docopt import docopt
import multiprocessing

# import reproducibility function
from qppkg import __version__
from qppkg.reproducibility import run_all_analyses

args = """ Run all QP2 analyses
        Usage:
          main [--n_runs=<value>] [--n_cores=<value>] [--output_dir=<value>] [--force]
          main (-h | --help)
          main --version
        
        Optional arguments:

          -h --help                                     Show this screen.
          --version                                     Show version.
          
          --n_runs=<value>          Integer specifying number of simulation runs. Defaults to 100. (it takes a while)
          --n_codes=<value>         Integer specifying number of cores for parallel computation. If not given, defaults to CPU count - 2.
          --output_dir=<value>      Path to output directory. Defaults is dat/output-<today>-<now>.
          --force                   If passed, it will force running the simulation (it will overwrite the output_dir, if existing).
"""

if __name__ == '__main__':
    arguments = docopt(args, version=f"qppkg v. {__version__}")

    # run all analyses
    run_all_analyses(
        n_runs=int(arguments.get("--n_runs", 10)),
        n_cores=int(arguments.get("--n_cores", multiprocessing.cpu_count() - 2)),
        output_dir=arguments.get("--output_dir"),
        force=arguments.get("--force")
    )
