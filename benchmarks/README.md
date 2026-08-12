# Benchmarks

This directory contains controlled performance measurements. Scientific case
studies and validation experiments belong under `experiments/` and
`validation/`, respectively.

## Benchmarks

- `dimensional_workload`: fitting workload for the Chimera collections from
  four to eight variables, using 300 observations and one CPU core.
- `pyvinecopulib_thread_scaling`: scaling of one fixed eight-dimensional fit
  as the number of `pyvinecopulib` threads increases.

Both benchmarks use synthetic inputs generated with Clayton copulas, 300
observations and high dependence. They were run on an Intel Xeon Silver 4208
CPU at 2.10 GHz with `pyvinecopulib` 0.7.6.

All figures use `styles/trasgu.mplstyle`. Plotting scripts read CSV files under
their benchmark's `results/` directory and write publication-ready figures to
`figures/`.

Trasgu worker scaling is deliberately not included. Measuring the complete
Snakemake/SLURM stack would mix fitting time with scheduler, storage, and
cluster-load effects, while these overheads are amortized in exhaustive
seven- and eight-dimensional campaigns.
