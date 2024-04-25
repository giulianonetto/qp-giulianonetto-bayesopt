# STAT 548 Qualifying Paper Report
This repository contains the report for Giuliano's Qualifying Paper (STAT548). The paper reference is shown below.

Frazier PI. A Tutorial on Bayesian Optimization. rXiv. 2018. DOI: [http://arxiv.org/abs/1807.02811](http://arxiv.org/abs/1807.02811).

# Reproducibility

To reproduce all results, please make sure you have a Docker installation (v. >= 24.0.1) on your computer. Then, run the following (from this project's root):

```
docker build -t qp:qp5 .
docker run --rm -it -v $(pwd):/home/rstudio \
    qp:qp5 \
    python3.10 src/main.py \
    --output_dir output-reproduced \
    --n_trials 20 \
    --n_runs 2
```

The output will be available in the directory `output-reproduced`. You can change the values in `--n_trails` or `--n_runs` as you'd like (though it may take a while to run!).
