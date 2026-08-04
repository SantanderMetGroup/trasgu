# Benchmarks

This directory contains controlled performance measurements. Scientific case
studies and validation experiments belong under `experiments/` and
`validation/`, respectively.

## Benchmarks

- `dimensional_workload`: fitting workload for the Chimera collections from
  four to eight variables, using 300 observations and one CPU core.
- `pyvinecopulib_thread_scaling`: scaling of one fixed eight-dimensional fit
  as the number of `pyvinecopulib` threads increases.

All figures use `styles/trasgu.mplstyle`. Plotting scripts read CSV files under
their benchmark's `results/` directory and write publication-ready figures to
`figures/`.

Trasgu worker scaling is deliberately not included. Measuring the complete
Snakemake/SLURM stack would mix fitting time with scheduler, storage, and
cluster-load effects, while these overheads are amortized in exhaustive
seven- and eight-dimensional campaigns.
