# Benchmarks

This directory contains two controlled `pyvinecopulib` fitting benchmarks.
Both use 300-observation synthetic inputs generated from high-dependence
Clayton copulas, the `one_par` family set, maximum likelihood estimation,
and AIC selection. The recorded results were obtained on an Intel(R) Xeon(R)
Gold 5218 CPU @ 2.30GHz.

## Measurements

- [Dimensional workload](dimensional_workload/README.md) measures full
  Chimera collections for four and five variables on one core. It estimates
  the six-, seven-, and eight-variable totals from 1,000 fits per dimension.
- [Thread scaling](pyvinecopulib_thread_scaling/README.md) measures one fixed
  eight-variable vine fit at 1–48 allocated CPUs, with seven repetitions
  per CPU count.

Each benchmark directory contains its script, recorded CSV results, a plotting
script, generated figures, and a README with the commands and measurement
protocol. Input data are in [`data/`](data/). The plotting scripts use
[`styles/trasgu.mplstyle`](../styles/trasgu.mplstyle) and generate PNG, PDF,
and SVG figures.

Scientific case studies and validation are documented separately under
[`experiments/`](../experiments/) and [`validation/`](../validation/).
